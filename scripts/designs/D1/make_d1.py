"""Generate .tmp/designs/D1/variants/D1.toml - "Dune Cocoon" (Soft Curves / Cocooning Modern).

Starts from a re-keyed copy of V1 (keeps AC units, vents, fixed-point pieces), then restyles and re-plans.
Run:  uv run python .tmp/designs/D1/make_d1.py
"""
from dataclasses import replace
from pathlib import Path

from apartment_core.furniture import RoomFinish, _item, _storage, copy_variant, load_variant, variant_to_toml
from apartment_core.model import parse_finish

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "variants" / "D1.toml"

# ---------------------------------------------------------------- palette
CREAM = "#e6d3bd"      # cloud-cream walls / stretch ceilings
OAT = "#b8976f"        # oat boucle upholstery
CLAY = "#c99f8b"       # clay-rose (enveloping colour, master suite)
MOCHA = "#6e4b3a"      # mocha walnut joinery (wood 2)
SAND = "#cdb89a"       # travertine sand (stone)
RUST = "#9a4a30"       # accent 1: rust velvet
OCHRE = "#c9963f"      # accent 2: ochre
OAK = "#c49a6c"        # warm oak floor (wood 1)
BRASS = "#b08d57"      # brushed brass (metal 1); metal 2 = matte black (tracks, appliances)
FRONT_CREAM = "#e8dfd2"
PEACH = "#dcb29c"      # kids' doors - a lighter clay-rose
CLAY_UNITS = "#b98a74" # kitchen base units - deeper clay-rose

src = load_variant(ROOT / "data" / "variants" / "V1.toml")
v = copy_variant(src, "D1", "Dune Cocoon")
v = replace(v, description=("Soft Curves / Cocooning Modern: rounded oat-boucle and rust-velvet seating, oval pedestal "
                            "tables, pill (arch) mirrors and sculpted dune walls wrapped in cloud cream, clay-rose and "
                            "mocha walnut, lit softly from coves and low lamps."),
            based_on="V1", wall_color=CREAM, true_colors=True)

# ---------------------------------------------------------------- own finishes
FIN = {
    "d1_warm_oak": dict(kind="parquet", size=[1.5, 0.22], color=OAK, color2="#b0865a", joint_color="#6e4b3a",
                        joint=0.0015, direction="x", roughness=0.5,
                        note="warm natural oak, wide 22 cm planks (living, bedrooms)"),
    "d1_travertine": dict(kind="stone", size=[1.2, 0.6], color="#d6c3a6", color2="#bea98a", joint_color="#c4b092",
                          joint=0.002, roughness=0.45,
                          note="honed sand travertine-look porcelain 120 x 60 (hall, kitchen, bath floors - one stone)"),
    "d1_blush_zellige": dict(kind="tiles", size=[0.13, 0.13], color="#d6ab95", color2="#c4927b",
                             joint_color="#eadfd1", joint=0.003, roughness=0.15,
                             note="glossy blush-clay zellige 13 x 13 (kitchen backsplash)"),
    "d1_clay_plaster": dict(kind="stone", size=[1.2, 0.6], color="#d4b49b", color2="#bd977c", joint_color="#c7a68c",
                            joint=0.0015, roughness=0.55,
                            note="tadelakt-look clay-rose plaster panels (bath walls) - soft, seamless feel"),
    "d1_dune_ripple": dict(kind="ripple", size=[3.8, 2.65], color="#d4b896", color2="#ad8762", joint_color="#d4b896",
                           joint=0.0, roughness=0.85, note="sculpted dune ripple, warm sand (living sofa wall)"),
    "d1_clay_ripple": dict(kind="ripple", size=[3.04, 2.7], color="#bf8f78", color2="#9e6c57", joint_color="#bf8f78",
                           joint=0.0, roughness=0.85, note="dune ripple in clay-rose (master bed wall, colour drench)"),
    "d1_sunrise_sky": dict(kind="watercolor", size=[3.1, 2.7], color="#f3e7d8", color2="#e2a98a",
                           joint_color="#f3e7d8", joint=0.0, roughness=0.8,
                           note="watercolour apricot sunrise sky (child's bed wall)"),
    "d1_terracotta": dict(kind="tiles", size=[0.3, 0.3], color="#b9775a", color2="#a56649", joint_color="#d8c7ae",
                          joint=0.004, roughness=0.7, note="terracotta outdoor tiles 30 x 30 (balcony)"),
}
v.finishes.clear()
for n, f in FIN.items():
    v.finishes[n] = parse_finish(n, f)

