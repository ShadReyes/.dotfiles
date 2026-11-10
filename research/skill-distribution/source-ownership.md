# Third-party source inventory and Figma comparison

Research snapshot: 2026-11-10. This report establishes acquisition and compatibility facts; it does **not** choose ownership, exposure, update, fork, vendoring, or migration policy.

## Scope and evidence boundaries

- **Observed local baseline:** dotfiles commit `bc5175c3c246ff728cc3a366f857baf30935c8df`. The original main checkout was inspected read-only for the approved shared catalog and the eight declared third-party shared source trees. Scoped `git status --short --untracked-files=all` and `git diff --name-status bc5175c…` returned no differences for those paths or `skills/README.md` at observation time. Thus the relevant shared working files matched the pinned research checkout; this is not a claim that the entire main checkout was clean. [L1–L10]
- **Declarations, not ancestry findings:** `provenance: third-party` is the current approved catalog classification. It does not prove complete authorship, source ancestry, or confidentiality status. Only approved shared records and shared trees were inspected. No private catalog, private originals, plans, receipts, recovery material, or unrelated home configuration was inspected. [L1]
- **Verified external comparison:** the public Figma repository was fetched into separate temporary storage and checked out at the exact recorded commit. No acquired skill, script, plugin installer, or MCP configuration was executed. Other vendors' attribution below is recorded local evidence, **not** a fresh upstream content audit.
- **Installation state unknown:** actual Figma plugin installation, enablement, account state, MCP connection, and runtime discovery were not inspected. Repository metadata and documentation below do not demonstrate that any client currently loads the bundle.
- No implementation, manager mutation, tests, builds, linters, or formatters were run. The report is the only research-branch change.

## 1. Declared third-party inventory

The shared catalog declares **eight third-party sources and 56 associated skill records**. All eight currently have `type: directory` and repository-relative paths `skills/<source-id>`. Four source records contain an `upstream` URL: `brando`, `figma`, `herdr`, and `matt`. None of the eight source records itself stores a revision or version pin. A source's optional attribution URL is therefore distinct from its current acquisition type. Counts and mappings are from the shared catalog, not active profiles or installed skills. [L1]

