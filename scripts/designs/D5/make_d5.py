"""Generate .tmp/designs/D5/variants/D5.toml - "Jewel Box Deco" (Neo Art Deco), from a copy of V1.

Run from the repo root:  uv run python .tmp/designs/D5/make_d5.py
"""

from dataclasses import replace
from pathlib import Path

from apartment_core.furniture import (
    Fitting,
    Front,
    Item,
    Light,
    Module,
    RoomFinish,
    Storage,
    copy_variant,
    load_variant,
    variant_to_toml,
)
from apartment_core.model import parse_finish

OUT = Path(".tmp/designs/D5/variants/D5.toml")

# ---------------------------------------------------------------- palette
IVORY = "#ece4d4"       # walls, uppers
IVORY_2 = "#f3eee4"     # stretch ceilings, sheers
BLACK = "#151413"       # black lacquer
EMERALD = "#0f4a3b"     # living / kitchen jewel
SAPPHIRE = "#1c355e"    # suite jewel
OXBLOOD = "#5c1a1e"     # accent
BRASS = "#b8903f"       # polished brass (metal 1; metal 2 = matte black)
BRASS_M = "#86672e"     # brass on solid (non-metal-shaded) pieces: reads less yellow
MACASSAR = "#3e2a1e"    # wood 1: dark smoked oak / macassar
WALNUT = "#6b4630"      # wood 2: fluted walnut
ASH = "#d6bf9c"         # wood 3: pale ash (kids' room)
CHAMPAGNE = "#cdb894"   # velvet bed / lamp shades
CELADON = "#a3b5a6"     # kids: softened emerald
BLUSH = "#d4a99a"       # kids: softened oxblood
WARM = "#ffd29e"        # ~2700 K light

v1 = load_variant("data/variants/V1.toml")
v = copy_variant(v1, "D5", "Jewel Box Deco")
v.description = ("Neo Art Deco made livable: an ivory envelope with one jewel tone per room (emerald living + kitchen, "
                 "sapphire suite, oxblood accents), black lacquer and polished brass, fluted walnut, bold-veined "
                 "marble, brass-strip terrazzo and statement halo lights.")
v.based_on = "V1"
v.wall_color = IVORY
v.true_colors = True

# ---------------------------------------------------------------- own finishes (d5_)
FIN = {
    "d5_smoked_oak": dict(kind="parquet", size=[0.60, 0.10], color="#4a3324", color2="#3a281b", joint_color="#1a110b",
                          joint=0.0015, direction="x", roughness=0.35,
                          note="smoked oak short planks 60 x 10 - dark Deco floor (living, suite)"),
    "d5_brass_terrazzo": dict(kind="tiles", size=[0.60, 0.60], color="#ece5d6", color2="#2b2826",
                              joint_color=BRASS, joint=0.005, roughness=0.25,
                              note="ivory terrazzo with black chips, 60 x 60 fields split by brass divider strips "
                                   "(Miami-Deco floor) - hall + kitchen"),
    "d5_arabescato": dict(kind="marble", size=[1.20, 0.60], color="#f1ede5", color2="#2b2a28", joint_color="#d8d2c6",
                          joint=0.0015, roughness=0.15,
                          note="white marble with bold graphite veins (Arabescato look) - kitchen splash, bath 2 walls"),
    "d5_nero_gold": dict(kind="marble", size=[0.60, 0.60], color="#171615", color2="#c9a25c", joint_color="#232120",
                         joint=0.0015, roughness=0.18,
                         note="black marble with gold veins (Nero Portoro look) - bath floors, tub front"),
    "d5_verde_ivory": dict(kind="marble", size=[0.60, 1.20], color="#eeeae0", color2="#0f5c3e", joint_color="#d9d3c6",
                           joint=0.0015, roughness=0.18,
                           note="ivory marble with emerald veins (Calacatta Verde look), 60 x 120 vertical - bath 1 walls"),
    "d5_emerald_chevron": dict(kind="chevron", size=[3.78, 2.65], color="#114a3b", color2="#0c3a2e",
                               joint_color=BRASS, joint=0.0, roughness=0.45,
                               note="emerald lacquer-look wall panel with brass chevron inlay lines - living sofa wall"),
    "d5_sapphire_chevron": dict(kind="chevron", size=[3.04, 2.70], color="#1d365e", color2="#172c4d",
                                joint_color=BRASS, joint=0.0, roughness=0.45,
                                note="sapphire panel with brass chevron inlay lines - master bed wall"),
    "d5_celadon_chevron": dict(kind="chevron", size=[3.10, 2.70], color="#b3cbbe", color2="#a5bfb1",
                               joint_color="#f3ece2", joint=0.0, roughness=0.8,
                               note="soft celadon chevron with ivory lines - Deco softened for the kids' bed wall"),
    "d5_pale_ash": dict(kind="parquet", size=[1.20, 0.16], color="#d6bf9c", color2="#c8ae88", joint_color="#8a6f50",
                        joint=0.0015, direction="x", roughness=0.45, note="pale ash planks - kids' room"),
    "d5_balcony_terrazzo": dict(kind="tiles", size=[0.60, 0.60], color="#e3dccd", color2="#3a3634",
                                joint_color="#9c9488", joint=0.003, roughness=0.6,
                                note="outdoor ivory terrazzo-look porcelain 60 x 60 - balcony"),
}
v.finishes = {n: parse_finish(n, f) for n, f in FIN.items()}