LED = dict(stretch_ceiling=True, stretch_led_color="#ffc98f", stretch_led_w_per_m=7.0, stretch_color="#efe4d6")
v.rooms.clear()
v.rooms.update({
    "living": RoomFinish(floor="d1_warm_oak", paint="#d4b796", skirting="#b8977a", **LED),
    "hall": RoomFinish(floor="d1_travertine", paint="#d4b796", **LED),
    "kitchen": RoomFinish(floor="d1_travertine", paint="#d9c0a2"),
    "bath_1": RoomFinish(floor="d1_travertine", walls="d1_clay_plaster", **LED),
    "bath_2": RoomFinish(floor="d1_travertine", walls="d1_clay_plaster", **LED),
    "bedroom_1": RoomFinish(floor="d1_warm_oak", paint="#e8c5a8", skirting="#d0a88a"),
    "bedroom_2": RoomFinish(floor="d1_warm_oak", paint="#c4957f", skirting="#a87a65", **LED),
    "balcony": RoomFinish(floor="d1_terracotta"),
})

# ---------------------------------------------------------------- helpers
items = {it.local_id: it for it in v.items}
order = [it.local_id for it in v.items]


def mod(lid, **kw):
    items[lid] = replace(items[lid], **kw)


def rename(old, new, **kw):
    it = items.pop(old)
    items[new] = replace(it, id=f"D1.{new}", **kw)
    order[order.index(old)] = new


def drop(*lids):
    for lid in lids:
        items.pop(lid)
        order.remove(lid)


def add(lid, **d):
    d.setdefault("status", "draft")
    items[lid] = _item({"id": f"D1.{lid}", **d})
    order.append(lid)


def fronts(lid, cmap, **skw):
    it = items[lid]
    st = it.storage
    mods = tuple(replace(m, front_color=cmap.get(m.front_color, m.front_color)) for m in st.modules)
    items[lid] = replace(it, storage=replace(st, modules=mods, **skw))


# global recolour of V1 colours (then specific overrides below)
CMAP = {
    "#a08b78": FRONT_CREAM, "#8a5f3e": MOCHA, "#6b4a33": MOCHA, "#6b4428": MOCHA, "#3f2a1c": MOCHA,
    "#7a5236": MOCHA, "#cfc2ad": "#e3d3bf", "#efe6d6": "#f1e9dd", "#7f9fb0": PEACH, "#8ea8b6": "#d9ae8c",
    "#6f5646": "#cbb59a", "#d9cbb5": OAT, "#ecebe8": MOCHA, "#d8cfc2": "#efe3cf", "#151515": "#151515",
    "#c9a77c": OAK, "#9a6b43": "#a8794f", "#c4b6a4": "#cdb29b", "#4e3322": MOCHA,
}
for lid, it in list(items.items()):
    if it.color.lower() in CMAP:
        items[lid] = replace(it, color=CMAP[it.color.lower()])
    if items[lid].storage is not None:
        fronts(lid, CMAP, handle_color=BRASS, interior_color=MOCHA)

# ================================================================= LIVING
# conversation circle: oat plush L-sofa + two round rust-velvet tub chairs around an oval travertine table
mod("plush-corner-sofa-living-1", color=OAT, accent=MOCHA,
    label="Oat boucle plush L-sofa with rolled edges, chaise to the balcony side",
    note="D1: the cocoon of the room - deep, rounded, oat boucle")
rename("organic-shag-rug-living-1", "organic-shag-rug-living-1", color="#b9997a", size=(3.5, 2.6, 0.012),
       position=(2.95, 8.85), label="Cream pebble shag rug - soft organic outline")
rename("round-coffee-table-living-1", "round-coffee-table-living-1", size=(1.15, 0.72, 0.38), position=(3.1, 9.0),
       color=SAND, label="Oval travertine pedestal coffee table 115 x 72")
