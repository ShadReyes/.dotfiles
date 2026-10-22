---
name: launch-product
description: Take a fixed or personalized decal from a reference URL or existing SVG through design alternatives and selection, design approval, DecalFlow registration, physical cut qualification, approved listing assets, and a verified Etsy draft. Use to start or resume the complete product-launch workflow.
---

# Launch a decal product

Coordinate the existing design, DecalFlow, Inkcut, and listing-assets skills. Finish with a verified Etsy **draft** and its DecalFlow Product/listing mapping. Publication and cutter motion require separate actions; this workflow does neither.

## Start or resume

Create or load `launch.json` in the product's production folder. Follow [run state and approvals](references/run-state.md) before mutations or resuming a stage. Reuse existing design versions, Products, listing IDs, artifacts, and valid approvals. Keep one active writer per run.

Accept a reference URL or existing artwork, product name, and optional template listing. Default to the owner's “Your Seat Awaits” listing; resolve it in the connected shop and retain its exact ID. If ambiguous, ask which listing to use. Read-only discovery can proceed while a human gate is pending; dependent production stages must wait.

The agreed defaults are fixed **and** personalized designs, a 12-inch initial minimum test width, and template size/price options filtered to the approved range. Read the [production contract](../../references/decalflow-production-contract.md) before choosing sizes, authoring personalization, capturing exports, or resuming a changed design. Use [finished artwork sizing](../../references/artwork-sizing.md) for measurement technique. Automatic physical-cuttability detection remains unavailable.

## Wedding sample names and dates

For new wedding sign samples, rotate among these selected couples instead of inheriting names and dates from copied artwork or listing templates. Explicit user or customer wording takes precedence.

| Couple names | Sample wedding date |
|---|---|
| Sofia & Mateo | August 14, 2027 |
| Daniel & Ethan | November 6, 2027 |
| Elena & Luca | June 19, 2027 |
| Clara & Adrian | May 15, 2027 |
| Lucas & Gabriel | July 10, 2027 |

Choose one pair and date per product and record them in `launch.json`. Keep them consistent across design alternatives, personalization previews, and listing assets; pass them to the design and listing-assets skills. Adapt date formatting to the design while retaining the same date. When resuming, retain the recorded sample wording and existing approvals unless the user requests a change. Preserve original artwork and source references as review evidence; apply the selected sample wording to newly generated versions.

## Visual review briefs

For design verification in stage 1 and listing-image verification in stage 4, use `present-plan` to create a standalone HTML review brief. Read that skill and inline its `assets/plan-brief.css`, adapting its restrained, responsive, print-friendly layout to visual review. Use the product's production folder as the workspace and save numbered revisions in `plan-briefs/`, such as `0001-design-review.html` and `0002-listing-image-review.html`. Preserve earlier briefs as review history.

Lead with the visuals and the exact decision requested. Include the product/version, review status, relevant dimensions, agent verification results, unresolved defects, and changes since the prior review. Use comparison panels and concise captions; include tradeoffs only where a real choice remains. Embed review images or SVGs so the brief renders without external assets, preserve aspect ratios, and provide large views for detail inspection. Link retained source artifacts and final exports with paths that resolve from the brief.

For artwork briefs, include the [font access and licensing summary](../font-match/references/font-access.md): exact styles, access status, preview representation, purchase links and current costs, and coverage for the intended production workflow. Show unresolved access before visual approval; record visual acceptance separately from purchase authorization and production readiness.

Before requesting approval, check that embedded visuals match the artifacts under review, open and inspect the brief when possible, and verify readable screen and print layouts. Link the brief in the handoff and record its path and hash with the reviewed artifact identities in `launch.json`. Distinguish agent checks from pending user approval. The brief presents evidence; only the user's explicit decision satisfies the existing approval gate.

## 1. Review artwork and shipped Pieces together

### Compare and select a design

Default to a baseline plus three alternatives unless the user specifies another count or requests reconstruction only. For a reference URL, use `decal:recreate-listing-design` for the baseline and complete its [font-match checkpoint](../font-match/SKILL.md). Retain the WhatTheFont evidence, independent visual review, and any scoped substitute acceptance or Affinity fallback authorization in the run record. Scope the close-match requirement to the baseline; intentional alternative designs are not failed reconstructions. For existing artwork, preserve the original as the baseline and skip reconstruction. Reuse an already selected version when resuming; generate new alternatives when the user requests them without replacing the retained approval of the previous version.

