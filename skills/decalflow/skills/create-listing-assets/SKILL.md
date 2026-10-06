---
name: create-listing-assets
description: Create a complete decal listing image set from supplied product artwork and existing Affinity templates, including imagegen lifestyle mockups, in a separate production folder. Use for new Etsy listing graphics or revisions to an existing listing set. Preserves design masters; does not publish listings or reconstruct product lettering.
---

# Create listing assets

Deliver editable listing sources and ordered upload images for the supplied product design. Use `affinity` for native template work and exact artwork placement; use `imagegen` for photographic scenes. Keep the supplied design authoritative, including its lettering geometry and proportions.

## Protect the inputs

Original brand assets, templates, reference exports, and supplied product designs are read-only inputs. Create independent file copies before opening documents for editing. Never save, export, relink, rename, or write generated content into those originals or their folders. This includes brand documentation and existing template exports.

Resolve actual paths before writing: the production root must be outside the protected asset trees, including through symlinks. Use regular copies, never symlinks or hard links to editable originals. Record SHA-256 hashes of the original files used, including original linked resources, and verify them at completion. Hashes detect changes; they do not replace destination checks. If an original changes, report the discrepancy and investigate without automatically restoring over possible user work.

For The Decal Company, read [references/company-templates.md](references/company-templates.md) before staging. It identifies the protected roots, current templates, and default production location. For another shop, use its supplied assets and instructions instead of importing these brand rules.

## Establish the listing

Inspect the supplied design and every template/export pair. Record the intended product name, artwork path, confirmed sale sizes and colors, personalization, actual shipped piece count, and included items. Distinguish product facts from example names, SVG canvas dimensions, and template copy. Ask only for missing facts that affect the output; continue independent scene and layout work. Keep unresolved claims out of final exports.

Choose a descriptive listing slug and create a new folder. If it already exists, inspect it and create a new revision directory unless the user explicitly requests replacement. Each run uses this structure unless an established production convention applies:

```text
<production-root>/<listing-slug>/
  sources/                  # Working Affinity files, copied product SVG, local resources
  exports/                  # Only finished, numbered upload images
  mockups/                  # Selected generated scenes and prompt records
  review/                   # Input hashes, template map, contact sheet, review findings
  listing.json              # Facts, provenance, output inventory, completion status
```

In `listing.json`, record facts with their source and unknowns as null, the original and copied input paths, output order/dimensions, source document for each output, and status (`draft`, `blocked`, or `complete`). Store the original-input hash inventory under `review/`. Record why a template is unchanged or inapplicable; account for every template in the supplied set.

## Adapt the templates

Load `affinity` and follow its live SDK discovery procedure. Inspect only the working copies for dimensions, spreads, layer structure, fonts, linked/embedded resources, and existing export destinations. Verify the active document's path before any mutation or save; a session UUID alone does not prove it is a copy. Replace inherited export paths with paths under this listing's `exports/`.

Compare native renders with the reference PNGs before choosing replacement layers. Record actual document/spread/layer identifiers and roles in `review/template-map.json`; rediscover session-specific identifiers on later runs. Do not invent SDK methods or rely on layer names guessed from filenames.

Replace every old-product occurrence: artwork, sample personalization, placement boxes, measurements, piece counts, and lettering inside photographs. Preserve fixed branding and applicable instruction copy. Place the exact SVG rather than asking a generator to redraw its letters. Fit by visible artwork bounds, preserving aspect ratio; use a perspective transform only when the photographed surface requires it. Retain a flat copy for comparison.

Copy linked resources into `sources/` and relink the working document there, or embed them in the copy. Resolve font substitution before final export. Preserve outlined artwork as curves; an outlined SVG does not provide keyboard-editable personalization. If a raster photo contains old lettering, use the mockup procedure to replace the photographic region while preserving the template's editable layout.

If Affinity tools are unavailable or return an application restriction, report the specific limitation. Continue inventory, copying, scene preparation, and other independent work; mark native editing/export as blocked. Do not silently substitute Canva web, flatten the whole template, or claim untested native automation works. If the connector requires Desktop staging, work on another copy there and return saved results to the listing folder; inspect the copied resources and save destinations again.

## Create mockups when requested

Read [references/mockups.md](references/mockups.md) for imagegen scene generation, exact artwork compositing in Affinity, and thumbnail review. A complete set for the established workflow includes a hero mockup plus each applicable template graphic. Additional angles or scenes follow the request rather than an arbitrary image quota.

## Verify and deliver

Inspect every final image at full size and as a small thumbnail. Check exact lettering, old-design remnants, proportion, font substitution, placement, realistic material appearance, cropping, logo geometry, disclaimers, and confirmed product facts. Review a contact sheet for consistency and intended order. Measure export dimensions and verify the intended color profile; template dimensions are not universal Etsy requirements.

Keep review previews and unfinished drafts outside `exports/`. Save the editable native files, then reopen the production copies to verify they render and retain their resources. Check original-input hashes again. Mark the listing complete only when the required outputs exist, the editable sources are usable, and visual review passes. Otherwise identify the missing deliverables and retain an accurate draft/blocked status.

Return links to the listing folder, contact sheet, and final exports, with any specific limitation. For generated scenes, record the final prompts and tool mode in `mockups/` and link that record. Publishing to Etsy is a separate task.
