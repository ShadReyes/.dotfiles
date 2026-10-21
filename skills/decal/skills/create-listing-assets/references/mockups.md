# Lifestyle mockups and listing thumbnails

Use `imagegen` for generated photographic scenes and raster edits, and Affinity for the user-requested exact vector placement and template assembly. Load both skills. Use the built-in image generation tool by default; CLI fallback requires the authorization described by `imagegen`.

Read [shared Etsy guidance](../../../references/etsy-listing-guidance.md) before choosing the scene canvas or upload role. Apply its export defaults, crop checks, and photo and mockup guidance for drafts and publication.

## Reference direction

The user supplied `https://www.etsy.com/shop/MMWeddingSigns` as a visual reference, including its mirror-decal thumbnails. A representative listing is `https://www.etsy.com/listing/4385189112/custom-wedding-mirror-decal-easy-to`. Inspect actual reference images when matching their composition; titles, alt text, and the user's statement about AI generation do not verify their production method.

Use references to establish lighting, setting, materials, framing, and product prominence. Generate original scenes for this shop. Keep competitor artwork, branding, and photographs out of final customer-facing assets.

## Choose staging for the design

The user approved these three staging directions. Choose contextually from the actual decal's purpose, wording, typography, visible proportions and confirmed vinyl color; user-supplied venue preferences take precedence. These are visual directions, not blanket approval of the test images' reflection geometry.

| Direction | Useful starting fit | Scene details and tradeoffs |
|---|---|---|
| Shaded terrace | Garden, romantic or relaxed welcome designs; lettering that remains clear over foliage | A simple brass rectangular mirror, pale exterior wall, terracotta flowers and an opposite lawn with irregular trees. Natural overcast light and weathered stone. Simplify the reflected foliage behind fine strokes. |
| Blue indoor foyer | Classic or formal designs, delicate script, detailed personalization that benefits from a quieter reflection | Oak-framed mirror, muted blue plaster, linen welcome table and restrained flowers. Soft window light; simple opposite curtains. Adjust wall/curtain tone for the confirmed vinyl color. |
| Garden porch | Informal, rustic or playful designs; short, bold wording that remains legible in a wider contextual view | Thin black arched mirror on a stable stand, cream wall, wood bench and modest planting. Include ordinary porch space and a coherent opposite lawn/tree reflection. Move closer if the design becomes too small. |

Treat these matches as starting points, not a rigid classification. For example, delicate romantic lettering can suit the foyer better than a busy garden reflection. Fit mirror shape and framing to the artwork without changing its proportions. Choose the best-fitting scene rather than producing all three by default. Record the selected direction and a brief design-specific reason in `mockups/prompts.md`; retain the applicable output count from the requested listing scope.

## Generate the scene

For each wedding mirror-decal design, follow [the required 01A-style couple selfie](couple-selfie.md). Its prompt and acceptance criteria govern that output. The general staging example below applies to additional requested scenes.

Use the selected staging direction to specify the physical surface, opposite reflected scene, camera position, lighting and peripheral props. Keep the venue attractive but attainable and the image like an ordinary phone photograph. Natural variation in materials and incidental framing should provide realism; artificial blur, repeated greenery and uniform hyper-sharp texture should not substitute for a believable scene. For other decal types, choose a setting appropriate to their actual use.

Generate only the blank scene; describe the reserved artwork area by proportions rather than asking imagegen to render the product design. Complete scene edits before adding lettering. Favor a nearly frontal mirror, a quiet reflection behind the lettering, realistic glass and frame details, and sufficient crop margin. For angled glass, keep four reliable coplanar landmarks visible, preferably the four pane corners. Use a window rather than a mirror when the requested use calls for one; account for both transmitted scenery and reflections. Keep props out of the design area. Record the exact final prompt, tool mode, selected output, and intended artwork placement in `mockups/prompts.md`.

Example starting prompt, adapted to the actual design:

```text
Use case: product-mockup
Asset type: Supporting Etsy lifestyle mockup background for a vinyl mirror decal
Primary request: Photorealistic wedding mirror scene with a blank mirror surface for separately placed product artwork.
Scene/backdrop: Elegant wedding interior, restrained white flowers near the base, soft window light.
Subject: Gold-framed arched mirror with realistic reflections and a broad, unobstructed area for the decal.
Composition/framing: Landscape canvas, nearly frontal view; mirror prominent; preserve margin around the frame for thumbnail cropping.
Constraints: No lettering, names, numbers, decals, logos, or watermarks. Quiet reflection behind the future lettering; realistic proportions and materials.
```

Inspect the output before accepting it: geometry, reflection consistency, sufficient placement area, and lack of stray lettering. Request a targeted correction for a specific defect. If two targeted retries fail to fix the same defect, report it and propose a different scene/composition instead of repeating generation indefinitely.

Copy selected generated images into the listing's `mockups/` before referencing them from a native document. A tool's default generated-image directory is not the final project storage location. Preserve reusable clean scenes and their prompt records; reuse them when their surface, lighting, and framing suit another design.

## Place and inspect the exact artwork

For template graphics, place the copied SVG as a distinct editable object/group, preserving the approved flat color and sharp vector appearance. Fit by [visible artwork bounds](../../../references/artwork-sizing.md).

For photographic composites, follow the [Affinity MCP compositing workflow](affinity-compositing.md). It covers direct native placement, a single planar perspective mapping, scene-dependent color and edge treatment, and blank-layer/reopen verification. Keep an unchanged flat SVG for comparison. Preserve source proportions in the surface plane; perspective changes their photographed appearance. Apply photographic treatments only to the composite, never the production SVG or flat product diagrams.

Only when the user explicitly requests a product-specific installation photograph, inspect the local edit target first. The Decal Company uses a shared illustrated installation guide, so its normal listing workflow does not include this step. Use imagegen to produce or edit the blank photographic region, then place the source artwork in Affinity with correct transfer-sheet positioning and hand/tool occlusion. Keep instructional text, logos, and layout outside the generated edit. Review whether the pictured installation action agrees with the accompanying instructions.

Compare the composite to the flat SVG, including fine strokes, punctuation, flourishes, and line breaks. Apply the full-size and thumbnail crop checks in the shared Etsy guidance. The design should remain recognizable and readable, with the frame and props supporting it.

Save a native editable composite in `sources/` and a finished image in `exports/`. Never use a visually plausible generated approximation of the product lettering as the final design. Label illustrative mockups appropriately in listing materials where needed, and keep included-item claims consistent with the decal-only product.
