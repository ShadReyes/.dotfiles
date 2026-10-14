# Skills

These directories are the source of truth for local AI skills. Run `../sync-skills.sh` from this directory's parent to symlink them into the supported AI CLI locations.

Imported upstream skills:

- `brando` is a local plugin bundle vendored from `brs98/.dotfiles`.
- `matt` is a local plugin bundle vendored from `mattpocock/skills`.
- `herdr` is a local plugin bundle vendored from `ogulcancelik/herdr`.
- `figma` contains the 14 official MCP skills from
  [figma/mcp-server-guide](https://github.com/figma/mcp-server-guide), plugin
  version `2.2.155`, commit `2b85b7d27bd6ee124667fcfe88856f6b1f81671a`.
  Preserve the complete `skills/` tree and upstream `figma-*` names when refreshing;
  keep the local manifest's `skills: "./skills/"` declaration. MCP is configured
  separately in the client; the bundle contains skills only.

## Skill naming policy

Every `name` in `SKILL.md` frontmatter must be globally unique because some skill harnesses
discover nested plugin skills without applying plugin namespaces. Global uniqueness also keeps
the flat `~/.agents/skills-index/` discovery index unambiguous.
Keep the preferred implementation of a workflow under its short name and prefix alternative
implementations with their bundle or author, such as `tdd` and `matt-tdd`.

`../test-sync.sh` enforces this invariant and reports every path involved in a collision.
When refreshing vendored copies, preserve these local compatibility renames:

- upstream `matt/skills/engineering/tdd` → local
  `matt/skills/engineering/matt-tdd` (`name: matt-tdd`)
- upstream `matt/skills/engineering/improve-codebase-architecture` → local
  `matt/skills/engineering/matt-improve-codebase-architecture`
  (`name: matt-improve-codebase-architecture`)
To refresh the imported copies from upstream:

```sh
git clone --depth 1 https://github.com/brs98/.dotfiles /tmp/brs98-dotfiles
git clone --depth 1 https://github.com/mattpocock/skills /tmp/mattpocock-skills

# Copy the relevant skill directories into skills/brando/skills/ and skills/matt/skills/.
# Keep root skills such as manage-skills under skills/<name>/.
```

## Native OMP discovery

OMP scans direct children of each skill root, not arbitrary nested bundles.
Configure the following once in `~/.omp/agent/config.yml`, preserving other settings:

```yaml
skills:
  customDirectories:
    - ~/.dotfiles/skills/figma/skills
```

Restart OMP after changing discovery configuration.
