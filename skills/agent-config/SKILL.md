---
name: agent-config
description: Normalize a repository or workspace to agent-first configuration. Use when asked to create, migrate, symlink, or repair AGENTS.md, CLAUDE.md, .agents/skills, .claude/skills, or shared AI agent guidance across repos.
---

# Agent Config

Use this skill when a repo should be made agent-first while keeping Claude compatibility.

## Canonical Layout

Prefer this shape at every meaningful repo or workspace root:

```text
AGENTS.md
CLAUDE.md -> AGENTS.md
.agents/
  skills/
.claude/
  skills -> ../.agents/skills
```

If `.claude/agents` exists, make `.agents/agents` canonical too:

```text
.agents/agents/
.claude/agents -> ../.agents/agents
```

## Workflow

1. Inspect first:
   - `find <path> -maxdepth 3 \( -name AGENTS.md -o -name CLAUDE.md -o -name .agents -o -name .claude \) -print`
   - `git -C <repo> status --short`
2. Run the deterministic normalizer:
   - Single repo: `~/dotfiles/scripts/agentize-repo <path>`
   - Workspace tree: `~/dotfiles/scripts/agentize-repo --recursive <path>`
3. If the script reports conflicts, do not guess. Read the conflicting files and ask the user or make a narrow manual merge only when the correct source of truth is clear.
4. After migration, search canonical files for stale Claude-only wording:
   - `rg -n 'Claude Code|CLAUDE.md|\.claude/skills|CLAUDE.local' <path>`
   - Keep compatibility mentions only when they describe symlinks or tool-specific behavior.
5. Verify symlinks resolve and canonical paths are readable.

## Rules

- `AGENTS.md` is the source of truth.
- Keep project-specific guidance in the project or workspace, not only in home dotfiles.
- Keep personal setup automation in dotfiles.
- Preserve existing user content. Do not overwrite conflicting docs or skill directories.
- Leave unrelated dirty worktree changes untouched.
- Do not add AI attribution, signatures, or self-identification to docs, comments, commits, or PR bodies.
