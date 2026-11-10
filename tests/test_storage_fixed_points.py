"""Storage pieces (modules, openable fronts, interior) and fixed service points (ADR 0006)."""

import math
from dataclasses import replace

import pytest

from apartment_core import load
from apartment_core.furniture import (
    Fitting,
    Front,
    Item,
    Light,
    Module,
    Storage,
    Variant,
    auto_modules,
    find_item,
    is_light,
    light_of,
    light_source_z,
    load_variant,
    load_variants,
    storage_layout,
    validate_variants,
    variant_to_toml,
)
from apartment_core.validate import validate


@pytest.fixture(scope="module")
def apt():
    return load()


def issues(apt, *items, key="T"):
    return validate_variants(apt, [Variant(key=key, name="test", items=list(items))])


def codes(apt, *items):
    return [i.code for i in issues(apt, *items)]


def sink(**kw):
    base = dict(id="T.sink-kitchen-1", type="sink", room="kitchen", size=(0.8, 0.5, 0.04),
                position=(3.55, 6.33), rotation=180, elevation=0.9)
    return Item(**{**base, **kw})


def wardrobe(storage=None, **kw):
    base = dict(id="T.wardrobe-master-suite-1", type="wardrobe", room="bedroom_2", size=(1.8, 0.6, 2.4),
                position=(2.0, 3.4), rotation=180, storage=storage)
    return Item(**{**base, **kw})


# --------------------------------------------------------------------------- fixed points
def test_fixed_points_load_and_the_shell_is_valid(apt):
    ids = {f.id for f in apt.fixed_points}
    assert {"FX_kitchen_sink", "FX_kitchen_hood", "FX_bath1_washer", "FX_bath1_wc", "FX_bath2_wc"} <= ids
    assert not [i for i in validate(apt) if i.code == "fixed_point"]
    assert next(o for o in apt.openings if o.id == "D_entrance").fixed


def test_fixed_point_outside_its_room_is_an_error(apt):
    apt2 = replace(apt, fixed_points=[replace(apt.fixed_points[0], position=(9.0, 9.0))])
    assert "fixed_point" in [i.code for i in validate(apt2)]


def test_sink_on_the_water_point_is_fine(apt):
    assert "fixed_point" not in codes(apt, sink())


def test_sink_away_from_the_water_point_is_an_error(apt):
    msg = [i for i in issues(apt, sink(position=(1.6, 6.33))) if i.code == "fixed_point"]
    assert msg and msg[0].level == "error" and "FX_kitchen_sink" in msg[0].message


def test_any_sink_type_is_bound_by_the_pipes(apt):
    vessel = sink(id="T.vessel-sink-kitchen-1", type="vessel-sink", position=(1.6, 6.33))
    assert "fixed_point" in codes(apt, vessel)


def test_toilet_in_the_wrong_corner_is_an_error(apt):
    wc = Item(id="T.toilet-bathroom-1-1", type="toilet", room="bath_1", size=(0.38, 0.55, 1.1),
              position=(8.7, 6.7), rotation=180)
    assert "fixed_point" in codes(apt, wc)


def test_unused_fixed_points_warn_only_in_non_empty_variants(apt):
    assert issues(apt) == []  # an empty variant is not nagged
    unused = [i for i in issues(apt, sink()) if i.code == "fixed_point_unused"]
    assert unused and all(i.level == "warning" for i in unused)
    assert not any("FX_kitchen_sink" in i.message for i in unused)


def test_developer_variant_respects_every_fixed_point(apt):
    dev = [v for v in load_variants() if v.key == "DEV"]
    assert dev, "data/variants/DEV.toml missing"
    found = validate_variants(apt, dev)
    assert not [i for i in found if i.level == "error"], "\n".join(map(str, found))
    assert not [i for i in found if i.code == "fixed_point_unused"]


# --------------------------------------------------------------------------- storage modules
def test_auto_modules_doors_up_to_60cm_and_drawers_for_nightstands():
    mods = auto_modules("wardrobe", 1.8, 2.4)
    assert [round(m.width, 3) for m in mods] == [0.6, 0.6, 0.6]
    assert [m.fronts[0].kind for m in mods] == ["door-left", "door-right", "door-left"]
    (ns,) = auto_modules("nightstand", 0.45, 0.5)
    assert ns.fronts[0].kind == "drawers" and ns.fronts[0].count == 2


def test_modules_run_from_the_viewers_left():
    lay = storage_layout(wardrobe())
    (a0, a1), (b0, b1), (c0, c1) = lay.modules
    assert a1 == pytest.approx(0.9) and a0 > b0 > c0  # m1 at local +x (viewer faces -y)


def test_door_hinges_and_opening_direction():
    st = Storage(modules=(Module(0.6, (Front("door-left"),)), Module(0.6, (Front("door-right"),)),
                          Module(0.6, (Front("doors"),))))
    fronts = {f.name: f for f in storage_layout(wardrobe(st)).fronts}
    left, right = fronts["m1-door-left-1"], fronts["m2-door-right-1"]
    assert left.pivot[0] > right.pivot[0]
    assert left.amount < 0 < right.amount  # both swing towards the viewer (+y)
    assert {"m3-door-left-1", "m3-door-right-1"} <= set(fronts)
    # an opened door's free edge ends up in front of the piece
    for f in (left, right):
        x_far = max((b for p in f.parts for b in (p.box[0], p.box[3])), key=abs)
        assert x_far * math.sin(f.amount) > 0.3  # rotated free edge: y > 0


