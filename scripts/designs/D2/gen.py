"""D2 - 'Colour Drenched' variant generator: V1 copied, re-keyed, then redesigned.

Run from the repo root:  uv run python .tmp/designs/D2/gen.py
Writes .tmp/designs/D2/variants/D2.toml (sandbox only).
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

K = "D2"
OUT = Path(".tmp/designs/D2/variants/D2.toml")

# ---------------------------------------------------------------- palette (sRGB)
TEAL, TEAL_JOIN, TEAL_DEEP, PEACOCK = "#2d5f61", "#285a5c", "#1f4749", "#2e6b6b"
OXBLOOD, OX_JOIN, OX_DEEP, ROSEWOOD, BLUSH = "#5a2329", "#5f262c", "#4a1a20", "#b0645c", "#d9a091"
OCHRE, OCHRE_JOIN, OCHRE_DEEP = "#c08a2d", "#b98228", "#a37020"
OLIVE, OLIVE_JOIN = "#6b6a35", "#5c5b2a"
BUTTER, BUTTER_JOIN, MINT = "#efc66f", "#e2b75a", "#8fb5aa"
IVORY, INK = "#efe4d2", "#1c1c1e"
WALNUT, OAK = "#5e3f2a", "#cfb08a"  # the two woods (walnut joinery, light oak in the kids' room)
HONEY = "#b07f4f"  # honey-oak floor planks (third and last wood tone)
BRASS, BLACK = "#a8834a", "#151515"  # the two metals

v1 = load_variant("data/variants/V1.toml")
v = copy_variant(v1, K, "Colour Drenched")
v.description = ("Colour drenching / livable dopamine: every room wrapped in one saturated colour (walls, skirting, "
                 "ceiling, joinery, textiles tone-on-tone) - ochre hall, teal living, olive kitchen, oxblood suite, "
                 "rosewood bath, butter kids' room - tied together by honey oak, walnut, oxblood-fleck terrazzo and "
                 "aged brass.")
v.based_on = "V1"
v.true_colors = True
v.wall_color = IVORY

F = {
    "d2_honey_oak": dict(kind="parquet", size=[1.2, 0.19], color=HONEY, color2="#9a6c40", joint_color="#4a301c",
                         joint=0.0015, direction="x", roughness=0.42,
                         note="honey-oak planks: the warm common floor under every drenched colour"),
    "d2_terrazzo": dict(kind="tiles", size=[0.6, 0.6], color="#ece0cc", color2="#8c2f35", joint_color="#d8cab3",
                        joint=0.002, roughness=0.3,
                        note="ivory terrazzo with oxblood flecks 60 x 60 - hall, kitchen, both baths (one floor)"),
    "d2_teal_zellige": dict(kind="stone", size=[0.1, 0.1], color="#2f6e6e", color2="#1d4f52", joint_color="#d9cfbd",
                            joint=0.002, roughness=0.12, note="glossy teal zellige 10 x 10, ivory grout (bath 1)"),
    "d2_rose_zellige": dict(kind="stone", size=[0.075, 0.3], color="#b5716a", color2="#965149",
                            joint_color="#efe4d2", joint=0.002, roughness=0.12,
                            note="rosewood glazed 7.5 x 30 vertical stack (bath 2 + tub front)"),
    "d2_ochre_zellige": dict(kind="stone", size=[0.1, 0.1], color="#c99a3c", color2="#a87a22",
                             joint_color="#efe4d2", joint=0.002, roughness=0.12,
                             note="glossy ochre zellige backsplash, the hall colour carried into the kitchen"),
    "d2_teal_waves": dict(kind="mural", size=[3.8, 2.65], color="#2f6466", color2="#3b7371", joint_color="#2f6466",
                          joint=0.0, roughness=0.8, note="tone-on-tone teal wave mural behind the sofa"),
    "d2_oxblood_ripple": dict(kind="ripple", size=[3.04, 2.7], color="#6b2a30", color2="#4f1c22",
                              joint_color="#6b2a30", joint=0.0, roughness=0.85,
                              note="oxblood sculpted ripple wall behind the master bed (tonal relief)"),
    "d2_sunrise": dict(kind="watercolor", size=[3.1, 2.7], color="#f3e2b0", color2="#e3a27a",
                       joint_color="#f3e2b0", joint=0.0, roughness=0.8,
                       note="butter / apricot watercolour sunrise behind the child's bed"),
    "d2_ceil_olive": dict(kind="tiles", size=[3.0, 3.0], color="#757440", color2="#757440", joint_color="#757440",
                          joint=0.0, roughness=0.9, note="olive ceiling paint (drench)"),
    "d2_ceil_oxblood": dict(kind="tiles", size=[3.0, 3.0], color="#62282e", color2="#62282e",
                            joint_color="#62282e", joint=0.0, roughness=0.9, note="oxblood ceiling paint (drench)"),
    "d2_ceil_butter": dict(kind="tiles", size=[3.0, 3.0], color="#f0cf80", color2="#f0cf80",
                           joint_color="#f0cf80", joint=0.0, roughness=0.9, note="butter ceiling paint (drench)"),
}
v.finishes = {n: parse_finish(n, d) for n, d in F.items()}

LED = dict(stretch_led_color="#ffc98f", stretch_led_w_per_m=7.0)
v.rooms = {
    "hall": RoomFinish(floor="d2_terrazzo", paint=OCHRE, skirting=OCHRE_DEEP, stretch_ceiling=True,
                       stretch_color="#c8953c", **LED),
    "living": RoomFinish(floor="d2_honey_oak", paint=TEAL, skirting=TEAL_DEEP, stretch_ceiling=True,
                         stretch_color="#33686a", **LED),
    "kitchen": RoomFinish(floor="d2_terrazzo", paint=OLIVE, skirting=OLIVE_JOIN, ceiling="d2_ceil_olive"),
    "bath_1": RoomFinish(floor="d2_terrazzo", walls="d2_teal_zellige", stretch_ceiling=True,
                         stretch_color="#2f6e6e", **LED),
    "bath_2": RoomFinish(floor="d2_terrazzo", walls="d2_rose_zellige", stretch_ceiling=True,
                         stretch_color="#b5716a", **LED),
    "bedroom_1": RoomFinish(floor="light_oak", paint=BUTTER, skirting=BUTTER_JOIN, ceiling="d2_ceil_butter"),
    "bedroom_2": RoomFinish(floor="d2_honey_oak", paint=OXBLOOD, skirting=OX_DEEP, ceiling="d2_ceil_oxblood"),
    "balcony": RoomFinish(floor="deck"),
}

items = {it.local_id: it for it in v.items}
order = [it.local_id for it in v.items]


def get(lid):
    return items[lid]


def setp(lid, **kw):
    items[lid] = replace(items[lid], **kw)


def rename(old, new_type, **kw):
    """Same slot, new type -> new id (e.g. plush-corner-sofa -> tufted-corner-sofa)."""
    it = items.pop(old)
    room_slug = old[len(it.type) + 1:].rsplit("-", 1)[0]
    n = old.rsplit("-", 1)[1]
    new = f"{new_type}-{room_slug}-{n}"
    items[new] = replace(it, id=f"{K}.{new}", type=new_type, **kw)
    order[order.index(old)] = new


def remove(lid):
    items.pop(lid)
    order.remove(lid)


def add(lid, type_, room, size, pos, rot=0.0, elev=0.0, color="#b8b0a2", **kw):
    items[lid] = Item(id=f"{K}.{lid}", type=type_, room=room, size=tuple(size), position=tuple(pos), rotation=rot,
                      elevation=elev, color=color, **kw)
    order.append(lid)


def recolor_storage(lid, body, fronts=None, handle=BRASS, interior=None, wood=WALNUT):
    """Tone-on-tone joinery: body + fronts in the room colour, 'wood' modules walnut, brass handles."""
    it = items[lid]
    st = it.storage
    mods = tuple(replace(m, front_color=(wood if m.finish == "wood" else (fronts or body)) if m.front_color else "")
                 for m in st.modules)
    items[lid] = replace(it, color=body, storage=replace(st, modules=mods, handle_color=handle,
                                                         interior_color=interior if interior is not None
                                                         else (st.interior_color and wood)))


# ================================================================= LIVING - teal drench
rename("plush-corner-sofa-living-1", "tufted-corner-sofa", color=PEACOCK, accent=WALNUT,
       note="peacock-teal velvet blocks: tone-on-tone with the teal walls")
rename("plush-armchair-living-1", "tub-armchair", color=OCHRE, size=(0.85, 0.82, 0.72),
       note="ochre velvet tub chair - the hall colour pops against the teal")
rename("plush-armchair-living-2", "tub-armchair", color=OCHRE, size=(0.85, 0.82, 0.72))
setp("organic-shag-rug-living-1", color=BLUSH)
setp("round-coffee-table-living-1", color=OX_JOIN, note="oxblood lacquer drum - the suite colour as a graphic dot")
setp("round-side-table-living-1", color=BRASS)
recolor_storage("wardrobe-living-1", TEAL_JOIN)
setp("slat-panel-living-1", color=TEAL_JOIN)
setp("wall-tv-living-1", color=INK)
setp("wallpaper-living-1", apron="d2_teal_waves")
setp("floor-lamp-living-1", color=BRASS)
setp("infinity-pendant-light-living-1", color=BRASS)
for d in ("drape-living-1", "drape-living-2", "drape-living-3", "drape-living-4"):
    setp(d, color="#234f51")
for s in ("sheer-curtain-living-1", "sheer-curtain-living-2"):
    setp(s, color=IVORY)
setp("panel-desk-living-1", color=WALNUT, note="work desk 160 x 80: window on the left side, no screen glare")
setp("gaming-chair-living-1", color=OX_JOIN)
# media console floating under the TV + an open bookcase beside the TV wall
add("media-console-living-1", "media-console", "living", (1.8, 0.4, 0.42), (2.6, 6.972), 0, 0.22, TEAL_DEEP,
    storage=Storage(handle_color=BRASS, modules=(Module(0.6, (Front("drawers", None, 2),)),
                                                 Module(0.6, (Front("flap"),), finish="wood", front_color=WALNUT),
                                                 Module(0.6, (Front("drawers", None, 2),)))),
    note="floating media console: closed storage under the TV")
add("bookcase-living-1", "bookcase", "living", (0.8, 0.35, 2.2), (4.35, 6.925), 0, 0.0, OX_JOIN,
    storage=Storage(handle_color=BRASS, interior_color=OX_JOIN, modules=(
        Module(0.8, (Front("open"),), interior=tuple(Fitting("shelf", z) for z in (0.5, 0.92, 1.34, 1.76))),)),
    note="oxblood open bookcase - books + objects, the graphic accent of the teal room")
for i, (z, c, w) in enumerate(((0.5, OCHRE, 0.5), (0.92, IVORY, 0.4), (1.34, PEACOCK, 0.55), (1.76, BLUSH, 0.35))):
    add(f"books-living-{i + 1}", "books", "living", (w, 0.22, 0.24), (4.35 - (0.75 - w) / 2 + 0.02, 6.93), 0, z, c)
add("vase-living-1", "vase", "living", (0.13, 0.13, 0.22), (4.62, 6.93), 0, 0.92, OCHRE)
add("table-lamp-living-1", "table-lamp", "living", (0.25, 0.25, 0.4), (1.95, 6.98), 0, 0.64, OCHRE,
    light=Light(kind="point", watts=12.0, color="#ffd29e", size=0.1), note="accent lamp on the media console")

# ================================================================= KITCHEN - olive drench
for lid in ("base-cabinet-kitchen-1", "base-cabinet-kitchen-2", "base-cabinet-kitchen-3", "tall-cabinet-kitchen-1"):
    recolor_storage(lid, OLIVE_JOIN)
for lid in ("oven-kitchen-1", "plinth-kitchen-1"):
    setp(lid, color=OLIVE_JOIN)
recolor_storage("wall-cabinet-kitchen-2", OLIVE_JOIN, handle=BRASS)
recolor_storage("wall-cabinet-kitchen-1", WALNUT, handle=BRASS)
for lid in ("countertop-kitchen-1", "countertop-kitchen-2", "countertop-kitchen-3", "countertop-kitchen-4"):
    setp(lid, color=IVORY)
setp("backsplash-kitchen-1", apron="d2_ochre_zellige")
setp("dining-table-kitchen-1", color=WALNUT)
for lid in ("upholstered-chair-kitchen-1", "upholstered-chair-kitchen-2", "upholstered-chair-kitchen-5",
            "upholstered-chair-kitchen-6"):
    setp(lid, color=ROSEWOOD, metal=BRASS)
setp("linear-pendant-light-kitchen-1", color=BRASS)
setp("venetian-blind-kitchen-1", color=IVORY)
setp("serving-bowl-kitchen-1", color=OCHRE)

# ================================================================= HALL - ochre drench
recolor_storage("wardrobe-hall-1", OCHRE_JOIN)
setp("slat-panel-hall-1", color=OCHRE_JOIN)
for lid in ("wall-shelf-hall-1", "wall-shelf-hall-2"):
    setp(lid, color=WALNUT)
setp("vase-hall-1", color=ROSEWOOD)
setp("vase-hall-2", color=PEACOCK)
setp("doormat-hall-1", color=OX_DEEP)
setp("shoes-hall-1", position=(5.37, 5.55), rotation=270)  # off the entrance-door swing, by the bench
setp("shoes-hall-2", position=(5.37, 6.05), rotation=270, color=ROSEWOOD)
# bench with shoe drawers + cushion, mirror and a brass sconce on the free kitchen-side wall (x 4.825)
add("shoe-bench-cabinet-hall-1", "shoe-bench-cabinet", "hall", (0.95, 0.38, 0.42), (5.015, 5.81), 270, 0.0,
    OCHRE_JOIN, storage=Storage(plinth=0.06, handle_color=BRASS, modules=(
        Module(0.475, (Front("drawer"),)), Module(0.475, (Front("drawer"),)))),
    note="shoe drawers you sit on: with the 0.82 m wardrobe = 1.77 m closed coat + shoe run")
add("cushion-hall-1", "cushion", "hall", (0.93, 0.36, 0.06), (5.015, 5.81), 270, 0.42, OX_JOIN)
add("mirror-hall-1", "mirror", "hall", (0.6, 0.02, 1.0), (4.835, 5.81), 270, 0.95, "#d9dde0")
add("wall-sconce-hall-1", "wall-sconce", "hall", (0.14, 0.1, 0.22), (4.875, 6.22), 270, 1.75, BRASS,
    light=Light(kind="point", watts=8.0, color="#ffd29e", size=0.1), note="accent + mirror light")

# ================================================================= BATH 1 - teal zellige
for lid in ("vanity-frame-bathroom-1-1", "slat-screen-bathroom-1-1", "slat-screen-bathroom-1-2"):
    setp(lid, color=WALNUT)
recolor_storage("tall-cabinet-bathroom-1-1", WALNUT)
setp("towels-bathroom-1-1", color=OCHRE)
setp("vessel-sink-bathroom-1-1", color=IVORY)
for lid in ("backlit-mirror-bathroom-1-1", "shower-head-bathroom-1-1"):
    setp(lid, metal=BRASS)
for lid in ("toilet-paper-holder-bathroom-1-1", "toilet-roll-stand-bathroom-1-1", "toilet-brush-bathroom-1-1"):
    setp(lid, color=BRASS)
setp("wall-niche-bathroom-1-1", color="#2f6e6e")
setp("walk-in-shower-bathroom-1-1", accent="#ece0cc")

# ================================================================= BATH 2 - rosewood zellige
for lid in ("vanity-frame-master-bathroom-1",):
    setp(lid, color=WALNUT)
recolor_storage("tall-cabinet-master-bathroom-1", WALNUT)
setp("towels-master-bathroom-1", color=PEACOCK)
setp("vessel-sink-master-bathroom-1", color=IVORY)
setp("bathtub-master-bathroom-1", apron="d2_rose_zellige")
for lid in ("backlit-mirror-master-bathroom-1", "shower-head-master-bathroom-1", "bath-screen-master-bathroom-1"):
    setp(lid, metal=BRASS)
for lid in ("toilet-paper-holder-master-bathroom-1", "toilet-roll-stand-master-bathroom-1",
            "toilet-brush-master-bathroom-1"):
    setp(lid, color=BRASS)
setp("wall-niche-master-bathroom-1", color="#b5716a")

# ================================================================= KIDS (bedroom 1) - butter drench
setp("floating-bed-bedroom-1-1", color=OAK, accent=BLUSH, tag_color=PEACOCK)
recolor_storage("wardrobe-bedroom-1-1", BUTTER_JOIN, handle=OAK, interior=BUTTER_JOIN)
it = items["wardrobe-bedroom-1-1"]
items["wardrobe-bedroom-1-1"] = replace(it, storage=replace(it.storage, modules=tuple(
    replace(m, front_color=MINT if m.label == "wood column" else BUTTER_JOIN) for m in it.storage.modules)))
recolor_storage("storage-cabinet-bedroom-1-1", BUTTER_JOIN, handle=OAK)
setp("nightstand-bedroom-1-1", color=MINT)
setp("rug-bedroom-1-1", color=MINT)
setp("slat-panel-bedroom-1-1", color=OAK)
setp("desk-bedroom-1-1", color=OAK)
setp("chair-bedroom-1-1", color=MINT)
setp("table-lamp-bedroom-1-1", color=IVORY)
setp("wallpaper-bedroom-1-1", apron="d2_sunrise")
for d in ("drape-bedroom-1-1", "drape-bedroom-1-2"):
    setp(d, color="#c48e34", note="blackout drape")
setp("sheer-curtain-bedroom-1-1", color=IVORY)
# low open toy shelf at child height, rounded-feel light oak, beside the storage cabinet
add("toy-unit-bedroom-1-1", "toy-unit", "bedroom_1", (0.75, 0.35, 0.6), (7.13, 8.25), 270, 0.0, OAK,
    storage=Storage(plinth=0.04, handle_color=OAK, modules=(
        Module(0.75, (Front("open"),), interior=(Fitting("shelf", 0.3),)),)),
    note="low open toy + picture-book shelf (60 cm, nothing tippy)")
add("toy-basket-bedroom-1-1", "toy-basket", "bedroom_1", (0.3, 0.25, 0.2), (7.13, 8.42), 270, 0.37, ROSEWOOD)
add("toy-basket-bedroom-1-2", "toy-basket", "bedroom_1", (0.3, 0.25, 0.2), (7.13, 8.08), 270, 0.37, PEACOCK)
add("night-light-bedroom-1-1", "night-light", "bedroom_1", (0.12, 0.12, 0.12), (7.2, 8.52), 0, 0.6, BUTTER,
    light=Light(kind="point", watts=3.0, color="#ffc98f", size=0.06), note="soft nightlight")

# ================================================================= MASTER SUITE - oxblood drench
setp("floating-bed-master-suite-1", color="#7a3238", accent=BLUSH, note="oxblood velvet bed, blush linen")
for lid in ("nightstand-master-suite-1", "nightstand-master-suite-2"):
    setp(lid, color=WALNUT)
for lid in ("table-lamp-master-suite-1", "table-lamp-master-suite-2"):
    setp(lid, color=OCHRE)
setp("rug-master-suite-1", color=ROSEWOOD)
recolor_storage("tv-console-master-suite-1", OX_JOIN)
recolor_storage("wardrobe-master-suite-1", OX_JOIN)
recolor_storage("wardrobe-master-suite-2", OX_JOIN)
setp("slat-panel-master-suite-1", color=OX_JOIN, size=(2.4, 0.03, 2.69))
setp("wallpaper-master-suite-1", apron="d2_oxblood_ripple")
for d in ("drape-master-suite-1", "drape-master-suite-2"):
    setp(d, color=OX_DEEP, note="blackout drape")
setp("sheer-curtain-master-suite-1", color=IVORY)
setp("wall-tv-master-suite-1", color=INK)
# oxblood absorbs light: a tinted stretch ceiling with a warm LED line (ambient cove layer) + stronger tracks
v.rooms["bedroom_2"] = RoomFinish(floor="d2_honey_oak", paint=OXBLOOD, skirting=OX_DEEP, stretch_ceiling=True,
                                  stretch_color="#6a2c32", stretch_led_color="#ffc98f", stretch_led_w_per_m=9.0)
for lid in ("drape-master-suite-1", "drape-master-suite-2", "sheer-curtain-master-suite-1"):
    it = items[lid]
    setp(lid, size=(it.size[0], it.size[1], 2.63))
setp("slat-panel-master-suite-1", size=(2.4, 0.03, 2.64))
setp("wallpaper-master-suite-1", size=(3.04, 0.004, 2.64))
for lid in ("track-light-master-suite-1", "track-light-master-suite-2"):
    tr = items[lid].track
    setp(lid, track=replace(tr, watts=tr.watts * 1.6))
add("bench-master-suite-1", "bench", "bedroom_2", (1.3, 0.36, 0.45), (1.75, 2.56), 0, 0.0, OCHRE,
    note="ochre velvet bench at the bed foot (0.78 m left to the console)")
add("mirror-master-suite-1", "mirror", "bedroom_2", (0.42, 0.02, 1.7), (5.95, 2.186), 0, 0.3, "#d9dde0",
    note="full-length mirror in the dressing, beside the bath-2 door")

# ================================================================= BALCONY
for lid in ("outdoor-chair-balcony-1", "outdoor-chair-balcony-2", "outdoor-dining-table-balcony-1"):
    setp(lid, color="#9a6b43")
setp("mug-balcony-1", color=OCHRE)
setp("mug-balcony-2", color=PEACOCK)
add("plant-balcony-1", "plant", "balcony", (0.4, 0.4, 1.1), (-1.38, 6.96), 0, 0.0, "#4f6b34")
add("plant-balcony-2", "plant", "balcony", (0.4, 0.4, 0.6), (-0.35, 10.6), 0, 0.0, "#5f7a3a")
add("outdoor-rug-balcony-1", "outdoor-rug", "balcony", (1.0, 2.4, 0.008), (-0.85, 8.25), 0, 0.0, OCHRE,
    note="ochre outdoor rug: the hall colour steps out onto the deck")

# ================================================================= lights: tracks black, warm
v.items = [replace(items[lid], status="draft") for lid in order]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(variant_to_toml(v), encoding="utf-8")
print("wrote", OUT, len(v.items), "pieces")
