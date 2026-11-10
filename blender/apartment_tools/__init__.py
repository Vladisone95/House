"""Apartment Tools - viewport helpers for the apartment design project.

Sidebar (N) > Apartment:
  * top-down plan / 3D overview, ceiling modes, labels
  * jump to / walk through each room at eye height
  * furniture variants: switch without moving the view, id labels, copy id of the selection
  * storage: open doors / drawers, hide fronts to look inside, copy module ids (m1, m2...)
  * price list: fit-out + furniture cost estimate of the shown variant (opens in the browser)
  * sun study: date + time at the real location and orientation, day animation
"""

bl_info = {
    "name": "Apartment Tools",
    "author": "apartment project",
    "version": (0, 4, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Apartment",
    "description": "Plan / walk-through / sun-study tools for the apartment model",
    "category": "3D View",
}

import bpy
from bpy.app.handlers import persistent

from . import colors, ops, overlay, props, ui


@persistent
def _on_frame_change(scene, depsgraph=None):
    s = getattr(scene, "apt", None)
    if s is None or not s.animate_day:
        return
    from .sun import hour_from_frame

    h = hour_from_frame(scene, scene.frame_current)
    if abs(s.hour - h) > 1e-6:
        s.hour = h  # triggers update_sun


@persistent
def _on_load(_dummy=None):
    for scene in bpy.data.scenes:
        if getattr(scene, "apt", None) and bpy.data.objects.get("Sun"):
            try:
                from .sun import update_sun

                update_sun(scene)
                ops.apply_ceiling_mode(scene)
                ops.apply_variant(scene)
                ops.apply_lights(scene)
                ops.hide_gizmos()
                ops.hide_floor_grid()
            except Exception as exc:  # never break file loading
                print("[apartment_tools] sun update failed:", exc)
    # the window's own screen is restored after load_post: set the start view a moment later
    if bpy.data.scenes and bpy.data.scenes[0].get("start_view"):
        # after the window's screen and the add-on's own view restore: once soon, once again a bit later
        bpy.app.timers.register(_start_view_later, first_interval=0.8)
        bpy.app.timers.register(_start_view_later, first_interval=2.5)


def _start_view_later():
    try:
        scene = bpy.context.window.scene if bpy.context.window else bpy.data.scenes[0]
        screens = [w.screen for w in bpy.context.window_manager.windows] or None
        ops.apply_start_view(scene, screens)
        ops.hide_floor_grid(screens)
    except Exception as exc:  # never break file loading
        print("[apartment_tools] start view failed:", exc)
    return None  # run once


def register():
    props.register()
    for c in ops.CLASSES + colors.CLASSES + ui.CLASSES:
        bpy.utils.register_class(c)
    overlay.register()
    bpy.app.handlers.frame_change_post.append(_on_frame_change)
    bpy.app.handlers.load_post.append(_on_load)


def unregister():
    for h, fn in ((bpy.app.handlers.frame_change_post, _on_frame_change), (bpy.app.handlers.load_post, _on_load)):
        if fn in h:
            h.remove(fn)
    overlay.unregister()
    for c in reversed(ops.CLASSES + colors.CLASSES + ui.CLASSES):
        bpy.utils.unregister_class(c)
    props.unregister()
