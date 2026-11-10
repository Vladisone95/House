"""Shape library - extra furniture shapes (pure Python), looked up by ``furniture.item_parts`` first.

Every function returns ``Part`` lists in the piece's local frame (origin = footprint centre on the underside,
front = +y, back / wall = -y, w along x, d along y, h up), inside the footprint unless its docstring says
otherwise. Recolourable built-in colours: ``BRASS`` (-> item ``metal``), ``ACCENTS`` (-> ``accent``: wooden
legs / frames / bodies), ``CUSHIONS`` (-> ``cushion``: throw pillows, towels, changing mats, bins). Everything
else takes the piece colour (``color``) or a shade derived from it (soft = lighter, dark = darker).

Faces of different parts that could be seen together are kept >= 1 mm apart (no z-fighting / flicker).
"""

from __future__ import annotations

import math
from collections.abc import Callable

from .furniture import ACCENTS, BRASS, CUSHIONS, WARM_WHITE, Part, _box

WOOD, PILLOW, LIGHT_TONE, DARK_TONE = ACCENTS[0], CUSHIONS[0], CUSHIONS[1], CUSHIONS[2]


# --------------------------------------------------------------------------- helpers
def _sphere(cx: float, cy: float, cz: float, r: float, shade: str, color: str = "", n: int = 12) -> list[Part]:
    """Ball from stacked discs (centre cx, cy, cz)."""
    parts = []
    for i in range(n):
        za, zb = cz - r + 2 * r * i / n, cz - r + 2 * r * (i + 1) / n
        rr = max(math.sqrt(max(r * r - ((za + zb) / 2 - cz) ** 2, 0.0)), r * 0.2)
        parts.append(Part(_box(cx - rr, cy - rr, za, cx + rr, cy + rr, zb), shade, "cyl", color))
    return parts


def _dome(cx: float, cy: float, z0: float, r: float, h: float, shade: str, color: str = "", n: int = 8) -> list[Part]:
    """Half-ellipsoid shade: widest (r) at z0, closing at z0 + h."""
    parts = []
    for i in range(n):
        za, zb = z0 + h * i / n, z0 + h * (i + 1) / n
        rr = r * max(math.sqrt(max(1 - (i / n) ** 2, 0.0)), 0.15)
        parts.append(Part(_box(cx - rr, cy - rr, za, cx + rr, cy + rr, zb), shade, "cyl", color))
    return parts


def _arch(w: float, h: float, y1: float, y2: float, shade: str, color: str = "", z0: float = 0.0,
          n: int = 40) -> list[Part]:
    """Upright arch in the x-z plane (flat bottom at z0, round top), w wide, h tall, between y1 and y2."""
    r = w / 2
    zc = z0 + max(h - r, 0.0)  # centre of the round top
    parts = [Part(_box(-r, y1, z0, r, y2, zc), shade, color=color)] if zc > z0 else []
    top = z0 + h
    for i in range(n):
        za, zb = zc + (top - zc) * i / n, zc + (top - zc) * (i + 1) / n
        half = math.sqrt(max(r * r - ((za + zb) / 2 - zc) ** 2 * (r / max(top - zc, 1e-6)) ** 2, 0.0))
        parts.append(Part(_box(-half, y1, za, half, y2, zb), shade, color=color))
    return parts


def _path(points: list[tuple[float, float, float]], tube: float, shade: str, color: str = "") -> list[Part]:
    """A bent rod through 3D points: one box per segment, each enclosing its segment (arcs, leaning legs)."""
    parts = []
    for (x1, y1, z1), (x2, y2, z2) in zip(points, points[1:], strict=False):
        t = tube / 2
        parts.append(Part(_box(min(x1, x2) - t, min(y1, y2) - t, min(z1, z2) - t, max(x1, x2) + t, max(y1, y2) + t,
                               max(z1, z2) + t), shade, color=color))
    return parts


def _line(a: tuple[float, float, float], b: tuple[float, float, float], n: int) -> list[tuple[float, float, float]]:
    return [tuple(a[k] + (b[k] - a[k]) * i / n for k in range(3)) for i in range(n + 1)]


def _taper_leg(x: float, y: float, z0: float, z1: float, r_top: float, r_foot: float, color: str = WOOD,
               n: int = 4) -> list[Part]:
    """Tapered round leg from the floor (r_foot) up to its top (r_top)."""
    parts = []
    for i in range(n):
        za, zb = z0 + (z1 - z0) * i / n, z0 + (z1 - z0) * (i + 1) / n
        r = r_foot + (r_top - r_foot) * (i + 0.5) / n
        parts.append(Part(_box(x - r, y - r, za, x + r, y + r, zb), "main", "cyl", color))
    return parts


def _frame(x1: float, z1: float, x2: float, z2: float, y1: float, y2: float, s: float, shade: str,
           color: str = "") -> list[Part]:
    """Rectangular frame (4 bars of width s) in the x-z plane between y1 and y2."""
    return [Part(_box(x1, y1, z2 - s, x2, y2, z2), shade, color=color), Part(_box(x1, y1, z1, x2, y2, z1 + s), shade,
                                                                             color=color),
            Part(_box(x1, y1, z1 + s, x1 + s, y2, z2 - s), shade, color=color),
            Part(_box(x2 - s, y1, z1 + s, x2, y2, z2 - s), shade, color=color)]


def _tap(x: float, y: float, z: float, reach: float) -> list[Part]:
    """Deck-mounted brass mixer at (x, y) on a surface at z: body, spout reaching ``reach`` towards +y, lever."""
    return [Part(_box(x - 0.018, y - 0.018, z, x + 0.018, y + 0.018, z + 0.15), "handle", "cyl", BRASS),
            Part(_box(x - 0.011, y - 0.011, z + 0.125, x + 0.011, y + reach, z + 0.147), "handle", color=BRASS),
            Part(_box(x - 0.006, y - 0.05, z + 0.11, x + 0.006, y - 0.018, z + 0.12), "handle", color=BRASS)]


