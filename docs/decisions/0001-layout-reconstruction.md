# ADR 0001 — Reconstructing the layout from the developer's render

- Status: accepted (iteration 1) · Date: 2026-10-04
- Sources: sales sheet areas (`docs/reference/developer_plan_C3.jpg`, page
  viennaparkside.ro/apartamente/c3-scb-161/), owner answers in the 2026-10-04 session.

## Problem
The developer publishes only a perspective 3D render and room areas. No dimensions.

## Method
1. **Rectification.** Wall tops lie on one horizontal plane. The four outer corners of that
   plane were picked in the render and a homography mapped them to a rectangle, giving a
   top-down view (`docs/reference/draft_plan_v0_compare.png`, right). The aspect ratio
   (facade A / facade B ≈ 0.95) came from the two vanishing points with an assumed principal
   point (stable 0.93–1.00 across reasonable choices).
2. **Scale from areas.** With partitions read off the rectified image, living, kitchen,
   bedroom 1, bath 1 and hall all implied the same scale (±3 %), validating the reading.
   The bedroom-2 wing was drawn ~0.5 m short in the render; it was sized from areas instead.
3. **Owner corrections** (below) were applied and the remaining free dimensions solved so every
   room matches its listed area (`uv run apartment validate`).

## Owner-confirmed facts (do not change without asking)
| # | Fact | Where in data |
|---|---|---|
| 1 | Clear ceiling height 2.70 m | `levels.ceiling_height` |
| 2 | Exterior walls 30 cm AAC + 15 cm EPS = 45 cm | `wall_types.exterior` |
| 3 | Interior partitions 12.5 cm; walls to neighbours doubled = 25 cm | `wall_types` |
| 4 | Orientation: facade A (living, bedroom 1) WNW ~294°, facade B (balcony, kitchen, bedroom 2) SSW ~204° | `site.plus_y_bearing` |
| 5 | Windows standard: sill 0.90 m, head 2.40 m; balcony door to 2.40 m | `openings_defaults` |
| 6 | Bedroom-2 suite: dressing is open to bedroom 2 (one space, 17.31 m²); only bath 2 is walled; only door inside the suite is bath 2's | rooms `bedroom_2`, `bath_2` |
| 7 | Bath 2 wall towards bedroom 2 = ~~1.80~~ 1.725 m (developer plan 1.85 minus a wall, 2026-10-06, ADR 0012) | `part_bath2_left` |
| 8 | Bath 1 wall towards bedroom 1 = ~~1.80~~ 1.725 m (developer plan 1.85 minus a wall, 2026-10-06, ADR 0012) | `part_bed1_bath1` |
| 9 | Kitchen door: 0.60 m between the door and the wall on the left when entering (room for a 60 cm cabinet) | `D_kitchen` |
| 10 | Balcony starts at the facade-A wall, ends where the kitchen wall begins - 3.95 m clear, half recessed (ADR 0012) | `balcony.polygon` |
| 11 | Bedroom-1 entry corridor runs alongside bath 1 (~~1.22~~ 0.785 m, ADR 0012) | `bedroom_1` polygon |
| 12 | Suite: keep wing wall aligned with living/bedroom-1 wall and respect listed area (v1) - owner noted the dressing zone may be deeper than 60 cm | `corr_wing`, `part_bath2_top` |

## Estimated (to be measured on site)
Window and door widths/positions (except D_kitchen), the exact position of the entrance and
suite doors, corridor-wall thickness (assumed 25 cm), balcony side wall (full height at the
facade-A end, glass railing elsewhere), the floor above having the same balcony.

## Known deviations
- Hall: 7.61 m² vs listed 7.47 m² (+1.9 %), a consequence of facts 8 + 11.
- Usable total 86.13 m² vs 85.99 m² (+0.16 %).
- Dressing cabinet run along the corridor wall is 1.62 m (owner's 3 × 60 cm assumption could
  not be kept together with the listed suite area and wall alignment).

## Change log
- 2026-10-04 — initial reconstruction (v0 → v1), owner review of v0, v1 variants and v2 options.
- 2026-10-06 — **re-fitted to the developer's dimensioned plan** (`docs/uploads/dimensiuni.jpeg`): its sizes
  include ~one wall, the listed areas stay the truth (owner). Facade B stepped, balcony half recessed (fact 10),
  bath walls 1.725 (facts 7 + 8), strip by bath 1 0.785 (fact 11), WCs as on the 2D plan. Details: ADR 0012.
