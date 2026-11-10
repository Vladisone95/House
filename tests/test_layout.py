import pytest

from apartment_core import load
from apartment_core.geometry import door_swing, polygon_area, rect_area, wall_boxes
from apartment_core.validate import room_areas, validate


@pytest.fixture(scope="module")
def apt():
    return load()


def test_model_has_no_validation_errors(apt):
    errors = [i for i in validate(apt) if i.level == "error"]
    assert not errors, "\n".join(map(str, errors))


@pytest.mark.parametrize(
    "room_id,listed",
    [("living", 26.52), ("kitchen", 11.46), ("bedroom_1", 14.01), ("bath_1", 4.61), ("hall", 7.47),
     ("bedroom_2", 13.53 + 3.78), ("bath_2", 4.61), ("balcony", 6.76)],
)
def test_room_areas_match_sales_sheet(apt, room_id, listed):
    assert room_areas(apt)[room_id] == pytest.approx(listed, rel=apt.area_tolerance)


def test_usable_area_matches_listing(apt):
    usable = sum(room_areas(apt)[r.id] for r in apt.rooms)
    assert usable == pytest.approx(85.99, rel=0.01)


def test_developer_plan_sizes_include_about_one_wall(apt):
    """docs/uploads/dimensiuni.jpeg prints sizes ~one wall thickness bigger than the clear room (owner 2026-10-06)."""
    def box(room_id):
        xs, ys = zip(*apt.room(room_id).polygon, strict=True)
        return max(xs) - min(xs), max(ys) - min(ys)

    printed = {"kitchen": (4.57, 2.63), "bath_1": (1.85, 2.80), "bath_2": (2.80, 1.85), "balcony": (1.90, 4.10)}
    for room_id, sizes in printed.items():
        for clear, label in zip(box(room_id), sizes, strict=True):
            assert 0.0 <= label - clear <= 0.20, (room_id, clear, label)
    # baths: printed size minus 12.5 cm each way = the listed 4.61 (owner's check)
    assert box("bath_1") == pytest.approx((1.85 - 0.125, 2.80 - 0.125), abs=0.006)
    assert box("bath_2") == pytest.approx((2.80 - 0.125, 1.85 - 0.125), abs=0.001)


def test_owner_confirmed_dimensions(apt):
    assert apt.levels.ceiling_height == 2.70
    assert apt.wall_types["exterior"] == 0.45
    assert apt.wall_types["partition"] == 0.125
    assert apt.wall_types["party"] == 0.25
    # bath walls towards the bedrooms: 1.725 m (developer plan 1.85 minus 12.5 cm, owner 2026-10-06; was 1.80)
    assert apt.wall("part_bath2_left").axis_range[1] - apt.wall("part_bath2_left").axis_range[0] == pytest.approx(1.725)
    lo, hi = apt.wall("part_bed1_bath1").axis_range
    assert hi - lo == pytest.approx(1.725)
    # kitchen door: 60 cm between door and the kitchen's bottom wall (left when entering)
    kitchen_bottom = min(p[1] for p in apt.room("kitchen").polygon)
    door = next(o for o in apt.openings if o.id == "D_kitchen")
    assert door.span[0] - kitchen_bottom == pytest.approx(0.60, abs=0.001)


def test_balcony_is_a_half_recessed_loggia_along_the_living_room(apt):
    # developer plan 2026-10-06: from the facade-A wall to the end of the kitchen wall, inside the step of facade B
    bal_y = sorted({p[1] for p in apt.balcony.polygon})
    assert bal_y[1] == max(p[1] for p in apt.room("living").polygon)
    assert bal_y[0] == apt.wall("ext_facade_b").rect[3]
    assert max(p[0] for p in apt.balcony.polygon) == apt.wall("ext_facade_b_living").rect[0]


def test_room_polygons_are_ccw(apt):
    for r in apt.all_rooms():
        assert polygon_area(r.polygon) > 0, r.id


def test_wall_boxes_preserve_volume():
    rect = (0.0, 0.0, 4.0, 0.45)
    h = 2.7
    ops = [(1.0, 2.0, 0.9, 2.4)]
    boxes = wall_boxes(rect, True, h, ops)
    vol = sum((b[3] - b[0]) * (b[4] - b[1]) * (b[5] - b[2]) for b in boxes)
    expected = rect_area(rect) * h - 1.0 * 0.45 * (2.4 - 0.9)
    assert vol == pytest.approx(expected)


def test_footprint_has_no_gaps_inside_walls(apt):
    cells = apt.footprint_cells()
    total = sum(rect_area(c) for c in cells)
    walls = sum(rect_area(w.rect) for w in apt.walls)
    rooms = sum(room_areas(apt)[r.id] for r in apt.rooms)
    assert total == pytest.approx(walls + rooms, rel=1e-6)


def test_door_swing_horizontal_wall_opens_to_plus_side():
    # 0.8 m door in a wall y 1.0-1.1, hinge at x=2.0, opening towards +Y
    leaf, arc = door_swing((0.0, 1.0, 5.0, 1.1), True, (2.0, 2.8), "start", "+")
    assert leaf == [(2.0, 1.1), pytest.approx((2.0, 1.9))]
    assert arc[0] == pytest.approx((2.0, 1.9))  # open tip
    assert arc[-1] == pytest.approx((2.8, 1.1))  # closed latch point on the wall face
    assert all(((x - 2.0) ** 2 + (y - 1.1) ** 2) ** 0.5 == pytest.approx(0.8) for x, y in arc)


def test_door_swing_vertical_wall_hinge_end_opens_to_minus_side():
    leaf, arc = door_swing((3.0, 0.0, 3.125, 6.0), False, (4.0, 4.7), "end", "-")
    assert leaf == [(3.0, 4.7), pytest.approx((2.3, 4.7))]
    assert arc[-1] == pytest.approx((3.0, 4.0))


def test_doors_have_valid_swing_and_windows_none(apt):
    for o in apt.openings:
        if o.kind == "door":
            assert o.hinge in ("start", "end") and o.swing in ("+", "-"), o.id
        else:
            assert not o.hinge and not o.swing, o.id

