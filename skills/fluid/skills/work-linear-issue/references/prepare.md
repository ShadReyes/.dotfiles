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
- extract durable schema, route, authorization, and external-system decisions;
- use thin, end-to-end tracer-bullet phases;
- map every acceptance criterion to at least one phase;
- carry forward testing decisions and out-of-scope items;
- name unresolved decisions without inventing answers;
- list proportional verification for each phase.

## Recommend issue granularity

Recommend a child issue when a phase is independently mergeable and verifiable,
has a distinct blocker or owner, crosses a repository boundary, or warrants a
separate pull request. Keep blocking relations as the source of work order;
parent relationships do not inherit blockers.

Propose child titles, descriptions, and blocking order when useful. Do not
create them without approval. Keep `ready-for-agent` off unless the user
explicitly approves it for each actionable issue.

## Completion criterion

Finish only when:

- the contract is sufficient or every material gap is explicit;
- the plan candidate exists at the reported path;
- every acceptance criterion maps to a phase;
- blockers, risks, validation, and proposed child boundaries are visible;
- the user has received the phase list and a request for granularity approval;
- no product code or Linear data changed.
