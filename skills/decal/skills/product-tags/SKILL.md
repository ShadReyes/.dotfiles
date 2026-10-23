---
name: product-tags
description: Research, create, or improve Etsy product tags for decal listings and templates. Use for keyword selection, a reusable base plus product-specific tags, or tag audits; supports the launch-product draft workflow.
---

# Create Etsy product tags

Produce a relevant, validated set of 13 tags and retain the reasoning needed to revise it. Treat improved search matching as the objective; tag compliance alone does not prove higher conversion.

## Establish the product and evidence

Read [research and source priorities](references/research.md) before selecting tags. Recheck official Etsy limits and guidance for the current task; retain source URLs and the access date. Etsy controls platform rules. Treat third-party advice as research methods, and the base/dynamic split as a local default.

Inspect the approved artwork, exact wording, physical contents, supported surfaces, occasion, style, sale options, and actual personalization contract. For an existing listing or template, retrieve its tags, language, category path, and populated attributes. Use live product facts; a photo prop is not an included item. Missing facts exclude the affected claim until verified.

Identify buyer intent: what the buyer receives and what task it serves. A decal-only listing needs decal, lettering, vinyl, or sticker terms to distinguish it from a finished mirror or sign. A seating-chart heading does not include guest names unless the product contract says so. Use custom/personalized tags only when those options can actually be purchased and fulfilled.

## Research and choose

Build more candidates than slots from product type, purpose, wording, surface, style, technique, and supported customization. Favor plausible buyer phrases over internal production terms. Prefer available first-party Etsy Marketplace Insights measurements for marketplace demand; use Shop Stats for the listing's own performance. Connected keyword services can add evidence, with their provider and methodology identified. For Marketplace Insights searches or saved GUI results, read [the research procedure](references/marketplace-insights.md); use `cua-driver` for authorized work in an authenticated browser. Record the provider, displayed geography if any, time window, retrieval date, and observed values. Search suggestions and competitor tags generate ideas; their presence alone does not establish demand or conversion.

Compare relevant phrases using search demand, Etsy's displayed conversion tier, competing results, and distinct intent coverage together. Conversion tiers are ordinal marketplace indicators, not exact percentages, a ranking within the same tier, or this listing's conversion rate. Preserve rounded counts, unavailable values, and incomplete captures as displayed. A search-to-results ratio is only a rough comparison, not a sales forecast.

If keyword metrics are unavailable, continue with a fact-based candidate set and label demand unmeasured. Never invent search volume, low competition, or sales evidence. Do not buy subscriptions or require paid keyword tooling to finish a tag plan.

For wedding mirror decals, use [the conditional base](references/wedding-base.md). Start with up to **4 applicable base tags** and reserve **at least 9 slots for this product**. Replace an inapplicable or weak base tag with another relevant phrase; base tags are candidates, not mandatory shop-wide tags. Other product families need their own facts and phrases. Fill all 13 slots in the final listing; dynamic slots contain real tags, never blanks or placeholders.

Select for truthful buyer intent first, observed demand when available, specificity, and coverage the other tags do not provide. Preserve useful multi-word phrases. When a query exceeds 20 characters, use natural shorter phrases that cover its meaning; do not truncate words or claim that split tags guarantee an exact-phrase match. Some words can recur in distinct useful phrases; do not impose a blanket ban on repeated words. Remove duplicates, plural-only variants, and weak paraphrases that add no useful intent.

## Validate and retain

Before writing, check every selected tag:

- Exactly 13 nonempty, trimmed strings, unique after case and whitespace normalization. Each has at most 20 characters, counting spaces and punctuation.
- Characters comply with the current Etsy rules in the research reference; letters/numbers/spaces are the default, with permitted internal apostrophes or hyphens when needed. Tags are separate array entries, not a comma-delimited string.
- Language matches the listing. Use correct spelling; intentional typos, separate singular/plural variants, and extra language variants consume slots without useful coverage.
- Each tag describes the actual product or a supported use. Remove inherited phrases, props, sample couple names/dates, unsupported customization, and irrelevant trends.
- No tag merely duplicates an exact category or populated attribute phrase. A longer phrase that adds relevant meaning can remain. Important title phrases can also be tags; do not stuff all tags into the title or description.
- The set covers the product and distinct buyer intents. Do not fill slots with misleading terms merely to reach 13. If 13 relevant phrases cannot be justified, retain the partial plan and report the missing facts or research needed.

Save `tag-plan.json` in the product's production folder, or an explicitly chosen local evidence folder for a standalone template edit. Retain product identity/version, fact sources, listing language/category/attributes, research URLs/date and metric availability, candidate decisions, base/dynamic roles, each selected tag's character count and rationale, the exact final array, and validation results. For measured candidates, link the captured query, period, displayed searches/results/conversion tier, source type (direct query or related suggestion), and snapshot. Distinguish unavailable measurements, pending UI content, and unqueried candidates. Keep shop performance and private records outside public skill files. Link the plan and its hash from `launch.json` when part of a launch.

## Apply and verify when authorized

Creating a plan does not authorize remote edits. Follow the current request or parent workflow's mutation scope. `launch-product` may write the destination draft after its existing gates; it does not authorize changing the source template. An explicit request to update the template authorizes that scoped edit.

Inspect the current Etsy MCP schemas. Re-read the target immediately before writing, reconcile changes, and save the before snapshot and intended tag array. For a tags-only edit, send only `tags` to `updateListing`; omit state and unrelated fields. This replaces the whole tag set, so send all 13 selected tags. Read the listing back and compare normalized tag sets, allowing order changes. Verify its state and unrelated listing fields remain unchanged; retain the request, response, and readback. An uncertain write requires readback before any retry.

For a new draft, use the final array in the destination specification and verify it with the rest of the saved draft. Completion requires a valid plan and, when a write was requested, matching saved tags. A mismatch remains incomplete.

## Review later evidence

Record the change date and baseline when traffic/search data are available. Compare subsequent search terms, visits, clicks, and orders over comparable periods, noting seasonality and concurrent listing changes. Revise weak tags when evidence warrants it. A sparse sample, tool score, competitor sales, or before/after change alone does not establish a conversion effect. Do not schedule monitoring unless requested.
