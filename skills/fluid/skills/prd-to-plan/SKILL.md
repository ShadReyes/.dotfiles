---
name: prd-to-plan
description: Turn a Fluid PRD from the conversation, a local Markdown file, or a Fluid Linear issue into an approved multi-phase implementation plan using tracer-bullet vertical slices.
---

# Fluid PRD to Plan

Convert an approved PRD into a phased implementation plan. Preserve the PRD's
user-story numbering, architectural constraints, testing decisions, and scope
boundaries.

## Resolve the PRD source

Accept the first source explicitly identified by the user:

1. PRD content in the current conversation.
2. A local path, normally under `docs/prds/`.
3. A Fluid Linear issue URL or identifier.

Read Linear issues through `fluid:linear-fluid` and use the issue description as
the PRD source. Preserve the issue URL in the plan header. If no source exists,
ask the user to paste the PRD or provide a local path or issue identifier.

## Process

1. Explore the repository if its architecture and integration layers are not
   already understood.
2. Extract durable architectural decisions before slicing. Include route
   structures, schema shape, data models, authorization, and third-party
   boundaries when relevant.
3. Map every phase to the numbered user stories it advances.
4. Draft thin tracer-bullet vertical slices. Each slice must cross the needed
   schema, API, UI, and test boundaries end-to-end and be demoable or
   verifiable independently.
5. Prefer many narrow complete slices over a few broad phases. Avoid
   horizontal layer-by-layer work and unstable file or function names.
6. Present the proposed phase titles and covered user stories. Ask whether the
   granularity is too coarse or too fine and iterate until approved.
7. Write the approved plan to:

```text
./plans/<feature-slug>.md
```

The path is relative to the repository in which the skill is invoked. Do not
update Linear with a plan backlink unless the user explicitly requests it.

## Plan structure

```md
# Plan: <Feature Name>

> Source PRD: <local path or Linear URL>

## Architectural decisions

- **Routes**: ...
- **Schema**: ...
- **Key models**: ...
- **Authorization**: ...
- **External boundaries**: ...

---

## Phase 1: <Title>

**User stories**: <numbered stories>

### What to build

Describe the end-to-end behavior of this slice.

### Acceptance criteria

- [ ] Observable criterion
- [ ] Observable criterion

<!-- Repeat for each phase. -->
```

Keep acceptance criteria externally observable and testable. Carry forward
testing decisions and explicit out-of-scope items from the source PRD.
