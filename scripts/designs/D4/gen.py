"""Generate variant D4 "Teak & Saffron" (Mid-Century Modern Revival) from a copy of V1.

Run: uv run python .tmp/designs/D4/gen.py   -> .tmp/designs/D4/variants/D4.toml
"""
from __future__ import annotations

import tomllib
from dataclasses import replace
from pathlib import Path

from apartment_core.furniture import RoomFinish, _item, copy_variant, load_variant, variant_to_toml
from apartment_core.model import parse_finish

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "variants" / "D4.toml"

# ---------------------------------------------------------------- palette
CREAM = "#efe8da"      # walls
SAND = "#d8c6a4"       # oat / sand textiles
TEAK = "#a2683c"       # wood 1 - furniture
WALNUT = "#5b3b27"     # wood 2 - darker accents, skirting, slats
OLIVE = "#5f6233"      # main colour - sofa, kitchen base, hall cupboards
TEAL = "#1f5c60"       # main colour - baths, master drapes / rug, kids
MUSTARD = "#d19a2a"    # accent
RUST = "#b4542a"       # accent - burnt orange
CHAR = "#2c2a28"       # matte black / charcoal
BRASS = "#b08d57"      # metal 1 (shapes' built-in) ; metal 2 = matte black

v1 = load_variant(ROOT / "data" / "variants" / "V1.toml")
v = copy_variant(v1, "D4", "Teak & Saffron")
v.description = ("Mid-century modern revival, 2025-26 take: low teak pieces on slim legs, an olive velvet sofa "
                 "facing a long teak credenza, a cognac lounge-chair corner by the WNW window, cream terrazzo "
                 "underfoot, teal and olive glazed baths, mustard and burnt-orange accents on warm cream walls.")
v.based_on = "V1"
v.wall_color = CREAM
v.true_colors = True

# ---------------------------------------------------------------- finishes (own, d4_ prefix)
FIN = """
[d4_oak]
kind = "parquet"
size = [1.20, 0.19]
direction = "x"
color = "#c9a274"
color2 = "#b48d61"
joint_color = "#6f5236"
joint = 0.0015
roughness = 0.45
note = "D4: natural oak planks, mid-light, so teak and walnut furniture read darker against them"

[d4_terrazzo]
kind = "tiles"
size = [0.60, 0.60]
color = "#ece3d2"
color2 = "#b9784e"
joint_color = "#ddd3c0"
joint = 0.002
roughness = 0.35
note = "D4: cream terrazzo-look porcelain 60 x 60 with rust / ochre chips (hall, kitchen, both bath floors)"

[d4_terrazzo_wall]
kind = "tiles"
size = [0.60, 1.20]
color = "#dfcfb2"
color2 = "#a9653d"
joint_color = "#cdbd9f"
joint = 0.002
roughness = 0.35
note = "D4: warmer sand terrazzo 60 x 120 slabs with rust chips on the bath-2 walls"

[d4_teal_glaze]
kind = "stone"
size = [0.075, 0.30]
color = "#1f5f63"
color2 = "#174b4f"
joint_color = "#d9cfbd"
joint = 0.002
roughness = 0.12
note = "D4: deep-teal glazed 7.5 x 30 tiles, vertical stack bond (bath 1, tile-drenched)"

[d4_olive_glaze]
kind = "stone"
size = [0.075, 0.30]
color = "#7a7a3e"
color2 = "#66672f"
joint_color = "#ddd2bd"
joint = 0.002
roughness = 0.15
note = "D4: olive / avocado glazed 7.5 x 30 vertical tiles (bath-2 tub front)"

[d4_amber_glaze]
kind = "stone"
size = [0.075, 0.30]
color = "#c98a34"
color2 = "#b07325"
joint_color = "#efe6d6"
joint = 0.002
roughness = 0.12
note = "D4: amber-mustard glazed 7.5 x 30 vertical tiles (kitchen backsplash)"

[d4_sunset_mural]
kind = "mural"
size = [3.80, 2.65]
color = "#efe3cc"
color2 = "#c56f35"
joint_color = "#efe3cc"
joint = 0.0
roughness = 0.75
note = "D4: 70s-flavoured supergraphic - flowing cream / burnt-orange waves behind the sofa"

[d4_sunrise_watercolor]
kind = "watercolor"
size = [3.10, 2.70]
color = "#f3e8d6"
color2 = "#e0a85a"
joint_color = "#f3e8d6"
joint = 0.0
roughness = 0.8
note = "D4: soft apricot-mustard watercolour sky on the child's bed wall"

[d4_teak_chevron]
kind = "chevron"
size = [3.04, 2.70]
color = "#a2683c"
color2 = "#8a5530"
joint_color = "#3a2416"
joint = 0.0
roughness = 0.6
note = "D4: teak wall panelling in chevron groups behind the master bed (MCM wood-panelled wall)"

[d4_teak_deck]
kind = "parquet"
size = [1.20, 0.14]
direction = "y"
color = "#9a6a43"
color2 = "#87593a"
joint_color = "#2b1c12"
joint = 0.006
roughness = 0.6
note = "D4: teak-tone deck boards on the balcony"
"""
for name, f in tomllib.loads(FIN).items():
    v.finishes[name] = parse_finish(name, f)