mod("round-side-table-living-1", color=MOCHA, size=(0.45, 0.45, 0.5), label="Mocha walnut drum side table (lamp)")
rename("plush-armchair-living-1", "tub-armchair-living-1", type="tub-armchair", size=(0.82, 0.8, 0.74),
       color=RUST, position=(4.5, 9.2), rotation=110, label="Round tub chair, rust velvet")
rename("plush-armchair-living-2", "tub-armchair-living-2", type="tub-armchair", size=(0.82, 0.8, 0.74),
       color=RUST, position=(1.85, 8.3), rotation=313.5, label="Round tub chair, rust velvet")
rename("infinity-pendant-light-living-1", "ring-pendant-light-living-1", type="ring-pendant-light",
       size=(1.0, 1.0, 0.75), position=(3.1, 9.0), elevation=1.95, color=BRASS,
       label="Halo ring pendant 100 cm, brushed brass, glowing underside, over the oval table")
mod("floor-lamp-living-1", color=MOCHA, size=(0.42, 0.42, 1.55), label="Mushroom floor lamp, linen shade (reading)")
add("table-lamp-living-1", type="table-lamp", room="living", size=(0.26, 0.26, 0.38), position=(2.25, 9.3),
    elevation=0.5, color="#efe3cf", label="Small mushroom lamp on the side table",
    light={"kind": "point", "watts": 8, "color": "#ffcf96", "size": 0.1})
mod("wallpaper-living-1", apron="d1_dune_ripple", color="#e3cdb3", label="Sculpted dune ripple wall (sand) behind the sofa")
mod("slat-panel-living-1", color=MOCHA, label="Fluted mocha-walnut TV wall")
mod("wardrobe-living-1", label="Cream living wardrobe with mocha column: m1 utility (vacuum, ironing board, mop), books, linen",
    note="D1: the hall-end module is the tall utility cupboard")
rename("panel-desk-living-1", "round-desk-living-1", type="round-desk", size=(1.6, 0.8, 0.75),
       position=(6.38, 10.1), rotation=90, color="#ece3d6",
       label="Oval tulip desk 160 x 80 (cream lacquer, pedestal) - soft curve, side-lit from W1")
for lid in ("monitor-living-1", "keyboard-living-1", "mouse-living-1", "pc-tower-living-1", "bonsai-living-1"):
    mod(lid, elevation=0.75)
mod("pc-tower-living-1", position=(6.5, 9.55))
mod("gaming-chair-living-1", color="#cdb89c", label="Ergonomic work chair, oat boucle")
for lid in ("drape-living-1", "drape-living-2", "drape-living-3", "drape-living-4"):
    mod(lid, color="#cbb59a")
for lid in ("sheer-curtain-living-1", "sheer-curtain-living-2", "sheer-curtain-bedroom-1-1",
            "sheer-curtain-master-suite-1"):
    mod(lid, color="#f3e9db")
add("vase-living-1", type="vase", room="living", size=(0.3, 0.3, 0.55), position=(4.99, 6.93), color="#b98a74",
    label="Sculptural clay floor vase by the portal")

# ================================================================= HALL
# rectangular wood portal removed (soft, open passage); curved-seat shoe bench + tall pill (arch) mirror
# (portal pieces were removed from V1 itself, owner 2026-10-05)
mod("wardrobe-hall-1", color=FRONT_CREAM, label="Cream hall wardrobe: coats + shoes, brass bar handles")
add("shoe-cabinet-hall-2", type="shoe-cabinet", room="hall", size=(0.9, 0.38, 0.44), position=(5.015, 5.82),
    rotation=270, color=MOCHA, label="Mocha shoe bench: 2 tilt-out shoe drawers, seat on top",
    storage={"handles": False, "modules": [{"width": 0.45, "fronts": [{"kind": "flap"}]},
                                           {"width": 0.45, "fronts": [{"kind": "flap"}]}]})
add("seat-cushion-hall-1", type="seat-cushion", room="hall", size=(0.88, 0.36, 0.07), position=(5.015, 5.82),
    rotation=270, elevation=0.44, color=OAT, label="Oat boucle seat pad on the shoe bench")
add("backlit-mirror-hall-1", type="backlit-mirror", room="hall", size=(0.6, 0.02, 1.3), position=(4.837, 5.82),
    rotation=270, elevation=0.85, color="#d9dde0", metal=BRASS,
    label="Tall pill (arch) mirror with warm halo over the bench")

