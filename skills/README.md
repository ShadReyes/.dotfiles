# Skills

These directories are the source of truth for local AI skills. Run `../sync-skills.sh` from this directory's parent to symlink them into the supported AI CLI locations.

Imported upstream skills:

- `brando` is a local plugin bundle vendored from `brs98/.dotfiles`.
- `matt` is a local plugin bundle vendored from `mattpocock/skills`.
- `herdr` is a local plugin bundle vendored from `ogulcancelik/herdr`.
- `grilling` remains a root skill vendored from `mattpocock/skills`.

## Skill naming policy

Every `name` in `SKILL.md` frontmatter must be globally unique because universal skill
harnesses recursively discover nested plugin skills without applying plugin namespaces.
Keep the preferred implementation of a workflow under its short name and prefix alternative
implementations with their bundle or author, such as `tdd` and `matt-tdd`.

`../test-sync.sh` enforces this invariant and reports every path involved in a collision.
When refreshing vendored copies, preserve these local compatibility renames:

- upstream `matt/skills/tdd` → local `matt/skills/matt-tdd` (`name: matt-tdd`)
- upstream `matt/skills/to-prd` → local `matt/skills/matt-to-prd` (`name: matt-to-prd`)
To refresh the imported copies from upstream:

```sh
git clone --depth 1 https://github.com/brs98/.dotfiles /tmp/brs98-dotfiles
git clone --depth 1 https://github.com/mattpocock/skills /tmp/mattpocock-skills

# Copy the relevant skill directories into skills/brando/skills/ and skills/matt/skills/.
# Keep root skills such as manage-skills under skills/<name>/.
```