| Source ID; catalog skill count | Catalog upstream declaration | Recorded attribution, revision, or version | Gaps / evidence limits |
| --- | --- | --- | --- |
| `blowmage`; 3 | Absent | Local README says “vendored and adapted” from the `blowmage` author and explicitly attributes **`assess-me`** to `https://github.com/blowmage/harness`. Local wrapper version `1.2.0`; `assess-me` metadata version `0.1.0`. [L3] | No recorded whole-bundle upstream repository or acquisition commit. The `assess-me` URL must not be generalized to `plan-feature` and `tdd`. Adaptation is recorded, but no upstream diff was performed. |
| `brando`; 7 | `https://github.com/brs98/.dotfiles` | Local README and global skills README describe vendoring from that repository. Wrapper version `1.0.0`. Global refresh instructions copy relevant directories into `skills/brando/skills/`. [L2, L4] | No recorded acquisition commit, upstream plugin release, exact upstream subtree mapping, or license in the inspected bundle metadata. Wrapper version is not evidence of an upstream pin. |
| `cua-driver`; 1 | Absent | README links the product source at `https://github.com/trycua/cua/tree/main/libs/cua-driver/rust`; skill version `0.14.2`. README describes ClawHub `@cua/driver` and version-matched driver installation routes, plus repository MIT versus ClawHub MIT-0 distribution. [L5] | Product-source link and installation documentation are not proof of the route used for this copy. No acquisition commit or exact skill-package subtree is recorded in inspected attribution. Local tracked pack has `BROWSER.md`, `EMBEDDING.md`, `MACOS.md`, `README.md`, `RECORDING.md`, and `SKILL.md`; no tracked Windows/Linux guides. This is an observed local selection, not an instruction to install or expand it. |
| `figma`; 14 | `https://github.com/figma/mcp-server-guide` | Global README records plugin `2.2.155` and commit `2b85b7d27bd6ee124667fcfe88856f6b1f81671a`; wrapper author is Figma. Public revision and content comparison verified below. [L2, L6, U1–U3] | Full skills tree is unchanged, but local wrapper differs and the upstream repository contains other omitted capabilities. No explicit license grant was found in the pinned public tree; see §4. |
| `herdr`; 1 | `https://github.com/ogulcancelik/herdr` | Global README records vendoring from that repository. Local wrapper version `1.0.0`, exposing `./skills/`. [L2, L7] | No recorded acquisition commit, upstream release, exact upstream skill path, or license in inspected metadata. No fresh upstream comparison. |
| `matt`; 27 | `https://github.com/mattpocock/skills` | Bundle README records commit `59db609eb1e18aaf59b63284d0e52255aff0c63c`, plugin `1.3.1`, all 27 supported engineering/productivity skills, exclusion of upstream `in-progress` and `misc`, and retirement of `resolving-merge-conflicts`. Manifest declares MIT; retained MIT license credits Matt Pocock, 2026. [L8] | These are recorded attribution/selection facts, not independently re-fetched revision evidence. Two local directory/frontmatter compatibility renames are documented: `tdd` → `matt-tdd`; `improve-codebase-architecture` → `matt-improve-codebase-architecture`. |
| `rust-best-practices`; 1 | Absent | Skill declares author `apollographql`, version `1.1.0`, MIT, and Rust 1.70+/Cargo compatibility. It says it is based on the handbook at `https://github.com/apollographql/rust-best-practices`. [L9] | Handbook attribution is not proof of the skill's acquisition repository, subtree, or commit. Exact skill source remains unknown; do not silently promote the handbook URL to that role. |
| `vercel`; 2 | Absent | README records `ai-sdk` from `skills/use-ai-sdk` at `3c98985d44482f36704acd1a76f351f329028b5f`; that skill identifies `https://github.com/vercel/ai` as its repository. README records `vercel-cli` from `https://github.com/vercel/vercel`, `skills/vercel-cli`, at `17d9ebaf8e9b335d550dea1a243743a74edc772e`. Claude and Codex wrappers both use local version `0.2.0`; Codex metadata credits Vercel. [L10] | One local source groups attribution to two upstream repositories. Exact revision/path contents and license were not independently checked. The local wrapper version does not replace either recorded upstream commit. |

### Catalog membership boundaries

- `blowmage`: `assess-me`, `plan-feature`, `tdd`.
- `brando`: `find-skills`, `improve-codebase-architecture`, `prd-to-plan`, `react-doctor`, `turborepo`, `typescript-doctor`, `validate-startup-idea`.
- `cua-driver`, `herdr`, and `rust-best-practices`: one same-named skill each.
- `figma`: all 14 names enumerated in §2.
- `matt`: 20 engineering and seven productivity skills; its manifest enumerates all 27, including the two local compatibility names.
- `vercel`: `ai-sdk`, `vercel-cli`.

These are shared catalog source/skill mappings, not decisions about what should be exposed. A catalog source can be a selected subset or a local composition rather than an upstream repository boundary. [L1, L3–L10]

## 2. Figma: exact revision, layout, and complete skills comparison

### Revision verification

