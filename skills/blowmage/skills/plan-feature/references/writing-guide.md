# Feature-Planning Writing Guide

Apply this guide after repository-specific writing rules. Its goal is a concise, checkable plan, not a uniform house style.

## Table of Contents

- [Ground claims in evidence](#ground-claims-in-evidence)
- [Handle uncertainty honestly](#handle-uncertainty-honestly)
- [Write for the artifact's audience](#write-for-the-artifacts-audience)
- [Make completion observable](#make-completion-observable)
- [Slice delivery vertically](#slice-delivery-vertically)
- [Avoid common failure modes](#avoid-common-failure-modes)
- [Quality checklist](#quality-checklist)

## Ground Claims in Evidence

A load-bearing claim changes the scope, requirements, or technical direction. Verify it before using it.

- Prefer a stable symbol such as `path#symbol` for source behavior.
- Use a line reference when no stable symbol fits.
- Use test names for pinned behavior, issue links for reported behavior, and document anchors for recorded decisions.
- Cite data or research with enough context for another person to reproduce the interpretation.
- Treat comments and earlier plans as leads, not proof. Check the underlying implementation or authoritative record.

**Weak:** “The resolver probably accepts inactive records.”

**Checkable:** “`Resolver#resolve` queries by hostname without an active-state condition (`src/resolver.ts#resolve`).”

If verification disproves a claim, correct the plan and record the correction when reviewers may have seen the earlier version.

## Handle Uncertainty Honestly

Distinguish these categories:

| Category | Meaning | Treatment |
|---|---|---|
| Known | Supported by current evidence | State it and cite when load-bearing |
| Assumed | Temporarily accepted but unverified | Label it and name a verification step |
| Open | Requires a choice | Record what closes the decision |
| Deferred | Deliberately excluded | Name its future destination or boundary |

Ask an informed question when an unresolved choice materially changes product behavior, scope, irreversible data design, or architecture. Continue autonomously when repository evidence answers it or the uncertainty can safely remain open in the plan.

## Write for the Artifact's Audience

### Overview and navigation

- Lead with the user or system outcome.
- Use plain language and define project-specific terms.
- Keep architecture detail in the plan.
- Make links and next actions easy to scan.

### Specification and plan

- Use literal, evidence-led language.
- State rules so tests or observations can check them.
- Explain tradeoffs fairly, including the simplest credible alternative.
- Use a diagram or table only when relationships are harder to understand in prose.

### Tasks

- Begin each slice with an observable outcome.
- Name the behavior, boundary, or artifact being changed.
- Include the verification evidence expected.
- Avoid vague verbs such as “handle,” “support,” or “clean up” without an object and success condition.

## Make Completion Observable

Describe what a user, system, test, or operator can observe.

**Good:** “A retried payment reuses the original idempotency key and creates one charge.”

**Weak:** “Payment retry code is complete.”

Tie each completion criterion to planned and then actual evidence. A checked task is not evidence by itself.

Do not invent quantitative targets. Preserve user-supplied or authoritative project targets, and state how they will be measured.

## Slice Delivery Vertically

A useful phase delivers a coherent behavior through the layers it needs.

**Vertical:** “A member signs in and receives a scoped token,” including the necessary UI, API, persistence, and tests.

**Horizontal:** “Create all models,” followed by “create all services,” with no independently testable outcome.

Use dependencies only when one slice truly requires evidence or capability from another. “We plan to build it first” is ordering, not a dependency.

## Avoid Common Failure Modes

### Imposing a foreign structure

Do not create `features/` merely because the fallback uses it. Search for the project’s RFCs, proposals, ADRs, issue templates, or plan directories first.

### Creating the whole lifecycle at once

Do not fill speculative plan and task files to make a directory look complete. Create the smallest artifact that matches the current stage.

### Letting the overview become the entire plan

Keep overview material navigational. Link to detailed requirements, architecture, and execution records instead of duplicating them.

### Hiding dependencies in prose

For three or more phases or branching dependencies, use a small table or flow that shows what blocks what and the exact unblocking evidence.

### Using vague status labels

Use the repository’s vocabulary consistently. If none exists, define a small lifecycle in the plan rather than inventing near-duplicate statuses.

### Treating risk adjectives as analysis

Replace “safer,” “robust,” or “high risk” with the specific scenario, affected boundary, evidence, and mitigation.

### Copying templates literally

Delete irrelevant headings. A short complete document is better than a long document full of “N/A.”

### Mixing supporting documentation with deliverable planning

Follow the repository’s placement rules. Link to durable API references, architecture documentation, meeting records, or vendor material rather than copying them into a feature folder unless the project explicitly colocates them.

## Quality Checklist

### Fit

- [ ] Applicable repository instructions and planning conventions were inspected.
- [ ] Location, filenames, metadata, statuses, and vocabulary fit the project.
- [ ] Only meaningful artifacts and directories were created.
- [ ] An index was changed only if the project uses one or the user requested it.

### Evidence and scope

- [ ] The current state is verified.
- [ ] Every load-bearing claim has an appropriate citation.
- [ ] Facts, assumptions, open decisions, deferred work, and exclusions are distinct.
- [ ] Requirements and acceptance criteria are testable.
- [ ] The simplest credible alternative is treated fairly when the change is non-trivial.
- [ ] Omission consequences name concrete outcomes.

### Delivery

- [ ] Each phase or slice produces an independently observable outcome.
- [ ] Requirements map to phases and verification.
- [ ] Dependencies include explicit unblocking evidence.
- [ ] Testing, compatibility, migration, rollout, observability, and rollback are addressed when relevant.
- [ ] Completion criteria describe behavior and evidence.

### Clarity

- [ ] The overview is brief and navigational.
- [ ] The specification says what must hold; the plan says how and why.
- [ ] Tasks are specific and executable.
- [ ] Terminology is consistent and defined when needed.
- [ ] No template placeholders remain.
- [ ] Links and citations resolve.
- [ ] The voice is blame-free and evidence-led.
