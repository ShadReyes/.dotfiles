---
name: mist-desktop-debugging-preview
description: Diagnose Mist chat sessions, AI SDK operations, tool calls, and Fluid workflows using persisted evidence plus the local AI DevTools introduced by fluid-mono PR #7279. Use while that PR is unmerged when a Mist conversation, provider call, tool repair, workflow attempt, attachment, generated artifact, or state-changing action is missing, stalled, duplicated, incomplete, slow, or otherwise unexpected.
---

# Mist Desktop Debugging Preview

Investigate Mist from persisted artifacts first, then use the preview branch's local AI traces
when the symptom requires runtime evidence. Do not turn an investigation into a general
architecture description.

This is a temporary companion to `$fluid:mist-desktop-debugging`. Before relying on trace
commands, confirm that the active `fluid-mono` checkout contains the `dev:ai`, `devtools`, and
`traces:clear` scripts. If it does not, use the stable skill without the trace workflow.

## Guardrails

- Begin read-only. Do not edit, delete, replay, clear, or repair evidence unless the user
  explicitly requests it.
- Treat prompts, responses, reasoning, tool inputs/results, attachment metadata, cookies,
  signed URLs, and customer data as sensitive.
- Prefer identifiers, metadata, and structural queries before reading payloads.
- Distinguish observed facts, supported inferences, and unresolved unknowns.
- Do not assume a display-cased `.workspace` directory maps to a similarly named working
  directory. Establish the relationship from identifiers, timestamps, and contents.
- Treat DevTools storage as an observed third-party schema, not a canonical AI SDK contract.
- Do not expect development evidence in Sentry. The preview branch initializes Sentry only in
  packaged production builds.

## Load references

- Read [fluid-directory.md](references/fluid-directory.md) before searching
  `/Users/shadrac/Fluid`.
- Read [ai-tooling.md](references/ai-tooling.md) for streaming, model output, persistence, tool
  lifecycle, provider, or AI SDK symptoms.
- Read [local-ai-devtools.md](references/local-ai-devtools.md) before starting, attaching to,
  inspecting, or clearing a local trace session.

## Investigation workflow

### 1. Define the incident

Capture the workspace or company, workflow or skill, approximate local time, chat title or ID,
expected behavior, observed behavior, and whether a state-changing action completed. Continue
with the narrowest defensible time window when details are missing.

### 2. Choose the evidence path

Start with existing chat, workflow, history, attachment, and generated-file evidence. Add a
local trace only when the issue is reproducible and runtime sequencing, provider behavior,
repair, timing, or cross-operation correlation would discriminate between hypotheses.

Do not rerun a state-changing workflow merely to obtain a trace. Require the user's explicit
authorization and confirm the workflow's recovery policy before replaying any mutation.

### 3. Locate persisted evidence without dumping it

Set the root explicitly and enumerate current surfaces:

```bash
fluid_root=/Users/shadrac/Fluid
find "$fluid_root" -path '*/.mist-desktop/chats/index.json' -type f -print
find "$fluid_root" -path '*/skills/.chats/*' -type d -print
```

Use indexes and modification times before opening chat files:

```bash
jq -r '.chats[] | [.lastActiveAt, .id, .title] | @tsv' <index.json>
jq -r '.messages[] | [.ts, .role, ([.blocks[]?.type] | join(","))] | @tsv' <chat.json>
```

Search stable identifiers before prose:

```bash
rg -l -F --glob 'chat-*.json' -- '<identifier>' "$fluid_root"
```

### 4. Add trace evidence when needed

Follow [local-ai-devtools.md](references/local-ai-devtools.md). Use a dedicated
`MIST_DEV_INSTANCE`, record the reproduction time, and correlate trace function identifiers by
`chatId`, `turnId`, `runId`, `stepId`, and `attemptId`.

Default traces are structural. Enable payload capture only for a controlled local reproduction
where its diagnostic value justifies retaining potentially sensitive content. Do not clear the
trace store until the investigation is complete and the user has authorized cleanup.

### 5. Build one chronology

Correlate:

1. chat index and message timestamps;
2. tool-use identifiers and result presence;
3. workflow run, step, attempt, and diagnostic identifiers;
4. trace operations and provider/model metadata;
5. `.history` mutation records;
6. attachment and generated-file timestamps.

Account for ISO timestamps, epoch values, and local filesystem time. A complete-looking message
does not prove that its stream closed normally.

### 6. Classify the failure boundary

Select the strongest supported boundary:

- discovery/indexing;
- persistence;
- AI lifecycle or provider;
- tool-call repair or execution;
- workflow orchestration or recovery;
- domain mutation;
- presentation.

Do not assign a root cause from an absent artifact until establishing that the artifact should
exist.

### 7. Report and recommend

Return:

- the symptom and investigated scope;
- a compact chronology with paths and correlation IDs;
- verified facts;
- the most likely boundary and why;
- alternative explanations;
- the next discriminating check;
- a repair recommendation only when supported by evidence.

Link local files when useful and redact sensitive payloads. If evidence points into application
source or a third-party package, hand off with the chronology, resolved package versions, and
minimal failing artifact shape attached.
