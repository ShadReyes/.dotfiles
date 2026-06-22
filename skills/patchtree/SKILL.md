---
name: patchtree
description: Use Patchtree workspace primitives to create cheap isolated native workspaces for repository tasks without orchestrating agents. Use when an agent needs a safe per-task workspace, parallel repo work, APFS CoW/reflink workspaces, workspace diff/export/delete/cleanup, or machine-readable workspace status.
---

# Patchtree

## Purpose

Use `patchtree` as a primitive workspace layer: cheap isolated directories, command execution, status, diff, export, delete, and cleanup. Do not add scheduling, queues, task assignment, or agent orchestration. Agents/scripts are only consumers of the primitives.

## Quick start

Create a control directory outside the base repo, then fork one workspace per task:

```bash
mkdir -p ~/workspaces/<project-name>
cd ~/workspaces/<project-name>
patchtree init /path/to/base-repo
patchtree fork <task-name>
patchtree path --json <task-name>
```

Run, inspect, export, and clean up:

```bash
patchtree run <task-name> -- <command...>
patchtree run --kind test --label "unit tests" <task-name> -- npm test
patchtree status --json <task-name>
patchtree diff <task-name>
patchtree export <task-name> --patch /tmp/<task-name>.patch
patchtree delete <task-name> --force
patchtree cleanup
patchtree cleanup --apply
```

## Rules for agents

- Use one `patchtree` workspace per independent task.
- Do not mutate the base repo directly.
- Prefer `patchtree path --json`, `patchtree status --json`, `patchtree inspect --json`, and `patchtree list --json` for machine-readable state.
- Use `patchtree run` for commands that should be recorded as workspace evidence.
- Use `patchtree diff` or `patchtree export --patch` to hand changes back to the caller.
- Use `patchtree delete --force` only after needed changes are exported or intentionally discarded.
- Use `patchtree cleanup` as a dry run first; use `patchtree cleanup --apply` only for stale/orphaned `.workspace-state` files.
- Never build agent orchestration on top of this skill: no queues, schedulers, worker pools, assignment logic, or PR automation unless the user explicitly asks outside this skill.

## Backend behavior

`patchtree fork` defaults to a copy-on-write clone of the **entire** base repo — including `.git` and untracked files like `node_modules` and build artifacts — so the workspace is immediately runnable without reinstalling dependencies. On macOS this is a single `clonefile(2)` syscall on the repo root (recursive, near-instant, ~0 added disk); on Linux it uses reflink (`cp --reflink`). Unchanged file blocks are shared with the base until modified. If CoW is unavailable (e.g. base and workspace on different volumes/filesystems), it falls back to a full copy.

`WS_MATERIALIZATION_POLICY` selects the backend:

```bash
WS_MATERIALIZATION_POLICY=reflink  patchtree fork <task-name>   # force CoW, error if unavailable
WS_MATERIALIZATION_POLICY=copy     patchtree fork <task-name>   # plain recursive copy
WS_MATERIALIZATION_POLICY=worktree patchtree fork <task-name>   # git worktree
```

Use `reflink` to require block sharing. Use `worktree` for a fast git-only checkout — but note it does NOT include untracked files (node_modules, Pods), so the workspace needs its own dependency install.

## Common workflows

Start a task:

```bash
cd ~/workspaces/<project-name>
patchtree fork <task-name>
workspace_path=$(patchtree path <task-name>)
```

Export a patch or branch:

```bash
patchtree export <task-name> --patch /tmp/<task-name>.patch
patchtree export <task-name> --branch workspace/<task-name>
```

Compare attempts:

```bash
patchtree compare <task-a> <task-b>
```

## Troubleshooting

If a command says the workspace is locked, another mutation operation is active or a stale lock exists:

```bash
patchtree cleanup
patchtree cleanup --apply
```

If `patchtree` is unavailable, install it from the source repo (private):

```bash
# if already cloned at ~/personal/patchtree:
cd ~/personal/patchtree && ./scripts/install.sh

# otherwise clone it fresh:
gh repo clone ShadReyes/patchtree ~/personal/patchtree
cd ~/personal/patchtree && ./scripts/install.sh
```

`install.sh` runs `cargo build --release` and symlinks the binary into `~/.local/bin`. Requires a Rust toolchain and `git`. Source: <https://github.com/ShadReyes/patchtree>
