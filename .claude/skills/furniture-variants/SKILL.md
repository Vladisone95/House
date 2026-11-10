---
name: furniture-variants
description: Add, move, rotate, resize, recolour or remove furniture by id, and create / compare / switch furniture variants (A, B, C...). Use whenever the owner names a furniture id (e.g. "A.sofa-living-1", "move the bed-master-suite-1"), asks for a new variant or a copy of one, wants different colours / wall paint, or wants to see a variant. Also storage modules / interiors ("shelves in .../m2", open a wardrobe) and fixed service points (sink, WC, MSR, hood).
---

# Furniture variants - working by id

Source of truth: `data/variants/<KEY>.toml` (one file per variant). Schema, conventions and the
reasoning: `docs/decisions/0005-furniture-variants.md`. Never hand-place furniture in Blender.

## Resolve the id first
- Full id `A.sofa-living-1` → variant A, file `data/variants/A.toml`.
- Short id `sofa-living-1` → the variant the owner is looking at (ask if unclear - check
  `scene.apt.variant` via the Blender MCP `get_scene_info` / panel, or ask).
- Unknown id → `uv run apartment variant list` and `uv run apartment plan --variant <KEY>`;
  show the owner the PNG and ask which piece they meant. Never guess.

## Translate the owner's words into data
Model frame: +X along facade A, +Y towards facade A (see CLAUDE.md). The owner thinks in
"left/right/towards the window". Say how you interpreted the direction ("moving it 30 cm towards
the balcony door = −X") and, if ambiguous, ask with an image.
- **move** → change `position` (centre of the footprint). Keep 3 decimals.
- **rotate / turn to face X** → `rotation` (deg CCW): 0 = front faces +Y, 90 = −X, 180 = −Y,
  270 = +X. Rotating 90° swaps the footprint's x/y extents - re-check walls.
- **resize** → `size = [width, depth, height]`, width along the front.
- **hang / raise** → `elevation` (underside height).
- **recolour** → `color = "#rrggbb"`; variant wall paint → `[variant] wall_color`.
- **add** → new `[[items]]` with id `<KEY>.<type>-<room-slug>-<n>`; first free n
  (`furniture.next_id`). Sizes from the `interior-design-standards` skill unless the owner gives them.
- **remove** → delete the `[[items]]` block. Never reuse a removed id for a different piece.
- **moved to another room / type changed** → rename the id to match (validator warns
  `furniture_id_name`) and tell the owner the new id.
- **only this variant** - never edit another variant's file unless asked ("do the same in B").

## New variant / copy
`uv run apartment variant new B --from A --name "Scandi light"` (copy, ids re-keyed) or
`uv run apartment variant new C` (empty). Then edit `data/variants/B.toml`.

## After every change
1. `uv run apartment validate` - no errors. Report warnings to the owner in plain words
   (overlap, outside the room, blocks a door swing) - they may be intended.
2. `uv run apartment plan --variant <KEY>` → look at `docs/variants/<KEY>.png`.
3. `uv run apartment build` then `uv run apartment render --variant <KEY> --views plan,<room>`
   and look at the images before reporting (render-review skill).
4. The owner's open Blender keeps the old file: tell them File → Revert (their variant buttons
   and Show IDs then show the change).
5. Status: new pieces are `draft`; set `approved` only when the owner says so.

## Storage pieces (open / interior) - ADR 0006
- Owner addresses: `<id>/m<k>` (module, m1 = leftmost seen from the front) and
  `<id>/m<k>/<kind>-<n>` (fitting). Resolve with `furniture.find_item` (accepts part paths).
- "3 shelves in DEV.wardrobe-living-1/m2" → that module's `interior = [{kind="shelf", z=...}]`
  (z from the piece's underside; spread evenly unless told). Kinds: shelf, rail, drawer
  (z + height), divider (x from the module's left). Fronts: door-left|door-right|doors|drawer|
  drawers|flap|panel|open; finish matte|gloss|wood|glass|mirror. Module widths must sum to width.
- A piece with no `[items.storage]` gets automatic modules - write them out before editing one.

## Fixed service points
- Sinks (any type), toilets, washing machine, cooktop/cooker hood, shower/bathtub must sit on a
  `[[fixed_points]]` entry of `data/apartment.toml` (validator error `fixed_point`). Never move
  the point to make a layout fit - ask the owner (it is where the pipes/vents are).
