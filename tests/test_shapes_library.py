"""Shape library (apartment_core.shapes_library): every new type has a recognisable shape that stays inside
its footprint, sinks still bind to the plumbing, lamps light the scene, storage library types open."""

import pytest

from apartment_core import load
from apartment_core.furniture import (
    ACCENTS,
    BRASS,
    CUSHIONS,
    SHADES,
    Item,
    casts_shadow,
    is_light,
    is_storage,
    item_parts,
    light_of,
    light_source_pos,
    on_point,
    recolored_parts,
    serves,
    storage_layout,
    validate_variants,
)
from apartment_core.furniture import Variant as V

# type -> suggested size (w, d, h) and elevation
NEW_TYPES = {
    "console-sink": ((0.80, 0.48, 0.86), 0.0),
    "integrated-sink": ((1.00, 0.46, 0.86), 0.0),
    "pedestal-sink": ((0.56, 0.46, 0.86), 0.0),
    "round-mirror": ((0.70, 0.03, 0.70), 1.15),
    "arched-mirror": ((0.60, 0.03, 1.10), 1.05),
    "backlit-round-mirror": ((0.70, 0.04, 0.70), 1.15),
    "mirror-cabinet": ((0.80, 0.15, 0.70), 1.15),
    "ladder-towel-rail": ((0.45, 0.35, 1.60), 0.0),
    "towel-rail": ((0.60, 0.10, 0.50), 0.85),
    "open-shelf-unit": ((0.40, 0.30, 1.60), 0.0),
    "framed-art": ((0.80, 0.03, 1.00), 1.20),
    "gallery-wall": ((1.60, 0.03, 1.00), 1.25),
    "painted-arch": ((1.20, 0.006, 2.20), 0.0),
    "colour-block": ((1.80, 0.006, 1.20), 0.0),
    "wall-panelling": ((2.40, 0.03, 2.20), 0.0),
    "fluted-panel": ((1.20, 0.03, 2.40), 0.0),
    "floating-shelf": ((0.80, 0.22, 0.04), 1.30),
    "pegboard": ((0.80, 0.15, 0.60), 1.10),
    "globe-pendant": ((0.30, 0.30, 0.80), 1.90),
    "cluster-pendant": ((0.60, 0.60, 0.90), 1.80),
    "arc-floor-lamp": ((1.50, 0.40, 2.05), 0.0),
    "wall-sconce": ((0.14, 0.16, 0.25), 1.60),
    "picture-light": ((0.50, 0.15, 0.12), 2.20),
    "mushroom-lamp": ((0.30, 0.30, 0.40), 0.0),
    "legged-sofa": ((2.20, 0.92, 0.82), 0.0),
    "modular-sofa": ((2.80, 1.05, 0.70), 0.0),
    "pouf": ((0.50, 0.50, 0.42), 0.0),
    "daybed": ((2.00, 0.95, 0.80), 0.0),
    "bench": ((1.30, 0.40, 0.46), 0.0),
    "ottoman": ((0.60, 0.45, 0.42), 0.0),
    "floor-tv": ((1.45, 0.45, 1.55), 0.0),
    "easel-floor-tv": ((1.25, 0.60, 1.60), 0.0),
    "swivel-tv": ((1.25, 0.50, 1.45), 0.0),
    "projector-screen": ((2.40, 0.12, 1.70), 1.00),
    "peninsula-counter": ((1.60, 0.90, 0.92), 0.0),
    "bar-stool": ((0.42, 0.42, 0.66), 0.0),
    "bunk-shelf": ((1.10, 0.33, 0.75), 0.0),
    "toy-chest": ((0.80, 0.42, 0.48), 0.0),
    "crib": ((1.26, 0.66, 0.90), 0.0),
    "changing-table": ((1.00, 0.55, 1.00), 0.0),
}
SINKS = ("console-sink", "integrated-sink", "pedestal-sink")
LAMPS = ("globe-pendant", "cluster-pendant", "arc-floor-lamp", "wall-sconce", "picture-light", "mushroom-lamp")
STORAGE = ("mirror-cabinet", "open-shelf-unit", "toy-chest")
TAP_ABOVE_RIM = 0.30  # sinks: h is the rim height, the mixer stands above it (as for vessel-sink)


