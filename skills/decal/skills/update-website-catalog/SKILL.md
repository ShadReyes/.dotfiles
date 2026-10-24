---
name: update-website-catalog
description: Add or update an approved decal listing in The Decal Company website catalog, using Etsy Share & Save links. Use after the launch-product Etsy handoff or for catalog maintenance in /Users/shad/src/the-decal-company-site.
---

# Update the website catalog

Add the listing to `/Users/shad/src/the-decal-company-site` using its approved launch facts and images. This is the final `decal:launch-product` step and can also run independently. Prepare and verify repository changes; commit, push, or deploy when the current request or existing authorization includes those actions.

## Establish the product and site state

Use [implement-change](../../../implement-change/SKILL.md) for repository discovery and edits. Read the site's local instructions, README, branch, working tree, and current catalog implementation. Preserve unrelated work and existing products.

Load the product's `launch.json`, listing manifest, destination Etsy listing ID, approved image identities, sale range, and personalization decisions. Read the current listing and relevant inventory/images through the Etsy connector before asserting availability or product options. Match the connected shop and listing ID to this product; the reference and template listings are not the destination. Read-only discovery does not authorize Etsy mutations.

A verified Etsy draft is sufficient to prepare the catalog change locally. Before deploying a public purchase link, confirm the listing is active and available to buyers. Keep a draft's website change local or in a non-production preview until then. An active listing does not authorize deployment by itself; follow the current request's deployment scope. When resuming after owner publication, retain that active state and record it separately from the earlier draft evidence.

## Use the owner's Share & Save URLs

Every link to this Etsy shop uses this exact storefront origin:

```text
https://thedecalcompanyusa.etsy.com
https://thedecalcompanyusa.etsy.com/listing/{listing_id}/{listing_slug}
```

For example: `https://thedecalcompanyusa.etsy.com/listing/4601892113/personalized-wedding-welcome-mirror`.

Reuse the site's `ETSY_SHOP_URL` constant for shop links and construct listing links from that origin and the verified listing identity. Keep the listing ID intact when the title or slug changes. Use these URLs in navigation, catalog image and text links, buttons, footer links, and structured metadata. API responses can contain ordinary `www.etsy.com` URLs; retain those in source receipts, but convert links placed on the website to the storefront format above. Etsy-hosted image files are assets, not shop links.

## Update the catalog

The current catalog source is `src/data/products.ts` (`CATALOG_PRODUCTS`); `src/components/CatalogCard.astro` renders it on `src/pages/index.astro`. Rediscover these paths if the site changes. Update an existing entry by listing ID on resume instead of adding a duplicate. Keep unrelated catalog entries and the general example/guide content.

Use the approved listing title or a concise equivalent, factual product copy, the destination listing ID and slug, and a product-specific image. Copy the approved export into `public/images/products/` using a stable descriptive filename. Retain the source path/hash and copied file hash; preserve artwork and image proportions. Use actual image dimensions and descriptive alt text, identifying styled mockups and sample personalization where relevant. Website preparation reuses approved assets; artwork or image revisions return to their owning design/listing-assets workflow.

Describe only the verified product: personalization, included Pieces, colors, surfaces, and offered sizes. State that mirrors and props are excluded when applicable. Use customer language; keep production implementation details in the run record. Prefer referring buyers to Etsy for current prices/options instead of duplicating a changing price ladder. Any displayed price must come from current enabled offerings with its currency and relevant variation qualification.

## Verify and record

Run the repository's build and relevant checks. Inspect the built home page on desktop and mobile: the new entry appears once, the correct image loads without clipping the design, copy remains readable, and its image/button links target the exact listing. Check internal links and local image paths. Inspect all generated pages, including structured metadata, for links to Etsy; links to this shop must use the storefront origin above. A source-only URL search misses rendered links and metadata.

Record a website checkpoint in the product's `launch.json`, with a linked receipt when useful:

- Repository, branch, listing ID, Share & Save URL, and current Etsy state/readback timestamp.
- Catalog entry and asset paths/hashes, approved source-image identity, changed files, and build/review results.
- Preparation status, commit/push status, and deployment status separately. If deployed, retain the revision/deployment identity, public URL, and live page/link verification. A local build or preview upload is not production verification.
- Any deferred action, such as owner publication of an Etsy draft or a requested deployment.

Completion means the catalog change is present and verified at the requested scope. The default launch handoff is **website prepared and verified locally**; report deployment separately. Return the catalog changes, Share & Save listing URL, checks, and actual deployment state.