# --------------------------------------------------------------------------- bathroom
def console_sink(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Wall-hung rectangular ceramic basin (rim at h) on a slim brass frame: two front legs, side rails to the
    wall, a towel bar along the front and a low open wooden shelf. The tap rises above h (like every sink)."""
    hw, hd, top = w / 2, d / 2, h
    deep, lx, ly = 0.14, hw - 0.04, hd - 0.045
    parts = [Part(_box(-hw, -hd, top - deep, hw, hd, top - 0.10), "ceramic"),  # basin floor (10 cm deep bowl)
             Part(_box(-hw, -hd, top - 0.10, hw, -hd + 0.11, top), "ceramic"),  # tap deck at the back
             Part(_box(-hw, hd - 0.03, top - 0.10, hw, hd, top), "ceramic"),
             Part(_box(-hw, -hd + 0.11, top - 0.10, -hw + 0.03, hd - 0.03, top), "ceramic"),
             Part(_box(hw - 0.03, -hd + 0.11, top - 0.10, hw, hd - 0.03, top), "ceramic"),
             Part(_box(-0.025, -0.005, top - 0.102, 0.025, 0.045, top - 0.099), "chrome", "cyl")]  # drain
    for sx in (-1, 1):
        x = sx * lx
        parts += [Part(_box(x - 0.012, ly - 0.012, 0, x + 0.012, ly + 0.012, top - deep), "handle", "cyl", BRASS),
                  Part(_box(x - 0.01, -hd, top - deep - 0.02, x + 0.01, ly - 0.012, top - deep), "handle", color=BRASS),
                  Part(_box(x - 0.01, -hd, 0.14, x + 0.01, ly - 0.012, 0.155), "handle", color=BRASS),  # shelf rail
                  Part(_box(x - 0.008, ly + 0.012, top - 0.25, x + 0.008, hd - 0.004, top - 0.235), "handle",
                       color=BRASS)]  # towel-bar bracket
    parts += [Part(_box(-lx, hd - 0.022, top - 0.252, lx, hd - 0.002, top - 0.232), "handle", "xcyl", BRASS),
              Part(_box(-lx + 0.012, -hd + 0.01, 0.155, lx - 0.012, ly - 0.014, 0.18), "main", color=WOOD)]  # shelf
    return parts + _tap(0.0, -hd + 0.055, top, 0.12)


def integrated_sink(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Wall-hung solid-surface counter (piece colour, top at h, 15 cm thick) with a moulded ramp basin: the floor
    slopes from the front down to a dark slot drain at the back; brass mixer on the back deck."""
    hw, hd, t = w / 2, d / 2, 0.15
    bx = min(0.28, hw - 0.08)  # half the basin width
    yb, yf = -hd + 0.13, hd - 0.05  # basin back (after the deck) / front lip
    parts = [Part(_box(-hw, -hd, h - t, hw, yb, h), "main"), Part(_box(-hw, yf, h - t, hw, hd, h), "main"),
             Part(_box(-hw, yb, h - t, -bx, yf, h), "main"), Part(_box(bx, yb, h - t, hw, yf, h), "main"),
             Part(_box(-bx, yb, h - t, bx, yb + 0.035, h - 0.11), "dark")]  # slot drain
    n = 8
    for k in range(n):  # ramp: shallow at the front (k = 0), deepest at the slot
        y2 = yf - (yf - yb - 0.035) * k / n
        y1 = yf - (yf - yb - 0.035) * (k + 1) / n
        parts.append(Part(_box(-bx, y1, h - t, bx, y2, h - 0.02 - 0.07 * (k + 1) / n), "main"))
    return parts + _tap(0.0, -hd + 0.06, h, 0.13)


def pedestal_sink(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Round / oval basin (rim at h) on a tapered column with a flat tap deck at the back; brass mixer."""
    hw, hd = w / 2, d / 2
    rc = min(0.085, hw * 0.35)
    parts = [Part(_box(-rc * 1.5, -rc * 1.5 - 0.03, 0, rc * 1.5, rc * 1.5 - 0.03, 0.03), "ceramic", "cyl")]
    for i in range(5):  # column narrowing towards the basin
        za, zb = 0.03 + (h - 0.2) * i / 5, 0.03 + (h - 0.2) * (i + 1) / 5
        r = rc * (1.15 - 0.1 * i)
        parts.append(Part(_box(-r, -r - 0.03, za, r, r - 0.03, zb), "ceramic", "cyl"))
    for i in range(6):  # bowl under the rim, widening upwards
        za, zb = h - 0.2 + 0.1 * i / 6, h - 0.2 + 0.1 * (i + 1) / 6
        f = 0.45 + 0.55 * math.sin(math.pi / 2 * (i + 1) / 6)
        parts.append(Part(_box(-hw * f, -hd * f, za, hw * f, hd * f, zb), "ceramic", "cyl"))
    tube, n = 0.035, 48
    rx, ry = hw - tube / 2, hd - tube / 2
    for k in range(n):  # rim wall: a ring of short upright tubes -> a real hollow bowl
        a = 2 * math.pi * k / n
        cx, cy = rx * math.cos(a), ry * math.sin(a)
        parts.append(Part(_box(cx - tube / 2, cy - tube / 2, h - 0.1, cx + tube / 2, cy + tube / 2, h), "ceramic",
                          "cyl"))
    parts += [Part(_box(-hw * 0.45, -hd * 0.97, h - 0.1, hw * 0.45, -hd * 0.62, h - 0.003), "ceramic"),  # deck
              Part(_box(-0.022, -0.022, h - 0.102, 0.022, 0.022, h - 0.099), "chrome", "cyl")]  # drain
    return parts + _tap(0.0, -hd * 0.8, h - 0.003, 0.11)


def round_mirror(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Round mirror (diameter = min(w, h), centred) in a thin brass frame; 'backlit' = LED halo behind it."""
    hd, r, zc = d / 2, min(w, h) / 2, h / 2
    if "backlit" in words:
        return [Part(_box(-r, -hd, zc - r, r, -hd + 0.003, zc + r), "emit", "ycyl", WARM_WHITE),
                Part(_box(-r + 0.025, -hd + 0.003, zc - r + 0.025, r - 0.025, hd - 0.003, zc + r - 0.025), "handle",
                     "ycyl", BRASS),
                Part(_box(-r + 0.031, -hd + 0.005, zc - r + 0.031, r - 0.031, hd, zc + r - 0.031), "mirror", "ycyl")]
    return [Part(_box(-r, -hd, zc - r, r, hd - 0.004, zc + r), "handle", "ycyl", BRASS),
            Part(_box(-r + 0.012, -hd + 0.002, zc - r + 0.012, r - 0.012, hd, zc + r - 0.012), "mirror", "ycyl")]


def arched_mirror(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Tall arched mirror: flat bottom, round top, thin brass frame."""
    hd = d / 2
    return [*_arch(w, h, -hd, hd - 0.004, "handle", BRASS),
            *_arch(w - 0.024, h - 0.024, -hd + 0.002, hd, "mirror", z0=0.012)]


def ladder_towel_rail(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Wooden ladder leaning against the wall (feet at the front, top at the wall), 5 rungs, one towel."""
    hw, hd, s = w / 2, d / 2, 0.035
    y_at = lambda z: (hd - s / 2 - 0.004) - (d - s - 0.012) * z / h  # noqa: E731 - rail centre at height z
    parts = []
    for x in (-hw + s / 2, hw - s / 2):
        pts = [(x, y_at(z), z) for z in (h * i / 16 for i in range(17))]
        parts += [p._replace(box=(x - s / 2, p.box[1], max(p.box[2], 0.0), x + s / 2, p.box[4], min(p.box[5], h)))
                  for p in _path(pts, s, "main")]
    for k in range(5):
        z = h * (0.18 + 0.17 * k)
        parts.append(Part(_box(-hw + s, y_at(z) - 0.012, z - 0.012, hw - s, y_at(z) + 0.012, z + 0.012), "main", "xcyl"))
    zt = h * (0.18 + 0.17 * 3)  # towel over the 4th rung
    yt, tw = y_at(zt), hw - s - 0.03
    parts += [Part(_box(-tw, yt - 0.02, zt - 0.006, tw, yt + 0.02, zt + 0.022), "soft", "xcyl", LIGHT_TONE),
              Part(_box(-tw, yt + 0.013, zt - 0.24, tw, yt + 0.022, zt + 0.004), "soft", color=LIGHT_TONE),
              Part(_box(-tw, yt - 0.022, zt - 0.20, tw, yt - 0.013, zt + 0.004), "soft", color=LIGHT_TONE)]
    return parts


def towel_rail(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Wall towel bar (brass) near the top of the piece, two wall posts, one towel hanging over it."""
    hw, hd = w / 2, d / 2
    zb, yb = h - 0.03, hd - 0.025  # bar axis
    parts = [Part(_box(x - 0.012, -hd, zb - 0.012, x + 0.012, yb, zb + 0.012), "handle", "ycyl", BRASS)
             for x in (-hw + 0.02, hw - 0.02)]
    parts.append(Part(_box(-hw + 0.008, yb - 0.01, zb - 0.01, hw - 0.008, yb + 0.01, zb + 0.01), "handle", "xcyl",
                      BRASS))
    tw, drop = min(0.32, hw - 0.06), min(0.42, zb - 0.01)
    if tw > 0.05:
        parts += [Part(_box(-tw, yb - 0.02, zb - 0.005, tw, yb + 0.02, zb + 0.02), "soft", "xcyl", LIGHT_TONE),
                  Part(_box(-tw, yb + 0.013, zb - drop, tw, yb + 0.022, zb + 0.004), "soft", color=LIGHT_TONE),
                  Part(_box(-tw, yb - 0.022, zb - drop * 0.8, tw, yb - 0.013, zb + 0.004), "soft", color=LIGHT_TONE)]
    return parts


# --------------------------------------------------------------------------- walls / decor
def _canvas(x1: float, z1: float, x2: float, z2: float, y: float, k: int) -> list[Part]:
    """Abstract composition in tones of the piece colour (canvas surface at y, layers 2 mm proud each)."""
    cw, ch = x2 - x1, z2 - z1
    r = min(cw, ch) * 0.24
    cx, cz = x1 + cw * (0.34 if k % 2 == 0 else 0.62), z1 + ch * (0.62 if k % 3 else 0.42)
    bx = x1 + cw * (0.55 if k % 2 == 0 else 0.18)
    return [Part(_box(cx - r, y, cz - r, cx + r, y + 0.002, cz + r), "soft", "ycyl"),
            Part(_box(bx, y, z1 + ch * 0.14, bx + cw * 0.22, y + 0.004, z1 + ch * 0.70), "dark")]


def framed_art(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Canvas (piece colour, abstract shapes in lighter / darker tones) in a thin wooden frame (accent);
    'metal' in the type = brass frame (metal). Hangs flat on the wall (suggest d = 0.03)."""
    hw, hd = w / 2, d / 2
    s, color = min(0.03, w * 0.06, h * 0.06), (BRASS if "metal" in words else WOOD)
    yc = hd - 0.012  # canvas surface, recessed into the frame
    return [*_frame(-hw, 0, hw, h, -hd, hd, s, "handle" if color == BRASS else "main", color),
            Part(_box(-hw + s, -hd, s, hw - s, yc, h - s), "main"), *_canvas(-hw + s, s, hw - s, h - s, yc, 0)]


GALLERY = ((0.00, 0.52, 0.30, 1.00), (0.34, 0.62, 0.62, 1.00), (0.66, 0.48, 1.00, 1.00), (0.00, 0.00, 0.22, 0.46),
           (0.26, 0.08, 0.50, 0.50), (0.54, 0.00, 0.78, 0.42), (0.82, 0.06, 1.00, 0.42))  # x1, z1, x2, z2 (fractions)


def gallery_wall(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Cluster of 7 frames of varied sizes inside the w x h rectangle; frames alternate wood (accent) and brass
    (metal), canvases alternate the piece colour and its lighter tone."""
    hw, hd, parts = w / 2, d / 2, []
    for k, (fx1, fz1, fx2, fz2) in enumerate(GALLERY):
        x1, x2, z1, z2 = -hw + fx1 * w, -hw + fx2 * w, fz1 * h, fz2 * h
        s = min(0.025, (x2 - x1) * 0.08, (z2 - z1) * 0.08)
        brass = k % 3 == 1
        yc = hd - 0.012
        parts += _frame(x1, z1, x2, z2, -hd, hd, s, "handle" if brass else "main", BRASS if brass else WOOD)
        parts.append(Part(_box(x1 + s, -hd, z1 + s, x2 - s, yc, z2 - s), "soft" if k % 2 else "main"))
        parts += _canvas(x1 + s, z1 + s, x2 - s, z2 - s, yc, k)
    return parts


def painted_arch(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """2 mm paint layer in an arch (piece colour) on the front 2 mm of the footprint - give it d = 0.006 and
    place it flush on the wall, so it sits in front of the room paint (2 mm) and wallpaper (4 mm)."""
    hd = d / 2
    return _arch(w, h, hd - 0.002, hd, "main")


def colour_block(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Flat 2 mm painted rectangle (wainscot / headboard block), on the front 2 mm of the footprint (d = 0.006)."""
    return [Part(_box(-w / 2, d / 2 - 0.002, 0, w / 2, d / 2, h), "main")]


def wall_panelling(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Box-moulding / shaker panelling in the piece colour: flat backing, raised frame strips per panel, a cap
    rail on top and a skirting rail at the bottom. Over 1.5 m tall: a low row + a tall row of panels."""
    hw, hd = w / 2, d / 2
    yb, ys, s, m = hd - 0.012, hd - 0.002, 0.025, 0.07  # backing front, strip front, strip width, margin
    parts = [Part(_box(-hw, -hd, 0.1, hw, yb, h - 0.045), "main"),
             Part(_box(-hw, -hd, h - 0.045, hw, hd, h), "main"),  # cap / chair rail
             Part(_box(-hw, -hd, 0, hw, hd - 0.004, 0.1), "main")]  # skirting
    cols = max(1, round(w / 0.7))
    rows = [(0.1, min(0.75, h * 0.32)), (min(0.75, h * 0.32), h - 0.045)] if h > 1.5 else [(0.1, h - 0.045)]
    cw = w / cols
    for z1, z2 in rows:
        for i in range(cols):
            x1 = -hw + i * cw
            parts += _frame(x1 + m, z1 + m, x1 + cw - m, z2 - m, yb, ys, s, "main")
    return parts


def fluted_panel(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Vertical reeded panel: half-round flutes (3 cm) standing out of a backing board, piece colour."""
    hw, hd = w / 2, d / 2
    r = min(0.011, d / 3)
    pitch = 0.03
    n = max(1, int(w / pitch + 1e-6))
    x0 = -n * pitch / 2
    parts = [Part(_box(-hw, -hd, 0, hw, hd - r, h), "main")]
    parts += [Part(_box(x0 + i * pitch, hd - 2 * r, 0, x0 + (i + 1) * pitch, hd, h), "main", "cyl") for i in range(n)]
    return parts


def pegboard(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Perforated board (piece colour) on battens, a grid of holes, wooden pegs (accent), two small shelves on
    the pegs, two brass hooks and a small potted plant."""
    hw, hd = w / 2, d / 2
    yb, yf = -hd + 0.012, -hd + 0.03  # board back / front
    parts = [Part(_box(-hw + 0.03, -hd, z, hw - 0.03, yb, z + 0.04), "dark") for z in (0.05, h - 0.09)]
    parts.append(Part(_box(-hw, yb, 0, hw, yf, h), "main"))
    pitch = 0.075
    nx, nz = max(1, int((w - 0.06) / pitch)), max(1, int((h - 0.06) / pitch))
    ox, oz = -(nx - 1) * pitch / 2, (h - (nz - 1) * pitch) / 2
    pegs = {(1, nz - 3), (nx - 2, nz - 3), (2, 2), (nx // 2 + 1, 2), (nx // 2 + 2, nz // 2), (nx - 2, nz // 2)}
    shelves = ((1, nz - 3, max(3, nx // 2 - 1)), (nx // 2 + 1, 2, max(2, nx // 2 - 2)))
    for i in range(nx):
        for k in range(nz):
            x, z = ox + i * pitch, oz + k * pitch
            parts.append(Part(_box(x - 0.006, yf - 0.002, z - 0.006, x + 0.006, yf + 0.001, z + 0.006), "dark", "ycyl"))
            if (i, k) in pegs:
                parts.append(Part(_box(x - 0.008, yf, z - 0.008, x + 0.008, min(hd, yf + 0.09), z + 0.008), "main",
                                  "ycyl", WOOD))
    for i0, k0, span in shelves:  # shelf resting on two pegs (i0 and i0 + span - 1)
        x1, x2, z = ox + i0 * pitch - 0.04, ox + min(nx - 1, i0 + span - 1) * pitch + 0.04, oz + k0 * pitch + 0.008
        parts.append(Part(_box(max(x1, -hw + 0.01), yf + 0.001, z, min(x2, hw - 0.01), hd - 0.005, z + 0.018), "main",
                          color=WOOD))
    i0, k0, _ = shelves[0]
    px, pz = ox + (i0 + 0.5) * pitch, oz + k0 * pitch + 0.026  # potted plant on the first shelf
    parts += [Part(_box(px - 0.04, yf + 0.02, pz, px + 0.04, yf + 0.1, pz + 0.08), "ceramic", "cyl", "#e9e4dc"),
              *_sphere(px, yf + 0.06, pz + 0.12, 0.06, "plant", n=6)]
    for i in (nx - 2, nx - 3):  # brass hooks low on the board
        x, z = ox + i * pitch, oz + 4 * pitch
        parts += [Part(_box(x - 0.005, yf, z - 0.005, x + 0.005, yf + 0.05, z + 0.005), "handle", "ycyl", BRASS),
                  Part(_box(x - 0.005, yf + 0.04, z, x + 0.005, yf + 0.05, z + 0.03), "handle", color=BRASS)]
    return parts


# --------------------------------------------------------------------------- lighting
def globe_pendant(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Opal glass globe (glows) on a brass rod from a ceiling canopy; globe diameter = min(w, d)."""
    r = min(w, d) / 2
    return [Part(_box(-0.05, -0.05, h - 0.025, 0.05, 0.05, h), "handle", "cyl", BRASS),
            Part(_box(-0.006, -0.006, 2 * r, 0.006, 0.006, h - 0.025), "handle", "cyl", BRASS),
            Part(_box(-0.03, -0.03, 2 * r - 0.012, 0.03, 0.03, 2 * r + 0.015), "handle", "cyl", BRASS),
            *_sphere(0.0, 0.0, r, r, "emit", n=14)]


CLUSTER = ((0.0, 0.0, 0.0, 1.0), (1.0, 0.0, 0.42, 0.85), (1.0, 0.25, 0.18, 0.9), (1.0, 0.5, 0.55, 0.8),
           (1.0, 0.75, 0.3, 0.95))  # ring (0 = centre / 1 = ring), angle (turns), lift (x globe d), size factor


def cluster_pendant(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """3 (narrow) or 5 opal globes hanging at different heights on black cords from one brass canopy."""
    n = 3 if min(w, d) < 0.5 else 5
    g = min(0.22, min(w, d) / (2.4 if n == 3 else 3.0))  # globe diameter
    ring = min(w, d) / 2 - g / 2
    canopy = min(w, d) * 0.22
    parts = [Part(_box(-canopy, -canopy, h - 0.03, canopy, canopy, h), "handle", "cyl", BRASS)]
    spots = CLUSTER[1:4] if n == 3 else CLUSTER
    for ring_f, turn, lift, size in spots:
        r = g / 2 * size
        a = 2 * math.pi * (turn + (0.08 if n == 3 else 0.0))
        cx, cy = ring_f * (ring - (g / 2 - r)) * math.cos(a), ring_f * (ring - (g / 2 - r)) * math.sin(a)
        z0 = lift * g * 1.6
        parts += _sphere(cx, cy, z0 + r, r, "emit", n=12)
        parts.append(Part(_box(cx - 0.002, cy - 0.002, z0 + 2 * r, cx + 0.002, cy + 0.002, h - 0.03), "black"))
        parts.append(Part(_box(cx - 0.018, cy - 0.018, z0 + 2 * r - 0.008, cx + 0.018, cy + 0.018, z0 + 2 * r + 0.02),
                          "handle", "cyl", BRASS))
    return parts


def arc_geometry(w: float, d: float, h: float) -> dict:
    """Key points of an arc floor lamp: base at the local -x end, the arm arcs over w to the shade at +x."""
    hw = w / 2
    br = min(d / 2, 0.2)  # heavy base radius
    sr = min(0.19, d / 2)  # shade radius
    bx, sx = -hw + br, hw - sr
    span = max(sx - bx, 0.0)
    rise = min(max(span * 0.5, 0.15), 0.6) if span > 0.05 else 0.0
    sh = sr * 0.85  # shade height
    z_end = h - rise - 0.01  # where the arc comes back down (shade hangs below it)
    shade_top = z_end - 0.04 if span > 0.05 else h - 0.01
    return {"br": br, "sr": sr, "bx": bx, "sx": sx, "span": span, "rise": rise, "z_end": z_end, "sh": sh,
            "shade_top": shade_top, "shade_bottom": shade_top - sh}


def arc_floor_lamp(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Arc floor lamp: heavy round base (dark tone of the piece colour) at the local -x end, brass stem rising
    and arching over w, dome shade (piece colour) at the +x end with a glowing diffuser. The whole lamp stays in
    w x d, so place the footprint over what it lights (it reaches over the sofa: footprint overlap expected)."""
    g = arc_geometry(w, d, h)
    bx, sx, tube = g["bx"], g["sx"], 0.022
    parts = [Part(_box(bx - g["br"], -g["br"], 0, bx + g["br"], g["br"], 0.05), "dark", "cyl"),
             Part(_box(bx - g["br"] * 0.8, -g["br"] * 0.8, 0.05, bx + g["br"] * 0.8, g["br"] * 0.8, 0.07), "dark",
                  "cyl")]
    if g["span"] > 0.05:
        parts.append(Part(_box(bx - tube / 2, -tube / 2, 0.07, bx + tube / 2, tube / 2, g["z_end"]), "handle", "cyl",
                          BRASS))
        pts = [(bx + g["span"] * (1 - math.cos(math.pi * i / 24)) / 2, 0.0,
                g["z_end"] + g["rise"] * math.sin(math.pi * i / 24)) for i in range(25)]
        parts += _path(pts, tube, "handle", BRASS)
        parts.append(Part(_box(sx - 0.006, -0.006, g["shade_top"], sx + 0.006, 0.006, g["z_end"]), "handle", "cyl",
                          BRASS))
    else:  # too narrow to arc: straight stem, the dome on top
        parts.append(Part(_box(bx - tube / 2, -tube / 2, 0.07, bx + tube / 2, tube / 2, g["shade_top"]), "handle",
                          "cyl", BRASS))
    sb = g["shade_bottom"]
    parts += _dome(sx, 0.0, sb, g["sr"], g["sh"], "main")
    parts.append(Part(_box(sx - g["sr"] * 0.85, -g["sr"] * 0.85, sb - 0.004, sx + g["sr"] * 0.85, g["sr"] * 0.85,
                           sb - 0.001), "emit", "cyl"))
    return parts


def sconce_geometry(w: float, d: float, h: float) -> tuple[float, float]:
    """(shade radius, shade centre y) of a wall sconce."""
    r = max(min(w / 2, (d - 0.03) / 2), 0.02)
    return r, d / 2 - r


def wall_sconce(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Round brass wall plate + short arm + upright cylinder shade (piece colour), glowing at both ends."""
    hd = d / 2
    r, cy = sconce_geometry(w, d, h)
    pr = min(w / 2, 0.05, h / 2)
    return [Part(_box(-pr, -hd, h / 2 - pr, pr, -hd + 0.012, h / 2 + pr), "handle", "ycyl", BRASS),
            Part(_box(-0.008, -hd + 0.012, h / 2 - 0.008, 0.008, cy - r + 0.004, h / 2 + 0.008), "handle", color=BRASS),
            Part(_box(-r, cy - r, 0.015, r, cy + r, h - 0.015), "main", "cyl"),
            Part(_box(-r * 0.85, cy - r * 0.85, 0.0, r * 0.85, cy + r * 0.85, 0.015), "emit", "cyl"),
            Part(_box(-r * 0.85, cy - r * 0.85, h - 0.015, r * 0.85, cy + r * 0.85, h), "emit", "cyl")]


def picture_light(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Brass picture light: wall plate, stem up the wall, arm forward, long half-round hood with an LED strip
    underneath. Hang it just above a frame (elevation = top of the art)."""
    hw, hd = w / 2, d / 2
    return [Part(_box(-0.035, -hd, 0.0, 0.035, -hd + 0.01, 0.06), "handle", color=BRASS),
            Part(_box(-0.006, -hd + 0.01, 0.03, 0.006, -hd + 0.022, h - 0.02), "handle", "cyl", BRASS),
            Part(_box(-0.006, -hd + 0.01, h - 0.032, 0.006, hd - 0.04, h - 0.02), "handle", color=BRASS),
            Part(_box(-hw, hd - 0.05, h - 0.05, hw, hd, h), "handle", "xcyl", BRASS),
            Part(_box(-hw + 0.02, hd - 0.04, h - 0.055, hw - 0.02, hd - 0.01, h - 0.052), "emit")]


def mushroom_lamp(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Table lamp with a mushroom dome: round foot, slim stem, half-dome shade (piece colour), glow under it."""
    hw, hd = w / 2, d / 2
    dh = min(hw * 0.8, h * 0.4)
    sb = h - dh
    return [Part(_box(-hw * 0.5, -hd * 0.5, 0, hw * 0.5, hd * 0.5, 0.02), "main", "cyl"),
            Part(_box(-hw * 0.36, -hd * 0.36, 0.02, hw * 0.36, hd * 0.36, 0.04), "main", "cyl"),
            Part(_box(-0.016, -0.016, 0.04, 0.016, 0.016, sb), "main", "cyl"),
            *_dome(0.0, 0.0, sb, min(hw, hd), dh, "main", n=10),
            Part(_box(-hw * 0.8, -hd * 0.8, sb - 0.004, hw * 0.8, hd * 0.8, sb - 0.001), "emit", "cyl")]


# --------------------------------------------------------------------------- seating
def legged_sofa(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Straight sofa on tapered wooden legs (accent): slim arms, base, seat + back cushions per seat,
    two throw pillows (cushion)."""
    hw, hd = w / 2, d / 2
    leg, arm, base = 0.15, 0.11, 0.33
    seat = base + 0.12
    parts = [Part(_box(-hw, -hd, leg, hw, hd, base), "soft"),
             Part(_box(-hw + arm, -hd, base, hw - arm, -hd + 0.15, h - 0.08), "soft")]  # back frame
    for sx in (-1, 1):
        x1, x2 = sorted((sx * hw, sx * (hw - arm)))
        parts.append(Part(_box(x1, -hd, base, x2, hd, 0.64), "soft"))  # arm
        for y in (-hd + 0.07, hd - 0.07):
            parts += _taper_leg(sx * (hw - 0.07), y, 0, leg, 0.024, 0.014)
    n = max(1, round((w - 2 * arm) / 0.8))
    sw = (w - 2 * arm) / n
    for i in range(n):
        x1, x2 = -hw + arm + i * sw + 0.004, -hw + arm + (i + 1) * sw - 0.004
        parts += [Part(_box(x1, -hd + 0.15, base, x2, hd - 0.012, seat), "soft"),
                  Part(_box(x1, -hd + 0.13, seat, x2, -hd + 0.32, h), "soft")]
    for k, sx in enumerate((-1, 1)):
        cx = sx * (hw - arm - 0.26)
        parts.append(Part(_box(cx - 0.21, -hd + 0.33, seat, cx + 0.21, -hd + 0.46, seat + 0.38), "soft",
                          color=(PILLOW, DARK_TONE)[k]))
    return parts


def modular_sofa(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """2-4 low armless modules side by side (4 mm apart): base, deep seat cushion, thick back block,
    one throw pillow (cushion)."""
    hw, hd = w / 2, d / 2
    n = min(4, max(2, round(w / 0.95)))
    mw, base, seat = w / n, 0.24, 0.40
    parts = []
    for i in range(n):
        x1, x2 = -hw + i * mw + 0.002, -hw + (i + 1) * mw - 0.002
        parts += [Part(_box(x1 + 0.03, -hd + 0.03, 0, x2 - 0.03, hd - 0.03, 0.03), "dark"),  # recessed plinth
                  Part(_box(x1, -hd, 0.03, x2, hd, base), "soft"),
                  Part(_box(x1 + 0.006, -hd + 0.26, base, x2 - 0.006, hd - 0.006, seat), "soft"),
                  Part(_box(x1, -hd, base, x2, -hd + 0.26, h - 0.05), "soft"),
                  Part(_box(x1 + 0.006, -hd + 0.006, h - 0.1, x2 - 0.006, -hd + 0.254, h), "soft", "xcyl")]
    cx = -hw + mw * 0.5
    parts.append(Part(_box(cx - 0.22, -hd + 0.27, seat, cx + 0.22, -hd + 0.4, seat + 0.4), "soft", color=PILLOW))
    return parts


def pouf(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Round soft pouf: bulging drum, slightly domed top, a stitched centre button."""
    hw, hd, n, parts = w / 2, d / 2, 8, []
    for i in range(n):
        f = 0.9 + 0.1 * math.sin(math.pi * (i + 0.5) / n)
        parts.append(Part(_box(-hw * f, -hd * f, (h - 0.02) * i / n, hw * f, hd * f, (h - 0.02) * (i + 1) / n),
                          "soft", "cyl"))
    parts += [Part(_box(-hw * 0.8, -hd * 0.8, h - 0.02, hw * 0.8, hd * 0.8, h - 0.004), "soft", "cyl"),
              Part(_box(-0.02, -0.02, h - 0.006, 0.02, 0.02, h), "dark", "cyl")]
    return parts


def daybed(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Daybed: wooden frame (accent) with a back and two low ends on short legs, a mattress (piece colour),
    back cushions, two bolsters and a pillow (cushion)."""
    hw, hd, t = w / 2, d / 2, 0.04
    parts = [*(p for x in (-hw + 0.03, hw - 0.03) for y in (-hd + 0.03, hd - 0.03)
               for p in _taper_leg(x, y, 0, 0.12, 0.024, 0.018)),
             Part(_box(-hw, -hd, 0.12, hw, hd, 0.30), "main", color=WOOD),  # box frame
             Part(_box(-hw, -hd, 0.30, hw, -hd + t, h), "main", color=WOOD),  # back
             Part(_box(-hw, -hd + t, 0.30, -hw + t, hd, 0.66), "main", color=WOOD),  # low ends
             Part(_box(hw - t, -hd + t, 0.30, hw, hd, 0.66), "main", color=WOOD),
             Part(_box(-hw + t + 0.004, -hd + t + 0.004, 0.30, hw - t - 0.004, hd - 0.004, 0.47), "soft")]
    n = max(2, round((w - 2 * t) / 0.65))
    cw = (w - 2 * t) / n
    for i in range(n):  # back cushions
        x1 = -hw + t + i * cw + 0.004
        parts.append(Part(_box(x1, -hd + t + 0.004, 0.47, x1 + cw - 0.008, -hd + t + 0.18, h - 0.04), "soft"))
    for sx, tone in ((-1, PILLOW), (1, DARK_TONE)):  # bolsters along the ends
        x1, x2 = sorted((sx * (hw - t - 0.004), sx * (hw - t - 0.2)))
        parts.append(Part(_box(x1, -hd + t + 0.19, 0.47, x2, hd - 0.03, 0.66), "soft", "ycyl", tone))
    parts.append(Part(_box(-0.22, -hd + t + 0.19, 0.47, 0.22, -hd + t + 0.32, 0.85), "soft", color=LIGHT_TONE))
    return parts


def bench(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Upholstered bench: padded seat (piece colour, rolled front edge) on a wooden rail + tapered legs (accent)."""
    hw, hd, pad = w / 2, d / 2, min(0.10, h * 0.3)
    rail = h - pad
    parts = [Part(_box(-hw + 0.01, -hd + 0.01, rail - 0.05, hw - 0.01, hd - 0.01, rail), "main", color=WOOD),
             Part(_box(-hw, -hd, rail, hw, hd - 0.04, h), "soft"),
             Part(_box(-hw, hd - 0.08, rail, hw, hd, h), "soft", "xcyl")]
    for x in (-hw + 0.06, hw - 0.06):
        for y in (-hd + 0.06, hd - 0.06):
            parts += _taper_leg(x, y, 0, rail - 0.05, 0.022, 0.015)
    return parts


def ottoman(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Upholstered footstool (piece colour) with a welted top cushion on short wooden legs (accent);
    'round' in the type = drum shape."""
    hw, hd, leg = w / 2, d / 2, 0.06
    shape = "cyl" if "round" in words else "box"
    parts = [Part(_box(-hw + 0.004, -hd + 0.004, leg, hw - 0.004, hd - 0.004, h - 0.06), "soft", shape),
             Part(_box(-hw, -hd, h - 0.065, hw, hd, h - 0.05), "soft", shape),  # welt
             Part(_box(-hw + 0.006, -hd + 0.006, h - 0.05, hw - 0.006, hd - 0.006, h), "soft", shape)]
    f = 0.65 if shape == "cyl" else 1.0
    for x in (-(hw * f - 0.05), hw * f - 0.05):
        for y in (-(hd * f - 0.05), hd * f - 0.05):
            parts += _taper_leg(x, y, 0, leg, 0.02, 0.015, n=2)
    return parts


# --------------------------------------------------------------------------- media
def _screen(hw: float, y1: float, z1: float, z2: float) -> list[Part]:
    """TV panel 3 cm deep from y1 (back) with a dark glass face 1 mm proud of its bezel."""
    return [Part(_box(-hw, y1, z1, hw, y1 + 0.03, z2), "black"),
            Part(_box(-hw + 0.008, y1 + 0.03, z1 + 0.008, hw - 0.008, y1 + 0.031, z2 - 0.008), "dark")]


def floor_tv(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Free-standing TV (w = TV width, 16:9 panel at the top of h) on a pole stand: flat foot plate + pole
    (piece colour). 'easel' in the type = three leaning wooden legs (piece colour) and a ledge instead."""
    hw, hd = w / 2, d / 2
    sh = w * 0.5625 + 0.02
    z1 = max(h - sh, 0.3)
    if "easel" in words:
        yf = hd - 0.05  # screen back
        z_ledge = z1
        legs = [_line((sx * hw * 0.42, yf - 0.03, 0.0), (sx * 0.05, yf - 0.09, h), 12) for sx in (-1, 1)]
        legs.append(_line((0.0, -hd + 0.02, 0.0), (0.0, yf - 0.1, h - 0.03), 12))
        parts = [p for pts in legs for p in _path(pts, 0.03, "main")]
        parts.append(Part(_box(-hw * 0.5, yf - 0.06, z_ledge - 0.03, hw * 0.5, hd, z_ledge), "main"))
        return parts + _screen(hw, yf, z_ledge, min(z_ledge + sh, h))
    plate = min(hw * 0.7, 0.32)
    return [Part(_box(-plate, -hd, 0, plate, hd, 0.02), "main"),
            Part(_box(-0.035, -0.06, 0.02, 0.035, -0.02, z1 + sh * 0.7), "main"),
            Part(_box(-0.12, -0.03, z1 + sh * 0.25, 0.12, -0.02, z1 + sh * 0.65), "dark"),  # VESA plate
            *_screen(hw, -0.02, z1, z1 + sh)]


def swivel_tv(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """TV on a swivel floor pedestal: round weighted base and a round column (piece colour), panel on top."""
    hw, hd = w / 2, d / 2
    sh = w * 0.5625 + 0.02
    z1 = max(h - sh, 0.3)
    br = min(hd, 0.3)
    return [Part(_box(-br, -br, 0, br, br, 0.025), "main", "cyl"),
            Part(_box(-br * 0.7, -br * 0.7, 0.025, br * 0.7, br * 0.7, 0.04), "main", "cyl"),
            Part(_box(-0.045, -0.045, 0.04, 0.045, 0.045, z1 + sh * 0.6), "main", "cyl"),
            Part(_box(-0.14, 0.045, z1 + sh * 0.25, 0.14, 0.06, z1 + sh * 0.65), "dark"),
            *_screen(hw, 0.06, z1, z1 + sh)]


def projector_screen(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Ceiling cassette (piece colour, top at h) with the screen pulled down to the bottom of the piece: black
    top drop + side borders, matte white surface, weighted bottom bar and a pull tab."""
    hw, hd = w / 2, d / 2
    cas, drop = 0.09, min(0.25, h * 0.15)
    zt, zb = h - cas, 0.035  # screen top / bottom
    sx = hw - 0.06
    return [Part(_box(-hw, -hd, zt, hw, hd, h), "main"),
            Part(_box(-hw - 0.0, -hd + 0.01, zt - 0.004, -hw + 0.03, hd - 0.01, zt), "dark"),  # end caps
            Part(_box(hw - 0.03, -hd + 0.01, zt - 0.004, hw, hd - 0.01, zt), "dark"),
            Part(_box(-sx, -0.005, zt - drop, sx, 0.005, zt - 0.004), "black"),
            Part(_box(-sx, -0.004, zb, sx, 0.004, zt - drop), "main", color="#f2f1ee"),  # projection surface
            Part(_box(-sx, -0.005, zb, -sx + 0.04, 0.005, zt - drop), "black"),
            Part(_box(sx - 0.04, -0.005, zb, sx, 0.005, zt - drop), "black"),
            Part(_box(-sx - 0.005, -0.012, zb - 0.03, sx + 0.005, 0.012, zb), "dark"),  # bottom bar
            Part(_box(-0.03, -0.004, 0.0, 0.03, 0.004, zb - 0.03), "black")]


# --------------------------------------------------------------------------- kitchen / bar
def peninsula_counter(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Peninsula: 60 cm base-cabinet run on the -y (kitchen) side - doors in the accent colour with brass bar
    handles - a stone top (piece colour) overhanging towards +y for stools, and a waterfall end at +x."""
    hw, hd = w / 2, d / 2
    t, cab = 0.04, min(0.6, d - 0.05)
    xe = hw - t - 0.002  # cabinet run stops before the waterfall end
    parts = [Part(_box(-hw, -hd, h - t, hw, hd, h), "main"), Part(_box(hw - t, -hd, 0, hw, hd, h - t), "main"),
             Part(_box(-hw + 0.01, -hd + 0.06, 0, xe - 0.01, -hd + cab - 0.02, 0.1), "dark"),  # plinth
             Part(_box(-hw, -hd + 0.019, 0.1, xe, -hd + cab, h - t), "main", color=WOOD)]  # carcass
    n = max(1, round((xe + hw) / 0.6))
    dw = (xe + hw) / n
    for i in range(n):
        x1, x2 = -hw + i * dw + 0.0015, -hw + (i + 1) * dw - 0.0015
        parts.append(Part(_box(x1, -hd, 0.1 + 0.002, x2, -hd + 0.019, h - t - 0.002), "front", color=WOOD))
        hx = x1 + 0.04 if i % 2 else x2 - 0.05
        parts.append(Part(_box(hx, -hd - 0.025, h - t - 0.2, hx + 0.012, -hd, h - t - 0.05), "handle", color=BRASS))
    return parts


def bar_stool(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Bar / counter stool: round upholstered seat (piece colour) on a wooden pan, four slim brass legs and a
    brass footrest frame at 30 cm. Seat height = h (65 counter / 75 bar)."""
    hw, hd = w / 2, d / 2
    lx, ly = hw * 0.6, hd * 0.6
    parts = [Part(_box(-hw, -hd, h - 0.065, hw, hd, h), "soft", "cyl"),
             Part(_box(-hw * 0.85, -hd * 0.85, h - 0.09, hw * 0.85, hd * 0.85, h - 0.065), "main", "cyl", WOOD)]
    for x in (-lx, lx):
        for y in (-ly, ly):
            parts.append(Part(_box(x - 0.012, y - 0.012, 0, x + 0.012, y + 0.012, h - 0.09), "handle", "cyl", BRASS))
    z = 0.30
    parts += [Part(_box(-lx, -ly - 0.008, z, lx, -ly + 0.008, z + 0.016), "handle", color=BRASS),
              Part(_box(-lx, ly - 0.008, z, lx, ly + 0.008, z + 0.016), "handle", color=BRASS),
              Part(_box(-lx - 0.008, -ly + 0.008, z, -lx + 0.008, ly - 0.008, z + 0.016), "handle", color=BRASS),
              Part(_box(lx - 0.008, -ly + 0.008, z, lx + 0.008, ly - 0.008, z + 0.016), "handle", color=BRASS)]
    return parts


# --------------------------------------------------------------------------- kids / baby
def bunk_shelf(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Low kids' cube shelf (piece colour): grid of ~36 cm open cubes on a back panel, fabric toy bins (cushion
    tones) in every other cube with a finger hole."""
    hw, hd, t = w / 2, d / 2, 0.018
    cols, rows = max(1, round(w / 0.36)), max(1, round(h / 0.36))
    cw, rh = (w - t) / cols, (h - t) / rows
    parts = [Part(_box(-hw, -hd, 0, hw, -hd + 0.006, h), "main")]
    for i in range(cols + 1):
        x = -hw + i * cw
        parts.append(Part(_box(x, -hd + 0.006, 0, x + t, hd, h), "main"))
    for k in range(rows + 1):
        z = k * rh
        parts.append(Part(_box(-hw + t, -hd + 0.006, z, hw - t, hd, z + t), "main"))  # between the sides
    tones = (PILLOW, LIGHT_TONE, DARK_TONE)
    for i in range(cols):
        for k in range(rows):
            if (i + k) % 2:
                continue
            x1, z1 = -hw + i * cw + t + 0.01, k * rh + t
            x2, z2 = x1 + cw - t - 0.02, z1 + (rh - t) * 0.8
            parts += [Part(_box(x1, -hd + 0.03, z1, x2, hd - 0.01, z2), "soft", color=tones[(i + k // 2) % 3]),
                      Part(_box((x1 + x2) / 2 - 0.04, hd - 0.01, z2 - 0.07, (x1 + x2) / 2 + 0.04, hd - 0.008, z2 - 0.04),
                           "dark", color=DARK_TONE)]
    return parts


def crib(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Baby cot (60 x 120 mattress -> about 1.26 x 0.66 x 0.9 m): corner posts, top / bottom rails, round slats
    on all four sides (gaps ~5 cm, EN 716), mattress on a base board at the upper position, a folded blanket."""
    hw, hd, p = w / 2, d / 2, 0.045
    parts = [Part(_box(x, y, 0, x + p, y + p, h), "main") for x in (-hw, hw - p) for y in (-hd, hd - p)]
    for z1, z2 in ((0.12, 0.17), (h - 0.045, h)):
        parts += [Part(_box(-hw + p, -hd + 0.005, z1, hw - p, -hd + 0.04, z2), "main"),
                  Part(_box(-hw + p, hd - 0.04, z1, hw - p, hd - 0.005, z2), "main"),
                  Part(_box(-hw + 0.005, -hd + p, z1, -hw + 0.04, hd - p, z2), "main"),
                  Part(_box(hw - 0.04, -hd + p, z1, hw - 0.005, hd - p, z2), "main")]
    pitch, r = 0.075, 0.011
    for y in (-hd + 0.0225, hd - 0.0225):  # long sides
        n = int((w - 2 * p) / pitch)
        x0 = -(n - 1) * pitch / 2
        parts += [Part(_box(x0 + i * pitch - r, y - r, 0.17, x0 + i * pitch + r, y + r, h - 0.045), "main", "cyl")
                  for i in range(n)]
    for x in (-hw + 0.0225, hw - 0.0225):  # ends
        n = int((d - 2 * p) / pitch)
        y0 = -(n - 1) * pitch / 2
        parts += [Part(_box(x - r, y0 + i * pitch - r, 0.17, x + r, y0 + i * pitch + r, h - 0.045), "main", "cyl")
                  for i in range(n)]
    mz = min(0.38, h - 0.45)
    parts += [Part(_box(-hw + 0.04, -hd + 0.04, mz - 0.02, hw - 0.04, hd - 0.04, mz), "dark"),
              Part(_box(-hw + 0.045, -hd + 0.045, mz, hw - 0.045, hd - 0.045, mz + 0.10), "soft", color=LIGHT_TONE),
              Part(_box(hw - 0.4, -hd + 0.08, mz + 0.10, hw - 0.1, hd - 0.08, mz + 0.13), "soft", color=PILLOW)]
    return parts


def changing_table(w: float, d: float, h: float, words: list[str]) -> list[Part]:
    """Changing table: 3-drawer dresser (piece colour, top at h - 0.10) with brass knobs, a padded changing mat
    with raised edges (cushion) and a low wooden guard rail on the back and both ends (up to h)."""
    hw, hd = w / 2, d / 2
    top, plinth, rail = h - 0.10, 0.08, 0.02
    ff = hd - 0.022  # drawer front face (the knobs stand out to hd)
    yf = ff - 0.02  # drawer fronts from yf to ff
    parts = [Part(_box(-hw + 0.02, -hd + 0.02, 0, hw - 0.02, yf - 0.03, plinth), "dark"),
             Part(_box(-hw, -hd, plinth, hw, yf - 0.005, top), "main"),
             Part(_box(-hw + 0.004, yf - 0.005, plinth + 0.002, hw - 0.004, yf, top - 0.03), "dark")]  # shadow gaps
    dh = (top - 0.03 - plinth) / 3
    for k in range(3):
        z1, z2 = plinth + k * dh + 0.0015, plinth + (k + 1) * dh - 0.0015
        parts.append(Part(_box(-hw + 0.0015, yf, z1, hw - 0.0015, ff, z2), "front"))
        zc = (z1 + z2) / 2
        for kx in ((-w / 4, w / 4) if w > 0.8 else (0.0,)):  # brass knobs
            parts.append(Part(_box(kx - 0.015, ff - 0.004, zc - 0.015, kx + 0.015, hd, zc + 0.015), "handle", "ycyl",
                              BRASS))
    parts.append(Part(_box(-hw, -hd, top - 0.03, hw, ff, top), "main"))  # top board (over the fronts)
    parts += [Part(_box(-hw, -hd, top, hw, -hd + rail, h), "main"),  # guard rails
              Part(_box(-hw, -hd + rail, top, -hw + rail, ff - 0.01, h), "main"),
              Part(_box(hw - rail, -hd + rail, top, hw, ff - 0.01, h), "main")]
    mx = min(0.4, hw - rail - 0.004)
    parts += [Part(_box(-mx + 0.06, -hd + rail + 0.004, top, mx - 0.06, ff - 0.03, top + 0.05), "soft",
                   color=LIGHT_TONE),
              Part(_box(-mx, -hd + rail + 0.004, top, -mx + 0.07, ff - 0.03, top + 0.09), "soft", "ycyl", LIGHT_TONE),
              Part(_box(mx - 0.07, -hd + rail + 0.004, top, mx, ff - 0.03, top + 0.09), "soft", "ycyl", LIGHT_TONE)]
    return parts


# --------------------------------------------------------------------------- dispatch
Shape = Callable[[float, float, float, list[str]], list[Part]]

# (main type word, word that must also be in the type or None, shape). First match wins; checked before the
# built-in shapes of furniture._parts, so 'console-sink' is found here and plain 'sink' falls through.
LIBRARY: tuple[tuple[str, str | None, Shape], ...] = (
    ("sink", "console", console_sink), ("sink", "integrated", integrated_sink), ("sink", "pedestal", pedestal_sink),
    ("mirror", "round", round_mirror), ("mirror", "arched", arched_mirror),
    ("rail", "ladder", ladder_towel_rail), ("rail", "towel", towel_rail),
    ("art", "framed", framed_art), ("art", None, framed_art), ("wall", "gallery", gallery_wall),
    ("arch", "painted", painted_arch), ("block", "colour", colour_block), ("block", "color", colour_block),
    ("panelling", None, wall_panelling), ("paneling", None, wall_panelling), ("panel", "fluted", fluted_panel),
    ("pegboard", None, pegboard),
    ("pendant", "globe", globe_pendant), ("pendant", "cluster", cluster_pendant),
    ("lamp", "arc", arc_floor_lamp), ("lamp", "mushroom", mushroom_lamp), ("sconce", None, wall_sconce),
    ("light", "picture", picture_light),
    ("sofa", "legged", legged_sofa), ("sofa", "modular", modular_sofa), ("pouf", None, pouf),
    ("daybed", None, daybed), ("ottoman", None, ottoman),
    ("tv", "floor", floor_tv), ("tv", "easel", floor_tv), ("tv", "swivel", swivel_tv),
    ("screen", "projector", projector_screen), ("counter", "peninsula", peninsula_counter),
    ("stool", "bar", bar_stool), ("stool", "counter", bar_stool),
    ("shelf", "bunk", bunk_shelf), ("crib", None, crib), ("cot", None, crib), ("table", "changing", changing_table),
)


def library_parts(type_: str, w: float, d: float, h: float) -> list[Part] | None:
    """Parts of a library shape, or None if the type is not in the library."""
    words = type_.split("-")
    t = words[-1]
    if t == "bench" and "banquette" not in words:  # banquette benches stay solid blocks
        return bench(w, d, h, words)
    for main, extra, shape in LIBRARY:
        if t == main and (extra is None or extra in words):
            return shape(w, d, h, words)
    return None
