# Extend and verify lettering joins

Use this procedure for an authorized flourish, terminal extension, or stroke repair. Preserve the approved letter bodies and source evidence. The objective is a continuous silhouette and cut contour, not merely overlapping shapes that look connected at normal size.

## 1. Establish the representation

- Prefer licensed font outlines or existing editable vector lettering. Retain an untouched copy and identify the exact attachment region.
- A raster specimen can support a provisional visual study. Record its native resolution, scale and renderer. Render it with enough source pixels for the largest intended inspection view; enlarging a small bitmap cannot establish edge quality.
- Label raster/vector composites as provisional. They cannot establish a welded vector join or pass production verification. Do not trace unrelated lettering or extract vendor font software to bypass missing licensed outlines.
- Treat a reported bump as a reopened attachment defect. Inspect it before attributing it to antialiasing. Acknowledging a defect does not resolve it.

## 2. Measure before drawing

Retain a tight attachment crop with document coordinates and visible letter height. Identify the incoming upper and lower boundaries, local stroke width, direction and change in curvature. Use a stable span of the existing exit, not a single noisy pixel or the extreme terminal tip.

Read the live document's DPI, spread bounds and transforms after import. Map reference-image coordinates into those native units explicitly; an SVG viewBox or export size does not establish native coordinates. Assert that the mapped attachment lies on the intended stroke before editing. Recheck the whole-word render and attachment location before measuring a crop, so an unchanged raster exit cannot be mistaken for the new geometry.

For raster context, sample both edge positions over several adjacent cross-sections. State the threshold, pixel-center convention, transforms and uncertainty. Check several opacity thresholds to distinguish a position error from an edge-profile difference. These are preview measurements, not exact font geometry.

For vectors, read the endpoint and control-point coordinates. For a cubic Bézier with points P0, P1, P2, P3, the endpoint tangents are proportional to P1−P0 and P3−P2. Compare both sides of the stroke, not just its centerline. Check the direction of traversal before comparing tangents.

## 3. Construct the transition in Affinity

1. Keep the contour fixed outside the authorized repair region.
2. Choose an attachment where direction and width are stable. Replace the obsolete exit segment; avoid a hard crop across a thick turn.
3. Match position, tangent direction and stroke width on both boundaries. Adjust handle lengths so curvature changes gradually through the transition. Collinear handles alone do not establish smooth curvature or consistent width.
4. For final vector lettering, make the intended silhouette continuous. Join or union overlapping geometry as appropriate, remove internal seams and redundant nodes, and inspect the result. A union can leave a cusp; it is not an automatic pass.
5. Confirm the intended component count and closed cut contours. Remove duplicate edges, unintended holes, slivers and self-intersections. Preserve legitimate counters and disconnected design elements.

Use the actual renderer and export path for inspection. Do not conceal an attachment defect with blur, feathering, lossy export, a changed display scale or a background chosen to hide the edge. Retain earlier revisions for comparison.

## 4. Run two separate checks

**Geometry check:** For each repaired boundary, retain endpoint separation, tangent-angle difference, local width before/at/after the join, and the relevant node/control coordinates. Express tolerances in document units and relative to letter height or local stroke width; choose them before acceptance. Inspect curvature through the transition as well as at its endpoints. Verify the topology of the exported cut contour. Report unavailable measurements as unverified, not passed.

**Render check:** Export the actual revision with enough resolution for 100%, 400% and 800% inspection. Define 100% against a stated reference or output size. Distinguish nearest-neighbor pixel enlargement from a fresh high-resolution render; label the source/export resolution and prevent browser auto-fit from silently changing the declared scale. Make matched before/after crops on light and dark backgrounds, with identical scale, alignment and crop bounds. Render both polarities through the intended path; an inverted screenshot is only a diagnostic. Include the full word and source overlay. Use lossless images; do not smooth the comparison crop after export. If a raster source cannot support a magnification, label that limit and keep the vector-join check pending.

Inspect both edges for a gap, lip, doubled edge, cusp, flat spot, local bulge, sudden width change or abrupt change in direction. Examine the attachment separately from the crest, sweep and endpoint. A good full-word silhouette cannot override a failed attachment crop.

## 5. Independent acceptance and handoff

The independent reviewer opens the actual exports, matched crops and geometry evidence. Return separate verdicts for:

- Overall contour and source fidelity.
- Attachment appearance at each declared scale and polarity.
- Vector continuity/topology, or explicitly unverified raster context.

Any observed attachment defect requires correction and re-review. Do not pass a residual lip as an acceptable raster/vector limitation. A clean provisional preview may pass its stated visual scope while production continuity remains unverified; keep those statuses separate. User feedback reopens the affected verdict.

Record the revision and artifact hashes, representation, source/render resolution, join coordinates, transforms, measurements and tolerances, contact-sheet paths, reviewer findings, corrections and outstanding checks in the product review record. Present and automatically open the revised HTML brief through `present-plan`.

Production acceptance requires both the geometry and render checks on the same final vector revision. Physical cut qualification and user artwork approval remain separate gates.
