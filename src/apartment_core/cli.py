"""Project CLI - ``uv run apartment <command>``.

Commands
  validate                     check data/apartment.toml + data/variants/*.toml
  plan [--sun "Y-m-d H:M"]     write the 2D plan PNG (docs/plan.png)
  plan --variant A             2D furniture plan with ids (docs/variants/A.png)
  variant list                 list furniture variants
  variant new B [--from A]     create data/variants/B.toml (empty, or a copy of A with re-keyed ids)
  prices [--variant V1] [--open]  fit-out + furniture cost estimate -> docs/prices/<KEY>.html
  sun "Y-m-d H:M"              print sun azimuth/elevation (+ sunrise/sunset)
  build                        generate models/apartment.blend with Blender (headless)
  render [--views ...]         render room cameras to renders/ (--variant B to furnish)
  sun-study --date Y-m-d       render a camera every N minutes through a day
  install-addon                link + enable the 'Apartment Tools' Blender add-on
  open                         open models/apartment.blend in Blender
"""

from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

from .furniture import VARIANTS_DIR, copy_variant, load_variants, validate_variants, variant_to_toml
from .model import PROJECT_ROOT, load
from .validate import room_areas, validate

BLEND = PROJECT_ROOT / "models" / "apartment.blend"
BLENDER_DIR = PROJECT_ROOT / "blender"


def find_blender() -> str:
    if exe := os.environ.get("BLENDER_EXE"):
        return exe
    candidates = sorted(glob.glob(r"C:\Program Files\Blender Foundation\Blender *\blender.exe"), reverse=True)
    if candidates:
        return candidates[0]
    if exe := shutil.which("blender"):
        return exe
    sys.exit("Blender not found - set BLENDER_EXE to the blender executable.")


def run_blender(args: list[str], background: bool = True) -> int:
    cmd = [find_blender(), *(["-b"] if background else []), *args]
    print(">", " ".join(f'"{c}"' if " " in c else c for c in cmd))
    return subprocess.call(cmd, cwd=PROJECT_ROOT)


def cmd_validate(a) -> int:
    apt = load(a.data)
    issues = validate(apt)
    areas = room_areas(apt)
    print(f"{apt.name} - {len(apt.walls)} walls, {len(apt.openings)} openings, {len(apt.all_rooms())} spaces")
    for r in apt.all_rooms():
        dev = (areas[r.id] - r.listed_area) / r.listed_area
        print(f"  {r.id:12} {areas[r.id]:6.2f} m2   listed {r.listed_area:6.2f}   {dev:+6.1%}")
    usable = sum(areas[r.id] for r in apt.rooms)
    print(f"  {'USABLE':12} {usable:6.2f} m2   listed {apt.listed_usable_area:6.2f}")
    variants = load_variants(a.variants_dir)
    for v in variants:
        print(f"  variant {v.key:4} {v.name!r}: {len(v.items)} pieces")
    issues += validate_variants(apt, variants)
    for i in issues:
        print(i)
    errors = [i for i in issues if i.level == "error"]
    print("OK" if not errors else f"FAILED: {len(errors)} error(s)")
    return 1 if errors else 0


def _parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M")


def cmd_plan(a) -> int:
    from .plan2d import render_plan
    from .solar import sun_position_local

    apt = load(a.data)
    sun = None
    if a.sun:
        sun = sun_position_local(_parse_dt(a.sun), apt.site.latitude, apt.site.longitude, apt.site.utc_offset_standard)
    variant = None
    if a.variant:
        variant = next((v for v in load_variants(a.variants_dir) if v.key == a.variant), None)
        if variant is None:
            sys.exit(f"no variant {a.variant!r} - see `apartment variant list`")
    out = a.out or str(PROJECT_ROOT / "docs" / ("plan.png" if not variant else f"variants/{variant.key}.png"))
    out = render_plan(apt, Path(out), sun=sun, variant=variant)
    print(f"wrote {out}")
    return 0


