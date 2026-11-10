"""2D/3D geometry helpers - pure Python, no numpy, no bpy."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence

Rect = tuple[float, float, float, float]
Box = tuple[float, float, float, float, float, float]  # x1, y1, z1, x2, y2, z2
Point = tuple[float, float]

EPS = 1e-6


def polygon_area(poly: Sequence[Point]) -> float:
    """Signed shoelace area (positive = counter-clockwise)."""
    s = 0.0
    for (x1, y1), (x2, y2) in zip(poly, [*poly[1:], poly[0]], strict=True):
        s += x1 * y2 - x2 * y1
    return s / 2.0


def polygon_centroid(poly: Sequence[Point]) -> Point:
    a = polygon_area(poly)
    cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(poly, [*poly[1:], poly[0]], strict=True):
        f = x1 * y2 - x2 * y1
        cx += (x1 + x2) * f
        cy += (y1 + y2) * f
    return cx / (6 * a), cy / (6 * a)


def point_in_polygon(pt: Point, poly: Sequence[Point]) -> bool:
    x, y = pt
    inside = False
    for (x1, y1), (x2, y2) in zip(poly, [*poly[1:], poly[0]], strict=True):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def rect_area(r: Rect) -> float:
    return max(0.0, r[2] - r[0]) * max(0.0, r[3] - r[1])


def rect_intersection(a: Rect, b: Rect) -> float:
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w * h if w > EPS and h > EPS else 0.0


def point_in_rect(pt: Point, r: Rect) -> bool:
    return r[0] < pt[0] < r[2] and r[1] < pt[1] < r[3]


def polygon_rect_overlap(poly: Sequence[Point], r: Rect, samples: int = 6) -> bool:
    """Coarse test: does the interior of ``r`` overlap the polygon interior?"""
    for i in range(samples):
        for j in range(samples):
            px = r[0] + (r[2] - r[0]) * (i + 0.5) / samples
            py = r[1] + (r[3] - r[1]) * (j + 0.5) / samples
            if point_in_polygon((px, py), poly):
                return True
    return False


def footprint_cells(rects: Iterable[Rect], polygons: Iterable[Sequence[Point]]) -> list[Rect]:
    """Split the union of rects + polygons into grid cells (for floor / ceiling slabs)."""
    rects = list(rects)
    polygons = [list(p) for p in polygons]
    xs = sorted({round(v, 6) for r in rects for v in (r[0], r[2])} | {round(p[0], 6) for poly in polygons for p in poly})
    ys = sorted({round(v, 6) for r in rects for v in (r[1], r[3])} | {round(p[1], 6) for poly in polygons for p in poly})
    cells = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            c = (xs[i], ys[j], xs[i + 1], ys[j + 1])
            if rect_area(c) < EPS:
                continue
            mid = ((c[0] + c[2]) / 2, (c[1] + c[3]) / 2)
            if any(point_in_rect(mid, r) for r in rects) or any(point_in_polygon(mid, p) for p in polygons):
                cells.append(c)
    return cells


def wall_boxes(
    rect: Rect,
    horizontal: bool,
    height: float,
    openings: Sequence[tuple[float, float, float, float]],
) -> list[Box]:
    """Split a rectangular wall into solid boxes around its openings.

    ``openings`` = [(axis_from, axis_to, sill, head), ...] along the wall's long axis.
    Returns boxes (x1, y1, z1, x2, y2, z2) whose union is the wall minus the openings.
    """
    x1, y1, x2, y2 = rect
    a0, a1 = (x1, x2) if horizontal else (y1, y2)

    def box(s: float, e: float, z0: float, z1: float) -> Box:
        if horizontal:
            return (s, y1, z0, e, y2, z1)
        return (x1, s, z0, x2, e, z1)

    out: list[Box] = []
    cursor = a0
    for s, e, sill, head in sorted(openings):
        if s - cursor > EPS:
            out.append(box(cursor, s, 0.0, height))
        if sill > EPS:
            out.append(box(s, e, 0.0, sill))
        if height - head > EPS:
            out.append(box(s, e, head, height))
        cursor = e
    if a1 - cursor > EPS:
        out.append(box(cursor, a1, 0.0, height))
    return out


def door_swing(
    rect: Rect,
    horizontal: bool,
    span: tuple[float, float],
    hinge: str,
    swing: str,
    segments: int = 16,
) -> tuple[list[Point], list[Point]]:
    """Plan symbol of a hinged door drawn wide open (90 degrees).

    ``hinge`` = "start" | "end" of ``span``; ``swing`` = "+" | "-" side of the wall the leaf
    opens to. Returns (leaf, arc): leaf = [hinge point, open tip] on the wall face of the swing
    side; arc = points from the open tip round to the closed latch point.
    """
    x1, y1, x2, y2 = rect
    t_lo, t_hi = (y1, y2) if horizontal else (x1, x2)
    face = t_hi if swing == "+" else t_lo
    out = 1.0 if swing == "+" else -1.0
    a_h, a_o = (span[0], span[1]) if hinge == "start" else (span[1], span[0])
    width = abs(a_o - a_h)
    along = 1.0 if a_o > a_h else -1.0

    def pt(a: float, t: float) -> Point:
        return (a, t) if horizontal else (t, a)

    leaf = [pt(a_h, face), pt(a_h, face + out * width)]
    arc = []
    for i in range(segments + 1):
        th = math.pi / 2 * (1 - i / segments)  # 90 deg (open) -> 0 (closed)
        arc.append(pt(a_h + along * width * math.cos(th), face + out * width * math.sin(th)))
    return leaf, arc


def rotated_rect(center: Point, width: float, depth: float, angle_deg: float) -> list[Point]:
    """Corners (counter-clockwise) of a width x depth rectangle centred on ``center``, rotated CCW."""
    cx, cy = center
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    hw, hd = width / 2, depth / 2
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd))]


def offset_convex(poly: Sequence[Point], d: float) -> list[Point]:
    """Shrink (d < 0) or grow (d > 0) a convex polygon by moving each vertex away from the centroid."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    out = []
    for x, y in poly:
        r = math.hypot(x - cx, y - cy) or 1.0
        out.append((x + (x - cx) / r * d, y + (y - cy) / r * d))
    return out


