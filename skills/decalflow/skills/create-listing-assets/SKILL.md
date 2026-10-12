---
name: create-listing-assets
description: Create a complete decal listing image set from supplied product artwork and existing Affinity templates, including imagegen lifestyle mockups, in a separate production folder. Use for new Etsy listing graphics or revisions to an existing listing set. Preserves design masters; does not publish listings or reconstruct product lettering.
---

# Create listing assets

Deliver editable listing sources and ordered upload images for the supplied product design. Use `affinity` for native template work and exact artwork placement; use `imagegen` for photographic scenes. Keep the supplied design authoritative, including its lettering geometry and proportions.

## Protect the inputs

Original brand assets, templates, reference exports, and supplied product designs are read-only inputs. For each template that needs adaptation, create one independent copy directly under its numbered production filename (for example, `sources/02-about-this-design.af`) before opening it for editing. This copy becomes the editable production source; keep the pristine master in its original location rather than retaining another base-template copy in the listing. Never save, export, relink, rename, or write generated content into those originals or their folders. This includes brand documentation and existing template exports.

Resolve actual paths before writing: the production root must be outside the protected asset trees, including through symlinks. Use regular copies, never symlinks or hard links to editable originals. Record SHA-256 hashes of the original files used, including original linked resources, and verify them at completion. Hashes detect changes; they do not replace destination checks. If an original changes, report the discrepancy and investigate without automatically restoring over possible user work.

For The Decal Company, read [references/company-templates.md](references/company-templates.md) before staging. It identifies the protected roots, current templates, and default production location. For another shop, use its supplied assets and instructions instead of importing these brand rules.

## Establish the listing

Read [shared Etsy guidance](../../references/etsy-listing-guidance.md) before choosing image dimensions, composition, or upload order. Use its export defaults for new images and its first-photo rule for Etsy-ready sets; preserve approved template dimensions.

Inspect the supplied design and every template/export pair. Record the product name and artwork path. For The Decal Company, request only these missing production details, preferably together:

- SVG display color: white, black, or gold.
- Number of separate pieces the design ships in.

Reuse answers already supplied. Continue independent scene and layout work while awaiting either answer. Treat the remaining template copy as approved and fixed, including personalization instructions, sizing bullets, measurement examples and disclaimers. These examples are template content, not sale-option data to collect. Preserve them instead of substituting placeholders or adding questions about sale sizes, available color ranges, personalization policies or included items. Expand the intake only when the user explicitly requests changes that need additional facts. For another shop, follow its supplied template rules.

Choose a descriptive listing slug and create a new folder. If it already exists, inspect it and create a new revision directory unless the user explicitly requests replacement. Each run uses this structure unless an established production convention applies:

```text
<production-root>/<listing-slug>/
  sources/                  # Working Affinity files, copied product SVG, local resources
  exports/                  # Finished product-specific upload images; create at first final export
  mockups/                  # Selected generated scenes and prompt records
  review/                   # Input hashes, template map, contact sheet, review findings
  listing.json              # Facts, provenance, output inventory, completion status
```

Create folders only when they contain required files. Store drafts in `review/drafts/`; a blocked run can have no `exports/` folder. Keep one current native source per product-specific output. Keep user-requested prior revisions under `review/superseded/` and distinguish them from current sources. Temporary inspection copies and Desktop staging belong outside the deliverable; remove only run-created temporary files after verifying the returned production sources and their resources. Do not delete pre-existing revisions or possible user work as routine cleanup.

In `listing.json`, record the selected SVG color and shipped piece count with their source; use null for either unanswered detail. Record the approved template-copy policy, the original and copied input paths, output order/dimensions, source document for each output, and status (`draft`, `blocked`, or `complete`). Store the original-input hash inventory under `review/`. Account for every template as adapted, shared unchanged, or inapplicable. Record shared graphics in `shared_assets` with their canonical export and native source paths, upload order, dimensions, and current export hash. Reference shared graphics directly; do not copy their native files, PNGs, or mockups into each listing. Include them in upload order and contact-sheet review. A complete listing set can combine product-specific exports and shared assets.

## Adapt the templates

