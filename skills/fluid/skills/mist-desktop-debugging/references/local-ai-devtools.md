# Local AI DevTools

Merged to `fluid-mono` main in PR #7530 (2026-07-30). Any current checkout has the commands
below; if `jq '.scripts["dev:ai"]' apps/mist-desktop/package.json` returns null, the checkout
predates the feature — update it rather than working around the gap.

## What is traced, and what is not

Instrumented operations (trace `function_id` prefixes):

- `mist.chat.turn` — the main streaming chat turn (`streamText`);
- `mist.chat.compaction` — proactive preflight and reactive (context-overflow retry) history
  compaction, correlated to the triggering chat turn;
- `mist.advisors.debrief`, `mist.advisors.answer`, `mist.advisors.route-question`;
- `mist.test.devtools` — appears only from the test suite.

Deliberately NOT traced:

- transcription and voice streaming — `transcribe`/`streamTranscribe` expose no telemetry
  options, and audio must never be routed through text telemetry as a workaround;
- anything in a packaged build — initialization requires an unpackaged app AND
  `MIST_AI_DEVTOOLS=1`, and `@ai-sdk/devtools` is absent from the packaged runtime closure;
- tool-call repair — that instrumentation belongs to unmerged reliability work. Do not search
  for `mist.chat.tool-call-repair`; its absence is expected, not evidence.

## Start or attach

Start Mist with tracing plus the localhost viewer:

```bash
MIST_DEV_INSTANCE=debug-incident pnpm --filter mist-desktop dev:ai
```

The startup line prints the selected instance, the exact trace-store path, and the viewer URL
(default `http://localhost:4983`). Always derive paths from that line instead of guessing.

Start only the viewer (inspecting stored traces, or attaching to an already trace-enabled
Mist):

```bash
MIST_DEV_INSTANCE=debug-incident pnpm --filter mist-desktop devtools
```

`devtools` (viewer mode) does NOT enable tracing — a plain `pnpm start` emits no traces. To
control the processes separately:

```bash
MIST_DEV_INSTANCE=debug-incident MIST_AI_DEVTOOLS=1 pnpm --filter mist-desktop start
MIST_DEV_INSTANCE=debug-incident pnpm --filter mist-desktop devtools
```

Use the same `MIST_DEV_INSTANCE` for Mist, viewer, and cleanup. Override the viewer port with
`MIST_AI_DEVTOOLS_PORT` (or `AI_SDK_DEVTOOLS_PORT`); valid range 1024–65535. Lifecycle: in
`dev:ai`, a dying viewer leaves Mist running (warning only); Mist exiting kills the viewer.
Initialization failure logs `[ai-devtools] Local tracing unavailable; Mist will continue
without it:` — non-fatal by design.

## Store location and lifecycle

- macOS store: `~/Library/Application Support/mist-desktop-dev[-<instance>]/.devtools/generations.json`.
  Instance names are sanitized (`[^a-zA-Z0-9_-]` → `-`, max 64 chars), so a display name may not
  match the directory literally — trust the startup line.
- Retention is enforced at every initialization: runs older than 14 days are pruned (their
  steps go with them); a store over 25 MB, or one that fails to parse, is DELETED wholesale
  rather than repaired. A missing or freshly-empty `generations.json` after a restart can mean
  retention fired — establish that before treating it as evidence loss.
- `MIST_DEV_INSTANCE=<name> pnpm --filter mist-desktop traces:clear` deletes only that named
  instance's `.devtools` directory. Never substitute a broader manual deletion.

## Correlate

DevTools 1.0.7 does not persist runtime context, so Mist packs correlation into the
`function_id` string itself:

```
<operation> chatId=<v> turnId=<v> runId=<v> stepId=<v> attemptId=<v> phase=<v> projectKind=<v> modelId=<v> provider=<v> providerRequestId=<v> appVersion=<v> environment=<v>
```

Keys appear in that order and only when populated. Values are sanitized to
`[a-zA-Z0-9._:/-]` and capped at 256 chars per token. Ad-hoc chat turns carry
chatId/turnId/projectKind/modelId/provider (plus appVersion/environment defaults); turns and
compactions inside a workflow step additionally carry runId/stepId/attemptId/phase from the
workflow context.

Query the store structurally before reading payloads:

```bash
jq '{runs: (.runs | length), steps: (.steps | length)}' <generations.json>
jq -r '.runs[] | select(.function_id | contains("chatId=<id>")) |
  [.id, .started_at, .function_id] | @tsv' <generations.json>
jq -r --arg run "<run-id>" '.steps[] | select(.run_id == $run) |
  [.step_number, .duration_ms, (.usage | type), (.error | type)] | @tsv' <generations.json>
```

Treat `runs[].{id, function_id, parent_run_id, started_at}` and
`steps[].{run_id, step_number, duration_ms, usage, error, output}` as the observed
DevTools 1.0.7 storage shape, not a stable contract — inspect `keys` first if a query misses.

A trace proves an instrumented operation emitted events. It does not prove UI persistence or a
domain mutation completed. Build the chronology by joining trace identifiers with:

- chat index and `chat-*.json` message timestamps and tool-use IDs;
- workflow run snapshots at `<userData>/workflows/<runId>.json` (steps, attempts, transitions,
  recovery) and compact summaries under `<userData>/workflows/diagnostics/`;
- `.history` mutation records;
- attachment and generated-file timestamps.

## Payload capture

Default traces are content-free and fail closed: `recordInputs`/`recordOutputs` are false, and
because DevTools 1.0.7 records prompt/output fields regardless, Mist's sanitizer strips them
via structural allowlists before the integration sees them — unknown future SDK fields are
dropped, not forwarded. Timing, token usage, step structure, and correlated function IDs
remain.

For a controlled local reproduction where content is necessary:

```bash
MIST_DEV_INSTANCE=debug-incident \
MIST_AI_DEVTOOLS_CAPTURE_PAYLOADS=1 \
pnpm --filter mist-desktop dev:ai
```

Capture is bounded: recognized secret fields are redacted and recursion stops at depth 12 with
`[OMITTED]`, but retained values can still contain customer content. Minimize what you print,
never quote sensitive values in a report, and clear the instance's traces once the
investigation ends and cleanup is authorized.

## Adjacent evidence channels (one owner each)

Local traces own development AI execution evidence. Workflow snapshots own workflow state and
diagnosis. `.history` owns domain mutations. Usage reporting owns billing. Sentry owns crash
evidence — in development it is off by default but CAN be force-enabled with
`MIST_SENTRY_FORCE=1` (`src/main/sentry.ts`); do not expect dev events in Sentry unless that
was set. Do not treat these channels as interchangeable.

## Source-of-truth files

Inspect these instead of copying implementation constants into an incident report:

- `apps/mist-desktop/src/main/ai-devtools.ts` — gating, retention, registration
- `apps/mist-desktop/src/main/ai-telemetry.ts` — correlation grammar, sanitizer allowlists
- `apps/mist-desktop/scripts/ai-devtools.mjs` — instance/store/port resolution, process wiring
- `apps/mist-desktop/scripts/clear-ai-traces.mjs` — cleanup scope
- `apps/mist-desktop/AGENTS.md` — the "AI diagnostics" rules the implementation must uphold
