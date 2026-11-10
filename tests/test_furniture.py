from dataclasses import replace
from pathlib import Path

import pytest

from apartment_core import load
from apartment_core.furniture import (
    SHADES,
    Part,
    Variant,
    copy_variant,
    find_item,
    item_parts,
    load_variant,
    load_variants,
    next_id,
    validate_variants,
    variant_to_toml,
)
from apartment_core.geometry import convex_overlap, polygon_inside, rotated_rect

FIXTURES = Path(__file__).parent / "fixtures" / "variants"


@pytest.fixture(scope="module")
def apt():
    return load()


@pytest.fixture
def variants():
    return load_variants(FIXTURES)


def codes(apt, variants, level=None, unused=False):
    """Issue codes; 'fixed_point_unused' (the small fixtures have no sinks / WCs) only if asked."""
    return [i.code for i in validate_variants(apt, variants)
            if (level is None or i.level == level) and (unused or i.code != "fixed_point_unused")]


def add(variants, key, item):
    next(v for v in variants if v.key == key).items.append(item)
    return variants


def sofa(variants):
    return variants[0].item("sofa-living-1")


# --------------------------------------------------------------------------- loading / ids
def test_fixture_variants_load_and_are_clean(apt, variants):
    assert [v.key for v in variants] == ["A", "B", "C"]
    assert variants[2].style_of == "A" and not variants[0].style_of  # C = a colour style of layout A
    assert len(variants[0].items) == 4
    assert codes(apt, variants) == []


def test_real_variants_have_no_errors(apt):
    errors = [i for i in validate_variants(apt, load_variants()) if i.level == "error"]
    assert not errors, "\n".join(map(str, errors))


def test_item_exposes_variant_and_local_id(variants):
    it = sofa(variants)
    assert (it.variant, it.local_id) == ("A", "sofa-living-1")
    assert variants[0].item("A.sofa-living-1") is it


def test_find_item_accepts_short_id_in_active_variant(variants):
    assert find_item(variants, "corner-sofa-living-1", active="B").id == "B.corner-sofa-living-1"
    assert find_item(variants, "A.bed-master-suite-1").room == "bedroom_2"
    with pytest.raises(KeyError):
        find_item(variants, "sofa-living-9", active="A")


def test_next_id_picks_first_free_index(variants):
    assert next_id(variants[0], "sofa", "living") == "A.sofa-living-2"
    assert next_id(variants[0], "armchair", "living") == "A.armchair-living-1"


def test_id_reused_in_another_variant_is_an_error(apt, variants):
    variants[1].items[0] = sofa(variants)  # B now holds 'A.sofa-living-1': wrong prefix + duplicate
    assert codes(apt, variants, "error").count("furniture_id") == 2


@pytest.mark.parametrize("bad", ["A.Sofa-living-1", "A.sofa_living_1", "A.sofa-living", "sofa-living-1"])
def test_malformed_ids_are_errors(apt, variants, bad):
    variants[0].items[0] = replace(sofa(variants), id=bad)
    assert "furniture_id" in codes(apt, variants, "error")


def test_id_that_no_longer_matches_its_room_is_a_warning(apt, variants):
    variants[0].items[0] = replace(sofa(variants), id="A.sofa-kitchen-1")
    assert codes(apt, variants) == ["furniture_id_name"]


def test_unknown_room_bad_color_and_too_tall_are_errors(apt, variants):
    items = variants[0].items
    items[0] = replace(items[0], room="garage")
    items[1] = replace(items[1], color="red")
    items[2] = replace(items[2], size=(1.6, 2.1, 3.0))
    assert sorted(codes(apt, variants, "error")) == ["furniture_color", "furniture_room", "furniture_size"]


def test_bad_variant_key_is_an_error(apt):
    assert "variant_key" in codes(apt, [Variant(key="a1", name="x")])


# --------------------------------------------------------------------------- placement checks
def test_piece_outside_its_room_is_a_warning(apt, variants):
    variants[0].items[0] = replace(sofa(variants), position=(3.6, 6.6))  # crosses the living/kitchen wall
    assert "furniture_outside" in codes(apt, variants, "warning")


def test_overlapping_pieces_warn_but_stacked_pieces_do_not(apt, variants):
    chair = replace(sofa(variants), id="A.chair-living-1", type="chair", size=(0.5, 0.5, 0.9))
    assert "furniture_overlap" in codes(apt, add(variants, "A", chair), "warning")
    variants[0].items[-1] = replace(chair, id="A.shelf-living-1", type="shelf", elevation=1.2, size=(0.5, 0.3, 0.6))
    assert codes(apt, variants) == []  # shelf hangs above the sofa


