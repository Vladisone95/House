"""'Well lit' daylight time, floor finishes and LED light defaults (ADR 0007)."""

from dataclasses import replace

import pytest

from apartment_core import load
from apartment_core.daylight import brightest_time, daylight_score, facade_windows
from apartment_core.furniture import Item, default_light, light_of, light_source_z
from apartment_core.validate import validate


@pytest.fixture(scope="module")
def apt():
    return load()


def test_facade_windows_face_the_two_facades(apt):
    bearings = {round(b) for b, _ in facade_windows(apt)}
    assert bearings == {294, 204}  # facade A WNW, facade B SSW
    assert all(a > 1.0 for _, a in facade_windows(apt))


def test_no_daylight_at_night_and_more_sun_on_the_glass_scores_higher():
    win = [(204.0, 2.0)]
    assert daylight_score(204, -5, win) == 0
    assert daylight_score(204, 30, win) > daylight_score(110, 30, win)


def test_brightest_summer_time_is_mid_afternoon(apt):
    t = brightest_time(apt, 2026)
    assert (t.month, t.day) == (6, 21)
    assert 14 <= t.hour <= 18  # SSW facade still lit while the WNW facade starts getting sun


def test_finishes_match_the_design(apt):
    wood, tiles = apt.finishes["wood"], apt.finishes["tiles"]
    assert wood.kind == "parquet" and wood.size == (1.2, 0.19)
    assert tiles.kind == "tiles" and tiles.size == (0.6, 0.6)
    assert {r.finish for r in apt.all_rooms()} <= set(apt.finishes)
    assert not [i for i in validate(apt) if i.code == "finish"]


def test_bad_finish_is_an_error(apt):
    bad = replace(apt.finishes["tiles"], kind="carpet")
    apt2 = replace(apt, finishes={**apt.finishes, "tiles": bad})
    assert "finish" in [i.code for i in validate(apt2) if i.level == "error"]


def test_led_strip_defaults_scale_with_length_and_can_aim_up():
    assert default_light("led-strip", (2.0, 0.02, 0.01)).kind == "rect"
    assert default_light("led-strip", (2.0, 0.02, 0.01)).watts == pytest.approx(30.0)
    assert default_light("ring-pendant-light", (1.0, 1.0, 0.7)).kind == "area"
    assert default_light("recessed-spotlight").kind == "spot"
    strip = Item(id="T.led-strip-living-1", type="led-strip", room="living", size=(3.0, 0.02, 0.01),
                 position=(3, 9), elevation=2.6)
    up = replace(strip, light=replace(light_of(strip), aim="up"))
    assert light_source_z(strip) < 0 < light_source_z(up)


def test_only_pendants_cast_shadows_by_default_and_cutoff_is_room_sized():
    from apartment_core.furniture import Light, casts_shadow, light_cutoff

    def it(type_, **kw):
        return Item(id=f"T.{type_}-living-1", type=type_, room="living", size=(0.5, 0.5, 0.5), position=(3, 9), **kw)

    assert casts_shadow(it("ring-pendant-light")) and casts_shadow(it("linear-pendant-light"))
    assert not any(casts_shadow(it(t)) for t in ("led-strip", "recessed-spotlight", "ceiling-light", "table-lamp"))
    assert casts_shadow(it("led-strip", light=Light("rect", 20.0, shadow=True)))  # explicit override wins
    assert all(2.5 <= light_cutoff(it(t)) <= 7.0 for t in ("led-strip", "ring-pendant-light", "recessed-spotlight"))