# ---------------------------------------------------------------- room finishes
STRETCH = dict(stretch_ceiling=True, stretch_led_color="#ffc98f", stretch_led_w_per_m=7)
v.rooms = {
    "living": RoomFinish(floor="d4_oak", skirting=WALNUT),
    "hall": RoomFinish(floor="d4_terrazzo", skirting=WALNUT),
    "kitchen": RoomFinish(floor="d4_terrazzo"),
    "bedroom_1": RoomFinish(floor="d4_oak", skirting=WALNUT, paint="#f2e9d8"),
    "bedroom_2": RoomFinish(floor="d4_oak", skirting=WALNUT, paint="#e6d8bf"),
    "bath_1": RoomFinish(floor="d4_terrazzo", walls="d4_teal_glaze", **STRETCH),
    "bath_2": RoomFinish(floor="d4_terrazzo", walls="d4_terrazzo_wall", **STRETCH),
    "balcony": RoomFinish(floor="d4_teak_deck"),
}

# ---------------------------------------------------------------- removals (V1 pieces with no place in D4)
REMOVE = {
    # living: corner sofa, plush chairs, organic rug, round tables, wardrobe + its LEDs, infinity pendant,
    # floor lamp, gaming desk set, panel desk, pc tower
    "plush-corner-sofa-living-1", "organic-shag-rug-living-1", "round-coffee-table-living-1",
    "round-side-table-living-1", "plush-armchair-living-1", "plush-armchair-living-2", "wardrobe-living-1",
    "led-strip-living-1", "led-strip-living-3", "led-strip-living-4", "infinity-pendant-light-living-1",
    "floor-lamp-living-1", "panel-desk-living-1", "pc-tower-living-1",
    # kitchen: linear pendant, dining table (-> oval tulip)
    "linear-pendant-light-kitchen-1", "dining-table-kitchen-1",
    # hall: portal, slats, shelves and their decor
    "portal-jamb-hall-1", "portal-jamb-hall-2", "portal-head-hall-1", "slat-panel-hall-1", "slat-panel-hall-2",
    "wall-shelf-hall-1", "wall-shelf-hall-2", "plant-hall-1", "vase-hall-1", "vase-hall-2",
    # master: tv console (-> dresser on legs)
    "tv-console-master-suite-1",
    # kids: low cabinet (-> open toy shelf)
    "storage-cabinet-bedroom-1-1",
}
v.items = [it for it in v.items if it.local_id not in REMOVE]


def edit(local: str, **kw) -> None:
    for i, it in enumerate(v.items):
        if it.local_id == local:
            v.items[i] = replace(it, **kw)
            return
    raise KeyError(local)


def restore(local: str, fronts: dict[str, str], *, finish: dict[str, str] | None = None, **st) -> None:
    """Recolour a storage piece's module fronts ({old colour: new}) and storage fields."""
    for i, it in enumerate(v.items):
        if it.local_id == local:
            s = it.storage
            mods = tuple(replace(m, front_color=fronts.get(m.front_color.lower(), m.front_color),
                                 finish=(finish or {}).get(m.front_color.lower(), m.finish)) for m in s.modules)
            v.items[i] = replace(it, storage=replace(s, modules=mods, **st))
            return
    raise KeyError(local)


# ---------------------------------------------------------------- living (kept pieces)
edit("wall-tv-living-1", position=(2.1, 6.79), elevation=0.84,
     label="75\" TV hung on the walnut slat wall, centred over the teak credenza")
