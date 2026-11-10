"""Generate variant D3 "Biophilic Modern" from V1 (private sandbox, .tmp/designs/D3).

Run:  uv run python .tmp/designs/D3/make_d3.py   -> .tmp/designs/D3/variants/D3.toml
Shell, fixed points, AC units and heat-recovery vents are copied from V1 untouched (positions).
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from apartment_core.furniture import (
    Fitting,
    Front,
    Item,
    Light,
    Module,
    Storage,
    TrackHead,
    copy_variant,
    load_variant,
    variant_to_toml,
)
from apartment_core.model import parse_finish

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "variants" / "D3.toml"
K = "D3"

# ------------------------------------------------------------------ palette
LIME = "#ece5d8"      # clay-white limewash walls
OAT = "#c9b998"       # oatmeal linen
SAGE = "#8d9a72"      # sage (kitchen units, textiles)
SAGE_LT = "#b3bca2"   # pale sage (kids, cushions)
MOSS = "#6b7553"      # deep moss (armchairs, master drapes)
OAK = "#c4a079"       # light oak (wood 1)
CANE = "#b08453"      # honey cane / teak (wood 2 - rattan, cane, outdoor teak)
STONE = "#cfbe9f"     # travertine / limestone
CLAY = "#b5694b"      # terracotta accent
BRASS = "#a8864f"     # aged brass (metal 1)
BLACK = "#1e1e1e"     # matte black (metal 2)
WARM = "#ffd29e"      # ~2700 K
LEAF = "#3f6b35"
LEAF2 = "#4f7a3a"
LEAF3 = "#5d8a46"

v1 = load_variant(ROOT / "data" / "variants" / "V1.toml")
d3 = copy_variant(v1, K, "Biophilic Modern - Light & Leaf")
d3.description = ("Biophilic Modern: a light-led home where every room looks to daylight and a living plant - limewash "
                  "clay-white walls, light oak, cane and travertine, sage and moss linens, a preserved-moss media wall, "
                  "a plant-and-book wall, herbs in the kitchen, ferns in the baths and the balcony as a terracotta "
                  "garden room.")
d3.based_on = "V1"
d3.wall_color = LIME
d3.true_colors = True

# ------------------------------------------------------------------ own finishes
F = {
    "d3_oak": dict(kind="parquet", size=[1.80, 0.20], color="#cdab82", color2="#bb966b", joint_color="#8a6a4a",
                   joint=0.0015, direction="x", roughness=0.5,
                   note="light natural oak, wide 180 x 20 planks, matte oiled (living, both bedrooms)"),
    "d3_limestone": dict(kind="stone", size=[1.20, 0.60], color="#ddd2bd", color2="#c6b79c", joint_color="#cbbda5",
                         joint=0.002, roughness=0.45,
                         note="honed warm limestone-look 60 x 120 (hall + kitchen: one floor that flows)"),
    "d3_limestone_sq": dict(kind="stone", size=[0.60, 0.60], color="#d6c9b2", color2="#bfae92",
                            joint_color="#b9aa90", joint=0.003, roughness=0.5,
                            note="same limestone, 60 x 60, slip-resistant honed (bath floors)"),
    "d3_sage_zellige": dict(kind="stone", size=[0.13, 0.13], color="#93a48a", color2="#6f8568",
                            joint_color="#ddd5c6", joint=0.002, roughness=0.22,
                            note="handmade-look sage zellige 13 x 13, glossy, uneven glaze (bath 1 walls)"),
    "d3_cream_zellige": dict(kind="stone", size=[0.13, 0.13], color="#efe7d7", color2="#d7c9b0",
                             joint_color="#e2d8c6", joint=0.002, roughness=0.2,
                             note="cream zellige 13 x 13 (kitchen backsplash)"),
    "d3_clay_plaster": dict(kind="stone", size=[1.20, 1.20], color="#d9c5a7", color2="#c3a985",
                            joint_color="#d1bc9c", joint=0.0005, roughness=0.7,
                            note="tadelakt-style clay lime plaster, soft clouding, almost seamless (bath 2 walls + tub)"),
    "d3_moss": dict(kind="stone", size=[3.00, 2.65], color="#62793f", color2="#3d5230", joint_color="#4f6638",
                    joint=0.0, roughness=0.97,
                    note="preserved (no-water) moss panel: mottled moss + fern greens, one piece (living media wall)"),
    "d3_leaf_watercolor": dict(kind="watercolor", size=[3.10, 2.70], color="#eef0e4", color2="#98b08a",
                               joint_color="#eef0e4", joint=0.0, roughness=0.85,
                               note="soft sage watercolour 'forest canopy' mural (kids' bed wall)"),
    "d3_dune_sage": dict(kind="ripple", size=[3.04, 2.70], color="#e2e4d6", color2="#b3baa0", joint_color="#e2e4d6",
                         joint=0.0, roughness=0.9,
                         note="sculpted dune-ripple wall covering in pale sage (master bed wall)"),
    "d3_terracotta": dict(kind="stone", size=[0.30, 0.30], color="#b8714f", color2="#a05e41",
                          joint_color="#d8c9b0", joint=0.004, roughness=0.75,
                          note="frost-proof terracotta 30 x 30, cream joints (balcony garden room)"),
}
d3.finishes = {n: parse_finish(n, f) for n, f in F.items()}

R = {}
from apartment_core.furniture import RoomFinish  # noqa: E402

R["living"] = RoomFinish(floor="d3_oak", stretch_ceiling=True, stretch_led_color="#ffc98f", stretch_led_w_per_m=7.0,
                         skirting="#b08a62")
R["hall"] = RoomFinish(floor="d3_limestone", stretch_ceiling=True, stretch_led_color="#ffc98f", stretch_led_w_per_m=7.0)
R["kitchen"] = RoomFinish(floor="d3_limestone")
R["bath_1"] = RoomFinish(floor="d3_limestone_sq", walls="d3_sage_zellige", stretch_ceiling=True,
                         stretch_led_color="#ffc98f", stretch_led_w_per_m=7.0)
R["bath_2"] = RoomFinish(floor="d3_limestone_sq", walls="d3_clay_plaster", stretch_ceiling=True,
                         stretch_led_color="#ffc98f", stretch_led_w_per_m=7.0)
R["bedroom_1"] = RoomFinish(floor="d3_oak", skirting="#b08a62", paint="#eee9de")
R["bedroom_2"] = RoomFinish(floor="d3_oak", skirting="#b08a62", paint="#d3d6c4")
R["balcony"] = RoomFinish(floor="d3_terracotta")
d3.rooms = R

# ------------------------------------------------------------------ helpers
items: dict[str, Item] = {it.local_id: it for it in d3.items}
order: list[str] = [it.local_id for it in d3.items]
SLUG = {"living": "living", "kitchen": "kitchen", "hall": "hall", "balcony": "balcony", "bedroom_1": "bedroom-1",
        "bath_1": "bathroom-1", "bedroom_2": "master-suite", "bath_2": "master-bathroom"}


def keep(local: str, **kw) -> None:
    it = items[local]
    kw.setdefault("status", "draft")
    items[local] = replace(it, **kw)


def drop(*locals_: str) -> None:
    for loc in locals_:
        del items[loc]
        order.remove(loc)


def add(type_: str, room: str, size, pos, **kw) -> str:
    n = 1
    while f"{type_}-{SLUG[room]}-{n}" in items:
        n += 1
    loc = f"{type_}-{SLUG[room]}-{n}"
    items[loc] = Item(id=f"{K}.{loc}", type=type_, room=room, size=tuple(size), position=tuple(pos), **kw)
    order.append(loc)
    return loc


def lt(watts: float, size: float, kind: str = "rect", **kw) -> Light:
    return Light(kind=kind, watts=watts, color=WARM, size=size, **kw)


def recolor(st: Storage, fronts: dict, **kw) -> Storage:
    mods = tuple(replace(m, front_color=fronts.get(m.front_color, m.front_color)) for m in st.modules)
    return replace(st, modules=mods, **kw)


# ================================================================== LIVING
drop("wardrobe-living-1", "led-strip-living-1", "led-strip-living-3", "led-strip-living-4",
     "infinity-pendant-light-living-1", "plush-armchair-living-1", "plush-armchair-living-2",
     "organic-shag-rug-living-1", "slat-panel-living-1", "panel-desk-living-1", "bonsai-living-1",
     )
keep("plush-corner-sofa-living-1", color=OAT, accent=OAK,
     label="Plush oatmeal-linen corner sofa, light-oak base, chaise towards the balcony garden",
     note="D3: back to the WNW wall - no evening glare on the TV, faces the moss wall")
keep("round-coffee-table-living-1", color=STONE, size=(0.9, 0.9, 0.38),
     label="Round travertine coffee table (organic stone)", note="D3")
keep("round-side-table-living-1", color=OAK, label="Light-oak side table in the chaise corner", note="D3")
keep("bird-of-paradise-living-1", size=(0.6, 0.6, 1.75), position=(0.98, 7.1), color=LEAF,
     label="Bird of paradise beside the balcony door - the sunniest indoor spot (SSW, midday + afternoon)",
     note="D3: sun study 2026-10-04 13:00-16:00: direct sun through the balcony door")
add("organic-rug", "living", (3.4, 2.5, 0.01), (2.95, 8.95), color="#b39c70",
    label="Organic pebble rug, natural jute-wool", note="D3: soft acoustics, natural fibre")
add("tub-armchair", "living", (0.8, 0.8, 0.74), (4.3, 9.5), rotation=100, color=MOSS, accent=OAK,
    label="Round moss-green velvet tub chair, turned to the sofa", note="D3: seat 4")
add("tub-armchair", "living", (0.8, 0.8, 0.74), (4.3, 8.5), rotation=80, color=MOSS, accent=OAK,
    label="Round moss-green velvet tub chair, turned to the sofa",
    note="D3: seat 5; keeps a 1.0 m path TV wall -> balcony door")
add("bird-of-paradise", "living", (0.48, 0.48, 1.95), (0.72, 10.55), color="#3d5e30",
    label="Giant white bird of paradise (Strelitzia nicolai), corner by the balcony door - bright, sheer-filtered",
    note="D3")
add("bird-of-paradise", "living", (0.44, 0.44, 1.3), (4.1, 10.45), color=LEAF2,
    label="Orange bird of paradise (Strelitzia reginae) between the sofa and W1 (WNW afternoon sun)", note="D3")
keep("floor-lamp-living-1", size=(0.35, 0.35, 1.6), position=(0.75, 9.75), color="#e8dcc6",
    label="Linen-shade floor lamp at the chaise - reading light", note="D3: task layer",
    light=lt(22, 0.1, "point"))
add("rattan-pendant-light", "living", (0.62, 0.62, 0.7), (2.95, 9.0), elevation=1.95, color=CANE,
    label="Woven rattan dome pendant over the coffee table (statement light, casts shadows)", note="D3: ambient + mood",
    light=Light(kind="point", watts=40, color=WARM, size=0.08))
# media wall: preserved moss + floating oak sideboard + TV
add("wallpaper", "living", (3.0, 0.004, 2.65), (2.6, 6.739), color="#6a7f48", apron="d3_moss",
    label="Preserved-moss wall behind the TV (no water, no light needed)", note="D3: biophilic hero wall")
keep("wall-tv-living-1", size=(1.72, 0.035, 0.99), position=(2.6, 6.79), elevation=0.62,
     label="77-inch TV on the moss wall (seat ~3.2 m = 1.6 x diagonal)", note="D3")
add("media-sideboard", "living", (2.4, 0.4, 0.4), (2.6, 6.945), elevation=0.15, color=OAK,
    label="Floating light-oak media sideboard, cane-look doors + drawers (media + closed storage)", note="D3",
    storage=Storage(plinth=0.0, handles=False, interior_color=OAK, modules=(
        Module(0.8, (Front("doors"),), "wood", CANE, label="cane doors"),
        Module(0.8, (Front("drawers", count=2),), "wood", OAK),
        Module(0.8, (Front("doors"),), "wood", CANE, label="cane doors"))))
add("bonsai", "living", (0.3, 0.22, 0.34), (1.75, 6.95), elevation=0.55, color="#4f6b34",
    label="Bonsai on the sideboard", note="D3: moved from the desk")
add("trailing-plant", "living", (0.34, 0.24, 0.2), (3.55, 6.96), elevation=0.55, color=LEAF3,
    label="Trailing string-of-hearts on the sideboard", note="D3")
add("vase", "living", (0.14, 0.14, 0.3), (3.25, 6.95), elevation=0.55, color=CLAY,
    label="Terracotta vase", note="D3: accent")
# plant + book wall (replaces the living wardrobe)
add("bookcase", "living", (2.4, 0.4, 2.25), (6.6, 7.99), rotation=90, color=OAK,
    label="Plant & book wall: open light-oak shelves over closed doors / drawers (books, media, paperwork)",
    note="D3: replaces V1's living wardrobe; drawers next to the desk hold the paperwork",
    storage=Storage(handle_color=BRASS, interior_color=OAK, modules=(
        Module(0.8, (Front("open"), Front("doors", 0.78)), "wood", OAK,
               interior=(Fitting("shelf", 1.25), Fitting("shelf", 1.7))),
        Module(0.8, (Front("open"), Front("drawers", 0.78, 2)), "wood", CANE, label="paperwork drawers",
               interior=(Fitting("shelf", 1.25), Fitting("shelf", 1.7))),
        Module(0.8, (Front("open"), Front("doors", 0.78)), "wood", OAK,
               interior=(Fitting("shelf", 1.25), Fitting("shelf", 1.7))))))
add("trailing-plant", "living", (0.3, 0.5, 0.24), (6.6, 7.15), elevation=2.25, color=LEAF2,
    label="Pothos trailing from the top of the plant wall", note="D3")
add("trailing-plant", "living", (0.3, 0.5, 0.24), (6.6, 8.75), elevation=2.25, color=LEAF3,
    label="Philodendron trailing from the top of the plant wall", note="D3")
add("plant", "living", (0.22, 0.26, 0.24), (6.6, 7.55), elevation=1.25, color=LEAF,
    label="Small fern on the shelf", note="D3")
add("plant", "living", (0.22, 0.24, 0.22), (6.6, 8.4), elevation=1.7, color=LEAF2,
    label="Peperomia on the shelf", note="D3")
add("books", "living", (0.42, 0.24, 0.26), (6.62, 8.1), rotation=90, elevation=1.25, color=CLAY,
    label="Books", note="D3")
add("books", "living", (0.5, 0.24, 0.24), (6.62, 7.35), rotation=90, elevation=1.7, color=SAGE,
    label="Books", note="D3")
add("books", "living", (0.36, 0.24, 0.26), (6.62, 8.85), rotation=90, elevation=1.25, color="#e4dccb",
    label="Books", note="D3")
add("vase", "living", (0.13, 0.13, 0.2), (6.6, 8.75), elevation=1.7, color="#e9e1d2", label="Stoneware vase",
    note="D3")
add("led-strip", "living", (2.3, 0.02, 0.01), (6.43, 7.99), rotation=90, elevation=2.22, color="#c9c9c9",
    label="LED under the top board of the plant wall: lights the shelves and plants (accent)", note="D3",
    light=lt(14, 2.3))
# desk (work from home) - side-lit by W1, back to nothing, screen away from the window
add("panel-desk", "living", (1.6, 0.75, 0.75), (6.425, 10.1), rotation=90, color=OAK,
    label="Light-oak work desk 160 x 75, side-lit by W1 (no screen glare)", note="D3")
keep("monitor-living-1", position=(6.64, 10.1), elevation=0.75)
keep("keyboard-living-1", position=(6.25, 10.1), elevation=0.75)
keep("mouse-living-1", position=(6.27, 9.75), elevation=0.75)
keep("pc-tower-living-1", position=(6.58, 9.47), elevation=0.75)
keep("gaming-chair-living-1", color="#7a8270", label="Ergonomic task chair, sage-grey fabric")
add("table-lamp", "living", (0.22, 0.22, 0.42), (6.62, 10.7), elevation=0.75, color="#e8dcc6",
    label="Linen desk lamp (task)", note="D3", light=lt(14, 0.1, "point"))
# curtains: linen
for loc in ("sheer-curtain-living-1", "sheer-curtain-living-2"):
    keep(loc, color="#f7f3ea", label="Linen sheer (filters the WNW / SSW sun for the plants)")
for loc in ("drape-living-1", "drape-living-2", "drape-living-3", "drape-living-4"):
    keep(loc, color="#c8b998", label="Oat linen drape, stacked open (keeps the views)")
keep("led-strip-living-2")

# ================================================================== HALL
keep("wardrobe-hall-1", color=OAK, label="Floating light-oak coat + shoe wardrobe (coats, drawer, shoe flap)",
     storage=recolor(items["wardrobe-hall-1"].storage, {"#a08b78": OAK}, handle_color=BRASS,
                     interior_color="#d9c4a4"))
add("shoe-cabinet", "hall", (0.95, 0.38, 0.46), (5.015, 5.81), rotation=270, color=OAK,
    label="Oak shoe bench: shoe drawers below, seat on top (to put shoes on)", note="D3: hall seat + shoes",
    storage=Storage(handle_color=BRASS, plinth=0.06, modules=(
        Module(0.475, (Front("drawers", count=2),), "wood", CANE), Module(0.475, (Front("drawers", count=2),), "wood", CANE))))
add("seat-cushion", "hall", (0.9, 0.34, 0.05), (5.0, 5.81), rotation=270, elevation=0.46, color=SAGE,
    label="Sage linen seat cushion", note="D3")
add("backlit-mirror", "hall", (0.6, 0.02, 1.0), (4.836, 5.81), rotation=270, elevation=1.0, color="#d9dde0",
    metal=BRASS, label="Pill mirror with brass frame + soft halo over the bench", note="D3")
keep("wall-shelf-hall-1", color=OAK)
keep("wall-shelf-hall-2", color=OAK)
keep("plant-hall-1", color=LEAF3, label="Pothos (low light) on the shelf")
keep("vase-hall-1", color="#e9e1d2")
keep("vase-hall-2", color=CLAY)
add("snake-plant", "hall", (0.28, 0.28, 0.9), (7.0, 4.76), color="#4e6b3c",
    label="Snake plant in a clay pot (tolerates the windowless hall)", note="D3: corner by the door hinge")
drop("shoes-hall-1", "shoes-hall-2")
keep("doormat-hall-1", color="#a88b5e", label="Coir doormat")
keep("track-light-hall-2", track=replace(items["track-light-hall-2"].track, heads=(
    TrackHead(-0.6, (5.2, 4.4, 0.0)), TrackHead(0.6, (5.8, 6.6, 0.0)), TrackHead(0.0, (4.84, 5.83, 1.3)))))
keep("slat-panel-hall-1", color=OAK)

# ================================================================== KITCHEN
drop("base-cabinet-kitchen-1", "base-cabinet-kitchen-2", "base-cabinet-kitchen-3", "tall-cabinet-kitchen-1",
     "countertop-kitchen-1", "countertop-kitchen-2", "countertop-kitchen-3", "countertop-kitchen-4",
     "glass-fridge-kitchen-1", "wall-cabinet-kitchen-1", "wall-cabinet-kitchen-2", "led-strip-kitchen-2",
     "backsplash-kitchen-1", "dining-table-kitchen-1", "upholstered-chair-kitchen-1", "upholstered-chair-kitchen-2",
     "upholstered-chair-kitchen-5", "upholstered-chair-kitchen-6", "linear-pendant-light-kitchen-1",
     "place-setting-kitchen-1", "place-setting-kitchen-2", "place-setting-kitchen-3", "place-setting-kitchen-4",
     "serving-bowl-kitchen-1")
Y_RUN = 6.312
BASE = dict(handle_color=BRASS, plinth=0.09)
keep("oven-kitchen-1", color=SAGE)
keep("plinth-kitchen-1", color=SAGE)
keep("cooktop-kitchen-1")
keep("hood-visor-kitchen-1", color=BLACK)
keep("black-sink-kitchen-1", position=(3.55, 6.33), color="#2b2b2b",
     label="Matte black undermount sink + gooseneck tap under the open shelves")
add("base-cabinet", "kitchen", (0.6, 0.6, 0.87), (1.35, Y_RUN), rotation=180, color=SAGE,
    label="Sage drawers beside the hob (pots, pans)", note="D3: 60 cm landing beside the hob",
    storage=Storage(**BASE, modules=(Module(0.6, (Front("drawers", count=3),), "matte", SAGE),)))
add("fridge", "kitchen", (0.6, 0.6, 2.1), (1.95, Y_RUN), rotation=180, color=SAGE, tag="FRIDGE",
    label="Integrated fridge-freezer column (sage panel) between hob and sink",
    note="D3: work triangle on one line - hob 1.2 m fridge 1.6 m sink, sum 5.6 m (V1: ~8.7 m)")
add("base-cabinet", "kitchen", (0.4, 0.6, 0.87), (2.45, Y_RUN), rotation=180, color=SAGE,
    label="Sage drawers: cutlery + spices (landing next to the fridge)", note="D3",
    storage=Storage(**BASE, modules=(Module(0.4, (Front("drawers", count=3),), "matte", SAGE),)))
add("dishwasher-cabinet", "kitchen", (0.6, 0.6, 0.87), (2.95, Y_RUN), rotation=180, color=SAGE, tag="DISHWASHER",
    label="Integrated dishwasher behind a sage panel, next to the sink", note="D3",
    storage=Storage(**BASE, modules=(Module(0.6, (Front("panel"),), "matte", SAGE),)))
add("base-cabinet", "kitchen", (0.6, 0.6, 0.87), (3.55, Y_RUN), rotation=180, color=SAGE,
    label="Sink cabinet: bins (3-way sorting) + cleaning", note="D3",
    storage=Storage(**BASE, modules=(Module(0.6, (Front("doors"),), "matte", SAGE),)))
add("pantry", "kitchen", (0.84, 0.6, 2.7), (4.27, Y_RUN), rotation=180, color=SAGE,
    label="Floor-to-ceiling sage pantry (dry food, small appliances)", note="D3: the pantry / tall unit",
    storage=Storage(**BASE, modules=(
        Module(0.42, (Front("door-left", 0.55), Front("door-left")), "matte", SAGE,
               interior=(Fitting("shelf", 0.5), Fitting("shelf", 0.9), Fitting("shelf", 1.3), Fitting("shelf", 1.7))),
        Module(0.42, (Front("door-right", 0.55), Front("door-right")), "matte", SAGE,
               interior=(Fitting("shelf", 0.5), Fitting("shelf", 0.9), Fitting("shelf", 1.3), Fitting("shelf", 1.7))))))
for x1, x2 in ((0.45, 1.65), (2.25, 3.30), (3.80, 3.85)):
    add("countertop", "kitchen", (x2 - x1, 0.62, 0.03), ((x1 + x2) / 2, 6.302), elevation=0.87, color=STONE,
        label="Honed travertine worktop", note="D3")
add("countertop", "kitchen", (0.5, 0.113, 0.03), (3.55, 6.049), elevation=0.87, color=STONE,
    label="Travertine worktop in front of the sink", note="D3")
add("countertop", "kitchen", (0.5, 0.057, 0.03), (3.55, 6.583), elevation=0.87, color=STONE,
    label="Travertine worktop behind the sink", note="D3")
add("backsplash", "kitchen", (1.2, 0.01, 0.6), (1.05, 6.592), rotation=180, elevation=0.9, color="#efe7d7",
    apron="d3_cream_zellige", label="Cream zellige backsplash behind the hob", note="D3")
add("backsplash", "kitchen", (1.6, 0.01, 1.3), (3.05, 6.592), rotation=180, elevation=0.9, color="#efe7d7",
    apron="d3_cream_zellige", label="Cream zellige up to the cabinet behind the open shelves", note="D3")
add("wall-cabinet", "kitchen", (1.2, 0.35, 1.2), (1.05, 6.437), rotation=180, elevation=1.5, color=OAK,
    label="Light-oak wall cabinet over the hob to the ceiling (integrated hood inside, visor below)", note="D3",
    storage=Storage(handles=False, plinth=0.0, interior_color=OAK, modules=(
        Module(0.6, (Front("door-left", 0.55), Front("flap")), "wood", OAK),
        Module(0.6, (Front("door-right", 0.55), Front("flap")), "wood", OAK))))
add("wall-cabinet", "kitchen", (0.6, 0.6, 0.6), (1.95, Y_RUN), rotation=180, elevation=2.1, color=SAGE,
    label="Sage cupboard over the fridge column", note="D3",
    storage=Storage(handles=False, plinth=0.0, modules=(Module(0.6, (Front("flap"),), "matte", SAGE),)))
add("wall-cabinet", "kitchen", (1.6, 0.35, 0.5), (3.05, 6.437), rotation=180, elevation=2.2, color=OAK,
    label="Light-oak top cabinets over the open shelves", note="D3",
    storage=Storage(handles=False, plinth=0.0, interior_color=OAK, modules=(
        Module(0.8, (Front("flap"),), "wood", OAK), Module(0.8, (Front("flap"),), "wood", OAK))))
for el in (1.45, 1.85):
    add("wall-shelf", "kitchen", (1.6, 0.25, 0.035), (3.05, 6.462), elevation=el, color=OAK,
        label="Open light-oak shelf (everyday crockery, plants)", note="D3")
add("trailing-plant", "kitchen", (0.38, 0.22, 0.2), (2.5, 6.47), elevation=1.885, color=LEAF3,
    label="Pothos trailing from the upper open shelf", note="D3")
add("vase", "kitchen", (0.13, 0.13, 0.22), (3.45, 6.47), elevation=1.885, color="#e9e1d2", label="Stoneware jar",
    note="D3")
add("serving-bowl", "kitchen", (0.26, 0.26, 0.12), (3.25, 6.46), elevation=1.485, color="#e9e1d2",
    label="Stoneware bowls on the open shelf", note="D3")
add("vase", "kitchen", (0.12, 0.12, 0.2), (2.65, 6.47), elevation=1.485, color=CLAY, label="Terracotta jug", note="D3")
add("led-strip", "kitchen", (1.15, 0.02, 0.01), (1.05, 6.3), rotation=180, elevation=1.485, color="#c9c9c9",
    label="LED under the wall cabinet over the hob (task)", note="D3", light=lt(14, 1.15))
add("led-strip", "kitchen", (1.55, 0.02, 0.01), (3.05, 6.4), rotation=180, elevation=1.435, color="#c9c9c9",
    label="LED under the open shelf over sink / prep (task)", note="D3", light=lt(18, 1.55))
keep("led-strip-kitchen-1")
keep("venetian-blind-kitchen-1", color="#b8935e", label="Bamboo venetian blind (slats half open)")
add("utility-cupboard", "kitchen", (0.6, 0.6, 2.6), (4.39, 4.215), color=SAGE,
    label="Tall utility cupboard by the door: vacuum, mop, ironing board, folding drying rack",
    note="D3: the owner-reserved 60 cm beside the kitchen door; the fridge moved into the run",
    storage=Storage(handle_color=BRASS, modules=(
        Module(0.6, (Front("door-left", 0.5), Front("door-left")), "matte", SAGE,
               interior=(Fitting("shelf", 2.05),)),)))
# dining: oak banquette along the wall + table + 2 cane chairs (5 daily, 6 with the stool)
add("banquette-bench", "kitchen", (2.0, 0.4, 0.42), (2.05, 4.115), color=OAK,
    label="Built-in light-oak banquette along the wall (3 seats, storage lids)", note="D3: dining nook")
add("seat-cushion", "kitchen", (1.96, 0.38, 0.06), (2.05, 4.115), elevation=0.42, color=SAGE_LT,
    label="Sage linen seat cushion", note="D3")
add("back-cushion", "kitchen", (1.96, 0.08, 0.36), (2.05, 3.955), elevation=0.5, color=SAGE_LT,
    label="Sage linen back cushions", note="D3")
add("dining-table", "kitchen", (1.6, 0.7, 0.75), (2.05, 4.665), color=OAK,
    label="Light-oak dining table 160 x 70 (5 daily, 6 occasionally)",
    note="D3: 1.0 m clear between table and worktop")
add("upholstered-chair", "kitchen", (0.45, 0.5, 0.85), (0.8, 4.665), rotation=270, color=CANE, metal=BRASS,
    label="Cane-and-linen dining chair (window end, pushes under the sill)", note="D3")
add("upholstered-chair", "kitchen", (0.45, 0.5, 0.85), (3.3, 4.665), rotation=90, color=CANE, metal=BRASS,
    label="Cane-and-linen dining chair", note="D3")
for x, y, r in ((1.75, 4.49, 180), (2.35, 4.49, 180), (1.39, 4.665, 90), (2.71, 4.665, 270)):
    add("place-setting", "kitchen", (0.4, 0.28, 0.12), (x, y), rotation=r, elevation=0.75, color="#efe9de",
        label="Stoneware place setting", note="D3")
add("serving-bowl", "kitchen", (0.26, 0.26, 0.13), (2.05, 4.78), elevation=0.75, color="#d9cbb0",
    label="Clay bowl with fruit", note="D3")
for x in (1.65, 2.45):
    add("rattan-pendant-light", "kitchen", (0.38, 0.38, 1.2), (x, 4.665), elevation=1.5, color=CANE,
        label="Rattan pendant over the table (75 cm above the top)", note="D3",
        light=Light(kind="point", watts=22, color=WARM, size=0.06))
add("wall-shelf", "kitchen", (1.4, 0.2, 0.035), (2.05, 4.015), elevation=1.35, color=OAK,
    label="Herb shelf over the banquette", note="D3: kitchen herbs")
add("herb-planter", "kitchen", (1.2, 0.18, 0.14), (2.05, 4.015), elevation=1.385, color=CLAY,
    label="Terracotta herb trough on the shelf", note="D3: kitchen herbs")
add("herb-plant", "kitchen", (1.14, 0.15, 0.2), (2.05, 4.015), elevation=1.525, color="#6f9a52",
    label="Kitchen herbs in the trough: basil, thyme, mint, parsley", note="D3")

# ================================================================== BATH 1
keep("vanity-frame-bathroom-1-1", color="#b08a62", label="Floating light-oak vanity frame")
keep("vessel-sink-bathroom-1-1", color="#ddd2bd", metal=BRASS, label="Travertine-look vessel bowl, aged-brass spout")
keep("backlit-mirror-bathroom-1-1", metal=BRASS)
keep("towels-bathroom-1-1", color="#b9c2a6", label="Sage linen towels")
keep("shower-head-bathroom-1-1", metal=BRASS, color=BRASS)
keep("walk-in-shower-bathroom-1-1", accent="#cdbfa6")
keep("tall-cabinet-bathroom-1-1", color="#b08a62",
     storage=recolor(items["tall-cabinet-bathroom-1-1"].storage, {"#3f2a1c": "#b08a62"}, interior_color="#b08a62"))
for loc in ("slat-screen-bathroom-1-1", "slat-screen-bathroom-1-2"):
    keep(loc, color="#b08a62", label="Light-oak slat screen around the boiler")
keep("wall-niche-bathroom-1-1", color="#93a48a")
for loc in ("toilet-paper-holder-bathroom-1-1", "toilet-roll-stand-bathroom-1-1", "toilet-brush-bathroom-1-1"):
    keep(loc, color=BRASS)
add("fern-plant", "bath_1", (0.18, 0.18, 0.3), (10.05, 6.03), elevation=0.85, color=LEAF2,
    label="Bird's-nest fern on the vanity (loves humidity, low light)", note="D3: bathroom greenery")

# ================================================================== BATH 2
keep("bathtub-master-bathroom-1", apron="d3_clay_plaster", label="Bathtub with a clay-plaster front")
keep("vanity-frame-master-bathroom-1", color="#b08a62", label="Floating light-oak vanity frame")
keep("vessel-sink-master-bathroom-1", color="#ddd2bd", metal=BRASS)
keep("backlit-mirror-master-bathroom-1", metal=BRASS)
keep("towels-master-bathroom-1", color="#b9c2a6", label="Sage linen towels")
keep("bath-screen-master-bathroom-1", metal=BRASS)
keep("shower-head-master-bathroom-1", metal=BRASS, color=BRASS)
keep("tall-cabinet-master-bathroom-1", color="#b08a62",
     storage=recolor(items["tall-cabinet-master-bathroom-1"].storage, {"#3f2a1c": "#b08a62"},
                     interior_color="#b08a62"))
keep("wall-niche-master-bathroom-1", color="#c9b08e")
for loc in ("toilet-paper-holder-master-bathroom-1", "toilet-roll-stand-master-bathroom-1",
            "toilet-brush-master-bathroom-1"):
    keep(loc, color=BRASS)
add("fern-plant", "bath_2", (0.16, 0.16, 0.28), (6.05, 0.45), elevation=0.85, color=LEAF2,
    label="Maidenhair fern on the vanity", note="D3: bathroom greenery")

# ================================================================== KIDS (bedroom 1)
drop("desk-bedroom-1-1", "chair-bedroom-1-1", "notebooks-bedroom-1-1", "pencils-bedroom-1-1",
     "pencil-case-bedroom-1-1", "storage-cabinet-bedroom-1-1", "slat-panel-bedroom-1-1", "rug-bedroom-1-1")
keep("wardrobe-bedroom-1-1", color="#efe7d8", label="Kids' wardrobe: pale-sage doors, oak handles, lit niche",
     storage=recolor(items["wardrobe-bedroom-1-1"].storage, {"#7f9fb0": SAGE_LT, "#efe6d6": "#efe7d8"},
                     handle_color=OAK))
keep("floating-bed-bedroom-1-1", size=(0.9, 2.0, 0.9), position=(9.775, 9.65), rotation=0, color=OAK,
     accent="#c9d0b8", label="Low floating oak child bed along the wall (one open side, safe)",
     note="D3: lengthwise on the mural wall - frees the middle of the room for play")
keep("led-strip-bedroom-1-4", position=(9.775, 9.66), rotation=0, label="Night glow under the bed (nightlight)")
keep("nightstand-bedroom-1-1", size=(0.4, 0.35, 0.5), position=(9.08, 8.85), rotation=0, color=OAK)
keep("table-lamp-bedroom-1-1", position=(9.08, 8.86), color="#efe7d8", label="Linen table lamp (dimmable)")
keep("wallpaper-bedroom-1-1", apron="d3_leaf_watercolor", color="#eef0e4",
     label="Watercolour forest-canopy mural behind the bed")
for loc in ("drape-bedroom-1-1", "drape-bedroom-1-2"):
    keep(loc, color="#a3ad8f", label="Sage blackout drape")
keep("sheer-curtain-bedroom-1-1", color="#f7f3ea")
keep("track-light-bedroom-1-1", track=replace(items["track-light-bedroom-1-1"].track, heads=(
    TrackHead(0.2, (8.9, 7.85, 1.2)), TrackHead(0.9, (9.8, 7.85, 1.2)), TrackHead(0.6, (9.6, 9.4, 0.6)),
    TrackHead(-0.9, (7.6, 6.4, 0.0)))))
add("changing-dresser", "bedroom_1", (1.0, 0.55, 0.9), (7.2, 8.0), rotation=270, color="#e6decf",
    label="Changing dresser (3 drawers, oak top) - later a desk surface", note="D3: changing / desk surface",
    storage=Storage(handle_color=OAK, modules=(Module(1.0, (Front("drawers", count=3),), "matte", "#e6decf"),)))
add("changing-mat", "bedroom_1", (0.8, 0.5, 0.1), (7.2, 8.0), rotation=270, elevation=0.9, color=SAGE_LT,
    label="Changing mat", note="D3")
add("low-bookcase", "bedroom_1", (1.2, 0.35, 0.6), (7.1, 9.2), rotation=270, color=OAK,
    label="Low open oak toy + book shelf at child height", note="D3: toy storage",
    storage=Storage(modules=(Module(0.4, (Front("open"),), "wood", OAK, interior=(Fitting("shelf", 0.32),)),
                             Module(0.4, (Front("open"),), "wood", OAK, interior=(Fitting("shelf", 0.32),)),
                             Module(0.4, (Front("open"),), "wood", OAK, interior=(Fitting("shelf", 0.32),)))))
for y in (8.8, 9.6):
    add("toy-basket", "bedroom_1", (0.3, 0.28, 0.2), (7.11, y), rotation=270, elevation=0.1, color=CANE,
        label="Woven seagrass toy basket", note="D3")
add("tub-armchair", "bedroom_1", (0.66, 0.66, 0.72), (7.29, 10.2), rotation=270, color=SAGE, accent=OAK,
    label="Small sage nursing / reading chair beside the drapes (below the sill)", note="D3")
add("wall-sconce", "bedroom_1", (0.14, 0.1, 0.16), (6.975, 10.2), rotation=270, elevation=1.55, color="#e6decf",
    label="Linen wall sconce over the reading chair (task)", note="D3", light=lt(12, 0.06, "point"))
add("wall-shelf", "bedroom_1", (1.0, 0.2, 0.03), (7.025, 9.2), rotation=270, elevation=1.8, color=OAK,
    label="High oak plant shelf (wall-fixed, out of the child's reach)", note="D3")
add("parlor-palm-plant", "bedroom_1", (0.3, 0.2, 0.36), (7.05, 8.95), rotation=90, elevation=1.83, color=LEAF2,
    label="Parlour palm - non-toxic, out of reach at 1.8 m", note="D3: kid-safe plant (ASPCA non-toxic list)")
add("boston-fern-plant", "bedroom_1", (0.34, 0.2, 0.24), (7.05, 9.45), rotation=90, elevation=1.83, color=LEAF3,
    label="Boston fern - non-toxic, out of reach at 1.8 m", note="D3: kid-safe plant (ASPCA non-toxic list)")
add("organic-rug", "bedroom_1", (2.2, 1.7, 0.01), (8.35, 9.55), rotation=90, color="#b9c2a6",
    label="Soft sage play rug", note="D3")
keep("led-strip-bedroom-1-1", label="Warm cove along the shelf wall (ambient / grazing)")

# ================================================================== MASTER SUITE (bedroom 2)
drop("tv-console-master-suite-1", "wall-tv-master-suite-1", "slat-panel-master-suite-1")
keep("floating-bed-master-suite-1", position=(1.85, 1.3), color="#b08a62", accent="#b9c0a3",
     label="Floating light-oak bed 160 x 200, sage-linen bedding",
     note="D3: 0.60 m free on the window side, 0.86 m to the wardrobe")
keep("led-strip-master-suite-7", position=(1.85, 1.3))
keep("nightstand-master-suite-1", position=(0.775, 0.45), color=CANE, label="Cane nightstand")
keep("nightstand-master-suite-2", position=(2.925, 0.45), color=CANE, label="Cane nightstand")
keep("table-lamp-master-suite-1", position=(0.775, 0.45), color="#e8dcc6", label="Linen reading lamp")
keep("table-lamp-master-suite-2", position=(2.925, 0.45), color="#e8dcc6", label="Linen reading lamp")
keep("rug-master-suite-1", position=(1.85, 1.7), color="#c9c0a6", label="Wool-jute rug, oat")
keep("wallpaper-master-suite-1", apron="d3_dune_sage", color="#e2e4d6",
     label="Sage dune-ripple wall behind the bed")
for loc in ("drape-master-suite-1", "drape-master-suite-2"):
    keep(loc, color=MOSS, label="Moss-green blackout drape")
keep("sheer-curtain-master-suite-1", color="#f7f3ea")
for loc in ("wardrobe-master-suite-1", "wardrobe-master-suite-2"):
    keep(loc, color="#e3dacb", label="Linen-white doors + light-oak column (lit niche, drawers)",
         storage=recolor(items[loc].storage, {"#a08b78": "#e3dacb", "#8a5f3e": OAK}, handle_color=BRASS,
                         interior_color="#d9c4a4"))
add("dresser", "bedroom_2", (1.6, 0.5, 0.8), (2.6, 3.54), rotation=180, color=OAK,
    label="Light-oak chest of drawers on the old TV wall (screen-free bedroom)",
    note="D3: wellbeing - no TV in the bedroom; more folded storage",
    storage=Storage(handle_color=BRASS, modules=(Module(0.8, (Front("drawers", count=3),), "wood", OAK),
                                                 Module(0.8, (Front("drawers", count=3),), "wood", OAK))))
add("backlit-mirror", "bedroom_2", (0.7, 0.02, 1.05), (2.6, 3.78), rotation=180, elevation=1.0, color="#d9dde0",
    metal=BRASS, label="Pill mirror with brass frame over the dresser", note="D3: master mirror")
add("trailing-plant", "bedroom_2", (0.36, 0.26, 0.22), (3.2, 3.55), elevation=0.8, color=LEAF3,
    label="Trailing pothos on the dresser", note="D3")
add("vase", "bedroom_2", (0.13, 0.13, 0.26), (2.0, 3.6), elevation=0.8, color=CLAY, label="Terracotta vase",
    note="D3")
add("tub-armchair", "bedroom_2", (0.75, 0.75, 0.72), (1.02, 3.33), rotation=270, color=OAT, accent=OAK,
    label="Oatmeal reading chair in the window corner", note="D3: chair + reading corner")
add("floor-lamp", "bedroom_2", (0.32, 0.32, 1.5), (1.6, 3.6), color="#e8dcc6",
    label="Linen floor lamp for the reading chair", note="D3", light=lt(18, 0.1, "point"))
add("bird-of-paradise", "bedroom_2", (0.48, 0.48, 1.7), (3.75, 3.45), color="#3d5e30",
    label="Bird of paradise at the dressing entrance (bright SSW light from W4)", note="D3")

# ================================================================== BALCONY - garden room
keep("outdoor-dining-table-balcony-1", size=(1.0, 0.6, 0.74), position=(-1.25, 8.2), color="#a8784a",
     label="Teak bistro table against the railing", note="D3: 0.95 m free in front of the balcony door")
keep("outdoor-chair-balcony-1", position=(-1.25, 9.15), color="#a8784a")
keep("outdoor-chair-balcony-2", position=(-1.25, 7.25), color="#a8784a")
keep("lemon-tree-balcony-1", color="#3f6b2c")
keep("mug-balcony-1", position=(-1.22, 8.52))
keep("mug-balcony-2", position=(-1.28, 7.88))
add("outdoor-rug", "balcony", (2.2, 1.1, 0.008), (-1.0, 8.2), rotation=90, color="#cdbb94",
    label="Natural outdoor rug (recycled fibre, jute look)", note="D3")
add("lemon-tree", "balcony", (0.5, 0.5, 1.3), (-0.4, 7.0), color="#4a7a34",
    label="Second citrus (Meyer lemon) beside the balcony door - full SSW sun",
    note="D3: a small citrus grove at both ends")
add("planter-box", "balcony", (0.55, 0.27, 0.4), (-1.47, 9.92), rotation=270, color=CLAY,
    label="Terracotta planter on the railing side", note="D3")
add("planter-box", "balcony", (0.7, 0.27, 0.4), (-0.55, 10.765), rotation=180, color=CLAY,
    label="Terracotta planter along the end wall", note="D3")
add("lavender-plant", "balcony", (0.5, 0.22, 0.3), (-1.47, 9.92), rotation=270, elevation=0.4, color="#8a87a3",
    label="Lavender in the planter (scent, pollinators)", note="D3")
add("herb-plant", "balcony", (0.65, 0.22, 0.28), (-0.55, 10.765), rotation=180, elevation=0.4, color="#6f9a52",
    label="Rosemary, oregano and sage in the planter", note="D3")
add("table-lamp", "balcony", (0.18, 0.18, 0.32), (-1.25, 8.2), elevation=0.74, color="#e8dcc6",
    label="Rechargeable lantern on the table (outdoor accent light)", note="D3", light=lt(10, 0.08, "point"))
add("drying-rack", "balcony", (1.0, 0.06, 0.7), (-0.03, 10.1), rotation=90, elevation=1.1, color="#e9e6df",
    label="Wall-mounted fold-down drying rack (shown folded)", note="D3: drying space")
keep("ceiling-light-balcony-1", color="#e8dcc6")

# ------------------------------------------------------------------ write
d3.items = [items[loc] for loc in order]
for it in d3.items:  # every piece of this design is a draft for the owner
    assert it.id.startswith(f"{K}."), it.id
OUT.write_text(variant_to_toml(d3), encoding="utf-8")
print(f"wrote {OUT} - {len(d3.items)} pieces")
