# The Decal Company template reference

Inspected on 2026-10-05: filesystem inventory, all three listing PNGs, PNG dimensions, brand instructions, and example SVG structure. Native Affinity documents, layer IDs, installed fonts, and export behavior remain unverified. Recheck assets on each run; this map identifies candidates, not guaranteed matching revisions.

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
| Installation guide | `ListingGraphics/InstallationGuide.png` | `SourceFiles/InstallationGuide.af` | None identified | 4000 × 4000 |

`SourceFiles/mirror.png` is a possible linked resource; inspect native resource metadata before deciding where it is used. Other `.af` files in that directory serve branding or other purposes and are not automatically listing templates.

The About and Size Guide references use a black arched mirror. Both contain the old design: initials, “Smile. You're on Camera.”, names, and year. About also has three placement boxes and copy claiming three shipped decals. Replace the old artwork and its placement boxes; request the new shipped-piece count and change that count in the About copy.

The Installation Guide contains the old phrase inside its installation photograph. It cannot automatically be copied unchanged for a request to update all listing graphics. Inspect whether that photo is layered; if flattened, create a replacement photo region with blank transfer material and composite the actual design. Preserve the six-step layout and applicable instructions.

Production rule confirmed by the user on 2026-10-06: request only the SVG display color (white, black, or gold) and shipped-piece count. The remaining template text is fixed. Preserve all three size-guide bullets exactly, including the 2–3 inch guidance and 23-inch mirror/20-inch decal example. Retain the `23"` label above the mirror arrow. Preserve the About personalization and crafting copy, the installation instructions, and mirror-not-included disclaimers. This user-confirmed adaptation rule takes precedence over older guidance that treated template examples as unconfirmed listing facts. Consult `BRAND.md` for visual brand rules without editing that protected file.

One-piece placement rule confirmed by the user on 2026-10-06: unless the design calls for another placement, put the complete one-piece design at the top of the size-guide mirror, above the sizing arrow. Shift the arrow down when necessary and keep its `23"` label above it. Preserve the artwork proportions and all fixed template text. Apply this rule after the shipped-piece count is confirmed.

Suggested order: `01-hero`, `02-about-this-design`, `03-size-guide`, `04-installation-guide`. Use explicit image extensions and preserve template dimensions. Choose hero dimensions for the requested crop and export quality; verify current marketplace guidance if claiming platform compliance.

## Initial example

Input: `/Users/shad/Downloads/wedding-signs-reference-match-production/02-favorite-people-outlined.svg`.

Observed SVG structure: `viewBox="0 0 520 180"`, canvas `24in × 8.307692in`, no SVG text or image elements. Treat it as supplied outlined artwork, not a live-font source. Inspect its render before placement. Canvas size alone does not establish cut bounds, available sale sizes, shipped piece count, or personalization options.

Suggested first listing slug: `favorite-people`. The example input is for the first run, not a fixed input for future invocations.
