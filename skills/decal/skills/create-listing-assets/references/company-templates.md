# The Decal Company template reference

Initial inspection on 2026-10-05: filesystem inventory, all three listing PNGs, PNG dimensions, brand instructions, and example SVG structure. Native Affinity documents, layer IDs, installed fonts, and export behavior remain unverified. Recheck assets on each run; this map identifies candidates, not guaranteed matching revisions.

## Locations and authority

- Workspace: `/Users/shad/Documents/The Decal Comany` (retain this spelling).
- Protected asset tree: `<workspace>/Design Assets`, including `ListingGraphics`, `SourceFiles`, `EditableSVG`, brand documentation, and logo assets.
- Read `<workspace>/Design Assets/AGENTS.md` and `BRAND.md` before design work. Use them as references without editing them during listing production.
- Default production root: `<workspace>/Production Listings`, a sibling of `Design Assets`. A user-specified separate root takes precedence.
- Protect the supplied product's original file and source folder as well; copy needed files into the listing's `sources/`.

Do not put production folders in `Design Assets`. Do not move brand assets into the skill repository. Keep local paths and mappings here; keep brand rules in the existing `BRAND.md`.

## Template candidates

Paths below are relative to `Design Assets`.

| Output role | Reference export | Native source candidate | Other source candidate | Export dimensions |
|---|---|---|---|---|
| About this design | `ListingGraphics/AboutThisProduct.png` | `SourceFiles/About this Product.af` | `EditableSVG/AboutThisDesign.svg` | 4000 × 4250 |
| Size guide | `ListingGraphics/SizeGuide.png` | `SourceFiles/Size Guide.af` | `EditableSVG/SizeGuide.svg` | 4000 × 4250 |
| Installation guide (shared unchanged) | `ListingGraphics/InstallationGuide.png` | `SourceFiles/InstallationGuide.af` | None | 3000 × 4000 |

`SourceFiles/mirror.png` is a possible linked resource; inspect native resource metadata before deciding where it is used. Other `.af` files in that directory serve branding or other purposes and are not automatically listing templates.

The About and Size Guide references use a black arched mirror. Both contain the old design: initials, “Smile. You're on Camera.”, names, and year. About also has three placement boxes and copy claiming three shipped decals. Replace the old artwork and its placement boxes.

Installation guide policy confirmed on 2026-10-11: use the approved universal 3:4 portrait, eight-step guide with the dotted backing cut line in step 4. Its canonical paths are listed above. Reference this shared PNG as upload image 4 in every listing; do not adapt its artwork or copy its native source, export, or supporting assets into production listings. Earlier guides under `Design Assets/Archived/Installation Guides` are deprecated. Recheck the canonical asset and current brand instructions on each run.

## Intake and approved copy

Production rule confirmed by the user on 2026-10-06: request only these missing details, preferably together:

- SVG display color: white, black, or gold.
- Number of separate pieces the design ships in.

Update only the shipped-piece count in the template copy, with singular/plural agreement where needed. Treat all remaining template text as approved and fixed, including personalization instructions, sizing bullets, measurement examples and disclaimers. Preserve all three size-guide bullets exactly, including the 2–3 inch guidance and 23-inch mirror/20-inch decal example. Retain the `23"` label above the mirror arrow. Preserve the About personalization and crafting copy, installation instructions, and mirror-not-included disclaimers.

Preserve branding and keep approved sizing examples separate from the artwork being replaced. Sizing examples are template content, not sale-option data to collect. Preserve them instead of substituting placeholders or adding questions about sale sizes, available color ranges, personalization policies or included items. Expand the intake and change approved text only when the user explicitly requests changes that need them. This user-confirmed rule takes precedence over older guidance that treated template examples as unconfirmed listing facts. Consult `BRAND.md` for visual brand rules without editing that protected file.

## Mirror placement

Placement rule clarified by the user on 2026-10-11: place the complete sign design toward the top of the mirror in both About and Size Guide graphics. Match its relative position within each mirror rather than using equal page coordinates when mirror sizes or positions differ. Preserve exact artwork proportions and use consistent scale relative to mirror width.

Use another arrangement when confirmed separate pieces, the supplied design, or explicit user instructions require it; record the reason. Placement does not establish the shipped-piece count, which must be confirmed separately.

In the Size Guide, keep the artwork above the sizing arrow and label. Move the arrow and label down together if clearance is needed, keeping the label above the arrow and preserving all measurement text and sizing bullets.

## Upload order

Suggested order: `01-hero`, `02-about-this-design`, `03-size-guide`, `04-installation-guide`, `05-couple-selfie`. Images 1–3 and 5 are product-specific exports; image 4 is a reference to the shared installation PNG. Follow [the couple-selfie procedure](couple-selfie.md) for required image 5 on wedding mirror-decal listings. Use explicit image extensions and preserve template dimensions. Use [shared Etsy guidance](../../../references/etsy-listing-guidance.md) for new hero dimensions and first-image eligibility. Keep generated scenes in supporting roles; reserve image 1 for a suitable first photo and retain the shared installation guide at image 4.

## Initial example

Input: `/Users/shad/Downloads/wedding-signs-reference-match-production/02-favorite-people-outlined.svg`.

Observed SVG structure: `viewBox="0 0 520 180"`, canvas `24in × 8.307692in`, no SVG text or image elements. Treat it as supplied outlined artwork, not a live-font source. Inspect its render before placement. Canvas size alone does not establish cut bounds, available sale sizes, shipped piece count, or personalization options.

Suggested first listing slug: `favorite-people`. The example input is for the first run, not a fixed input for future invocations.
