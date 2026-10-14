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
  nested `skills/<name>/SKILL.md` entries, like `brando`, `matt`, and `vercel`.
- The pool holds top-level root-skill and bundle symlinks back into the repo;
  never flatten bundles or rename every bundled skill to add a prefix.
- Claude and Codex use their supported discovery locations. OMP scans registered
  skill-parent directories; Pi supports recursive discovery and the local package.
- Every `SKILL.md` frontmatter `name` is globally unique across root skills and nested plugin
  skills. Keep the preferred implementation's short name and prefix alternatives with their
  bundle or author. Preserve compatibility renames documented in `~/.dotfiles/skills/README.md`
  when refreshing vendored skills.

## Common tasks

**Clone or vendor a skill from someone else.** Copy the full skill directory into the intended
location in this repo, preserving companion files such as `references/`, `scripts/`, and
supporting markdown docs.
OMP and Pi setup is documented in `~/.dotfiles/skills/README.md`. Adding a skill
beneath an existing OMP discovery root needs no configuration update; a new bundle
or category needs its parent registered once. Pi's package manifest needs no change.


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
~/.dotfiles/test-sync.sh  # includes a global frontmatter-name collision check
find ~/.agents/skills -maxdepth 1 -type l -print
```

## Verification and commits

Run `~/.dotfiles/test-sync.sh` after changes and exercise discovery in the active
harness, for example `omp read skill://manage-skills`. Restart OMP or use Pi's
`/reload` when refreshing an existing session. Commit only when explicitly requested.

## Engine reference

`~/.dotfiles/sync-skills.sh`

- Links every top-level directory in `~/.dotfiles/skills/` into `~/.agents/skills/`.
- Populates Claude's skill location and the shared pool with root-skill/bundle links.
- Also syncs local agents and commands.
