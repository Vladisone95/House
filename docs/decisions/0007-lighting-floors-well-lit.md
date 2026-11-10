# ADR 0007 — LED lighting scheme, floor finishes, "Well lit", ceiling fix

- Status: accepted · Date: 2026-10-04

## Context
Owner: a *Well lit* sun button (summer, most light, to see the rooms well); more transparent
windows; modern LED lights in all rooms (strips, different types and sizes, biggest in the living
room, stylish choices), switchable with *Lights on*; parquet and ceramic tiles as in the design,
with true tile sizes and colours.

## Decision
- **Well lit** (Sun study panel): 21 June at the time `daylight.brightest_time()` finds - the
  sum over all facade glazing of direct sun (cosine of incidence on vertical glass) + a sky share.
  Result 16:20: sun at az 256 / el 47 on both facades (SSW 204 and WNW 294). Also sky × 1.5.
- **Glass**: alpha 0.12 → 0.04, near-white tint; balcony railing glass 0.25 → 0.12.
- **Lights as furniture** (ADR 0006 light fixtures) gained LED types, defaults in
  `furniture.default_light()`: `led-strip` (rectangle light, 15 W/m, `aim = "down" | "up"`),
  `ring-pendant-light` / `ring-ceiling-light` (glowing ring, disk light the ring's size),
  `linear-pendant-light` (bar + rectangle light), `recessed-spotlight` (flush, 50 deg spot).
  *Lights on* also stops the fixtures' diffusers glowing.
- **DEV lighting scheme** (warm white ~3000 K, cooler over worktop / vanities):
  living - 100 cm LED ring over the coffee table, cove strip on the wardrobe top washing the
  ceiling, recessed wall-washer along the window wall, reading floor lamp; kitchen - linear pendant
  over the table, recessed LED profile over the worktop; hall - 4 recessed downlights; bedroom 1 -
  flush panel, LED grazing the slat wall, bedside lamp; baths - IP downlights + LED bar over each
  vanity; suite - 60 cm flush ring + cove strips on both wardrobes; balcony - flush light.
- **Floor finishes** are data: `[finishes.<name>]` in apartment.toml (kind parquet|tiles, size,
  colours, joint, direction, roughness), read off the rectified developer render: rustic oak
  planks 1.20 × 0.19 m along facade A; speckled beige porcelain 60 × 60 cm (hall, kitchen, baths);
  light outdoor porcelain 60 × 60 (balcony). Built as procedural Blender materials (brick texture
  in true metres, two-tone planks + grain / speckle, joint bump). Validator code `finish`.

## Bug fixed
The ceiling slab was solidified *downwards* (2.45-2.70 m) because of a negative thickness - the
rooms showed 25 cm too low, ceiling lights sat inside the slab and 2.6 m wardrobes poked through.
`slab_from_cells` now uses `abs(thickness)` with the sign as direction: ceiling 2.70-2.95 m.
Renders before 2026-10-04 (this fix) had a 2.45 m visual ceiling.

## Change log
- 2026-10-04 — retired DEV ids (replaced by the scheme): ceiling-light-living-1/2, -kitchen-1,
  -hall-1/2, -bathroom-1-1, -master-suite-1/2, -master-bathroom-1, pendant-light-kitchen-1.
- 2026-10-04 — owner: more bathroom light + mirrors in front of the sinks. Added
  `DEV.mirror-bathroom-1-1`, `DEV.mirror-master-bathroom-1` (under the existing LED bars),
  square 45 cm LED ceiling panels (`led-panel-light`, 90 W) in both baths, bath downlights 15 → 30 W
  with a 70 deg beam. Fresh builds start with *Lights on*. One sphere reflection probe per room
  (`PROBE_<room>`) so EEVEE mirrors reflect the room instead of black patches.
