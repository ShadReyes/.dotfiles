---
name: solving-linear-issues
description: Works on Linear issues end-to-end by fetching issue details, creating git branches, and implementing solutions. Use when referencing a Linear issue ID (e.g., MOBILE-123), Linear URL, or asking to work on, solve, fix, or implement a Linear issue.
---

# Solving Linear Issues

## Workflow

### Step 1: Fetch Issue Details

Use the Linear MCP tool to retrieve the issue:

```
mcp__linear__get_issue(id: "<issue-id>", includeRelations: true)
```

Extract:
- Title and description
- Acceptance criteria
- Labels and priority
- Related/blocking issues
- Git branch name (`branchName` field)
- Attachments or links

### Step 2: Gather Context

- Read any linked documents or referenced files
- Search the codebase for relevant existing code
- Understand the current implementation for bug fixes or enhancements

### Step 3: Clarify Requirements

Ask clarifying questions if:
- The description is ambiguous
- Multiple implementation approaches are possible
- Technical decisions need user input
- Acceptance criteria are unclear

### Step 4: Branch Management

Check current branch:

```bash
git branch --show-current
```

If not on the correct branch:

1. Stash uncommitted changes: `git stash`
2. Fetch latest: `git fetch origin`
3. Check if branch exists: `git ls-remote --heads origin <branch-name>`
4. Create or checkout:
   - Exists: `git checkout <branch-name> && git pull`
   - New: `git checkout -b <branch-name> origin/main`

The git branch name comes from the Linear issue's `branchName` field.

### Step 5: Implement the Solution

- Use `TodoWrite` to break down implementation into trackable tasks
- Follow existing code patterns and conventions
- Write clean, well-structured code
- Add appropriate error handling
- Include necessary tests

### Step 6: Final Steps

After implementation:

1. Run linting/type checks: `yarn lint`, `yarn tsc`
2. Run relevant tests
5. Provide summary of changes

### Step 7: Update Linear (Optional)

If requested:
- Add a comment summarizing changes via `mcp__linear__create_comment`
- Update issue status via `mcp__linear__update_issue`

## Example

**User:** "Work on MOBILE-1922"

**Process:**
1. Fetch MOBILE-1922 from Linear
2. Display issue summary to user
3. Ask any clarifying questions
4. Create/checkout branch `shadrac/mobile-1922-...`
5. Implement the fix with tracked todos
6. Report completion

## Notes

- Always read and understand the full issue before starting
- For complex issues, present a plan before implementing
- Keep user informed of progress throughout
