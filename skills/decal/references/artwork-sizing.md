# Finished artwork sizing

For The Decal Company, a requested decal width means the finished visible
artwork width. For lettering-only designs, measure the lettering, including
its dots, punctuation and flourishes. Include other supplied design elements
when they form part of the decal. An explicitly requested measurement of a
particular element takes precedence; record that element as the size reference.

Artboard, SVG viewport, PDF page, transparent margins, mirror dimensions,
transfer tape and weed borders are separate measurements. None establishes
the finished artwork width. A size-guide example is not an available sale size.

## Measure and scale

1. Measure the union of the intended artwork contours in assembled design
   alignment, after applying transforms and resolving fonts or expanding
   actual artwork strokes. Exclude hidden objects, guides, registration marks,
   generated weed borders and display-only cut-path stroke widths. Use vector
   extrema or an editor's verified geometry bounds, not SVG metadata, text
   advance widths, path control-point bounds or raster pixel counting.
2. Convert those bounds to physical units using the SVG viewport/viewBox mapping
   or the editor's document units. Use 25.4 mm per inch. Keep full precision
   during geometry operations; round only displayed measurements.
3. Scale the entire design uniformly by `target width / measured artwork width`.
   Preserve lettering proportions and authored alignment. Set the page to fit
   the resulting artwork plus any explicit margin; adding a margin must not
   shrink the artwork. For a requested height, use the corresponding height ratio.
4. Re-measure the exported SVG and PDF geometry in physical units after the
   final edit. Verify the requested dimension against the project's agreed
   tolerance. Record digital verification separately from physical cut evidence.

A 24-inch artboard containing 22-inch lettering does not satisfy a request for
24-inch lettering. Scale the artwork by `24 / 22`, then fit the artboard around
it. Merely relabeling the page or stripping margins without correcting the
physical transform does not establish the requested size.

For several shipped pieces, measure their combined bounds in the intended
assembled alignment. Record individual piece dimensions separately. Nesting
or ungrouping for cutting does not redefine the sold design width. Path count
does not establish the number of shipped pieces.

## Apply in each workflow

- **Vector production:** set the requested artwork size in new production
  copies and verify SVG/PDF geometry. Preserve original sources and previously
  retained exports; changes to existing production artwork require a separate
  revision and the applicable qualification checks.
- **Listing graphics:** fit supplied artwork by these visible bounds while
  preserving proportions. Keep source production geometry unchanged. Retain
  approved template examples and distinguish mirror arrows from decal-width
  arrows. Flag a measurement label that conflicts with measured artwork;
  correct only working copies within the user's authorized scope.

In the production notes or listing manifest, record the measured object/group
IDs, measurement method, requested dimension and units, measured artwork bounds,
artboard dimensions, and applied uniform scale. If no production size was
requested, record the supplied file's measured size without inventing a target.
If bounds cannot be verified, mark sizing unverified rather than treating page
dimensions or an SVG description as evidence.
