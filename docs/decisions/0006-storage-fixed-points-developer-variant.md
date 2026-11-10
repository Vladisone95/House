# ADR 0006 — Openable storage, fixed service points, developer variant (DEV)

- Status: accepted · Date: 2026-10-04
- Builds on ADR 0004 (door symbols) and 0005 (variants + ids).

## Context
The owner asked for:
1. A variant that recreates the developer's furnished render 1:1 ("Real estate developer
   schema"), tweaked only where the image is unclear (e.g. hidden WCs).
2. Every *storage* piece (wardrobes, cabinets, drawers...) to be interactive everywhere in the
   project: open doors / drawers and design the interior (shelves, drawers, rails), possibly
   left empty at first.
3. Things the building forces (entrance door, water + drains under sinks, WC stacks, washing-
   machine connection "M.S.R.", cooker-hood vent) enforced in every variant and shown on the
   2D plan of the Apartment tab; doors between rooms drawn as red lines.

## Decision

### Fixed service points — `[[fixed_points]]` in `data/apartment.toml`
Shell data (shared by all variants): `id, kind (water|wc|washer|hood|shower), label, room,
position [x, y], serves [types], radius, status, note`. A piece *serves* a point if its full type
or the type's last word is listed (`double-sink` → `sink`). Validator (`validate_variants`):
- **error `fixed_point`**: a piece of a served type that is not on a matching point (its
  footprint further than `radius` from it, or in another room) — e.g. a sink moved away from the
  pipes. Any sink type counts ("even if they are of different types").
- **warning `fixed_point_unused`**: a non-empty variant leaves a point unused (empty variants
  are not nagged).
- Shell checks (`validate`): unique ids, known room, point inside its room.
The entrance door is `fixed = true` on the opening (drawn dark red, labelled "ENTRANCE (fixed)").
All positions are read from the developer render → `status = "estimated"` until measured.

### Storage pieces
A type whose last word is in `STORAGE_WORDS` (wardrobe, cabinet, nightstand, dresser, console,
vanity, sideboard, bookcase, chest, cupboard, closet, drawers, unit, pantry) is storage. Optional
data per piece:

```toml
[items.storage]
plinth = 0.08            # default: 8 cm on the floor, 0 when hung
handle_color = "#c8a165"
interior_color = ""      # default: the piece colour
[[items.storage.modules]]           # left -> right as seen standing in front
width = 1.0
front = "doors"                     # door-left|door-right|doors|drawer|drawers|flap|panel|open
# drawers = 3                       # with front = "drawers"
# fronts = [{kind="drawer", height=0.18}, {kind="doors"}]   # stacked top -> bottom
finish = "glass"                    # matte|gloss|wood|glass|mirror
front_color = "#906c43"
interior = [{kind="shelf", z=0.4}, {kind="rail", z=1.8}, {kind="drawer", z=0.1, height=0.18},
            {kind="divider", x=0.45}]   # heights from the piece's underside
```
Without modules, pieces get automatic ones (doors ≤ 60 cm; drawers for nightstands/dressers/
consoles). Interiors start empty (owner: organise them once a variant is liked).
`furniture.storage_layout()` (pure Python, tested) returns the carcass, the moving fronts
(pivot + motion `hinge|flap|slide|none` + amount) and the fittings. Addresses for the owner:
module `DEV.wardrobe-living-1/m2`, fitting `DEV.wardrobe-living-1/m2/shelf-1`; m1 = leftmost
seen from the front. Validator code `storage`: module widths must add up to the piece width,
known fronts/finishes/fittings, fittings inside the piece, `[storage]` only on storage types.

### Blender
- Storage pieces: `FURN_<id>` = carcass (keeps `furniture_id`), children `FRONT_<id>_<m-name>`
  with their origin on the hinge (props `part_id, module, motion, amount, pivot`) and
  `INT_<id>_<m>_<fitting>`. Glass fronts are tinted and see-through.
- Panel **Storage (open / look inside)**: Open/close selected, Open all / Close all, Open slider,
  *Show doors & drawer fronts* toggle (hide all fronts to see every interior), selected
  module/part id + Copy module id / Copy part id. Show IDs adds blue m1, m2... tags on open pieces.
- Plan symbols: doors between rooms red (leaf + swing + line across the opening), entrance dark
  red + label; fixed points = coloured dot + tolerance ring + label (SINK, WC, MSR, HOOD, SHOWER,
  BATH) in the Annotations collection, so the Top-down plan shows them. `docs/plan.png` and the
  variant plans show the same, plus storage module divisions.
- New simple shapes: corner sofa (L, `mirror = true` flips the chaise), round tables, toilet,
  bathtub, shower, sink / double sink, washing machine, fridge, oven, cooktop, cooker hood, TV,
  slat panel, plant, mirror.

### Variant DEV — "Real estate developer schema"
`data/variants/DEV.toml`, 51 pieces, colours sampled from the render, positions read off a
rectified render (homography of the wall-top plane + parallax to the floor) and snapped to our
walls. Notes on pieces mark guesses: the bath-1 WC (hidden in the render), the oven position
under the "M.S.V." label, the cooker hood (not drawn), the hall slat panel.

## Consequences
- A sink/WC/washing machine/hood can only move together with its fixed point (shell change,
  owner decision) — variants cannot silently relocate plumbing.
- Interior design is data: "3 shelves in DEV.wardrobe-living-1/m2" → edit `interior` → rebuild.
  An in-Blender editor that writes back to the TOML can come later.
- Room cameras for living and bedroom 2 moved 0.55 m off the new wardrobes (shell `camera`).

## Owner answers (2026-10-04, after the first DEV build)
| Question | Answer | Change |
|---|---|---|
| Bath-1 WC (hidden in the render) | on the wall towards the building corridor, facing the shower | `FX_bath1_wc` → (9.650, 4.620), status confirmed; `DEV.toilet-bathroom-1-1` moved |
| Oven vs dishwasher (M.S.V.) | side by side under the worktop | kept, note updated |
| Bath-2 door hit the 70 cm tub | move the door 10 cm | `D_bath2` span 4.839-5.539 → 4.939-5.639 (still estimated) |
| Hall slat panel | keep the small panel | kept |

## Change log
- 2026-10-04 — owner: kitchen table pushed against the bedroom-2 wall; `DEV.chair-kitchen-3` and
  `-4` (the wall side) removed (ids retired, never reused).
- 2026-10-04 — owner: lights in DEV. New *light fixtures* (type ends in light | lamp | spotlight |
  sconce): a glowing fixture + a real Blender light (child `LIGHT_<id>`, prop `furniture_light`),
  default per type (ceiling = 60 W area disk, pendant = 40 W point, spot = 20 W spot, lamps 25 W;
  warm white ~3000 K), optional `[items.light]` (kind, watts, color, size, spot_angle). Panel:
  *Lights on* toggle next to Show IDs. Renders: `--lights auto|on|off`, auto = on when the sun is
  below 8 deg. DEV has a ceiling light per room (2 in living, hall, suite), a pendant over the
  table and one on the balcony - none are in the developer render, all `draft`.
