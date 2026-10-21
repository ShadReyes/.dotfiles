---
name: create-listing-assets
description: Create a complete decal listing image set from supplied product artwork and existing Affinity templates, including imagegen lifestyle mockups, in a separate production folder. Use for new Etsy listing graphics or revisions to an existing listing set. Preserves design masters; does not publish listings or reconstruct product lettering.
---

# Create listing assets

Deliver editable listing sources and ordered upload images for the supplied product design. Use `affinity` for native template work and exact artwork placement; use `imagegen` for photographic scenes. Keep the supplied design authoritative, including its lettering geometry and proportions.

## Protect the inputs

Original brand assets, templates, reference exports, and supplied product designs are read-only inputs. For each template that needs adaptation, create one independent copy directly under its numbered production filename (for example, `sources/02-about-this-design.af`) before opening it for editing. This copy becomes the editable production source; keep the pristine master in its original location rather than retaining another base-template copy in the listing. Never save, export, relink, rename, or write generated content into those originals or their folders. This includes brand documentation and existing template exports.

Resolve actual paths before writing: the production root must be outside the protected asset trees, including through symlinks. Use regular copies, never symlinks or hard links to editable originals. Record SHA-256 hashes of the original files used, including original linked resources, and verify them at completion. Hashes detect changes; they do not replace destination checks. If an original changes, report the discrepancy and investigate without automatically restoring over possible user work.

For The Decal Company, read [references/company-templates.md](references/company-templates.md) before staging. It defines the protected roots, current templates, production location, intake, approved copy, and mirror placement rules. For another shop, use its supplied assets and instructions instead of importing these brand rules.

## Establish the listing

Read [shared Etsy guidance](../../references/etsy-listing-guidance.md) before choosing image dimensions, composition, or upload order. Use its export defaults for new images and its photo and mockup guidance for draft sets and publication checks; preserve approved template dimensions.

Apply [finished artwork sizing](../../references/artwork-sizing.md) when inspecting SVG dimensions, placing artwork, or verifying size graphics. Record measured artwork bounds separately from artboard dimensions in `listing.json`; a decal-width claim refers to visible artwork. This does not expand the template intake below or change the supplied production master.

Inspect the supplied design and every template/export pair. Record the product name and artwork path. For The Decal Company, follow the [intake and approved copy rules](references/company-templates.md#intake-and-approved-copy). For another shop, use its supplied template rules. Reuse answers already supplied and continue independent scene and layout work while awaiting missing details.

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

Replace old artwork, sample names and dates within the artwork, artwork-specific placement boxes, and lettering inside photographs. Apply the shop's approved copy rules. For SVG placement on templates or photographs, follow [exact artwork placement](references/mockups.md#place-and-inspect-the-exact-artwork). For The Decal Company, also apply the [mirror placement rules](references/company-templates.md#mirror-placement).

Copy linked resources into `sources/` and relink the working document there, or embed them in the copy. Resolve font substitution before final export. Preserve outlined artwork as curves; an outlined SVG does not provide keyboard-editable personalization. If a raster photo contains old lettering, use the mockup procedure to replace the photographic region while preserving the template's editable layout.

If Affinity tools are unavailable or return an application restriction, report the specific limitation. Continue inventory, copying, scene preparation, and other independent work; mark native editing/export as blocked. Do not silently substitute Canva web, flatten the whole template, or claim untested native automation works. If the connector requires Desktop staging, work on another copy there and return saved results to the listing folder; inspect the copied resources and save destinations again.

## Create supporting mockups

Read [references/mockups.md](references/mockups.md) for imagegen scene generation, exact artwork compositing in Affinity, and thumbnail review. For every wedding mirror-decal design, generate the required [01A-style couple selfie](references/couple-selfie.md) as a product-specific supporting image. Generate and inspect a blank photographic scene, then use the [Affinity MCP compositing workflow](references/affinity-compositing.md) to place the supplied SVG, match the surface perspective, and match the photographed appearance. Keep the product artwork separate from image generation. Include this output in the manifest and contact sheet; retain draft/blocked status if its scene or composite fails review. For a product that does not suit a wedding mirror selfie, record the reason it is inapplicable rather than forcing that setting onto it.

A complete draft image set includes a suitable first image, each applicable template graphic, and the required selfie. Follow shared Etsy guidance for photo and mockup provenance. Use an approved exact-artwork composite for the first draft image and record its provenance in `listing.json`. For additional staging, [choose the scene contextually from the design](references/mockups.md#choose-staging-for-the-design). Other staging variations remain optional unless requested.

## Verify and deliver

For a requested DecalFlow handoff, use `decal:decalflow` with the reviewed design
package. Reference its package manifest in `listing.json`; preserve the design
version, package hash and returned Product/mapping IDs under `decalflow`. Register
or update local records only within the requested workflow. Listing-image
completion does not imply registration, Etsy publication, or cutter start.

Inspect every final image at full size and as a small thumbnail. Check exact lettering, old-design remnants, proportion, font substitution, placement, realistic material appearance, cropping, logo geometry, disclaimers, selected SVG color and shipped piece count. Compare template text and measurement labels against the originals using the shop's approved copy rules. For The Decal Company, compare About and Size Guide side by side against the mirror placement rules and record any permitted exception. Review a contact sheet for consistency and intended order. Check export dimensions, color profile, thumbnail crops, and first-image eligibility against the shared Etsy guidance; record approved template exceptions.

Keep review previews and unfinished drafts outside `exports/`. Save the editable native files, then reopen the production copies to verify they render and retain their resources. Check original-input hashes again. Verify every shared-asset path resolves and its recorded hash matches. Check that current sources contain no redundant pristine template copies and that manifests reference the current files. Mark the listing complete only when the required product-specific outputs and shared graphics exist, the editable sources are usable, and visual review passes. Otherwise identify the missing deliverables and retain an accurate draft/blocked status.

Return links to the listing folder, contact sheet, final product-specific exports, and shared upload graphics, with any specific limitation. For generated scenes, record the final prompts and tool mode in `mockups/` and link that record. Publishing to Etsy is a separate task.
