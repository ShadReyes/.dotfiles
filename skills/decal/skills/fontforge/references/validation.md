# Validation and repeatability

## Inspect final appearance

Use freshly rendered final SVGs and, when delivered, the saved font itself. Compare candidates at equal visible letter height or another declared scale, preserving aspect ratio. Inspect the complete word and composition for legibility, spacing and collisions before close details.

Generate local connection crops at defined 1x/4x/8x scales in both polarities. Inspect both boundaries, incoming/outgoing segments, loop tops, lower turns and adjacent counters. Look for gaps, teeth, doubled seams, shoulders and abrupt width changes. A viewer that fits a large image to its window does not provide native-scale edge inspection. Split wide crops into unscaled tiles or use actual-size viewing; retain the framing and scale.

Keep ordinary smooth joins distinct from deliberate corners and crossings. A one-degree tangent-change threshold was useful as a diagnostic in the tested workflow, not as a universal acceptance rule. Declare the threshold appropriate to the task, retain raw measurements, and explain classifications. Tangent agreement alone does not establish curvature continuity or steady stroke width. Sample widths across both sides before/at/after a suspect join when necessary.

## Reopen and check actual exports

Reopen native masters and generated fonts. Record contour closure, point/segment counts, winding, counters, zero-length edges, bounding boxes and validation masks. Expected counters come from the intended construction, not a fixed number copied from another word. An open construction skeleton is different from an invalid open filled outline.

Interpret validation flags against the installed API. In the tested CFF workflow, `0x80000` reported nonintegral coordinates; a checked-state bit also appeared in `validation_state`. This alone did not establish a self-intersection. Preserve raw flags and warnings rather than claiming an error-free run.

If an overlap warning occurs, isolate which native operation emits it and compare saved/exported contours independently. Successful generation is not evidence that the warning was harmless. State the demonstrated scope and any unresolved concern.

Compare the SVG with commands decoded directly from the saved font. Check contour endpoints before invoking a polygon library. For sampled topology:

- Use stored segment endpoints exactly. Evaluate intermediate samples without duplicating the evaluated endpoint at the next segment start.
- Retain the sampling method, tolerances and coverage. Floating endpoint duplicates can produce false microscopic spikes in sampled polygons.
- Distinguish that sampling artifact from an actual closing-edge delta present in decoded font commands.
- Inspect a failure in the raw curves. Keep the verifier faithful to the artifact; snapping, buffering or repairing its samples can conceal the defect.
- Report sampled validity and sampled distance as sampled evidence, not analytic proof of no Bezier intersections or a universal error bound.

For composition replacement, compare the entire retained XML tree after excluding only the authorized element, including root/ancestor attributes and order. If serialization changes, use a documented structural comparison rather than assuming pixel similarity proves preservation. Derive placement from actual curve bounds under the transform.

## Fresh reproduction

Freeze generator sources and candidate hashes before handoff. Run into a new unused directory; generators should refuse to overwrite reviewed outputs. Record application/library versions and exact commands. Reproduce supplemental deliverables separately if they use a different generator.

Compare original bytes first. If differences remain, classify them explicitly:

| Artifact | Required distinction |
| --- | --- |
| SVG, PNG, controls, JSON | Geometry/render/evidence changes versus known path-dependent fields |
| SFD | Actual point data versus observed generated timestamps and XUID |
| OTF | Each table and decoded commands; complete CFF equality versus head/FFTM metadata changes |
| Logs | Operation/warning changes versus output-directory text |

Only normalize fields demonstrated to be nondeterministic metadata, while retaining original files and a field-level report. OTF checksum adjustments may follow timestamp changes; confirm rather than broadly ignoring tables. Never normalize geometry to force a match.

Report the denominator and exceptions: exact-byte files, metadata-only files and path-only logs. Separate designer reruns from independent reruns, and core checks from supplemental files not independently exercised. A frozen hash manifest records identity, not visual approval.

## Review disposition

Tie the verdict to immutable versions and hashes. Report corrected defects, open findings, intentional geometry and aesthetic reservations separately. Reinspect affected outputs after a correction; do not transfer an earlier raster verdict to changed curves. Explicitly state what was viewed, reopened, sampled and rerun. Keep user selection and production qualification separate from this review.
