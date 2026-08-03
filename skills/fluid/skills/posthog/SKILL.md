---
name: posthog
description: Use when working with Fluid's PostHog data or setup, including product analytics, events and properties, dashboards and insights, feature flags and experiments, session recordings, surveys, error tracking, or PostHog-backed product questions.
---

# Fluid PostHog

Use the live PostHog tool catalog rather than memorizing tool names or schemas.
Fluid's product apps send data to PostHog US Cloud (`https://us.i.posthog.com`),
but the active authenticated project is authoritative. Never infer a project
from a public SDK key.

## Choose an interface

- Prefer the authenticated PostHog MCP for native, typed tool calls.
- Use `posthog-cli api` when shell composition, filtering, scripting, or smaller
  model context is useful, or when MCP is unavailable. It mirrors the MCP tool
  catalog.
- If authentication is missing, use `codex mcp login posthog` for MCP or
  `posthog-cli login` for the CLI. Never print or search for stored tokens.

## Discover before calling

Find and inspect the current tool instead of guessing:

```bash
posthog-cli api search '<task terms>'
posthog-cli api info <tool-name>
posthog-cli api schema <tool-name> <field.path> # required for fields with hints
posthog-cli api call <tool-name> '<json>'
```

Use `posthog-cli api --agent-help` when the CLI workflow is not already in
context. The live catalog covers analytics and SQL, data schemas, dashboards,
insights, flags, experiments, recordings, surveys, error tracking, logs, and
other PostHog products.

Before querying collected data, inspect `read-data-schema` and verify the event
and property names in the active Fluid project. Do not assume canonical-looking
names such as `$pageview` exist.

## Mutations

Only mutate PostHog when the user explicitly requests it. Read the current
object first, inspect the mutation schema, and use CLI `call --dry-run` before
executing when available. Destructive CLI calls require `--confirm`; verify the
exact target ID before adding it.

Official references:

- <https://posthog.com/docs/cli>
- <https://posthog.com/docs/model-context-protocol>
