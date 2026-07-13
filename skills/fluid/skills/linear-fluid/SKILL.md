---
name: linear-fluid
description: Use when reading, searching, creating, updating, or commenting on issues in Fluid's Linear workspace through the direct GraphQL API.
user-invocable: true
---

# Fluid Linear API

Use the locked Fluid launcher for every Linear API operation. It performs a
workspace identity check before the requested operation and reads the personal
API key from `~/.config/linear/workspaces/fluid.env`.

```bash
FLUID=~/.agents/skills/fluid/skills/linear-fluid
OPS=~/.agents/skills/fluid/skills/linear-graphql/operations
node "$FLUID/scripts/linear-fluid-gql.mjs" "$OPS/whoami.graphql" --pretty
```

The launcher is locked to Fluid Commerce:

- Organization: `Fluid Commerce`
- URL key: `fluid-commerce`
- Team: `Current`
- GraphQL endpoint: `https://api.linear.app/graphql`

Use the bundled operations for common requests. Use `--variables` or
`--variables-file` for user data; never interpolate values into GraphQL text.
For mutations, explain the intended change before running the operation and
report the returned Linear identifier or URL afterward.

Never pass credentials as arguments, inspect or print the dotenv file, use a
different workspace, or bypass the organization preflight.
