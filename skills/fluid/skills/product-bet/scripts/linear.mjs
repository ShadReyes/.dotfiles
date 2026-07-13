#!/usr/bin/env node

import { readFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";

import { executeVerifiedOperation } from "../../linear-graphql/scripts/linear-gql-core.mjs";
import { FLUID_LINEAR_PROFILE } from "../../linear-fluid/config.mjs";

const argv = process.argv.slice(2);
const flags = {};
const positional = [];

for (let index = 0; index < argv.length; index += 1) {
  const argument = argv[index];
  if (!argument.startsWith("--")) {
    positional.push(argument);
    continue;
  }
  const name = argument.slice(2);
  const next = argv[index + 1];
  if (next !== undefined && !next.startsWith("--")) {
    flags[name] = next;
    index += 1;
  } else {
    flags[name] = true;
  }
}

const command = positional.shift();
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function expandHome(filePath) {
  if (filePath === "~") return os.homedir();
  return filePath.startsWith("~/") ? path.join(os.homedir(), filePath.slice(2)) : filePath;
}

function output(value) {
  console.log(JSON.stringify(value, null, 2));
}

function fail(message) {
  throw new Error(message);
}

async function gql(query, variables = {}) {
  const result = await executeVerifiedOperation({
    profile: FLUID_LINEAR_PROFILE,
    query,
    variables,
  });
  return result.data;
}

function readContent() {
  if (flags.content !== undefined && flags["content-file"] !== undefined) {
    fail("pass --content or --content-file, not both");
  }
  if (flags.content !== undefined) return String(flags.content);
  if (flags["content-file"] === undefined) return undefined;
  const contentPath = String(flags["content-file"]);
  return contentPath === "-" ? readFileSync(0, "utf8") : readFileSync(expandHome(contentPath), "utf8");
}

async function resolveTeamId(nameOrId = FLUID_LINEAR_PROFILE.defaultTeam) {
  if (UUID_RE.test(String(nameOrId))) return String(nameOrId);
  const data = await gql(`
    query($name: String!) {
      teams(filter: { name: { containsIgnoreCase: $name } }, first: 10) {
        nodes { id name }
      }
    }
  `, { name: String(nameOrId) });
  const exact = data.teams.nodes.find(
    (team) => team.name.toLowerCase() === String(nameOrId).toLowerCase(),
  );
  const team = exact || data.teams.nodes[0];
  if (!team) fail(`no team matching "${nameOrId}"`);
  return team.id;
}

async function resolveInitiativeId(nameOrId = FLUID_LINEAR_PROFILE.defaultInitiative) {
  if (String(nameOrId).toLowerCase() === "none") return null;
  if (UUID_RE.test(String(nameOrId))) return String(nameOrId);
  const data = await gql(`
    query($name: String!) {
      initiatives(filter: { name: { containsIgnoreCase: $name } }, first: 10) {
        nodes { id name }
      }
    }
  `, { name: String(nameOrId) });
  const exact = data.initiatives.nodes.find(
    (initiative) => initiative.name.toLowerCase() === String(nameOrId).toLowerCase(),
  );
  const initiative = exact || data.initiatives.nodes[0];
  if (!initiative) fail(`no Initiative matching "${nameOrId}"`);
  return initiative.id;
}

async function listProjects() {
  const filter = flags.query
    ? { name: { containsIgnoreCase: String(flags.query) } }
    : null;
  const data = await gql(`
    query($filter: ProjectFilter) {
      projects(filter: $filter, first: 50) {
        nodes {
          id
          name
          url
          state
          description
          teams { nodes { id name } }
          initiatives { nodes { id name } }
        }
      }
    }
  `, { filter });
  return data.projects.nodes;
}

async function resolveProjectId(nameOrId) {
  if (UUID_RE.test(String(nameOrId))) return String(nameOrId);
  const projects = await listProjects();
  const exact = projects.find((project) => project.name.toLowerCase() === String(nameOrId).toLowerCase());
  const project = exact || projects[0];
  if (!project) fail(`no Project matching "${nameOrId}"`);
  return project.id;
}

const DOC_FIELDS = `id slugId title url createdAt updatedAt project { id name }`;

const commands = {
  async whoami() {
    const data = await gql(`
      query {
        viewer {
          id
          name
          email
          organization { id name urlKey }
        }
      }
    `);
    output(data.viewer);
  },

  async "list-teams"() {
    const data = await gql(`query { teams(first: 100) { nodes { id name key } } }`);
    let teams = data.teams.nodes;
    if (flags.query) {
      const query = String(flags.query).toLowerCase();
      teams = teams.filter((team) => team.name.toLowerCase().includes(query));
    }
    output(teams);
  },

  async "list-projects"() {
    output(await listProjects());
  },

  async "save-project"() {
    if (!flags.name && !flags.id) fail("save-project requires --name or --id");

    if (flags.id) {
      const input = {};
      if (flags.name) input.name = String(flags.name);
      if (flags.description) input.description = String(flags.description);
      const data = await gql(`
        mutation($id: String!, $input: ProjectUpdateInput!) {
          projectUpdate(id: $id, input: $input) {
            success project { id name url }
          }
        }
      `, { id: String(flags.id), input });
      output(data.projectUpdate);
      return;
    }

    const teamId = await resolveTeamId(flags.team || FLUID_LINEAR_PROFILE.defaultTeam);
    const initiativeName = flags.initiative || FLUID_LINEAR_PROFILE.defaultInitiative;
    const initiativeId = await resolveInitiativeId(initiativeName);
    const input = {
      name: String(flags.name),
      teamIds: [teamId],
    };
    if (flags.description) input.description = String(flags.description);

    const created = await gql(`
      mutation($input: ProjectCreateInput!) {
        projectCreate(input: $input) { success project { id name url } }
      }
    `, { input });
    const projectResult = created.projectCreate;
    if (!projectResult.success || !projectResult.project?.id) {
      output(projectResult);
      return;
    }

    if (initiativeId) {
      await gql(`
        mutation($input: InitiativeToProjectCreateInput!) {
          initiativeToProjectCreate(input: $input) { success }
        }
      `, { input: { projectId: projectResult.project.id, initiativeId } });
    }

    output({ ...projectResult, initiativeId: initiativeId || null });
  },

  async "list-docs"() {
    let documents;
    if (flags.project) {
      const projectId = await resolveProjectId(String(flags.project));
      const data = await gql(`
        query($id: String!) {
          project(id: $id) { documents(first: 100) { nodes { ${DOC_FIELDS} } } }
        }
      `, { id: projectId });
      documents = data.project?.documents.nodes || [];
    } else {
      const data = await gql(`query { documents(first: 100) { nodes { ${DOC_FIELDS} } } }`);
      documents = data.documents.nodes;
    }
    if (flags.query) {
      const query = String(flags.query).toLowerCase();
      documents = documents.filter((document) => document.title.toLowerCase().includes(query));
    }
    output(documents);
  },

  async "get-doc"() {
    const id = positional[0];
    if (!id) fail("get-doc requires a document ID or slug");
    const data = await gql(`
      query($id: String!) { document(id: $id) { ${DOC_FIELDS} content } }
    `, { id });
    output(data.document);
  },

  async "save-doc"() {
    const content = readContent();
    if (flags.id) {
      const input = {};
      if (flags.title) input.title = String(flags.title);
      if (content !== undefined) input.content = content;
      const data = await gql(`
        mutation($id: String!, $input: DocumentUpdateInput!) {
          documentUpdate(id: $id, input: $input) {
            success document { ${DOC_FIELDS} }
          }
        }
      `, { id: String(flags.id), input });
      output(data.documentUpdate);
      return;
    }

    if (!flags.title || !flags.project) {
      fail("save-doc requires --title and --project when creating a document");
    }
    const projectId = await resolveProjectId(String(flags.project));
    const input = { title: String(flags.title), projectId };
    if (content !== undefined) input.content = content;
    const data = await gql(`
      mutation($input: DocumentCreateInput!) {
        documentCreate(input: $input) { success document { ${DOC_FIELDS} } }
      }
    `, { input });
    output(data.documentCreate);
  },
};

if (!command || !commands[command]) {
  console.error(`Unknown command "${command || ""}". Commands: ${Object.keys(commands).join(", ")}`);
  process.exitCode = 1;
} else {
  commands[command]().catch((error) => {
    console.error(`Error: ${error.message}`);
    process.exitCode = 1;
  });
}
