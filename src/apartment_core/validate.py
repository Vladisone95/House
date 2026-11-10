"""Consistency checks for the apartment model. Run: ``uv run apartment validate``."""

from __future__ import annotations

from dataclasses import dataclass

from .geometry import (
    EPS,
    offset_convex,
    point_in_polygon,
    point_polygon_distance,
    polygon_area,
    polygon_inside,
    polygon_rect_overlap,
    rect_intersection,
)
from .model import Apartment


@dataclass(frozen=True)
class Issue:
    level: str  # "error" | "warning"
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper():7}] {self.code}: {self.message}"


def room_areas(apt: Apartment) -> dict[str, float]:
    return {r.id: abs(polygon_area(r.polygon)) for r in apt.all_rooms()}


def validate(apt: Apartment) -> list[Issue]:
    issues: list[Issue] = []
    err = lambda c, m: issues.append(Issue("error", c, m))  # noqa: E731
    warn = lambda c, m: issues.append(Issue("warning", c, m))  # noqa: E731

    # --- rooms vs listed areas
    areas = room_areas(apt)
    for r in apt.all_rooms():
        a = areas[r.id]
        dev = (a - r.listed_area) / r.listed_area
        if abs(dev) > apt.area_tolerance:
            err("area", f"{r.id}: {a:.2f} m2 vs listed {r.listed_area:.2f} m2 ({dev:+.1%})")
        if polygon_area(r.polygon) < 0:
            warn("winding", f"{r.id}: polygon is clockwise (expected counter-clockwise)")
    usable = sum(areas[r.id] for r in apt.rooms)
    dev = (usable - apt.listed_usable_area) / apt.listed_usable_area
    if abs(dev) > apt.area_tolerance:
        err("area_total", f"usable {usable:.2f} m2 vs listed {apt.listed_usable_area:.2f} ({dev:+.1%})")

    # --- walls
    ids = [w.id for w in apt.walls]
    for dup in {i for i in ids if ids.count(i) > 1}:
        err("wall_id", f"duplicate wall id {dup}")
    for w in apt.walls:
        x1, y1, x2, y2 = w.rect
        if x2 - x1 <= EPS or y2 - y1 <= EPS:
            err("wall_rect", f"{w.id}: degenerate rect {w.rect}")
            continue
        short = min(x2 - x1, y2 - y1)
        if abs(short - w.thickness) > 0.002:
            err("wall_thickness", f"{w.id}: {short:.3f} m thick, type '{w.type}' expects {w.thickness:.3f} m")
    for i, a in enumerate(apt.walls):
        for b in apt.walls[i + 1 :]:
            if (ov := rect_intersection(a.rect, b.rect)) > 1e-5:
                err("wall_overlap", f"{a.id} overlaps {b.id} ({ov:.4f} m2) - walls must tile, not overlap")

    # --- openings
    wall_ids = set(ids)
    h = apt.levels.ceiling_height
    for o in apt.openings:
        if o.wall not in wall_ids:
            err("opening_wall", f"{o.id}: unknown wall '{o.wall}'")
            continue
        w = apt.wall(o.wall)
        lo, hi = w.axis_range
        if o.span[0] < lo + 0.05 - EPS or o.span[1] > hi - 0.05 + EPS:
            err("opening_span", f"{o.id}: span {o.span} not inside wall {w.id} range ({lo:.3f}, {hi:.3f}) with 5 cm margin")
        if o.width <= 0.3:
            err("opening_width", f"{o.id}: width {o.width:.3f} m is implausible")
        if not (0 <= o.sill < o.head <= h + EPS):
            err("opening_height", f"{o.id}: sill {o.sill} / head {o.head} invalid for ceiling {h}")
        if o.kind == "door":
            if o.hinge not in ("", "start", "end") or o.swing not in ("", "+", "-") or bool(o.hinge) != bool(o.swing):
                err("door_swing", f"{o.id}: hinge '{o.hinge}' / swing '{o.swing}' - need both, hinge start|end, swing +|-")
        elif o.hinge or o.swing:
            err("door_swing", f"{o.id}: hinge/swing only apply to kind 'door', not '{o.kind}'")
        # an opening must not cut through a wall that joins this one
        for other in apt.walls:
            if other.id == w.id or not _touching(w.rect, other.rect):
                continue
            o_lo, o_hi = (other.rect[0], other.rect[2]) if w.horizontal else (other.rect[1], other.rect[3])
            if o_lo < o.span[1] - EPS and o_hi > o.span[0] + EPS and (o_hi - o_lo) < (hi - lo):
                err("opening_junction", f"{o.id} on {w.id} cuts through joining wall {other.id}")
    for w in apt.walls:
        ops = apt.openings_in(w.id)
        for a, b in zip(ops, ops[1:], strict=False):
            if b.span[0] < a.span[1] + 0.10:
                err("opening_overlap", f"{a.id} and {b.id} overlap or are < 10 cm apart on {w.id}")

    # --- rooms vs walls / each other
    for r in apt.all_rooms():
        for w in apt.walls:
            if polygon_rect_overlap(r.polygon, w.rect):
                err("room_wall_overlap", f"{r.id} overlaps wall {w.id}")
        if r.camera and not point_in_polygon(r.camera.eye, r.polygon):
            warn("camera", f"{r.id}: camera eye {r.camera.eye} is outside the room")
    # --- fixed service points (pipes, drains, vents) - variants must respect them
    room_ids = {r.id for r in apt.all_rooms()}
    fids = [f.id for f in apt.fixed_points]
    for dup in sorted({i for i in fids if fids.count(i) > 1}):
        err("fixed_point", f"duplicate fixed point id {dup}")
    for f in apt.fixed_points:
        if f.room not in room_ids:
            err("fixed_point", f"{f.id}: unknown room '{f.room}'")
            continue
        if not f.serves or f.radius <= 0:
            err("fixed_point", f"{f.id}: needs a non-empty 'serves' list and a positive radius")
        if point_polygon_distance(f.position, apt.room(f.room).polygon) > 0.05:
            err("fixed_point", f"{f.id}: position {f.position} is not inside room '{f.room}'")

    # --- floor finishes
    for f in apt.finishes.values():
        bad_color = [c for c in (f.color, f.color2, f.joint_color) if not _is_hex(c)]
        if f.kind not in ("parquet", "tiles", "stone", "marble", "mural", "watercolor", "chevron", "ripple") or len(f.size) != 2 or min(f.size) <= 0 or bad_color:
            err("finish", f"{f.name}: kind parquet|tiles|stone|marble, size [a, b] > 0 and #rrggbb colours needed")
        if f.direction not in ("x", "y") or not 0 <= f.joint < min(f.size or (1,)) / 4:
            err("finish", f"{f.name}: direction x|y and a joint smaller than a quarter of the size needed")
    if apt.finishes:
        for r in apt.all_rooms():
            if r.finish not in apt.finishes:
                warn("finish", f"{r.id}: finish '{r.finish}' is not defined in [finishes] (plain grey floor)")

    # --- built-ins (boiler...): already in the apartment, shown in every variant
    bids = [b.id for b in apt.built_ins]
    for dup in sorted({i for i in bids if bids.count(i) > 1}):
        err("built_in", f"duplicate built-in id {dup}")
    for b in apt.built_ins:
        if b.room not in room_ids:
            err("built_in", f"{b.id}: unknown room '{b.room}'")
            continue
        if len(b.size) != 3 or min(b.size) <= 0 or b.elevation < 0 or b.top > apt.levels.ceiling_height + 1e-6:
            err("built_in", f"{b.id}: size must be 3 positive numbers between floor and ceiling")
        elif not polygon_inside(offset_convex(b.footprint(), -0.01), apt.room(b.room).polygon):
            err("built_in", f"{b.id}: footprint leaves room '{b.room}'")
        if not _is_hex(b.color):
            err("built_in", f"{b.id}: color '{b.color}' is not #rrggbb")

    if (bd := apt.building) is not None and (bd.storeys_below < 0 or bd.floors_above < 0
                                             or bd.party_extension < 0 or bd.grass_margin < 0):
        err("building", "[building]: storeys, extension and grass margin must be >= 0")

    rooms = apt.all_rooms()
    for i, a in enumerate(rooms):
        for b in rooms[i + 1 :]:
            if any(point_in_polygon(p, b.polygon) for p in _interior_samples(a.polygon)):
                err("room_overlap", f"{a.id} overlaps {b.id}")
    return issues


def _is_hex(c: str) -> bool:
    return len(c) == 7 and c[0] == "#" and all(ch in "0123456789abcdefABCDEF" for ch in c[1:])


def _touching(a, b, tol: float = 1e-4) -> bool:
    """Rects share a boundary segment (not just a corner) without overlapping."""
    ox = min(a[2], b[2]) - max(a[0], b[0])
    oy = min(a[3], b[3]) - max(a[1], b[1])
    return (abs(ox) < tol and oy > tol) or (abs(oy) < tol and ox > tol)


def _interior_samples(poly, n: int = 12):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    for i in range(n):
        for j in range(n):
            pt = (min(xs) + (max(xs) - min(xs)) * (i + 0.5) / n, min(ys) + (max(ys) - min(ys)) * (j + 0.5) / n)
            if point_in_polygon(pt, poly):
                yield pt