STRETCH = dict(stretch_ceiling=True, stretch_color=IVORY_2, stretch_led_color="#ffc98f", stretch_led_w_per_m=7.0)
v.rooms = {
    "living": RoomFinish(floor="d5_smoked_oak", skirting=BLACK, skirting_height=0.12, **STRETCH),
    "kitchen": RoomFinish(floor="d5_brass_terrazzo", paint=IVORY),
    "hall": RoomFinish(floor="d5_brass_terrazzo", skirting=BLACK, skirting_height=0.12, **STRETCH),
    "bath_1": RoomFinish(floor="d5_nero_gold", walls="d5_verde_ivory", **STRETCH),
    "bath_2": RoomFinish(floor="d5_nero_gold", walls="d5_arabescato", **STRETCH),
    "bedroom_1": RoomFinish(floor="d5_pale_ash", paint="#f1e6dc", skirting="#efe6d6", skirting_height=0.10),
    "bedroom_2": RoomFinish(floor="d5_smoked_oak", skirting=BLACK, skirting_height=0.12),
    "balcony": RoomFinish(floor="d5_balcony_terrazzo"),
}

items = {it.local_id: it for it in v.items}
order = [it.local_id for it in v.items]


def get(lid):
    return items[lid]


def upd(lid, **kw):
    items[lid] = replace(items[lid], **kw)


def rm(*lids):
    for lid in lids:
        del items[lid]
        order.remove(lid)


def add(lid, type_, room, size, pos, **kw):
    assert lid not in items, lid
    kw.setdefault("status", "draft")
    items[lid] = Item(id=f"D5.{lid}", type=type_, room=room, size=tuple(size), position=tuple(pos), **kw)
    order.append(lid)


def rename(old, new, **kw):
    it = items.pop(old)
    i = order.index(old)
    order[i] = new
    items[new] = replace(it, id=f"D5.{new}", **kw)


def restyle_storage(lid, color, finish, front_colors=None, handle=BRASS, interior=None, **st):
    """Recolour every module: front_colors[i] (or color) + finish; keep the module layout."""
    it = items[lid]
    s = it.storage
    mods = []
    for i, m in enumerate(s.modules):
        fc = (front_colors[i] if front_colors else color)
        fin = finish if not isinstance(finish, (list, tuple)) else finish[i]
        mods.append(replace(m, front_color=fc, finish=fin))
    items[lid] = replace(it, color=color, storage=replace(s, modules=tuple(mods), handle_color=handle,
                                                          interior_color=interior or s.interior_color, **st))


def light(watts, kind="point", size=0.1, color=WARM, **kw):
    return Light(kind=kind, watts=watts, color=color, size=size, **kw)


# ================================================================ LIVING
rename("plush-corner-sofa-living-1", "tufted-corner-sofa-living-1", type="tufted-corner-sofa", color="#e9e0cd",
       accent=BRASS, cushion=OXBLOOD, mirror=True,
       label="Channel-tufted corner sofa, ivory velvet on a brass plinth, oxblood cushions",
       note="D5: ivory velvet against the emerald chevron wall; chaise on the balcony side")
rm("organic-shag-rug-living-1", "round-side-table-living-1", "plush-armchair-living-1", "plush-armchair-living-2",
   "infinity-pendant-light-living-1")
