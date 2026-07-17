# Addressing Review Comments

How the team responds to review feedback — from Greptile, the reviewer committee, and teammates. The goal is **correct** fixes, **verified** before you claim them, with **product decisions escalated to the human** rather than guessed.

## 1. Triage every comment first

Bots and humans can be wrong, stale, or out of scope. Before changing anything, judge each comment:

| Question                                                    | If NO →                                               |
| ----------------------------------------------------------- | ----------------------------------------------------- |
| **Correct?** Factually accurate about the code as it is now | Skip — reply explaining why it's wrong                |
| **Valid?** Points to a real issue worth fixing              | Skip — reply why                                      |
| **In scope?** Belongs to this PR, not a pre-existing issue  | Skip — reply "out of scope, keeping the diff focused" |

Verify the claim against the actual code before accepting it. **A confident bot comment is a claim to check, not a fact.** Greptile in particular will sometimes over-reach or describe code that the PR already changed.

## 2. Classify what survives triage

Each remaining comment is one of:

1. **Mechanical / clearly-correct fix** → fix it (with TDD — see below).
2. **Product / UX / business decision** → **STOP. Do not decide this unilaterally.** Surface it to the user with a recommendation and let them choose. Examples: changing user-facing copy, altering a default, removing or gating a feature, changing how an error behaves — anything a PM or designer would have an opinion on.
3. **Disagreement on approach** → reply with your reasoning. If it stays unresolved, flag it to the user rather than silently complying _or_ silently ignoring.

> When unsure whether something is "just a fix" or a product decision, treat it as a product decision and ask. Reaching out is cheap; shipping the wrong behavior is not.

## 3. Fix with TDD

For any behavioral change a reviewer asks for:

1. **Write or adjust a test that fails** — encode the behavior the reviewer wants, or the bug they found. Run it and watch it fail. This proves the issue is real and that your fix actually targets it.
2. **Make the minimal change** to pass.
3. **Run the test and watch it pass.**

If the change genuinely isn't unit-testable (config, copy, infra), state _how_ you verified it instead — manual steps, a screenshot, a type-check. **Never reply "fixed" without evidence.**

## 4. Verify before committing

In order: **lint → format → test**, on the changed files. Use the repository's documented
commands and the narrowest relevant checks first, then the required full checks. For
For JavaScript/TypeScript work, use the repository's documented typecheck, lint, format, and
test commands. For Rails work in the Fluid devcontainer, run Ruby/Rails/bundle/rake commands
through `docker exec`. Match each repository's own tooling.

## 5. Commit, reply, resolve

- Commit with a Conventional Commit message describing what was addressed.
- Push — **never force-push unless the user explicitly asks.**
- Reply to each thread with the commit SHA and a one-line explanation. For skipped comments, reply with the reason from triage so reviewers know it was considered.
- Resolve **only** the threads you actually addressed.
- Update the PR description (`gh pr edit`) if your fixes made it stale.

```bash
# reply on an inline review thread
gh api repos/<owner>/<repo>/pulls/<PR>/comments/<comment_id>/replies \
  -X POST -f body="Fixed in <sha>: <one-line explanation>"
```

## Red flags — STOP

- About to change user-facing behavior / copy / a default without asking → **escalate to the user.**
- About to reply "fixed" with no test or verification → **verify first.**
- Accepting a bot comment without reading the referenced code → **check it against the code.**
- "I'll just quickly comply" on a design disagreement → reply with reasoning, or escalate.