def _item(type_: str, **kw) -> Item:
    size, elev = NEW_TYPES[type_]
    return Item(id=f"S.{type_}-living-1", type=type_, room="living", size=size, position=(3.0, 8.0),
                elevation=elev, **kw)


@pytest.mark.parametrize("type_", [t for t in NEW_TYPES if t not in STORAGE])
@pytest.mark.parametrize("mirror", [False, True])
def test_new_shape_inside_its_footprint(type_, mirror):
    (w, d, h), _ = NEW_TYPES[type_]
    parts = item_parts(type_, w, d, h, mirror=mirror)
    assert len(parts) > 1 or type_ == "floating-shelf", "a library type must not fall back to a plain box"
    top = h + (TAP_ABOVE_RIM if type_ in SINKS else 0.0)
    for p in parts:
        x1, y1, z1, x2, y2, z2 = p.box
        assert x1 < x2 and y1 < y2 and z1 < z2, (type_, p)
        assert -w / 2 - 1e-6 <= x1 and x2 <= w / 2 + 1e-6, (type_, p)
        assert -d / 2 - 1e-6 <= y1 and y2 <= d / 2 + 1e-6, (type_, p)
        assert -1e-6 <= z1 and z2 <= top + 1e-6, (type_, p)
        assert p.shade in SHADES and p.shape in ("box", "cyl", "ycyl", "xcyl")


def test_library_shapes_scale_with_their_size():
    small = item_parts("legged-sofa", 1.6, 0.85, 0.8)
    big = item_parts("legged-sofa", 2.6, 0.95, 0.8)
    assert len(big) > len(small)  # more seat cushions
    assert len(item_parts("modular-sofa", 3.6, 1.0, 0.7)) > len(item_parts("modular-sofa", 1.9, 1.0, 0.7))
    assert item_parts("cluster-pendant", 0.4, 0.4, 0.8) != item_parts("cluster-pendant", 0.7, 0.7, 0.8)


def test_existing_types_keep_their_shapes():
    assert len(item_parts("sink", 0.6, 0.45, 0.2)) == 6  # basin + tap
    assert item_parts("banquette-bench", 2.0, 0.4, 0.42) == item_parts("unknown-thing", 2.0, 0.4, 0.42)
    assert item_parts("backlit-mirror", 0.6, 0.03, 0.9)[0].shade == "emit"


def test_new_sinks_bind_to_the_plumbing():
    apt = load()
    point = next(p for p in apt.fixed_points if p.id == "FX_bath1_sink")
    for type_ in SINKS:
        it = _item(type_)
        assert serves(point, it), type_
        on = Item(id=f"S.{type_}-bathroom-1-1", type=type_, room="bath_1", size=it.size, rotation=90,
                  position=(10.245 - it.size[1] / 2, 5.67))
        assert on_point(point, on)
        away = Item(id=f"S.{type_}-living-1", type=type_, room="living", size=it.size, position=(3.0, 8.0))
        codes = [i.code for i in validate_variants(apt, [V("S", "S", items=[away])])]
        assert "fixed_point" in codes, type_


def test_new_sink_taps_follow_metal():
    it = _item("console-sink", metal="#202020")
    parts = recolored_parts(it, item_parts(it.type, *it.size))
    assert not any(p.color == BRASS for p in parts)
    assert any(p.color == "#202020" for p in parts)


@pytest.mark.parametrize("type_", LAMPS)
def test_lamps_get_a_default_light_inside_the_footprint(type_):
    it = _item(type_)
    assert is_light(type_)
    lt = light_of(it)
    assert lt.watts > 0
    x, y, z = light_source_pos(it)
    w, d, h = it.size
    assert abs(x) <= w / 2 and abs(y) <= d / 2 and -0.05 <= z <= h, (type_, (x, y, z))
    assert any(p.shade == "emit" for p in item_parts(type_, *it.size)), "a lamp needs a glowing diffuser"