def convex_overlap(a: Sequence[Point], b: Sequence[Point]) -> bool:
    """True if two convex polygons overlap with positive area (separating-axis test)."""
    for poly in (a, b):
        for (x1, y1), (x2, y2) in zip(poly, [*poly[1:], poly[0]], strict=True):
            nx, ny = y1 - y2, x2 - x1
            pa = [nx * x + ny * y for x, y in a]
            pb = [nx * x + ny * y for x, y in b]
            if max(pa) <= min(pb) + EPS or max(pb) <= min(pa) + EPS:
                return False
    return True


def polygon_inside(inner: Sequence[Point], outer: Sequence[Point], samples: int = 8) -> bool:
    """True if every vertex and sampled edge point of ``inner`` lies inside ``outer`` (any simple polygon)."""
    for (x1, y1), (x2, y2) in zip(inner, [*inner[1:], inner[0]], strict=True):
        for i in range(samples):
            t = i / samples
            if not point_in_polygon((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t), outer):
                return False
    return True


def point_segment_distance(pt: Point, a: Point, b: Point) -> float:
    (px, py), (ax, ay), (bx, by) = pt, a, b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 < EPS else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def point_polygon_distance(pt: Point, poly: Sequence[Point]) -> float:
    """0 inside the polygon, else the distance to its nearest edge."""
    if point_in_polygon(pt, poly):
        return 0.0
    return min(point_segment_distance(pt, a, b) for a, b in zip(poly, [*poly[1:], poly[0]], strict=True))


def cladding_boxes(
    polygon: Sequence[Point],
    walls: Sequence[tuple[Rect, bool, Sequence[tuple[float, float, float, float]]]],
    height: float,
    thickness: float = 0.01,
) -> list[Box]:
    """All wall-tile boxes of a room (see ``cladding_walls``)."""
    return [b for _, boxes in cladding_walls(polygon, walls, height, thickness) for b in boxes]