Load `affinity` and follow its live SDK discovery procedure. Inspect only the working copies for dimensions, spreads, layer structure, fonts, linked/embedded resources, and existing export destinations. Verify the active document's path before any mutation or save; a session UUID alone does not prove it is a copy. Replace inherited export paths with paths under this listing's `exports/` for final images or `review/drafts/` for drafts. Apply this editing procedure only to templates marked for adaptation.

Compare native renders with the reference PNGs before choosing replacement layers. Record actual document/spread/layer identifiers and roles in `review/template-map.json`; rediscover session-specific identifiers on later runs. Do not invent SDK methods or rely on layer names guessed from filenames.

Replace old artwork, sample names and dates within the artwork, artwork-specific placement boxes, and lettering inside photographs. Update only the shipped-piece count in the template copy, with singular/plural agreement where needed. Preserve all other template text, measurement labels, branding and instructions unless the user requests a text change. Keep approved sizing examples separate from the artwork being replaced. Place the exact SVG rather than asking a generator to redraw its letters. Fit by visible artwork bounds, preserving aspect ratio; use a perspective transform only when the photographed surface requires it. Retain a flat copy for comparison.

For The Decal Company, place the complete sign design toward the top of the mirror in both the About and Size Guide graphics. Match its relative position within the mirror across both graphics, rather than using equal page coordinates when mirror sizes or positions differ. Preserve the exact artwork proportions and use consistent scale relative to mirror width. Use another arrangement when confirmed separate pieces, the supplied design, or user instructions require it; record that reason. This placement default does not establish the shipped-piece count, which must still be confirmed separately. In the Size Guide, keep the artwork above the sizing arrow and label. Move the arrow and label down together if clearance is needed, keeping the label above the arrow and preserving all measurement text and sizing bullets.

Copy linked resources into `sources/` and relink the working document there, or embed them in the copy. Resolve font substitution before final export. Preserve outlined artwork as curves; an outlined SVG does not provide keyboard-editable personalization. If a raster photo contains old lettering, use the mockup procedure to replace the photographic region while preserving the template's editable layout.

If Affinity tools are unavailable or return an application restriction, report the specific limitation. Continue inventory, copying, scene preparation, and other independent work; mark native editing/export as blocked. Do not silently substitute Canva web, flatten the whole template, or claim untested native automation works. If the connector requires Desktop staging, work on another copy there and return saved results to the listing folder; inspect the copied resources and save destinations again.

## Create mockups when requested

Read [references/mockups.md](references/mockups.md) for imagegen scene generation, exact artwork compositing in Affinity, and thumbnail review. A complete Etsy-ready set includes a suitable first photo plus each applicable template graphic. Generated lifestyle mockups follow the roles in the shared Etsy guidance. If the first photo is missing, continue the requested asset work and record that gap in `listing.json`. Additional angles or scenes follow the request rather than an arbitrary image quota.

## Verify and deliver

Inspect every final image at full size and as a small thumbnail. Check exact lettering, old-design remnants, proportion, font substitution, placement, realistic material appearance, cropping, logo geometry, disclaimers, selected SVG color and shipped piece count. Compare template text and measurement labels against the originals; only the piece-count substitution and user-requested text changes should differ. Compare the About and Size Guide side by side: verify consistent artwork height and scale relative to the mirror, top placement, and clearance above the sizing arrow and label. Record any design-specific reason for a different arrangement. Review a contact sheet for consistency and intended order. Check export dimensions, color profile, thumbnail crops, and first-image eligibility against the shared Etsy guidance; record approved template exceptions.

Keep review previews and unfinished drafts outside `exports/`. Save the editable native files, then reopen the production copies to verify they render and retain their resources. Check original-input hashes again. Verify every shared-asset path resolves and its recorded hash matches. Check that current sources contain no redundant pristine template copies and that manifests reference the current files. Mark the listing complete only when the required product-specific outputs and shared graphics exist, the editable sources are usable, and visual review passes. Otherwise identify the missing deliverables and retain an accurate draft/blocked status.

Return links to the listing folder, contact sheet, final product-specific exports, and shared upload graphics, with any specific limitation. For generated scenes, record the final prompts and tool mode in `mockups/` and link that record. Publishing to Etsy is a separate task.
