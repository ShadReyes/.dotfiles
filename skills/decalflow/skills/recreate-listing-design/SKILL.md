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

For multiple independent references, use one specialist agent per design when delegation is available. This skill explicitly calls for that delegation. Limit concurrency to available slots and queue additional designs. For one reference, work directly and perform the same review steps; use a separate reviewer when it would resolve a difficult match.

Each specialist owns a unique filename prefix, its font assets, and its production exports. State that other agents share the workspace and that their files must be preserved. Keep integration, comparison, and packaging with the lead agent. If delegation is unavailable, perform these roles sequentially.

Give each specialist:

- The exact listing URL and selected image path, with instructions to view the image.
- Confirmed font evidence and unresolved identities, without presenting guesses as facts.
- The fidelity priority, required wording, requested size, and folder/XML conventions.
- Ownership boundaries and available vector/export tools.
- A requirement to render and inspect its output, disclose remaining differences, and return editable SVG, outlined SVG, vector PDF, preview, and brief notes.

## Resolve lettering before polishing

Use the confirmed font when accessible with suitable usage rights. Check the seller's font statement and primary font sources; a visually similar family is still an approximation. Include redistributable fonts and their licenses in the editable package. Keep purchased fonts out of redistributed packages unless their terms permit inclusion.

Compare candidates using the actual target word or phrase. Judge slant, x-height, stroke contrast, loops, descenders, terminals, and joins—not the broad label “script” or “serif.” Review a small useful set and reject visibly poor matches.

When a font substitute materially changes the appearance, construct custom Bézier lettering that follows the reference. This was the decisive improvement over generic script substitutions. Keep names, dates, and other suitable wording as live text. Explain that custom script is node-editable artwork, not a font that supports arbitrary retyping. If the user requires all wording to remain keyboard-editable, resolve that conflict before replacing text with curves.

An unavailable exact font is not a reason to stop all work. Continue the layout and other designs, and ask for a licensed local font path when it would improve the result. Disclose the fallback. Do not describe custom lettering as the original font or silently claim an exact match.

Match the reference's weight first. If the user also wants easier cutting, identify the tradeoff and, when useful, supply a separately labeled thicker variant. Preserve the approved reference-match version. Large bold generic lettering is not a substitute for fine handwritten lettering in a close-match task.

## Build and review

Read [references/vector-production.md](references/vector-production.md) when constructing or exporting the SVGs. It covers text shaping, script outlines, physical sizing, and preflight.

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

Completion requires all requested designs, visually inspected final renders, resolved conspicuous mismatches or explicit limitations, and production preflight after the last edit. State what remains approximate rather than assigning an invented similarity score.

## Deliver

Package the editable SVGs and allowed fonts, outlined SVGs, vector PDFs, previews, comparison, and concise production notes. Exclude discarded font candidates and temporary specimens. Check the archive opens and includes each design.

Notes must distinguish live text from node-editable curves, sample personalization from customer data, and artboard size from artwork bounds. Explain that editing the source does not update the existing outlined SVG/PDF automatically. Report digital validation separately from physical print/cut testing. Link the comparison and complete package in the final response.
