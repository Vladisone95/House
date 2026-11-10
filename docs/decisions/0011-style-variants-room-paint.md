# ADR 0011 — Style variants of a layout (V1 restyled), per-room paint, Style dropdown

- Status: accepted · Date: 2026-10-04

## Context
Owner (2026-10-04): "Take V1 and create some variants with different color schemes with the same furniture
layout. Search online and give me some valid options for every room ... change the colors, tile colors, pretty
much everything but do not change where the objects are being placed." Then: also restyle V1 in ten named
styles (Contemporary, Modern Minimalism, Warm Minimalism, Japandi, Organic Modern, Quiet Luxury, Modern
Mediterranean, Scandinavian, Wabi-Sabi, Modern Industrial), and pick a style from a **dropdown** instead of a
long row of variant buttons; V2 / V3 belong in that dropdown too.

Until now a variant had one wall paint (`wall_color`) for the whole apartment, and the add-on showed every
variant as a button.

## Decision
- **`[variant] style_of = "<layout key>"`**: the variant restyles that layout - same ids (re-keyed), types,
  sizes, positions, rotations, elevations, storage modules, lights; only colours and finishes differ.
  Validator `variant_style`: must name another variant that is not itself a style (one level).
- **Add-on (Furniture variants panel)**: *Layout* buttons show only layouts (A, DEV, V1 ...; ◀ ▶ cycle them);
  under them a **Style** dropdown lists the active layout's "Original" + all its styles, with ◀ ▶ to step
  through styles. Switching keeps the view (it only toggles collections, as before). Variant keys sort
  naturally (V2 < V10). Operators `apt.set_style`, `apt.cycle_style`; GUI test `step_style` (fixture `C` =
  style of `A`).
- **`[rooms.<id>] paint = "#rrggbb"`**: a room's own wall colour - a 2 mm painted skin on its walls
  (`FINISH_<KEY>_paint_<room>_<n>`, in the variant's collection). Ignored where `walls` tiles the room.
  Wallpaper panels (4 mm) stay in front of it; skirting (12 mm) too. Pricing unchanged (still paint).
- Restyles are generated, not hand-edited: a mapping {room: {V1 colour: new colour}} + floor / wall / apron
  finish swaps applied to a copy of V1. Upholstery, rugs and towels use the build's lightened `soft` / `shag`
  shades (sRGB c + (1 − c) × 0.55 / ~0.43), so the generator back-computes the base colour from the colour
  the piece should *look*; looks darker than ~#8c8c8c per channel are not reachable in those shades.
- Hard-coded part colours inside shapes (brass vessel-sink spout / mirror frame / dining-chair legs, bed
  linen, plant pots) are not item colours and stay as they are in every style.

## V2 / V3 (researched 2026 trends: warm neutrals, sage / smoky jade, espresso - BM Silhouette, khaki -
SW Universal Khaki, Cloud Dancer white, terracotta, deep teal, soft terrazzo, zellige, tile drenching)
| Room | V2 Sage & Oak | V3 Espresso & Terracotta |
|---|---|---|
| Living | pale ash floor, sage-white walls, oatmeal sofa + armchairs, smoky-jade drapes, light-oak slat wall + coffee table, sage-grey wardrobe, sage ripple wallpaper | smoked-oak floor, khaki walls, pale-clay sofa, rust drapes, espresso slat wall, travertine coffee table, khaki + espresso wardrobe, sand/terracotta ripple |
| Kitchen | cream terrazzo floor, eucalyptus-green base + top units, light-oak worktop / shallow units / table, sage zellige backsplash, black handles | terracotta floor, ink-teal units, espresso worktop / wood units / table, terracotta zellige backsplash, antique brass |
| Hall | cream terrazzo, light-oak portal + shelves, sage-grey wardrobe | terracotta tiles, espresso portal, khaki wardrobe |
| Bath 1 | sage zellige walls, cream terrazzo floor, light-oak vanity + slats, matte black fittings | deep-teal zellige walls, travertine floor, espresso vanity, antique brass |
| Bath 2 | warm-white stone walls + tub front, cream terrazzo floor, light oak | travertine walls + tub front, terracotta floor, espresso |
| Kids' room | butter-yellow + cream wardrobe, sage drapes / rug, meadow mural, pale ash | terracotta + cream wardrobe, mustard drapes, apricot mural, honey oak |
| Master suite | muted-rose walls, forest-green ripple wall behind the bed, warm-white wardrobes + oak, green drapes, rose rug | taupe walls, espresso chevron wall, khaki wardrobes + espresso, merlot drapes, plum-rose rug |
| Balcony | light outdoor tiles, oak furniture | terracotta tiles, black furniture |

