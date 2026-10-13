---
name: decalflow
description: Register reviewed decal designs and Etsy listing mappings in local DecalFlow, prepare saved orders, retain reviewed SVG exports, and hand an exact export to Inkcut. Use for DecalFlow production automation or as the handoff from decal design and listing skills.
---

# DecalFlow workflow

Use the DecalFlow CLI as the application boundary. The local application owns
validation, revisions, records and retained exports. Keep source artwork unchanged.

## Discover the installed contract

Use the user's DecalFlow checkout; the current installation is
`/Users/shad/src/decalflow`. Read `docs/implementation/local-agent-automation-usage.md`
and the CLI help there before constructing commands. Use the repository's pinned
Node version and pnpm script. Resolve schema examples from that checkout rather
than reconstructing request bodies from memory.

Check service status. If unavailable, report the documented local startup command.
Keep local session credentials out of command arguments, manifests and output.
Use CLI commands for persistence; do not edit the database or reference fixtures.

## Register a reviewed design

1. Inspect the actual artwork and its visual/vector review. Read
   [finished artwork sizing](../../references/artwork-sizing.md). Choose a stable
   design key and explicit immutable version. Requested width measures visible
   artwork, separately from the artboard.
2. Build a package in a separate output directory using the installed package
   schema and examples. Include exact asset hashes, explicit units, object IDs,
   Piece/Cut Group membership and authored alignment. Keep one copy's alignment
   distinct from every other copy. Use `fixed-outlines` for outlined artwork.
   Outlined sample names are fixed artwork; editable personalization requires a
   supported template package with declared fields, bindings and exact fonts.
3. Run the import dry-run and inspect its measured bounds and validation report.
   Fix unsupported content explicitly; do not drop shapes or scale from page
   dimensions to make validation pass. Preserve the original file hashes.
4. When registration is within the requested workflow, import with a retained
   operation key. Record the returned design identity, version and package hash.
   A retry reuses its original key and input; changed content gets an explicit
   new version. Import does not establish physical cut qualification.
5. Inspect or create the Product using an explicit definition. Associate an Etsy
   listing only when requested and its exact shop/listing identity and purchased
   option values are known. Dry-run catalog mutations first. Reuse existing
   Product/mapping IDs and expected revisions instead of creating duplicates.

Store results under a `decalflow` object in the existing `listing.json` or design
delivery manifest. Preserve unrelated fields. Record package path/hash, immutable
design identity/version, Product/mapping IDs and revisions, operation keys, and
paths to command-result files. Keep registration status separate from completion
of listing images. Publishing to Etsy is a separate task.

## Prepare and export

For saved Orders, inspect eligibility, item revisions and selected copy counts.
Sync remains manual. Report missing or ambiguous personalization with the buyer's
retained text. Use the separate correction command with a reason and explicit
confirmation only when supported by the user's instructions or verified values.
Preparation itself does not confirm personalization. Keep canceled Items out of
production; use the UI when a case needs manual review.

Prepare through the CLI, retain job IDs, and resume a timed-out job by ID. Inspect
the resulting geometry and arrangement preview: wording, finished-artwork width,
holes, alignment groups, individual weed borders, copy counts, material width
and feed orientation. Record digital review as an agent review within the user's
authorized task; do not claim a human or physical review took place.

Capture the exact reviewed snapshot in the requested piece or arranged-sheet
mode. If inputs change, review again. Download retained SVGs/manifests and verify
the reported hashes. Record preparation, review and export IDs with the operation
results so a retry resumes without producing duplicate exports.

## Hand off to Inkcut

Select the exact retained SVG explicitly when an export contains several files.
Use the CLI handoff command and report its actual state. `launched` does not prove
that Inkcut loaded the file; an acknowledgment does not prove physical size or
successful cutting. For an active or unverified Inkcut instance, return the exact
file and manual-open instructions. Preserve the current job and device settings.

Cutter start and dispatch remain operator actions. Completion means the requested
registration/export/handoff has evidence, original hashes still match, and any
review blocker or unverified import is stated in the result.