add("rug-living-1", "rug", "living", (3.6, 2.6, 0.012), (2.850, 9.100), color="#0f1d36",
    label="Sapphire wool rug", note="D5: deep sapphire under the ivory sofa - colour block, acoustic softness")
upd("round-coffee-table-living-1", size=(1.0, 1.0, 0.40), position=(2.875, 9.000), color=BLACK,
    label="Round black lacquer coffee table")
add("tub-armchair-living-1", "tub-armchair", "living", (0.78, 0.78, 0.74), (4.350, 9.650), rotation=90,
    color=OXBLOOD, accent=BRASS, label="Oxblood velvet tub chair", note="D5: Deco tub chair facing the sofa")
add("tub-armchair-living-2", "tub-armchair", "living", (0.78, 0.78, 0.74), (4.350, 8.450), rotation=90,
    color=OXBLOOD, accent=BRASS, label="Oxblood velvet tub chair")
add("round-side-table-living-1", "round-side-table", "living", (0.40, 0.40, 0.50), (4.350, 9.050), color=BRASS_M,
    label="Brass drum side table between the tub chairs")
# statement light: two concentric brass halos = a tiered Deco chandelier over the coffee table
add("ring-pendant-light-living-1", "ring-pendant-light", "living", (1.10, 1.10, 0.62), (2.875, 9.000),
    elevation=2.08, color=BRASS, light=light(70, "area", 1.1),
    label="Brass halo chandelier, outer ring", note="D5 statement light (tier 1), top on the stretch ceiling")
add("ring-pendant-light-living-2", "ring-pendant-light", "living", (0.66, 0.66, 0.84), (2.875, 9.000),
    elevation=1.86, color=BRASS, light=light(45, "area", 0.66, shadow=False),
    label="Brass halo chandelier, inner ring (lower tier)")
# TV wall: fluted walnut, wider; floating black lacquer media console; 85" TV
upd("slat-panel-living-1", size=(3.0, 0.03, 2.65), position=(2.875, 6.752), color=WALNUT,
    label="Fluted walnut TV wall")
upd("wall-tv-living-1", size=(1.89, 0.035, 1.09), position=(2.875, 6.790), elevation=0.62,
    label='85" wall TV (seat ~3.3 m away)')
add("tv-console-living-1", "tv-console", "living", (2.2, 0.38, 0.42), (2.875, 6.957), rotation=0, elevation=0.12,
    color=BLACK, label="Floating black lacquer media console, brass pulls, walnut centre flap",
    storage=Storage(modules=(Module(0.7, (Front("drawers", None, 2),), "gloss", BLACK),
                             Module(0.8, (Front("flap"),), "wood", WALNUT),
                             Module(0.7, (Front("drawers", None, 2),), "gloss", BLACK)),
                    plinth=0.0, handle_color=BRASS, interior_color=MACASSAR))
for k, x in ((1, 1.600), (2, 4.150)):
    add(f"wall-sconce-living-{k}", "wall-sconce", "living", (0.10, 0.10, 0.24), (x, 6.830), elevation=1.50,
        color=BRASS_M, light=light(14, size=0.06), label="Brass cylinder sconce on the fluted wall")
upd("floor-lamp-living-1", color=CHAMPAGNE, label="Brass floor lamp, champagne shade (reading)")
upd("bird-of-paradise-living-1", size=(0.62, 0.62, 1.75), position=(1.000, 7.060))
restyle_storage("wardrobe-living-1", BLACK, ["gloss", "wood", "gloss"], [BLACK, WALNUT, BLACK],
                interior=MACASSAR)
upd("panel-desk-living-1", color=MACASSAR, label="Macassar-wood desk 160 x 80 on dark slab legs")
upd("gaming-chair-living-1", color=OXBLOOD, label="Ergonomic task chair, oxblood leather")
add("table-lamp-living-1", "table-lamp", "living", (0.22, 0.22, 0.45), (6.350, 10.700), elevation=0.80,
    color=CHAMPAGNE, light=light(12, size=0.06), label="Brass desk lamp (task light)")
for lid in ("drape-living-1", "drape-living-2", "drape-living-3", "drape-living-4"):
    upd(lid, color=EMERALD)
upd("wallpaper-living-1", apron="d5_emerald_chevron", color="#114a3b",
    label="Emerald panel wall with brass chevron inlay")

