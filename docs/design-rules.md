# Design ground rules - a good home to live in

Every design variant of this apartment (layouts **and** styles) must respect these rules, however different it
looks. A design may move, replace, add or drop furniture, change textures and ideas completely - but it may not
drop a function the household needs. Check a design against this list before showing it (the **Checklist** at
the end). Numbers come from the `interior-design-standards` skill; where a rule and a pretty idea conflict, the
rule wins.

## 0. Set in stone (never change in a design)
- **The shell**: walls, rooms, ceiling 2.70 m, windows, doors and their swings, balcony - `data/apartment.toml`
  and the owner-confirmed facts in `docs/decisions/0001-layout-reconstruction.md`.
- **Fixed service points** (`[[fixed_points]]`): each sink, WC, the washing machine (MSR) and the cooker hood /
  hob sit on their point - that is where the pipes and the vent are. Bath 1: walk-in shower, washer + the 180 L
  **boiler** over it (built-in), sink, WC. Bath 2: bathtub, sink, WC. Kitchen sink + hob on their points.
- **Built-ins** (boiler, entrance door) and the **entrance** position.
- **Technical pieces stay where V1 has them**: wall AC units and heat-recovery vents (they are installed with
  their pipes / ducts) - recolour them at most.
- Furniture ids follow `<KEY>.<type>-<room-slug>-<n>`; `uv run apartment validate` must say `OK`
  (no errors; warnings explained).

## 1. The household (design for these people)
- Adults in the **master suite** (bedroom 2 + open dressing + bath 2).
- A **baby / small child** in **bedroom 1** ("Baby Turi" - keep the name on the bed): safe, calm, grows with the
  child (cot or low bed now -> desk later), toy storage at child height, nothing tall that is not wall-fixed.
- **Someone works from home**: a real desk (>= 120 x 60 cm, ideally 140-160 x 70-80) with a good chair, out of
  screen glare from the WNW evening sun, with storage for paperwork. It may live in the living room or elsewhere,
  but it must exist.
- Guests: the living room seats **at least 4** (sofa + chairs), dining seats **4 daily, 6 occasionally**.

## 2. Circulation and safety
- Main paths (entrance -> hall -> every room, living -> balcony door, kitchen door -> sink / hob) **>= 0.90 m**;
  between furniture >= 0.60 m (0.75 comfortable).
- No piece in a **door swing**, in front of a **window sill used for opening**, or blocking the **balcony door**.
- 0.70 m clear in front of wardrobes (doors open) and in front of the WC / basin; 0.60 m beside a double bed on
  **both** sides and at the foot where it is a path.
- Tall pieces (> 1.2 m) against a wall (wall-fixed in reality); nothing sharp or tippy in the kids' room.

## 3. Storage (an apartment without enough storage fails, whatever it looks like)
- **Entrance / hall**: closed coat + shoe storage (>= 1.0 m run), a mirror, a place to sit or a bench / shelf to put
  keys and bags on.
- **Master**: hanging + shelves + drawers for two adults - **>= 2.4 m** of wardrobe run in the suite (the open
  dressing + the bath-2 wall).
- **Kids' room**: >= 1.2 m wardrobe / chest + low open storage for toys and books.
- **Kitchen**: base + wall (or tall) units along the full run, a pantry / tall unit, room for the fridge,
  dishwasher, oven, bins (under the sink), small appliances on the worktop.
- **Bathrooms**: closed storage for towels and toiletries in each (vanity drawers / cabinet), towel rail / hooks.
- **Living**: media + books + general closed storage.
- **Cleaning / utility**: vacuum, mop, ironing board, drying rack - a tall utility cupboard somewhere (hall or
  dressing) and drying space (balcony or a pull-out rack).

## 4. Kitchen that works
- Sink, hob and fridge form a work triangle of 4-7 m total; >= 0.60 m worktop between sink and hob, >= 0.40 m
  beside the hob, landing space next to the fridge.
- Dishwasher next to the sink; oven at a safe height or under the hob; hood over the hob.
- Worktop 0.90-0.92 m high, 1.0-1.2 m clear in front; dining table with 0.75-0.90 m chair zone behind it.

