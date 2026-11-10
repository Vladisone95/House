"""Restyle V1: same furniture, ids, sizes, positions, rotations - only colours and finishes change.

One file per style in scripts/restyle/styles/<KEY>.py defines SPEC; `uv run python scripts/restyle/run.py`
regenerates every style (or only the keys given) from the CURRENT layout and merges the styles' finishes into
data/apartment.toml (ADR 0011). Edit a layout -> re-run, the styles follow. To try a style privately:

    from restyle_lib import make, stage
    SPEC = dict(name=..., description=..., wall_color=..., rooms={...}, aprons={...}, colors={...},
                finishes={"<style>_<name>": {kind=..., size=[..], color=.., color2=.., joint_color=.., joint=.., roughness=.., note=..}})
    make("V7", SPEC)    # writes data/variants/V7.toml
    stage("V7", SPEC)                            # private apartment.toml + variants dir for validate / build / render

SPEC keys
- rooms:   {room_id: dict(floor=<finish>, walls=<finish>|absent, paint="#rrggbb", skirting="#rrggbb")}
           room ids: living, kitchen, hall, bath_1, bath_2, bedroom_1 (kids), bedroom_2 (master suite), balcony.
           V1 values are kept for anything not given (except walls / paint, which reset).
- aprons:  {V1 apron finish: new finish | {room_id: new finish}} - V1 aprons: ripple (living + master wallpaper),
           delicate_blues (kids wallpaper), cream_marble (kitchen backsplash), greige_stone (bath 2 tub front).
- colors:  {"*" | room_id: {V1 colour (lower-case #rrggbb): new colour}}. Style variants are built with
           true_colors: sofas, chairs, rugs, towels, sheers show exactly the colour given (any darkness).
           A "soft:" / "shag:" prefix is accepted and ignored (older specs).
- accent:  {"*" | room_id: colour} - the built-in second colour of pieces that have one: sofa / armchair
           wooden base + feet, duvet linen on beds, the walk-in shower curb. Per piece: accent_items {local id: colour}.
- cushion: {"*" | room_id: colour} (or cushion_items {local id: colour}) - throw cushions on sofas / armchairs.
- metal:   {"*" | room_id: colour} - taps, shower bars, mirror frames, screen profiles, dining-chair legs
           (default: the colour the style maps V1's brass #b08d57 to).
- items:   {local id: {field: value}} - exact per-piece overrides applied last (color, accent, metal,
           apron_color, tag_color, handle_color, interior_color, front_color:<module index>).
- finishes: new finishes this style needs (names MUST start with the style's slug, e.g. "japandi_"),
           merged into data/apartment.toml by the orchestrator later.
"""
from dataclasses import replace
from pathlib import Path

from apartment_core.furniture import (
    ACCENTS,
    BRASS,
    CUSHIONS,
    RoomFinish,
    copy_variant,
    get_color,
    item_parts,
    load_variant,
    set_color,
    variant_to_toml,
)

ROOT = Path(__file__).resolve().parents[2]
SCRATCH = ROOT / ".tmp"  # stage() output (git-ignored)


def base_for(target: str, lighten: float) -> str:
    """Base colour that the build's lightened shade (sRGB c + (1 - c) * lighten) turns into ``target``."""
    out = []
    for i in (1, 3, 5):
        t = int(target[i:i + 2], 16) / 255
        out.append(round(max(0.0, (t - lighten) / (1 - lighten)) * 255))
    return "#" + "".join(f"{v:02x}" for v in out)


