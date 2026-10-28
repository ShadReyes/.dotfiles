# matt (personal plugin)

Vendored from [`mattpocock/skills`](https://github.com/mattpocock/skills) at
commit `59db609eb1e18aaf59b63284d0e52255aff0c63c` (plugin version `1.3.1`).
The bundle contains all 27 supported engineering and productivity skills
from the upstream plugin manifest, including `pr`, `implement-spec`, and `retro`.
It excludes the upstream `in-progress` and `misc` directories.

This local plugin uses the `matt:` namespace. Two skills have compatibility
names to keep every local `SKILL.md` frontmatter name globally unique:

- upstream `tdd` is `matt-tdd`
- upstream `improve-codebase-architecture` is
  `matt-improve-codebase-architecture`

The plugin lives under `~/.dotfiles/skills/matt/` and is symlinked into the
universal skill pool by `sync-skills.sh`.

Upstream retired `resolving-merge-conflicts`; this bundle follows that removal.
