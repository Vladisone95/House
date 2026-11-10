"""One-off migration (ADR 0012): move furniture, fixed points and built-ins with their room's walls
when the shell was re-fitted to the developer's dimensioned plan + sales-sheet areas (2026-10-06).

Rule per axis: a piece keeps its distance to the nearest wall face of its room (old face -> new face).
Text-based edits so comments / formatting in the TOML files survive. Run once from the repo root:
    uv run python scripts/migrate_dimensions_2026_10_06.py
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

# room -> (X breakpoints, Y breakpoints) as (old face, new face)
BP: dict[str, tuple[list[tuple[float, float]], list[tuple[float, float]]]] = {
    "living": ([(0.45, 0.90), (6.8, 7.015)], [(6.737, 6.37), (10.913, 10.70)]),
    "kitchen": ([(0.45, 0.45), (4.7, 4.945)], [(3.915, 3.695), (6.612, 6.245)]),
    "bedroom_1": ([(6.925, 7.14), (8.32, 8.715), (10.245, 10.565)], [(5.986, 6.19), (7.206, 6.975), (10.913, 10.70)]),
    "bath_1": ([(8.445, 8.84), (10.245, 10.565)], [(4.52, 4.18), (7.081, 6.85)]),
    "hall": ([(4.825, 5.07), (6.8, 7.015), (8.32, 8.715)], [(3.915, 4.18), (4.52, 4.18), (5.861, 6.065), (6.737, 6.37)]),
    "bedroom_2": ([(0.45, 0.45), (4.114, 4.15), (6.8, 6.95)], [(0.25, 0.25), (2.175, 2.10), (3.79, None)]),
    "bath_2": ([(4.239, 4.275), (6.8, 6.95)], [(0.25, 0.25), (2.05, 1.975)]),
    "balcony": ([(-1.619, -1.265), (0.0, 0.45)], [(6.737, 6.75), (10.913, 10.70)]),
}
# whole-room polygons before the change (to find the room of a piece without `room`)
OLD_BOX = {
    "living": (0.45, 6.737, 6.8, 10.913), "kitchen": (0.45, 3.915, 4.7, 6.612),
    "bedroom_1": (6.925, 5.986, 10.245, 10.913), "bath_1": (8.445, 4.52, 10.245, 7.081),
    "hall": (4.825, 3.915, 8.32, 6.737), "bedroom_2": (0.45, 0.25, 6.8, 3.79),
    "bath_2": (4.239, 0.25, 6.8, 2.05), "balcony": (-1.619, 6.737, 0.0, 10.913),
}


def extents(size, rotation) -> tuple[float, float]:
    w, d = float(size[0]), float(size[1])
    r = round(float(rotation or 0)) % 180
    if r == 0:
        return w, d
    if r == 90:
        return d, w
    return max(w, d), max(w, d)


def shift(bps, c: float, half: float, other_hi: float | None = None) -> float:
    """Delta for a footprint [c-half, c+half]: move with the nearest old wall face."""
    best = None
    for old, new in bps:
        if new is None:  # bedroom-2 top: kitchen wall left of x 5.145, hall/suite wall right of it
            new = 3.57 if other_hi is not None and other_hi <= 5.12 else 4.055
        dist = min(abs(c - half - old), abs(c + half - old))
        if best is None or dist < best[0]:
            best = (dist, new - old)
    return best[1]


def room_of(x: float, y: float) -> str | None:
    for rid, (x1, y1, x2, y2) in OLD_BOX.items():
        if x1 - 0.05 <= x <= x2 + 0.05 and y1 - 0.05 <= y <= y2 + 0.05:
            return rid
    return None


def delta(room: str | None, pos, size=(0, 0), rotation=0) -> tuple[float, float]:
    room = room if room in BP else room_of(*pos)
    if room is None:
        return 0.0, 0.0
    ex, ey = extents(size, rotation)
    bx, by = BP[room]
    dx = shift(bx, pos[0], ex / 2)
    dy = shift(by, pos[1], ey / 2, other_hi=pos[0] + ex / 2)
    return dx, dy


def fmt(v: float) -> str:
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


POS = re.compile(r"^position = \[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]", re.M)
AIM = re.compile(r"aim = \[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,")


def move_block(block: str, dx: float, dy: float) -> str:
    if not (dx or dy):
        return block
    block = POS.sub(lambda m: f"position = [{fmt(float(m[1]) + dx)}, {fmt(float(m[2]) + dy)}]", block, count=1)
    return AIM.sub(lambda m: f"aim = [{fmt(float(m[1]) + dx)}, {fmt(float(m[2]) + dy)},", block)


def migrate_variant(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    items = {i["id"]: i for i in tomllib.loads(text).get("items", [])}
    parts = re.split(r"(?m)^(?=\[\[items\]\]\s*$)", text)
    log = []
    for k, part in enumerate(parts):
        m = re.search(r'(?m)^id = "([^"]+)"', part)
        if not part.startswith("[[items]]") or not m or m[1] not in items:
            continue
        it = items[m[1]]
        dx, dy = delta(it.get("room"), it["position"], it.get("size", (0, 0)), it.get("rotation", 0))
        parts[k] = move_block(part, dx, dy)
        if dx or dy:
            log.append(f"{it['id']}: {dx:+.3f}, {dy:+.3f}")
    path.write_text("".join(parts), encoding="utf-8", newline="\n")
    return log


def migrate_layout(path: Path) -> list[str]:
    """Fixed points + built-ins in apartment.toml (the entrance door is placed explicitly)."""
    text = path.read_text(encoding="utf-8")
    raw = tomllib.loads(text)
    log = []
    for kind in ("fixed_points", "built_ins"):
        for it in raw.get(kind, []):
            if it["id"] == "BI_entrance_door":
                continue
            dx, dy = delta(it["room"], it["position"], it.get("size", (0, 0)), it.get("rotation", 0))
            pat = re.compile(r'(id = "' + re.escape(it["id"]) + r'"\n(?:[^\[\n][^\n]*\n|\n)*?)position = \[[^\]]*\]')
            x, y = it["position"]
            new = f"position = [{x + dx:.3f}, {y + dy:.3f}]"
            text = pat.sub(lambda m, new=new: m[1] + new, text, count=1)
            log.append(f"{it['id']}: {dx:+.3f}, {dy:+.3f}")
    path.write_text(text, encoding="utf-8", newline="\n")
    return log


if __name__ == "__main__":
    for line in migrate_layout(Path("data/apartment.toml")):
        print(line)
    for p in sorted(Path("data/variants").glob("*.toml")):
        log = migrate_variant(p)
        print(f"{p.name}: {len(log)} pieces moved")