# ================================================================ KITCHEN
# Run re-planned so the work triangle closes (V1 ~9 m -> ~6.9 m): spice pull-out | hob over oven (shifted 14 cm,
# still on the hood point) | 1.30 drawers + doors | dishwasher | sink (on its point) | 35 cm landing drawers | fridge.
# The tall pantry takes the old fridge spot by the door.
Y_RUN, BASE_H = 6.312, 0.87
st_k = dict(plinth=0.09, handle_color=BRASS, door_handles=True, interior_color="#e9e2d4")
add("base-cabinet-kitchen-5", "base-cabinet", "kitchen", (0.14, 0.6, BASE_H), (0.520, Y_RUN), rotation=180,
    color=EMERALD, label="15 cm spice / oil pull-out beside the hob",
    storage=Storage(modules=(Module(0.14, (Front("drawer"),), "gloss", EMERALD),), **st_k))
upd("plinth-kitchen-1", position=(0.890, 6.287), color=EMERALD)
upd("oven-kitchen-1", position=(0.890, Y_RUN), color=BLACK)
upd("cooktop-kitchen-1", position=(0.890, 6.320))
upd("hood-visor-kitchen-1", position=(0.890, 6.440), color=BLACK)
upd("base-cabinet-kitchen-1", size=(1.30, 0.6, BASE_H), position=(1.840, Y_RUN), color=EMERALD,
    storage=Storage(modules=(Module(0.6, (Front("drawers", None, 3),), "gloss", EMERALD),
                             Module(0.7, (Front("doors"),), "gloss", EMERALD)), **st_k))
upd("base-cabinet-kitchen-3", size=(0.60, 0.6, BASE_H), position=(2.790, Y_RUN), color=EMERALD, tag="DISHWASHER",
    label="Integrated dishwasher (emerald panel) next to the sink",
    storage=Storage(modules=(Module(0.6, (Front("panel"),), "gloss", EMERALD),), **st_k))
upd("base-cabinet-kitchen-2", position=(3.390, Y_RUN), color=EMERALD,
    label="Sink cabinet: bins + cleaning under the sink",
    storage=Storage(modules=(Module(0.6, (Front("doors"),), "gloss", EMERALD),), **st_k))
upd("black-sink-kitchen-1", position=(3.390, 6.330))
add("base-cabinet-kitchen-4", "base-cabinet", "kitchen", (0.35, 0.6, BASE_H), (3.865, Y_RUN), rotation=180,
    color=EMERALD, label="Landing drawers beside the fridge",
    storage=Storage(modules=(Module(0.35, (Front("drawers", None, 3),), "gloss", EMERALD),), **st_k))
upd("glass-fridge-kitchen-1", position=(4.340, 6.322), rotation=180,
    note="D5: in the run beside the sink + landing worktop (closes the work triangle)")
upd("countertop-kitchen-1", size=(2.69, 0.62, 0.03), position=(1.795, 6.302), color="#1f1e1d")
upd("countertop-kitchen-2", size=(0.40, 0.62, 0.03), position=(3.840, 6.302), color="#1f1e1d")
upd("countertop-kitchen-3", position=(3.390, 6.049), color="#1f1e1d")
upd("countertop-kitchen-4", position=(3.390, 6.583), color="#1f1e1d")
upd("backsplash-kitchen-1", size=(3.59, 0.01, 0.6), position=(2.245, 6.592), apron="d5_arabescato",
    color="#f1ede5", label="Bold-veined white marble splash (Arabescato look)")
upd("wall-cabinet-kitchen-1", position=(2.250, 6.412))
restyle_storage("wall-cabinet-kitchen-1", WALNUT, "wood", interior=WALNUT)
w2 = get("wall-cabinet-kitchen-2")
upd("wall-cabinet-kitchen-2", size=(4.23, 0.6, 0.6), position=(2.575, 6.312),
    storage=replace(w2.storage, modules=tuple(Module(0.705, (Front("flap"),), "gloss", IVORY) for _ in range(6))))
restyle_storage("wall-cabinet-kitchen-2", IVORY, "gloss")
rename("tall-cabinet-kitchen-1", "pantry-kitchen-1", type="pantry", size=(0.60, 0.58, 2.40), position=(4.390, 4.205),
       rotation=0, color=EMERALD, tag="", label="Tall pantry by the door (shelves, emerald gloss)",
       note="D5: was the V1 tall unit; dishwasher moved next to the sink",
       storage=Storage(modules=(Module(0.6, (Front("door-left", 0.5), Front("door-left")), "gloss", EMERALD,
                                       tuple(Fitting("shelf", z) for z in (0.45, 0.80, 1.15, 1.50))),),
                       plinth=0.09, handle_color=BRASS, handle_length=0.6, interior_color="#e9e2d4"))
