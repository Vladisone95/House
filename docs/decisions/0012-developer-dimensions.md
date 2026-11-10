# ADR 0012 — Shell re-fitted to the developer's dimensioned plan + the sales-sheet areas

- Status: accepted · Date: 2026-10-06
- Sources: `docs/uploads/dimensiuni.jpeg` (developer's top-down C3 plan with room sizes, received
  2026-10-06), the sales-sheet areas (ADR 0001), owner answers 2026-10-06.

## Owner decisions (2026-10-06)
- The printed sizes are **not** clear sizes: they include about one wall thickness. Owner's check: baths
  (1.85 − 0.125) × (2.80 − 0.125) = 4.61 m² = the listed area. So the **sales-sheet areas stay the truth**
  (3 % validator tolerance) and the printed sizes are honoured "minus a wall".
  (A first attempt the same day used the labels as clear sizes - rooms came out up to 15 % too big - and was undone.)
- Balcony: half recessed into the building (loggia), as drawn - replaces fact 10 of ADR 0001.
- Furniture moves with its walls and is then fitted to the new rooms; WCs are placed as on the 2D plan.

## Method
Least-squares fit of the wall coordinates (`scratch fit`, numbers below): every room's area = listed
(weight 0.2 %), every printed size − 12.5 cm (weight 5 cm), wing wall ≈ in line with the living/bedroom-1
wall; the baths pinned to the owner's rule. Result: each printed size is the clear size + 2.5…18.5 cm
(bedroom 2's 3.30 is 2 cm short of its clear 3.32). Walls keep the owner-confirmed thicknesses.

| Room | clear size now (printed) | area (listed) |
|---|---|---|
| Living | 6.115 × 4.33 (6.25 × 4.40) | 26.48 (26.52) |
| Kitchen | 4.495 × 2.55 (4.57 × 2.63) | 11.46 (11.46) |
| Hall | 3.645 × 1.885 + strip by the kitchen wall (3.73 × 2.02) | 7.46 (7.47) |
| Bedroom 1 | 3.425 × 4.51 minus the bath-1 corner (3.45 × 4.57) | 13.99 (14.01) |
| Bath 1 / Bath 2 | 1.725 × 2.675 (1.85 × 2.80) | 4.61 (4.61) |
| Bedroom 2 + dressing | bedroom 3.70 × 3.32 (3.80 × 3.30) + dressing | 17.31 (17.31) |
| Balcony | 3.95 × 1.715 (4.10 × 1.90) | 6.77 (6.76) |
| Usable | | 85.93 (85.99) |

## What changed in the shell (before → after)
- **Facade B is stepped**: kitchen + bedroom 2 keep the outer line (inner x 0.45); the living's wall
  (`ext_facade_b_living`) sits one wall thickness further in (inner x 0.90). The balcony is half inside
  that step (x −1.265 … 0.45, y 6.75 … 10.70).
- Apartment outer size 10.50 × 11.36 → 10.82 × 11.15 (+0.32 towards the party wall, facade A −0.21).
- Hall is a straight corridor 1.885 wide (was an L); hall/dressing wall (`part_suite_top`) is its own wall
  0.485 m nearer the entrance than the kitchen/bedroom-2 wall (new `part_kitchen_bed2`).
- Bath walls towards the bedrooms 1.80 → 1.725 (facts 7, 8); bedroom-1 strip by bath 1 1.22 → 0.785 (fact 11).
- Openings (read off the drawing): W1 4.82-6.22, W2 7.84-9.34 (1.50 wide), balcony door 7.05-8.85, W3 4.375-5.375,
  entrance 7.45-8.45, D_suite 5.355-6.155, D_bedroom1 7.31-8.11, D_bath1 5.195-5.895; D_kitchen keeps 0.60 from
  its wall, D_bath2 keeps 0.70 for the tub; W4 unchanged.
- Fixed points + boiler moved with their rooms; **WCs moved as drawn on the 2D plan**: FX_bath1_wc
  (9.40, 4.33) on the corridor wall by the hall wall, FX_bath2_wc (6.80, 1.515) on the corridor wall by the
  dressing wall (both `confirmed`).

## Furniture
`scripts/migrate_dimensions_2026_10_06.py` moved every piece with its nearest wall, then
`scripts/fit_furniture_2026_10_06.py` fitted V1 (styles V2-V13 regenerated), D1-D5 and DEV:
kitchen run +24.5 cm (base unit 1.745 with a 24.5 cm pull-out, worktop / backsplash / wall units / LED to the
tall unit), dining table 90 → 80 deep; bath-1 shower 120 → 110 (washer + shower side by side), WCs and their
accessories on the new points, tub 1.705 wall to wall; curtains follow the moved windows; living desk 1.55 long and
17 cm off facade A (window W1 now ends at the desk corner); hall key shelf to the wall by the entrance (its wall
stub is gone); bedroom-2 AC over the TV wall (window wall too short for drape + AC); balcony set re-spaced.
Validator: no new warnings in any variant (16 left, all pre-existing; was 42).
