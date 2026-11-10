# Installed harness baseline and narrow Figma entry points

Research date: 2026-11-10. Shared repository baseline: [`bc5175c3c246ff728cc3a366f857baf30935c8df`](https://github.com/ShadReyes/.dotfiles/tree/bc5175c3c246ff728cc3a366f857baf30935c8df). This report records installed-version and Figma-only filesystem/configuration observations. It does not choose ownership, exposure policy, or migration, and does not establish a running session's effective capabilities.

## Findings

| Harness | Observed availability / version | Evidence and limits |
| --- | --- | --- |
| Claude Code | No `claude` executable resolved on the research shell's PATH. Installed version **unverified**. | Exact-name PATH probe only; narrow conventional public package-metadata probes also found no matching manifest. This is not proof of total absence, nor evidence about an application-bundled or separately managed copy. [L1,L3] |
| Codex CLI | No `codex` executable resolved on that PATH. Installed version **unverified**. | Same bounded observation and absence caveat as Claude Code. No app, session, authentication state, or broader installation inventory was inspected. [L1,L3] |
| OMP | PATH-resolved executable reports **`omp/18.18.6`**. | `omp --version` completed successfully. Its entry point resolves through a symlink to a large executable rather than the small shell-wrapper form found for Pi. This is the executable's reported version, not a reconstruction of its source commit or proof of its active settings. [L1,L2] |
| Pi | PATH entry is a managed shell launcher; its selected installed package is **`@earendil-works/pi-coding-agent` `0.99.1`**. | Static launcher inspection established how it selects a release. The selected public package manifest reports `0.99.1`, agreeing with the selected-release marker, and the selected executable exists and is executable. Pi was **not invoked**. This is installed-package evidence, not captured CLI output or a claim that the session currently running elsewhere uses this build. [L1,L3] |

**Figma:** both `~/.claude/skills/figma` and `~/.agents/skills/figma` exist as directory symlinks resolving to the approved shared repository's `skills/figma` bundle. The target has a Figma plugin manifest and all fourteen known nested skill entry points. That establishes linked source presence—not a plugin-manager installation, effective enablement, loading, or invocation. [L4,R1,R2]

## Local observation record

These first-hand observations are the primary local evidence for this report. Only approved shared Figma paths, executable/installed-public-package metadata, and narrowly projected Figma configuration fields were inspected. Generic role notation below intentionally omits machine-specific installation roots. The records do not include private Skillset identifiers, catalogs, plans, receipts, originals, recovery data, unrelated plugin records, credentials, or sessions.

### L1 — Exact-name PATH availability

The shell builtin probe was:

```sh
command -v claude codex omp pi
```

Only `omp` and `pi` resolved. A separate exact-name resolver produced the same per-name presence results. Both resolved entries were symlinks. No full command or skill/plugin inventory was requested. PATH non-resolution is scoped to this research environment and time; an installed tool outside that PATH remains possible.

### L2 — OMP version-only exit

```text
$ omp --version
omp/18.18.6
```

The command exited successfully. No agent session, discovery listing, reload, installer, update, or configuration-changing subcommand was invoked. Neither binary provenance nor equality with a particular upstream commit was established.

### L3 — Pi launcher and installed public metadata

The existing PATH-resolved Pi launcher was read as text; it was not executed. Its relevant static sequence is:

1. Follow its own symlink chain and derive the managed installation root from the launcher's location.
2. Read `<managed-Pi-root>/install/current-version` and reject invalid version strings.
3. Select `<managed-Pi-root>/install/releases/<selected-version>/node_modules/.bin/pi`, requiring an executable target.
4. Optionally prepend the managed Node runtime to the child process's PATH, export `PI_MANAGED_INSTALL_ROOT`, and `exec` the selected Pi entry point.

The static launcher contains no install/update invocation. Nevertheless, installed public metadata was sufficient, so no Pi process was launched and its environment-setting path was not exercised.

Privacy-filtered observations from that selected release:

```json
{
  "selectedRelease": "0.99.1",
  "selectedExecutablePresentAndExecutable": true,
  "package": {
    "name": "@earendil-works/pi-coding-agent",
    "version": "0.99.1",
    "bin": {"pi": "dist/bundle/cli.js"},
    "repository": {
      "type": "git",
      "url": "git+https://github.com/earendil-works/pi.git",
      "directory": "packages/coding-agent"
    }
  }
}
```

The package identity comes from the actual selected release's `node_modules/@earendil-works/pi-coding-agent/package.json`, not an assumption that all Pi installations still use `@badlogic`. Its `repository` field is package-declared attribution, not an independent installation-integrity or source-commit audit. [P1]

Separately, exact public package-manifest probes under the conventional Homebrew global, Bun global, and home-local global `node_modules` roles found no manifests for `@anthropic-ai/claude-code`, `@openai/codex`, `@oh-my-pi/pi-coding-agent`, `@badlogic/pi-coding-agent`, or `@earendil-works/pi-coding-agent`. These bounded misses neither contradict the separately managed Pi release nor establish machine-wide absence. No package-root directory was enumerated.

### L4 — Approved Figma source/link presence

| Narrow probe | Observed result |
| --- | --- |
| `~/.claude/skills/figma` | Symlink; target directory exists; resolved target equals approved shared `skills/figma`. |
| `~/.agents/skills/figma` | Same result and same approved shared target. |
| Shared `skills/figma/.claude-plugin/plugin.json` | `name: "figma"`, `version: "2.2.155"`, `skills: "./skills/"`. |
| Shared bundle-root `skills/figma/SKILL.md` | Absent. |
| Fourteen known `skills/figma/skills/<figma-name>/SKILL.md` entry points | All present. The probe used the fourteen already approved names rather than enumerating other sources. |

The observed wrapper fields agree with the pinned shared manifest. The repository README documents the full nested Figma tree, retained upstream names, explicit local `skills` declaration, and separately configured MCP. Its sync script describes the two bundle-level link destinations. Neither file is evidence of currently active settings. [R1,R2]

This narrow presence check did not repeat the prior report's whole-tree byte comparison. The earlier immutable source report remains the evidence for tree equality and wrapper differences. [R3]

### L5 — Figma-only Claude registration / user declaration

The known default registry role `~/.claude/plugins/installed_plugins.json` was probed with a JSON projection selecting **only** the exact `figma` key or keys beginning `figma@`, retaining only generic origin category, `scope`, and `version`. The file was **not found** at that default location. No other registry/cache root or recovery file was searched.

The same exact Figma-key selection over `enabledPlugins` in `~/.claude/settings.json` returned **`[]`**. The projection would retain only Figma origin category and its user-level enable value; it did not return settings contents, marketplace names, install paths, or any unrelated plugin entry. The research process had neither `CLAUDE_CONFIG_DIR` nor `CLAUDE_CODE_PLUGIN_CACHE_DIR` override set; values were not dumped.

These observations mean only:

- No Figma install record was obtainable from that missing default registry.
- No exact Figma plugin enable/disable declaration was observed in that one user settings field.

They do **not** mean Figma is disabled, uninstalled everywhere, or unloaded. Claude's current owning documentation distinguishes settings declaration, fetched install records, and loaded session state; it also documents in-place `@skills-dir` plugins that need not have a marketplace install receipt. Other scopes, defaults, managed policy, alternate execution environments, or account-synced state were not inspected. [C1]

### L6 — Deliberately unverified entry-point settings

The approved shared README names `skills/figma/skills` as an OMP `skills.customDirectories` target and documents Pi's shared-pool/package workflows. These are repository instructions, not observed local registration. [R1]

OMP's actual custom-directory setting remains **unverified**. A check for an already available safe YAML parser returned unavailable; no YAML configuration contents were dumped and no parser was installed. The prerequisite for a later narrow read is an existing trusted YAML-capable projection that emits only whether the exact approved Figma directory is registered, not other directories/settings. Even a matching user setting would not establish effective enablement or loading.

Pi's actual package registration/resource filters and OMP provider/skill filters remain **unverified**. The library-wide Pi package record would not be a Figma-only plugin entry, so it was not inspected. No project, session, trust, enterprise-policy, MCP, or plugin-runtime state was read.

## Relationship to the earlier capability report

The [earlier harness report](https://github.com/ShadReyes/.dotfiles/blob/b409c767321e0dcdbb12b14a4f310a2e47673356/research/skill-distribution/harness-discovery.md) identifies source snapshots, not the installations measured here. [H1]

| Earlier evidence | Observed local baseline | Permitted conclusion |
| --- | --- | --- |
| OMP `18.18.7`, commit `e325ffc73ab86e03bdd20a91b77d8e2b3964c906` | Executable reports `18.18.6`. | Versions differ. The report's exact provider, filtering, namespace, and rediscovery implementation cannot be attributed to this binary merely because the version difference is small. No documented feature-introduction boundary was established here. |
| Pi `@earendil-works/pi-coding-agent` `1.5.2`, commit `750d6210308eb4ef4fa393dce7b7490be8234eeb` | Selected installed package is the same package name at `0.99.1`. | Versions differ. Current trust, package reconciliation, shared-root discovery, MCP, and collision semantics are not thereby proven for the selected installed release. No supported feature boundary was established here. |
| Codex commit `c9bbed2dae6aa1d3a0057001dec64d08e7882a9f`, workspace version `0.0.0` | No PATH executable/version established. | No installed-release comparison is possible; `0.0.0` must not be used as an installed version. |
| Claude Code mutable official docs with explicit minimum versions for some features | No PATH executable/version established. | No documented version boundary can be applied locally. In particular, current `@skills-dir` documentation describes a possible route, not a measured capability of an unknown local Claude build. |

No new source-snapshot behavior was promoted to an installed-behavior claim. Symlink presence likewise does not establish traversal, namespace, deduplication, or refresh behavior in any of these installed clients.

## State distinctions and unresolved inputs

| State | Established here | Still unknown |
| --- | --- | --- |
| Installed build/package | OMP's version-only self-report; Pi's selected package metadata and executable presence. | Claude/Codex versions; exact binary source commits/integrity; versions used by any existing sessions. |
| Figma source/link presence | Two approved shared bundle links; manifest identity/version; fourteen known nested entry points. | Other copies or alternate roots, intentionally not inventoried. |
| Registration/declaration | Missing default Claude install-registry file; no Figma user `enabledPlugins` entry returned by the narrow projection. | Alternate/scoped registration, OMP custom directory, Pi package/resource registration. |
| Effective enablement | Not established. | Applicable defaults, settings precedence, policy, trust, provider and resource filters. |
| Loading | Not inspected. | Whether any session has admitted any local Figma instructions, and through which route. |
| Invocation | Not exercised. | Whether any particular Figma skill can be invoked in a particular installed harness/session. |

This baseline does not justify removing, installing, enabling, disabling, migrating, or updating any source/plugin. It does not take over unrelated plugin capabilities or MCP. Obtaining the remaining facts requires separately authorized, still narrowly scoped evidence—not interpreting an absent PATH entry or empty Figma settings projection as a negative runtime test.

## Primary-source citations

Local primary evidence: **L1–L6** above are contemporaneous, bounded observation records. Their sanitized outputs are included because publishing a full home configuration or executable-location dump would exceed the research boundary.

- **R1** — Shared [`skills/README.md`](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/README.md#L30-L35), [OMP entry-point convention](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/README.md#L62-L88), [Pi convention](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/README.md#L90-L101), and [`sync-skills.sh`](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/sync-skills.sh#L30-L60).
- **R2** — Pinned shared [Figma manifest](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/figma/.claude-plugin/plugin.json) and [Figma skills tree](https://github.com/ShadReyes/.dotfiles/tree/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/figma/skills).
- **R3** — [Completed source comparison](https://github.com/ShadReyes/.dotfiles/blob/9cfffafc6296fd40dd131ad30ea75b14eb3cea54/research/skill-distribution/source-ownership.md), containing pinned upstream/local tree and blob identities. Secondary to the linked underlying first-party source objects; used only for the already completed comparison, not new installed-state evidence.
- **C1** — Anthropic, [Plugin loading reference](https://code.claude.com/docs/en/plugins/loading.md), retrieved 2026-11-10: declared/fetched/loaded distinction; default registry/cache roles; `enabledPlugins` scope precedence; in-place `@skills-dir` origin. Mutable current documentation, not an identified installed Claude version.
- **P1** — Installed Pi package metadata recorded in L3 declares the first-party repository [`earendil-works/pi`](https://github.com/earendil-works/pi), directory `packages/coding-agent`. This citation identifies the owning project; no uninspected repository revision is attributed to the installed package.
- **H1** — [Completed capability report and its primary-source citations](https://github.com/ShadReyes/.dotfiles/blob/b409c767321e0dcdbb12b14a4f310a2e47673356/research/skill-distribution/harness-discovery.md#evidence-boundary-and-versions). Its pinned first-party manifests identify [OMP `18.18.7`](https://github.com/can1357/oh-my-pi/blob/e325ffc73ab86e03bdd20a91b77d8e2b3964c906/packages/coding-agent/package.json), [Pi `1.5.2`](https://github.com/earendil-works/pi/blob/750d6210308eb4ef4fa393dce7b7490be8234eeb/packages/coding-agent/package.json), and [Codex workspace version](https://github.com/openai/codex/blob/c9bbed2dae6aa1d3a0057001dec64d08e7882a9f/codex-rs/Cargo.toml#L174-L175).

## Research operations boundary

Exactly this report is the research-branch deliverable. No main-checkout/ticket/map changes, private Skillset inspection, acquired code execution, live discovery experiments, CLI inventory, reload, agent session launch, installer, software acquisition/update, plugin-manager mutation, MCP configuration change, tests, builds, linters, or formatters were performed. The authorized publication is a throwaway research branch only, with no PR or merge.
