from datetime import date, datetime

import pytest

from apartment_core.solar import direction_in_plan, eu_utc_offset, sun_events, sun_position_local

LAT, LON, TZ = 44.365, 26.124, 2.0


def test_summer_time_rules_romania():
    assert eu_utc_offset(datetime(2026, 1, 15, 12), TZ) == 2
    assert eu_utc_offset(datetime(2026, 7, 15, 12), TZ) == 3
    # 2026: summer time from Sun 29 March 04:00 local (01:00 UTC) to Sun 25 October 04:00 local
    assert eu_utc_offset(datetime(2026, 3, 29, 2, 30), TZ) == 2
    assert eu_utc_offset(datetime(2026, 3, 29, 5, 0), TZ) == 3
    assert eu_utc_offset(datetime(2026, 10, 25, 5, 0), TZ) == 2


@pytest.mark.parametrize(
    "day,expected_noon_elevation",
    [
        (date(2026, 6, 21), 90 - LAT + 23.44),  # summer solstice
        (date(2026, 12, 21), 90 - LAT - 23.44),  # winter solstice
        (date(2026, 3, 20), 90 - LAT),  # equinox
    ],
)
def test_noon_elevation(day, expected_noon_elevation):
    ev = sun_events(day, LAT, LON, TZ)
    pos = sun_position_local(ev["solar_noon"], LAT, LON, TZ)
    assert pos.elevation == pytest.approx(expected_noon_elevation, abs=0.6)
    assert pos.azimuth == pytest.approx(180, abs=1.0)


def test_solar_noon_time_bucharest_june():
    # lon 26.124 E -> 10:15 UTC mean noon, EoT ~ -1.8 min -> ~13:17 EEST
    ev = sun_events(date(2026, 6, 21), LAT, LON, TZ)
    minutes = ev["solar_noon"].hour * 60 + ev["solar_noon"].minute
    assert minutes == pytest.approx(13 * 60 + 17, abs=3)


def test_sunrise_sunset_june_bucharest():
    ev = sun_events(date(2026, 6, 21), LAT, LON, TZ)
    # published values for Bucharest ~05:31 / 21:02 EEST
    assert ev["sunrise"].hour * 60 + ev["sunrise"].minute == pytest.approx(5 * 60 + 31, abs=6)
    assert ev["sunset"].hour * 60 + ev["sunset"].minute == pytest.approx(21 * 60 + 2, abs=6)


def test_direction_in_plan_axes():
    pos = sun_position_local(datetime(2026, 6, 21, 13, 17), LAT, LON, TZ)
    # sun due south; facade B normal is plus_y_bearing - 90 = 204 deg -> mostly -X
    d = direction_in_plan(pos, 294.0)
    assert d[0] < -0.2 and d[2] > 0.9
    assert sum(v * v for v in d) == pytest.approx(1.0)
