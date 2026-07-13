#!/usr/bin/env node

import { executeVerifiedOperation } from "../../linear-graphql/scripts/linear-gql-core.mjs";
import { FLUID_LINEAR_PROFILE } from "../../linear-fluid/config.mjs";

const args = process.argv.slice(2);

function getArg(name) {
  const index = args.indexOf(`--${name}`);
  return index >= 0 && index + 1 < args.length ? args[index + 1] : null;
}

const projectFilter = getArg("project");
const stateFilter = getArg("state");
const formatJson = args.includes("--format=json");
const providedTeam = getArg("team");

if (providedTeam && providedTeam.toLowerCase() !== FLUID_LINEAR_PROFILE.defaultTeam.toLowerCase()) {
  console.error(`Error: triage only runs against the "${FLUID_LINEAR_PROFILE.defaultTeam}" team.`);
  process.exit(1);
}

async function gql(query, variables = {}) {
  const result = await executeVerifiedOperation({
    profile: FLUID_LINEAR_PROFILE,
    query,
    variables,
  });
  return result.data;
}

async function fetchViewer() {
  const data = await gql(`query { viewer { id name } }`);
  return data.viewer;
}

async function fetchTeam() {
  const data = await gql(`
    query($filter: TeamFilter) {
      teams(filter: $filter, first: 10) { nodes { id name } }
    }
  `, { filter: { id: { eq: FLUID_LINEAR_PROFILE.defaultTeamId } } });

  const team = data.teams.nodes[0];
  if (!team || team.name !== FLUID_LINEAR_PROFILE.defaultTeam) {
    throw new Error(`Configured team is not available: ${FLUID_LINEAR_PROFILE.defaultTeam}`);
  }
  return team;
}

async function fetchProjects(teamId) {
  const projects = [];
  let after = null;
  let hasNextPage = true;

  while (hasNextPage) {
    const data = await gql(`
      query($filter: ProjectFilter, $after: String) {
        projects(filter: $filter, first: 100, after: $after) {
          nodes {
            id
            name
            initiatives { nodes { id name } }
          }
          pageInfo { hasNextPage endCursor }
        }
      }
    `, { filter: { accessibleTeams: { id: { eq: teamId } } }, after });

    projects.push(...data.projects.nodes);
    hasNextPage = data.projects.pageInfo.hasNextPage;
    after = data.projects.pageInfo.endCursor;
  }

  return projects;
}

async function fetchIssues(teamId, projectId = null) {
  const issues = [];
  let after = null;
  let hasNextPage = true;
  const filter = { team: { id: { eq: teamId } } };
  if (projectId) filter.project = { id: { eq: projectId } };

  while (hasNextPage) {
    const data = await gql(`
      query($filter: IssueFilter, $after: String) {
        issues(filter: $filter, first: 100, after: $after, orderBy: updatedAt) {
          nodes {
            id
            identifier
            title
            assignee { id name }
            state { name type }
            labels { nodes { name } }
            project { id name }
            parent { id identifier }
            children { nodes { id identifier } }
            relations {
              nodes {
                type
                relatedIssue { id identifier }
              }
            }
          }
          pageInfo { hasNextPage endCursor }
        }
      }
    `, { filter, after });

    issues.push(...data.issues.nodes);
    hasNextPage = data.issues.pageInfo.hasNextPage;
    after = data.issues.pageInfo.endCursor;
  }

  return issues;
}

