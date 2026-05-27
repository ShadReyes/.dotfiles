---
name: address-pr-comments
description: Use when asked to review, triage, or address bot/reviewer comments on a GitHub PR. Triggers on phrases like "address PR comments", "handle bot comments", "fix review comments", or when given a PR URL/number and told to act on its comments.
---

# Address PR Comments

## Overview

Fetch comments from a GitHub PR, evaluate each for correctness and relevance, address valid ones with code changes, then commit, push, and reply on GitHub.

## Workflow

### Step 1: Identify the PR

If a PR number or URL was provided, use it. Otherwise infer from current branch:

```bash
gh pr view --json number,url,headRefName
```

### Step 2: Fetch All Comments

Fetch both PR-level comments and inline review comments:

```bash
# PR-level comments (bot summaries, general comments)
gh pr view <PR_NUMBER> --json comments,reviews

# Inline review comments
gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments
```

Extract `--repo` from `gh repo view --json nameWithOwner`.

### Step 3: Evaluate Each Comment

For each comment, judge:

| Question | If NO → |
|---|---|
| Is it **correct**? (factually accurate about the code) | Skip — note why |
| Is it **valid**? (points to a real issue worth fixing) | Skip — note why |
| Is it **related**? (within scope of this PR's changes) | Skip — out of scope |

Only address comments that pass all three. Use your judgment — bot comments are sometimes wrong or over-reaching.

### Step 4: Address Valid Comments

For each valid comment:
1. Read the referenced file and line(s)
2. Make the minimal fix
3. Note which comment it addresses

### Step 5: Lint, Format, and Test

**Lint and format first**, then run tests.

1. **Lint** — run the project's linter on changed files (e.g., RuboCop, ESLint, Biome, Ruff). Fix any offenses before committing. Check project config files, CLAUDE.md, or package.json to identify the correct linter.
2. **Format** — run the project's formatter on changed files if it's separate from the linter (e.g., Prettier, Black). Some linters handle formatting too (RuboCop, Biome) — don't double-run.
3. **Test** — run the test file(s) most relevant to what changed. Don't run the full suite unless necessary.

### Step 6: Commit and Push

```bash
git add <changed files>
git commit -m "<concise message describing what was addressed>"
git push
```

### Step 7: Reply to Comments on GitHub

For each comment you addressed, post a reply:

```bash
# Reply to a PR-level issue comment
gh api repos/{owner}/{repo}/issues/<PR_NUMBER>/comments \
  -X POST -f body="Addressed in <commit-sha>: <one-line explanation>"

# Reply to an inline review comment thread
gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments/<comment_id>/replies \
  -X POST -f body="Fixed in <commit-sha>: <one-line explanation>"
```

For comments you skipped, post a reply explaining why (incorrect, out of scope, etc.).

### Step 8: Resolve Threads (if applicable)

To resolve an inline review thread via GraphQL:

```bash
# Get thread IDs
gh api graphql -f query='
  query {
    repository(owner: "{owner}", name: "{repo}") {
      pullRequest(number: <PR_NUMBER>) {
        reviewThreads(first: 50) {
          nodes { id isResolved comments(first:1) { nodes { body } } }
        }
      }
    }
  }
'

# Resolve a thread
gh api graphql -f query='
  mutation {
    resolveReviewThread(input: {threadId: "<thread_id>"}) {
      thread { isResolved }
    }
  }
'
```

Only resolve threads for comments you've addressed.

### Step 9: Update PR Description

If the changes you made affect what the PR description says, update it with `gh pr edit`. Common reasons:

- New files were added or changed that aren't listed
- Behavior described in "How it works" or similar sections is now different
- Verification/test steps should cover the new fixes
- Decisions or trade-offs were made that reviewers should know about

Read the current description (`gh pr view <PR_NUMBER> --json body`), update only the sections that are stale, and preserve the rest.

## Skipping Comments

When skipping, still reply so reviewers know it was considered:

- **Incorrect:** "This comment isn't accurate — `subject` was added to the auto-destroy check in this PR (line 15 of save_drafts_controller.rb)."
- **Out of scope:** "This is a pre-existing issue unrelated to this PR's changes. Skipping to keep the diff focused."
- **Bot false positive:** "The linter flag here is a false positive — this pattern is intentional per project conventions."

## Example

**User:** `/address-pr-comments 15376`

**Process:**
1. Fetch PR 15376 comments
2. Find Greptile's stale description comment — correct, valid, in scope → fix it
3. Run rubocop + relevant spec
4. Commit + push
5. Reply to Greptile's comment with commit SHA
6. Resolve the thread