def test_light_defaults_per_lamp():
    assert casts_shadow(_item("globe-pendant")) and casts_shadow(_item("cluster-pendant"))  # statement pendants
    assert not casts_shadow(_item("arc-floor-lamp")) and not casts_shadow(_item("wall-sconce"))
    assert light_of(_item("picture-light")).kind == "spot"
    assert light_of(_item("cluster-pendant")).watts > light_of(_item("globe-pendant")).watts
    # arc lamp: the bulb is in the shade at the far end of the arm; mirror = the other end
    x, _, z = light_source_pos(_item("arc-floor-lamp"))
    assert x > 0.4 and 1.0 < z < 2.0
    assert light_source_pos(_item("arc-floor-lamp", mirror=True))[0] == pytest.approx(-x)
    # pendants keep the bulb under the globe (they cast shadows - a bulb inside would be dark)
    assert light_source_pos(_item("globe-pendant"))[2] < 0


def test_narrow_arc_lamp_is_still_a_lamp():
    parts = item_parts("arc-floor-lamp", 0.3, 0.3, 1.65)  # D4's size: no room to arc -> straight stem + dome
    assert any(p.shade == "emit" for p in parts)
    assert all(-0.15 - 1e-6 <= p.box[0] and p.box[3] <= 0.15 + 1e-6 for p in parts)


@pytest.mark.parametrize("type_", STORAGE)
def test_storage_library_types(type_):
    assert is_storage(type_)
    lay = storage_layout(_item(type_))
    if type_ == "open-shelf-unit":
        assert not lay.fronts and 2 <= len(lay.interior) <= 5
        assert all(name.split("/")[1].startswith("shelf") for name, _, _ in lay.interior)
    if type_ == "toy-chest":
        assert [mp.motion for mp in lay.fronts] == ["flap"]
    if type_ == "mirror-cabinet":
        fronts = [p for mp in lay.fronts for p in mp.parts]
        assert fronts and all(p.finish == "mirror" for p in fronts if p.shade == "front")
        assert not any(p.shade == "handle" for p in fronts)  # push-to-open


def test_recolour_fields_reach_library_parts():
    sofa = _item("legged-sofa", accent="#111111", cushion="#336699")
    parts = recolored_parts(sofa, item_parts(sofa.type, *sofa.size))
    assert any(p.color == "#111111" for p in parts) and not any(p.color == ACCENTS[0] for p in parts)
    assert not any(p.color in CUSHIONS for p in parts)
    for type_, field in (("framed-art", "accent"), ("gallery-wall", "metal"), ("crib", "cushion"),
                         ("globe-pendant", "metal"), ("bar-stool", "metal"), ("daybed", "accent")):
        it = _item(type_, **{field: "#123456"})
        assert any(p.color == "#123456" for p in recolored_parts(it, item_parts(type_, *it.size))), type_


def test_wall_paint_pieces_are_thin_and_never_overlap():
    for type_ in ("painted-arch", "colour-block"):
        (w, d, h), _ = NEW_TYPES[type_]
        assert all(p.box[4] - p.box[1] <= 0.002 + 1e-9 and p.box[4] == pytest.approx(d / 2)
                   for p in item_parts(type_, w, d, h))
    apt = load()
    sofa = Item(id="S.legged-sofa-living-1", type="legged-sofa", room="living", size=(2.2, 0.92, 0.82),
                position=(3.0, 10.45))
    block = Item(id="S.colour-block-living-1", type="colour-block", room="living", size=(2.6, 0.006, 1.2),
                 position=(3.0, 10.91))
    panel = Item(id="S.wall-panelling-living-1", type="wall-panelling", room="living", size=(2.6, 0.5, 1.2),
                 position=(3.0, 10.6))
    codes = [i.code for i in validate_variants(apt, [V("S", "S", items=[sofa, block, panel])])]
    assert "furniture_overlap" not in codes