**Observed:** the documented repository exists at the recorded commit, whose commit message is “skills: Update image generation and asset handling (#116)”, dated `2026-10-14T08:45:59Z`. Its `.claude-plugin/plugin.json` version is `2.2.155`, matching the local README and local manifest. The public commit's root tree is `a322c6df342a7e58291051d5c498cc216f767564`. This verifies the recorded baseline; it does not assert that it is the latest upstream version. [L2, L6, U1, U2]

**Actual path mapping:** upstream `skills/<figma-name>/…` maps to local `skills/figma/skills/<figma-name>/…`. The upstream skills live at repository-root `skills/`, not beneath a `figma/` plugin directory. Other upstream roots, including `skills-figquery/` and `workflow-skills/`, are separate trees. [L6, U3, U4]

### All tracked skill and companion files

Git object comparison of the entire mapped tree found:

| Comparison | Result |
| --- | --- |
| Upstream tracked files under `skills/` | 93 |
| Local tracked files under `skills/figma/skills/` | 93 |
| Same path, mode, type, and blob content | 93 |
| Modified, upstream-only, or local-only skill/companion files | 0 |
| Mode for every file | `100644` |
| Both complete skills tree object IDs | `edc8f50c1e5fc079642c26f0efc26b0088209e88` |

**Observed:** all 14 `SKILL.md` files, **71 reference/support files**, and **eight JavaScript scripts** are byte-identical to the pinned upstream tree. The reference count includes `plugin-api-standalone.d.ts` and `plugin-api-standalone.index.md`, not just prose Markdown. There are no omitted supporting assets **inside this mapped skills tree**. This comparison includes names, frontmatter, compatibility/tool metadata, relative references, file modes, and script contents; scripts were compared as data and not executed. [L6, U3]

| Unchanged skill directory | All tracked files, including its `SKILL.md` |
| --- | ---: |
| `figma-code-connect` | 3 |
| `figma-create-new-file` | 1 |
| `figma-design-to-code` | 1 |
| `figma-generate-design` | 3 |
| `figma-generate-diagram` | 8 |
| `figma-generate-library` | 16 |
| `figma-generative-plugins` | 2 |
| `figma-implement-motion` | 7 |
| `figma-shaders` | 2 |
| `figma-swiftui` | 3 |
| `figma-use` | 21 |
| `figma-use-figjam` | 14 |
| `figma-use-motion` | 5 |
| `figma-use-slides` | 7 |
| **Total** | **93** |

The eight retained scripts are `bindVariablesToComponent.js`, `cleanupOrphans.js`, `createComponentWithVariants.js`, `createDocumentationPage.js`, `createSemanticTokens.js`, `createVariableCollection.js`, `inspectFileStructure.js`, and `validateCreation.js`, all beneath `figma-generate-library/scripts/`. The retained `figma-use/references/working-with-design-systems/` hierarchy contains nine reference files. These are acquisition payload, not disposable `SKILL.md`-only metadata. [L6, U3]

## 3. Figma differences that must remain visible

### Committed local compatibility wrapper

The **only modified common path** when comparing the entire local Figma bundle against the upstream root is `.claude-plugin/plugin.json`. Its complete semantic diff is:

```diff
 {
   "name": "figma",
-  "description": "Plugin that includes the Figma MCP server and Skills for common workflows",
+  "description": "Official Figma skills for common MCP workflows",
   "version": "2.2.155",
+  "skills": "./skills/",
   "author": {
     "name": "Figma"
   }
 }
```

The local version, plugin name, and author match upstream. The changed description narrows the wrapper to skills, and the explicit `skills` declaration is a local compatibility requirement recorded in `skills/README.md`. These are **committed differences**, not uncommitted drift or unproven cosmetic changes. No local skill-name renames exist in this Figma bundle. [L2, L6, U2]

The Figma bundle's sole path-history commit at observation was `b9a301dddb095385434025f4a4b0dda1a6521595` (“Add official Figma skills bundle”, 2026-10-14). It already added this wrapper plus all 93 companion/skill files and the global README attribution. The scoped original-main working-state checks found **no staged, unstaged, or untracked non-ignored changes** in the Figma tree, global skills README, shared catalog, or other seven inspected source trees. No ignored-path contents were inspected. [L11]

Local evidence identifiers:

| Path | Git blob/tree ID at local baseline |
| --- | --- |
| `skills/figma/skills/` tree | `edc8f50c1e5fc079642c26f0efc26b0088209e88` |
| `skills/figma/.claude-plugin/plugin.json` blob | `823e349a436215343560e90a0e78cbd254ad2d88` |
| Upstream `.claude-plugin/plugin.json` blob | `c60244d93d35542b10404e62c629c64c9d94d59c` |
| `skills/README.md` blob | `e99942961b2c4d048ed706485bf7183c7e4b0547` |
| `skillset/catalog.json` blob | `274159c7b18957ab4a7028801f5dc3667241722f` |

### Upstream content outside the local skills-only bundle

**Observed full comparison:** upstream has 221 tracked files; the local Figma bundle has 94. There are **127 upstream-only files**, **zero local-only files**, and the single modified common manifest above. The omitted paths are grouped exhaustively below and listed individually in Appendix A. Omission is a difference, not a finding that the content can be discarded. [L6, U4]

| Upstream-only root/group | Files | Observed role / boundary |
| --- | ---: | --- |
| `.cursor-plugin/plugin.json` | 1 | Cursor wrapper explicitly selects `./skills-figquery/` and declares `./.mcp.json`. [U5] |
| `.github/plugin/plugin.json` | 1 | Separate GitHub plugin metadata, same `2.2.155` version and Figma author. [U6] |
| `.mcp.json` | 1 | Figma remote MCP endpoint declaration, bundle-version header, tool titles, and icon metadata. Not present in local skills bundle. [U7] |
| `Figma Icon (Full-color).svg` | 1 | Root icon asset referenced by Cursor metadata. [U5] |
| `Figma Icon (Mono-line black, tight).svg` | 1 | Root icon asset referenced by MCP metadata. [U7] |
| `README.md` | 1 | Upstream guide and setup documentation. Attribution in the local global README is not a copy of this guide. [L2, U8] |
| `figma-power/` | 5 | Separate `POWER.md`, `mcp.json`, and three steering documents. [U9] |
| `gemini-extension.json` | 1 | Separate extension metadata. [U4] |
| `server.json` | 1 | Separate server metadata. [U4] |
| `skills-figquery/` | 92 | Alternative guidance tree plus its README; not the source of the local copied skills. [U10] |
| `workflow-skills/` | 22 | Two standalone workflow skills and their references/scripts, explicitly described upstream as **not bundled with the Figma plugin**. [U8, U11] |
| **Total** | **127** | |

The upstream `skills-figquery/README.md` says Cursor alone selects this alternative tree; the same 14 names/descriptions appear there, but guidance content differs. It describes `skills/` as the default tree for other clients. It also says the trees are generated by upstream tooling and should not be hand-edited. This report treats that as upstream source guidance, not authorization to run its generator or to introduce a new client workflow. [U10]

### Recorded local discovery/compatibility context

The local global README records preserving the full Figma `skills/` tree and upstream `figma-*` names, retaining the explicit local manifest `skills: "./skills/"`, and keeping MCP configuration separate. It lists `skills/figma/skills` as an OMP custom directory and describes existing Pi discovery through the shared pool/package. It also separates Skillset registration/profile management from the legacy discovery pool. These are **recorded repository expectations**; this research did not change or validate live Claude Code, Codex, OMP, or Pi settings. [L2]

**[INFERENCE]** Replacing the local Figma bundle with the entire upstream repository is not a content-neutral substitution: it changes payload boundaries, removes the local explicit skill declaration unless retained elsewhere, and brings server/other-client metadata into the candidate source. Conversely, fetching only the 14 entrypoint Markdown files loses 79 byte-identical supporting files. These are compatibility facts relevant to remote/fork/vendoring discussion, not a selection among those options. [L2, L6, U2–U11]

## 4. Figma license and attribution evidence

**Observed attribution:** upstream Claude manifest credits `Figma`; the local wrapper preserves that author and version. Local `skills/README.md` retains the official repository URL, exact commit, and plugin version. Upstream GitHub/Cursor metadata also identifies Figma/the official repository. [L2, L6, U2, U5, U6]

**Observed absence:** the fetched public tree at the pinned commit contains no file named `LICENSE`, `LICENCE`, `COPYING`, or `NOTICE` (including suffixed variants), no license field in the inspected plugin manifests, and no license/copyright statement found by a case-aware search across the public working tree. The search's only attribution-word hit was unrelated workflow guidance about quoting codebase documents. The local tracked Figma bundle likewise has no separate license/notice file. [L6, U2, U4–U6]

**Unknown:** an applicable redistribution/modification license grant was not established from this pinned tree. Public availability, an “official” description, or a plugin version is not evidence of a particular license. This report does not assign MIT or another license to Figma, does not claim that upstream has no rights terms elsewhere, and does not provide legal clearance for redistribution. No upstream license text was observed and then silently dropped from the mapped skill tree; the uncertainty exists at the inspected upstream baseline itself.

## 5. Facts available for later policy discussion; unresolved inputs

### Established inputs

1. Current acquisition is local-directory based even when an upstream URL is declared; attribution metadata alone is not a remote acquisition contract. [L1]
2. A library-wide “one catalog source equals one pristine upstream repository” assumption does not describe this inventory: Vercel is a two-repository composition; Blowmage records adaptation and only one explicit skill-level repository attribution; Matt has documented selection and compatibility renames; Figma has an unchanged complete skills tree plus a changed wrapper and omitted upstream surfaces. [L3, L8, L10; §§2–3]
3. For Figma, exact skill payload reconstruction has a verified repository, immutable commit, correct source subdirectory, and whole-tree identity. There is no evidence here of Figma skill-content patches requiring an upstream-content fork, but the committed wrapper changes and payload exclusions remain real requirements to account for. [L2, L6, U1–U4]
4. Figma's README attribution and wrapper metadata currently live outside/alongside the copied skills tree. A later policy must not mistake tree-content identity for identity of the complete distributable wrapper or its attribution record. [L2, L6, U2]
5. No automatic upstream update, manager takeover of server/plugin capabilities, expansion to other client workflows, or source migration follows from these findings.

### Unknowns, not filled with guessed URLs or policy choices

- Exact skill acquisition locations/commits for the full Blowmage bundle, Cua Driver pack, and Rust skill; Brando/Herdr acquisition revisions and exact upstream subtree mappings.
- Upstream content verification for the recorded Matt and Vercel revisions and all non-Figma differences; local wrapper versions do not settle these.
- Figma redistribution/modification license terms beyond the inspected pinned tree, and non-Figma licensing where no recorded license was identified.
- Actual client installation/enablement/discovery and live Figma MCP configuration; no narrowly filtered state probe was attempted, so those remain unverified rather than inferred from manifests.
- Human choices about source ownership, exposure, update cadence, remote source shape, fork exceptions, compatibility-overlay representation, and migration. These are intentionally not resolved by this research.

## Appendix A. Every upstream-only Figma path

Paths are relative to the upstream repository at `2b85b7d27bd6ee124667fcfe88856f6b1f81671a`. This is the complete 127-file upstream-only set when comparing upstream root with local `skills/figma/`. It does not classify these files as safe to remove or safe to acquire. [U4]

```text
.cursor-plugin/plugin.json
.github/plugin/plugin.json
.mcp.json
Figma Icon (Full-color).svg
Figma Icon (Mono-line black, tight).svg
README.md
figma-power/POWER.md
figma-power/mcp.json
figma-power/steering/code-connect-components.md
figma-power/steering/create-design-system-rules.md
figma-power/steering/implement-design.md
gemini-extension.json
server.json
skills-figquery/README.md
skills-figquery/figma-code-connect/SKILL.md
skills-figquery/figma-code-connect/references/advanced-patterns.md
skills-figquery/figma-code-connect/references/api.md
skills-figquery/figma-create-new-file/SKILL.md
skills-figquery/figma-design-to-code/SKILL.md
skills-figquery/figma-generate-design/SKILL.md
skills-figquery/figma-generate-diagram/SKILL.md
skills-figquery/figma-generate-diagram/references/architecture.md
skills-figquery/figma-generate-diagram/references/erd.md
skills-figquery/figma-generate-diagram/references/flowchart.md
skills-figquery/figma-generate-diagram/references/gantt.md
skills-figquery/figma-generate-diagram/references/sequence.md
skills-figquery/figma-generate-diagram/references/state.md
skills-figquery/figma-generate-diagram/references/workflow.md
skills-figquery/figma-generate-library/SKILL.md
skills-figquery/figma-generate-library/references/code-connect-setup.md
skills-figquery/figma-generate-library/references/component-creation.md
skills-figquery/figma-generate-library/references/discovery-phase.md
skills-figquery/figma-generate-library/references/documentation-creation.md
skills-figquery/figma-generate-library/references/error-recovery.md
skills-figquery/figma-generate-library/references/naming-conventions.md
skills-figquery/figma-generate-library/references/token-creation.md
skills-figquery/figma-generate-library/scripts/bindVariablesToComponent.js
skills-figquery/figma-generate-library/scripts/cleanupOrphans.js
skills-figquery/figma-generate-library/scripts/createComponentWithVariants.js
skills-figquery/figma-generate-library/scripts/createDocumentationPage.js
skills-figquery/figma-generate-library/scripts/createSemanticTokens.js
skills-figquery/figma-generate-library/scripts/createVariableCollection.js
skills-figquery/figma-generate-library/scripts/inspectFileStructure.js
skills-figquery/figma-generate-library/scripts/validateCreation.js
skills-figquery/figma-generative-plugins/SKILL.md
skills-figquery/figma-generative-plugins/references/authoring.md
skills-figquery/figma-implement-motion/SKILL.md
skills-figquery/figma-implement-motion/references/examples-and-anti-examples.md
skills-figquery/figma-implement-motion/references/framework-recommendations.md
skills-figquery/figma-implement-motion/references/gotchas.md
skills-figquery/figma-implement-motion/references/motion-lint-rules.md
skills-figquery/figma-implement-motion/references/svg-and-path-motion.md
skills-figquery/figma-implement-motion/references/unsupported-and-fallbacks.md
skills-figquery/figma-shaders/SKILL.md
skills-figquery/figma-shaders/references/authoring.md
skills-figquery/figma-swiftui/SKILL.md
skills-figquery/figma-swiftui/references/code-to-design.md
skills-figquery/figma-swiftui/references/design-to-code.md
skills-figquery/figma-use-figjam/SKILL.md
skills-figquery/figma-use-figjam/references/batch-modify.md
skills-figquery/figma-use-figjam/references/create-code-block.md
skills-figquery/figma-use-figjam/references/create-connector.md
skills-figquery/figma-use-figjam/references/create-label.md
skills-figquery/figma-use-figjam/references/create-section.md
skills-figquery/figma-use-figjam/references/create-shape-with-text.md
skills-figquery/figma-use-figjam/references/create-sticky.md
skills-figquery/figma-use-figjam/references/create-table.md
skills-figquery/figma-use-figjam/references/create-text.md
skills-figquery/figma-use-figjam/references/edit-text.md
skills-figquery/figma-use-figjam/references/figjam-colors.md
skills-figquery/figma-use-figjam/references/plan-board-content.md
skills-figquery/figma-use-figjam/references/position-figjam-nodes.md
skills-figquery/figma-use-motion/SKILL.md
skills-figquery/figma-use-motion/references/motion-easing.md
skills-figquery/figma-use-motion/references/motion-patterns.md
skills-figquery/figma-use-slides/SKILL.md
skills-figquery/figma-use-slides/references/slide-content.md
skills-figquery/figma-use-slides/references/slide-design.md
skills-figquery/figma-use-slides/references/slide-gotchas.md
skills-figquery/figma-use-slides/references/slide-grid.md
skills-figquery/figma-use-slides/references/slide-lifecycle.md
skills-figquery/figma-use-slides/references/slide-properties.md
skills-figquery/figma-use/SKILL.md
skills-figquery/figma-use/references/api-reference.md
skills-figquery/figma-use/references/common-patterns.md
skills-figquery/figma-use/references/component-patterns.md
skills-figquery/figma-use/references/critical-rules-deep.md
skills-figquery/figma-use/references/effect-style-patterns.md
skills-figquery/figma-use/references/fig-builder.md
skills-figquery/figma-use/references/gotchas.md
skills-figquery/figma-use/references/plugin-api-patterns.md
skills-figquery/figma-use/references/plugin-api-standalone.d.ts
skills-figquery/figma-use/references/plugin-api-standalone.index.md
skills-figquery/figma-use/references/text-style-patterns.md
skills-figquery/figma-use/references/validation-and-recovery.md
skills-figquery/figma-use/references/variable-patterns.md
skills-figquery/figma-use/references/working-with-design-systems/wwds-components--creating.md
skills-figquery/figma-use/references/working-with-design-systems/wwds-components--using.md
skills-figquery/figma-use/references/working-with-design-systems/wwds-components.md
skills-figquery/figma-use/references/working-with-design-systems/wwds-effect-styles.md
skills-figquery/figma-use/references/working-with-design-systems/wwds-text-styles.md
skills-figquery/figma-use/references/working-with-design-systems/wwds-variables--creating.md
skills-figquery/figma-use/references/working-with-design-systems/wwds-variables--using.md
skills-figquery/figma-use/references/working-with-design-systems/wwds-variables.md
skills-figquery/figma-use/references/working-with-design-systems/wwds.md
workflow-skills/generate-project-plan/SKILL.md
workflow-skills/generate-project-plan/references/blocks/diagram-section.md
workflow-skills/generate-project-plan/references/blocks/intro-callout.md
workflow-skills/generate-project-plan/references/blocks/metadata-strip.md
workflow-skills/generate-project-plan/references/blocks/multi-column-text.md
workflow-skills/generate-project-plan/references/blocks/nested-section.md
workflow-skills/generate-project-plan/references/blocks/section.md
workflow-skills/generate-project-plan/references/blocks/sticky-column.md
workflow-skills/generate-project-plan/references/blocks/table.md
workflow-skills/generate-project-plan/references/blocks/text-primitives.md
workflow-skills/generate-project-plan/references/foundation/codebase-grounding.md
workflow-skills/generate-project-plan/references/foundation/layout.md
workflow-skills/generate-project-plan/references/foundation/palette.md
workflow-skills/generate-project-plan/references/foundation/plugin-api-traps.md
workflow-skills/generate-project-plan/references/section-catalog.md
workflow-skills/video-interaction-mapper/README.md
workflow-skills/video-interaction-mapper/SKILL.md
workflow-skills/video-interaction-mapper/scripts/extract_key_frames.py
workflow-skills/video-interaction-mapper/scripts/generate_figma_calls.py
workflow-skills/video-interaction-mapper/scripts/prepare_upload_frames.py
workflow-skills/video-interaction-mapper/scripts/resolve_moment_frames.py
workflow-skills/video-interaction-mapper/scripts/update_run_manifest.py
```

## Evidence and reproducibility

Primary local citations are immutable views of the approved shared files at the inspected baseline. Public citations are immutable views of the verified upstream revision. Local working-state observations are time-scoped research observations; an immutable repository URL cannot represent later uncommitted filesystem state.

- **L1:** [Shared catalog](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skillset/catalog.json): third-party source records, acquisition types, attribution fields, and source/skill mappings.
- **L2:** [Global skills README](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/README.md): imported upstream attribution, Figma pin, names/layout, Matt compatibility renames, and recorded discovery expectations.
- **L3:** Blowmage [README](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/blowmage/README.md), [manifest](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/blowmage/.claude-plugin/plugin.json), and [`assess-me` metadata](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/blowmage/skills/assess-me/SKILL.md).
- **L4:** Brando [README](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/brando/README.md) and [manifest](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/brando/.claude-plugin/plugin.json).
- **L5:** Cua Driver [README](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/cua-driver/README.md), [skill metadata](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/cua-driver/SKILL.md), and [tracked shared tree](https://github.com/ShadReyes/.dotfiles/tree/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/cua-driver).
- **L6:** Local Figma [complete bundle](https://github.com/ShadReyes/.dotfiles/tree/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/figma), [skills tree](https://github.com/ShadReyes/.dotfiles/tree/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/figma/skills), and [compatibility manifest](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/figma/.claude-plugin/plugin.json).
- **L7:** Herdr [manifest](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/herdr/.claude-plugin/plugin.json); upstream attribution is in L1–L2.
- **L8:** Matt [README](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/matt/README.md), [manifest](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/matt/.claude-plugin/plugin.json), and [retained license](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/matt/LICENSE).
- **L9:** Rust [skill attribution and metadata](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/rust-best-practices/SKILL.md).
- **L10:** Vercel [README](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/vercel/README.md), [AI SDK repository attribution](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/vercel/skills/ai-sdk/SKILL.md), [Claude manifest](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/vercel/.claude-plugin/plugin.json), and [Codex manifest](https://github.com/ShadReyes/.dotfiles/blob/bc5175c3c246ff728cc3a366f857baf30935c8df/skills/vercel/.codex-plugin/plugin.json).
- **L11:** [Figma import commit](https://github.com/ShadReyes/.dotfiles/commit/b9a301dddb095385434025f4a4b0dda1a6521595), plus scoped local `git log -- skills/figma`, status, and diff observations described above.
- **U1:** [Official public commit](https://github.com/figma/mcp-server-guide/commit/2b85b7d27bd6ee124667fcfe88856f6b1f81671a) and [first-party commit API record](https://api.github.com/repos/figma/mcp-server-guide/commits/2b85b7d27bd6ee124667fcfe88856f6b1f81671a).
- **U2:** [Upstream Claude manifest](https://github.com/figma/mcp-server-guide/blob/2b85b7d27bd6ee124667fcfe88856f6b1f81671a/.claude-plugin/plugin.json).
- **U3:** [Complete upstream skills tree](https://github.com/figma/mcp-server-guide/tree/2b85b7d27bd6ee124667fcfe88856f6b1f81671a/skills).
- **U4:** [Complete upstream root](https://github.com/figma/mcp-server-guide/tree/2b85b7d27bd6ee124667fcfe88856f6b1f81671a) and [recursive Git tree API](https://api.github.com/repos/figma/mcp-server-guide/git/trees/a322c6df342a7e58291051d5c498cc216f767564?recursive=1).
- **U5:** [Upstream Cursor manifest](https://github.com/figma/mcp-server-guide/blob/2b85b7d27bd6ee124667fcfe88856f6b1f81671a/.cursor-plugin/plugin.json).
- **U6:** [Upstream GitHub manifest](https://github.com/figma/mcp-server-guide/blob/2b85b7d27bd6ee124667fcfe88856f6b1f81671a/.github/plugin/plugin.json).
- **U7:** [Upstream MCP declaration](https://github.com/figma/mcp-server-guide/blob/2b85b7d27bd6ee124667fcfe88856f6b1f81671a/.mcp.json).
- **U8:** [Upstream guide, including standalone workflow boundary](https://github.com/figma/mcp-server-guide/blob/2b85b7d27bd6ee124667fcfe88856f6b1f81671a/README.md#tools-and-skills).
- **U9:** [Upstream Figma power tree](https://github.com/figma/mcp-server-guide/tree/2b85b7d27bd6ee124667fcfe88856f6b1f81671a/figma-power).
- **U10:** [Alternative-tree README](https://github.com/figma/mcp-server-guide/blob/2b85b7d27bd6ee124667fcfe88856f6b1f81671a/skills-figquery/README.md) and [complete alternative tree](https://github.com/figma/mcp-server-guide/tree/2b85b7d27bd6ee124667fcfe88856f6b1f81671a/skills-figquery).
- **U11:** [Standalone workflow tree](https://github.com/figma/mcp-server-guide/tree/2b85b7d27bd6ee124667fcfe88856f6b1f81671a/workflow-skills).

Comparison method used Git's own tracked tree objects rather than sampling entrypoints:

```sh
# In separate, read-only-inspected source checkouts:
git -C <main-checkout> rev-parse HEAD:skills/figma/skills
git -C <pinned-upstream-copy> rev-parse HEAD:skills
# Both returned edc8f50c1e5fc079642c26f0efc26b0088209e88.

git -C <main-checkout> ls-tree -r HEAD -- skills/figma/
git -C <pinned-upstream-copy> ls-tree -r HEAD
# Strip only the local skills/figma/ prefix and compare path/mode/type/blob.
# Full result: 94 local files, 221 upstream files; one modified common
# manifest, 127 upstream-only files, no local-only files.
```
