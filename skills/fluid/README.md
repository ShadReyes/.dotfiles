# fluid (personal plugin)

Personal, work-specific skills for Fluid Commerce, namespaced under `fluid:`.

This is a local **skills-dir plugin**: because it lives at `~/.claude/skills/fluid/`
(via the `~/.agents/skills/fluid` -> `.dotfiles` symlink) and contains
`.claude-plugin/plugin.json`, Claude Code auto-loads it as `fluid@skills-dir` — no
remote marketplace required. Its skills are exposed as `fluid:<skill-name>`.

Distinct from the team's `fluid-skills` plugin (github.com/fluid-commerce/fluid-skills):
that one is shared/team-owned; this one is personal and version-controlled in my `.dotfiles`.

## Skills

- `fluid:investigate-prod-issue` — root-cause a production/user-reported issue using
  read-only prod DB access (no Docker) and scoped gcloud log queries.

## Adding a skill

Drop `skills/<name>/SKILL.md` here and restart Claude Code. No symlink needed — the
whole plugin dir is already linked into the agent hub.

## Credentials

Skills here may rely on machine-local credentials kept **out** of version control
(e.g. `~/.pgpass` for the read-only prod DB). Recreate those per machine.