edit("slat-panel-living-1", size=(2.6, 0.03, 2.7), position=(2.1, 6.752), color=WALNUT,
     label="Walnut slat wall behind the TV (MCM wood panelling, fresh slatted take)")
edit("wallpaper-living-1", apron="d4_sunset_mural", color="#efe3cc",
     label="Supergraphic wave mural behind the sofa: cream / burnt orange (70s warmth)")
edit("sheer-curtain-living-1", color="#f6f1e6")
edit("sheer-curtain-living-2", color="#f6f1e6")
for k in (1, 2, 3, 4):
    edit(f"drape-living-{k}", color=RUST, label="Burnt-orange linen drape, stacked open")
edit("led-strip-living-2", label="Warm cove line along the window wall (ambient)")
edit("gaming-chair-living-1", position=(5.62, 10.1), color=CHAR,
     label="Ergonomic task chair (charcoal), at the teak desk")
edit("monitor-living-1", position=(6.62, 10.0), elevation=0.75)
edit("keyboard-living-1", position=(6.2, 10.0), elevation=0.75)
edit("mouse-living-1", position=(6.22, 9.66), elevation=0.75)
edit("bonsai-living-1", position=(6.62, 9.55), elevation=0.75)
edit("bird-of-paradise-living-1", position=(3.85, 7.12), label="Bird of paradise in a stone pot at the end of the credenza")

# ---------------------------------------------------------------- kitchen (fixed run kept, restyled)
for cab in ("base-cabinet-kitchen-1", "base-cabinet-kitchen-2", "base-cabinet-kitchen-3", "tall-cabinet-kitchen-1"):
    edit(cab, color=OLIVE)
    restore(cab, {"#cfc2ad": OLIVE, "#7a5236": OLIVE}, handle_color=BRASS, interior_color="#e9e1d2")
edit("plinth-kitchen-1", color=OLIVE)
edit("oven-kitchen-1", color=CHAR)
for k in (1, 2, 3, 4):
    edit(f"countertop-kitchen-{k}", color="#e8e0d0")
edit("wall-cabinet-kitchen-1", color=TEAK, label="Shallow teak wall units 1.50-2.10 m, lift-up push-to-open")
restore("wall-cabinet-kitchen-1", {"#7a5236": TEAK, "#cfc2ad": TEAK}, interior_color=TEAK)
edit("wall-cabinet-kitchen-2", color="#ebe3d4", label="Cream top boxes to the ceiling (blend with the walls)")
restore("wall-cabinet-kitchen-2", {"#cfc2ad": "#ebe3d4", "#7a5236": "#ebe3d4"}, interior_color="#ebe3d4")
edit("backsplash-kitchen-1", apron="d4_amber_glaze", color="#c98a34",
     label="Amber-mustard glazed 7.5 x 30 tiles, vertical stack")
edit("venetian-blind-kitchen-1", color=TEAK, label="Teak-tone wooden venetian blind")
for k in (1, 2, 5, 6):
    edit(f"upholstered-chair-kitchen-{k}", color=MUSTARD,
         label="Mustard velvet shell dining chair, slim brass legs")
edit("place-setting-kitchen-3", position=(1.86, 4.37))
edit("place-setting-kitchen-4", position=(2.94, 4.37))
edit("serving-bowl-kitchen-1", color="#e9d9b8")
edit("led-strip-kitchen-2", label="LED under the teak wall units (worktop task light)")

# ---------------------------------------------------------------- hall
edit("wardrobe-hall-1", color=OLIVE,
     label="Utility cupboard to the ceiling: vacuum, mop, ironing board, drying rack, cleaning shelf",
     note="D4: becomes the utility cupboard; coats + shoes go to D4.wardrobe-hall-2")
for i, it in enumerate(v.items):
    if it.local_id == "wardrobe-hall-1":
        s = it.storage
        m = replace(s.modules[0], front_color=OLIVE,
                    interior=tuple(f for f in s.modules[0].interior if f.kind == "shelf"))
        v.items[i] = replace(it, storage=replace(s, modules=(m,), handle_color=TEAK))
edit("doormat-hall-1", color="#6b4a2c")