upd("venetian-blind-kitchen-1", color="#e9e2d4")
# dining: Deco booth - oxblood banquette along the end wall, 1.9 m table, 2 end chairs (5 daily, 6 at a squeeze)
rm("upholstered-chair-kitchen-1", "upholstered-chair-kitchen-2", "linear-pendant-light-kitchen-1",
   "place-setting-kitchen-1", "place-setting-kitchen-2", "place-setting-kitchen-3", "place-setting-kitchen-4",
   "serving-bowl-kitchen-1")
add("banquette-sofa-kitchen-1", "banquette-sofa", "kitchen", (2.0, 0.50, 0.95), (1.950, 4.165), color=OXBLOOD,
    label="Built-in oxblood velvet banquette (3 seats, 4 at a squeeze)",
    note="D5: Deco booth seating against the end wall frees the counter side (0.90 m path)")
upd("dining-table-kitchen-1", size=(1.9, 0.70, 0.75), position=(1.950, 4.765), color=BLACK,
    label="Black lacquer dining table 190 x 70")
upd("upholstered-chair-kitchen-5", position=(0.730, 4.765), color="#e6dccb", label="Ivory velvet chair, brass legs")
upd("upholstered-chair-kitchen-6", position=(3.170, 4.765), color="#e6dccb", label="Ivory velvet chair, brass legs")
for k, x in ((1, 1.450), (2, 2.450)):
    add(f"pendant-light-kitchen-{k}", "pendant-light", "kitchen", (0.32, 0.32, 1.18), (x, 4.765), elevation=1.52,
        color=BRASS_M, light=light(28, size=0.08, shadow=(k == 1)), label="Brass dome pendant over the table")
for k, (x, y, r) in enumerate(((1.450, 4.590, 180), (2.450, 4.590, 180), (1.110, 4.765, 90), (2.790, 4.765, 270)), 1):
    add(f"place-setting-kitchen-{k}", "place-setting", "kitchen", (0.4, 0.28, 0.12), (x, y), rotation=r,
        elevation=0.75, color="#f4f3f0")
add("serving-bowl-kitchen-1", "serving-bowl", "kitchen", (0.26, 0.26, 0.13), (1.950, 4.840), elevation=0.75,
    color=BRASS_M)

# ================================================================ HALL
rm("track-light-hall-1", "track-light-hall-2", "shoes-hall-1", "shoes-hall-2", "wall-shelf-hall-1", "wall-shelf-hall-2",
   "plant-hall-1", "vase-hall-1", "vase-hall-2")
restyle_storage("wardrobe-hall-1", BLACK, "gloss")
upd("wardrobe-hall-1", label="Utility cupboard: vacuum, mop, ironing board (black lacquer)")
add("wardrobe-hall-2", "wardrobe", "hall", (1.10, 0.60, 2.55), (5.125, 5.950), rotation=270, elevation=0.10,
    color=BLACK, label="Coat + shoe wardrobe: bronze-mirror door, lacquer door, open bench niche, shoe drawer",
    note="D5: coats (rail) + shoes (drawer) + a sit-down niche; the mirror door is the full-length hall mirror",
    storage=Storage(modules=(Module(0.55, (Front("door-left"),), "mirror", "#d6d0c2",
                                    (Fitting("shelf", 2.10), Fitting("rail", 1.95)), "coats"),
                             Module(0.55, (Front("door-right", 1.45), Front("open", 0.55), Front("drawer", None)),
                                    "gloss", BLACK, (Fitting("shelf", 1.40),), "bench + shoes")),
                    plinth=0.0, handle_color=BRASS, handle_length=0.6, interior_color=OXBLOOD))
add("console-table-hall-1", "console-table", "hall", (0.60, 0.30, 0.82), (6.650, 6.200), rotation=90, color=BLACK,
    label="Black lacquer console (keys + bags)")
add("backlit-mirror-hall-1", "backlit-mirror", "hall", (0.50, 0.02, 1.00), (6.790, 6.200), rotation=90,
    elevation=1.10, color="#d9dde0", label="Arched (pill) brass mirror with halo over the console")
