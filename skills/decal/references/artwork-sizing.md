# Finished artwork sizing

Before sizing a DecalFlow design or making listing claims from its output, read
[the production contract](decalflow-production-contract.md#width-and-geometry).
For standalone artwork, retain and label the requested element or assembled
reference. Resolve the measurement basis before scaling.

Artboard, SVG viewport, PDF page, transparent margins, mirror dimensions,
transfer tape and weed borders are separate measurements. None establishes
artwork width.

## Measure and scale

1. Measure intended contour bounds after transforms, font shaping and actual
   stroke expansion. Measure authored groups and their assembled union. Exclude
   hidden objects, guides, registration marks, generated weed borders and
   display-only cut-path strokes. Use vector extrema or verified geometry
   bounds, not text advances, control-point bounds or raster pixel counting.
2. Convert to physical units using the SVG viewport/viewBox mapping or editor
   units. Use 25.4 mm per inch; retain calculation precision.
3. For standalone sizing, scale uniformly by target / measured reference
   dimension. Fit the page around artwork plus explicit margins without
   shrinking it. For DecalFlow, use the contract's fitting and sizing sequence.
4. Re-measure exported geometry after the final edit. Keep digital verification
   distinct from physical cut evidence. Preserve original sources and exports.

A 24-inch artboard containing one 22-inch lettering Piece does not satisfy a
24-inch artwork target. Scale the artwork by 24 / 22; changing page metadata is
not a size correction.

Record measured group IDs, method, requested dimension/basis/units, group and
assembled bounds, page dimensions, and scale. If no target was requested,
report supplied measurements without inventing one. Unverifiable bounds remain
unverified; page metadata is not geometry evidence.
