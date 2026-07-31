---
name: mist-desktop-debugging
description: Diagnose Mist chat sessions, AI harness operations, and Fluid workflows from evidence under /Users/shadrac/Fluid plus local AI DevTools traces. Use when a Mist conversation, tool call, workflow, attachment, generated artifact, or state-changing action behaves unexpectedly; when a chat appears missing, stalled, duplicated, or incomplete; when runtime AI sequencing, provider behavior, or token/timing evidence is needed; or when correlating chat activity with Fluid workspace history. Locate and interpret local artifacts without documenting Mist Desktop's implementation.
---

# Mist Desktop Debugging

Investigate Mist as Fluid's chat and workflow harness. Treat its persisted artifacts as the
primary evidence surface. Do not turn an investigation into an architecture description of the
Mist Desktop application.

## Guardrails

- Begin read-only. Do not edit, delete, replay, or repair artifacts unless the user explicitly
  requests a fix after the diagnosis.
- Treat prompts, messages, tool inputs/results, attachment metadata, cookies, signed URLs, and
  customer data as sensitive. Summarize or redact them in reports and command output.
- Prefer metadata and structural queries before reading message bodies or tool payloads.
- Distinguish observed facts, supported inferences, and unresolved unknowns.
- Do not assume a display-cased directory under `.workspace` maps to a similarly named
  lower-case working directory. Confirm the relationship from identifiers, timestamps, and
  contents.
- Do not assume a persisted schema is the canonical schema of an AI library. Treat the local
  DevTools trace store as an observed third-party schema, not a canonical AI SDK contract.

## Load references

- Read [fluid-directory.md](references/fluid-directory.md) before searching
  `/Users/shadrac/Fluid`.
- Read [ai-tooling.md](references/ai-tooling.md) when the symptom involves streaming, model
  output, message persistence, tool calls, tool results, or an AI SDK/provider error.
- Read [local-ai-devtools.md](references/local-ai-devtools.md) before starting, attaching to,
  inspecting, or clearing a local AI trace session.

## Investigation workflow

### 1. Define the incident

Capture the workspace or company, workflow or skill name, approximate local time, chat title or
ID if known, expected behavior, observed behavior, and whether any state-changing action
completed. If some details are missing, continue with the narrowest defensible time window.

### 2. Choose the evidence path

Start with existing chat, workflow, history, attachment, and generated-file evidence. Add a
local AI trace (see [local-ai-devtools.md](references/local-ai-devtools.md)) when the issue is
reproducible and runtime sequencing, provider behavior, timing, token usage, or
cross-operation correlation would discriminate between hypotheses that persisted artifacts
cannot separate.

Do not rerun a state-changing workflow merely to obtain a trace. Require explicit
authorization and confirm the workflow's recovery policy before replaying any mutation.

**Visual evidence — `cua-driver`.** Persisted artifacts tell you what Mist
recorded; they do not tell you what the user actually saw. When the report is
about rendering, a card that did or didn't appear, a control in the wrong state,
or a renderer-side error, capture the window itself. See the `cua-driver` skill;
it drives GUI apps in the **background without stealing focus**.

```bash
cua-driver list_windows '{"pid":<MIST_PID>}' \
  | jq -r '.windows[] | select(.title|test("Fluid Mist|Developer Tools"))
           | "\(.window_id)\t\(.title)\ton_screen=\(.is_on_screen)"'
cua-driver get_window_state '{"pid":<MIST_PID>,"window_id":<ID>}' \
  --screenshot-out-file /tmp/mist-evidence.png     # ~0.2s
```

The Electron **DevTools window captures legibly too** (Network panel, request
table, console badges), so you can pull renderer-side evidence without attaching
a debugger.

Three constraints, all measured:

- **Always pass `--screenshot-out-file`.** Inline base64 was ~165 KB per
  snapshot straight into context.
- **Assert `on_screen=true` before believing the image.** An off-Space window
  returns the last painted frame — byte-identical across 10 minutes in testing,
  with no staleness signal in the response. You will confidently analyse an
  hours-old picture.
