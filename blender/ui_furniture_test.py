"""GUI test for furniture variants: id overlay + switching variants keeps the view.

Opens the real Blender UI (overlays only draw in a window), shows ids, switches variants,
asserts the viewport matrix did not change, saves screenshots and quits.

Run:  "<blender.exe>" <file with >= 2 variants>.blend --python blender/ui_furniture_test.py
      e.g. after  uv run apartment --variants-dir tests/fixtures/variants build --out <tmp>/test.blend
Output: renders/ui_furniture/*.png and a line  [furniture-ui] PASS | FAIL ...
"""

import traceback
from pathlib import Path

import bpy

OUT = Path(__file__).resolve().parents[1] / "renders" / "ui_furniture"
OUT.mkdir(parents=True, exist_ok=True)
state: dict = {"failures": []}


def _view3d():
    win = bpy.context.window_manager.windows[0]
    area = max((a for a in win.screen.areas if a.type == "VIEW_3D"), key=lambda a: a.width * a.height)
    region = next(r for r in area.regions if r.type == "WINDOW")
    return win, area, region


def _run(op, **kw):
    win, area, region = _view3d()
    with bpy.context.temp_override(window=win, area=area, region=region):
        return op(**kw)


def _shot(name: str) -> None:
    _run(bpy.ops.screen.screenshot_area, filepath=str(OUT / f"{name}.png"))
    print(f"[furniture-ui] {OUT / name}.png")


def _view_matrix():
    return _view3d()[1].spaces.active.region_3d.view_matrix.copy()


def _check(cond: bool, msg: str) -> None:
    print(f"[furniture-ui] {'ok  ' if cond else 'FAIL'} {msg}")
    if not cond:
        state["failures"].append(msg)


def _keys():
    from apartment_tools.ops import variant_collections

    return [c["variant_key"] for c in variant_collections()]


def _visible_ids():
    return sorted(o["furniture_id"] for o in bpy.context.view_layer.objects if "furniture_id" in o and o.visible_get())


def step_setup():
    keys = _keys()
    _check(len(keys) >= 2, f"at least two variants in the file ({keys})")
    s = bpy.context.scene.apt
    s.show_ids = True
    _, area, _ = _view3d()
    area.spaces.active.show_region_ui = True  # sidebar, so the panel draws (and any draw error shows)
    # tabs can't be selected from Python: re-register the panels into the (active) Tool tab
    from apartment_tools import ui

    for c in reversed(ui.CLASSES):
        bpy.utils.unregister_class(c)
    for c in ui.CLASSES:
        c.bl_category = "Tool"
        bpy.utils.register_class(c)
    _run(bpy.ops.apt.set_variant, key=keys[0])
    _run(bpy.ops.apt.view_overview)


def step_first():
    keys = _keys()
    ids = _visible_ids()
    _check(all(i.startswith(keys[0] + ".") for i in ids), f"only {keys[0]} pieces visible: {len(ids)}")
    state["view"] = _view_matrix()
    _shot(f"overview_{keys[0]}_ids")


def step_switch():
    _run(bpy.ops.apt.cycle_variant, step=1)


def step_second():
    keys = _keys()
    ids = _visible_ids()
    _check(bpy.context.scene.apt.variant == keys[1], f"cycle moved to {keys[1]}")
    _check(bool(ids) and all(i.startswith(keys[1] + ".") for i in ids), f"only {keys[1]} pieces visible: {len(ids)}")
    _check(_view_matrix() == state["view"], "view did not move when switching variant")
    _shot(f"overview_{keys[1]}_ids")


def step_style():
    """A style of a layout (C = style_of A) is in the Style dropdown, not in the layout buttons."""
    from apartment_tools.ops import _style_items, layout_of, variant_collections

    _run(bpy.ops.apt.set_variant, key="A")
    items = [i[0] for i in _style_items(None, bpy.context)]
    _check(items == ["A", "C"], f"Style dropdown of layout A lists A (original) + C: {items}")
    _run(bpy.ops.apt.set_style, key="C")
    ids = _visible_ids()
    _check(bpy.context.scene.apt.variant == "C" and bool(ids) and all(i.startswith("C.") for i in ids),
           f"style C shown: {len(ids)} pieces")
    _check(_view_matrix() == state["view"], "view did not move when switching style")
    col = next(c for c in variant_collections() if c["variant_key"] == "C")
    _check(layout_of(col) == "A", "C belongs to layout A")
    _shot("overview_style_C")
    _run(bpy.ops.apt.cycle_style, step=1)
    _check(bpy.context.scene.apt.variant == "A", "cycling styles wraps back to the original A")
    _run(bpy.ops.apt.cycle_variant, step=1)
    _check(bpy.context.scene.apt.variant == "B", "layout arrows skip the style C: A -> B")


def step_select():
    obj = next(o for o in bpy.context.view_layer.objects if "furniture_id" in o and o.visible_get())
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    _run(bpy.ops.apt.copy_furniture_id)
    _check(bpy.context.window_manager.clipboard == obj["furniture_id"], f"copied id {obj['furniture_id']}")
    _run(bpy.ops.apt.view_plan)


def step_plan():
    _shot("plan_ids_selected")


def _storage_root():
    roots = [o for o in bpy.context.view_layer.objects if o.get("storage") and o.visible_get()]
    return max(roots, key=lambda o: o.get("modules", 0)) if roots else None


def step_storage_open():
    root = _storage_root()
    _check(root is not None, "a storage piece is visible")
    if root is None:
        return
    door = next(c for c in root.children if c.get("motion") == "hinge")
    bpy.ops.object.select_all(action="DESELECT")
    door.select_set(True)
    bpy.context.view_layer.objects.active = door
    _run(bpy.ops.apt.storage_open, mode="OPEN", scope="SELECTED")
    _check(abs(door.rotation_euler.z - door["amount"]) < 1e-6, f"{door['part_id']} opened")
    _run(bpy.ops.apt.copy_part_id, module_only=True)
    cb = bpy.context.window_manager.clipboard
    _check(cb == "/".join(door["part_id"].split("/")[:2]), f"copied module id {cb}")
    _run(bpy.ops.apt.storage_open, mode="OPEN", scope="ALL")
    _run(bpy.ops.apt.view_overview)


def step_storage_shot():
    _shot("storage_open_all")
    bpy.context.scene.apt.show_fronts = False


def step_fronts_hidden():
    root = _storage_root()
    fronts = [c for c in root.children if c.get("storage_front")]
    _check(all(not c.visible_get() for c in fronts), "fronts hidden")
    _shot("storage_fronts_hidden")
    bpy.context.scene.apt.show_fronts = True
    _run(bpy.ops.apt.storage_open, mode="CLOSE", scope="ALL")
    _check(all(abs(c.rotation_euler.z) < 1e-9 for c in fronts), "closed again")
    bpy.context.scene.apt.show_ids = False
    _run(bpy.ops.apt.view_plan)


def step_plan_symbols():
    _shot("plan_doors_fixed_points")


def step_finish():
    print("[furniture-ui]", "PASS" if not state["failures"] else f"FAIL {state['failures']}")
    bpy.ops.wm.quit_blender()


STEPS = [step_setup, step_first, step_switch, step_second, step_style, step_select, step_plan, step_storage_open,
         step_storage_shot, step_fronts_hidden, step_plan_symbols, step_finish]


def _tick():
    if not STEPS:
        return None
    step = STEPS.pop(0)
    try:
        step()
    except Exception:
        traceback.print_exc()
        state["failures"].append(step.__name__)
    return 3.0


bpy.app.timers.register(_tick, first_interval=8.0)
