# Prepare a Fluid Linear issue

Produce an approved-plan candidate. Do not edit product code.

## Check the contract

Confirm that the issue defines:

- the observable outcome and affected actor;
- testable acceptance criteria, including important failure behavior;
- authorization, data-integrity, and operational constraints when applicable;
- explicit scope boundaries;
- dependencies and the highest useful testing seam.

When a material product choice is missing, stop and identify the decision. Use
`fluid:to-prd` only when the user asks to resolve the gap as a PRD. Do not create
a redundant PRD for a sufficient issue.

## Establish the issue's role

Use this bounded context ladder before repository exploration:

1. Read the selected issue in full.
2. Follow each explicit `parent` link to the top ancestor. Read every ancestor
   description because each one constrains the selected issue's purpose.
3. Read active `blocks` and `blockedBy` relations from Linear triage.
4. If the issue has a parent, inspect that parent's direct children as sibling
   summaries: identifier, title, state, and dependency relations.
5. Read a sibling description only when its ownership overlaps the selected
   issue or the boundary is unclear.
6. If the issue has children, inspect their summaries to determine whether the
   selected issue is an actionable slice or a coordination parent.
7. If no explicit parent exists and the role remains unclear, scan issue
   summaries in the same Project for an obvious containing outcome. Read only
   plausible candidate descriptions and report the missing hierarchy. Never
   infer or create a parent silently.
8. Read linked Project documents only when the hierarchy and relations do not
   supply a necessary constraint.

Record a concise role statement with:

- the parent outcome or candidate parent;
- the selected issue's responsibility;
- sibling responsibilities that bound its scope;
- upstream and downstream dependencies;
- explicit boundaries that prevent duplicate work.

Hierarchy supplies context only. Blocking relations remain the source of work
order and readiness.

## Explore narrowly

1. Read all applicable `AGENTS.md` files and repository-local guidance.
2. Locate the highest existing seam that can prove the requested behavior.
3. Inspect the implementation around that seam, adjacent tests, relevant ADRs,
   and established domain vocabulary.
4. Record architectural constraints and third-party boundaries. Avoid an
   exhaustive repository survey.

## Write the plan

Read and follow `fluid:fluid-prd-to-plan`, using the Linear issue as its source.
Write the plan to `./plans/<issue-id-lower>-<slug>.md` in the implementation
repository.

The plan must:

- preserve the issue URL and scope boundaries;
- include the issue role statement and relevant parent outcome;
- extract durable schema, route, authorization, and external-system decisions;
- use thin, end-to-end tracer-bullet phases;
- map every acceptance criterion to at least one phase;
- carry forward testing decisions and out-of-scope items;
- name unresolved decisions without inventing answers;
- list proportional verification for each phase.

## Decide issue granularity

Default to implementing the approved plan as one issue. Evaluate the plan as a
whole before proposing children. Recommend decomposition only when the plan is
too large or structurally unsuitable to implement, review, and verify as one
change. Strong signals are separate repository or pull-request boundaries,
distinct owners or active blockers that require independent scheduling, or a
dependency or deployment order that requires independent delivery.

Do not recommend a child merely because a tracer-bullet phase is independently
mergeable or verifiable. Multiple phases are normal within one issue.

When decomposition is not warranted, hand off the original issue and approved
plan for implementation without proposing children. When it is warranted,
propose child titles, descriptions, and blocking order, then ask for explicit
approval before creating them. Keep blocking relations as the source of work
order; parent relationships do not inherit blockers. Treat approved children as
implementation-ready slices of the parent plan; do not recursively prepare or
decompose them unless a newly discovered material gap makes one non-actionable.
Keep `ready-for-agent` off unless the user explicitly approves it for each
actionable issue.

## Completion criterion

Finish only when:

- the contract is sufficient or every material gap is explicit;
- the plan candidate exists at the reported path;
- every acceptance criterion maps to a phase;
- the issue's parent outcome, responsibility, sibling boundaries, and dependency
  role are explicit;
- blockers, risks, validation, and proposed child boundaries are visible;
- the user has received the phase list and either a direct implementation
  handoff or, only when decomposition is warranted, a request to approve the
  proposed children;
- no product code or Linear data changed.
