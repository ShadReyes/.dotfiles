---
name: select-work
description: Orient to a Fluid Current-team Linear Project or issue, run dependency-aware triage, and recommend one existing issue or a small parallel-safe batch to prepare next. Use when deciding what Fluid work to take on, learning the high-level purpose and boundaries of a Project or issue, or producing an approved handoff for parallel preparation.
---

# Select Fluid work

Produce a read-only work proposal. Learn enough to explain the work before
selecting it, but do not prepare issues, implement code, create worktrees, or
mutate Linear.

## Establish the scope

Require one Fluid Linear Project name or one Current-team issue ID or URL. If
given an issue, center the analysis on that issue and use its Project as the
triage boundary. If given a Project, consider its active issues.

Read and follow `fluid:linear-fluid`, then read and follow
`fluid:linear-triage`. Run the triage script for the identified Project before
recommending any work.

## Orient at a high level

Build a bounded orientation from the Project summary, selected issue
description, hierarchy, direct relations, and only the linked documents needed
to understand the intended outcome or a shared contract. Inspect sibling
summaries when they clarify ownership or boundaries. Use workspace guidance and
narrow repository inspection only when the likely implementation repository or
system boundary is ambiguous; do not perform preparation-level code discovery.

Report:

- the intended product outcome and affected actor;
- the selected issue's role, scope boundaries, and dependency position;
- the likely implementation repository for each actionable issue;
- cross-issue schemas, APIs, identities, deployment ownership, or other shared
  decisions that could couple otherwise parallel work;
- material unknowns that must be resolved before implementation.

Distinguish evidence from inference and link the Linear records used.

## Select the next work

Use issue status and active blocking relationships from `linear-triage` as the
source of readiness and order. Do not reorder work using Linear priority,
estimate, assignee, Initiative membership, or labels other than
`ready-for-agent`.

Prefer one issue. Recommend a small parallel batch only when every issue:

- is actionable at the same time and has no blocking path to another issue in
  the batch;
- owns a separable repository, delivery boundary, or non-overlapping change;
- contributes to one coherent outcome;
- has explicit shared contracts and synchronization points;
- is implementation work rather than a coordination parent whose children own
  the work.

Do not maximize worker count. When parallelism would create semantic or merge
risk, recommend the next single issue or sequential waves instead. If the
selected issue is blocked, identify its actionable blocker before unrelated
work.

Select existing issues only. If the desired outcome has no actionable issue or
requires decomposition, describe the gap and recommend
`fluid:work-linear-issue Prepare` for granularity analysis or
`fluid:linear-create` for user-approved issue creation. Do not draft or create
issues in this skill.

## Propose the handoff

Return:

1. The Project or issue scope and orientation brief.
2. The triage result, including blockers and work order.
3. The recommended issue or batch, with issue URLs, repository mapping,
   responsibility, and readiness evidence.
4. Parallel waves, shared contracts, synchronization points, risks, and
   unresolved decisions.
5. The exact next invocation. Use `$fluid:work-linear-issue Prepare <issue>`
   for ordinary single-issue preparation. Use
   `$fluid:herdr-orchestrate-linear-work Prepare` with the complete approved
   batch when the user wants Herdr-backed parallel preparation.

Ask for explicit approval of the proposed issue set and repository mapping.
Keep Linear, Git, Herdr, and external systems unchanged.
