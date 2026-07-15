---
name: manage-skills
description: Add, author, update, or audit agent skills so they stay tracked in the ~/.dotfiles repo and in sync with the universal pool (~/.agents/skills). Use when the user wants to install/clone a skill from GitHub, create a new skill, update cloned skills, or check that skills aren't drifting out of the dotfiles repo.
---

# manage-skills

Keeps every agent skill — authored or cloned — physically tracked in `~/.dotfiles/skills/`
and symlinked into the universal pool (`~/.agents/skills`, shared by Claude Code and Codex).
The deterministic engine for this repo is `~/.dotfiles/sync-skills.sh`; this skill drives that
workflow.

## The invariant (never break it)

- The dotfiles repo is the **one physical home** for local skills.
- Root skills live at `~/.dotfiles/skills/<name>/SKILL.md`.
- Local plugin bundles live at `~/.dotfiles/skills/<plugin>/.claude-plugin/plugin.json` with
  nested `skills/<name>/SKILL.md` entries, like `fluid`, `brando`, and `matt`.
- The pool (`~/.agents/skills/<name>`) holds symlinks back into the repo.
- `~/.claude/skills` points at the same pool, so one sync updates both Claude Code and Codex.

## Common tasks

**Clone or vendor a skill from someone else.** Copy the full skill directory into the intended
location in this repo, preserving companion files such as `references/`, `scripts/`, and
supporting markdown docs.

```bash
git clone --depth 1 <repo-url> /tmp/<repo-name>
cp -a /tmp/<repo-name>/path/to/skill ~/.dotfiles/skills/<name>
~/.dotfiles/sync-skills.sh
```

For a plugin bundle, copy into the nested plugin skills directory:

```bash
cp -a /tmp/<repo-name>/path/to/skill ~/.dotfiles/skills/<plugin>/skills/<name>
~/.dotfiles/sync-skills.sh
```

**Author a new root skill.** Create it directly in the repo, then sync so it links into the pool:

```bash
# create ~/.dotfiles/skills/<name>/SKILL.md ...
~/.dotfiles/sync-skills.sh
```

**Author a new plugin skill.** Add it under the plugin bundle:

```bash
# create ~/.dotfiles/skills/<plugin>/skills/<name>/SKILL.md ...
~/.dotfiles/sync-skills.sh
```

If the plugin does not exist yet, create `~/.dotfiles/skills/<plugin>/.claude-plugin/plugin.json`
with `"skills": "./skills/"`.

**Audit / verify sync behavior:**

```bash
~/.dotfiles/test-sync.sh
find ~/.agents/skills -maxdepth 1 -type l -print
```

## Always commit afterwards

Adopted/authored skills are real folders in the repo. Commit the copied skill files, plugin
manifests, and any docs/test updates together:

```bash
git -C ~/.dotfiles add skills && git -C ~/.dotfiles commit -m "skills: <what changed>"
```

## Engine reference

`~/.dotfiles/sync-skills.sh`

- Links every top-level directory in `~/.dotfiles/skills/` into `~/.agents/skills/`.
- Links `~/.claude/skills` to the same pool.
- Also syncs local agents and commands.
