# matt (personal plugin)

Vendored from [`mattpocock/skills`](https://github.com/mattpocock/skills) at
commit `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76` (plugin version `1.2.3`).
The bundle contains the supported engineering and productivity skills from the
upstream plugin manifest. It excludes the upstream `in-progress` and `misc`
directories.

This local plugin uses the `matt:` namespace. Two skills have compatibility
names to keep every local `SKILL.md` frontmatter name globally unique:

- upstream `tdd` is `matt-tdd`
- upstream `improve-codebase-architecture` is
  `matt-improve-codebase-architecture`

The plugin lives under `~/.dotfiles/skills/matt/` and is symlinked into the
universal skill pool by `sync-skills.sh`.