add("vase-hall-1", "vase", "hall", (0.14, 0.14, 0.30), (6.680, 6.370), elevation=0.82, color=EMERALD)
add("plant-hall-1", "plant", "hall", (0.16, 0.16, 0.30), (6.660, 6.030), elevation=0.82, color="#3f6b35")
add("stool-hall-1", "stool", "hall", (0.40, 0.40, 0.45), (7.020, 4.740), color=OXBLOOD,
    label="Oxblood velvet stool by the door (shoes on / off)")
upd("doormat-hall-1", color="#1b1a19")
for k, (x, y) in enumerate(((5.812, 5.300), (7.560, 5.190)), 1):
    add(f"ceiling-light-hall-{k}", "ceiling-light", "hall", (0.45, 0.45, 0.14), (x, y), elevation=2.56,
        color=BRASS_M, light=light(40, "area", 0.4), label="Brass Deco flush dome")
upd("slat-panel-hall-1", color=WALNUT)

# ================================================================ BATH 1
upd("walk-in-shower-bathroom-1-1", accent="#171615")
upd("vanity-frame-bathroom-1-1", color=BLACK, label="Black lacquer floating vanity")
upd("vessel-sink-bathroom-1-1", color="#efe9de")
upd("towels-bathroom-1-1", color=EMERALD)
upd("tall-cabinet-bathroom-1-1", color=BLACK)
restyle_storage("tall-cabinet-bathroom-1-1", BLACK, "gloss", interior=MACASSAR, handle=BRASS)
upd("slat-screen-bathroom-1-1", color=WALNUT)
upd("slat-screen-bathroom-1-2", color=WALNUT)
upd("wall-niche-bathroom-1-1", color="#eeeae0")
for lid in ("toilet-paper-holder-bathroom-1-1", "toilet-roll-stand-bathroom-1-1", "toilet-brush-bathroom-1-1",
            "shower-head-bathroom-1-1"):
    upd(lid, color=BRASS)

# ================================================================ BATH 2
upd("bathtub-master-bathroom-1", apron="d5_nero_gold")
upd("vanity-frame-master-bathroom-1", color=BLACK, label="Black lacquer floating vanity")
upd("vessel-sink-master-bathroom-1", color="#efe9de")
upd("towels-master-bathroom-1", color="#e9e1d2")
restyle_storage("tall-cabinet-master-bathroom-1", BLACK, "gloss", interior=MACASSAR, handle=BRASS)
upd("wall-niche-master-bathroom-1", color="#f1ede5")
for lid in ("toilet-paper-holder-master-bathroom-1", "toilet-roll-stand-master-bathroom-1",
            "toilet-brush-master-bathroom-1", "shower-head-master-bathroom-1"):
    upd(lid, color=BRASS)

# ================================================================ BEDROOM 1 (kids - Deco softened)
upd("floating-bed-bedroom-1-1", color="#efe6d6", accent="#ead3c9", tag_color=SAPPHIRE)
upd("wallpaper-bedroom-1-1", apron="d5_celadon_chevron", color="#b3cbbe",
    label="Soft celadon chevron wall behind the bed")
upd("slat-panel-bedroom-1-1", color=ASH, label="Fluted pale-ash wall (desk side)")
restyle_storage("wardrobe-bedroom-1-1", CELADON, "matte", [CELADON, "#efe6d6", CELADON], handle=BRASS,
                interior="#efe6d6")
restyle_storage("storage-cabinet-bedroom-1-1", "#efe6d6", "matte", handle=BRASS)
upd("storage-cabinet-bedroom-1-1", label="Low cabinet: changing top now, toys later (wall-fixed)")
upd("nightstand-bedroom-1-1", color="#efe6d6")
upd("rug-bedroom-1-1", color=BLUSH, label="Soft blush rug")
upd("desk-bedroom-1-1", color=ASH)
upd("chair-bedroom-1-1", color=CELADON)
upd("table-lamp-bedroom-1-1", color=BLUSH, label="Nightlight lamp, blush shade")
for lid in ("drape-bedroom-1-1", "drape-bedroom-1-2"):
    upd(lid, color="#879e8f", label="Celadon blackout drape")
