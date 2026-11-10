"""GUI smoke test for the Apartment add-on.

Opens the real Blender UI, runs the panel operators (plan view, go-to-room, winter sun),
saves viewport screenshots to renders/ui_smoke/ and quits.

Run:  "<blender.exe>" models/apartment.blend --python blender/ui_smoke_test.py
"""

import traceback
from pathlib import Path

import bpy

OUT = Path(bpy.data.filepath).resolve().parents[1] / "renders" / "ui_smoke"
OUT.mkdir(parents=True, exist_ok=True)


def _view3d():
    win = bpy.context.window_manager.windows[0]
    area = max((a for a in win.screen.areas if a.type == "VIEW_3D"), key=lambda a: a.width * a.height)
    region = next(r for r in area.regions if r.type == "WINDOW")
    return win, area, region


def _run(op, **kw):
    win, area, region = _view3d()
    with bpy.context.temp_override(window=win, area=area, region=region):
        op(**kw)


def _shot(name: str) -> None:
    _run(bpy.ops.screen.screenshot_area, filepath=str(OUT / f"{name}.png"))
    print(f"[smoke] {OUT / name}.png")


def _winter():
    s = bpy.context.scene.apt
    s.month, s.day, s.hour = 12, 21, 13.0
    _run(bpy.ops.apt.view_plan)


STEPS = [
    lambda: _run(bpy.ops.apt.view_plan),
    lambda: _shot("plan_summer_1700"),
    lambda: _run(bpy.ops.apt.goto_room, camera="CAM_living"),
    lambda: _shot("living_eye_level"),
    _winter,
    lambda: _shot("plan_winter_1300"),
    lambda: bpy.ops.wm.quit_blender(),
]


def _tick():
    if not STEPS:
        return None
    step = STEPS.pop(0)
    try:
        step()
    except Exception:
        traceback.print_exc()
        print("[smoke] FAILED step")
    return 4.0


bpy.app.timers.register(_tick, first_interval=8.0)
