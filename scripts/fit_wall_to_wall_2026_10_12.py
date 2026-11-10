"""One-off (ADR 0013): built-in furniture fitted wall to wall again after the ADR 0012 re-dimensioning.

SPANS: local id -> (a, b, at): the world interval [a, b] its width must cover (x for pieces at 0/180 deg, y at
90/270; None = keep that end) and `at`, the piece's centre on the other axis (which wall it stands against).
A piece is fitted in every variant file (V1, DEV, D1-D5) where it exists against that wall (within AT) and
both its ends are already within MATCH of the target - a variant that placed it elsewhere is left alone.
Storage modules follow: an end that grows by >= NEW_MODULE gets its own module (copy of the end module, single
door hinged at the wall end, empty interior); a smaller change widens the end module.
MOVES: (local id, expected y, new y). Run from the repo root, then regenerate the V1 styles:
    uv run python scripts/fit_wall_to_wall_2026_10_12.py
    uv run python scripts/restyle/run.py
"""

from __future__ import annotations

import math
import re
import tomllib
from pathlib import Path

MATCH = 0.40
AT = 0.15
NEW_MODULE = 0.20
MODULE = r"(?ms)^\[\[items\.storage\.modules\]\]\n.*?(?=^\[|\Z)"

SPANS: dict[str, tuple[float | None, float | None, float]] = {
    # bedroom 2 dressing: bath-2 wall (y 2.10) to the dressing-door wall (y 4.055) - was 35 cm short
    "wardrobe-master-suite-1": (2.10, 4.055, 6.65),
    "led-strip-master-suite-2": (2.10, 4.055, 6.62),  # cove strip on top of it
    # bedroom 2 wardrobe on the bath-2 wall: facade-B corner to the end of that wall (y 2.10)
    "wardrobe-master-suite-2": (0.25, 2.10, 3.85),
    "led-strip-master-suite-1": (0.25, 2.10, 3.836),
    # bedroom 1 wardrobe on the bath-1 wall: party wall to the bath-1 corner (x 8.715)
    "wardrobe-bedroom-1-1": (8.715, 10.565, 7.275),
    # kitchen run on the living wall: facade B (x 0.45) to the hall wall (x 4.945)
    "wall-cabinet-kitchen-1": (0.45, 4.245, 6.045),
    "wall-cabinet-kitchen-2": (0.45, 4.245, 5.945),
    "tall-cabinet-kitchen-1": (4.245, 4.945, 5.945),
    "pantry-kitchen-1": (4.095, 4.945, 5.945),  # D3's tall unit at the same place
    # bath 2: tub wall to wall, tall cabinet down to the facade-side wall
    "bathtub-master-bathroom-1": (0.25, 1.975, 4.63),
    "tall-cabinet-master-bathroom-1": (0.25, 1.15, 6.79),
    # wallpapers: corner to the next piece / window
    "wallpaper-master-suite-1": (0.45, 3.55, 0.252),  # facade B to wardrobe-master-suite-2
    "wallpaper-living-1": (0.90, 4.82, 10.698),  # facade B to window W1
    # DEV living wardrobe up to facade A; D4/D5 hall wardrobes up to the end of the hall wall (y 6.37)
    "wardrobe-living-1": (6.887, 10.70, 6.715),
    "wardrobe-hall-2": (None, 6.37, 5.33),
}
# niche LEDs stay centred on the dressing's wood column m1 (it grows 7 mm at the +y end)
MOVES = [("led-strip-master-suite-3", 3.748, 3.7515), ("led-strip-master-suite-4", 3.748, 3.7515)]
FILES = ["V1", "DEV", "D1", "D2", "D3", "D4", "D5"]


def num(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def fit(block: str, it: dict, span: tuple) -> str | None:
    w = it["size"][0]
    rot = it.get("rotation", 0) % 360
    ux, uy = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
    ax = 0 if ux else 1  # world axis of the width
    sign = ux or uy  # +1: local +x (module 1) is the high world end
    if abs(it["position"][1 - ax] - span[2]) > AT:
        return None
    c = it["position"][ax]
    lo, hi = c - w / 2, c + w / 2
    a, b = span[0] if span[0] is not None else lo, span[1] if span[1] is not None else hi
    if abs(lo - a) > MATCH or abs(hi - b) > MATCH or (abs(lo - a) < 5e-4 and abs(hi - b) < 5e-4):
        return None
    pos = list(it["position"])
    pos[ax] = (a + b) / 2
    block = re.sub(r"(?m)^size = \[[^,]+,", f"size = [{num(b - a)},", block, count=1)
    block = re.sub(r"(?m)^position = \[[^\]]*\]", f"position = [{num(pos[0])}, {num(pos[1])}]", block, count=1)
    if not re.search(MODULE, block):
        return block
    # growth at the module-1 end (local +x) and at the last-module end
    first_ext, last_ext = (b - hi, lo - a) if sign > 0 else (lo - a, b - hi)
    for ext, which, hinge in ((last_ext, -1, "door-right"), (first_ext, 0, "door-left")):
        if abs(ext) < 5e-4:
            continue
        text = list(re.finditer(MODULE, block))[which][0]
        if ext >= NEW_MODULE:
            if which == 0:
                raise ValueError(f"{it['id']}: adding a module before m1 is not supported")
            new = re.sub(r"(?m)^width = .*$", f"width = {num(ext)}", text)
            new = re.sub(r'kind = "doors"', f'kind = "{hinge}"', new)
            new = re.sub(r"(?m)^interior = .*$", "interior = []", new)
            new = re.sub(r"(?m)^label = .*\n", "", new)
            block = block.replace(text, text.rstrip("\n") + "\n" + new.rstrip("\n") + "\n\n", 1)
        else:
            width = float(re.search(r"(?m)^width = ([\d.]+)", text)[1]) + ext
            block = block.replace(text, re.sub(r"(?m)^width = .*$", f"width = {num(width)}", text, count=1), 1)
    return block


def apply(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    items = {i["id"].split(".", 1)[1]: i for i in tomllib.loads(text).get("items", [])}
    parts = re.split(r"(?m)^(?=\[\[items\]\]\s*$)", text)
    done = []
    for k, part in enumerate(parts):
        m = re.search(r'(?m)^id = "[^".]+\.([^"]+)"', part)
        if not part.startswith("[[items]]") or not m:
            continue
        local = m[1]
        if local in SPANS and (new := fit(part, items[local], SPANS[local])) is not None:
            parts[k] = new
            done.append(local)
        for mid, y0, y1 in MOVES:
            if local == mid and abs(items[local]["position"][1] - y0) < 5e-4:
                parts[k] = re.sub(r"(?m)^position = \[([^,]+), [^\]]*\]", rf"position = [\1, {num(y1)}]", part, count=1)
                done.append(local)
    path.write_text("".join(parts), encoding="utf-8", newline="\n")
    return done


if __name__ == "__main__":
    for key in FILES:
        print(f"{key}:", ", ".join(apply(Path("data/variants") / f"{key}.toml")) or "-")
