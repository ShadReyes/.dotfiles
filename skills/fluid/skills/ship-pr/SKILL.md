---
name: ship-pr
description: >
  Use when the user wants to commit, push, create a PR, and keep iterating on review feedback
  until the branch is clean and approved.
license: MIT
compatibility: Requires git and gh (GitHub CLI) installed and authenticated.
metadata:
  author: parkerrudd
  version: "1.0"
allowed-tools: Bash(gh:*) Bash(git:*)
---

# Ship a Fluid PR

Use this skill when a user wants the full pull-request lifecycle handled end to end for a
Fluid repository. Confirm the repository's own contribution guide and available checks before
running commands; repositories may use different languages, package managers, or devcontainers.

## Goal

Commit the change, push it, open a PR, wait for CI and configured automated review, fix
actionable feedback, re-run review, and trigger the Fluid Reviewer Committee only after the
latest Greptile review reaches 5/5 when that integration is enabled for the repository.

## Flow

1. Audit the diff and avoid unrelated files.
2. Commit with a conventional message.
3. Push and create the PR. Shape the title and description per
   [`references/writing-pr-descriptions.md`](references/writing-pr-descriptions.md).
4. Wait for checks and configured automated review. If Greptile is not configured, continue
   with the checks and reviewers that are available.
5. Address actionable review comments per
   [`references/addressing-review-comments.md`](references/addressing-review-comments.md)
   (triage each comment, escalate product decisions to the user, fix with TDD, verify before replying).
6. Re-push and re-check automated review after every change.
7. In repositories where it is configured, trigger
   `@fluid-commerce/reviewer-committee` only after the latest Greptile review is 5/5.
8. Resolve or reply to final committee comments as needed.
9. Report the PR URL, comment counts, and final CI status, including any checks or review
   integrations that were unavailable.

## Rules

- Never force-push unless the user explicitly asks.
- Never skip CI hooks.
- Stage only the files that belong to the change.
- Default to fixing bot feedback when it is cheap and clearly correct.
- Do not trigger Reviewer Committee before the latest Greptile review is 5/5 when that review
  integration is enabled.
- Extract the Linear issue URL from the branch name or issue lookup and include it in the PR
  description. If no issue can be identified, ask the user before creating the PR.
- Follow the repository's contribution instructions for testing. For JavaScript/TypeScript
  work, use the repository's documented package-manager checks; for Rails work, run
  Rails/Ruby/bundle/rake commands through the `fluid` Docker devcontainer.

## Useful commands

```bash
git status -u
git diff --stat
git push -u origin HEAD
gh pr create --title "<title>" --body "<body>"
# non-zero = checks failed; inspect the output before moving on
gh pr checks <PR_NUMBER> --watch || true
gh pr comment <PR_NUMBER> --body "@fluid-commerce/reviewer-committee"
```

The last command is conditional: use it only when the repository has the Reviewer Committee
integration and the latest Greptile review is 5/5.

## References

- [`references/writing-pr-descriptions.md`](references/writing-pr-descriptions.md) — team conventions for PR titles (Conventional Commits) and descriptions (what / why / how / test). Read before step 3.
- [`references/addressing-review-comments.md`](references/addressing-review-comments.md) — triaging and responding to review comments: verify correctness, escalate product decisions, fix with TDD. Read before step 5.