function buildGraph(rawIssues) {
  const issueMap = new Map();
  const blockedBy = new Map();
  const blocks = new Map();

  for (const raw of rawIssues) {
    issueMap.set(raw.id, {
      id: raw.id,
      identifier: raw.identifier,
      title: raw.title,
      state: raw.state?.name || "Unknown",
      stateType: raw.state?.type || "unknown",
      assignee: raw.assignee?.name || null,
      assigneeId: raw.assignee?.id || null,
      labels: (raw.labels?.nodes || []).map((label) => label.name),
      project: raw.project || null,
      parentId: raw.parent?.id || null,
      parentIdentifier: raw.parent?.identifier || null,
      children: [],
    });
    blockedBy.set(raw.id, new Set());
    blocks.set(raw.id, new Set());
  }

  for (const raw of rawIssues) {
    const issue = issueMap.get(raw.id);
    if (issue.parentId && issueMap.has(issue.parentId)) {
      issueMap.get(issue.parentId).children.push(issue.id);
    }

    for (const relation of raw.relations?.nodes || []) {
      const relatedId = relation.relatedIssue?.id;
      if (!relatedId || !issueMap.has(relatedId)) continue;
      if (relation.type === "blocks") {
        blocks.get(raw.id).add(relatedId);
        blockedBy.get(relatedId).add(raw.id);
      }
      if (relation.type === "blockedBy") {
        blockedBy.get(raw.id).add(relatedId);
        blocks.get(relatedId).add(raw.id);
      }
    }
  }

  return { issueMap, blockedBy, blocks };
}

function isComplete(issue) {
  return issue.stateType === "completed" || issue.stateType === "canceled";
}

function isAgentReady(issue) {
  return issue.labels.some(
    (label) => label.toLowerCase() === FLUID_LINEAR_PROFILE.labels.agentReady,
  );
}

function activeBlockers(issue, graph) {
  return [...graph.blockedBy.get(issue.id)]
    .map((id) => graph.issueMap.get(id))
    .filter((blocker) => blocker && !isComplete(blocker));
}

function topologicalOrder(graph) {
  const degree = new Map();
  for (const id of graph.issueMap.keys()) {
    degree.set(id, activeBlockers(graph.issueMap.get(id), graph).length);
  }

  const sortIds = (a, b) => a.localeCompare(b);
  const queue = [...degree].filter(([, value]) => value === 0).map(([id]) => id).sort(sortIds);
  const ordered = [];

  while (queue.length > 0) {
    const current = queue.shift();
    ordered.push(current);
    for (const blockedId of graph.blocks.get(current)) {
      const nextDegree = (degree.get(blockedId) || 0) - 1;
      degree.set(blockedId, nextDegree);
      if (nextDegree === 0) queue.push(blockedId);
    }
    queue.sort(sortIds);
  }

  return {
    ordered,
    cyclic: [...graph.issueMap.keys()].filter((id) => !ordered.includes(id)),
  };
}

function projectLabel(issue) {
  return issue.project ? issue.project.name : "No Project";
}

function initiativeNames(issue, projects) {
  return projects.find((project) => project.id === issue.project?.id)?.initiatives
    ?.nodes.map((initiative) => initiative.name) || [];
}

function issueJson(issue, graph, projects) {
  return {
    identifier: issue.identifier,
    title: issue.title,
    state: issue.state,
    stateType: issue.stateType,
    assignee: issue.assignee,
    project: projectLabel(issue),
    initiatives: initiativeNames(issue, projects),
    parent: issue.parentIdentifier,
    agentReady: isAgentReady(issue),
    blockedBy: activeBlockers(issue, graph).map((blocker) => blocker.identifier),
  };
}

function marker(issue, graph) {
  if (isComplete(issue)) return "DONE";
  if (activeBlockers(issue, graph).length > 0) return "BLOCKED";
  if (issue.stateType === "triage") return "TRIAGE";
  if (isAgentReady(issue)) return "AGENT";
  if (issue.stateType === "started") return "IN PROGRESS";
  return "READY";
}

function printIssue(issue, graph, projects, prefix = "") {
  const initiatives = initiativeNames(issue, projects);
  const context = `${projectLabel(issue)}${initiatives.length ? ` | ${initiatives.join(", ")}` : ""}`;
  const assignee = issue.assignee ? ` | ${issue.assignee}` : "";
  console.log(`${prefix}${issue.identifier}: ${issue.title} [${issue.state}] (${context}${assignee})`);
}

