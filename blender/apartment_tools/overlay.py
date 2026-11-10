"""Furniture id labels drawn over the 3D view (screen-space, always readable, never rendered).

Toggle: Apartment panel > Furniture > Show IDs. The selected piece is highlighted in yellow.
"""

from __future__ import annotations

import blf
import bpy
import gpu
from bpy_extras.view3d_utils import location_3d_to_region_2d
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

_handle = None
FONT = 0


def _label_anchor(obj) -> Vector:
    """Top centre of the object's world bounding box, 5 cm above it."""
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return Vector((sum(c.x for c in corners) / 8, sum(c.y for c in corners) / 8, max(c.z for c in corners) + 0.05))


def _draw() -> None:
    ctx = bpy.context
    s = getattr(ctx.scene, "apt", None)
    region, rv3d = ctx.region, ctx.region_data
    if s is None or not s.show_ids or rv3d is None:
        return
    scale = ctx.preferences.system.ui_scale
    pad = 3 * scale
    blf.size(FONT, 11 * scale)
    shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    active = ctx.active_object
    gpu.state.blend_set("ALPHA")
    for obj in ctx.view_layer.objects:
        if "furniture_id" not in obj or not obj.visible_get():
            continue
        p = location_3d_to_region_2d(region, rv3d, _label_anchor(obj))
        if p is None:  # behind the viewer
            continue
        text = obj["furniture_id"]
        w, h = blf.dimensions(FONT, text)
        x0, y0 = p.x - w / 2 - pad, p.y - pad - h * 0.25
        x1, y1 = p.x + w / 2 + pad, p.y + h + pad
        batch = batch_for_shader(shader, "TRIS", {"pos": ((x0, y0), (x1, y0), (x1, y1), (x0, y1))},
                                 indices=((0, 1, 2), (0, 2, 3)))
        selected = obj == active and obj.select_get()
        shader.bind()
        shader.uniform_float("color", (1.0, 0.82, 0.2, 0.95) if selected else (0.08, 0.08, 0.08, 0.78))
        batch.draw(shader)
        blf.position(FONT, p.x - w / 2, p.y, 0)
        blf.color(FONT, *((0, 0, 0, 1) if selected else (1, 1, 1, 1)))
        blf.draw(FONT, text)
        if obj.get("storage") and (obj.get("open", 0.0) > 0 or not s.show_fronts):
            _module_labels(obj, region, rv3d, shader, pad)
    gpu.state.blend_set("NONE")


def _module_labels(obj, region, rv3d, shader, pad) -> None:
    """m1, m2... in front of each module of an open storage piece (blue tags)."""
    for k, c in enumerate(obj.get("module_centres", []), start=1):
        p = location_3d_to_region_2d(region, rv3d, obj.matrix_world @ Vector(c))
        if p is None:
            continue
        text = f"m{k}"
        w, h = blf.dimensions(FONT, text)
        x0, y0, x1, y1 = p.x - w / 2 - pad, p.y - pad - h * 0.25, p.x + w / 2 + pad, p.y + h + pad
        batch = batch_for_shader(shader, "TRIS", {"pos": ((x0, y0), (x1, y0), (x1, y1), (x0, y1))},
                                 indices=((0, 1, 2), (0, 2, 3)))
        shader.bind()
        shader.uniform_float("color", (0.1, 0.35, 0.8, 0.9))
        batch.draw(shader)
        blf.position(FONT, p.x - w / 2, p.y, 0)
        blf.color(FONT, 1, 1, 1, 1)
        blf.draw(FONT, text)


def register() -> None:
    global _handle
    if _handle is None:
        _handle = bpy.types.SpaceView3D.draw_handler_add(_draw, (), "WINDOW", "POST_PIXEL")


def unregister() -> None:
    global _handle
    if _handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handle, "WINDOW")
        _handle = None