# ================================================================= KITCHEN
for lid in ("base-cabinet-kitchen-1", "base-cabinet-kitchen-2", "base-cabinet-kitchen-3"):
    mod(lid, color=CLAY_UNITS)
    fronts(lid, {"#e3d3bf": CLAY_UNITS})
mod("oven-kitchen-1", color="#ece3d6")
mod("plinth-kitchen-1", color=CLAY_UNITS)
for lid in ("countertop-kitchen-1", "countertop-kitchen-2", "countertop-kitchen-3", "countertop-kitchen-4"):
    mod(lid, color=SAND)
mod("backsplash-kitchen-1", apron="d1_blush_zellige", color="#d6ab95", label="Blush-clay zellige backsplash")
rename("dining-table-kitchen-1", "round-dining-table-kitchen-1", type="round-dining-table", size=(1.8, 0.9, 0.75),
       position=(2.4, 4.38), color=MOCHA,
       label="Oval pedestal dining table 180 x 90 (mocha walnut): 4 daily (2 + 2 ends), 5-6 occasional")
for lid, pos in (("upholstered-chair-kitchen-1", (2.0, 5.1)), ("upholstered-chair-kitchen-2", (2.8, 5.1)),
                 ("upholstered-chair-kitchen-5", (1.25, 4.38)), ("upholstered-chair-kitchen-6", (3.55, 4.38))):
    mod(lid, color=OAT, position=pos)
for lid, pos in (("place-setting-kitchen-1", (2.0, 4.68)), ("place-setting-kitchen-2", (2.8, 4.68)),
                 ("place-setting-kitchen-3", (1.74, 4.32)), ("place-setting-kitchen-4", (3.06, 4.32)),
                 ("serving-bowl-kitchen-1", (2.4, 4.3))):
    mod(lid, position=pos)
mod("serving-bowl-kitchen-1", color="#c98b6b")
rename("linear-pendant-light-kitchen-1", "ring-pendant-light-kitchen-1", type="ring-pendant-light",
       size=(0.8, 0.8, 1.15), position=(2.4, 4.38), elevation=1.55, color=BRASS,
       label="Brass halo ring 80 cm over the oval table")
mod("venetian-blind-kitchen-1", color="#efe6da")

# ================================================================= BATHS (fixed points untouched; restyle)
for lid in ("vanity-frame-bathroom-1-1", "vanity-frame-master-bathroom-1", "tall-cabinet-bathroom-1-1",
            "tall-cabinet-master-bathroom-1", "slat-screen-bathroom-1-1", "slat-screen-bathroom-1-2"):
    mod(lid, color=MOCHA)
mod("bathtub-master-bathroom-1", apron="d1_clay_plaster")
for lid in ("vessel-sink-bathroom-1-1", "vessel-sink-master-bathroom-1"):
    mod(lid, color="#efe7dc")
for lid in ("towels-bathroom-1-1", "towels-master-bathroom-1"):
    mod(lid, color="#e6d3bd")
mod("wall-niche-bathroom-1-1", color="#cdb29b")
mod("wall-niche-master-bathroom-1", color="#cdb29b")

# ================================================================= KIDS (bedroom 1)
mod("floating-bed-bedroom-1-1", color="#dcbfa2", tag_color=RUST)
mod("wallpaper-bedroom-1-1", apron="d1_sunrise_sky", color="#f3e7d8", label="Apricot sunrise watercolour mural")
rename("rug-bedroom-1-1", "organic-rug-bedroom-1-1", type="organic-rug", color="#d9b98a", size=(2.6, 2.2, 0.01),
       label="Soft ochre pebble rug (play area)")
mod("nightstand-bedroom-1-1", position=(10.015, 8.72), color="#f1e9dd",
    label="Rounded-look cream bedside drawers (moved to the door side of the bed)")
mod("table-lamp-bedroom-1-1", position=(10.015, 8.72), color="#f3e2c9", label="Mushroom nightlight lamp")
add("tub-armchair-bedroom-1-1", type="tub-armchair", room="bedroom_1", size=(0.68, 0.66, 0.68),
    position=(9.6, 10.36), rotation=200, color=OCHRE,
    label="Low round nursing / reading chair, ochre boucle (no corners)")