def test_rug_under_furniture_is_fine(apt, variants):
    rug = replace(sofa(variants), id="A.rug-living-1", type="rug", size=(3.0, 2.0, 0.01), position=(3.6, 8.0))
    assert codes(apt, add(variants, "A", rug)) == []


def test_piece_in_door_swing_is_a_warning(apt, variants):
    # the kitchen door opens into the kitchen, hinge at y=5.315: sweeps x 3.90-4.70, y 4.515-5.315
    box = replace(sofa(variants), id="A.cabinet-kitchen-1", type="cabinet", room="kitchen",
                  size=(0.5, 0.5, 0.9), position=(4.4, 4.9))
    assert "furniture_door" in codes(apt, add(variants, "A", box), "warning")


# --------------------------------------------------------------------------- copy / round trip
def test_copy_variant_rekeys_every_id(variants):
    c = copy_variant(variants[0], "C", "Scandi")
    assert [it.id for it in c.items] == [f"C.{it.local_id}" for it in variants[0].items]
    assert (c.based_on, c.wall_color, c.name) == ("A", "#e8e4dc", "Scandi")


def test_toml_round_trip(tmp_path, variants):
    c = copy_variant(variants[0], "C")
    p = tmp_path / "C.toml"
    p.write_text(variant_to_toml(c), encoding="utf-8")
    back = load_variant(p)
    assert back.items == c.items
    assert (back.key, back.name, back.based_on, back.wall_color) == ("C", c.name, "A", c.wall_color)


# --------------------------------------------------------------------------- geometry / shapes
def test_rotated_rect_quarter_turn_swaps_extents():
    pts = rotated_rect((0, 0), 2.0, 1.0, 90)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    assert max(xs) - min(xs) == pytest.approx(1.0)
    assert max(ys) - min(ys) == pytest.approx(2.0)


def test_convex_overlap_ignores_touching_edges():
    a = rotated_rect((0, 0), 1, 1, 0)
    assert not convex_overlap(a, rotated_rect((1, 0), 1, 1, 0))
    assert convex_overlap(a, rotated_rect((0.9, 0), 1, 1, 45))


def test_polygon_inside_l_shaped_room(apt):
    room = apt.room("bedroom_2").polygon  # L-shape, bath 2 notch at x > 4.114, y < 2.175
    assert polygon_inside(rotated_rect((2.0, 2.0), 1.0, 1.0, 0), room)
    assert not polygon_inside(rotated_rect((4.3, 1.9), 1.0, 1.0, 0), room)


SHAPED = ["bed", "sofa", "corner-sofa", "dining-table", "round-coffee-table", "chair", "rug", "wardrobe", "toilet",
          "bathtub", "shower", "sink", "double-sink", "washing-machine", "fridge", "oven", "cooktop", "cooker-hood",
          "tv", "slat-panel", "plant", "mirror", "ceiling-light", "pendant-light", "floor-lamp", "wall-spotlight",
          "led-strip", "ring-pendant-light", "ring-ceiling-light", "linear-pendant-light", "recessed-spotlight", "led-panel-light"]


@pytest.mark.parametrize("type_", SHAPED)
@pytest.mark.parametrize("mirror", [False, True])
def test_parts_stay_inside_the_bounding_box(type_, mirror):
    w, d, h = 1.6, 0.9, 0.95
    parts = item_parts(type_, w, d, h, mirror=mirror)
    assert parts
    for p in parts:
        x1, y1, z1, x2, y2, z2 = p.box
        assert -w / 2 - 1e-9 <= x1 < x2 <= w / 2 + 1e-9
        assert -d / 2 - 1e-9 <= y1 < y2 <= d / 2 + 1e-9
        assert 0 <= z1 < z2 <= h + 0.2  # taps may rise above a basin's rim
        assert p.shade in SHADES and p.shape in ("box", "cyl", "ycyl", "xcyl")


def test_unknown_type_is_a_single_box():
    assert item_parts("bean-bag", 0.3, 0.3, 0.6) == [Part((-0.15, -0.15, 0, 0.15, 0.15, 0.6), "main")]


def test_mirror_moves_the_corner_sofa_chaise_to_the_other_side():
    left = item_parts("corner-sofa", 2.6, 1.6, 0.8)
    right = item_parts("corner-sofa", 2.6, 1.6, 0.8, mirror=True)
    chaise = lambda parts: max(parts, key=lambda p: p.box[4]).box  # noqa: E731 - reaches furthest forward
    assert chaise(left)[0] < 0 < chaise(right)[3]