def cladding_walls(
    polygon: Sequence[Point],
    walls: Sequence[tuple[Rect, bool, Sequence[tuple[float, float, float, float]]]],
    height: float,
    thickness: float = 0.01,
    walled_only: bool = False,
) -> list[tuple[Point, list[Box]]]:
    """Wall tiles of a room: a thin skin inside every (axis-aligned) polygon edge, up to ``height``.

    ``walls`` = [(rect, horizontal, openings), ...] with openings as in ``wall_boxes``. Openings of a
    wall whose face lies on an edge are cut out of that edge's skin (doors stay open).
    One entry per edge: (origin, boxes) - origin = the edge's low-coordinate corner on the tiled face,
    where the tile layout starts with a full tile. ``walled_only``: only where a wall's face really is (open
    passages between rooms stay bare - e.g. skirting boards).
    """
    ccw = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(polygon, [*polygon[1:], polygon[0]], strict=True)) > 0
    out: list[tuple[Point, list[Box]]] = []
    for a, b in zip(polygon, [*polygon[1:], polygon[0]], strict=True):
        horizontal = abs(a[1] - b[1]) < EPS
        if not horizontal and abs(a[0] - b[0]) > EPS:
            continue  # slanted edge: no skin
        k = 1 if horizontal else 0  # coordinate that is constant along the edge
        c, (s0, s1) = a[k], sorted((a[1 - k], b[1 - k]))
        d = (b[0] - a[0]) if horizontal else -(b[1] - a[1])  # interior on the left of a CCW edge
        inward = (1 if d > 0 else -1) * (1 if ccw else -1)
        lo, hi = (c, c + thickness) if inward > 0 else (c - thickness, c)
        ops, spans = [], []
        for rect, w_horizontal, w_ops in walls:
            faces = (rect[1], rect[3]) if w_horizontal else (rect[0], rect[2])
            if w_horizontal != horizontal or not any(abs(f - c) < 1e-3 for f in faces):
                continue
            r0, r1 = (rect[0], rect[2]) if horizontal else (rect[1], rect[3])
            if min(r1, s1) - max(r0, s0) > EPS:
                spans.append((max(r0, s0), min(r1, s1)))
            ops += [(max(s, s0), min(e, s1), sill, head) for s, e, sill, head in w_ops if min(e, s1) - max(s, s0) > EPS]
        face = hi if inward > 0 else lo
        boxes: list[Box] = []
        for a0, a1 in (sorted(spans) if walled_only else [(s0, s1)]):
            rect = (a0, lo, a1, hi) if horizontal else (lo, a0, hi, a1)
            boxes += wall_boxes(rect, horizontal, height,
                                [(max(s, a0), min(e, a1), sl, hd) for s, e, sl, hd in ops if min(e, a1) - max(s, a0) > EPS])
        out.append(((s0, face) if horizontal else (face, s0), boxes))
    return out


def scatter_trees(footprint: Rect, margin: float, n: int, seed: int = 7, keep_off: float = 6.0
                  ) -> list[tuple[float, float, float, float]]:
    """Deterministic tree spots on the lawn ring around a building footprint: (x, y, height, crown radius).

    Trees stay ``keep_off`` m clear of the building and 2 m inside the lawn's edge, and 4 m apart."""
    import random

    rnd = random.Random(seed)
    x0, y0, x1, y1 = footprint
    out: list[tuple[float, float, float, float]] = []
    tries = 0
    while len(out) < n and tries < n * 200:
        tries += 1
        x, y = rnd.uniform(x0 - margin + 2, x1 + margin - 2), rnd.uniform(y0 - margin + 2, y1 + margin - 2)
        if x0 - keep_off < x < x1 + keep_off and y0 - keep_off < y < y1 + keep_off:
            continue
        if any(math.hypot(x - a, y - b) < 4.0 for a, b, _, _ in out):
            continue
        out.append((round(x, 2), round(y, 2), round(rnd.uniform(5.5, 9.0), 2), round(rnd.uniform(1.6, 2.6), 2)))
    return out


def _edges(polygon: Sequence[Point]) -> list[tuple[Point, Point]]:
    return list(zip(polygon, [*polygon[1:], polygon[0]], strict=True))


def inward_normals(polygon: Sequence[Point]) -> list[Point]:
    """Unit normal of every edge pointing into the polygon (either winding)."""
    ccw = sum(a[0] * b[1] - b[0] * a[1] for a, b in _edges(polygon)) > 0
    out = []
    for a, b in _edges(polygon):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1.0
        out.append((-dy / n, dx / n) if ccw else (dy / n, -dx / n))
    return out


def walled_edges(polygon: Sequence[Point], wall_rects: Iterable[Rect], tol: float = 1e-3) -> list[bool]:
    """For each (axis-aligned) edge: does a wall's face lie on it (overlapping > 5 cm)?"""
    rects = list(wall_rects)
    out = []
    for a, b in _edges(polygon):
        horizontal = abs(a[1] - b[1]) < EPS
        k = 1 if horizontal else 0
        c, (s0, s1) = a[k], sorted((a[1 - k], b[1 - k]))
        hit = False
        for r in rects:
            faces, (r0, r1) = ((r[1], r[3]), (r[0], r[2])) if horizontal else ((r[0], r[2]), (r[1], r[3]))
            if any(abs(f - c) < tol for f in faces) and min(s1, r1) - max(s0, r0) > 0.05:
                hit = True
                break
        out.append(hit)
    return out


def inset_rectilinear(polygon: Sequence[Point], dists: Sequence[float]) -> list[Point]:
    """Move every edge of a rectilinear polygon inwards by its own distance (0 = stays); corners follow."""
    normals = inward_normals(polygon)
    out = []
    for i, v in enumerate(polygon):
        (n1, d1), (n2, d2) = (normals[i - 1], dists[i - 1]), (normals[i], dists[i])
        if abs(n1[0] * n2[1] - n1[1] * n2[0]) < EPS:  # collinear edges: one offset
            out.append((v[0] + n2[0] * d2, v[1] + n2[1] * d2))
        else:
            out.append((v[0] + n1[0] * d1 + n2[0] * d2, v[1] + n1[1] * d1 + n2[1] * d2))
    return out