async function main() {
  const viewer = await fetchViewer();
  const team = await fetchTeam();
  const projects = await fetchProjects(team.id);
  let selectedProject = null;

  if (projectFilter) {
    selectedProject = projects.find(
      (project) => project.id === projectFilter || project.name.toLowerCase() === projectFilter.toLowerCase(),
    );
    if (!selectedProject) throw new Error(`Project not found on ${team.name}: ${projectFilter}`);
  }

  let rawIssues = await fetchIssues(team.id, selectedProject?.id || null);
  if (stateFilter) {
    const allowed = new Set(stateFilter.split(",").map((state) => state.trim().toLowerCase()));
    rawIssues = rawIssues.filter(
      (issue) => allowed.has(issue.state?.type?.toLowerCase()) || allowed.has(issue.state?.name?.toLowerCase()),
    );
  }

  if (rawIssues.length === 0) {
    console.log("No issues found matching the requested filters.");
    return;
  }

  const graph = buildGraph(rawIssues);
  const { ordered, cyclic } = topologicalOrder(graph);
  const issues = [...graph.issueMap.values()];
  const inProgress = issues.filter((issue) => issue.stateType === "started");
  const ready = issues.filter(
    (issue) => !isComplete(issue) && activeBlockers(issue, graph).length === 0 && issue.stateType !== "triage" && issue.stateType !== "started" && !isAgentReady(issue),
  );
  const agentReady = issues.filter((issue) => !isComplete(issue) && isAgentReady(issue));
  const triage = issues.filter((issue) => issue.stateType === "triage");

  if (formatJson) {
    console.log(JSON.stringify({
      workspace: FLUID_LINEAR_PROFILE.organization,
      viewer: { id: viewer.id, name: viewer.name },
      team,
      project: selectedProject?.name || null,
      inProgress: inProgress.map((issue) => issueJson(issue, graph, projects)),
      ready: ready.map((issue) => issueJson(issue, graph, projects)),
      agentReady: agentReady.map((issue) => issueJson(issue, graph, projects)),
      triage: triage.map((issue) => issueJson(issue, graph, projects)),
      workOrder: ordered.map((id) => ({
        marker: marker(graph.issueMap.get(id), graph),
        ...issueJson(graph.issueMap.get(id), graph, projects),
      })),
      cyclic: cyclic.map((id) => graph.issueMap.get(id).identifier),
    }, null, 2));
    return;
  }

  console.log(`Scope: team "${team.name}"${selectedProject ? ` | project "${selectedProject.name}"` : ""}`);
  console.log(`Issues: ${issues.length} | In Progress: ${inProgress.length} | Ready: ${ready.length} | Agent-ready: ${agentReady.length} | Triage: ${triage.length}`);

  console.log("\nIN PROGRESS");
  inProgress.forEach((issue) => printIssue(issue, graph, projects, "  "));

  console.log("\nREADY TO WORK");
  ready.forEach((issue) => printIssue(issue, graph, projects, "  "));

  console.log("\nAGENT-READY WORK");
  agentReady.forEach((issue) => printIssue(issue, graph, projects, "  "));

  console.log("\nTRIAGE QUEUE");
  triage.forEach((issue) => printIssue(issue, graph, projects, "  "));

  console.log("\nRECOMMENDED WORK ORDER");
  ordered.forEach((id, index) => {
    const issue = graph.issueMap.get(id);
    printIssue(issue, graph, projects, `  ${index + 1}. [${marker(issue, graph)}] `);
  });

  console.log("\nDEPENDENCY GRAPH");
  for (const issue of issues) {
    const blockers = activeBlockers(issue, graph);
    const blocked = [...graph.blocks.get(issue.id)]
      .map((id) => graph.issueMap.get(id))
      .filter(Boolean);
    if (blockers.length || blocked.length) {
      console.log(`  ${issue.identifier}: blocked by [${blockers.map((item) => item.identifier).join(", ") || "none"}] | blocks [${blocked.map((item) => item.identifier).join(", ") || "none"}]`);
    }
  }

  if (cyclic.length > 0) {
    console.log(`\nWARNING: dependency cycle detected among ${cyclic.map((id) => graph.issueMap.get(id).identifier).join(", ")}`);
  }
}

main().catch((error) => {
  console.error(`Error: ${error.message}`);
  process.exitCode = 1;
});
