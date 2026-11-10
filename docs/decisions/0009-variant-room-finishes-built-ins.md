# ADR 0009 — Variant room finishes (floor + wall tiles), built-ins (boiler), V1 spa bathrooms

- Status: accepted · Date: 2026-10-04

## Context
Owner (2026-10-04), with the reference photo `docs/uploads/bathroom.jpg` (warm spa bathroom):
in **V1 (Vlad 1)** make both bathrooms match it in colour - floor and wall tiles; one sink per
bathroom, a bowl (vessel) sink on a thick wooden vanity, a mirror with lights all around, a
wall-hung toilet. And in **all variants**: the apartment already has a **180 L boiler**, a big
oval tank above the washing machine, up to the ceiling.

Floors were shell data (one finish per room, all variants) and walls had a single paint colour
per variant, so neither could differ per variant per room.

## Decision
- **Variant room finishes**: a variant file may contain `[rooms.<room id>]` with `floor` and/or
  `walls` = a finish name from `[finishes]` in apartment.toml (+ optional `walls_height`, 0 =
  ceiling). The build adds `FINISH_<KEY>_floor_<room>` (room polygon 4 mm above the shell floor)
  and `FINISH_<KEY>_walls_<room>` (1 cm tile skin inside every wall, door openings left open,
  `geometry.cladding_boxes`) **inside the variant's collection**, so the variant switch shows /
  excludes them with the furniture. Validator code `finish` checks room and finish names.
- **Finish kind `stone`**: large slabs with soft clouding/veining (noise ramp color → color2) and
  thin grout. Wall materials (`MAT_wall_<finish>`) map (x + y, z) so slabs are true size on
  walls in either direction.
- New finishes (owner photo): `wood_look_tiles` - warm walnut wood-look porcelain planks
  120 x 20, along y; `greige_stone` - greige stone-look porcelain slabs 120 x 60, full height.
- **Built-ins** `[[built_ins]]` in apartment.toml: equipment the apartment already has. Same
  fields as a furniture piece; built as `BUILTIN_<id>` in collection *Built-ins* (outside the
  variants, so every variant - A, DEV, V1, future ones - shows it); drawn on every 2D plan.
  Validator `built_in` (room, size, inside the room); furniture running into one in 3D →
  warning `furniture_built_in`.
- **Boiler** `BI_bath1_boiler`: 180 L, Ø 56 cm, from 1.05 m (20 cm above the 85 cm washer) to
  2.65 m, centred over the MSR point against the wall. Owner chose "fill the gap"; the diameter
  is an estimate to measure on site.
- New shapes: `toilet` is now truly wall-hung (rounded bowl from 20 cm, nothing on the floor -
  this also changes how DEV's WCs look; DEV labels already said wall-hung); `vessel-sink` (round
  bowl, brass wall spout); `backlit-mirror` (pill mirror, thin brass frame, glowing LED halo -
  switches with *Lights on*); `boiler` (cylinder with domed ends). Storage `handles = false` =
  push-to-open fronts without handles.

## V1 changes (ids the owner uses)
| Before | After |
|---|---|
| `V1.double-sink-bathroom-1-1` | `V1.vessel-sink-bathroom-1-1` (one bowl) |
| `V1.sink-master-bathroom-1` | `V1.vessel-sink-master-bathroom-1` |
| `V1.mirror-bathroom-1-1`, `V1.mirror-master-bathroom-1` | `V1.backlit-mirror-bathroom-1-1`, `V1.backlit-mirror-master-bathroom-1` |
| `V1.countertop-bathroom-1-1` | removed - the thick vanity is the top |
| `V1.led-strip-bathroom-1-1`, `V1.led-strip-master-bathroom-1` | removed - replaced by the mirror halo |
| — | `V1.shelf-bathroom-1-1`, `V1.shelf-master-bathroom-1` (floating towel shelves) |

`V1.vanity-bathroom-1-1` / `V1.vanity-master-bathroom-1`: 30 cm thick floating walnut blocks
(top at 85 cm), 2 push-to-open drawers. Both baths: `wood_look_tiles` floor, `greige_stone` walls.

