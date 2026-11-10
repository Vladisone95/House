"""When does the most daylight enter the apartment? Drives the add-on's "Well lit" button."""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta

from .model import Apartment
from .solar import sun_position_local

BEST_DAY = (6, 21)  # summer solstice: highest, longest sun


def facade_windows(apt: Apartment) -> list[tuple[float, float]]:
    """(compass bearing the glass faces, glazed area m2) for every window / balcony door in an exterior wall."""
    xs = [p[0] for r in apt.rooms for p in r.polygon]
    ys = [p[1] for r in apt.rooms for p in r.polygon]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    out = []
    for o in apt.openings:
        if o.kind not in ("window", "balcony_door"):
            continue
        w = apt.wall(o.wall)
        x1, y1, x2, y2 = w.rect
        if w.horizontal:  # faces +Y or -Y
            turn = 0.0 if (y1 + y2) / 2 > cy else 180.0
        else:  # faces +X (90 deg clockwise of +Y) or -X
            turn = 90.0 if (x1 + x2) / 2 > cx else -90.0
        out.append(((apt.site.plus_y_bearing + turn) % 360.0, o.width * (o.head - o.sill)))
    return out


def daylight_score(azimuth: float, elevation: float, windows: list[tuple[float, float]]) -> float:
    """Relative daylight through vertical glazing: direct sun (cosine of incidence) + a sky share."""
    if elevation <= 0:
        return 0.0
    el = math.radians(elevation)
    direct = sum(a * max(0.0, math.cos(el) * math.cos(math.radians(azimuth - b))) for b, a in windows)
    sky = 0.35 * math.sin(el) * sum(a for _, a in windows)
    return direct + sky


def brightest_time(apt: Apartment, year: int, step_minutes: int = 10) -> datetime:
    """Local time on the summer solstice when the most daylight comes in (sun + sky through all windows)."""
    windows = facade_windows(apt)
    day = date(year, *BEST_DAY)
    best, best_t = -1.0, datetime(year, *BEST_DAY, 12, 0)
    t = datetime.combine(day, datetime.min.time()) + timedelta(hours=5)
    while t.hour < 22:
        s = apt.site
        pos = sun_position_local(t, s.latitude, s.longitude, s.utc_offset_standard)
        score = daylight_score(pos.azimuth, pos.elevation, windows)
        if score > best:
            best, best_t = score, t
        t += timedelta(minutes=step_minutes)
    return best_t