New finishes: `cream_terrazzo`, `sage_zellige`, `cloud_stone`, `pale_ash`, `ripple_sage`, `ripple_forest`,
`meadow_watercolor`, `terracotta_tiles`, `teal_zellige`, `travertine`, `clay_zellige`, `smoked_oak`, `honey_oak`,
`ripple_clay`, `espresso_chevron`, `apricot_watercolor`.

## Change log
- 2026-10-04 — V2, V3 created (style_of V1). Ten more styles V4-V13 commissioned (one research + render pass
  each); see the entries below as they land.
- 2026-10-04 — **V4-V13** (one researched pass each, rendered and checked, then merged):

| Key | Style | Palette in one line |
|---|---|---|
| V4 | Contemporary | soft-white / greige walls, graphite + white joinery, grey-washed oak, concrete-look + statuario porcelain, walnut warmth, ink-blue + cognac accents, brushed steel |
| V5 | Modern Minimalism | strict monochrome: chalk white, greige, pale microcement, grey-washed oak, matte white handleless fronts, graphite wood, steel; one signal-yellow accent in the kids' room |
| V6 | Warm Minimalism | one sand / oat / camel family, limewash walls with matching skirting, natural oak, limestone + tadelakt baths, ecru boucle, brushed bronze |
| V7 | Japandi | light oak against charred black wood (shou sugi ban), rice-paper whites, stone + slate greys, muted clay, matte black (no sage - that is V2) |
| V8 | Organic Modern | mushroom limewash, white oak + walnut, limestone + travertine, moss-olive kitchen / bath tiles, camel boucle, aged bronze |
| V9 | Quiet Luxury | tonal greige / mushroom / mink, greige oak, honed limestone, taupe-veined marble, smoked walnut, cashmere textiles, smoked bronze |
| V10 | Modern Mediterranean | limewash creams, Aegean blue kitchen + zellige, olive, bleached oak, limestone, lemon-grove kids' mural, aged brass; terracotta only as accents |
| V11 | Scandinavian | crisp whites, white-washed pine + birch, soft greys, dusty-blue kitchen / bath subway tiles, mustard + dusty-pink hygge textiles, brushed steel |
| V12 | Wabi-Sabi | bone / mushroom / sand limewash, tadelakt baths, ash microcement, aged oak, raw clay, linen, soot iron + aged bronze |
| V13 | Modern Industrial | microcement + raw concrete, exposed-brick sofa wall and backsplash, blackened steel, smoked reclaimed oak, graphite kitchen, cognac-tan, rust accents |

- 2026-10-04 — **item `metal = "#rrggbb"`**: recolours a shape's built-in brass fittings (`BRASS` #b08d57: shower
  mixer / riser / rain head, vessel-sink spout, backlit-mirror frame, bath-screen profiles, upholstered-chair legs).
  The generator sets it from each style's brass mapping, so black / steel / bronze styles no longer show brass taps.
- 2026-10-04 — the generator lives in the repo: `scripts/restyle/restyle_lib.py` + one `scripts/restyle/styles/<KEY>.py`
  per style; `uv run python scripts/restyle/run.py [KEYS]` rewrites the style variants from the current layout and
  the generated finish block at the end of data/apartment.toml (86 style finishes, names prefixed per style).
  **After changing V1's layout, re-run it** - never edit a style variant's positions by hand.
- 2026-10-04 — owner: "you have blocked the entrance to the living room with a white wall" - the paint skin (and wall
  tiles) skinned every room edge, including the open hall / living passage. Paint and wall-tile skins now cover real
  walls only (`cladding_walls(..., walled_only=True)`); door openings and open passages stay open.
