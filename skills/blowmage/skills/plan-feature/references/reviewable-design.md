# Reviewable Feature Designs

A reviewable design does more than describe scope. It gives reviewers the rules, evidence, alternatives, decisions, and verification path needed to check whether the proposed change is sufficient.

## Table of Contents

- [The argument](#the-argument)
- [Named invariants](#named-invariants)
- [The simplest credible alternative](#the-simplest-credible-alternative)
- [Consequences of omission](#consequences-of-omission)
- [Evidence and citations](#evidence-and-citations)
- [Decision ledger](#decision-ledger)
- [Review findings](#review-findings)
- [Traceability](#traceability)

## The Argument

Build the design around two questions:

1. What rule must hold after the change?
2. What evidence shows whether that rule holds today and will hold afterward?

For a small, obvious feature, ordinary requirements and acceptance criteria may answer both. For a non-trivial or disputed design, use the full pattern below.

## Named Invariants

An invariant is a stable, testable rule. Name it when the identifier will help trace requirements, phases, tests, or review findings.

```markdown
## Invariants

- **INV-1: One reservation consumes inventory at most once.**
  Retrying the reservation command does not decrement available inventory again.
- **INV-2: A rejected reservation leaves inventory unchanged.**
  Validation completes before any inventory mutation is committed.
```

Map requirements and acceptance criteria to the invariants they carry:

```markdown
### R-1: Idempotent reservation

**Invariants:** INV-1

- AC-1.1: Repeating a command with the same idempotency key returns the original reservation.
- AC-1.2: Available inventory decreases once across the initial command and all retries.
```

Do not create identifiers merely for ceremony. Use them when another artifact will refer back to the rule.

## The Simplest Credible Alternative

Answer “could we do less?” before a reviewer has to ask.

1. Name the smallest serious alternative.
2. Describe what it changes and what benefit it provides.
3. Identify the invariants it satisfies.
4. List the evidenced gaps it leaves.

```markdown
## Simplest Credible Alternative

The smaller change retries the existing reservation request only from the client.
It improves recovery from a dropped response without changing the service.

It does not make the command idempotent. The handler decrements inventory before
writing the reservation (`src/reservations/handler.ts#execute`), so a retry after
the decrement can consume inventory twice. INV-1 remains unsatisfied.
```

Represent the alternative fairly. If it satisfies the actual requirements, prefer it.

## Consequences of Omission

For each significant requirement or phase, state the concrete behavior that remains if it is omitted.

**Vague:** “Skipping this creates a serious consistency risk.”

**Checkable:** “A retry after the inventory write decrements stock twice (`src/reservations/handler.ts#execute`), violating INV-1.”

Use the format that best fits the project:

```markdown
**If omitted**

- {Specific scenario} ({evidence}), violating {invariant or requirement}.
- {Missing capability} remains unavailable to {affected user or system}.
```

Not every new capability has a current defect to cite. In that case, describe the missing outcome and cite the product requirement, issue, research, or user-provided evidence that establishes the need.

## Evidence and Citations

A citation must let another person inspect the claim.

| Evidence | Useful citation |
|---|---|
| Source behavior | `path#symbol`, then `path:line` when needed |
| Test-pinned behavior | `path#test name` |
| Configuration | file path and key |
| Product requirement | issue or document link plus anchor |
| Incident or user report | incident/issue ID and relevant event |
| Research or data | durable query, report, or note with method |

Open the evidence and verify it before asserting the claim. Comments, old plans, and issue summaries can be stale.

When evidence conflicts:

- Prefer the authoritative runtime behavior or record.
- Explain the discrepancy when it affects the plan.
- Record corrected claims when readers may have relied on an earlier version.

Use a blame-free form: observed behavior, evidence, invariant. Authorship is not relevant to whether the design is correct.

## Decision Ledger

Separate settled constraints from implementation freedom and unresolved questions.

```markdown
## Decisions

### Locked

- The service accepts an idempotency key on every reservation command because INV-1 applies across retries.

### Discretionary

- The internal cache key format and local helper names.

### Deferred

- Expiring abandoned reservations automatically; track in {destination}.

### Open

- Whether keys expire after 24 hours or with the reservation record; close after retention requirements are confirmed.
```

“Locked” requires evidence, explicit user confirmation, or an authoritative project constraint. Do not silently promote assumptions or open questions.

## Review Findings

Reviews test the design’s argument. Preserve material findings and update the primary artifacts.

```markdown
| ID | Finding | Evidence | Resolution | Updated artifacts |
|---|---|---|---|---|
| F-1 | Validation can pass before a concurrent decrement. | `src/inventory/store.ts#reserve` | Move the check into the atomic write. | R-2, plan § Storage, tasks § Slice 1 |
```

The findings table is an index, not a patch over stale documentation. Revise the specification, plan, tasks, acceptance criteria, and tests that the finding changes.

Use the project’s established finding identifiers when present. Otherwise a simple `F-N` sequence is sufficient.

## Traceability

A reviewer should be able to walk in both directions:

```text
evidence -> current-state claim -> invariant -> requirement
         -> design decision -> delivery slice -> verification
```

Check for broken links in that chain:

- An invariant with no requirement or verification is aspirational.
- A task with no requirement may be scope creep.
- A decision with no evidence or invariant may be accidental complexity.
- An acceptance criterion with no delivery slice will not be implemented.
- A review finding that changes no primary artifact is unresolved.

The goal is not maximum documentation. Keep only the links needed for another person to check the design and execute it confidently.
