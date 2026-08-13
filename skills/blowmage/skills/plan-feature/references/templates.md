# Adaptable Feature-Planning Templates

Use these as composable sections, not a mandatory file set. Preserve project-native filenames, metadata, headings, and vocabulary. Delete irrelevant sections and every placeholder.

## Table of Contents

- [Select artifacts](#select-artifacts)
- [Overview](#overview)
- [Specification](#specification)
- [Implementation plan](#implementation-plan)
- [Task list](#task-list)
- [Multi-phase root](#multi-phase-root)
- [Phase record](#phase-record)
- [Research findings](#research-findings)
- [Optional index](#optional-index)

## Select Artifacts

Create only what the current stage supports:

| Need | Smallest useful artifact |
|---|---|
| Capture an idea and boundaries | Overview |
| Agree on behavior | Specification |
| Agree on technical direction | Implementation plan |
| Execute approved work | Task list |
| Coordinate dependent slices | Multi-phase root plus phase records |
| Preserve supporting evidence | Research note |

Combine roles in one document when the project prefers a single RFC or proposal. Keep the conceptual boundaries visible through sections.

## Overview

```markdown
# {Work Name}

**Type:** {project-native work type}
**Status:** {project-native status}

## Outcome

{Two or three plain-language sentences describing the problem, the intended change, and who benefits.}

## Boundaries

- In scope: {deliverable behavior}
- Out of scope: {explicit exclusion}

## Success

- [ ] {Observable outcome}
- [ ] {Observable outcome}

## Documents

| Document | Purpose |
|---|---|
| [{link}]({path}) | {What belongs there} |

## Open Decisions

- {Question} — close when {evidence, experiment, or stakeholder decision}
```

Add dependencies, rollout notes, or risks only when they help orient the reader. Do not duplicate the detailed plan.

## Specification

```markdown
# {Work Name}: Specification

**Status:** {status}

## Problem

### Current State

{Verified behavior with citations to code, tests, issues, data, or research.}

### Desired Outcome

{Behavior after the change, without prescribing implementation unnecessarily.}

## Invariants

- **INV-1: {Checkable rule}.**
  {Concrete meaning and boundary conditions.}
- **INV-2: {Checkable rule}.**
  {Concrete meaning and boundary conditions.}

## Requirements

### R-1: {Requirement Name}

**Invariants:** INV-1

{Required behavior.}

**Acceptance criteria**

- AC-1.1: {Observable, testable criterion}
- AC-1.2: {Observable, testable criterion}

**If omitted**

{Specific failure or missing capability, with evidence.}

## Simplest Credible Alternative

{Describe the smaller option fairly, what it buys, and the evidenced gaps it leaves.}

## Out of Scope

- {Explicit exclusion and, when useful, its destination}

## Assumptions and Open Questions

- Assumption: {claim not yet verified} — verify with {source or experiment}
- Open: {decision} — close when {condition}
```

Use IDs only when traceability benefits from them. Preserve a project’s existing ID scheme when present.

## Implementation Plan

```markdown
# {Work Name}: Implementation Plan

**Status:** {status}

## Approach

{How the proposed change satisfies the specification.}

## System Changes

### {Component or Boundary}

**Location:** `{path, service, interface, or system}`

- Responsibility: {what it owns}
- Change: {what changes}
- Invariants: {INV-N or project-native requirement IDs}
- Compatibility: {how existing consumers behave}

## Data and Control Flow

1. {Trigger or input}
2. {Processing boundary}
3. {State change or output}

## Decisions

### Locked

- {Confirmed choice} — {evidence or rationale}

### Discretionary

- {Choice left to implementation}

### Deferred

- {Excluded change} — {future destination}

### Open

- {Question} — close when {evidence or decision}

## Delivery

| Slice | Outcome | Requirements | Depends on | Unblocked when |
|---|---|---|---|---|
| {slice} | {observable capability} | {IDs} | {dependency} | {criterion} |

## Verification

- {Test or inspection proving an invariant}
- {Integration or end-to-end behavior}
- {Migration, rollout, observability, or rollback check when relevant}
```

Use small interface examples only when prose cannot make a boundary precise.

## Task List

```markdown
# {Work Name}: Tasks

**Status:** {status}

## Requirement Coverage

| Requirement | Delivery slice | Status | Verification |
|---|---|---|---|
| R-1 | {slice} | Not started | {planned evidence} |

## {Delivery Slice}

**Outcome:** {Observable capability delivered by this slice}

- [ ] Pin the current or desired behavior with {test/evidence}
- [ ] Implement {specific change}
- [ ] Verify {specific success or failure path}
- [ ] Record {rollout/migration/observability work, if relevant}

**Complete when**

- [ ] {Observable criterion} — Verified by: {evidence once complete}
```

Write tasks that an implementer can complete and verify. Avoid placeholder tasks such as “handle edge cases” or “add tests.”

## Multi-Phase Root

```markdown
# {Work Name}

**Status:** {status}

## Outcome

{Outcome shared by all phases.}

## Shared Invariants

- **INV-1: {Checkable rule}.**

## Phases

| Phase | Outcome | Depends on | Unblocked when | Status |
|---|---|---|---|---|
| [{phase}]({link}) | {independently testable capability} | None | Ready | {status} |
| [{phase}]({link}) | {independently testable capability} | {phase} | {verified criterion} | {status} |

## Cross-Phase Decisions

{Only decisions and constraints shared by multiple phases.}

## Overall Success

- [ ] {Observable outcome spanning the phases}
```

Do not create a phase merely to reserve a number. Describe it in the root table until meaningful phase content exists.

## Phase Record

```markdown
# {Phase Name}

**Status:** {status}
**Depends on:** {phase or prerequisite}
**Delivers:** {observable capability}

## Scope

- In: {behavior delivered here}
- Out: {behavior left to another phase}

## Owned Requirements

- {requirement or invariant IDs}

## Plan

{Phase-specific system changes and decisions.}

## Complete When

- [ ] {Behavior} — verified by {evidence}
```

Split a phase record into separate spec, plan, and task artifacts only when its complexity warrants it or the repository requires it.

## Research Findings

```markdown
# Findings

## Corrected Claims

- {Earlier claim} was incorrect because {verified evidence}. The plan now {correction}.

## Review Findings

| ID | Finding | Evidence | Resolution | Plan updates |
|---|---|---|---|---|
| F-1 | {review finding} | {citation} | {decision or change} | {links to updated sections} |
```

Treat the table as an index. Update the specification, plan, and tasks themselves so the primary record does not remain stale.

## Optional Index

Create or update an index only when the repository uses one or the user requests it.

```markdown
# Planned Work

| Work | Type | Status | Outcome |
|---|---|---|---|
| [{name}]({path}) | {type} | {status} | {brief outcome} |
```