- 2026-10-04 — owner: change *everything* in a style (sofa, chairs, desks, floor, rugs, sinks, wallpapers, slat walls,
  wardrobes), and be able to pick colours himself:
  - `[variant] true_colors = true` (all styles): soft / shag / sheer shades show the colour as given - before, every
    fabric was lightened 55 % so all sofas / rugs looked near-white.
  - item `accent` (built-in second colours `ACCENTS`: sofa / armchair wooden base + feet, duvet linen, shower curb),
    `apron_color` (tints a wallpaper / backsplash / tub-front finish); vessel-sink bowl inside follows the sink colour.
  - `[rooms.<id>] floor_color`, `walls_color`: tint the floor / wall-tile finish (pattern kept; second tone and grout
    keep their offset - `tinted_finish`).
  - Ripple / watercolour / mural shaders: their fixed tints are now relative to each finish's own colours (`_rel`),
    so a recoloured wallpaper keeps its shading instead of turning cream.
  - **Colour picker** (add-on, Furniture panel): select a piece -> *Colours...* (body, accent, metal, wallpaper /
    tiles, every front module, handles, inside); *Room colours...* (floor, wall paint or wall tiles). Live (the
    piece's materials are copied and recoloured) and saved to `data/variants/<KEY>.toml`; each pick is listed in
    `[variant] owner_colors` and survives `scripts/restyle/run.py` regenerating the style.
  - A variant may define its own `[finishes.<key>_...]` (merged by `merge_variant_finishes`; validator `finish`).
- 2026-10-04 — `docs/design-rules.md`: ground rules for a good home (set-in-stone items, household, circulation,
  storage, kitchen, light, room functions, coherence + checklist). Every style / design must pass it.
- 2026-10-04 — styles deepened (owner: "change as much as possible"): every style now also sets accent (sofa base,
  duvet, curb), metal, `cushion` (new item field: the sofa / armchair throw cushions, 3 tones), per-piece `items`
  overrides, sheers, lamps, track lights (rail + heads now take the piece colour), sinks + taps (`metal` reaches
  a sink's chrome / black tap), interiors of every storage piece; ~125-130 of 167 pieces per style. True-colour
  fabrics: sheen tinted with the fabric colour (a white sheen washed rugs out).
- 2026-10-04 — **five free designs D1-D5** (new layouts, own `[finishes.dN_*]`, `true_colors`), each checked against
  `docs/design-rules.md`; generators in `scripts/designs/DN/` (reference - the TOML in data/variants is the truth):

| Key | Name | Movement | Notable moves |
|---|---|---|---|
| D1 | Dune Cocoon | Soft curves / cocooning | rust-velvet tub chairs, oval tables, brass halo rings, clay-rose drenched suite, hall portal removed, shoe bench + pill mirror |
| D2 | Colour Drenched | Colour drenching | one saturated colour per room (ochre hall, teal living, olive kitchen, oxblood suite, butter kids), bookcase + media console, hall shoe bench (1.77 m closed storage) |
| D3 | Biophilic Modern - Light & Leaf | Biophilic | preserved-moss media wall, plant + book wall, fridge into the run (triangle 5.6 m), banquette dining, kids' bed lengthwise + play floor, screen-free master, balcony garden + drying rack |
| D4 | Teak & Saffron | Mid-century revival | straight olive sofa + teak credenza, cognac lounge corner, teak tulip table, hall coat cupboard + bench, teak chevron bed wall |
| D5 | Jewel Box Deco | Neo Art Deco | emerald / sapphire panels with brass chevrons, tiered brass rings, kitchen run re-planned (triangle 6.96 m, dishwasher by the sink, `D5.pantry-kitchen-1`), oxblood banquette, dressing table |

  Known limits (shape library): no globe / arc lamp, no tapered-leg sofa (D4 uses separate legs), generic `plant`
  is a cylinder (D3 uses bird-of-paradise / lemon-tree for big plants), D3 kids' nursing chair overlaps a window
  edge by ~0.17 m below the sill.