upd("notebooks-bedroom-1-1", position=(7.250, 9.870))
add("bookcase-bedroom-1-1", "bookcase", "bedroom_1", (0.90, 0.30, 0.60), (7.105, 8.150), rotation=270, color=ASH,
    label="Low open toy + book cubbies at child height (wall-fixed)",
    storage=Storage(modules=(Module(0.45, (Front("open"),), "wood", ASH, (Fitting("shelf", 0.30),)),
                             Module(0.45, (Front("open"),), "wood", ASH, (Fitting("shelf", 0.30),))),
                    plinth=0.04, handle_color=BRASS))
add("table-lamp-bedroom-1-2", "table-lamp", "bedroom_1", (0.18, 0.18, 0.38), (7.080, 9.660), elevation=0.72,
    color=CELADON, light=light(10, size=0.05), label="Desk lamp, celadon shade")
rm("track-light-bedroom-1-1")
add("ceiling-light-bedroom-1-1", "ceiling-light", "bedroom_1", (0.50, 0.50, 0.12), (8.600, 8.900), elevation=2.58,
    color="#efe6d6", light=light(45, "area", 0.45), label="Ivory scalloped flush light (ambient)")

# ================================================================ MASTER SUITE
upd("floating-bed-master-suite-1", size=(1.6, 2.1, 1.25), color=CHAMPAGNE, accent="#efe8da",
    label="Floating bed, champagne velvet, tall headboard")
upd("wallpaper-master-suite-1", apron="d5_sapphire_chevron", color="#1d365e",
    label="Sapphire panel wall with brass chevron inlay")
for lid in ("nightstand-master-suite-1", "nightstand-master-suite-2"):
    upd(lid, color=BLACK)
for lid in ("table-lamp-master-suite-1", "table-lamp-master-suite-2"):
    upd(lid, color=CHAMPAGNE)
upd("rug-master-suite-1", color="#4a1418", label="Oxblood rug")
restyle_storage("tv-console-master-suite-1", BLACK, ["gloss", "wood", "gloss"], [BLACK, WALNUT, BLACK],
                interior=MACASSAR)
upd("slat-panel-master-suite-1", color=WALNUT, label="Fluted walnut TV wall")
restyle_storage("wardrobe-master-suite-1", SAPPHIRE, ["wood", "gloss"], [WALNUT, SAPPHIRE], interior=MACASSAR)
restyle_storage("wardrobe-master-suite-2", SAPPHIRE, ["gloss", "wood", "gloss"], [SAPPHIRE, WALNUT, SAPPHIRE],
                interior=MACASSAR)
for lid in ("drape-master-suite-1", "drape-master-suite-2"):
    upd(lid, color=SAPPHIRE, label="Sapphire velvet blackout drape")
rm("track-light-master-suite-1")
add("ceiling-light-master-suite-1", "ceiling-light", "bedroom_2", (0.60, 0.60, 0.14), (1.750, 2.300),
    elevation=2.56, color=BRASS_M, light=light(45, "area", 0.5), label="Brass Deco flush dome (ambient)")
# dressing table corner in the open dressing
add("dressing-table-master-suite-1", "dressing-table", "bedroom_2", (0.75, 0.42, 0.75), (4.530, 2.385), color=BLACK,
    label="Black lacquer dressing table")
add("backlit-mirror-master-suite-1", "backlit-mirror", "bedroom_2", (0.50, 0.02, 0.80), (4.530, 2.185),
    elevation=1.05, color="#d9dde0", label="Arched brass mirror with halo (dressing)")
add("stool-master-suite-1", "stool", "bedroom_2", (0.40, 0.40, 0.46), (4.530, 2.790), color=OXBLOOD,
    label="Oxblood velvet stool")

# ================================================================ BALCONY
for lid in ("outdoor-dining-table-balcony-1", "outdoor-chair-balcony-1", "outdoor-chair-balcony-2"):
    upd(lid, color=WALNUT)
upd("ceiling-light-balcony-1", color=BRASS_M)
add("plant-balcony-1", "plant", "balcony", (0.45, 0.45, 1.00), (-1.380, 6.980), color="#3f6b35",
    label="Clipped bay laurel in a black pot")
add("plant-balcony-2", "plant", "balcony", (0.45, 0.45, 1.00), (-0.330, 10.600), color="#3f6b35",
    label="Clipped bay laurel in a black pot")

v.items = [items[lid] for lid in order]
OUT.write_text(variant_to_toml(v), encoding="utf-8")
print(f"wrote {OUT} ({len(v.items)} pieces)")