Keep the product purpose and wording consistent unless the user requests copy changes. Offer two subtly differentiated alternatives through deliberate changes to typography, hierarchy, line breaks, spacing, or ornaments, plus one broader composition alternative. Each option needs a visible design difference, not only a color or size change. Label intentional font choices separately from unresolved font matches. Retain editable sources and rendered previews under stable option IDs and versions; assess obvious cut and personalization constraints without claiming physical qualification.

Use free, commercially usable fonts for all three alternatives by default, unless the user explicitly requests paid-font options. Prefer open-license fonts from their official foundry or repository, such as fonts distributed under the SIL Open Font License. “Free” means no font purchase fee, not absence of a license. Verify the exact files and terms for physical product sales and the intended personalization/rendering workflow; exclude personal-use-only, trial, and preview-only fonts. Retain the source URL, font files and hashes, license text, and relevant redistribution or modification requirements under the [font access procedure](../font-match/references/font-access.md).

Build alternatives from those usable fonts and deliberate layout choices. Do not reuse commercial-font specimen images or trace commercial glyphs to present an option as free-font artwork. Use each alternative's actual fonts for headings, script, names and dates; review its complete render and supported personalization examples independently. Report intentional differences from the baseline as design choices. A missing commercial font in the comparison baseline does not block designing or selecting a free-font alternative; keep the baseline provisional, and complete the selected alternative's visual, access, and production checks before packaging.

Present the baseline and alternatives in a visual review brief with the same sample wording, declared width basis and target, and background. Include the source reference separately, a large view of each option, and concise notes on what changed and likely production tradeoffs. For each option, show the exact font families/styles, license names, verified access status, and font purchase cost (zero when verified free); distinguish font cost from other production costs. Record available source ownership or license information and unresolved rights questions. Free-font licensing covers use of those fonts, not rights to the reference composition, wording, photographs, or other artwork. Small visual differences and user selection do not establish legal clearance; do not describe any option as legally safe or independently created merely because it differs from the reference. Keep third-party source photographs labeled as review references.

Ask the user to select an option, request revisions, or specify a combination. Save the exact selected option/version and decision in `launch.json`. Render a requested combination as a new version for review. Selection permits preparation of that design; it does not satisfy the final artwork/Piece approval below. Preserve the other options as review history and prepare only the selected design for production.

### Prepare and approve the selected design

Complete visual and vector preflight on the selected version. DecalFlow service failures do not replace or suspend unresolved lettering work. Use `decal:decalflow` to inspect the package contract and define Pieces through Cut Groups: a Piece is a shipped application unit, not every disconnected letter or SVG path. Account for every path, authored alignment, color, and shipped piece count.

For personalized designs, read [personalized designs](references/personalization.md). Build a supported template package with declared fields and fonts, not just outlined sample wording. Before approval, use authoring previews and a non-persisting package-import dry run. After approved registration, verify actual renderer output before physical qualification; any required artwork or field-contract change reopens design approval.

Present one design review brief: rendered artwork, side-by-side reference comparison when applicable, numbered Pieces, assembled installation layout, widest-Piece and assembled bounds, and personalization fields/examples with their fit rectangles, linked groups, tracking, and review limits. Identify the exact design package/version and summarize visual/vector preflight and package-import dry-run results. Record **user approval** of this exact artwork and Piece definition before registration and test preparation. Agent preflight alone does not satisfy this gate.

## 2. Register and determine test sizes

Use `decal:decalflow` to dry-run and import the approved versioned package and create or reuse its Product. Verify returned identity, measured bounds, Cut Groups, and field definitions. Keep pending physical qualification explicit; importing does not qualify a design.

Discover the installed CLI and read its `Calculated max design width` documentation. Prepare the exact design/fields at a valid reference width, wait for completion, then call `job size-limits PREPARATION_ID --json`. Retain the full result and limiting group IDs. Use the numeric result without rounding upward. An unavailable limit is a blocker, not zero or permission to estimate silently.

