# Skills

These directories are the source of truth for local AI skills. Run `../sync-skills.sh` from this directory's parent to symlink them into the supported AI CLI locations.

[Skillset](../skillset/README.md) separately manages registration, profiles, and
installations. Its selection does not change this legacy discovery pool. Private
sources registered with Skillset live outside dotfiles; reviewed relocation keeps
Git-excluded local path aliases so existing discovery continues to work.

## Machine-local confidential context

Public skills are versioned; confidential company skills and docs are local-only.
Existing confidential sources may remain under ignored directories pending a
reviewed Skillset migration. Keep new Skillset private originals outside dotfiles;
do not copy relocated sources back into this library. Preserve existing ignore
rules and verify each relevant exclusion with `git check-ignore -v <path>`.
Gitignore matches paths, not file contents.

`sync-skills.sh` only creates local harness symlinks, so ignored skills remain
available on this machine without being included in a Git clone. Preserve those
exclusions when updating skills; never force-add confidential files or copy
their contents into tracked documentation. Gitignore does not remove existing
Git history or control backups, cloud file sync, or AI-provider retention.

Imported upstream skills:

- `brando` is a local plugin bundle vendored from `brs98/.dotfiles`.
- `matt` is a local plugin bundle vendored from `mattpocock/skills`.
- `herdr` is a local plugin bundle vendored from `ogulcancelik/herdr`.
- Figma is supplied by independently installed native harness plugins, not this
  library or Skillset. See [native Figma setup](#native-figma-plugin).

## Native Figma plugin

For first-time OMP setup, add the official catalog before installing. An
unregistered marketplace identifier can fall through to ordinary package
installation; the preview must not warn that user scope is being ignored.

```sh
omp plugin marketplace add anthropics/claude-plugins-official
omp plugin install --dry-run --scope user figma@claude-plugins-official
omp plugin install --scope user figma@claude-plugins-official
omp plugin list
```

If the catalog is already registered, verify its official source and reuse it.
Run `/reload-plugins` manually in OMP, then verify skill loading and required tool
access separately. This does not register skills with Skillset or authenticate MCP.
Other harnesses use their own [Figma setup instructions](https://developers.figma.com/docs/figma-mcp-server/remote-server-installation/);
Codex app plugin setup is not Codex CLI setup. No automatic fallback is installed.

The retired copy came from [figma/mcp-server-guide](https://github.com/figma/mcp-server-guide),
version `2.2.155`, commit `2b85b7d27bd6ee124667fcfe88856f6b1f81671a`.
Its wrapper had a local description and explicit `skills: "./skills/"` declaration.
Recovery copies stay machine-local outside the repository. For stale machine
selections after pulling this change, use the [Figma reference repair](../skillset/README.md#retired-figma-profile).

## Skill naming policy

Keep `name` values globally unique because harnesses such as Pi discover nested
skills without applying plugin namespaces. Retain upstream names and the existing
bundle layout; prefix only alternative implementations that would otherwise
collide, such as `tdd` and `matt-tdd`.

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
# Keep root skills under skills/<name>/ and bundled skills in their existing taxonomy.
```

## Native OMP discovery

OMP scans direct children of each skill root, not arbitrary nested bundles.
Configure the following once in `~/.omp/agent/config.yml`, preserving other settings:

```yaml
skills:
  customDirectories:
    - ~/.dotfiles/skills/dotfiles/skills
    - ~/.dotfiles/skills/blowmage/skills
    - ~/.dotfiles/skills/brando/skills
    - ~/.dotfiles/skills/herdr/skills
    - ~/.dotfiles/skills/matt/skills/engineering
    - ~/.dotfiles/skills/matt/skills/productivity
    - ~/.dotfiles/skills/vercel/skills
```

Add skills beneath these parents without changing configuration or creating
per-skill links. A new bundle or category needs its parent registered once.
Root skills continue loading through the shared pool populated by `sync-skills.sh`.

Invoke unique names directly, such as `/skill:manage-skills` or
`skill://manage-skills`. OMP assigns namespaces to differing name collisions;
native plugin invocation names remain harness-specific. A local compatibility
manifest is not proof of a native plugin installation.
Restart OMP after changing discovery configuration.

## Native Pi discovery

Pi recursively discovers the existing shared pool. For direct source loading
independent of those links, this directory is also a local Pi package:

```sh
pi install ~/.dotfiles/skills
```

The package manifest exposes the whole collection, including nested categories.
Register it once; new skills and edits require no manifest changes or copies.
Use `/reload` in an existing Pi session to refresh its skills.

No flat indexer or extra Python runtime is required by synchronization.
