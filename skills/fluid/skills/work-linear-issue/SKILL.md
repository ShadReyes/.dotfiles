---
name: work-linear-issue
description: Prepare or implement one Fluid Current-team Linear issue through an explicit phase, with blocker checks, selective context loading, durable planning, scoped repository changes, and proportional verification. Use for a Fluid Linear issue ID or URL when the user asks to plan the issue or implement an approved plan.
---

# Work a Fluid Linear issue

Run exactly one phase per invocation: `prepare` or `implement`. Infer the phase
from the request when it is explicit. Otherwise, ask which phase the user wants.
Never continue from preparation into implementation in the same invocation.

## Shared preflight

1. Require one Fluid Linear issue ID or URL.
2. Read and follow `fluid:linear-fluid`. Fetch the issue, Project, relations,
   labels, state, and full description from the locked Fluid workspace.
3. Read and follow `fluid:linear-triage`. Run it for the issue's Project before
   recommending or starting work.
4. Treat the issue description as the implementation contract. Treat linked
   PRDs, bets, and discovery documents as supporting context.
5. Read a linked document only to resolve a specific gap or constraint. Do not
   rerun product discovery or mutate a graduated bet.
6. Keep Linear read-only unless the user explicitly authorizes a named mutation.
   Do not apply `ready-for-agent`, create children, comment, or change state by
   default.
7. Keep Git and external systems read-only unless the selected phase and user
   request authorize a change. Never stash, switch branches, commit, push, or
   open a pull request implicitly.

For `prepare`, report active blockers but continue only when the user explicitly
wants a blocked issue prepared. For `implement`, stop when any active blocker
exists.

## Context budget

- Fetch the selected issue and its direct relations, not the full Project history.
- Determine the likely repository and file scope before loading technical skills.
- Read the applicable repository instructions and only the specialist skills
  required by the likely changed files.
- Prefer the issue, one approved plan, relevant code seams, and adjacent tests.
- Do not paste source documents into new artifacts when a link is sufficient.

## Select the phase

- For `prepare`, read [references/prepare.md](references/prepare.md) completely.
  Do not read the implementation branch.
- For `implement`, read [references/implement.md](references/implement.md)
  completely. Do not read the preparation branch.

## Handoff

Report the issue URL, blocker result, artifacts created or changed, verification
results, remaining acceptance criteria, and the exact next invocation. Use
`fluid:ship-pr` separately when the user requests commit, push, PR creation, and
review iteration.
