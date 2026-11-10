# Skillset

A local Python 3.11+ / Git CLI for skill catalogs, profiles, independent machine choices, and reproducible installations. No pip dependencies, server, or AI harness is required.

**Selected, installed, and exposed are different.** Skillset manages the first two. `sync-skills.sh` still owns existing discovery links, agents, and commands. `skillset sync` never changes harness discovery.

## Run

Bootstrap provisions/checks Python and Git and links `~/.local/bin/skillset`; the shared Zsh configuration adds that directory to PATH. Restart the shell after bootstrap. Without bootstrap, run `./scripts/skillset` from the checkout. The launcher also works through its symlink and selects a supported versioned Python if `python3` is too old.

`--stow-only` / `--no-packages` does not download prerequisites; it reports missing runtimes. Package mode requires a supported runtime after provisioning. Older Linux distributions may require installing Python 3.11+ manually. An existing unrelated `~/.local/bin/skillset` is not overwritten.

Bootstrap does **not** import sources, select profiles, run manager sync, or relocate private files. Shared catalog and profile definitions do not activate skills automatically.

## First selection

These examples assume a shareable source already exists at `skills/example`. Registration defaults to **shared**; inspect the entire source, including companion and sibling files, before declaring it shared.

```sh
skillset source add personal --directory skills/example --provenance authored
skillset add example --source personal --path .
skillset profile create coding --name Coding
skillset profile add coding example
skillset profile select coding
skillset status
skillset sync
```

Register vendored third-party sources with `--provenance third-party` and optional `--upstream URL`. Import preserves existing working edits; it does not replace them with upstream downloads.

Profile selection is additive. `profile deselect PROFILE...` removes selected profiles. Enable and disable replace a skill's previous local override; reset restores inherited profile membership:

```sh
skillset enable example
skillset disable example
skillset reset example
```

Profile membership is a flat list, without nesting, wildcards, or exclusions. Rename changes the display name only. Removing referenced skills, sources, or profiles is rejected with reference details; no original files are deleted. Other machines' local references may need explicit repair after shared definitions are removed.

## Shared profiles

This checkout defines these reusable profiles:

| Profile | Membership |
| --- | --- |
| `coding` | Core implementation, planning, debugging, review, architecture, research, PR, and commit workflows. |
| `python` | Python design and testing patterns. |
| `rust` | Rust best practices and testing. |
| `figma` | The registered Figma namespace. |
| `decal` | The registered Decal production namespace. |
| `vercel` | `vercel-cli` and `ai-sdk`. |
| `tools` | `turborepo`. |

Membership is explicit, not a dynamic namespace rule: add future skills with `profile add`. Definitions are shared; profile selection and installation remain machine-local. All other skills remain independently enableable. Sentry currently has only `sentry-cli`, so it has no separate grouped profile.

## Remote sources

```sh
skillset source add upstream --git https://example.org/team/skills.git --ref main
skillset add remote-example --source upstream --path skills/example
skillset update upstream
skillset enable remote-example
skillset sync
skillset sync --offline
```

Git synchronization of dotfiles remains external. `update SOURCE...` resolves configured branches/tags and changes only exact source locks; `update --all` is an explicit all-remote-sources choice. Review and share lock changes with your existing Git workflow. A failed multi-source update retains old locks.

Sync fetches only missing exact locked content needed by selected skills. It preserves repository-relative assets without selecting sibling skills. Offline sync fails rather than substitutes another revision. Shared remote URLs must be portable; local Git repositories can be registered privately.

All selected installations are prepared before the active set switches. A failure retains the previous installed set while valid desired membership remains visible. Empty selection is valid. Caches and previous snapshots are retained; there is no pruning command.

Edit authored/vendored originals, not generated installations or managed fetched content. Unexpected edits to generated/fetched content are conflicts, not permission to overwrite it.

## Private sources

Private originals, registrations, profiles, locks, installations, and recovery contents stay outside dotfiles. Each new private source, skill, and profile requires `--private`:

```sh
skillset source add local-source --directory /absolute/local/source --private --provenance authored
skillset add local-skill --source local-source --path . --private
skillset profile create local-profile --private
skillset profile add local-profile local-skill
skillset profile select coding local-profile
```

A profile contains either shared or private skills, never both. A machine may select profiles from both scopes. IDs cannot collide across scopes or change visibility. Local status and JSON can contain private details: **do not publish them**. There is no export, transfer, or private-backup command. Migration recovery is local preservation, not a transfer feature.

