# ADR 0013 — Built-in furniture fitted wall to wall

- Status: accepted · Date: 2026-10-12
- Trigger: owner 2026-10-12 - "make the furniture fit wall to wall as it should (e.g. the matrimonial bedroom dressing)".

## Problem
The ADR 0012 re-dimensioning moved each piece with its nearest wall, so fitted joinery whose room got longer
stopped short of the far wall: the bedroom-2 dressing by 35 cm, other built-ins by 0.7-6 cm (the earlier fit
left 1 cm "scribe" gaps at the kitchen ends and the tub).

## Rule
Built-in pieces (wardrobes, kitchen wall / tall units, tub, wall-hung bath cabinet, wallpapers) cover their wall
exactly: from wall to wall, or to the end of the wall they stand against / the next built-in / a window. No gap.
Storage modules follow: an end that grows by >= 20 cm gets its own module (single door hinged at the wall end,
empty interior); a smaller change widens the end module. Free-standing pieces, pieces ending at an open room
boundary (living wardrobe / bookcases at the hall opening) and centred pieces (TV consoles, slat panels) are left.

## Changes (`scripts/fit_wall_to_wall_2026_10_12.py`, applied to V1, DEV, D1-D5; V2-V13 regenerated)
| Piece | Before → after |
|---|---|
| wardrobe-master-suite-1 (dressing) | 1.60 → 1.955 (y 2.10 … 4.055, bath-2 wall to dressing-door wall); new 0.348 door module m3 at the bath end; top LED strip follows |
| wardrobe-master-suite-2 | 1.80 → 1.85 (to the end of the bath-2 wall), m1 +5 cm; top LED strip follows |
| wardrobe-bedroom-1-1 | 1.80 → 1.85 (to the bath-1 corner), m3 +5 cm |
| wall-cabinet-kitchen-1/2, tall-cabinet-kitchen-1 (D3: pantry-kitchen-1) | run x 0.45 … 4.945 with no gaps (wall units 3.795, tall unit 0.70 / pantry 0.85) |
| D5.wall-cabinet-kitchen-1 | 3.54 → 3.795 (x 0.45 … 4.245, up to its fridge), new 0.225 flap module |
| bathtub-master-bathroom-1 | 1.705 → 1.725 (DEV 1.70 → 1.725) |
| tall-cabinet-master-bathroom-1 | 2 cm down to the wall |
| wallpaper-master-suite-1 / wallpaper-living-1 | to wardrobe-master-suite-2 / to window W1 |
| DEV.wardrobe-living-1 | up to facade A (+6.3 cm) |
| D4/D5 wardrobe-hall-2 | to the end of the hall wall (y 6.37): new module 0.287 / 0.237 |

Validator: same 16 pre-existing warnings, no new ones.
