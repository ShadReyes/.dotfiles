# Shop price ladder

Use this owner-approved USD ladder for new launches unless the user supplies a
product-specific override. The same prices apply to the retained black and white
options. This policy supersedes copied listing prices.

| Offered width | Price (USD) |
|---|---:|
| 12 inches | $29.99 |
| 15 inches | $33.99 |
| 17 inches | $37.99 |
| 20 inches | $41.99 |
| 23 inches | $45.99 |
| 25 inches | $49.99 |
| 28 inches | $53.99 |
| 30 inches | $57.99 |
| 36 inches | $63.99 |
| 48 inches | $75.99 |

## Filter and add the maximum

1. Use the final qualified minimum and the production-fit maximum established by
   launch stage 2, including the 48-inch cap. Keep raw calculated limits separate.
2. Retain only ladder widths inside that inclusive range, with their exact prices.
3. Set the whole-inch maximum rung to `floor(finalMaximumInches)`. Rounding down
   keeps the offered width within material and production constraints. If this
   width is inside the qualified range and is absent from the retained ladder,
   add it. An existing rung keeps its stated price and appears only once.
4. Price an added rung using the two original ladder entries that bracket its
   width, including entries excluded from the product's offered range. Interpolate
   linearly against logarithmic width:

   `rawPrice = lowerPrice + (upperPrice - lowerPrice) * ln(width / lowerWidth) / ln(upperWidth / lowerWidth)`

   Round to the nearest price ending in `.99`, with exact ties rounded upward:

   `price = floor(rawPrice - 0.99 + 0.5) + 0.99`

   Keep the result within the two anchor prices and store exact integer cents.
   This is a consistent interpolation rule for the owner's ladder, not a claim
   about market demand or production cost.
5. Sort by width and verify unique widths, nondecreasing prices, `.99` endings,
   currency, range containment, and actual production fit. Pricing never expands
   the qualified range. Resolve an empty set or a width outside the original
   ladder's 12–48 inch interpolation domain with the user instead of extrapolating.

For example, a fit-qualified 29-inch maximum adds a 29-inch / $55.99 option between
28 inches / $53.99 and 30 inches / $57.99. A 29.7-inch maximum also yields a
29-inch rung, subject to fit; it does not authorize a 30-inch offer. A maximum of
28.8 inches yields the existing 28-inch / $53.99 rung without a duplicate.

Record the ladder, qualified endpoints, rounded maximum, interpolation anchors,
raw price, final cents, and exact offered options in `pricing/price-plan.json`.
Link its path/hash from `launch.json`. Retain the user's price approval separately
from pending physical qualification, image approval, or remote inventory writes.
