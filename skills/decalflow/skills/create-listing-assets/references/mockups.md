# Lifestyle mockups and listing thumbnails

Use `imagegen` for generated photographic scenes and raster edits, and Affinity for the user-requested exact vector placement and template assembly. Load both skills. Use the built-in image generation tool by default; CLI fallback requires the authorization described by `imagegen`.

Read [shared Etsy guidance](../../../references/etsy-listing-guidance.md) before choosing the scene canvas or upload role. Apply its export defaults, crop checks, and personalized-item first-photo rule.

## Reference direction

The user supplied `https://www.etsy.com/shop/MMWeddingSigns` as a visual reference, including its mirror-decal thumbnails. A representative listing is `https://www.etsy.com/listing/4385189112/custom-wedding-mirror-decal-easy-to`. Inspect actual reference images when matching their composition; titles, alt text, and the user's statement about AI generation do not verify their production method.

Use references to establish lighting, setting, materials, framing, and product prominence. Generate original scenes for this shop. Keep competitor artwork, branding, and photographs out of final customer-facing assets.

## Generate the scene

Decide the physical surface and composition from the actual product and reference. A gold arched mirror in a wedding venue with soft window light and restrained flowers is a starting direction for this example, not a required setting for all decals.

Generate a blank surface so the final lettering can come from the supplied SVG. Favor a nearly frontal mirror, a quiet reflection behind the lettering, realistic glass and frame details, and sufficient crop margin. Keep props out of the design area. Record the exact final prompt, tool mode, selected output, and intended artwork placement in `mockups/prompts.md`.

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

Place the copied product SVG over the scene in Affinity as a distinct editable object/group. Preserve a flat vector version and the clean background. Match the plane of the glass without changing the underlying letter shapes, spacing, or aspect ratio. Use a confirmed product color, with realistic vinyl opacity and minimal effects; avoid a floating sticker or embossed appearance unless that matches the product.

Only when the user explicitly requests a product-specific installation photograph, inspect the local edit target first. The Decal Company uses a shared illustrated installation guide, so its normal listing workflow does not include this step. Use imagegen to produce or edit the blank photographic region, then place the source artwork in Affinity with correct transfer-sheet positioning and hand/tool occlusion. Keep instructional text, logos, and layout outside the generated edit. Review whether the pictured installation action agrees with the accompanying instructions.

Compare the composite to the flat SVG, including fine strokes, punctuation, flourishes, and line breaks. Apply the full-size and thumbnail crop checks in the shared Etsy guidance. The design should remain recognizable and readable, with the frame and props supporting it.

Save a native editable composite in `sources/` and a finished image in `exports/`. Never use a visually plausible generated approximation of the product lettering as the final design. Label illustrative mockups appropriately in listing materials where needed, and keep included-item claims consistent with the decal-only product.