def cmd_variant(a) -> int:
    variants = load_variants(a.variants_dir)
    if a.action == "list":
        for v in variants:
            base = f"  (based on {v.based_on})" if v.based_on else ""
            print(f"{v.key:4} {v.name}  - {len(v.items)} pieces{base}  {v.description}")
        return 0
    if not a.key:
        sys.exit("usage: apartment variant new <KEY> [--from <KEY>] [--name NAME]")
    directory = Path(a.variants_dir or VARIANTS_DIR)
    out = directory / f"{a.key}.toml"
    if out.exists():
        sys.exit(f"{out} already exists")
    if a.source:
        src = next((v for v in variants if v.key == a.source), None)
        if src is None:
            sys.exit(f"no variant {a.source!r}")
        new = copy_variant(src, a.key, a.name)
    else:
        from .furniture import Variant

        new = Variant(key=a.key, name=a.name or f"Variant {a.key}")
    issues = [i for i in validate_variants(load(a.data), [*variants, new]) if i.level == "error"]
    if issues:
        sys.exit("\n".join(map(str, issues)))
    directory.mkdir(parents=True, exist_ok=True)
    out.write_text(variant_to_toml(new), encoding="utf-8")
    print(f"wrote {out} ({len(new.items)} pieces)")
    return 0


def cmd_prices(a) -> int:
    from .pricing import write_price_list

    variants = load_variants(a.variants_dir)
    key = a.variant or load(a.data).start_variant or (variants[0].key if variants else "")
    variant = next((v for v in variants if v.key == key), None)
    if variant is None:
        sys.exit(f"no variant {key!r} - see `apartment variant list`")
    out = Path(a.out or PROJECT_ROOT / "docs" / "prices" / f"{variant.key}.html")
    write_price_list(load(a.data), variant, out)
    print(f"wrote {out}")
    if a.open:
        import webbrowser

        webbrowser.open(out.resolve().as_uri())
    return 0


def cmd_sun(a) -> int:
    from .solar import direction_in_plan, sun_events, sun_position_local

    apt = load(a.data)
    s = apt.site
    t = _parse_dt(a.when)
    pos = sun_position_local(t, s.latitude, s.longitude, s.utc_offset_standard)
    print(f"{t:%Y-%m-%d %H:%M} local (UTC{pos.utc_offset:+.0f})  azimuth {pos.azimuth:6.1f} deg  elevation {pos.elevation:5.1f} deg")
    print("direction to sun in model coords:", tuple(round(v, 3) for v in direction_in_plan(pos, s.plus_y_bearing)))
    ev = sun_events(t.date(), s.latitude, s.longitude, s.utc_offset_standard)
    print("  ".join(f"{k} {v:%H:%M}" if v else f"{k} -" for k, v in ev.items()))
    for facade, normal in (("Facade A (WNW)", s.plus_y_bearing), ("Facade B (SSW)", (s.plus_y_bearing - 90) % 360)):
        diff = (pos.azimuth - normal + 180) % 360 - 180
        lit = pos.elevation > 0 and abs(diff) < 90
        print(f"  {facade}: {'direct sun' if lit else 'no direct sun'} (sun {diff:+.0f} deg from facade normal)")
    return 0


def cmd_build(a) -> int:
    rc = cmd_validate(a)
    if rc and not a.force:
        print("Validation failed - fix data/apartment.toml or pass --force.")
        return rc
    return run_blender(["--factory-startup", "--python", str(BLENDER_DIR / "build_scene.py"), "--", "--data", str(a.data or ""), "--variants-dir", str(a.variants_dir or ""), "--out", str(a.out)])


def cmd_render(a) -> int:
    extra = ["--views", a.views, "--engine", a.engine, "--samples", str(a.samples), "--res", str(a.res)]
    if a.time:
        extra += ["--time", a.time]
    if a.no_ceiling:
        extra += ["--no-ceiling"]
    if a.variant:
        extra += ["--variant", a.variant]
    extra += ["--lights", a.lights]
    return run_blender([str(a.blend), "--python", str(BLENDER_DIR / "render_views.py"), "--", *extra])


