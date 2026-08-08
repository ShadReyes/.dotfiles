# Implement a Fluid Linear issue

Implement one approved, actionable slice. Do not ship it unless the user asks.

## Resolve the implementation source

Use the issue description and the approved plan path supplied by the user. If no
path is supplied, accept one unambiguous issue-matched plan under `./plans/`.

If no approved plan exists, stop and recommend:

```text
$fluid:work-linear-issue prepare <issue-id>
```

Proceed without a durable plan only when the issue is a single narrow slice and
the user explicitly asks for direct implementation. If an approved plan contains
multiple independently shippable phases and the user did not select one, stop
and ask for the target phase or child issue.

## Prepare the worktree

1. Read and follow `implement-change`.
2. Identify the repository, active worktree, current branch, and working-tree
   state.
3. Read all applicable `AGENTS.md` files and repository-local instructions.
4. Determine the smallest file set that can satisfy the selected slice.
5. Load only the repository skills required by those files and behaviors.

Do not stash, discard, or overwrite user changes. Stop when unrelated work
overlaps the required files and cannot be preserved safely.

## Implement and verify

1. Implement the selected tracer bullet across every required boundary.
2. Keep the diff scoped to the issue contract and approved phase.
3. Add or update tests at the plan's highest useful seam.
4. Run `git diff --check`.
5. Run the formatter, linter, type checker, and narrow tests required by the
   changed files. Expand verification only when the change risk warrants it.
6. Inspect the final diff and map evidence to the issue acceptance criteria.

Follow repository execution constraints. For example, run Rails, Ruby, Bundler,
and Rake commands through the required Fluid devcontainer.

## Completion criterion

Finish only when:

- the selected slice is implemented or a concrete blocker is demonstrated;
- relevant verification results are reported without weakened thresholds;
- satisfied, remaining, and blocked acceptance criteria are explicit;
- changed files and any residual risks are summarized;
- no commit, push, pull request, or Linear mutation occurred without explicit
  authorization.