- **For debugging, capture — don't drive.** The harness *is* able to press
  HITL/consent cards (see the `mist-comp:hackathon` runbook §8.4), but that is
  an operational capability, not an investigative one. Clicking a card while
  diagnosing changes the state you are trying to explain, and an
  agent-satisfied gate is never evidence that the gate works for a user.
  Screenshot it and keep investigating.

### 3. Locate the evidence surface

Set the root explicitly:

```bash
fluid_root=/Users/shadrac/Fluid
find "$fluid_root" -maxdepth 2 -mindepth 1 -type d -print
find "$fluid_root" -path '*/.mist-desktop/chats/index.json' -type f -print
```

Use chat indexes and modification times to narrow candidates before searching full chat files.
Include nested workflow surfaces under `skills/.chats` when the issue occurred inside a workflow.

### 4. Identify the chat without dumping it

Inspect an index structurally:

```bash
jq -r '.chats[] | [.lastActiveAt, .id, .title] | @tsv' <index.json>
```

Inspect a candidate chat timeline without printing text, inputs, or results:

```bash
jq -r '.messages[] | [.ts, .role, ([.blocks[]?.type] | join(","))] | @tsv' <chat.json>
jq -r '.messages[].blocks[]? | select(.type == "tool_use") |
  [.toolUseId, .toolName, (.result | type)] | @tsv' <chat.json>
```

When only a phrase or identifier is known, first list matching filenames:

```bash
rg -l -F --glob 'chat-*.json' -- '<needle>' "$fluid_root"
```

Read the minimum matching fragment only after locating the correct file.

### 5. Correlate across artifacts

Build a single chronology from:

1. chat index `createdAt` and `lastActiveAt`;
2. message `ts` values and tool-use identifiers;
3. workflow-specific chat artifacts, run snapshots (`<userData>/workflows/<runId>.json`), and
   diagnostic summaries;
4. `.history/index.json` rows and dated history records;
5. local AI trace runs and steps, joined by the correlation keys in their function
   identifiers (`chatId`, `turnId`, `runId`, `stepId`, `attemptId`);
6. attachment and generated-file modification times.

Search history by stable identifiers before searching prompt text:

```bash
jq -r '.rows[] | select(.chatTurnId == "<id>" or .workflowId == "<id>") |
  [.timestamp, .id, .method, .path, .summary] | @tsv' <history-index.json>
```

Use `stat` to compare filesystem times when timestamps are absent. Account for ISO timestamps,
epoch values, and local filesystem time before claiming an ordering.

If the persisted artifacts do not expose a completion marker or runtime error, state that
limit. Do not treat complete-looking text as proof that a stream closed normally — a local AI
trace of a reproduction is the discriminating evidence for stream lifecycle, and a trace in
turn proves only that an instrumented operation emitted events, not that persistence or a
domain mutation completed.

### 6. Classify the failure boundary

Classify the strongest supported boundary:

- discovery/indexing: artifact exists but is absent or stale in an index;
- persistence: a message, block, result, or generated artifact is incomplete or missing;
- AI lifecycle: text/tool progression is inconsistent or a provider/SDK error is recorded;
- tool execution: invocation exists but its result or intended side effect does not;
- workflow orchestration: the wrong step, nested chat, or correlation ID was used;
- domain mutation: history shows a request, response status, or state transition problem;
- presentation: persisted evidence is complete but the visible session is not.

Do not assign a root cause merely because a file is absent; first establish whether that artifact
should exist for the observed action.

### 7. Report and recommend

Return:

- the symptom and investigated scope;
- a compact chronology with artifact paths and IDs;
- verified facts;
- the most likely boundary and why;
- alternative explanations;
- the next discriminating check;
- a repair recommendation only if the evidence supports one.

Link local files when useful. Do not reproduce sensitive payloads. If evidence points into
application source or a third-party package, hand off to the relevant codebase or technology
skill with the artifact chronology attached.