def cmd_sun_study(a) -> int:
    extra = ["--date", a.date, "--views", a.views, "--start", a.start, "--end", a.end, "--step", str(a.step),
             "--engine", a.engine, "--samples", str(a.samples), "--res", str(a.res)]
    if a.variant:
        extra += ["--variant", a.variant]
    extra += ["--lights", a.lights]
    return run_blender([str(a.blend), "--python", str(BLENDER_DIR / "render_views.py"), "--", "--study", *extra])


def cmd_install_addon(a) -> int:
    return run_blender(["--python", str(BLENDER_DIR / "install_addon.py")])


def cmd_open(a) -> int:
    subprocess.Popen([find_blender(), str(a.blend)], cwd=PROJECT_ROOT)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="apartment", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=None, help="path to apartment.toml (default data/apartment.toml)")
    ap.add_argument("--variants-dir", default=None, help="folder of variant TOMLs (default data/variants)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate").set_defaults(fn=cmd_validate)
    p = sub.add_parser("plan")
    p.add_argument("--out", default=None, help="default docs/plan.png, or docs/variants/<KEY>.png")
    p.add_argument("--sun", help='draw sun direction, e.g. "2026-06-21 17:00"')
    p.add_argument("--variant", help="draw this variant's furniture with ids")
    p.set_defaults(fn=cmd_plan)
    p = sub.add_parser("variant")
    p.add_argument("action", choices=["list", "new"])
    p.add_argument("key", nargs="?", help="new variant key, e.g. B")
    p.add_argument("--from", dest="source", help="copy this variant's furniture")
    p.add_argument("--name", default="", help='display name, e.g. "Scandi light"')
    p.set_defaults(fn=cmd_variant)
    p = sub.add_parser("prices")
    p.add_argument("--variant", help="furniture variant to price (default: the start variant)")
    p.add_argument("--out", default=None, help="default docs/prices/<KEY>.html")
    p.add_argument("--open", action="store_true", help="open the page in the web browser")
    p.set_defaults(fn=cmd_prices)
    p = sub.add_parser("sun")
    p.add_argument("when", help='"YYYY-MM-DD HH:MM" local time')
    p.set_defaults(fn=cmd_sun)
    p = sub.add_parser("build")
    p.add_argument("--out", default=str(BLEND))
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_build)
    for name, fn in (("render", cmd_render), ("sun-study", cmd_sun_study)):
        p = sub.add_parser(name)
        p.add_argument("--blend", default=str(BLEND))
        p.add_argument("--views", default="all", help="comma list of room ids / 'plan' / 'overview', or 'all'")
        p.add_argument("--engine", choices=["eevee", "cycles"], default="eevee")
        p.add_argument("--samples", type=int, default=64)
        p.add_argument("--res", type=int, default=1600, help="image width in px")
        p.add_argument("--variant", help="furniture variant to show (default: the one saved in the .blend)")
        p.add_argument("--lights", choices=["auto", "on", "off"], default="auto",
                       help="furniture lights; auto = on when the sun is low (evening/night)")
        if name == "render":
            p.add_argument("--time", help='"YYYY-MM-DD HH:MM" local; default = value saved in the .blend')
            p.add_argument("--no-ceiling", action="store_true", help="hide ceiling from camera (keeps its shadows)")
        else:
            p.add_argument("--date", default=date.today().isoformat())
            p.add_argument("--start", default="06:00")
            p.add_argument("--end", default="21:00")
            p.add_argument("--step", type=int, default=60, help="minutes")
        p.set_defaults(fn=fn)
    sub.add_parser("install-addon").set_defaults(fn=cmd_install_addon)
    p = sub.add_parser("open")
    p.add_argument("--blend", default=str(BLEND))
    p.set_defaults(fn=cmd_open)

    a = ap.parse_args(argv)
    if a.data:
        a.data = Path(a.data).resolve()
    if a.variants_dir:
        a.variants_dir = Path(a.variants_dir).resolve()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
