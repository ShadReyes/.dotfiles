# Run state and approval evidence

Use `launch.json` as the coordinating record, with relative links to existing listing manifests, DecalFlow receipts, exports, and review artifacts. Application records remain authoritative for their own state. Do not duplicate their full schemas in this manifest or edit the DecalFlow database.

Record:

- Run ID, product slug, source reference/artwork, source hash, exact design version/package hash, and mode (`fixed` or `personalized`).
- Design options with stable IDs, versions, editable source and preview paths/hashes, change notes, available source ownership/license information, and unresolved rights questions. Record the comparison brief and the user's selected option/version separately from final design/Piece approval.
- Font-match record path/hash, per-element review status, WhatTheFont evidence, substitute acceptance, and scoped Affinity fallback authorization when reconstructing reference lettering. Fallback authorization permits the attempt; it does not approve the resulting artwork.
- Piece definitions, field contract and sample/extreme inputs, exact fitting policy, template shop/listing IDs, Product/mapping IDs and revisions.
- Preparation IDs and output hashes, sizing policy, per-Piece and assembled widths, local/final factors, measured warnings, and application warning-acceptance references. Link application receipts rather than inventing a parallel acceptance record.
- Each stage's status (`pending`, `working`, `awaiting-approval`, `blocked`, `complete`, or `stale`), evidence paths, and next action.
- Calculated size-limit receipts, production arrangement, candidate and approved endpoint widths, units, and offered size/price combinations. Record minimum physical results separately from maximum digital fit and optional maximum physical results. A skipped maximum physical test is not a pass. Retain the evidence basis for the approved sale range.
- Approvals with stage, exact artifact hashes or snapshot identity, relevant dimensions/fields/material, user's decision, timestamp, and conversation reference or retained approval text. A proposed default, agent review, or silence is not an approval.
- Deliberate mutation intent and saved operation key where supported; request fingerprint, resulting remote IDs, response receipt, and verification result. Keep credentials out of records.

Write a checkpoint after each durable result and before returning for human review. A small decision index should link settled choices to their evidence and list unresolved questions. This borrows Wayfinder's named decisions and context pointers; normal product runs do not need tracker tickets.

## Resume and uncertain writes

Read the record and inspect affected local/remote state before continuing. Check current artifact hashes and application revisions against the approved snapshots. Resume the first incomplete valid stage rather than reconstructing completed output.

DecalFlow retries reuse the saved operation key and exact inputs. Changed inputs need a new operation. Pending jobs resume by returned job ID.

Etsy writes have no assumed idempotency key. Persist intent before creating a draft or uploading an image and save returned IDs immediately. After an uncertain result, query the shop/listing/images and reconcile against the saved request and snapshot before retrying. If identity cannot be established, leave the stage blocked for review instead of risking a duplicate or deleting an uncertain resource. Do not overwrite unrelated remote edits.

## Approval validity

| Change | Required reconsideration |
|---|---|
| Selected design option or combination | Record a new selection; reopen design/Piece review and mark affected production evidence stale. Reuse valid selection evidence on resume; retain unselected options as history |
| Reference image, font, font features, or lettering | Affected font-match evidence and visual review; reconsider scoped substitution/fallback decisions and downstream artwork approvals |
| Artwork geometry, font, field layout, or Cut Group/Piece definition | Design/Piece review; new immutable design version; affected size calculations, endpoint tests, assets, and mapping |
| Material or production arrangement/settings that affect results | Fit and affected physical qualification |
| Fitting rectangles, shared scales, tracking, review thresholds, or new sizing policy | Apply the [production contract change scope](../../../references/decalflow-production-contract.md#retention-and-change-scope) and mark affected evidence stale |
| Allowed personalization inputs | Field validation, representative extremes, size calculations and affected qualification/assets |
| Test endpoint or offered width | Fit and qualification coverage; size graphics and inventory |
| Image content, crop, or upload order | Image review of the changed set |
| Listing copy, prices, or inventory | Draft readback and mapping verification; reopen other gates only if production facts changed |

Preserve old evidence as history; mark affected downstream state stale and state why. Approval remains valid only for its recorded scope. Reuse unrelated valid approvals. On resume, apply the [production contract](../../../references/decalflow-production-contract.md) to changed policy, generated preparations and retained artifacts.
