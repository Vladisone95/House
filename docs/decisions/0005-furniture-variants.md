# ADR 0005 — Furniture variants and readable ids

- Status: accepted · Date: 2026-10-04

## Context
The owner wants to (1) refer to every piece of furniture by an id and have Claude change exactly
that piece, (2) toggle the ids on in the 3D view (a simpler 2D id plan is fine, overlaps OK),
(3) keep several furnishing *variants* (placement, colours, number of pieces) and switch between
them quickly **without losing the camera position**. Ids must differ between variants.
The owner asked for ids "as human readable as possible, with what it is and where it is".

## Decision

### Data — one file per variant
`data/variants/<KEY>.toml`, KEY = 1–4 capitals/digits (A, B, C2…). The shell
(`data/apartment.toml`) is shared and never copied. A variant holds `[variant]` (key, name,
description, based_on, optional `wall_color`) and `[[items]]`:

| field | meaning |
|---|---|
| `id` | `<KEY>.<type>-<room-slug>-<n>`, e.g. `A.sofa-living-1`, `B.mirror-master-bathroom-1` |
| `type` | lowercase-hyphen word(s); last word picks the 3D shape (`dining-table` → table) |
| `room` | room id from apartment.toml (`bedroom_2`) — the id uses its slug (`master-suite`) |
| `size` | [width, depth, height] m (width = along the front) |
| `position` | [x, y] centre of the footprint, model metres |
| `rotation` | degrees CCW; 0 = front faces +Y (facade A), 90 = −X, 180 = −Y, 270 = +X |
| `elevation` | underside height (wall cabinets, shelves, mirrors); default 0 |
| `color` | "#rrggbb" (soft parts — mattress, cushions — are drawn lighter) |
| `label`, `note`, `status` | free text; status `draft` → `approved` |

Room slugs (new `slug` field on rooms): living, kitchen, hall, balcony, bedroom-1, bathroom-1,
master-suite (bedroom 2 + dressing), master-bathroom (bath 2).

Why files per variant (not one file with inheritance): a variant is self-contained and
diff-able; adding/removing pieces in one can never affect another; ids stay unique because the
key is part of every id. New variants are explicit copies: `apartment variant new B --from A`
re-keys every id (`A.sofa-living-1` → `B.sofa-living-1`).

### Ids
- Unique across all variants (validator `furniture_id`, error).
- The name part should be `<type>-<room-slug>-<n>`; if a piece changes type/room the validator
  warns (`furniture_id_name`) — rename it then, since the owner reads the id as a description.
- When the owner gives an id without the variant prefix, it refers to the variant shown in
  Blender (or the one being discussed); `furniture.find_item(..., active=)` implements that.

### Checks (`uv run apartment validate`)
Errors: bad key/file name, id format/duplicates, unknown room, size/elevation outside
floor–ceiling, colour format. Warnings: footprint leaves its room, pieces overlap (stacked
pieces and rugs excepted), piece inside a door's swing.

### Blender
- `Furniture` collection → one child per variant (`Variant A`, custom prop `variant_key`) →
  `FURN_<id>` objects (origin = footprint centre at its underside; location/rotation mirror the
  data; props `furniture_id`, `variant`, `type`, `room_id`, `size`, `status`).
- Shapes are simple recognisable blocks from `furniture.item_parts()` (bed, sofa/armchair,
  table/desk, chair/stool, rug; anything else is a box) — pure Python, tested.
- **Switching** (Apartment panel → Furniture variants: ◀ A B C ▶): toggles layer-collection
  visibility (+ `hide_render`) and applies the variant's wall paint. The viewport/camera is never
  touched — verified by `blender/ui_furniture_test.py` (view matrix unchanged).
- **Ids** in 3D: a POST_PIXEL viewport overlay (`apartment_tools/overlay.py`) draws each visible
  piece's id above it; selected piece in yellow; never rendered, always readable, constant size.
  "Copy id" puts the selected piece's id on the clipboard.
- Renders: `uv run apartment render --variant B` → `renders/<time>_B/`.

### 2D id plan
`uv run apartment plan --variant A` → `docs/variants/A.png`: footprints with the front edge
drawn thick, the id on each piece, full id list on the side. Labels may overlap (accepted).

## Consequences
- Furniture is data like the shell: never hand-placed in Blender; edits go to the variant TOML,
  then validate → build → render → look.
- Real 3D models (e.g. Poly Haven) can later replace the block shapes per type without
  changing ids or data.
- Variant A starts empty (owner's choice, 2026-10-04).
