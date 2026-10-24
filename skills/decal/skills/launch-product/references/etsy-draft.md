# Etsy draft handoff

Use the installed Etsy MCP and inspect its current tool schemas before constructing requests. The current local server source is `/Users/shad/src/etsy-mcp`; its README and generated endpoint catalog document transport and supported fields. Never read credentials into output. This workflow authorizes creating a new draft after its approval gates; it does not authorize changing the source listing or activating the destination.

For the destination link in the launch handoff and website, use the owner's Share & Save storefront format in [update-website-catalog](../../update-website-catalog/SKILL.md#use-the-owners-share--save-urls). Retain the API's original URL in readback evidence. After verifying this stage, continue to the launch workflow's final website catalog step.

## Adapt the source

Resolve the connected shop, then read the selected template listing, inventory, personalization, properties, images, and applicable variation-image mappings. Use live data, not synthetic DecalFlow fixtures or old receipts, for inherited settings. Use the approved [shop price plan](pricing.md) for destination widths and prices.

Build a destination specification before writing:

- Product-specific title, description, tags, materials, Piece count, supported surfaces/use, and personalization instructions. Remove old product wording and sample data.
- The exact 13-tag array from the validated `tag-plan.json`, prepared with [decal:product-tags](../../product-tags/SKILL.md). Re-evaluate base candidates against the destination category/attributes and replace the template's wording/use tags; reserved dynamic slots must be filled with actual product-specific phrases.
- Applicable taxonomy/properties, shipping, return policy, processing/readiness, shop section, and production-partner settings. Validate required values and whether inherited settings apply to the new product.
- Size/price combinations from the approved [shop price plan](pricing.md), filtered to the qualified sale range and with any whole-inch maximum rung calculated by that policy. Map widths to explicit units under the [production contract](../../../references/decalflow-production-contract.md#width-and-geometry). Apply its retention rules when revising historical claims. Preserve applicable template color/other combinations, quantities, and inventory dependency fields. The USD ladder supersedes copied widths and prices; resolve a currency mismatch explicitly. Size-guide examples do not establish sale options.
- New, non-colliding SKUs when the shop uses them, with a retained mapping to the new Product. Never reuse identifiers that would route this design's orders to the template product.
- Exact approved image paths, hashes, order, and descriptive alt text identifying styled mockups as such.
- Personalization questions for personalized designs, even when the template has none. Follow [personalization](personalization.md).

No clone endpoint exists. Translate read resources into each write schema. Strip response-only IDs and fields, convert Money amounts using the returned divisor, and retain only supported request fields. Do not reuse template image IDs as the new product's approved artwork.

## Write and read back

1. Save creation intent, then call `createDraftListing` with supported required fields and appropriate settings. Retain the returned listing ID immediately. This endpoint creates the draft; do not set `state: active`. The current `updateListing` state enum does not support setting `draft`; leave the creation state unchanged.
2. Set the complete intended inventory through `updateListingInventory`. It replaces inventory rather than patching individual options. Preserve the applicable `price_on_property`, `quantity_on_property`, `sku_on_property`, and readiness dependencies. Each offering's required readiness value must follow the current schema. `updateListing` does not set inventory price/quantity.
3. Set applicable properties and personalization through their dedicated endpoints. The current personalization body uses `personalization_questions`, with schema-defined question text, type, requiredness and limits. Follow [question readback and mapping verification](personalization.md#etsy-and-order-intake) after each question or instruction update, before building or reusing intake extraction rules; question IDs can change.
4. Upload approved images with explicit ranks; retain upload IDs after each response. Rebuild variation-image associations from destination image IDs where applicable. Verify the image count/order, dimensions, alt text, and returned image content against the approved set; server recompression can change file hashes.
5. Retrieve listing, inventory, personalization, properties, images, and applicable variation-image associations. Compare normalized values to the destination specification: state is draft, all 13 saved tags match the tag plan as a normalized set, retained options have correct prices/currency/quantities, images are complete and ordered, product facts and instructions match, and settings apply. Keep discrepancies blocked until corrected and read back again.
6. Use `decal:decalflow` to dry-run and save the exact shop/listing-to-Product mapping with current option labels/answers, fixed options, and personalization extraction rules. Verify IDs, revisions, and mappings using the installed read commands. Exercise extraction using the read-only procedure below; mapping persistence alone is insufficient.

Partial success remains a resumable draft. Follow [run-state recovery](run-state.md) after uncertain writes. An Etsy draft without a verified intake mapping is incomplete; leave it in draft and report the mapping blocker.


## Read-only extraction verification

The current CLI has no extraction-preview command. Use the installed checkout's pure `extractPersonalization` function in `packages/domain/src/personalization.ts`; rediscover its signature and input schemas before use. Create a temporary local TypeScript harness and run it with the checkout's pinned Node/tsx tooling. Import this domain function only, not API startup or database modules. Load the inspected Product definition, saved extraction rule, and destination question IDs from retained JSON evidence.

The current call is `extractPersonalization(raw, rule, definition, options, purchasedAnswers)`, where each purchased answer has `questionId`, `label`, and `answer`. Supply representative synthetic text/date answers and sale-option values. Assert the exact expected field values, date normalization, and automatic/review result. Also exercise missing required answers, invalid dates, and mismatched question identities; inspect issues rather than assuming a saved rule parsed the intended values. For the current exact-label mapping, include changed question IDs with unchanged labels and a nonmatching-label case, and verify the expected extraction/review outcomes. Fixed products still need their option-to-size/color mapping checked. Keep the harness inputs, assertions, and result with review evidence; do not create fake Orders, sync, or write the database. If current code no longer exposes a usable pure interface, report verification as blocked instead of inventing a CLI command.