# ---------------------------------------------------------------- bath 1
edit("vanity-frame-bathroom-1-1", color=TEAK)
edit("towels-bathroom-1-1", color=MUSTARD)
edit("vessel-sink-bathroom-1-1", color="#efe8da")
edit("tall-cabinet-bathroom-1-1", color=TEAK)
restore("tall-cabinet-bathroom-1-1", {"#3f2a1c": TEAK}, interior_color=TEAK)
edit("slat-screen-bathroom-1-1", color=TEAK)
edit("slat-screen-bathroom-1-2", color=TEAK)
edit("wall-niche-bathroom-1-1", color="#1f5f63")
edit("walk-in-shower-bathroom-1-1", accent="#ece3d2")

# ---------------------------------------------------------------- bath 2
edit("vanity-frame-master-bathroom-1", color=TEAK)
edit("towels-master-bathroom-1", color=RUST)
edit("vessel-sink-master-bathroom-1", color="#efe8da")
edit("tall-cabinet-master-bathroom-1", color=TEAK)
restore("tall-cabinet-master-bathroom-1", {"#3f2a1c": TEAK}, interior_color=TEAK)
edit("bathtub-master-bathroom-1", apron="d4_olive_glaze")
edit("wall-niche-master-bathroom-1", color="#7a7a3e")

# ---------------------------------------------------------------- kids' room
edit("floating-bed-bedroom-1-1", color=TEAK, accent=MUSTARD, tag_color=TEAL,
     label="Child's teak bed 90 x 200, mustard duvet - 'Baby Turi'")
edit("wallpaper-bedroom-1-1", apron="d4_sunrise_watercolor", color="#f3e8d6",
     label="Apricot-mustard watercolour sky on the bed wall")
edit("slat-panel-bedroom-1-1", color=TEAK)
edit("nightstand-bedroom-1-1", color=TEAK)
edit("table-lamp-bedroom-1-1", color=MUSTARD, label="Mushroom table lamp (nightlight on a dimmer)")
edit("rug-bedroom-1-1", color="#7fa39a", label="Soft sage-teal play rug")
edit("wardrobe-bedroom-1-1", color="#efe6d6", label="Kids' wardrobe: teal doors + cream column, teak handles")
restore("wardrobe-bedroom-1-1", {"#7f9fb0": "#3f7a7a"}, handle_color=TEAK)
edit("desk-bedroom-1-1", color=TEAK, label="Teak changing / drawing desk 90 x 45 (desk later)")
edit("chair-bedroom-1-1", color=MUSTARD)
edit("sheer-curtain-bedroom-1-1", color="#f6f1e6")
for k in (1, 2):
    edit(f"drape-bedroom-1-{k}", color="#c4922f", label="Mustard blackout drape")
edit("notebooks-bedroom-1-1", color=RUST)
edit("pencil-case-bedroom-1-1", color=TEAL)

# ---------------------------------------------------------------- master suite
BED_X = 1.85
edit("floating-bed-master-suite-1", position=(BED_X, 1.3), color="#8f5a33", accent=RUST,
     label="Teak floating bed 160 x 210, burnt-orange linen duvet")
edit("led-strip-master-suite-7", position=(BED_X, 1.3))
edit("wallpaper-master-suite-1", apron="d4_teak_chevron", color="#a2683c",
     label="Teak chevron panelling behind the bed")
edit("rug-master-suite-1", position=(BED_X, 1.75), size=(2.4, 2.6, 0.01), color=TEAL, label="Deep-teal wool rug")
edit("nightstand-master-suite-1", position=(0.8, 0.44), size=(0.4, 0.38, 0.32), elevation=0.26, color=TEAK,
     label="Wall-hung teak bedside drawer (left)")
edit("nightstand-master-suite-2", position=(2.87, 0.44), size=(0.38, 0.38, 0.32), elevation=0.26, color=TEAK,
     label="Wall-hung teak bedside drawer (right)")
edit("table-lamp-master-suite-1", position=(0.8, 0.44), elevation=0.58, color="#efe4cf",
     label="Opal mushroom reading lamp")
edit("table-lamp-master-suite-2", position=(2.87, 0.44), elevation=0.58, color="#efe4cf",
     label="Opal mushroom reading lamp")
edit("slat-panel-master-suite-1", position=(BED_X, 3.775), size=(2.2, 0.03, 2.7), color=WALNUT)
edit("wall-tv-master-suite-1", position=(BED_X, 3.742), elevation=1.02)
edit("sheer-curtain-master-suite-1", color="#f6f1e6")
for k in (1, 2):
    edit(f"drape-master-suite-{k}", color=TEAL, label="Deep-teal blackout drape")