## 5. Light, air, comfort
- **Three light layers in every room**: ambient (ceiling / track / cove), task (desk, worktop, mirror, reading by the
  bed) and accent (wall grazing, niches, lamps). Warm white (~2700 K) for living / bedrooms.
- **Daylight first**: don't block windows with tall furniture; desks and sofas oriented with the sun studies.
- Blackout + sheer curtains in both bedrooms; living room with sheers (+ drapes if wanted).
- Acoustic softness in the living room and bedrooms: rugs, curtains, upholstered pieces.
- Plants or natural materials somewhere in the main rooms.

## 6. Each room keeps its function
| Room | Must have |
|---|---|
| Hall | coat + shoe storage, mirror, seat / landing shelf, doormat, good light |
| Living | sofa + seats for 4, coffee / side table, TV or media focus at 1.2-1.6 x diagonal, rug, storage, reading light, the work desk (unless placed elsewhere), clear balcony-door path |
| Kitchen | full kitchen (section 4) + dining for 4 (6 occasional) |
| Bath 1 | walk-in shower, washer + boiler (screened or tidy), basin + mirror + storage, WC, towels |
| Bath 2 | bathtub (+ shower over it), basin + mirror + storage, WC, towels |
| Bedroom 1 (kids) | cot / child bed, changing / desk surface, wardrobe, toy storage, nightlight / lamp, blackout, rug |
| Master suite | double bed (>= 160 x 200) with 2 bedside tables + reading lights, wardrobes (section 3), a mirror, a chair or bench, blackout |
| Balcony | seating for 2+ (table), plants, outdoor light |

## 7. Coherence (one design = one idea)
- One concept stated in a sentence, a palette of **3-5 main colours + 1-2 accents**, max **3 wood tones** and **2
  metal finishes** across the home; the same family of materials flows from room to room (rooms may vary the
  accent, not the language).
- Repeat key materials (e.g. the hall floor continues into the kitchen; the TV-wall wood appears again in the
  bedroom) so it reads as one home.
- Every bold move has a reason (light, space, storage, mood) - say it in the design notes.

## 8. Free designs (D-series) must be genuinely different - not V1 reskinned
Owner (2026-10-04): "you should have given yourself more space for imagination". Within sections 0-7, a free
design **re-thinks the organisation of every room**, not only its colours:
- **Bathrooms**: a different basin type (vessel / console / integrated / pedestal), a different vanity concept
  (floating slab, console on legs, open shelf, cabinet), a different mirror (round, arched, mirror cabinet,
  backlit), a different storage plan (mirror cabinet, open etagere, niches, ladder rail, tall cabinet elsewhere).
  Only the fixed points (basin / WC / shower / tub / washer positions) stay.
- **Media**: question the TV - another wall, a floor / swivel TV, a projector, or no TV in a room (e.g. a
  screen-free bedroom). Glare-check it.
- **Walls**: no default wallpaper; choose per wall - paint, colour blocks, painted arches, panelling, fluting,
  limewash, tiles, art / gallery walls, shelving. A design may use zero wallpapers.
- **Every room changes its arrangement or concept** (furniture positions, zones, what lives where), unless the
  design notes say why V1's arrangement is the best for that room.
- Report a **"different from V1"** table: room -> what changed in organisation (not colour).

## Checklist (copy into each design's report and tick it)
- [ ] validate OK (no errors); fixed points + built-ins + AC / vents untouched
- [ ] paths >= 0.90 m, no door / window / balcony-door blocked
- [ ] hall: coats, shoes, mirror, seat / shelf
- [ ] master: double bed + 2 bedside + >= 2.4 m wardrobes + mirror + blackout
- [ ] kids: child bed with "Baby Turi", wardrobe, toy storage, changing / desk, safe
- [ ] work desk + chair, glare-checked
- [ ] living seats 4, media, rug, storage, reading light
- [ ] kitchen triangle + dishwasher by sink + pantry + dining for 4-6
- [ ] each bath: storage, mirror, towels, light
- [ ] utility cupboard + drying space
- [ ] 3 light layers per room, blackout in bedrooms
- [ ] one concept, coherent palette (3-5 + 1-2 accents, <= 3 woods, <= 2 metals)
- [ ] free designs: "different from V1" table - every room re-organised (baths, media, walls included)
