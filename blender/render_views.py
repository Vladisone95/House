"""Render camera views (and sun studies) from models/apartment.blend.

Run via:  uv run apartment render [--views living,plan] [--time "2026-12-21 12:00"] [--engine cycles]
          uv run apartment sun-study --date 2026-12-21 --views living --step 60
          uv run apartment render --variant B   (furniture variant; default = the one saved in the .blend)
Output:   renders/<label>[_<variant>]/<view>.png
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "blender"))


def ensure_addon():
    if not hasattr(bpy.types.Scene, "apt"):
        import apartment_tools

        apartment_tools.register()


def set_time(scene, when: datetime) -> None:
    s = scene.apt
    s.year, s.month, s.day = when.year, when.month, when.day
    s.hour = when.hour + when.minute / 60  # triggers update_sun


def cameras_for(spec: str) -> list[bpy.types.Object]:
    cams = [o for o in bpy.data.collections["Cameras"].objects if o.type == "CAMERA"]
    if spec == "all":
        return cams
    wanted = {v.strip() for v in spec.split(",")}
    return [c for c in cams if c.name.removeprefix("CAM_") in wanted]


def set_lights(scene, mode: str) -> None:
    """Furniture lights: on / off, or 'auto' = on when the sun is below 8 degrees (dusk, night)."""
    from apartment_tools.ops import apply_lights

    scene.apt.lights_on = mode == "on" or (mode == "auto" and scene.apt.info_elevation < 8.0)
    apply_lights(scene)


def render(scene, cam, out: Path, engine: str, samples: int, res: int, no_ceiling: bool) -> None:
    from apartment_tools.ops import apply_ceiling_mode

    scene.camera = cam
    is_top = cam.get("view") in ("plan", "overview")
    scene.apt.ceiling_mode = "XRAY" if (is_top or no_ceiling) else "SHOWN"
    apply_ceiling_mode(scene)
    for name in ("Annotations",):
        col = bpy.data.collections.get(name)
        if col:
            for o in col.objects:
                o.hide_render = cam.get("view") != "plan"
    scene.render.engine = "CYCLES" if engine == "cycles" else "BLENDER_EEVEE"
    if engine == "cycles":
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
    else:
        scene.eevee.taa_render_samples = samples
    scene.render.resolution_x = res
    scene.render.resolution_y = res if cam.get("view") == "plan" else int(res * 0.625)
    scene.render.filepath = str(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print(f"[render] {out}")


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--views", default="all")
    ap.add_argument("--engine", default="eevee")
    ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--res", type=int, default=1600)
    ap.add_argument("--time")
    ap.add_argument("--no-ceiling", action="store_true")
    ap.add_argument("--study", action="store_true")
    ap.add_argument("--date")
    ap.add_argument("--start", default="06:00")
    ap.add_argument("--end", default="21:00")
    ap.add_argument("--step", type=int, default=60)
    ap.add_argument("--variant", default="")
    ap.add_argument("--lights", choices=["auto", "on", "off"], default="auto")
    a = ap.parse_args(argv)

    ensure_addon()
    scene = bpy.context.scene
    scene.eevee.shadow_resolution_scale = 1.0  # full-quality shadows for final images (viewport uses 0.5)
    cams = cameras_for(a.views)
    if not cams:
        sys.exit(f"no cameras match {a.views!r}")
    suffix = ""
    if a.variant:
        from apartment_tools.ops import apply_variant, variant_collections

        keys = [c["variant_key"] for c in variant_collections()]
        if a.variant not in keys:
            sys.exit(f"no variant {a.variant!r} in the .blend (have {keys}) - rebuild?")
        scene.apt.variant = a.variant
        apply_variant(scene)
        suffix = f"_{a.variant}"

    if a.study:
        d = datetime.strptime(a.date, "%Y-%m-%d")
        h0, m0 = map(int, a.start.split(":"))
        h1, m1 = map(int, a.end.split(":"))
        t, end = h0 * 60 + m0, h1 * 60 + m1
        while t <= end:
            when = d.replace(hour=t // 60, minute=t % 60)
            set_time(scene, when)
            set_lights(scene, a.lights)
            for cam in cams:
                out = ROOT / "renders" / f"sun_study_{a.date}{suffix}" / cam.name.removeprefix("CAM_") / f"{when:%H%M}.png"
                render(scene, cam, out, a.engine, a.samples, a.res, a.no_ceiling)
            t += a.step
        return

    if a.time:
        set_time(scene, datetime.strptime(a.time, "%Y-%m-%d %H:%M"))
    from apartment_tools.sun import local_datetime

    set_lights(scene, a.lights)

    label = local_datetime(scene.apt).strftime("%Y-%m-%d_%H%M") + suffix
    for cam in cams:
        render(scene, cam, ROOT / "renders" / label / f"{cam.name.removeprefix('CAM_')}.png", a.engine, a.samples, a.res, a.no_ceiling)


if __name__ == "__main__":
    main()
