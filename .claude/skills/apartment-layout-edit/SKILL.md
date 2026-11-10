---
name: apartment-layout-edit
description: Change the apartment's geometry - move/resize walls, rooms, windows, doors, balcony, ceiling height, wall thickness - or apply measurements the owner took on site. Use whenever a dimension, opening or room shape in data/apartment.toml must change.
---

# Editing the apartment layout

The layout lives only in `data/apartment.toml`; the .blend is regenerated from it.

## Procedure
1. **Understand the request in model terms.** Map the owner's words to ids
   (`uv run apartment plan` → open `docs/plan.png`; walls/openings/rooms are labelled).
   "Left wall when entering the kitchen" etc. → work it out on the plan and say which id you mean.
2. **If anything is ambiguous, ask** (AskUserQuestion) and show an image of the options
   (render a variant PNG with `apartment_core.plan2d.render_plan` on a modified copy, open it with
   `cmd //c start "" file.png`). Never guess an owner-facing fact.
3. **Edit consistently.** A wall line is shared by: wall rects, room polygon vertices, opening spans,
   cameras. Grep the old coordinate (e.g. `6.800`) and update every occurrence that belongs to the
   same line. Keep areas matching the listing (validator tolerance 3 %) - if a measured value makes a
   room disagree with the listing, keep the measurement and tell the owner the listing differs.
4. **Validate**: `uv run apartment validate` (the hook does this too) and `uv run pytest`.
   Tests encode owner-confirmed facts; if one must change, ask the owner first, then update the test.
5. **Show**: `uv run apartment plan` and open `docs/plan.png`.
6. **Rebuild + verify**: `uv run apartment build`, then
   `uv run apartment render --views plan,<affected rooms>` and inspect the PNGs.
7. **Record**: set the item's `status` (`confirmed`/`measured`) and append an entry to
   `docs/decisions/0001-layout-reconstruction.md` (date, what changed, source).

## Measured values from the owner
When the owner provides tape measurements (clear wall-to-wall), they override estimates.
Convert to model coordinates from the nearest fixed reference (usually a facade inner face:
facade A inner face y = 10.913, facade B inner face x = 0.450) and propagate.

## Things that are easy to get wrong
- Wall thickness is the rect's short side; changing a wall type means changing its rect.
- Opening `span` is along the wall's long axis (X for horizontal walls, Y for vertical walls).
- The balcony is aligned with the living room (owner rule): if the living depth changes, move
  the balcony polygon/slab/side wall too.
- Hall and living are open to each other (no wall) - by design.