for w in ("wardrobe-master-suite-1", "wardrobe-master-suite-2"):
    edit(w, color="#e9dfcc", label="Cream lacquer wardrobe with a teak column (lit niche, drawers), walnut bar handles")
    restore(w, {"#a08b78": "#e9dfcc", "#8a5f3e": TEAK}, handle_color=WALNUT, interior_color=TEAK)
# full-length mirror: the last door module of the dressing wardrobe gets a mirror front
for i, it in enumerate(v.items):
    if it.local_id == "wardrobe-master-suite-1":
        mods = list(it.storage.modules)
        mods[-1] = replace(mods[-1], finish="mirror", label="full-length mirror door")
        v.items[i] = replace(it, storage=replace(it.storage, modules=tuple(mods)))

# ---------------------------------------------------------------- balcony
edit("outdoor-dining-table-balcony-1", color=TEAK)
edit("outdoor-chair-balcony-1", color=TEAK)
edit("outdoor-chair-balcony-2", color=TEAK)
edit("mug-balcony-1", color=MUSTARD)
edit("mug-balcony-2", color=TEAL)

# ---------------------------------------------------------------- new pieces
NEW = (Path(__file__).resolve().parent / "new_items.toml").read_text(encoding="utf-8")
for d in tomllib.loads(NEW)["items"]:
    d["id"] = "D4." + d["id"]
    d.setdefault("status", "draft")
    v.items.append(_item(d))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(variant_to_toml(v), encoding="utf-8")
print(f"wrote {OUT} ({len(v.items)} pieces)")

# ---------------------------------------------------------------- late fixes (round 1)
_v = __import__("tomllib")
def _late():
    from apartment_core.furniture import variant_to_toml as _t
    edit("place-setting-kitchen-3", position=(1.84, 4.3))
    edit("place-setting-kitchen-4", position=(2.96, 4.3))
    edit("shoes-hall-1", position=(7.0, 4.72))
    edit("shoes-hall-2", position=(7.0, 5.05), rotation=0)
    OUT.write_text(_t(v), encoding="utf-8")
_late()

# ---------------------------------------------------------------- round 2 (after the first renders)
def _round2():
    from apartment_core.furniture import variant_to_toml as _t
    for k in (1, 2, 3, 4):  # the mural already brings the orange: calmer camel drapes
        edit(f"drape-living-{k}", color="#a8834f", label="Camel linen drape, stacked open")
    for k in (1, 2):
        edit(f"drape-bedroom-1-{k}", color="#6f9a92", label="Sage-teal blackout drape")
    v.rooms["hall"] = replace(v.rooms["hall"], paint="#eadcc3")
    v.items[:] = [it for it in v.items if it.local_id != "plant-master-suite-1"]
    extra = tomllib.loads('''
[[items]]
id = "D4.rug-hall-1"
type = "rug"
room = "hall"
size = [0.75, 2.2, 0.01]
position = [5.85, 5.35]
color = "#b4542a"
label = "Graphic hall runner: burnt orange..."
[[items]]
id = "D4.rug-hall-2"
type = "rug"
room = "hall"
size = [0.12, 2.2, 0.012]
position = [5.62, 5.35]
color = "#d19a2a"
label = "...with a mustard stripe"
[[items]]
id = "D4.rug-hall-3"
type = "rug"
room = "hall"
size = [0.05, 2.2, 0.013]
position = [6.08, 5.35]
color = "#1f5c60"
label = "...and a teal line"
[[items]]
id = "D4.vase-master-suite-1"
type = "vase"
room = "bedroom_2"
size = [0.16, 0.16, 0.34]
position = [2.42, 3.55]
elevation = 0.84
color = "#b4542a"
label = "Burnt-orange ceramic vase on the dresser"
[[items]]
id = "D4.vase-master-suite-2"
type = "vase"
room = "bedroom_2"
size = [0.12, 0.12, 0.22]
position = [2.25, 3.58]
elevation = 0.84
color = "#1f5c60"
label = "Teal bud vase"
''')
    for d in extra["items"]:
        v.items.append(_item(d))
    OUT.write_text(_t(v), encoding="utf-8")
_round2()
