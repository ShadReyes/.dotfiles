# Fluid Linear API Reference

Set these non-secret paths for shorter commands:

```bash
FLUID=~/.agents/skills/fluid/skills/linear-fluid
OPS=~/.agents/skills/fluid/skills/linear-graphql/operations
CLI="$FLUID/scripts/linear-fluid-gql.mjs"
```

Verify identity or discover workspace IDs:

```bash
node "$CLI" "$OPS/whoami.graphql" --pretty
node "$CLI" "$OPS/teams.graphql"
node "$CLI" "$OPS/team-states.graphql" --variables '{"teamId":"team-uuid"}'
node "$CLI" "$OPS/labels.graphql"
node "$CLI" "$OPS/projects.graphql"
node "$CLI" "$OPS/users.graphql"
```

Read, create, update, and comment on issues with the corresponding bundled
operations. Keep variable files mode `0600` and remove temporary files after
use.

The launcher returns verified workspace metadata in an envelope. GraphQL data,
pagination cursors, and mutation results are nested under `data`.
