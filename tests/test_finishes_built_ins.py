"""Variant room finishes (floor / wall tiles), built-ins (boiler) and the new bathroom shapes (ADR 0009)."""

from dataclasses import replace

import pytest

from apartment_core import load
from apartment_core.furniture import (
    Item,
    RoomFinish,
    Storage,
    Variant,
    item_parts,
    load_variants,
    storage_layout,
    validate_variants,
    variant_to_toml,
)
from apartment_core.geometry import cladding_boxes, cladding_walls


@pytest.fixture(scope="module")
def apt():
    return load()


def test_boiler_is_built_in_above_the_washer_up_to_the_ceiling(apt):
    (boiler,) = [b for b in apt.built_ins if b.type == "boiler"]
    washer = next(f for f in apt.fixed_points if f.kind == "washer")
    assert boiler.room == washer.room == "bath_1"
    assert abs(boiler.position[0] - washer.position[0]) < 0.05
    assert boiler.elevation >= 0.85  # clears the washing machine
    assert apt.levels.ceiling_height - boiler.top <= 0.10


def test_cladding_skins_every_wall_and_leaves_the_door_open():
    square = ((0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (0.0, 1.0))
    wall = ((0.5, -0.1, 2.0, 0.0), True, [(0.8, 1.6, 0.0, 2.1)])  # door 0.8-1.6 in the wall under y = 0
    boxes = cladding_boxes(square, [wall], 2.7, 0.01)
    bottom = [b for b in boxes if b[1] == 0.0 and b[4] == 0.01]
    assert any(b[0] == 0.8 and b[3] == 1.6 and b[2] == 2.1 for b in bottom)  # only the lintel over the door
    assert not any(b[0] < 1.2 < b[3] and b[2] < 1.0 for b in bottom)
    assert all(0.0 <= b[1] and b[4] <= 1.0 and 0.0 <= b[0] and b[3] <= 2.0 for b in boxes)  # inside the room


def test_variant_room_finishes_round_trip_and_validate(apt, tmp_path):
    v = Variant(key="T", name="t", rooms={"bath_1": RoomFinish(floor="oak_tiles", walls="greige_stone")})
    path = tmp_path / "T.toml"
    path.write_text(variant_to_toml(v))
    (back,) = load_variants(tmp_path)
    assert back.rooms == v.rooms
    bad = Variant(key="T", name="t", rooms={"bath_1": RoomFinish(walls="nope"), "attic": RoomFinish()})
    assert len([i for i in validate_variants(apt, [bad]) if i.code == "finish"]) == 2


def test_v1_bathrooms_match_the_owner_photo(apt):
    v1 = next(v for v in load_variants() if v.key == "V1")
    assert {"bath_1", "bath_2"} <= set(v1.rooms)
    assert v1.rooms["hall"].floor == v1.rooms["kitchen"].walls == "calacatta_gold"  # owner photo gresie.jpg
    for room in ("bath_1", "bath_2"):
        types = [it.type for it in v1.items if it.room == room]
        assert [t for t in types if t.endswith("sink")] == ["vessel-sink"]  # one bowl per bathroom
        assert "backlit-mirror" in types and "toilet" in types
    assert not [i for i in validate_variants(apt, [v1]) if i.level == "error"]


def test_furniture_into_the_boiler_is_flagged(apt):
    b = apt.built_ins[0]
    it = Item(id="T.cabinet-bathroom-1-1", type="wall-cabinet", room=b.room, size=(0.5, 0.3, 0.6), position=b.position,
              elevation=1.5)
    issues = validate_variants(apt, [Variant(key="T", name="t", items=[it])])
    assert any(i.code == "furniture_built_in" for i in issues)
    low = replace(it, elevation=0.0, size=(0.5, 0.3, 0.5))
    assert not any(i.code == "furniture_built_in" for i in validate_variants(apt, [Variant("T", "t", items=[low])]))


def test_wall_hung_toilet_does_not_touch_the_floor():
    ceramic = [p for p in item_parts("toilet", 0.38, 0.55, 1.1) if p.shade == "ceramic"]
    assert min(p.box[2] for p in ceramic) >= 0.15


def test_push_to_open_storage_has_no_handles():
    it = Item(id="T.vanity-bathroom-1-1", type="vanity", room="bath_1", size=(1.0, 0.5, 0.3), position=(0, 0),
              elevation=0.55, storage=Storage(handles=False))
    lay = storage_layout(it)
    assert lay.fronts and not any(p.shade == "handle" for mp in lay.fronts for p in mp.parts)


def test_each_wall_skin_starts_its_tile_layout_at_its_corner():
    square = ((0.0, 0.0), (1.8, 0.0), (1.8, 2.5), (0.0, 2.5))
    skins = cladding_walls(square, [], 2.7, 0.01)
    assert sorted(o for o, _ in skins) == pytest.approx([(0.0, 0.01), (0.0, 2.49), (0.01, 0.0), (1.79, 0.0)])
    for (ox, oy), boxes in skins:  # origin lies on the tiled (room-side) face, at the low corner
        assert any(abs(b[0] - ox) < 1e-9 or abs(b[3] - ox) < 1e-9 for b in boxes)
        assert any(abs(b[1] - oy) < 1e-9 or abs(b[4] - oy) < 1e-9 for b in boxes)


def test_ceiling_finish_round_trips(tmp_path):
    v = Variant(key="T", name="t", rooms={"bath_2": RoomFinish(walls="greige_stone", ceiling="greige_stone")})
    (tmp_path / "T.toml").write_text(variant_to_toml(v))
    assert load_variants(tmp_path)[0].rooms == v.rooms


def test_washer_details_stand_proud_of_the_body_front():
    parts = item_parts("washing-machine", 0.6, 0.6, 0.85)
    body = parts[0].box
    for p in parts[2:]:  # strip, drawer, display, knob, door ring, glass
        assert p.box[4] > body[4] + 1e-4  # front face in front of the body: no flickering coplanar faces
    assert any(p.shape == "ycyl" for p in parts)  # round door


def test_bath_screen_and_shower_head_on_the_v1_bathtub():
    v1 = next(v for v in load_variants() if v.key == "V1")
    types = {it.type for it in v1.items if it.room == "bath_2"}
    assert {"bath-screen", "shower-head", "bathtub"} <= types


def test_v1_bathtub_spans_bath_2_wall_to_wall_with_a_tiled_front(apt):
    v1 = next(v for v in load_variants() if v.key == "V1")
    tub = v1.item("bathtub-master-bathroom-1")
    ys = [p[1] for p in apt.room("bath_2").polygon]
    assert tub.size[0] == pytest.approx(max(ys) - min(ys) - 0.02)  # wall to wall, minus 1 cm tiles each side
    assert tub.apron == "greige_stone"
    bad = replace(tub, id="T.rug-master-bathroom-1", type="rug")
    assert any(i.code == "finish" for i in validate_variants(apt, [Variant("T", "t", items=[bad])]))


def test_c_shaped_vanity_has_a_thick_top_and_thin_side_and_shelf():
    top, side, shelf = (p.box for p in item_parts("vanity-frame", 1.0, 0.5, 0.6))
    th = lambda b: b[5] - b[2]  # noqa: E731
    assert th(top) >= 3 * th(shelf) and top[5] == pytest.approx(0.6) and shelf[2] == 0
    assert side[3] - side[0] < 0.05 and side[3] == pytest.approx(0.5)  # thin, at one end
    v1 = next(v for v in load_variants() if v.key == "V1")
    for room in ("bath_1", "bath_2"):
        assert {"vanity-frame", "towels", "vessel-sink"} <= {it.type for it in v1.items if it.room == room}


def test_track_heads_aim_at_their_targets_and_round_trip(apt, tmp_path):
    from apartment_core.furniture import Track, TrackHead, track_heads

    it = Item(id="T.track-light-hall-1", type="track-light", room="hall", size=(1.8, 0.03, 0.04),
              position=(7.25, 5.19), rotation=90, elevation=2.66,
              track=Track(heads=(TrackHead(0.5, (7.25, 5.69, 0.0)),)))
    ((pos, d),) = track_heads(it)
    assert pos[0] == pytest.approx(7.25) and pos[1] == pytest.approx(5.69)  # rotation 90: local +x = world +y
    assert d == pytest.approx((0.0, 0.0, -1.0), abs=1e-9)  # straight down onto its target
    v = Variant(key="T", name="t", items=[it])
    (tmp_path / "T.toml").write_text(variant_to_toml(v))
    assert load_variants(tmp_path)[0].items[0].track == it.track


def test_v1_uses_track_lights_instead_of_downlights_and_panels():
    v1 = next(v for v in load_variants() if v.key == "V1")
    types = {it.type for it in v1.items}
    assert "track-light" in types
    assert not types & {"recessed-spotlight", "led-panel-light", "ceiling-light", "ring-ceiling-light"} - {
        it.type for it in v1.items if it.room == "balcony"}


def test_corner_sofa_overlap_uses_its_l_shape(apt):
    v1 = next(v for v in load_variants() if v.key == "V1")
    sofa, table = v1.item("plush-corner-sofa-living-1"), v1.item("round-coffee-table-living-1")
    assert len(sofa.footprint_parts()) == 2
    issues = validate_variants(apt, [v1])
    assert not [i for i in issues if i.code == "furniture_overlap" and sofa.id in i.message and table.id in i.message]


def test_push_to_open_flap_has_no_empty_parts():
    from apartment_core.furniture import Front, Module

    st = Storage(modules=(Module(width=0.8, fronts=(Front("drawers", 0.3, 2), Front("flap"))),), handles=False)
    it = Item(id="T.shoe-cabinet-hall-1", type="shoe-cabinet", room="hall", size=(0.8, 0.4, 0.9), position=(0, 0),
              elevation=0.12, storage=st)
    assert all(p is not None for mp in storage_layout(it).fronts for p in mp.parts)


def test_open_niche_over_drawers_gets_a_fixed_shelf():
    from apartment_core.furniture import Front, Module

    m = Module(width=0.6, fronts=(Front("door-right", 0.85), Front("open", 0.75), Front("drawers", 0.6, 3), Front("open")))
    it = Item(id="T.wardrobe-bedroom-1-1", type="wardrobe", room="bedroom_1", size=(0.6, 0.6, 2.6), position=(0, 0),
              storage=Storage(modules=(m,)))
    lay = storage_layout(it)
    flat = [p.box for p in lay.carcass if p.box[5] - p.box[2] < 0.03 and p.box[3] - p.box[0] > 0.4]  # horizontal panels
    tops = {round((b[2] + b[5]) / 2, 2) for b in flat}
    drawers_top = round(2.6 - 0.003 - 0.85 - 0.75, 2)
    assert any(abs(t - drawers_top) < 0.02 for t in tops)  # the top drawer is covered from the niche


def test_door_handles_off_keeps_drawer_handles_only():
    from apartment_core.furniture import Front, Module

    m = Module(width=0.6, fronts=(Front("drawer", 0.2), Front("door-left", 0.5), Front("flap")))
    it = Item(id="T.base-cabinet-kitchen-1", type="base-cabinet", room="kitchen", size=(0.6, 0.6, 0.9), position=(0, 0),
              storage=Storage(modules=(m,), door_handles=False))
    shades = {mp.name.split("-", 1)[1].rstrip("-0123456789"): [p.shade for p in mp.parts]
              for mp in storage_layout(it).fronts}
    assert "handle" in shades["drawer"]
    assert "handle" not in shades["door-left"] and "handle" not in shades["flap"]


def test_room_paint_round_trips_and_validates(apt, tmp_path):
    v = Variant(key="T", name="t", rooms={"living": RoomFinish(paint="#dfe3d4")})
    (tmp_path / "T.toml").write_text(variant_to_toml(v))
    assert load_variants(tmp_path)[0].rooms == v.rooms
    bad = Variant(key="T", name="t", rooms={"living": RoomFinish(paint="sage")})
    assert any(i.code == "finish" for i in validate_variants(apt, [bad]))



def test_style_of_must_name_a_layout_variant(apt):
    a = Variant(key="A", name="a")
    style = Variant(key="S", name="s", style_of="A")
    assert not [i for i in validate_variants(apt, [a, style]) if i.code == "variant_style"]
    nested = Variant(key="T", name="t", style_of="S")
    missing = Variant(key="U", name="u", style_of="ZZ")
    assert len([i for i in validate_variants(apt, [a, style, nested, missing]) if i.code == "variant_style"]) == 2


def test_metal_round_trips_and_validates(apt, tmp_path):
    it = Item(id="T.vessel-sink-bathroom-1-1", type="vessel-sink", room="bath_1", size=(0.42, 0.42, 0.15),
              position=(1.0, 1.0), metal="#2b2b2b")
    (tmp_path / "T.toml").write_text(variant_to_toml(Variant(key="T", name="t", items=[it])))
    assert load_variants(tmp_path)[0].items[0].metal == "#2b2b2b"
    bad = Variant(key="T", name="t", items=[replace(it, metal="black")])
    assert any("metal" in i.message for i in validate_variants(apt, [bad]))


def test_variant_own_finishes_round_trip_and_merge(tmp_path):
    from apartment_core.model import parse_finish

    apt = load()
    f = parse_finish("t_terrazzo", {"kind": "tiles", "size": [0.6, 0.6], "color": "#eeeeee"})
    v = Variant(key="T", name="t", finishes={"t_terrazzo": f}, rooms={"hall": RoomFinish(floor="t_terrazzo")})
    (tmp_path / "T.toml").write_text(variant_to_toml(v))
    back = load_variants(tmp_path)[0]
    assert back.finishes == v.finishes
    assert not [i for i in validate_variants(apt, [back]) if i.level == "error"]
    bad = Variant(key="T", name="t", finishes={"terrazzo": f})
    assert any(i.code == "finish" for i in validate_variants(load(), [bad]))


def test_colour_paths_get_and_set():
    from apartment_core.furniture import get_color, set_color

    v = next(v for v in load_variants() if v.key == "V1")
    set_color(v, "plush-corner-sofa-living-1/color", "#123456")
    set_color(v, "rooms.living/floor_color", "#abcdef")
    assert get_color(v, "plush-corner-sofa-living-1/color") == "#123456"
    assert get_color(v, "rooms.living/floor_color") == "#abcdef"
    assert v.owner_colors == ["plush-corner-sofa-living-1/color", "rooms.living/floor_color"]
