---
name: plan-feature
description: Create, revise, or audit feature-planning documentation while adapting to the repository's existing structure and terminology. Use for feature specs, implementation plans, task breakdowns, phased delivery plans, planning indexes, or plan-related files in locations such as features/, plans/, specs/, docs/, or RFC directories. Supports features, fixes, refactors, migrations, deprecations, and other deliverable changes without imposing one directory layout.
---

# Plan Feature

Create a plan that fits the project and lets a reviewer trace the proposed work from problem to evidence, decisions, implementation, and verification.

## Preserve Project Conventions

Treat repository-local instructions and established planning conventions as authoritative.

1. Read applicable agent instructions and planning skills.
2. Search for existing feature plans, specs, RFCs, ADRs, task lists, indexes, and templates.
3. Reuse the project's location, filenames, metadata, statuses, terminology, and citation style when they are consistent.
4. Use the fallback structure below only when no usable convention exists or the user asks for it.
5. Do not reorganize existing planning documentation merely to match this skill.

## Core Rules

1. **Inspect before asserting.** Verify current-state claims against source code, tests, configuration, issue data, research, or user-provided evidence.
2. **Separate fact from uncertainty.** Record unresolved matters as assumptions or open decisions. Ask the user only when a material product or architecture choice cannot be discovered safely.
3. **Keep scope deliverable.** Prefer independently testable vertical slices over layer-by-layer phases.
4. **Tie status to evidence.** Do not mark a plan or phase complete until its stated success criteria have been verified.
5. **Do not invent project-management data.** Omit effort estimates, deadlines, coverage percentages, and manual “last updated” dates unless the user supplies them or the project requires them.
6. **Create artifacts progressively.** Do not create empty directories or speculative phase files. Add an artifact only when it has meaningful content.
7. **Keep examples small.** Use signatures, schemas, interfaces, or pseudocode to explain an approach; avoid embedding full implementations.
8. **Write without blame.** Describe observed behavior, cite the evidence, and state the rule the design must satisfy.

## Workflow

### 1. Orient

- Identify the requested outcome, audience, and planning stage.
- Inspect the repository and existing planning records.
- Locate related code, tests, incidents, issues, decisions, and prior work.
- Determine whether the request is to create, revise, extend, or audit a plan.

### 2. Choose the Planning Shape

- Follow an existing project shape when one exists.
- Choose a single unit when the change can be delivered and verified together.
- Choose multiple phases when ordering, dependencies, rollout, or independently useful slices justify them.
- State why multiple phases are needed and show their dependencies explicitly.
- Use the project's work taxonomy. If none exists, choose a descriptive type such as feature, fix, refactor, migration, deprecation, or enablement.

### 3. Build the Evidence Base

- Describe the current state and desired outcome.
- Cite each load-bearing claim using the repository's stable citation style.
- Prefer stable symbols such as `path#symbol` when available; otherwise use paths, line references, issue links, test names, or document anchors.
- Identify affected users, systems, boundaries, and failure modes.
- Correct or remove claims that the evidence does not support.

### 4. Define the Contract

- State testable invariants or requirements.
- Map acceptance criteria to those requirements.
- Declare what is out of scope.
- For non-trivial changes, explain the simplest credible alternative and the specific gaps it leaves.
- Describe concrete consequences of omitting a requirement; avoid vague risk adjectives.

### 5. Record Decisions

Maintain a decision ledger in the project’s preferred format. If none exists, group decisions as:

- **Locked:** confirmed constraints or choices.
- **Discretionary:** implementation choices left to the implementer.
- **Deferred:** deliberately excluded work with a future destination.
- **Open:** unresolved questions and the evidence or owner needed to close them.

Never present an open choice as settled.

### 6. Plan Delivery and Verification

- Give every phase an observable outcome.
- Map requirements to phases and tasks.
- Show dependencies and unblocking criteria for multi-phase work.
- Include testing, rollout, compatibility, migration, observability, and rollback work when relevant.
- Define completion as observable behavior and recorded verification, not merely files changed or tasks checked.

### 7. Write and Validate

- Create only the artifacts needed at the current planning stage.
- Update an index only when the project already uses one or the user requests one.
- Resolve every template placeholder.
- Check internal links, terminology, requirement mappings, phase dependencies, and status consistency.
- Re-read cited evidence before finalizing load-bearing claims.

## Fallback Structure

When the repository has no planning convention, use this adaptable baseline:

```text
features/<work-name>/
├── README.md      # orientation, status, navigation, outcome
├── spec.md        # problem, requirements, acceptance criteria, scope
├── plan.md        # architecture, decisions, delivery, verification
├── tasks.md       # executable checklist mapped to requirements
└── research/      # supporting evidence, only when needed
```

Start a draft with `README.md`. Add `spec.md`, `plan.md`, and `tasks.md` as the work becomes specified and planned.

For multi-phase work, keep shared context at the root and put phase-specific artifacts under the repository’s preferred phase structure. If none exists, use `phases/001-<name>/`, `phases/002-<name>/`, and so on. Create only phases ready to describe meaningfully.

Use these fallback states only when the project provides none:

| Status | Evidence |
|---|---|
| Draft | Outcome and boundaries are being defined |
| Specified | Requirements and acceptance criteria are reviewable |
| Planned | Decisions, delivery slices, and verification are reviewable |
| In Progress | Implementation has started |
| Complete | Acceptance criteria have verified evidence |
| Archived | Work will not proceed or is retained only as history |

## Artifact Responsibilities

Keep each fact in one primary place and link to it elsewhere.

| Artifact role | Primary question |
|---|---|
| Overview | What is this, why does it matter, and where do I go? |
| Specification | What behavior and constraints must hold? |
| Plan | How will the system change, and why this approach? |
| Tasks | What executable work remains, and how is it verified? |
| Research | What evidence or exploration informed the plan? |

Do not force these exact filenames when the project uses another topology.

## References

- Read [templates.md](references/templates.md) when creating a new planning artifact or choosing a fallback layout.
- Read [writing-guide.md](references/writing-guide.md) before drafting or auditing plan prose.
- Read [reviewable-design.md](references/reviewable-design.md) for non-trivial changes whose correctness, scope, or tradeoffs need a checkable argument.
