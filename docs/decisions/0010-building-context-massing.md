# ADR 0010 — Building context: height above the street, gray block, lawn

- Status: accepted · Date: 2026-10-04

## Context
Owner: the apartment is on floor 6; simulate its height, the rest of the building can be a simple gray
block; grass outside to a certain distance (not infinite). Owner chose (2026-10-04): Romanian count
(etaj 6 = parter + 5 floors below), 2 floors above (P+8), lawn about 30 m around the building.

## Decision
- `[building]` in apartment.toml: `storeys_below = 6`, `floors_above = 2`, `grass_margin = 30`,
  `party_extension = 10` (estimated - how far the block continues past the party / corridor walls is
  unknown). Storey = clear height 2.70 + slab 0.25 = 2.95 m, so the street is 17.70 m below this floor.
- Build (`build_building`, collection *Context*): one gray `CONTEXT_building` object = the block below
  (street to the underside of this floor), the neighbours on this floor (beyond the party wall +X and the
  bottom party wall -Y) and the 2 floors above; facades A (+Y) and B (-X) stay the real outside faces.
  `CONTEXT_grass` = a lawn rectangle at street level, the block footprint + 30 m, nothing beyond.
- Context objects follow the add-on's ceiling mode: in plan / overview they are hidden from the camera
  but still cast shadows; room views and window views see them. So sun studies now include the
  building's own shadows.
- The hall camera moved behind the half-open entrance door (eye 7.90, 4.75 -> 8.15, 5.70); the kitchen camera
  moved to the end of the worktop (4.40, 4.20 -> 4.45, 6.05) because the fridge now stands there.

## Not modelled
Lower floors' balconies, the exact building outline, neighbouring buildings and trees.

## Change log
- 2026-10-04 — `trees = 18` in `[building]`: deterministic scatter on the lawn (`geometry.scatter_trees`,
  >= 6 m off the block, 4 m apart, 5.5-9 m tall) built as one `CONTEXT_trees` object.
