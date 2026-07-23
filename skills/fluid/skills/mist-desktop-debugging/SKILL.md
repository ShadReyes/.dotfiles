---
name: mist-desktop-debugging
description: Diagnose Mist chat sessions and Fluid workflows from evidence stored under /Users/shadrac/Fluid. Use when a Mist conversation, tool call, workflow, attachment, generated artifact, or state-changing action behaves unexpectedly; when a chat appears missing, stalled, duplicated, or incomplete; or when correlating chat activity with Fluid workspace history. Locate and interpret local artifacts without documenting Mist Desktop's implementation.
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
- Do not assume a persisted schema is the canonical schema of an AI library.

## Load references

- Read [fluid-directory.md](references/fluid-directory.md) before searching
  `/Users/shadrac/Fluid`.
- Read [ai-tooling.md](references/ai-tooling.md) when the symptom involves streaming, model
  output, message persistence, tool calls, tool results, or an AI SDK/provider error.

## Investigation workflow

### 1. Define the incident

Capture the workspace or company, workflow or skill name, approximate local time, chat title or
ID if known, expected behavior, observed behavior, and whether any state-changing action
completed. If some details are missing, continue with the narrowest defensible time window.

### 2. Locate the evidence surface

Set the root explicitly:

```bash
fluid_root=/Users/shadrac/Fluid
find "$fluid_root" -maxdepth 2 -mindepth 1 -type d -print
find "$fluid_root" -path '*/.mist-desktop/chats/index.json' -type f -print
```

Use chat indexes and modification times to narrow candidates before searching full chat files.
Include nested workflow surfaces under `skills/.chats` when the issue occurred inside a workflow.

### 3. Identify the chat without dumping it

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

### 4. Correlate across artifacts

Build a single chronology from:

1. chat index `createdAt` and `lastActiveAt`;
2. message `ts` values and tool-use identifiers;
3. workflow-specific chat artifacts;
4. `.history/index.json` rows and dated history records;
5. attachment and generated-file modification times.

Search history by stable identifiers before searching prompt text:

```bash
jq -r '.rows[] | select(.chatTurnId == "<id>" or .workflowId == "<id>") |
  [.timestamp, .id, .method, .path, .summary] | @tsv' <history-index.json>
```

Use `stat` to compare filesystem times when timestamps are absent. Account for ISO timestamps,
epoch values, and local filesystem time before claiming an ordering.

If the persisted artifacts do not expose a completion marker or runtime error, state that limit.
Do not treat complete-looking text as proof that a stream closed normally. Search for runtime
logs by filename and time window; if their location is not discoverable, identify runtime logs
as the next evidence source without inventing a path.

### 5. Classify the failure boundary

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

### 6. Report and recommend

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
