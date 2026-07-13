---
name: linear-triage
description: Analyze Current-team Linear issues by Project, issue status, and blocking relationships to determine what is ready, blocked, or in progress.
user-invocable: true
---

# Fluid Linear Triage

Run the bundled direct GraphQL script before recommending or starting Linear
work. It analyzes issues on the `Current` team and optionally limits the scope
to one Project.

```bash
node <skill-dir>/scripts/linear-triage.mjs
node <skill-dir>/scripts/linear-triage.mjs --project "Project name"
node <skill-dir>/scripts/linear-triage.mjs --format=json
node <skill-dir>/scripts/linear-triage.mjs --state "Todo,In Progress"
```

The script uses the locked Fluid GraphQL profile and reads the API key from
`~/.config/linear/workspaces/fluid.env`. It never accepts another team.

## Output

- `IN PROGRESS`: issues in a started state.
- `READY TO WORK`: unblocked issues that are not in triage and are not marked
  `ready-for-agent`.
- `AGENT-READY WORK`: unblocked or blocked issues carrying `ready-for-agent`.
- `TRIAGE QUEUE`: issues in a triage state.
- `RECOMMENDED WORK ORDER`: topological ordering derived from blocking
  relationships, with status markers.
- `DEPENDENCY GRAPH`: active blockers and blocked issues.

Projects and Initiatives are reported as context. They do not determine work
priority or ownership. Priority is determined only by issue status and active
blocking relationships. Linear priority, estimates, assignees, labels other
than `ready-for-agent`, and Initiative membership must not reorder work.

Parent/child issues are supported as optional context. A parent issue is not a
special planning container and should not be recommended over its actionable
children.
