---
name: fontforge
description: Create or refine custom decal lettering with FontForge, retaining editable curves, SVG outlines, and optional generated fonts. Use for original wordmarks, glyph construction, stroke expansion, or font export repairs; use font-match for identifying existing reference fonts.
---

# Construct lettering with FontForge

Create editable native curves and verify the actual exported artwork. This skill supplies construction and validation methods; wording, letter shapes, weight, proportions, ornament, variant count and layout come from the current brief.

## Establish the output contract

Distinguish fixed lettering, a whole-word font glyph, and a reusable alphabet. A private-use whole-word glyph does not support arbitrary personalization or an ordinary typed ligature. An alphabet needs additional coverage, spacing, shaping and supported-input tests beyond this lettering workflow.

Inspect the current artwork and its actual curves before editing. Record the authorized elements, source provenance, intended output formats and layout invariants. Original drawing, imported licensed glyphs and traced outlines need distinct provenance records; exporting a font does not change source rights.

Discover the installed FontForge executable and execute a Python capability probe. Record application, embedded Python and relevant library versions. CLI scripting and a desktop GUI are separate capabilities; available Spiro support does not mean Spiro constructed the artwork. Follow existing installation authorization if a required tool is missing.

## Construct and iterate

Read [native construction and export](references/construction.md) before building or changing the generator.

- Retain the original controls and define the drawing-to-font transform explicitly.
- Use native cubic contours or a centerline with native stroke expansion as appropriate. Keep the editable construction source as well as expanded contours.
- Inspect first renders before producing a large artifact set. Correct letter legibility and intended structure before detailed export checks.
- Save each review candidate in a new version directory. A correction after review starts creates a new candidate; preserve previous evidence.
- When replacing one element in an existing composition, reuse the surrounding tree and verify it remains unchanged. Apply the brief's placement rule to visible curve bounds with uniform scaling unless another transform is explicitly intended.

Keep visual refinement separate from numerical repair. A topology pass cannot establish lettering quality, and an attractive raster cannot establish valid saved-font geometry.

## Validate the frozen candidate

Read [validation and repeatability](references/validation.md) before final review, font-export troubleshooting, or a reproducibility claim.

Inspect the final full word and layout, actual local connection renders at 100%, 400% and 800% in light/dark polarity, and actual saved-font renders when a font is delivered. Check incoming and outgoing connections on both contour boundaries. Crop the whole relevant turn or loop; an exit-only crop can miss an incoming shoulder.

Use an independent reviewer when the requested workflow includes one. Otherwise report the review as self-review. Keep numerical findings, visible defects, intentional corners and aesthetic reservations separate. Correct observed defects within scope; do not convert an unresolved defect into a pass by listing it as a limitation.

## Deliver and record

Retain a local workflow with exact commands, versions, parameters, coordinate units, original controls, native masters, exported outlines, generated fonts when requested, render evidence and review findings. The manifest should identify each candidate's version, readable name, paths, visible bounds, transforms, source/artifact hashes, provenance, reproduction command, validation scope and remaining limitations.

Freeze reviewed artwork and its hash record. Later status integration can live in a separate handoff record. If a report contains an incorrect claim, preserve the evidence and add an explicit correction that supersedes the field; current summaries must use the corrected result.

Present an actual visual comparison before production packaging. In an existing decal launch, link the results from its launch record and preserve prior decisions. Separate technical review, user artwork approval, font functionality and physical cut qualification. This skill supplies neither production approval nor authority to publish a listing.
