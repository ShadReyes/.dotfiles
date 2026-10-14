# Blank scene to Affinity composite

Use this workflow for photographic decal mockups. The user adopted it after testing a frontal couple selfie and an angled porch window. Keep scene generation, vector placement and photographic appearance as separate operations. Use the `affinity` skill and its live SDK discovery procedure; the API notes below describe tested behavior, not a substitute for current documentation.

## Prepare the blank scene

Generate the scene with imagegen without product lettering. Inspect reflection geometry, support, contrast and space for the whole design before placement. Correct the blank image first. Keep the accepted blank image in `mockups/`; do not pass the finished lettering through imagegen to blend it into the scene.

For an angled surface, identify four coplanar landmarks in consistent corner order. Prefer the glass corners, not the outer frame edges at another depth. Request a framing correction if the required landmarks are cropped or ambiguous. A correct artwork mapping does not repair an impossible generated scene.

## Place through Affinity MCP

Work on copies and verify the native document path before mutation. Keep the supplied production SVG unchanged. Open/import that SVG through Affinity MCP, preserve its complete design as an editable vector group, and place the blank photo as a separate embedded layer beneath it. Perform artwork placement and appearance changes through MCP; an externally assembled SVG opened in Affinity afterward is not the tested native-placement workflow.

- For a frontal plane, uniformly scale by visible artwork bounds and translate the complete group into position.
- For an angled plane, map the complete design with one projective homography. Define its placement and unchanged aspect ratio in the physical surface plane before projection. Keep all lines, flourishes and punctuation under the same mapping. Rotation, shear or independent line adjustments cannot substitute for perspective.
- Record the landmarks, plane aspect ratio, placement rectangle and transform. Use measured surface dimensions when supplied; otherwise label the ratio and physical size assumptions as illustrative. Four image corners alone do not establish the physical aspect ratio or decal size.

### Perspective fallback through editable contours

In the tested SDK, the ordinary `Transform` supported affine operations, while curve editing allowed a projective mapping. Rediscover current support before selecting this fallback. Prefer a verified native perspective operation if available.

Read each path through `node.curvesInterface.polyCurve`. Apply a homography with homogeneous division to points on the actual curves. Adaptively subdivide the projected curves to a recorded subpixel error tolerance, rebuild editable contours with `CurveBuilder` and `PolyCurve`, and commit them through `DocumentCommand.createSetCurves(node.curvesInterface, polyCurve)`. Preserve contour closure, holes and fill rules. Transforming only Bezier control points is not an exact projective transform of a Bezier curve.

Account for the node/domain transforms and document units when converting projected pixel coordinates back to curve space; avoid applying inherited scaling twice. Preserve the unchanged source SVG separately. Describe this result as projected, approximated vector contours, not an unchanged path representation or a live perspective effect. Inspect fine strokes and counters after projection.

Tested native operations useful for this workflow:

- `Document.load`, `saveAs`, `setSpreadSizeWithAnchor` and `applyTransform` for the copied SVG and frontal placement.
- `Bitmap.loadFromFile`, `ImageNodeDefinition` and `AddChildNodesCommandBuilder` for the separate photo layer. In the test, targeting the current spread with `InsertionMode.Inside_AtFront` placed the photo beneath the artwork. Verify actual layer order with a render.
- `setBrushFillDescriptor(RGB8(...), curveNode)` for composite-only tone adjustments; `setGaussianBlurLayerEffectRadius` and `setGaussianBlurLayerEffectEnabled` for reversible edge softness on the artwork group.
- `setVisible(false, artworkGroup)` for blank-image verification, then restore visibility before saving.

## Match the photographed appearance

Match the photographed material and camera sharpness rather than leaving lettering unnaturally perfect. Keep the confirmed vinyl color category; these are rendering adjustments, not changes to product options or cutting artwork.

- For black vinyl, a slightly lifted dark neutral can fit the scene better than pure `#000000`. The approved test used `#242522`; use it as a starting point, not a universal replacement. Check against dark objects under comparable light in the current photo.
- Keep solid vinyl opaque. Do not lower the whole group's opacity to let reflections show through its strokes. Antialiasing and slight edge softness can affect edge pixels without making the vinyl translucent.
- When the photo is softer than the vectors, apply subtle, reversible edge softness to the artwork alone. The user preferred the softened selfie; the test used a Gaussian radius of `0.4` document units at a 1122 × 1402 export. Calibrate against the current document units, transforms and final pixel size rather than copying that number blindly.
- Keep sharp lettering on sharp scenes. The angled porch test used a slight color adjustment and no blur. Do not blur every lifestyle image, add a drop shadow or bevel to simulate thin vinyl, or blur the whole photo to conceal placement errors.

Inspect the complete image at native size and at listing-thumbnail size. Keep the subtitle readable and avoid halos or disappearing fine strokes. Use a same-scene comparison when tuning an unfamiliar treatment; the workflow does not require a new user approval for routine placement on every listing.

## Verify and retain

Save the native composite with embedded photo and editable artwork, then reopen it and compare the exported render. Hide the artwork and export a lossless blank check: with identical dimensions and color settings, it should match the accepted blank photo pixel-for-pixel. Investigate unexpected differences; if a documented profile conversion or resampling prevents equality, record that limitation instead of claiming an exact match. Restore artwork visibility and save the deliverable.

Retain the blank image, unchanged source SVG, native composite, final image and prompt/placement record in the listing's established folders. Record tone, opacity, edge-effect settings, transform method, approximation tolerance where applicable, dimensions, and verification results. Provide a blank/composite comparison for review. Keep unfinished outputs in drafts; upscaling a small generated base does not supply missing photographic detail. Preserve the listing's existing export order and generated-image provenance rules.
