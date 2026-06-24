---
name: bug-to-plan
description: Turn a bug discovery, bug report, support escalation, QA finding, production incident, or issue tracker ticket into a precise issue understanding and an implementation plan. Use when the user wants to clarify what is actually broken, decide expected product behavior, identify important open product decisions, create a bug-fix plan, convert a bug report into phases, or prepare a plan before implementation.
---

# Bug to Plan

Use this skill to move from "something is wrong" to a shared understanding of the issue and a fix plan that can be implemented without guessing product behavior.

## Process

### 1. Confirm the source material

Use the bug report, ticket, screenshots, logs, reproduction notes, user quotes, or conversation already in context. If the issue is too vague to identify the behavior, ask for the missing raw material before planning.

Extract:

- **Observed behavior**: what actually happens
- **Expected behavior**: what should happen, if known
- **Actor and workflow**: who is affected and what they were trying to do
- **Reproduction**: steps, inputs, environment, account type, device, browser, version, or data state
- **Evidence**: logs, screenshots, URLs, traces, IDs, timestamps, metrics, or customer reports
- **Impact**: severity, frequency, customer or business impact, data correctness, revenue, compliance, or trust risk

### 2. Establish the issue exactly

Explore the repo when the bug relates to local code. Use the project glossary and ADRs if they exist. Distinguish facts from hypotheses and product decisions.

Before proposing a fix, present a concise issue understanding:

- **Problem statement**: the user-facing problem in plain language
- **Actual vs expected**: what diverges from intended behavior
- **Scope**: affected and explicitly unaffected workflows, roles, platforms, states, or data
- **Repro confidence**: confirmed, likely, intermittent, or unknown
- **Likely area**: subsystem or integration boundary, framed as a hypothesis unless proven
- **Non-goals**: nearby improvements that should not be bundled into this bug fix

If the report describes symptoms without a clear root cause, say so. Do not turn a guessed root cause into a plan assumption.

### 3. Force product decisions into the open

Ask only decision questions that could change the implementation, tests, rollout, or user experience. Prefer a short decision checkpoint with recommended defaults when the codebase or product pattern supports one.

Product decisions commonly include:

- **Correct behavior**: what should happen in the failing scenario and adjacent edge cases
- **State and data repair**: whether existing bad records need migration, backfill, cleanup, or no-op handling
- **Permissions and visibility**: which users can see or perform the corrected behavior
- **Error handling**: whether to block, retry, degrade gracefully, warn, or silently recover
- **Notifications and messaging**: what users, admins, or support should see
- **Compatibility**: whether legacy clients, old data, imports, exports, or integrations must keep working
- **Rollout**: feature flag, staged release, monitoring, support comms, or rollback expectation
- **Success criteria**: what observable signal proves the bug is fixed

Do not bury unresolved product decisions in the plan. If the user wants momentum and a reasonable default exists, mark it as an **Assumption needing approval**.

### 4. Pick test seams

Sketch the highest useful test seam before planning implementation. Prefer existing seams and external behavior over implementation details.

Consider:

- Reproduction test that fails before the fix
- Regression coverage at the API, service, UI, worker, integration, or end-to-end seam
- Data repair or migration verification, when relevant
- Manual verification steps for hard-to-automate cases

Check with the user when the seam choice changes scope, cost, or confidence.

### 5. Draft the fix strategy

Identify durable implementation decisions that should survive later refactors:

- Route, API, event, job, or workflow boundaries
- Data model or schema shape
- State machine, validation, authorization, or integration contract
- Backfill, migration, cache invalidation, idempotency, or rollback approach

Avoid brittle file names, function names, and code snippets unless the user explicitly needs a code-level plan or a prototype clarified a decision more precisely than prose can.

### 6. Slice the work vertically

Break the fix into tracer-bullet phases. Each phase should be independently verifiable and cut through every required layer for a narrow behavior, not isolate one technical layer.

Good bug-fix phases often look like:

1. Reproduce and lock expected behavior
2. Implement the smallest end-to-end correction
3. Repair existing data or edge states, if needed
4. Add observability, rollout guards, and cleanup, if risk justifies it

Present the proposed phases with the user stories or workflows covered. Ask whether the granularity is right and whether any phase should be merged or split when the plan depends on collaboration or unresolved decisions.

### 7. Write the plan

When the issue understanding and product decisions are clear enough, create `./plans/` if it does not exist and write a Markdown plan named after the bug, such as `./plans/fix-duplicate-invoices.md`. If there is no local repo or the user asks for chat-only output, present the same structure inline.

Use this template:

```markdown
# Plan: Fix <Bug Name>

> Source bug report: <ticket, URL, incident, support thread, or "conversation">

## Issue Understanding

- **Problem statement**: ...
- **Actual behavior**: ...
- **Expected behavior**: ...
- **Affected scope**: ...
- **Repro confidence**: ...
- **Impact**: ...
- **Likely area**: ...

## Product Decisions

### Confirmed

- **Decision**: ...

### Assumptions Needing Approval

- **Assumption**: ...

### Out of Scope

- ...

## Implementation Decisions

- **Boundary**: ...
- **Data shape**: ...
- **Rollout**: ...

## Testing Decisions

- **Primary seam**: ...
- **Regression coverage**: ...
- **Manual verification**: ...

---

## Phase 1: <Title>

**Workflow covered**: <user/workflow/repro path>

### What to build

<Concise vertical-slice description.>

### Acceptance criteria

- [ ] ...
- [ ] ...

---

## Phase 2: <Title>

**Workflow covered**: ...

### What to build

...

### Acceptance criteria

- [ ] ...
```

## Operating Rules

- Make the issue understandable before making the plan.
- Ask about product behavior before committing to implementation shape.
- Treat root cause as unknown until evidence supports it.
- Keep questions concise and decision-oriented.
- Prefer fewer, higher-value tests over broad implementation-detail coverage.
- Keep unrelated refactors and opportunistic improvements out of scope unless they are required to fix the bug safely.