## Change log
- 2026-10-04 — **washing machine** redrawn: the door and control strip were coplanar with the body
  front and flickered (z-fighting). Now every detail stands proud of the body, the door is round
  (new part shape `ycyl` = cylinder lying along y), drawer + display + knob on the strip.
- 2026-10-04 — **big tiles**: owner asked for large format, researched standards (60 x 60 and
  60 x 120 are the common large formats; 60 x 120 gives fewer grout lines, good in small baths).
  Bath walls `greige_stone` 60 x 120 **vertical** (1.80 m walls = exactly 3 tiles, height 2 tiles +
  30 cm row under the ceiling); floor `wood_look_tiles` 20 x 120 (1.80 m = exactly 9 planks).
  Tile layouts now start with a full tile at each room's / wall's corner (object origin there;
  one wall-skin object per wall, `geometry.cladding_walls`). Grout a shade darker so the format reads.
- 2026-10-04 — `[rooms.<id>] ceiling = "<finish>"`: tiles the ceiling (`FINISH_<KEY>_ceiling_<room>`,
  prop `ceiling_skin` - follows the add-on's ceiling mode, so plan view still sees in). V1 baths:
  ceiling = greige_stone.
- 2026-10-04 — V1 Bath 2: `V1.bath-screen-master-bathroom-1` (fixed glass on the tub rim, 90 cm,
  brass profiles, top 2.0 m) and `V1.shower-head-master-bathroom-1` (brass bar shower on the mirror
  wall over the tub: mixer 1.0 m, rain head 25 cm at ~2.2 m). Sizes are standard choices.
- 2026-10-04 — owner photo `docs/uploads/gresie.jpg`: new finish kind **`marble`** (warm white,
  thin broken gold veins = contour lines of a stretched diagonal noise, faint grey hairlines,
  beige clouding) and finish `calacatta_gold` 60 x 120, laid horizontally as in the photo. V1:
  hall floor, kitchen floor + walls.
- 2026-10-04 — V1 bathtub wall to wall: `V1.bathtub-master-bathroom-1` 1.70 → 1.78 m (room 1.80 minus
  the wall tiles), 0.70 → 0.69 m wide so the door leaf (from x 4.939) still clears it. New item
  field `apron = "<finish>"` (bathtubs): tiled front panel `APRON_<id>`, here greige_stone.
- 2026-10-04 — bath floors: wood-look planks read as hardwood -> `oak_tiles` 60 x 60 square tiles, same dark
  oak colour (finish `wood_look_tiles` renamed). V1 vanities -> `vanity-frame` (C-shape: 18 cm top under the
  bowl, 4 cm side + shelf), `towels` on the shelf, LED strip under it (ids `V1.vanity-frame-bathroom-1-1`,
  `V1.vanity-frame-master-bathroom-1`, `V1.towels-*`, `V1.led-strip-bathroom-1-2`, `-master-bathroom-2`).
- 2026-10-04 — **stretch (Barrisol) ceiling** `[rooms.<id>] stretch_ceiling = true`: white membrane 5 cm under
  the slab (2.65 m), 5 cm short of every walled edge (`geometry.walled_edges` / `inset_rectilinear`), warm
  LED line in the gap (glow + wall-grazing rectangle lights, 12 W/m, no shadows); ceiling-mounted pieces are
  lowered onto it in the build; validator `stretch_ceiling`. V1: hall, living, both baths (replaces the bath
  ceiling tiles - owner's later instruction). Reference: owner photo of a floating ceiling.
- 2026-10-04 — **track lighting** (`track-light` + `[items.track]` heads aimed at world points): V1 downlights,
  ceiling panels, the bedroom-1 panel and the suite's flush ring replaced by 7 black tracks aimed at sink, WC,
  shower, washer, tub, entrance floor, wardrobe fronts, beds. Pendants, lamps, strips, balcony light kept.
- 2026-10-04 — **wardrobes** like owner photo `docs/uploads/dressing.jpg`: taupe-beige matte doors (tall door +
  top box, long oak bar handles - storage `handle_length`) + one wood column (top doors, lit open niche with a
  shelf, 3 drawers, open bottom) in all four V1 wardrobes; LED strips under the niche shelves.
- 2026-10-04 — **boiler slat screen**: `V1.slat-screen-bathroom-1-1/-2` walnut slats 3 cm, 1.5 cm gaps (boiler
  barely visible) on its front and shower side, 0.95 m to the stretch ceiling; the washer stays open.
- 2026-10-04 — living rug -> `V1.organic-rug-living-1` (was `V1.rug-living-1`): modern organic pebble outline,
  warm greige.
- 2026-10-04 — living pendant -> `V1.infinity-pendant-light-living-1` (replaces `V1.ring-pendant-light-living-1`):
  twisted 3D figure-eight LED band (lemniscate, loops +-10 cm), gold, glowing underside, 1.40 x 0.75 m - scaled
  to the 6.35 x 4.18 m room, over the coffee table, lowest point ~1.90 m under the stretch ceiling; 160 W area.
- 2026-10-04 — both V1 vanity frames dark walnut `#3f2a1c` (owner: the whole piece under the sink dark wood).
- 2026-10-04 — owner's desk `V1.panel-desk-living-1` (160 x 80, h 80, light-grey top, two solid dark-grey slab
  legs; new shape `panel-desk`) at the window end of the bedroom-1 wall of the living room. `V1.wardrobe-living-1`
  slid to the hall end and shortened 3.75 -> 2.55 m (one beige double-door module removed, wood column 1.05 ->
  0.75 m) so it stays inside the living room; its cove and niche LEDs moved with it.
- 2026-10-04 — V1 lighting dimmed to ~60 % and warmer (~2700 K, `#ffd29e`) on all 30 fixtures + track heads;
  stretch-ceiling LED line 12 -> 7 W/m, `#ffc98f` (owner: the house was too lit).
- 2026-10-04 — finish `walnut` (walnut-brown planks 120 x 19): V1 living, bedroom 1, master suite floors.
- 2026-10-04 — `V1.wardrobe-living-1`: wood column moved to the middle (beige / wood / beige) for contrast.
- 2026-10-04 — on the desk: `V1.monitor-living-1` (27", new shape `monitor`), `V1.keyboard-living-1`,
  `V1.mouse-living-1` (new shape `mouse`), `V1.pc-tower-living-1` (compact tower at the wardrobe end).
- 2026-10-04 — curtains: wave-fold (ripple) shapes `sheer-curtain` (white silk, new see-through `sheer` shade with
  transparent shadows) + `drape` (mocha `#6f5646`, new matte `fabric` shade), ceiling (2.65 living under the
  stretch ceiling / 2.70 bedrooms) to 1 cm above the floor, drapes stacked open at both sides: living W1 +
  balcony door, bedroom 1 W2, master suite W4. `V1.gaming-chair-living-1` (grey, 5-star base) at the desk.
  Master-suite wardrobes: wood column first, at the entrance end.
- 2026-10-04 — owner photos `sofa.jpg`, `armchair.jpg`: `V1.tufted-corner-sofa-living-1` (was
  `V1.corner-sofa-living-1`; tufted oatmeal bouclé blocks, L, wooden feet, throw cushions) and
  `V1.tub-armchair-living-1/-2` (were `V1.armchair-living-*`; round bouclé tub chair). Coffee table 45 cm from the
  seat (y 9.0), side table in the chaise corner, infinity pendant follows the coffee table. `V1.bonsai-living-1`
  on the desk. Validator: corner sofas overlap-checked by their real L footprint (`Item.footprint_parts`).
- 2026-10-04 — living: tub armchairs turned in towards the coffee table / sofa (conversation group, clear of
  the hall-desk path); `V1.wall-tv-living-1` 75" hung flat (new shape `wall-tv`) on `V1.slat-panel-living-1`, a
  floor-to-ceiling walnut slat wall 2.40 m wide on the kitchen wall facing the sofa (minimalist TV wall).
  Bath 1 shower glass up to the stretch ceiling (shower shape: pieces >= 2.40 m get full-height glass).
- 2026-10-04 — `V1.shoe-cabinet-hall-1`: floating hall cabinet 82 x 40 x 90 (2 drawers + tilt-out shoe flap,
  push-to-open, taupe-beige) left of the master-suite door. Master suite: `V1.slat-panel-master-suite-1`
  (walnut slat wall 2.40 m) + `V1.wall-tv-master-suite-1` 65" wall-hung (was `V1.tv-master-suite-1` on the
  console); console 3 cm forward.
- 2026-10-04 — floating beds: `V1.floating-bed-bedroom-1-1`, `V1.floating-bed-master-suite-1` (were `V1.bed-*`;
  frame + headboard hover 18 cm on a hidden recessed plinth, LED line + floor-glow strip underneath).
  Built-in `BI_entrance_door` (all variants): metallic-brown entrance door leaf, shown half open (45 deg).
- 2026-10-04 — balcony: finish `deck` (dark brown boards 120 x 14 along the balcony, open gaps; a variant floor on
  the balcony is raised onto its slab to ~0); `V1.outdoor-dining-table-balcony-1` + `V1.outdoor-chair-balcony-1/-2`
  (modern: anthracite aluminium, teak slats / arms, rope-woven seats; were `table-` / `chair-balcony-*`);
  `V1.lemon-tree-balcony-1` (was `V1.plant-balcony-1`).
- 2026-10-04 — living: `V1.bird-of-paradise-living-1` (exotic Strelitzia, stone pot; new part shape `xcyl`) in the
  corner of the TV wall and the hall opening (was `V1.plant-living-1` by the window); tub armchair 2 moved to the
  balcony side of the coffee table. Hall: `V1.wardrobe-hall-1` (was the shoe cabinet) - floating, ceiling
  height, coats + shoes.
- 2026-10-04 — kitchen: fridge moved left of the kitchen door (seen entering from the hall), before the table;
  `V1.plant-kitchen-1` removed; units, worktop, fridge matte white `#f7f7f5`, dining table dark wood `#3f2a1c`.
  Tree leaves matte (no specular).
- 2026-10-04 — kitchen: `V1.tall-cabinet-kitchen-1` (60 cm column to the ceiling on the old fridge spot: 30 cm floor
  drawer, integrated dishwasher panel - `V1.dishwasher-kitchen-1` removed -, 3 drawers, top cupboard); 60 cm sink
  cabinet next to it with `V1.black-sink-kitchen-1` (black bowl + matte black gooseneck faucet; was
  `V1.sink-kitchen-1`); `V1.base-cabinet-kitchen-3` 85 cm drawers in the old dishwasher slot; worktop 3.55 m;
  oven moved under the induction cooktop / hood; `V1.backsplash-kitchen-1` black dark-marble (finish
  `nero_marquina`, one row 120 x 60, worktop to 1.50 m - backsplash pieces take `apron`);
  `V1.venetian-blind-kitchen-1` horizontal blind over W3, slats half tilted.
- 2026-10-04 — `[start_view]` in apartment.toml: Blender opens just inside the entrance door, looking into the hall.
- 2026-10-04 — floating beds stronger: plinth 38 cm inside the frame, lift 22 cm. Bedroom 1: `V1.desk-bedroom-1-1`
  (90 x 45 x 72 light oak) + `V1.chair-bedroom-1-1` on the living-room wall, door end (fits beside the bed's foot).
  Bath 1: `V1.walk-in-shower-bathroom-1-1` (was `V1.shower-bathroom-1-1`): no tray, floor tiles run in, linear
  drain. Kitchen camera moved near the door (fridge / tall unit stand at the old eyes).
- 2026-10-04 — `[start_view]`: Blender opens standing in the entrance door opening (7.98, 4.40, eye 1.60) looking
  up the hallway, variant V1 active. The add-on applies it on every file load (timers after the UI restore, add-on
  0.3.2) and hides the X-Y floor grid / axes. Bird of paradise moved to the corner between the TV wall and the
  balcony door.
- 2026-10-04 — bedroom 1 desk + chair moved to the window end of the living-room wall. Builds save with nothing
  selected.
- 2026-10-04 — kitchen like `docs/uploads/kitchen.jpg` (wood + beige): `V1.wall-cabinet-kitchen-1` shallow 40 cm
  deep, 1.50-2.10 m, walnut wood `#7a5236`, lift-up push-to-open; `V1.wall-cabinet-kitchen-2` 60 cm deep boxes
  2.10 m to the ceiling, beige `#cfc2ad`; both from the hood to the tall unit (2.95 m). Worktop wood (= shallow
  units); base units, tall unit, oven, fridge beige (replaces the white). `V1.led-strip-kitchen-2` under the wood
  units.
- 2026-10-04 — kitchen: blind slats thinner / more open (window reads through); item `tag` (+ `tag_z`): a name
  written upright on the front in 3D - FRIDGE, OVEN, DISHWASHER (on the tall unit's panel), SINK, INDUCTION HOB,
  HOOD; dining table = worktop wood, chairs white; `V1.glass-fridge-kitchen-1` (was `V1.fridge-kitchen-1`): modern
  60 cm column, 2 tall smoked-glass doors (new shade `smoked`), lit shelves and food faintly visible.
  Bath 2: `V1.tall-cabinet-master-bathroom-1` wall-hung dark-walnut storage (90 x 30, 0.35-2.10 m) on the end
  wall between the WC and the vanity.
- 2026-10-04 — Bath 1: `V1.tall-cabinet-bathroom-1-1` (same wall-hung dark-walnut cabinet, 85 cm) on the WC wall by
  the door, clear of the door swing. Kitchen wall to wall: tall unit 60 -> 69 cm (closes the gap to the end wall),
  upper beige boxes now run over the hood from wall to the tall unit (3.54 m), hood chimney ends under them.
- 2026-10-04 — `air-conditioner` (slim grey wall split units) in living (balcony wall, sofa corner), bedroom 1 and
  the suite (window walls); `heat-recovery-vent` covers (160 mm core) beside / under each. Bird of paradise now a
  real mesh (`build_scene.bird_of_paradise_mesh`: tapered pot, arching stems, folded tapering paddle leaves,
  two greens). Two coffee mugs on the balcony table.
- 2026-10-04 — kitchen: glass fridge turned to face the middle of the kitchen (back on the end wall, 58 cm deep to
  clear the door frame); `V1.cooker-hood-kitchen-1` replaced by an integrated hood - wood wall units now run over
  the hob too and only `V1.hood-visor-kitchen-1` (slim pull-out visor, tag HOOD) shows; 4 `place-setting`s (plate,
  fork, knife, glass) + `serving-bowl` with fruit on the table. Bedroom 1 desk: notebooks, pencils, pencil case.
- 2026-10-04 — bedroom 1: `V1.storage-cabinet-bedroom-1-1` low storage (3 drawers + cupboard) beside the desk.
- 2026-10-04 — hall wardrobe: oak handles (long bar on the coat door, bars on the drawer and shoe flap).
- 2026-10-04 — `V1.wallpaper-living-1`: wallpaper mural "Suave" (Mourals) on the sofa wall, corner to the curtains, floor to ceiling - finish `suave_mural`, new kind `mural` (distorted diagonal wave bands, cream / sand / caramel, no seams); `wallpaper` pieces take `apron` like backsplashes.
- 2026-10-04 — wallpaper murals (Mourals, photos in docs/uploads/wallpaper_*.jpg) as procedural finishes on thin
  `wallpaper` panels: Suave (kind `mural`, broad diagonal agate waves) on the living sofa wall; Delicate Blues
  (kind `watercolor`, painted sky) on the child's bed wall; Madera (kind `chevron`, oak panels with V-groove groups)
  on the master bed wall. Child's room: the slat wall moved to the desk wall (desk, chair, storage, desk items
  3 cm forward; grazing LED moved with it).
- 2026-10-04 — kitchen tall unit: no drawers; integrated dishwasher at base-unit height (plinth 8 cm), cupboard
  above to 1.90 m, top cupboard; storage option `handles_low` (handles at the bottom of every door); panel fronts
  (integrated appliances) get a bar along the top edge. `V1.slat-panel-hall-2`: walnut slats on the hall-facing
  end of the living-room wardrobe.
- 2026-10-04 — kitchen backsplash: cream marble with soft taupe veins (finish `cream_marble`, 180 x 60 slabs) like docs/uploads/backsplash.jpg, replacing the black marble.
- 2026-10-04 — bathroom cabinets raised to 0.80-2.55 m; the bath 1 one narrowed to 55 x 25 cm so the WC has room.
- 2026-10-04 — walk-in shower: 3 cm curb (4 cm wide) along the open front edge in the floor-tile colour, keeps the water in.
- 2026-10-04 — `calacatta_gold` cleaner: whiter base `#f5f3ef`, paler gold `#d2bd96`; marble veins softer (main 0.75, side 0.45). Bath 1 camera moved clear of the raised cabinet.
- 2026-10-04 — kitchen tall unit: dishwasher lifted 30 cm again (accessibility) over a 30 cm drawer; cupboard 1.09-1.90 m, top cupboard; handles low.
- 2026-10-04 — master TV console in the dressing palette: taupe-beige drawer modules, walnut-wood centre flap, oak handles.
- 2026-10-04 — `[rooms.<id>] skirting = "#rrggbb"` (+ `skirting_height`, default 0.08): wooden skirting board along
  the real walls only (`cladding_walls(..., walled_only=True)`), cut at doors; V1 living + both bedrooms, walnut
  `#4e3322`. Kitchen units on a 9 cm plinth (base units, tall unit - its floor drawer 21 cm so the dishwasher still
  starts at 30 cm -, `V1.plinth-kitchen-1` under the raised oven). Floating beds: wood frame + headboard, white
  mattress, linen duvet with side drapes, white turned-down sheet, pillows.
- 2026-10-04 — Bath 1 walk-in: brass bar shower `V1.shower-head-bathroom-1-1` (mixer, riser, rain head; the
  walk-in shape drops its own head block). Lit soap niches `V1.wall-niche-bathroom-1-1` (shower wall) and
  `V1.wall-niche-master-bathroom-1` (over the tub) - shape `wall-niche` (tiled frame, dark recess, LED, bottles).
  Both WCs: brass `toilet-paper-holder` on the wall, `toilet-roll-stand` (3 spare rolls) and `toilet-brush` on the
  floor.
- 2026-10-04 — kitchen tall unit: dishwasher from 45 cm (plinth 9 + drawer 36), cupboard 1.24-1.90 m.
- 2026-10-04 — kids wardrobe `V1.wardrobe-bedroom-1-1`: own palette - dusty-blue doors `#7f9fb0`, cream column + carcass `#efe6d6`, light-oak handles.
- 2026-10-04 — kids low storage cabinet cream `#efe6d6`.
- 2026-10-04 — kids wardrobe: blue / cream / blue (cream column in the middle, 3 x 60 cm), niche LEDs moved with it.
- 2026-10-04 — master wardrobe on the bathroom wall: beige / wood / beige (wood column in the middle), niche LEDs moved with it.
- 2026-10-04 — bug fix (storage): a fixed carcass shelf where two different stacked fronts meet (door / open niche /
  drawers) - the top drawer was visible from the open niche above. Kids' room: drapes dusty blue `#8ea8b6`, slat wall
  light oak `#c9a77c`.
- 2026-10-04 — kids desk chair dusty blue `#7f9fb0`.
- 2026-10-04 — hall: two floating walnut shelves (70 cm at 1.20 m, 45 cm at 1.62 m) on the white wall right of the slatted wardrobe end.
- 2026-10-04 — bath floors `oak_tiles` -> warm taupe stone `#a89886` (60 x 60) to suit the greige walls / walnut / brass; shower curb follows.
- 2026-10-04 — `walnut` floor a little lighter: `#76533b` / `#62442f`.
- 2026-10-04 — master bed wall: wallpaper `ripple` (Mourals 'Ripple', new kind `ripple`: horizontal dune ridges with a
  real bump, warm white) replaces Madera. Hall shelves: small plant + 2 ceramic vases (new shape `vase`). Kids bed
  frame cream `#efe6d6`.
- 2026-10-04 — kids rug light blue (base `#6f93a8`, the soft shade lightens it).
- 2026-10-04 — rugs: kids light blue (deeper base `#5a7f96`), master warm greige-taupe `#8a7764`, living rug ->
  `V1.organic-shag-rug-living-1` with a new `shag` shade (fibre noise colour + strong bump, sheen). Hall: charcoal
  `V1.doormat-hall-1` + two pairs of `shoes` on it (they sit in the entrance door's swing - it opens about half, as
  shown); mats / rugs (top <= 1.5 cm) no longer count as blocking a door. White door frames on every door opening
  (`build_door_frames`: lining + 7 cm architraves both faces, all variants).
- 2026-10-04 — kitchen sink: undermount, 20 cm deep, rim flush; worktop split into 4 pieces around the opening
  (`V1.countertop-kitchen-1..4`); sinks no longer count as overlapping their cabinets. Suave mural richer: finer
  strands of varying thickness, hairlines, bright highlight streaks and vague sand / blush colour sprays.

### 2026-10-04 - plush seating, kids' room, portal, closed entrance door, mural directions
- Living sofa: `V1.tufted-corner-sofa-living-1` -> **`V1.plush-corner-sofa-living-1`** (new shape `plush-corner-sofa`:
  overstuffed cushions with rolled edges, rolled arm, one chaise cushion, warm cream `#86694b` base -> soft shade).
- Living armchairs: `V1.tub-armchair-living-1/2` -> **`V1.plush-armchair-living-1/2`** (shape `plush-armchair`, same cream).
- Kitchen chairs: `V1.chair-kitchen-1/2/5/6` -> **`V1.upholstered-chair-kitchen-1/2/5/6`** (upholstered shell back
  with low wings, padded seat, slim brass legs).
- Kids' room (bedroom_1): floor `light_oak` (new parquet finish, V1 only); bed single 90 x 200 with "Baby Turi"
  written flat on the duvet in blue (new item field `tag_color`; on beds the tag lies on the duvet); nightstand
  moved next to it; rug 2.8 x 2.2. Master rug 2.5 x 2.8.
- Hall: wood portal (`V1.portal-jamb-hall-1/2`, `V1.portal-head-hall-1`, slat-wall walnut, 20 cm deep) framing the
  open passage to the living room; hall shelves shifted 15 cm to clear it.
- `BI_entrance_door` closed (rotation 0, against the hall face); start view moved just inside it.
- Suave mural: strand families each get their own direction + domain warp, so strands cross and curl.
- Portal doubled to 40 cm deep (owner 2026-10-04); hall shelves shortened to 0.42 / 0.30 m to fit beside it.
- Living wallpaper Suave -> Ripple, same as the master bedroom (owner 2026-10-04).
- Kitchen + hall storage: new Storage field `door_handles = false` - doors, flaps and appliance panels are push-to-open, only drawers keep handles (owner 2026-10-04).

### 2026-10-05 - hall / living portal removed everywhere
- Owner: the wooden portal between the hall and the living "blocks the living room" - removed from every variant:
  `portal-jamb-hall-1/2`, `portal-head-hall-1` and the 60 cm `slat-panel-hall-2` beside them (V1 + its styles
  V2-V13, D1, D2, D3, D5; A, D4, DEV never had them). Design scripts in `scripts/designs/` no longer reference them.
- A tumble-dryer spot was studied (hall, bath 1, bath 2) and dropped by the owner - no dryer in any variant.