The existing calculation uses a 24-inch roll minus a **2-inch total** margin, independent 90-degree Cut Group rotation, and unlimited feed length. It excludes Weed Borders and production gaps and assumes alignment assemblies can be placed separately. Review the actual production arrangement with explicit material width, margins, borders, spacing, and rotation before choosing a maximum. Default to continuous roll feed: stack Pieces along the feed direction on one sheet when they fit across the usable width. Apply a feed-length limit only when the user specifies one or the installed device has a verified limit. If an export requires a finite sheet length, derive it from the arranged Pieces, gaps, and end margins; do not invent a cap or split the job merely to fit a default page length. Do not treat the geometric ceiling as an approved sale size or duplicate the calculation in this skill.

Start minimum testing at **12 inches**. If the feasible maximum is below 12 inches, present the conflict for a revised size or design; never silently invert the range. A failed minimum test can require a higher minimum or revised artwork. Retain distinct calculated, fit-verified, physically tested, and approved sale sizes.

## 3. Qualify physical production

Prepare retained minimum and maximum exports through DecalFlow and inspect the complete Piece arrangements for exact artwork, dimensions, count, material-width fit, margins, borders, gaps, and rotation. Apply the production contract's warning-acceptance gate through `decal:decalflow` before capture. Verify the minimum test’s exact-file import through `inkcut` or the acknowledged DecalFlow Inkcut bridge. Respect the active Inkcut job and serialize imports so the next test does not replace an uncompleted one. Keep the operator's cutter settings and results with each physical test.

Require the user to report **cutting, weeding, transfer, and application at the minimum size**. All four checks must pass. Record material information supplied, tested fields, file hash, actual width, each result, and the user's explicit approval. An import acknowledgment, render, or calculated fit does not replace this minimum physical test.

The maximum physical test is optional and skipped by default unless the user requests it. Digital verification of the maximum remains required: check the exact retained geometry and complete arrangement against the official size limit and actual material constraints. Record an untested maximum as **fit-verified; physical test skipped**, never physically passed. If the user elects to test it, verify its Inkcut import and collect the same four results. A reported failure must be resolved even though the test was optional.

After the minimum passes and the maximum passes digital fit verification, record the sale range and its mixed evidence basis; a skipped maximum physical test does not block listing assets or draft creation. Apply this coverage only to the approved design, fields, and arrangement. For personalized products, verify supported input extremes at offered sizes; fixed sample approval does not qualify an unresolved personalized template.

On failure, retain the result and propose a size or design correction. Recheck affected geometry and approvals under the run-state rules, then repeat affected checks. Do not advance to listing assets with unresolved failures or an unverified range.

## 4. Build and approve listing assets

Select the template's size/price options within the qualified range; retain their prices and currency. Check every offered option, including personalized inputs, against its production constraints. Ask for resolution if no options remain or a price/option cannot be mapped; do not invent prices or enlarge the approved range.

Use `decal:create-listing-assets`, with the approved artwork, piece count, color, and sale sizes. That skill owns template graphics, the required applicable couple selfie, and contextual staging. Generate blank photographic scenes and composite exact artwork through Affinity MCP. Verify product-specific size claims against the production contract. Preserve approved generic measurement examples as examples, not sale options. This launch workflow supplies the expanded intake for sizes and personalization; change product-specific copy that would otherwise misstate the approved product, retain unrelated template copy, and include those edits in image approval.

Present a listing-image review brief with the ordered contact sheet, a large preview of each final export, and its upload position, filename, dimensions, and hash. Include product-specific copy edits and verification of artwork fidelity, Piece count, colors, size claims, and personalization examples against the approved product. Record **user approval** of the exact image hashes and order before uploading.

## 5. Create and verify the Etsy draft

Read [Etsy draft handoff](references/etsy-draft.md). Use the Etsy MCP to adapt the template, create the draft, upload the approved assets, set inventory and personalization, and read back the saved resources. Never copy the template's active state. Link the exact new listing ID, options, and fields to the DecalFlow Product and verify the mapping.

Completion requires the design/Piece approval, minimum physical approval, maximum digital fit verification (and resolution of any elected maximum test failures), image approval, verified remote draft content and inventory, and verified DecalFlow mapping. Return the draft ID/link when available, product folder, approval evidence, and any remaining limitations. Leave the listing in draft; a blocked or partial draft is not a completed launch.