def test_drawers_slide_out_and_stack():
    st = Storage(modules=(Module(0.8, (Front("drawer", 0.2), Front("drawers", None, 3))),))
    item = Item(id="T.dresser-master-suite-1", type="dresser", room="bedroom_2", size=(0.8, 0.5, 0.9),
                position=(2.0, 3.4), storage=st)
    fronts = storage_layout(item).fronts
    assert [f.name for f in fronts] == [f"m1-drawer-{i}" for i in range(1, 5)]
    assert all(f.motion == "slide" and f.amount > 0.2 for f in fronts)
    tops = [max(p.box[5] for p in f.parts) for f in fronts]
    assert tops == sorted(tops, reverse=True)  # listed top -> bottom


def test_interior_fittings_are_named_per_module():
    st = Storage(modules=(Module(0.9, (Front("doors"),), interior=(Fitting("shelf", 1.6), Fitting("rail", 1.8),
                                                                   Fitting("shelf", 0.4))),
                          Module(0.9, (Front("doors"),))))
    names = [n for n, _, _ in storage_layout(wardrobe(st)).interior]
    assert names == ["m1/rail-1", "m1/shelf-1", "m1/shelf-2"]


def test_storage_errors(apt):
    bad_width = Storage(modules=(Module(0.6),))
    assert "storage" in codes(apt, wardrobe(bad_width))
    bad_front = Storage(modules=(Module(1.8, (Front("trapdoor"),)),))
    assert "storage" in codes(apt, wardrobe(bad_front))
    too_high = Storage(modules=(Module(1.8, interior=(Fitting("shelf", 2.9),)),))
    assert "storage" in codes(apt, wardrobe(too_high))
    not_storage = Item(id="T.sofa-living-1", type="sofa", room="living", size=(2, 0.9, 0.8), position=(3, 9),
                       storage=Storage())
    assert "storage" in codes(apt, not_storage)


def test_storage_round_trips_through_toml(tmp_path):
    st = Storage(modules=(Module(1.0, (Front("doors"),), "glass", "#906c43", (Fitting("rail", 1.8),), "hall end"),
                          Module(0.8, (Front("drawer", 0.2), Front("drawers", None, 2)),
                                 interior=(Fitting("divider", x=0.4), Fitting("drawer", 0.1, 0.18)))),
                 plinth=0.1, handle_color="#c8a165", interior_color="#ffffff")
    v = Variant(key="T", name="t", items=[wardrobe(st, id="T.wardrobe-master-suite-1")])
    p = tmp_path / "T.toml"
    p.write_text(variant_to_toml(v), encoding="utf-8")
    assert load_variant(p).items == v.items


def test_find_item_accepts_a_part_path():
    v = Variant(key="T", name="t", items=[wardrobe()])
    assert find_item([v], "T.wardrobe-master-suite-1/m2/shelf-1").id == "T.wardrobe-master-suite-1"
    assert find_item([v], "wardrobe-master-suite-1/m2", active="T").id == "T.wardrobe-master-suite-1"


# --------------------------------------------------------------------------- light fixtures
def lamp(**kw):
    base = dict(id="T.ceiling-light-living-1", type="ceiling-light", room="living", size=(0.35, 0.35, 0.06),
                position=(3.0, 9.0), elevation=2.64)
    return Item(**{**base, **kw})


def test_light_fixtures_get_a_default_light_per_type():
    assert light_of(lamp()).kind == "area"
    assert light_of(lamp(type="pendant-light")).kind == "point"
    assert light_of(lamp(type="wall-spotlight")).kind == "spot"
    assert is_light("floor-lamp") and not is_light("lamp-shade-box")


def test_light_source_sits_below_the_fixture():
    assert light_source_z(lamp()) < 0  # never inside the fixture's own body
    floor = lamp(type="floor-lamp", size=(0.4, 0.4, 1.6), elevation=0.0)
    assert 0 < light_source_z(floor) < 1.6


def test_ceiling_lights_do_not_count_as_overlapping_furniture(apt):
    sofa = Item(id="T.sofa-living-1", type="sofa", room="living", size=(2.2, 0.9, 0.8), position=(3.0, 9.0))
    assert "furniture_overlap" not in codes(apt, sofa, lamp())


def test_light_errors_and_round_trip(apt, tmp_path):
    assert "light" in codes(apt, lamp(light=Light("laser", 10.0)))
    assert "light" in codes(apt, lamp(id="T.sofa-living-1", type="sofa", light=Light()))
    v = Variant(key="T", name="t", items=[lamp(light=Light("spot", 15.0, "#fff4e0", 0.05, 40.0))])
    p = tmp_path / "T.toml"
    p.write_text(variant_to_toml(v), encoding="utf-8")
    assert load_variant(p).items == v.items
