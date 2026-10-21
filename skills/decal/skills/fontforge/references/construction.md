# Native construction and export

## Environment and units

Run a small probe through the installed FontForge executable, using its current CLI help to select Python scripting. Probe `fontforge.version()`, the embedded Python version, and any optional capability the task needs. Keep native-generation dependencies separate from the inspection environment: the embedded interpreter may differ from the shell's Python.

Record drawing units, font units, UPM, ascent/descent, advance width, codepoint mapping, and the full coordinate transform, including any y-axis inversion. Select these for the task; no prior project's dimensions or nib values are defaults. Record the renderer and its pixel-to-design-unit mapping so “100%” has a reproducible meaning.

## Construction stages

For a centerline approach, author original cubic controls and draw them through `glyphPen`. End an open construction path as open; close filled contours explicitly. Release the pen before subsequent glyph operations. Preserve these stages when they help diagnose the output:

1. Original controls and native centerline master.
2. Native expanded stroke before cleanup.
3. Cleaned native contour master.
4. Pre/post numerical-repair masters, if a repair is required.
5. Final native source and exported artifacts.

Native elliptical stroke expansion can encode contrast without polygon-buffer construction. Record nib dimensions, angle units, caps, joins, accuracy target and overlap options. Choose cleanup order deliberately; retain evidence around overlap removal, direction correction, simplification and extrema insertion. Accuracy/simplification settings are requested tolerances, not measured global bounds. Recheck counters and both sides of connections after cleanup.

Direct closed-contour drawing is also valid. Use Spiro only when it fits the task and is actually executed; label the parameterization and expansion engine separately. A different centerline representation using the same expansion engine is not a second vector application.

Align handles at intended smooth centerline joins, then inspect the expanded boundaries. A smooth centerline can produce a sharp inner offset at a narrow turn. Classify that corner from the intended letter structure and rendered appearance, not just its tangent angle.

## Curve-preserving export

Save the native SFD and generate the requested font through FontForge. For SVG, preserve native move/line/cubic/close commands and explicitly record transforms and decimal precision. Avoid replacing native curves with sampled polygons merely to serialize them.

A local FontForge 20251009 experiment found that `glyph.export` on an open construction curve invalidated the glyph handle. This is a build-specific observation, not a universal API claim. If export fails, retain a minimal reproducer and use the tested `glyph.draw(pen)` route: serialize native pen commands directly, implement contour closure correctly, and explicitly handle or reject components. Reopen and compare the result. Distinguish this serializer from a glyph reconstruction engine.

Decode a saved OTF's actual CFF commands for comparison; do not substitute the in-memory glyph or another installed font. Use a font renderer against the saved file as separate visual evidence. Cubic CFF and quadratic TrueType exports require different conversion checks; a successful CFF test does not validate a TrueType conversion.

## Conditional native-grid correction

Use coordinate quantization only when a measured export problem justifies it. In the tested build, a microscopic CFF closing-edge discrepancy was resolved by native `glyph.round(1024)` before saving and generating. That factor was one successful experiment, not a required grid for every design.

Retain pre-grid geometry and compare every corresponding on-curve and control point after the operation. Native rounding can move handles along with on-curve points: observed control-point displacement exceeded a nominal half-grid bound. Report measured per-axis and geometric changes, point correspondence, and any topology/count changes; do not assert a bound from grid spacing alone.

SFD decimal serialization can perturb binary grid coordinates when reopened. Check actual final CFF closure directly. Quantization is an artwork change and must run identically during reproduction; it is never a verifier-side snap or metadata normalization.

## API authority

Consult the installed help and [official FontForge Python API](https://fontforge.org/docs/scripting/python/fontforge.html) for current signatures of glyphPen, stroke, draw, round, validation and generation. Reproduce local failures on the current build before carrying a workaround into a different environment. Retain warnings and exit status with outputs.