`skillset validate --shared-only` validates shared files without reading private registrations or machine choices. Visibility checks are not a secret scanner: they cannot prove arbitrary source contents are safe to publish.

## Reviewed import and private relocation

Do not move existing private sources by hand as part of manager adoption. Create a local review plan:

```sh
skillset import --plan
# Edit the printed plan file locally, outside dotfiles.
skillset import --apply /absolute/path/to/reviewed-plan.json
```

The plan inventories existing top-level skill sources, nested `SKILL.md` directories, fingerprints, and affected existing discovery references. Every entry begins **unclassified**. Edit only `entries`:

- `classification`: `shared` or `private`.
- `source_id`: stable unique source ID.
- `provenance`: `authored` or `third-party`; optional `upstream` preserves known attribution.
- Every `skills[].id`: stable skill ID; optional `upstream_name` records the upstream display name. Do not remove discovered skill paths.
- For private sources, explicitly set `private_approved: true` after reviewing relocation and references.

Apply rejects unclassified entries, changed inventory/configuration/references, and duplicate IDs before publication. Import registers skills without selecting them. The plan, receipts, and journals are local-only artifacts, not safe to commit or upload.

Private relocation makes and verifies recovery and source copies under the private data root. It preserves the original discovery path as a Git-excluded local symlink to the relocated source, so existing links/configuration and repeated legacy sync continue to work. Any new exclusion goes into Git-local `info/exclude`, not tracked scripts. Existing JSON/TOML discovery references are verified; affected unsupported configuration formats block relocation rather than risk breaking discovery.

Tracked private content is refused: moving files cannot erase Git history. Resolve that separately before migration. On failure, recoverable originals/copies remain; an interrupted apply is recovered when the same unchanged plan is applied again. Successful unchanged-plan retries are idempotent. Subsequent source/configuration changes require a new plan.

## Files and JSON

Shared, versioned documents in this directory:

- `catalog.json`: `schema_version`, `sources`, and `skills` objects.
- `profiles.json`: `schema_version` and `profiles` object.
- `lock.json`: `schema_version` and `sources` mapping source IDs to exact commits.

Directory source records use `type: directory`, `path`, and `provenance`; shared paths are dotfiles-relative. Git records use `type: git`, `url`, `ref`, and `provenance`. Skill records use `source` and source-relative `path`, optionally `upstream_name`. Profiles use `skills` arrays and optional `name`.

All documents currently use `schema_version: 1`; unsupported schemas and duplicate JSON keys are errors. IDs start with an alphanumeric character and otherwise contain letters, digits, dot, underscore, colon, or hyphen. Source paths cannot traverse or resolve outside their declared roots. Arbitrary external dependencies and credentials are not provisioned.

Local configuration defaults to `$XDG_CONFIG_HOME/skillset` (`~/.config/skillset`): private `catalog.json`, `profiles.json`, `lock.json`, plus `machine.json` and `last-selection.json`. Machine state contains selected `profiles` and `overrides` values `enabled`/`disabled`; absence means inherited. Local data defaults to `$XDG_DATA_HOME/skillset` (`~/.local/share/skillset`), with separate shared/private source stores and an atomic `active.json` manifest. Local roots inside dotfiles or known harness discovery roots are rejected. `--repo PATH` selects another checkout for isolated use.

```sh
skillset list
skillset validate
skillset status --json
skillset resolve --json
```

Read-only inspection does not fetch, install, or rewrite configuration. Versioned resolve JSON reports desired selection, reasons, visibility, required content, installation availability and directories, active membership, and diffs. Missing known content is an installation mismatch, not an unknown identity. Invalid references mark retained last-good selection stale and exit unsuccessfully. Repair stale machine references with `reset` / `profile deselect`, or correct hand-edited JSON.

Diagnostics go to stderr; JSON stays on stdout. Exit codes: `0` success, `2` invalid input/configuration or stale selection, `3` unavailable/acquisition failure, `4` modification/concurrent-mutation conflict, `1` unexpected failure. Status can successfully describe unavailable/outdated installations without claiming a completed sync.

## Verification

From the repository, using Python 3.11+ on PATH:

```sh
python3 -B -m unittest -v test_skillset test_skillset_install test_skillset_migration
bash test_skillset_bootstrap.sh
bash test-bootstrap.sh
```

These checks use isolated temporary homes/checkouts and local Git fixtures; they do not migrate live skills.
