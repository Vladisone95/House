"""Sun position - NOAA solar calculator algorithm (accuracy ~0.01 deg for 1800-2100).

Pure Python so it runs both in CPython and inside Blender.
Reference: https://gml.noaa.gov/grad/solcalc/calcdetails.html
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta


@dataclass(frozen=True)
class SunPosition:
    azimuth: float  # degrees clockwise from true north
    elevation: float  # degrees above horizon (refraction corrected)
    utc: datetime
    utc_offset: float  # hours, local = utc + offset

    @property
    def is_up(self) -> bool:
        return self.elevation > -0.833


def _last_sunday(year: int, month: int) -> date:
    d = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)
    return d - timedelta(days=(d.weekday() + 1) % 7)


def eu_utc_offset(local: datetime, standard_offset: float) -> float:
    """UTC offset (h) for a local wall-clock time under EU summer-time rules.

    Summer time: last Sunday of March 01:00 UTC -> last Sunday of October 01:00 UTC.
    """
    start = datetime.combine(_last_sunday(local.year, 3), datetime.min.time()) + timedelta(hours=1)
    end = datetime.combine(_last_sunday(local.year, 10), datetime.min.time()) + timedelta(hours=1)
    utc_if_summer = local - timedelta(hours=standard_offset + 1)
    return standard_offset + 1 if start <= utc_if_summer < end else standard_offset


def _julian_day(utc: datetime) -> float:
    y, m = utc.year, utc.month
    d = utc.day + (utc.hour + utc.minute / 60 + utc.second / 3600) / 24
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def _refraction(elev: float) -> float:
    if elev > 85:
        return 0.0
    te = math.tan(math.radians(elev))
    if elev > 5:
        r = 58.1 / te - 0.07 / te**3 + 0.000086 / te**5
    elif elev > -0.575:
        r = 1735 + elev * (-518.2 + elev * (103.4 + elev * (-12.79 + elev * 0.711)))
    else:
        r = -20.772 / te
    return r / 3600


def sun_position_utc(utc: datetime, lat: float, lon: float, utc_offset: float = 0.0) -> SunPosition:
    jc = (_julian_day(utc) - 2451545.0) / 36525.0
    L0 = (280.46646 + jc * (36000.76983 + jc * 0.0003032)) % 360
    M = 357.52911 + jc * (35999.05029 - 0.0001537 * jc)
    e = 0.016708634 - jc * (0.000042037 + 0.0000001267 * jc)
    Mr = math.radians(M)
    C = math.sin(Mr) * (1.914602 - jc * (0.004817 + 0.000014 * jc)) + math.sin(2 * Mr) * (0.019993 - 0.000101 * jc) + math.sin(3 * Mr) * 0.000289
    omega = math.radians(125.04 - 1934.136 * jc)
    app_long = L0 + C - 0.00569 - 0.00478 * math.sin(omega)
    mean_obliq = 23 + (26 + (21.448 - jc * (46.815 + jc * (0.00059 - jc * 0.001813))) / 60) / 60
    obliq = math.radians(mean_obliq + 0.00256 * math.cos(omega))
    decl = math.asin(math.sin(obliq) * math.sin(math.radians(app_long)))
    y = math.tan(obliq / 2) ** 2
    L0r = math.radians(L0)
    eq_time = 4 * math.degrees(
        y * math.sin(2 * L0r)
        - 2 * e * math.sin(Mr)
        + 4 * e * y * math.sin(Mr) * math.cos(2 * L0r)
        - 0.5 * y * y * math.sin(4 * L0r)
        - 1.25 * e * e * math.sin(2 * Mr)
    )
    minutes = utc.hour * 60 + utc.minute + utc.second / 60
    tst = (minutes + eq_time + 4 * lon) % 1440
    ha = tst / 4 - 180 if tst / 4 >= 0 else tst / 4 + 180
    latr = math.radians(lat)
    cos_zen = math.sin(latr) * math.sin(decl) + math.cos(latr) * math.cos(decl) * math.cos(math.radians(ha))
    zen = math.acos(max(-1.0, min(1.0, cos_zen)))
    elev = 90 - math.degrees(zen)
    denom = math.cos(latr) * math.sin(zen)
    if abs(denom) < 1e-9:
        az = 180.0
    else:
        a = math.degrees(math.acos(max(-1.0, min(1.0, (math.sin(latr) * math.cos(zen) - math.sin(decl)) / denom))))
        az = (a + 180) % 360 if ha > 0 else (540 - a) % 360
    return SunPosition(azimuth=az, elevation=elev + _refraction(elev), utc=utc, utc_offset=utc_offset)


def sun_position_local(local: datetime, lat: float, lon: float, standard_offset: float) -> SunPosition:
    """Sun position for a naive local wall-clock time (EU summer time applied)."""
    off = eu_utc_offset(local, standard_offset)
    utc = (local - timedelta(hours=off)).replace(tzinfo=UTC)
    return sun_position_utc(utc, lat, lon, off)


def direction_in_plan(pos: SunPosition, plus_y_bearing: float) -> tuple[float, float, float]:
    """Unit vector pointing TOWARDS the sun in model coordinates.

    ``plus_y_bearing`` is the compass bearing of the model's +Y axis.
    """
    rel = math.radians(pos.azimuth - plus_y_bearing)
    ce = math.cos(math.radians(pos.elevation))
    return (math.sin(rel) * ce, math.cos(rel) * ce, math.sin(math.radians(pos.elevation)))


def sun_events(day: date, lat: float, lon: float, standard_offset: float) -> dict[str, datetime | None]:
    """Local sunrise, solar noon and sunset (minute resolution)."""

    def elev(minute: int) -> float:
        t = datetime.combine(day, datetime.min.time()) + timedelta(minutes=minute)
        return sun_position_local(t, lat, lon, standard_offset).elevation

    def crossing(lo: int, hi: int) -> datetime:
        rising = elev(hi) > elev(lo)
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if (elev(mid) > -0.833) == rising:
                hi = mid
            else:
                lo = mid
        return datetime.combine(day, datetime.min.time()) + timedelta(minutes=hi)

    samples = list(range(0, 1441, 20))
    vals = [elev(m) for m in samples]
    noon_idx = max(range(len(vals)), key=vals.__getitem__)
    lo, hi = max(samples[noon_idx] - 30, 0), min(samples[noon_idx] + 30, 1440)
    best = max(range(lo, hi + 1), key=elev)
    out: dict[str, datetime | None] = {
        "sunrise": None,
        "solar_noon": datetime.combine(day, datetime.min.time()) + timedelta(minutes=best),
        "sunset": None,
    }
    for a, b, va, vb in zip(samples, samples[1:], vals, vals[1:], strict=False):
        if va <= -0.833 < vb:
            out["sunrise"] = crossing(a, b)
        elif va > -0.833 >= vb:
            out["sunset"] = crossing(a, b)
    return out