def make(key: str, spec: dict, out: Path | None = None, source: str = "V1") -> Path:
    src = load_variant(ROOT / f"data/variants/{source}.toml")
    v = copy_variant(src, key, spec["name"])
    v.description, v.wall_color, v.style_of = spec["description"], spec["wall_color"], source
    rooms = {}
    for rid, rf in src.rooms.items():
        new = spec["rooms"].get(rid, {})
        rooms[rid] = replace(rf, floor=new.get("floor", rf.floor), walls=new.get("walls", ""),
                             paint=new.get("paint", ""), skirting=new.get("skirting", rf.skirting))
    for rid, new in spec["rooms"].items():
        rooms.setdefault(rid, RoomFinish(**new))
    v.rooms = rooms
    changed: set[str] = set()

    def remap(it, color: str) -> str:
        if not color:
            return color
        table = {**spec["colors"].get("*", {}), **spec["colors"].get(it.room, {})}
        new = table.get(color.lower())
        if new is None:
            return color
        if new.startswith(("soft:", "shag:")):
            new = new.split(":", 1)[1]  # true colours: the look colour is the colour
        if new != color:
            changed.add(it.id)
        return new

    items = []
    for it in v.items:
        upd = dict(color=remap(it, it.color), tag_color=remap(it, it.tag_color))
        builtin = set() if it.is_storage else {p.color.lower() for p in item_parts(it.type, *it.size, mirror=it.mirror)}
        metal = (spec.get("metal", {}).get(it.room) or spec.get("metal", {}).get("*")
                 or {**spec["colors"].get("*", {}), **spec["colors"].get(it.room, {})}.get(BRASS, ""))
        if metal and (BRASS in builtin or "sink" in it.type):  # brass fittings; sink taps
            upd["metal"] = metal.split(":")[-1]  # taps, mirror frames, screen profiles, chair legs
            changed.add(it.id)
        accent = (spec.get("accent_items", {}).get(it.local_id) or spec.get("accent", {}).get(it.room)
                  or spec.get("accent", {}).get("*"))
        if accent and builtin & set(ACCENTS):
            upd["accent"] = accent  # sofa base / feet, duvet, shower curb
            changed.add(it.id)
        cushion = (spec.get("cushion_items", {}).get(it.local_id) or spec.get("cushion", {}).get(it.room)
                   or spec.get("cushion", {}).get("*"))
        if cushion and builtin & set(CUSHIONS):
            upd["cushion"] = cushion  # throw cushions on sofas / armchairs
            changed.add(it.id)
        if it.apron:
            a = spec["aprons"].get(it.apron, it.apron)
            upd["apron"] = a.get(it.room, it.apron) if isinstance(a, dict) else a
        if it.storage is not None:
            st = it.storage
            mods = tuple(replace(m, front_color=remap(it, m.front_color)) for m in st.modules)
            upd["storage"] = replace(st, handle_color=remap(it, st.handle_color),
                                     interior_color=remap(it, st.interior_color), modules=type(st.modules)(mods))
        new = replace(it, **upd)
        if new != it:
            new = replace(new, note=f"{spec['name']} style (from {source}.{it.local_id}, same place and size)")
        items.append(new)
    v.items = items
    v.true_colors = True
    for local, fields in spec.get("items", {}).items():  # exact per-piece overrides
        for fld, val in fields.items():
            set_color(v, f"{local}/{fld}", val, owner=False)
    out = out or ROOT / f"data/variants/{key}.toml"
    if out.exists():  # colours the owner picked in Blender survive regeneration
        old = load_variant(out)
        for path in old.owner_colors:
            try:
                set_color(v, path, get_color(old, path))
            except (KeyError, StopIteration, IndexError):
                print(f"  {key}: owner colour {path} no longer applies (piece / module gone)")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(variant_to_toml(v), encoding="utf-8")
    print(key, "restyled", len(changed), "of", len(items), "pieces ->", out)
    return out


def finishes_toml(spec: dict) -> str:
    def val(x):
        if isinstance(x, str):
            return '"' + x.replace('"', "'") + '"'
        if isinstance(x, (list, tuple)):
            return "[" + ", ".join(val(e) for e in x) + "]"
        return repr(x)
    out = []
    for name, f in spec.get("finishes", {}).items():
        out += ["", f"[finishes.{name}]", *(f"{k} = {val(v)}" for k, v in f.items())]
    return "\n".join(out) + "\n"


def stage(key: str, spec: dict) -> Path:
    """scratchpad/styles/<KEY>/ : apartment.toml (+ this style's finishes), variants/<KEY>.toml (+ V1).
    Then:  uv run apartment --data <dir>/apartment.toml --variants-dir <dir>/variants validate
           uv run apartment --data ... --variants-dir ... build --out <dir>/<KEY>.blend
           uv run apartment render --blend <dir>/<KEY>.blend --variant <KEY> --views all --time "2026-10-04 13:00"
    """
    d = SCRATCH / "styles" / key
    (d / "variants").mkdir(parents=True, exist_ok=True)
    (d / "finishes.toml").write_text(finishes_toml(spec), encoding="utf-8")
    base = (ROOT / "data/apartment.toml").read_text(encoding="utf-8")
    marker = "# >>> style-variant finishes"  # run.py's generated block: dropped, this spec's finishes follow
    if marker in base:
        base = base[: base.index(marker)]
    (d / "apartment.toml").write_text(base + "\n" + finishes_toml(spec), encoding="utf-8")
    for f in (d / "variants").glob("*.toml"):
        f.unlink()
    (d / "variants" / "V1.toml").write_text((ROOT / "data/variants/V1.toml").read_text(encoding="utf-8"),
                                            encoding="utf-8")
    make(key, spec, out=d / "variants" / f"{key}.toml")
    return d
