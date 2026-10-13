# Vector construction and production

Use these mechanics when producing sign or decal vectors. Adapt to the available editor or code stack; the visual reference determines the design.

## Editable source

Apply [finished artwork sizing](../../../references/artwork-sizing.md) for the size reference, geometry measurement, uniform scaling and final dimension checks.

- Specify physical `width` and `height` in inches or millimeters plus a consistent `viewBox`. A scale such as 100 viewBox units per inch makes measurements easy; it is not a required SVG convention.
- Use `title`, `desc`, semantic group IDs, relative local font declarations, and separate text elements for personalization. Preserve the requested XML structure where practical.
- Set actual font weight, tracking, and OpenType features. Use lining numerals when the reference date uses equal-height digits; some serif fonts default to oldstyle numerals.
- Prefer natural font proportions and spacing. If `textLength`, `lengthAdjust`, or transforms are necessary to fit the photographed reference, reproduce the same adjustments in the outlined export. Avoid changing glyph proportions merely to fill a convenient box.
- Keep the background transparent unless the user requests a printed background. Mirror frames, flowers, and guest cards in a listing photograph are context unless explicitly included in the requested artwork.

## Shape text accurately

An editor's convert-to-curves operation is suitable. A working programmatic stack is FontTools + HarfBuzz for outlines, Shapely for custom script unions, resvg-py for raster previews, and svglib + ReportLab for vector PDFs.

In code:

1. Load the intended font and instantiate variable axes at the selected values. Shape the complete string with HarfBuzz using the intended kerning, ligature, and numeral features.
2. Use shaped glyph IDs, advances, and offsets. Reading the character map alone loses shaping and can break script joins.
3. Draw each glyph through a FontTools `SVGPathPen` and `TransformPen`. Scale from font units to SVG units, invert the font's upward Y axis, and position the baseline explicitly.
4. Apply the same tracking, centering, width adjustment, and features as the editable text. Render both versions to check consistency; matching outer bounds alone does not prove matching glyphs.

## Custom script curves

Start with the reference's letter skeleton: slant, baseline rhythm, x-height, loops, and entry/exit strokes. Build smooth cubic Bézier paths; adjust words as connected lettering, not isolated generic glyphs. Preserve intentional gaps and dots.

For monoline script, sample curves with a tolerance small relative to the final physical stroke width, then buffer the centerlines with round joins and caps. For visible stroke contrast, use variable-width outlines or explicit contours. State when a uniform-weight reconstruction only approximates the reference's pressure variation.

Expand strokes and union intersecting shapes in the production copy. Shapely `buffer` and `unary_union`, or equivalent vector-editor operations, can do this. Preserve holes/counters and export consistent contour winding or an explicit compatible fill rule. Overlapping outlines can create double cuts even when a PNG looks correct.

Inspect joins at large scale. Remove unintended disconnected swashes, kinks, filled counters, slivers, and duplicate contours. Detached dots and deliberate flourishes are valid; do not connect them solely to reduce the path count.

## Export and preflight

With resvg-py, pass a positive explicit DPI, such as `dpi=96`, when rendering an SVG whose dimensions use inches. In the tested environment, leaving DPI at its zero default caused “SVG has an invalid size.”

resvg-py provides previews without a system Cairo installation. If CairoSVG cannot find libcairo, use an available renderer rather than repeatedly reinstalling its Python wrapper. svglib/ReportLab can export outlined SVGs to vector PDF; verify the resulting page dimensions. These are ordinary vector PDFs unless a separate PDF/X workflow is performed.

Check every final design:

- XML parses and all editable font references resolve. If the editor ignores `@font-face`, explain how to install the bundled font.
- Production lettering is filled vector geometry with no live text, external font dependence, linked images, or unintended raster content.
- Cut contours close, script overlaps are unioned, and counters remain open. Path count alone does not prove these conditions.
- Rendered artwork lies inside the artboard with the intended margins. Check clipping and line collisions visually as well as through bounds.
- Verify artwork geometry independently from SVG viewport and PDF page dimensions. At 72 points per inch, 24-inch lettering spans 1728 points; the PDF page may be wider to include margins. Apply the shared sizing procedure to both exports.
- Record useful physical measurements, such as smallest visible text height and nominal script/rule thickness. Do not call these a measured minimum stroke width: serif tips, tapers, and counters can be finer.
- Inspect the actual final PNG or rendered SVG after the last change, including text legibility at the intended scale. Rerun relevant checks after corrections.

Preview PNGs are not automatically full-size print rasters. Deliver vector PDF/SVG for scaling, and label review images accordingly. Use material color to obtain white vinyl from black cut geometry. Print at actual size; keep no-bleed inset lettering distinct from an edge-to-edge print design that needs bleed.

State whether physical cutting or printing was performed. Digital preflight establishes file properties, not successful weeding or transfer on an unspecified machine and material.
