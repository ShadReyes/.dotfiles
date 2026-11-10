---
name: manage-skills
description: Add, author, update, or audit agent skills in ~/.dotfiles and the local universal pool (~/.agents/skills). Version public skills; preserve Git exclusions for confidential machine-local skills and docs. Use when installing, creating, updating, or auditing skills.
---

# manage-skills

Use [Skillset](../../../../skillset/README.md) for standalone registration,
profiles, machine selection, installations, and reviewed private relocation.
It does not control harness discovery. Existing discovery links, agents, and
commands remain owned by `~/.dotfiles/sync-skills.sh`; the legacy workflow follows.

## The invariant (never break it)

- Portable authored sources stay in dotfiles; generated Skillset installations
  and private sources stay outside it. Preserve relocated private aliases and
  their machine-local Git exclusions; keep originals outside dotfiles.
- Root portable skills live at `~/.dotfiles/skills/<name>/SKILL.md`.
- Version public skills only. Existing confidential skills may remain in ignored
  directories pending reviewed migration; new Skillset private sources live
  outside dotfiles. Preserve legacy exclusions, verify them with
  `git check-ignore -v`, and keep confidential names/content out of tracked docs.
  See `~/.dotfiles/skills/README.md` for the privacy boundary.
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

OMP and Pi setup is documented in `~/.dotfiles/skills/README.md`. Adding a skill
beneath an existing OMP discovery root needs no configuration update; a new bundle
or category needs its parent registered once. Pi's package manifest needs no change.

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
