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

The About and Size Guide references use a black arched mirror. Both contain the old design: initials, “Smile. You're on Camera.”, names, and year. About also has three placement boxes and copy claiming three shipped decals. Replace the old artwork and its placement boxes; request the new shipped-piece count and change that count in the About copy.

Installation guide policy confirmed on 2026-10-11: use the approved universal 3:4 portrait, eight-step guide with the dotted backing cut line in step 4. Its canonical paths are listed above. Reference this shared PNG as upload image 4 in every listing; do not adapt its artwork or copy its native source, export, or supporting assets into production listings. Earlier guides under `Design Assets/Archived/Installation Guides` are deprecated. Recheck the canonical asset and current brand instructions on each run.

Production rule confirmed by the user on 2026-10-06: request only the SVG display color (white, black, or gold) and shipped-piece count. The remaining template text is fixed. Preserve all three size-guide bullets exactly, including the 2–3 inch guidance and 23-inch mirror/20-inch decal example. Retain the `23"` label above the mirror arrow. Preserve the About personalization and crafting copy, the installation instructions, and mirror-not-included disclaimers. This user-confirmed adaptation rule takes precedence over older guidance that treated template examples as unconfirmed listing facts. Consult `BRAND.md` for visual brand rules without editing that protected file.

Mirror placement rule clarified by the user on 2026-10-11: place the sign design toward the top of the mirror in both About and Size Guide graphics, with matching relative position and scale. Use another arrangement when confirmed separate pieces, the design construction, or explicit user instructions require it. Follow the placement and clearance checks in the main skill. Placement does not confirm the shipped-piece count.

Suggested order: `01-hero`, `02-about-this-design`, `03-size-guide`, `04-installation-guide`. Images 1–3 are product-specific exports; image 4 is a reference to the shared installation PNG. Use explicit image extensions and preserve template dimensions. Use [shared Etsy guidance](../../../references/etsy-listing-guidance.md) for new hero dimensions and first-image eligibility. Keep generated scenes in supporting roles; reserve image 1 for a suitable first photo and retain the shared installation guide at image 4.

## Initial example

Input: `/Users/shad/Downloads/wedding-signs-reference-match-production/02-favorite-people-outlined.svg`.

Observed SVG structure: `viewBox="0 0 520 180"`, canvas `24in × 8.307692in`, no SVG text or image elements. Treat it as supplied outlined artwork, not a live-font source. Inspect its render before placement. Canvas size alone does not establish cut bounds, available sale sizes, shipped piece count, or personalization options.

Suggested first listing slug: `favorite-people`. The example input is for the first run, not a fixed input for future invocations.
