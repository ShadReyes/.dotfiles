---
name: to-prd
description: Turn the current conversation and repository context into a Fluid PRD saved locally or published to Fluid Linear. Use when shaping a feature, product problem, or implementation request into a requirements document.
---

# Fluid PRD

Synthesize the current conversation and codebase understanding into a PRD. Do
not restart discovery or interview the user about information already present.
Use the repository's glossary and relevant ADRs when they are available.

## Destination

Use a local Markdown file by default:

```text
docs/prds/<feature-slug>.md
```

Accept an explicit destination when the user requests Linear publication:

- For an existing issue, update only the supplied issue.
- For a new issue, require an explicit Current-team Project, resolve it, and
  preview the proposed title and body before creating anything.
- Use the locked Fluid Linear launcher and bundled operations from
  `fluid:linear-fluid`; never use another workspace or inline credentials.
- Apply `ready-for-agent` only when the user explicitly requests it.
- If Linear is unavailable, save the PRD locally and report that it is
  local-only. Offer publication later.

Do not automatically add a plan backlink or other Linear comment after creating
the PRD. Do that only when explicitly requested.

## Process

1. Explore the repository if the current conversation has not already
   established the relevant architecture. Prefer existing domain vocabulary,
   seams, and ADR decisions.
2. Identify the highest existing seam at which the feature can be tested. Keep
   the number of seams small and propose new seams only when necessary.
3. Check that the proposed testing seam matches the user's expectations.
4. Write the PRD using the required structure below.
5. Save it to the selected destination. For Linear mutations, explain the
   intended change, obtain approval for a new issue, and report the resulting
   identifier and URL.

## PRD structure

```md
## Problem Statement

The problem the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

1. As an <actor>, I want a <feature>, so that <benefit>

Cover all important user-visible behavior, including permissions, errors,
empty states, and operational needs where relevant.

## Implementation Decisions

- Modules, interfaces, data models, API contracts, architectural decisions,
  and specific interactions.
- Describe durable behavior and contracts; do not include unstable file paths
  or code snippets.

## Testing Decisions

- Test externally observable behavior at the highest useful seam.
- Identify modules and prior-art test patterns.

## Out of Scope

Explicitly exclude adjacent work that is not required for this feature.

## Further Notes

Dependencies, unresolved risks, rollout notes, or source references.
```

When a prototype contains a decision-rich state machine, reducer, schema, or
type shape, include only that precise decision and identify it as prototype
output.
