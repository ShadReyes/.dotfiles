# Skills

These directories are the source of truth for local AI skills. Run `../sync-skills.sh` from this directory's parent to symlink them into the supported AI CLI locations.

Imported upstream skills:

- `grill-me`, `grilling`, and `teach` come from `mattpocock/skills`.
- `teach` includes its workspace document formats: `MISSION-FORMAT.md`, `RESOURCES-FORMAT.md`, `LEARNING-RECORD-FORMAT.md`, and `GLOSSARY-FORMAT.md`.

To refresh the imported copies from upstream:

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo mattpocock/skills \
  --path skills/productivity/grill-me skills/productivity/grilling skills/productivity/teach
```