mod("chair-bedroom-1-1", color=OCHRE)
mod("slat-panel-bedroom-1-1", color=OAK)
mod("desk-bedroom-1-1", color=OAK, label="Changing / homework desk 90 x 45, oak")
mod("wardrobe-bedroom-1-1", label="Peach + cream wardrobe 1.80 m, brass handles")

# ================================================================= MASTER SUITE (colour drench)
mod("floating-bed-master-suite-1", position=(1.85, 1.3), color="#b89a7a", accent="#c9ad8c",
    label="Floating bed 160 x 200 with an oat boucle upholstered headboard")
mod("led-strip-master-suite-7", position=(1.85, 1.3))
mod("nightstand-master-suite-1", position=(0.78, 0.45), color=MOCHA)
mod("table-lamp-master-suite-1", position=(0.78, 0.45))
mod("nightstand-master-suite-2", position=(2.9, 0.45), size=(0.42, 0.4, 0.5), color=MOCHA)
mod("table-lamp-master-suite-2", position=(2.9, 0.45))
rename("rug-master-suite-1", "organic-rug-master-suite-1", type="organic-rug", color="#c9ad8c",
       size=(2.7, 2.5, 0.01), position=(1.85, 1.75), label="Cream pebble rug under the bed")
mod("wallpaper-master-suite-1", apron="d1_clay_ripple", color="#bf8f78",
    label="Clay-rose dune ripple behind the bed (colour-drenched cocoon)")
for lid in ("drape-master-suite-1", "drape-master-suite-2"):
    mod(lid, color="#8e5a46", label="Blackout velvet drape, deep clay")
mod("tv-console-master-suite-1", position=(2.05, 3.56), size=(1.3, 0.4, 0.5), color=FRONT_CREAM,
    storage=None, label="Cream console 140 cm (drawers)")
mod("wall-tv-master-suite-1", position=(2.05, 3.738))
mod("slat-panel-master-suite-1", position=(2.05, 3.775), size=(1.5, 0.03, 2.7), color=MOCHA)
add("tub-armchair-master-suite-1", type="tub-armchair", room="bedroom_2", size=(0.7, 0.7, 0.72),
    position=(0.95, 3.44), rotation=180, color=RUST, label="Round rust-velvet tub chair (dressing / reading)")
add("backlit-mirror-master-suite-1", type="backlit-mirror", room="bedroom_2", size=(0.5, 0.02, 1.7),
    position=(5.92, 2.186), elevation=0.25, color="#d9dde0", metal=BRASS,
    label="Full-length pill (arch) mirror in the dressing")
# wardrobe on the bath-2 wall: bed-side module becomes an open lit shelf column (no door swing at the bedside)
w2 = items["wardrobe-master-suite-2"]
m3 = _storage({"modules": [{"width": 0.6, "fronts": [{"kind": "open"}], "finish": "wood", "front_color": MOCHA,
                            "label": "open bedside shelves",
                            "interior": [{"kind": "shelf", "z": z} for z in (0.55, 0.95, 1.35, 1.75, 2.15)]}]}).modules[0]
items["wardrobe-master-suite-2"] = replace(w2, storage=replace(w2.storage, modules=(*w2.storage.modules[:2], m3)),
    label="Cream wardrobe 1.80 m: doors, lit mocha column, open shelf column at the bedside (no door swing there)")

# ================================================================= BALCONY
mod("outdoor-dining-table-balcony-1", color="#a8794f")
add("plant-balcony-1", type="plant", room="balcony", size=(0.45, 0.45, 0.9), position=(-0.35, 10.55), color="#6b7a45",
    label="Olive in a terracotta pot")
add("table-lamp-balcony-1", type="table-lamp", room="balcony", size=(0.2, 0.2, 0.3), position=(-0.85, 8.05),
    elevation=0.74, color="#efe3cf", label="Cordless mushroom lantern (outdoor)",
    light={"kind": "point", "watts": 5, "color": "#ffcf96", "size": 0.08})

mod("shoes-hall-1", position=(5.4, 5.55), rotation=270)
mod("shoes-hall-2", position=(5.4, 6.05), rotation=270)

v.items[:] = [items[k] for k in order]
OUT.write_text(variant_to_toml(v), encoding="utf-8")
print("wrote", OUT, len(v.items), "items")
