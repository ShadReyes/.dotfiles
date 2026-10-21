---
name: recreate-listing-design
description: Reconstruct lettering from Etsy or other product listing references as editable and production-ready SVGs. Use for closely matching sign, decal, or typography layouts from listing URLs or photos, including batches handled by design specialists. Not for duplicating shop listings, publishing products, or general website recreation.
---

# Recreate listing design

Deliver a close visual reconstruction of the requested lettering, with editable sources, outlined production files, and an honest reference comparison. Preserve the user's requested degree of fidelity. Treat a request to match or duplicate a reference as reconstruction, not permission to replace its typography with a new design.

## Establish the reference

- Open the supplied listings and inspect their actual images. Titles and image descriptions do not establish the layout or font shapes. Save the selected reference image and its listing URL for review.
- Identify which image or variant is the target. Use the cover image unless context specifies another. Ask only when competing variants would materially change the result; continue independent work while waiting.
- Record the visible wording, case, line breaks, hierarchy, occupied widths, baseline spacing, tracking, script flourishes, and rules. Measure ratios against the artwork width; separate perspective distortion from intentional letter shapes. Normalize a photographed design onto a flat artboard rather than reproducing the camera angle.
- Use supplied names and dates. Otherwise retain the reference's sample wording for a direct comparison and label it as sample personalization.
- If the user supplies an existing folder as a structural example, inspect its folder and SVG organization separately from visual references. Follow any restriction against taking design inspiration from that folder. Preserve originals in a separate output location.

For competitor research or customer-facing listing previews, read [shared Etsy guidance](../../references/etsy-listing-guidance.md). Use its evidence rules for comparisons and its image guidance only for listing previews. Preserve reference fidelity and physical vector sizing; a thumbnail crop must not change the reconstructed lettering. Review previews do not become Etsy-ready listing images automatically.

## Assign design ownership

Use [decal:font-match](../font-match/SKILL.md) for every reference reconstruction. It owns the researcher/designer/independent-reviewer flow, WhatTheFont evidence, visual acceptance, and approval-required Affinity fallback. Complete its checkpoint before production packaging. Preserve explicit user topology and use Herdr workers when Herdr orchestration is requested.

For multiple independent references, assign one design owner per reference and queue font research and review within available capacity. Each owner has a unique output prefix. The lead owns integration and packaging; workers must preserve each other's files. Supply the selected image, exact wording, fidelity priority, requested size, folder conventions, and any confirmed font evidence.

## Resolve lettering before polishing

Follow the font-match workflow before selecting substitutes or drawing custom lettering. An unavailable font can leave independent layout work available, but cannot pass the typography checkpoint. Keep purchased fonts out of redistributed packages unless their terms permit inclusion; include permitted fonts and licenses.

Match the reference's weight. If easier cutting requires thicker strokes, supply a separately labeled variant for review and preserve the reference-match version. Retain the font-match evidence outside the production package and link it in the design review.

Include the font-match [access and licensing summary](../font-match/references/font-access.md) beside the visual comparison before requesting design approval. Identify purchased versus missing fonts and preview-only lettering; retain visual approval separately from production readiness.

## Build and review

Read [finished artwork sizing](../../references/artwork-sizing.md) before choosing physical dimensions: requested decal size refers to visible artwork. Read [references/vector-production.md](references/vector-production.md) when constructing or exporting the SVGs for shaping, script outlines and preflight.

Maintain the user's requested folder convention. Otherwise use:

```text
<project>-editable-cutter/
  01-design.svg
  fonts/
<project>-production/
  01-design-outlined.svg
  01-design-print.pdf
  01-design-preview.png
  01-notes.txt
<project>-review/
  reference-comparison.html
  validation.json
```

The lead reviews actual renders against each reference. Correct the largest visible mismatch first: layout and wording, then font/letter shapes, weight, proportions, and spacing. Return concrete corrections to the owning specialist. A valid SVG or a specialist's completion message is not evidence of visual fidelity.

Create a side-by-side comparison containing the source photo, listing link, and rebuilt vector artwork. Make the lettering large enough to assess; include a detail view if the full product photo makes the letters too small. White-on-dark and black-on-light previews help assess mirror decals. Keep source photographs clearly labeled as review references, separate from customer listing assets.

Completion requires all requested designs, visually inspected final renders, a passed font-match checkpoint, resolved conspicuous mismatches or an explicitly user-approved change in fidelity scope, and production preflight after the last edit. State what remains approximate rather than assigning an invented similarity score.

## Deliver

When the requested delivery includes DecalFlow registration or production
automation, use `decal:decalflow` after visual and vector review. Emit its versioned
design package beside the production deliverables, retaining the outlined source
hash, measured artwork bounds, object IDs and authored Cut Group alignment. A
personalized template requires supported live-text bindings and exact fonts;
outlined sample wording remains a fixed design. Record the package and returned
application identities in the design delivery manifest. Artwork reconstruction
alone does not authorize listing publication or cutting.

Package the editable SVGs and allowed fonts, outlined SVGs, vector PDFs, previews, comparison, and concise production notes. Exclude discarded font candidates and temporary specimens. Check the archive opens and includes each design.

Notes must distinguish live text from node-editable curves, sample personalization from customer data, and artboard size from artwork bounds. Explain that editing the source does not update the existing outlined SVG/PDF automatically. Report digital validation separately from physical print/cut testing. Link the comparison and complete package in the final response.
