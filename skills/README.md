# Skills

These directories are the source of truth for local AI skills. Run `../sync-skills.sh` from this directory's parent to symlink them into the supported AI CLI locations.

Imported upstream skills:

- `brando` is a local plugin bundle vendored from `brs98/.dotfiles`.
- `matt` is a local plugin bundle vendored from `mattpocock/skills`.
- `grilling` remains a root skill vendored from `mattpocock/skills`.

To refresh the imported copies from upstream:

```sh
git clone --depth 1 https://github.com/brs98/.dotfiles /tmp/brs98-dotfiles
git clone --depth 1 https://github.com/mattpocock/skills /tmp/mattpocock-skills

# Copy the relevant skill directories into skills/brando/skills/ and skills/matt/skills/.
# Keep root skills such as manage-skills under skills/<name>/.
```
