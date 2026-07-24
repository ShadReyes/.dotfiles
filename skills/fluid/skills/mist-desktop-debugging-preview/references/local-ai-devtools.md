# Local AI DevTools preview

Use these commands only with a `fluid-mono` checkout that contains PR #7279 or equivalent local
changes. Treat source and command output as authoritative because the feature is not merged yet.

## Confirm availability

From the monorepo root:

```bash
jq '{dev_ai:.scripts["dev:ai"], devtools:.scripts.devtools, clear:.scripts["traces:clear"]}' \
  apps/mist-desktop/package.json
```

If any script is absent, stop using this reference and continue with persisted Fluid evidence.

## Start or attach

Start Mist with tracing and the viewer:

```bash
MIST_DEV_INSTANCE=debug-incident pnpm --filter mist-desktop dev:ai
```

`dev:ai` launches both Mist with `MIST_AI_DEVTOOLS=1` and the localhost viewer. The startup line
prints the selected instance, exact trace-store path, and viewer URL.

Start only the viewer when Mist is already trace-enabled or when inspecting stored traces:

```bash
MIST_DEV_INSTANCE=debug-incident pnpm --filter mist-desktop devtools
```

Starting `devtools` does not enable tracing in an ordinary Mist process. To control the processes
separately:

```bash
MIST_DEV_INSTANCE=debug-incident MIST_AI_DEVTOOLS=1 \
  pnpm --filter mist-desktop start
MIST_DEV_INSTANCE=debug-incident pnpm --filter mist-desktop devtools
```

Use the same `MIST_DEV_INSTANCE` for Mist, viewer, and cleanup. Override the viewer port with
`MIST_AI_DEVTOOLS_PORT` when necessary. A viewer failure is non-fatal to Mist.

## Reproduce safely

1. Record the local start time and chosen instance.
2. Prefer a non-mutating or synthetic reproduction.
3. Do not replay state-changing workflow steps without explicit authorization.
4. Capture the visible `chatId`, `runId`, `stepId`, or diagnostic ID when available.
5. Reproduce once, then inspect before generating additional noise.

Development Sentry is intentionally unavailable. Use the DevTools viewer, terminal output,
persisted chat/workflow evidence, and mutation history.

## Inspect and correlate

Search trace function identifiers for:

- `chatId` and `turnId` to isolate a chat operation;
- `runId`, `stepId`, and `attemptId` to isolate workflow execution and recovery;
- `provider`, `modelId`, `providerRequestId`, and `phase` for provider boundaries;
- operation names such as `mist.chat.turn`, `mist.chat.compaction`,
  `mist.chat.tool-call-repair`, and `mist.advisors.*`.

Use traces to establish runtime ordering and metadata, then correlate them with chat timestamps,
tool-use IDs, workflow diagnostics, and `.history` mutations. A trace proves that an instrumented
operation emitted an event; it does not by itself prove that UI persistence or a domain mutation
completed.

If direct store inspection is necessary, use the exact path printed at startup. Inspect its shape
before querying it:

```bash
jq 'keys' <generations.json>
jq '{runs:(.runs | length), steps:(.steps | length)}' <generations.json>
```

Treat those keys as an observed DevTools 1.0.7 storage shape, not a stable contract.

## Locate workflow snapshots and summaries

The preview branch currently persists workflow state beneath the same named instance's
`<userData>/workflows/` directory:

- `<runId>.json` contains the run snapshot, steps, attempts, diagnostics, transitions, recovery
  decisions, and recovery attempts.
- `diagnostics/<runId>-<timestamp>.json` contains a compact sanitized summary created from the
  workflow card.

Derive `<userData>` from the trace-store path printed by `dev:ai`; do not guess it from the
workspace name. Confirm the current location in
`src/main/services/workflow-orchestrator.service.ts` before relying on it.

Inspect structure before content:

```bash
jq '{runId, workflowSlug, status, outcome,
  steps:[.steps[] | {id, status, attemptCount:(.attempts | length)}]}' \
  <userData>/workflows/<runId>.json
```

Do not create a diagnostic summary merely to satisfy the investigation. If the user already
created one, treat it as a bounded support artifact and correlate it by `runId` and timestamp.

## Payload capture

Default traces omit prompts, responses, reasoning, tool payloads, provider bodies, credentials,
and files. For a controlled local reproduction where content is necessary:

```bash
MIST_DEV_INSTANCE=debug-incident \
MIST_AI_DEVTOOLS_CAPTURE_PAYLOADS=1 \
pnpm --filter mist-desktop dev:ai
```

Payload capture is bounded and redacts recognized secret fields, but it can still retain customer
content. Minimize output, do not quote sensitive values in the report, and clear the trace only
after the investigation is complete and cleanup is authorized.

## Clear a completed session

```bash
MIST_DEV_INSTANCE=debug-incident pnpm --filter mist-desktop traces:clear
```

The cleanup command deletes only that named instance's `.devtools` store. Never substitute a
broader manual deletion command.

## Source-of-truth files

Inspect these instead of copying implementation constants into an incident report:

- `apps/mist-desktop/scripts/ai-devtools.mjs`
- `apps/mist-desktop/scripts/clear-ai-traces.mjs`
- `apps/mist-desktop/src/main/ai-devtools.ts`
- `apps/mist-desktop/src/main/ai-telemetry.ts`
- `apps/mist-desktop/src/shared/workflow-diagnostics.ts`
- `apps/mist-desktop/src/main/sentry.ts`

Local traces own development AI execution evidence. Workflow snapshots own workflow state and
diagnosis, mutation history owns domain actions, usage reporting owns billing, and production
Sentry owns content-free terminal failure events. Do not treat these as interchangeable.
