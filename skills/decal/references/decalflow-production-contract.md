# DecalFlow production contract

This reference owns the operational rules shared by decal workflows. Read the
relevant sections before authoring, sizing, listing, preparing, or exporting a
DecalFlow design. Workflow skills own their task steps and evidence locations.

## Installed schema and service

Use the running installation's validated schema and supported application
operations. A newer skill or checkout does not prove service deployment. In a
DecalFlow checkout, consult `packages/domain/src/design-package.ts`,
`packages/domain/src/fitting.ts`, and
`docs/implementation/local-agent-automation-usage.md` for exact types, limits,
commands and acceptance endpoints. Do not reconstruct payloads from this guide.
If the installation cannot support a required rule, report the mismatch before
production; do not silently flatten a package or substitute another policy.

## Width and geometry

New preparations use `widest-cut-group-v1`: ordered width is the measured artwork
width of the widest individual Cut Group (one shipped Piece). Resolve authored
membership first; disconnected letters are not separate Pieces by default.
Report each Piece's width and the assembled union separately. Assembly spacing
can make assembled width larger than offered width. One-Piece widths coincide.
Page dimensions, margins, weed borders and production packing do not establish
artwork width or change membership. Explicit legacy `artwork` or `layout` width
requests are rejected for new preparations.

Apply local fitting first, then one uniform whole-design scale to the ordered
width. Use the compiler result; do not resize production Pieces independently.
Retain `sizing.policy`, finalScale, widest/per-Piece and assembled measurements,
and verify final exported contours. The width tolerance is 0.002 mm. Preserve
calculation precision and distinguish digital verification from physical tests.
Material and machine checks still inspect all Pieces and the arrangement.

For a requested assembled or element width, retain the stated reference and
convert explicitly before preparing. Listing options use the offered width
basis; label assembled dimensions separately when different and place arrows on
the geometry measured. A size-guide example does not establish a sale option.

## Editable fields and fitting

Outlined sample text is fixed artwork. Editable personalization requires a
supported template, declared fields/bindings and exact retained fonts. Freeform
requests do not change outlines or substitute for bound Order values.

Fitting is opt-in per binding. Author tracking, a rectangle in global template
coordinates, maximum reduction, final minimum height in millimeters, and an
optional shared-scale group using the installed schema. Rectangles scale with
the design. Maximum reduction is a fraction from zero to less than one. These
are design-review thresholds, not proof of physical cuttability. Two bindings
of one field may have different rectangles.

Independent bindings shrink as needed. A shared group uses the greatest required
reduction for every member, preserving unequal authored font-size ratios.
Tracking scales with glyphs about the anchor; baselines, connectors and fixed
artwork retain authored positions locally. Final uniform sizing can enlarge
short-value artwork. Review final contours and holes against scaled rectangles,
not only factors or bounding boxes.

Valid geometry can continue beyond a reduction threshold with measured warnings;
impossible containment reports actual overflow. Preserve glyph proportions and
content. Substitution, warping, clipping, truncation and implicit wrapping are
not fitting options. Missing fonts/glyphs and invalid geometry fail. Fitting
does not implement unsupported typography or waive material/machine gates.

## Warning acceptance and export

Show structured designWarnings, including affected binding, measured dimensions,
threshold and reason, to the Shop Operator. The compatibility warnings list
mirrors their message strings; it is not a separate approval record.

Export of a warned preparation requires explicit Shop Operator acceptance for
that exact preparation ID and result hash through the Cutting UI or a documented
application endpoint. Agent review, general design approval, Product Save and
local manifests do not satisfy acceptance. Discover the installed operation;
do not invent a CLI command. Retain and retrieve application acceptance evidence
before capture. Every new warned preparation needs its own acceptance, even if
its output bytes match. Acceptance cannot waive invalid geometry or machine and
material limits.

Capture the exact reviewed snapshot and verify retained export hashes. Record
package/assets, input values, local/final factors, measurements, structured
warnings, preparation/result identity, review/export IDs and acceptance receipts.

## Seller package and Order handoff

Choose outlined SVG for fixed one-Piece artwork. SVG ingestion creates one Cut
Group. To retain multiple Pieces, alignment or editable bindings, upload a
validated structured JSON bundle containing manifest and base64 assets, using
the installed portal schema and limits. A package directory is not an upload.
Preserve units, object/Cut Group identities, alignment, asset hashes and bindings.
General editor live text is not automatically a supported template.

Review displayed policy and preview, explicitly Save, then reload and verify
retained Piece/alignment and binding policy. Preview alone is not persistence.
When Order verification is in scope, save actual field values, prepare the
retained Item, and verify the retained package, values, geometry and warning gate
through export. Report incomplete checks instead of treating upload as proof of
the complete flow.

## Retention and change scope

Historical preparations and exports retain their original bytes and meaning.
Product changes do not rewrite retained Order packages or prior artifacts.
New preparation of an existing design uses the current width policy. Changed
artwork or fitting policy needs a new design version and affected review; changed
Item inputs need a new preparation and review. Preserve old evidence as history.

A software upgrade does not opt existing bindings into fitting. Fixed-sample
approval does not approve an editable counterpart. Keep qualification tied to
its exact artwork, inputs and tested range; reconsider affected design, size,
physical and listing evidence when geometry or policy changes. Reuse unrelated
valid approvals. Review historical listing claims before changing them.
