# ADR 0004 — Door & window symbols in the top-down plan

- Status: accepted · Date: 2026-10-04

## Context
From above, the wall over every opening (lintel from door/window head up to the 2.70 m
ceiling) hides it, so the Blender top-down plan showed no doors or windows. The owner asked to
see them in the 2D view.

## Decision
- Doors get two optional data fields in `data/apartment.toml`: `hinge = "start" | "end"`
  (end of `span` with the lower / higher coordinate) and `swing = "+" | "-"` (side of the wall
  the leaf opens to: towards +X/+Y or −X/−Y). The validator requires both or neither, and only
  on `kind = "door"` (issue code `door_swing`).
- `apartment_core.geometry.door_swing()` computes the leaf (door drawn 90° open) and swing arc;
  both `plan2d.py` (docs/plan.png) and `build_scene.py` use it.
- Blender: one `PLAN_<opening>` mesh per opening in the **Annotations** collection, 2 cm above
  the wall tops: white cut-out over the wall + blue glazing/face lines (windows, balcony door)
  or orange leaf + arc (doors). Emission materials (look the same at any sun time),
  `visible_shadow = False`. Annotations are shown by "Top-down plan" and the `plan` render,
  hidden in room views, so the 3D views are unchanged.

## Door swings (status: estimated)
Proposed convention, accepted by the owner on 2026-10-04 without a site check: every door opens
into the room it serves, hinge next to the nearest wall. Entrance opens into the hall.

| Door | hinge | swing | Meaning |
|---|---|---|---|
| D_entrance | start | + | into hall, hinge on the bedroom-2 corridor side |
| D_kitchen | end | − | into kitchen, hinge towards the living room (keeps the 60 cm cabinet spot free) |
| D_suite | end | − | into bedroom 2, hinge towards the corridor wall |
| D_bath2 | start | − | into bath 2, hinge near its left wall |
| D_bedroom1 | start | + | into bedroom 1, hinge near the living-room wall |
| D_bath1 | start | + | into bath 1, hinge near the entrance wall |

Verify on site; changing one is a one-line edit + rebuild.
