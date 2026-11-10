"""One-off (ADR 0012): fit the furniture to the re-dimensioned shell after
`migrate_dimensions_2026_10_06.py` moved every piece with its nearest wall.

EDITS are V1's pieces (local id = id without the "<KEY>." prefix). They are applied to V1 and to every
other variant that still has the same piece in the same place as V1 (D1-D5 started as copies of V1).
WCs follow the developer's 2D plan (owner 2026-10-06). Run from the repo root:
    uv run python scripts/fit_furniture_2026_10_06.py
then regenerate the V1 styles: uv run python scripts/restyle/run.py
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

# local id -> fields to set (position, size, rotation, elevation) + optional module widths / extra module
EDITS: dict[str, dict] = {
    # --- bath 1: WC on the corridor wall by the hall wall (developer plan); shower 110 next to the washer
    "toilet-bathroom-1-1": {"position": (9.40, 4.455)},
    "tall-cabinet-bathroom-1-1": {"position": (9.925, 4.305)},
    "toilet-paper-holder-bathroom-1-1": {"position": (9.13, 4.24)},
    "toilet-brush-bathroom-1-1": {"position": (9.12, 4.30)},
    "toilet-roll-stand-bathroom-1-1": {"position": (8.94, 4.30)},
    "track-light-bathroom-1-1": {"position": (9.70, 5.515)},
    "walk-in-shower-bathroom-1-1": {"position": (10.015, 6.40), "size": (1.10, 0.90, 2.65)},
    "slat-screen-bathroom-1-2": {"position": (9.45, 6.534)},
    # --- bath 2: WC on the corridor wall by the dressing wall (developer plan); tub wall to wall (1.725)
    "toilet-master-bathroom-1": {"position": (6.675, 1.515)},
    "toilet-paper-holder-master-bathroom-1": {"position": (6.88, 1.80)},
    "toilet-brush-master-bathroom-1": {"position": (6.87, 1.24)},
    "bathtub-master-bathroom-1": {"position": (4.63, 1.1125), "size": (1.705, 0.69, 0.55)},
    "track-light-master-bathroom-1": {"position": (5.61, 1.11)},
    # --- hall: straight corridor; key shelf moves to the wall by the entrance (bath-1 wall)
    "track-light-hall-2": {"position": (6.045, 5.275)},
    "doormat-hall-1": {"position": (7.95, 4.455)},
    "shoes-hall-1": {"position": (8.58, 4.33)},
    "shoes-hall-2": {"position": (8.575, 4.62)},
    "wall-shelf-hall-1": {"position": (8.605, 4.85)},
    "wall-shelf-hall-2": {"position": (8.605, 4.90)},
    "plant-hall-1": {"position": (8.605, 4.72)},
    "vase-hall-1": {"position": (8.615, 4.97)},
    "vase-hall-2": {"position": (8.615, 4.90)},
    # --- kitchen: run 24.5 cm longer, room 14.7 cm narrower (dining table 80 deep)
    "base-cabinet-kitchen-1": {"position": (1.9225, 5.945), "size": (1.745, 0.6, 0.87), "add_module": 0.245},
    "countertop-kitchen-1": {"position": (2.0725, 5.935), "size": (3.245, 0.62, 0.03)},
    "backsplash-kitchen-1": {"position": (2.3475, 6.225), "size": (3.795, 0.01, 0.6)},
    "wall-cabinet-kitchen-1": {"position": (2.3525, 6.045), "size": (3.785, 0.4, 0.6),
                               "modules": [0.631] * 5 + [0.63]},
    "wall-cabinet-kitchen-2": {"position": (2.3525, 5.945), "size": (3.785, 0.6, 0.6), "modules": [0.757] * 5},
    "led-strip-kitchen-1": {"position": (2.3225, 5.633), "size": (3.645, 0.03, 0.01)},
    "led-strip-kitchen-2": {"position": (2.6475, 5.875), "size": (3.095, 0.02, 0.01)},
    "venetian-blind-kitchen-1": {"position": (0.49, 4.875)},
    "dining-table-kitchen-1": {"position": (2.4, 4.095), "size": (1.6, 0.8, 0.75)},
    "linear-pendant-light-kitchen-1": {"position": (2.4, 4.095)},
    "upholstered-chair-kitchen-1": {"position": (2.0, 4.745)},
    "upholstered-chair-kitchen-2": {"position": (3.045, 4.745)},
    "upholstered-chair-kitchen-5": {"position": (1.35, 4.095)},
    "upholstered-chair-kitchen-6": {"position": (3.695, 4.095)},
    "place-setting-kitchen-1": {"position": (2.0, 4.335)},
    "place-setting-kitchen-2": {"position": (3.045, 4.335)},
    "place-setting-kitchen-3": {"position": (1.74, 3.99)},
    "place-setting-kitchen-4": {"position": (3.305, 3.99)},
    "serving-bowl-kitchen-1": {"position": (2.4, 4.025)},
    # --- living: desk corner now ends at window W1 -> desk 1.55 long, 17 cm off facade A (curtains pass in front)
    "panel-desk-living-1": {"position": (6.615, 9.715), "size": (1.55, 0.8, 0.8)},
    "monitor-living-1": {"position": (6.835, 9.715)},
    "keyboard-living-1": {"position": (6.415, 9.715)},
    "mouse-living-1": {"position": (6.435, 9.365)},
    "pc-tower-living-1": {"position": (6.765, 9.065)},
    "bonsai-living-1": {"position": (6.815, 10.295)},
    "gaming-chair-living-1": {"position": (5.765, 9.715)},
    # --- curtains follow their (moved) windows
    "drape-living-1": {"position": (4.835, 10.565)},
    "drape-living-2": {"position": (6.24, 10.565)},
    "sheer-curtain-living-1": {"position": (5.535, 10.655)},
    "drape-living-3": {"position": (1.035, 6.917)},
    "drape-living-4": {"position": (1.035, 8.977)},
    "sheer-curtain-living-2": {"position": (0.945, 7.952)},
    "drape-bedroom-1-1": {"position": (7.69, 10.565)},
    "drape-bedroom-1-2": {"position": (9.49, 10.565)},
    "sheer-curtain-bedroom-1-1": {"position": (8.59, 10.655)},
    "drape-master-suite-1": {"position": (0.585, 1.125)},
    "drape-master-suite-2": {"position": (0.585, 2.915)},
    "sheer-curtain-master-suite-1": {"position": (0.495, 2.025)},
    # --- bedroom 2: window wall now too short for drape + AC -> AC over the TV wall, right of the slats
    "air-conditioner-master-suite-1": {"position": (3.35, 3.46), "rotation": 180},
    "heat-recovery-vent-master-suite-1": {"position": (0.49, 3.30)},
    # --- bedroom 1: wallpaper from the wardrobe front to facade A
    "wallpaper-bedroom-1-1": {"position": (10.563, 9.1375), "size": (3.125, 0.004, 2.7)},
    # --- balcony (3.95 long): table set kept together, centred on the outer part
    "outdoor-dining-table-balcony-1": {"position": (-0.50, 8.25)},
    "outdoor-chair-balcony-1": {"position": (-0.50, 9.20)},
    "outdoor-chair-balcony-2": {"position": (-0.50, 7.30)},
    "ceiling-light-balcony-1": {"position": (-0.45, 9.20)},
    "mug-balcony-1": {"position": (-0.47, 8.62)},
    "mug-balcony-2": {"position": (-0.53, 7.88)},
    "lemon-tree-balcony-1": {"position": (-0.96, 10.40)},
}


# DEV and the D designs: their own pieces (applied unconditionally)
VARIANT_EDITS: dict[str, dict[str, dict]] = {
    "DEV": {
        "toilet-bathroom-1-1": {"position": (9.40, 4.455)},
        "shower-bathroom-1-1": {"position": (10.015, 6.40), "size": (1.10, 0.90, 2.10)},
        "recessed-spotlight-hall-1": {"position": (6.045, 4.55)},
        "recessed-spotlight-hall-2": {"position": (6.045, 6.05)},
        # living 23.5 cm shorter: sofa group 12 cm towards facade B, armchairs + plant 11.5 cm towards the wardrobe
        "corner-sofa-living-1": {"position": (2.73, 9.825)},
        "rug-living-1": {"position": (3.28, 8.687)},
        "round-coffee-table-living-1": {"position": (3.38, 8.333)},
        "ring-pendant-light-living-1": {"position": (3.38, 8.333)},
        "round-side-table-living-1": {"position": (2.63, 7.733)},
        "floor-lamp-living-1": {"position": (1.10, 10.387)},
        "armchair-living-1": {"position": (4.88, 9.937)},
        "armchair-living-2": {"position": (5.18, 8.637)},
        "plant-living-1": {"position": (4.38, 10.507)},
        "table-balcony-1": {"position": (-0.496, 8.25)},
        "chair-balcony-1": {"position": (-0.496, 9.113)},
        "chair-balcony-2": {"position": (-0.496, 7.45)},
    },
    "D1": {
        "shoe-cabinet-hall-2": {"position": (5.26, 5.92)},
        "seat-cushion-hall-1": {"position": (5.26, 5.92)},
        "tub-armchair-master-suite-1": {"position": (1.01, 3.19)},
        # desk set (also matched to V1's pieces): explicit so the desk shift is not applied twice
        "monitor-living-1": {"position": (6.835, 9.715)},
        "keyboard-living-1": {"position": (6.415, 9.715)},
        "mouse-living-1": {"position": (6.435, 9.365)},
        "pc-tower-living-1": {"position": (6.715, 9.165)},
        "bonsai-living-1": {"position": (6.815, 10.295)},
        "gaming-chair-living-1": {"position": (5.765, 9.715)},
    },
    "D2": {
        "shoe-bench-cabinet-hall-1": {"position": (5.26, 5.895)},
        "cushion-hall-1": {"position": (5.26, 5.895)},
        "mirror-hall-1": {"position": (5.08, 5.895)},
        "wall-sconce-hall-1": {"position": (5.12, 5.45)},
        "bench-master-suite-1": {"position": (1.75, 2.535)},
        "bookcase-living-1": {"position": (4.655, 6.558)},
        "place-setting-kitchen-3": {"position": (1.74, 3.99)},
        "place-setting-kitchen-4": {"position": (3.305, 3.99)},
    },
    "D3": {
        "shoe-cabinet-hall-1": {"position": (5.26, 5.895)},
        "seat-cushion-hall-1": {"position": (5.245, 5.895)},
        "bird-of-paradise-living-3": {"position": (4.53, 10.237)},
        "nightstand-bedroom-1-1": {"position": (9.44, 8.619)},
        "outdoor-chair-balcony-1": {"position": (-0.896, 9.02)},
    },
    "D4": {
        "bird-of-paradise-living-1": {"position": (4.09, 6.753)},
        "tub-armchair-living-1": {"position": (4.255, 9.837)},
        "arc-floor-lamp-living-1": {"position": (4.78, 10.317)},
        "round-dining-table-kitchen-1": {"position": (2.4, 4.095), "size": (1.6, 0.8, 0.75)},
        "place-setting-kitchen-3": {"position": (1.84, 3.99)},
        "place-setting-kitchen-4": {"position": (3.205, 3.99)},
        "rug-hall-1": {"position": (6.065, 5.275), "size": (0.75, 2.1, 0.01)},
        "rug-hall-2": {"position": (5.865, 5.275), "size": (0.12, 2.1, 0.012)},
        "rug-hall-3": {"position": (6.295, 5.275), "size": (0.05, 2.1, 0.013)},
    },
    "D5": {
        # the wall stub they hung on is gone: console + mirror + vase + plant to the bath-1 wall by the entrance
        "console-table-hall-1": {"position": (8.565, 4.85), "rotation": 90},
        "backlit-mirror-hall-1": {"position": (8.705, 4.85), "rotation": 90},
        "vase-hall-1": {"position": (8.58, 4.72)},
        "plant-hall-1": {"position": (8.58, 4.98)},
        "tub-armchair-living-1": {"position": (4.70, 9.437)},
    },
}
# desks in the living corner by window W1: (desk local id, new length or None, new centre y); everything on /
# at the desk (living, x > 5.3, y > 8.9, not curtains / wardrobe / strips) moves with it
DESKS = {"D1": ("round-desk-living-1", 1.55, 9.715), "D2": ("panel-desk-living-1", 1.55, 9.715),
         "D3": ("panel-desk-living-1", 1.55, 9.715), "D4": ("desk-living-1", None, 9.74),
         "D5": ("panel-desk-living-1", 1.55, 9.715)}


def desk_edits(path: Path, desk: str, length: float | None, y: float) -> dict[str, dict]:
    items = {i["id"].split(".", 1)[1]: i for i in tomllib.loads(path.read_text(encoding="utf-8"))["items"]}
    d = items[desk]
    dy = y - d["position"][1]
    out = {}
    for local, i in items.items():
        x0, y0 = i["position"]
        if i.get("room") != "living" or x0 <= 5.3 or y0 <= 8.9 or any(
                s in local for s in ("drape", "sheer", "wardrobe", "led-strip", "wallpaper")):
            continue
        out[local] = {"position": (x0, round(y0 + dy, 4))}
    if length:
        out[desk]["size"] = (length, *d["size"][1:])
    return out


def num(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def vec(v) -> str:
    return "[" + ", ".join(num(float(x)) for x in v) + "]"


def edit_block(block: str, e: dict) -> str:
    for key in ("position", "size"):
        if key in e:
            block = re.sub(rf"(?m)^{key} = \[[^\]]*\]", f"{key} = {vec(e[key])}", block, count=1)
    for key in ("rotation", "elevation"):
        if key in e:
            if re.search(rf"(?m)^{key} = ", block):
                block = re.sub(rf"(?m)^{key} = .*$", f"{key} = {num(e[key])}", block, count=1)
            else:
                block = re.sub(r"(?m)^(position = .*)$", rf"\1\n{key} = {num(e[key])}", block, count=1)
    if "modules" in e:
        widths = iter(e["modules"])
        block = re.sub(r"(?m)^(\[\[items\.storage\.modules\]\]\nwidth = )[\d.]+",
                       lambda m: m[1] + num(next(widths)), block)
    modules_sum = sum(float(w) for w in re.findall(r"(?m)^width = ([\d.]+)", block))
    if "add_module" in e and e["size"][0] - modules_sum > 0.01:  # idempotent: only while short of the width
        block = block.rstrip("\n") + (f"\n[[items.storage.modules]]\nwidth = {num(e['add_module'])}\n"
                                      'front = "doors"\ninterior = []\n\n')
    return block


def apply(path: Path, edits: dict[str, dict], reference: dict[str, dict] | None) -> list[str]:
    text = path.read_text(encoding="utf-8")
    items = {i["id"].split(".", 1)[1]: i for i in tomllib.loads(text).get("items", [])}
    parts = re.split(r"(?m)^(?=\[\[items\]\]\s*$)", text)
    done = []
    for k, part in enumerate(parts):
        m = re.search(r'(?m)^id = "[^".]+\.([^"]+)"', part)
        if not part.startswith("[[items]]") or not m or m[1] not in edits:
            continue
        local = m[1]
        if reference is not None:  # only pieces still identical to V1's (before this fit)
            ref, it = reference.get(local), items[local]
            if ref is None or any(ref.get(f) != it.get(f) for f in ("position", "size", "rotation")):
                continue
        parts[k] = edit_block(part, edits[local])
        done.append(local)
    path.write_text("".join(parts), encoding="utf-8", newline="\n")
    return done


if __name__ == "__main__":
    vdir = Path("data/variants")
    v1_before = {i["id"].split(".", 1)[1]: i for i in tomllib.loads(
        (vdir / "V1.toml").read_text(encoding="utf-8"))["items"]}
    print("V1:", len(apply(vdir / "V1.toml", EDITS, None)), "pieces fitted")
    for key, edits in VARIANT_EDITS.items():  # own pieces first: a moved piece then no longer matches V1's
        if key in DESKS:
            edits = {**desk_edits(vdir / f"{key}.toml", *DESKS[key]), **edits}
        print(f"{key}:", len(apply(vdir / f"{key}.toml", edits, None)), "own pieces fitted")
    for key in ("D1", "D2", "D3", "D4", "D5"):
        print(f"{key}:", len(apply(vdir / f"{key}.toml", EDITS, v1_before)), "pieces fitted like V1")
