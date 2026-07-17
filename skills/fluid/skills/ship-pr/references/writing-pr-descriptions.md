# Writing PR Titles & Descriptions

How Fluid teams shape PR titles and descriptions. A PR description is a permanent record — read
by reviewers today and by engineers debugging this code months from now. It exists to answer two
questions: **what** changed and **why**.

Sources: [Google eng-practices — CL descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html) and [HackerOne — Writing a great PR description](https://www.hackerone.com/blog/writing-great-pull-request-description).

## The title

Format: **Conventional Commits** — `<type>(<scope>): <subject>`. PRs squash-merge, so the title becomes the commit message on `main`. Get it right.

### What the lint enforces (hard requirements)

When a repository uses the standard Fluid title lint (check the repository workflow and
contribution docs), it rejects the PR title unless **all** of these hold:

- **type** is one of: `feat` `fix` `chore` `refactor` `docs` `test` `style` `perf` `build` `ci` `revert` — lowercase, exactly as written.
- **subject does not start with an uppercase letter** (pattern `^(?![A-Z]).+$`). So `feat: Add X` fails; `feat: add X` passes.
- A non-empty subject follows the `: ` separator.

`requireScope` is **false** — a scope is optional as far as the lint is concerned.

### Team conventions (on top of the lint)

These aren't always enforced by title lint, but Fluid repositories commonly expect them through
commit hooks and repository history:

- **Always add a scope** — the app or package: `fluid-admin`, `checkout`, `portal-sdk`, etc. Optional to the linter, expected by the team.
- **Imperative mood, no trailing period** (commitlint's `subject-full-stop`).
- **Be specific** — summarize _what_ the PR does well enough to stand alone in `git log`. The first line is _what_, not why — save the why for the body.

| Bad                    | Why it's bad                                | Good                                                                    |
| ---------------------- | ------------------------------------------- | ----------------------------------------------------------------------- |
| `Update code`          | rejected by lint — no type, uppercase start | `refactor(portal-sdk): replace --profile-* tokens with semantic tokens` |
| `feat: Add upload tab` | rejected by lint — uppercase subject        | `feat(fluid-admin): add uploads to mobile page builder tabs`            |
| `fix: bug`             | passes the lint, but vague and scope-less   | `fix(checkout): keep selected saved card active`                        |
| `feat: phase 1`        | passes the lint, but carries no information | `feat(orders): add partial-refund support to order detail`              |

## The description

Use this template. Drop sections that don't apply (e.g. screenshots for non-UI work), but **never drop Why.**

```markdown
## What

<The net effect in plain language. What changed, at a high level.>

## Why

<The motivation: the problem, the bug, the business or engineering goal.
This is the most important section — the diff shows what, never why.
Link the Linear issue, but don't make reviewers open it to understand the change.>

## How it works

<Significant design decisions and non-obvious logic. The diff shows the
details; call out the choices a reviewer can't infer from it — alternatives
considered, trade-offs made, and known limitations.>

## How to test

<Concrete steps a reviewer can follow, each with an expected result.
Note the automated tests you ran and any edge cases left uncovered.>

## Review guide (optional)

**Focus on:** <files with the core logic that need careful review>
**Skim:** <generated / boilerplate / mechanical changes>

## Linear

<LINEAR_URL>
```

## Principles

- **Why over what.** Reviewers read the diff for _what_; they can't read your mind for _why_. Both sources rank this as the single most important thing.
- **Stand alone.** Don't make the reviewer open the ticket to understand the change. Reference tickets; don't depend on them.
- **Write prose, not fragments.** Conversational, complete sentences — not terse, acronym-filled fragments.
- **Call out decisions, not the obvious.** "Wrote migration and model" is visible in the diff. "Used Devise so we don't roll our own MFA" is not.
- **Acknowledge shortcomings.** State known limitations and follow-ups so reviewers don't have to discover them.
- **A long description is a smell.** If it balloons, the PR is probably too big — split it.
- **Re-read before requesting review.** Descriptions drift during review; make sure it still matches the final diff before you ask for eyes.

## Checklist

- [ ] Title is Conventional Commits — imperative, lowercase, specific
- [ ] **Why** is explained, not just what
- [ ] Design decisions / trade-offs called out
- [ ] Test steps with expected results
- [ ] Linear link present (or the user has explicitly provided the tracking decision)
- [ ] Description matches the final diff
