---
name: font-match
description: Match decal reference lettering through WhatTheFont research, exact-text specimens, and independent visual review. Use before reconstructing reference typography or when a decal font match is disputed. Affinity custom lettering is an approval-required fallback.
---

# Match reference lettering

Resolve typography before production packaging. Use WhatTheFont as the font-identification service. Use Affinity for custom lettering only after the user approves that fallback for the specified elements. This approval is separate from approval of the resulting artwork.

## Assign work

This skill calls for a font researcher, reconstruction designer, and independent visual reviewer. Delegate these roles when agents are available; queue them within available capacity. The researcher hands off evidence before the designer selects fonts, and the reviewer inspects rendered output before packaging. For a small task the lead can design, but use a separate reviewer. If delegation is unavailable, perform separate passes and report that independent review was unavailable.

When Herdr orchestration is requested, use `herdr-orchestrator` and `herdr:herdr` for visible workers, caller validation, permissions, and monitoring. Otherwise use the available agent system. Preserve any explicit user topology; report a missing review role instead of silently changing that topology.

Give each worker the source image and URL, exact target wording, fidelity requirement, output directory, and ownership boundaries. Tell workers that others share the workspace and their edits must be preserved. Research owns crops and candidate evidence; design owns specimens and artwork; review owns findings. The lead alone integrates results and updates the launch record. The lead must inspect the comparisons, not accept worker completion as proof of fidelity.

## Research each lettering style

1. Retain the highest-resolution useful source images available. Create separate crops for headings, flourishes, small signatures, names, and dates. Do not assume these use the same font. Record exact case and punctuation. Two-letter samples need corroboration from other text or remain uncertain.
2. Correct camera perspective and rotation while preserving intended glyph proportions. Retain original and normalized crops. Use contrast cleanup that preserves strokes; generative enhancement cannot supply evidence for missing letter details.
3. Open [WhatTheFont](https://www.myfonts.com/pages/whatthefont) in an available browser automation tool and submit each unknown style separately. Discover supported browser controls; do not invent an API. Save the submitted crop, returned candidates, result capture, and source links. A search snippet or a guessed family name is not a completed identification attempt.
4. Search commercial as well as free candidates. Check promising families at their primary foundry or vendor and inspect weights, alternates, and flourishes. Retain exact-word previews when font files are not available. Present any purchase or licensed-font requirement; do not silently replace a strong commercial candidate with an installed font.
5. If upload or results are inaccessible, retain the failure and prepared crops. Continue independent research or layout work, but report identification as blocked. Do not switch to another identification service or custom lettering without the user's direction.

## Identify font access before visual approval

For every shortlisted font, follow [font access and licensing](references/font-access.md). Show exact styles, acquisition status, preview representation, current purchase links/costs, and intended-use coverage in the first candidate review and each approval brief. Keep visual acceptance separate from license acquisition and production readiness.

## Render and compare

Render the strongest candidates with the exact reference words, case, punctuation, and date. Include the reference crop beside every candidate, matched by visible letter height, with aspect ratios preserved. Add transparent overlays and enlarged details for distinguishing characters. Record any alignment or perspective transform used in an overlay.

Compare glyph shapes, stroke weight and contrast, slant, proportions, loops, terminals, joins, alternates, baseline, and spacing. Adjust tracking and layout separately from font selection. Do not distort a poor candidate to fit the reference's overall width. Test OpenType alternatives using a renderer that supports them and retain the selected settings. Compare the final production renderer's output before accepting those settings for personalized text.

For names and dates, test representative short, long, wide, accented, and punctuated inputs supported by the proposed field contract. Fixed sample curves do not provide arbitrary personalization. Resolve overflow through an explicit supported layout/input rule and review its visual effect.

## Review and acceptance

The independent reviewer opens source crops and actual rendered comparisons. Return findings per element with the differing glyph or property and the next correction. The designer revises and the reviewer rechecks affected elements. The lead inspects the final comparison too.

Record each element as `confirmed`, `close substitute`, `custom lettering`, or `unresolved`:

- `confirmed`: font identity has retained source evidence and its rendered glyphs agree with the reference. A top WhatTheFont result alone is insufficient.
- `close substitute`: a comparison demonstrates a close visual match; record residual differences and obtain explicit user acceptance of the substitution before packaging.
- `custom lettering`: the user authorized the Affinity fallback, and the resulting curves have passed visual review. Describe them as node-editable, not as the original font.
- `unresolved`: conspicuous differences, inadequate source detail, unavailable font evidence, or failed review remain. Disclosure alone does not pass this state.

Once promising candidates have been compared and corrected, present any remaining mismatch with the best alternatives. Ask whether the user accepts a specified substitute, can supply the identified font, or authorizes Affinity reconstruction of specified fixed elements. Do not repeat an unchanged search indefinitely or start custom lettering before that decision. Quote and link this approval rule when requesting fallback approval.

After fallback approval, load `affinity`, reconstruct only the approved elements, and repeat visual review. Keep personalized fields backed by usable fonts unless the user explicitly changes the product to fixed wording. Approval to attempt reconstruction does not approve its output.

When extending, joining, or repairing a lettering stroke, follow [lettering joins](references/lettering-joins.md) before presenting the revision. Review the attachment separately from the overall contour. A contour pass does not pass a join; a visible lip, gap, or width step keeps the attachment unresolved.

## Retain the handoff

Save `font-match.json` in the product's review folder. Include source/crop paths and hashes; wording per element; WhatTheFont attempts and evidence; candidate family/style/source; font file hashes and usage/redistribution terms when available; renderer and feature settings; comparison paths and hashes; reviewer findings and resolutions; per-element status; and exact user decisions with their scope and time. Retain rejected candidate evidence in the review folder, outside the production package.

The handoff passes only when every element has resolved visual review, any substitute acceptance and fallback authorization are recorded, and no conspicuous mismatch remains. A user-approved departure from reference fidelity must be recorded explicitly as changed scope. Link this record from `launch.json` when present. Changes to the reference, font, features, or lettering reopen affected review. This checkpoint permits packaging; it does not replace design/Piece approval, renderer verification, or physical qualification.
