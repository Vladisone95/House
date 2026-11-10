"""Operators for the Apartment panel."""

from __future__ import annotations

import math
import re
from datetime import datetime

import bpy
from mathutils import Vector

CEILING_COLLECTION = "Ceiling"
LABELS_COLLECTION = "Annotations"
CAMERAS_COLLECTION = "Cameras"
FURNITURE_COLLECTION = "Furniture"


# --------------------------------------------------------------------------- helpers
def _view3d(context):
    """Return (area, region, space) of the 3D view the operator should drive."""
    area = context.area if context.area and context.area.type == "VIEW_3D" else None
    if area is None:
        area = next((a for a in context.screen.areas if a.type == "VIEW_3D"), None)
    if area is None:
        return None, None, None
    region = next(r for r in area.regions if r.type == "WINDOW")
    return area, region, area.spaces.active


def _ensure_lit_shading(space):
    """Solid mode ignores the sun - switch to Material Preview with scene lights/world."""
    sh = space.shading
    if sh.type in {"SOLID", "WIREFRAME"}:
        sh.type = "MATERIAL"
    sh.use_scene_lights = True
    sh.use_scene_world = True


def apply_ceiling_mode(scene) -> None:
    """Ceiling + 'Context' (floor above) share the mode: hidden from camera but keep casting shadows."""
    mode = scene.apt.ceiling_mode
    objs = [o for name in (CEILING_COLLECTION, "Context") if (c := bpy.data.collections.get(name)) for o in c.all_objects]
    objs += [o for o in bpy.data.objects if o.get("ceiling_skin")]  # variants' ceiling tiles (ADR 0009)
    for obj in objs:
        obj.hide_viewport = mode == "HIDDEN"
        obj.hide_render = mode == "HIDDEN"
        obj.visible_camera = mode == "SHOWN"
        obj.visible_shadow = True


def variant_collections() -> list[bpy.types.Collection]:
    root = bpy.data.collections.get(FURNITURE_COLLECTION)
    if not root:
        return []
    return sorted((c for c in root.children if "variant_key" in c), key=lambda c: _natural(c["variant_key"]))


def _natural(key: str) -> tuple:
    """V2 < V10 (not V10 < V2)."""
    return tuple(int(t) if t.isdigit() else t for t in re.findall(r"\d+|\D+", key))


def layout_of(col) -> str:
    """The layout a variant shows: its own key, or for a style variant (style_of = V1) the layout it restyles."""
    return col.get("style_of", "") or col["variant_key"]


def style_group(layout_key: str) -> list:
    """The layout variant first ('Original'), then every style of it - what the Style dropdown lists."""
    cols = variant_collections()
    return [c for c in cols if c["variant_key"] == layout_key] + [c for c in cols if c.get("style_of") == layout_key]


def _hex_to_linear(hex_color: str) -> tuple[float, float, float]:
    out = []
    for i in (1, 3, 5):
        c = int(hex_color[i : i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def apply_variant(scene) -> None:
    """Show only the active variant's furniture + its wall paint. Never touches the view/camera."""
    cols = variant_collections()
    if not cols:
        return
    keys = [c["variant_key"] for c in cols]
    key = scene.apt.variant if scene.apt.variant in keys else keys[0]
    for vl in scene.view_layers:
        for c in cols:
            if lc := _find_layer_collection(vl.layer_collection, c.name):
                # exclude (not just hide): other variants' pieces and lights leave the depsgraph,
                # so their lights cost nothing (ADR 0008)
                lc.exclude = c["variant_key"] != key
                lc.hide_viewport = False
    for c in cols:
        c.hide_render = c["variant_key"] != key
    wall = bpy.data.materials.get("MAT_wall_paint")
    if wall and "default_color" in wall:
        hex_color = cols[keys.index(key)].get("wall_color", "")
        rgb = _hex_to_linear(hex_color) if hex_color else tuple(wall["default_color"])
        bsdf = next((n for n in wall.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        wall.diffuse_color = (*rgb, 1.0)


def apply_lights(scene) -> None:
    """Light fixtures' lamps follow the 'Lights on' switch (the variant switch still hides other variants)."""
    on = scene.apt.lights_on
    for o in bpy.data.objects:
        if o.get("furniture_light"):
            o.hide_viewport = not on
            o.hide_render = not on
    for m in bpy.data.materials:  # the fixtures' diffusers stop glowing when switched off
        if m.name.startswith("MAT_furn_emit_"):
            bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if bsdf:
                bsdf.inputs["Emission Strength"].default_value = 4.0 if on else 0.0


def hide_floor_grid(screens=None) -> None:
    """Owner 2026-10-04: no X-Y floor grid / axis lines in the 3D views (they cut through the building)."""
    for screen in screens or bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                ov = area.spaces.active.overlay
                ov.show_floor = False
                ov.show_axis_x = ov.show_axis_y = ov.show_axis_z = False


def apply_start_view(scene, screens=None) -> bool:
    """Put every 3D view at the scene's start view (stored by the build from [start_view]: standing just
    inside the entrance door). Returns True if a view was set."""
    sv = scene.get("start_view")
    if not sv:
        return False
    eye, target = Vector(sv[:3]), Vector(sv[3:6])
    done = False
    for screen in screens or bpy.data.screens:
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            sp = area.spaces.active
            rv = sp.region_3d
            rv.view_perspective = "PERSP"
            rv.view_rotation = (target - eye).to_track_quat("-Z", "Y")
            rv.view_distance = 1.0
            rv.view_location = eye + rv.view_rotation @ Vector((0, 0, -1.0))
            sp.lens, sp.clip_start, sp.clip_end = 18, 0.02, 1000
            sp.shading.type = "MATERIAL"
            sp.shading.use_scene_lights = sp.shading.use_scene_world = True
            done = True
    return done


def hide_gizmos(screens=None) -> None:
    """Project rule: light / probe / camera gizmos (the circles and lines) are not drawn in 3D views."""
    for screen in screens or bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.overlay.show_extras = False


def set_labels_visible(context, visible: bool) -> None:
    lc = _find_layer_collection(context.view_layer.layer_collection, LABELS_COLLECTION)
    if lc:
        lc.hide_viewport = not visible


def room_cameras() -> list[bpy.types.Object]:
    col = bpy.data.collections.get(CAMERAS_COLLECTION)
    if not col:
        return []
    cams = [o for o in col.objects if o.type == "CAMERA" and "room_id" in o]
    return sorted(cams, key=lambda o: o.get("order", 99))


def _set_view_from_camera(space, cam: bpy.types.Object, distance: float = 1.0) -> None:
    rv3d = space.region_3d
    rot = cam.matrix_world.to_quaternion()
    forward = rot @ Vector((0, 0, -1))
    rv3d.view_perspective = "PERSP"
    rv3d.view_rotation = rot
    rv3d.view_distance = distance
    rv3d.view_location = cam.matrix_world.translation + forward * distance
    space.lens = cam.data.lens
    space.clip_start = 0.05


# --------------------------------------------------------------------------- views
class APT_OT_view_plan(bpy.types.Operator):
    """Top-down orthographic plan. The ceiling becomes invisible but still casts sun shadows"""

    bl_idname = "apt.view_plan"
    bl_label = "Top-down plan"

    def execute(self, context):
        area, region, space = _view3d(context)
        if not space:
            self.report({"ERROR"}, "No 3D viewport found")
            return {"CANCELLED"}
        context.scene.apt.ceiling_mode = "XRAY"
        set_labels_visible(context, True)
        _ensure_lit_shading(space)
        with context.temp_override(area=area, region=region):
            bpy.ops.view3d.view_axis(type="TOP")
        rv3d = space.region_3d
        rv3d.view_perspective = "ORTHO"
        plan = bpy.data.objects.get("CAM_plan")
        space.lens = 50.0  # room views use 16 mm - restore the default
        if plan:  # frame the apartment (not the far-away sun lamp)
            rv3d.view_location = (plan.location.x, plan.location.y, 0.0)
            # at lens 50 the ortho viewport shows ~1.44 x view_distance across its width;
            # 1.15 x ortho_scale leaves a margin on typical (landscape) viewports
            rv3d.view_distance = plan.data.ortho_scale * 1.15
        space.overlay.show_ortho_grid = False
        return {"FINISHED"}


class APT_OT_view_overview(bpy.types.Operator):
    """3D overview from above (ceiling invisible, shadows kept)"""

    bl_idname = "apt.view_overview"
    bl_label = "3D overview"

    def execute(self, context):
        area, region, space = _view3d(context)
        cam = bpy.data.objects.get("CAM_overview")
        if not space or not cam:
            return {"CANCELLED"}
        context.scene.apt.ceiling_mode = "XRAY"
        _ensure_lit_shading(space)
        _set_view_from_camera(space, cam, distance=12.0)
        return {"FINISHED"}


class APT_OT_toggle_collection(bpy.types.Operator):
    """Show / hide a collection in the viewport"""

    bl_idname = "apt.toggle_collection"
    bl_label = "Toggle collection"
    collection: bpy.props.StringProperty()

    def execute(self, context):
        lc = _find_layer_collection(context.view_layer.layer_collection, self.collection)
        if lc:
            lc.hide_viewport = not lc.hide_viewport
        return {"FINISHED"}


def _find_layer_collection(lc, name):
    if lc.name == name:
        return lc
    for child in lc.children:
        if found := _find_layer_collection(child, name):
            return found
    return None


# --------------------------------------------------------------------------- rooms
class APT_OT_goto_room(bpy.types.Operator):
    """Put the viewport at eye height in this room (ceiling shown)"""

    bl_idname = "apt.goto_room"
    bl_label = "Go to room"
    camera: bpy.props.StringProperty()
    walk: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        area, region, space = _view3d(context)
        cam = bpy.data.objects.get(self.camera)
        if not space or not cam:
            self.report({"ERROR"}, "Camera or viewport not found")
            return {"CANCELLED"}
        context.scene.apt.ceiling_mode = "SHOWN"
        set_labels_visible(context, False)
        _ensure_lit_shading(space)
        _set_view_from_camera(space, cam)
        if self.walk:
            with context.temp_override(area=area, region=region):
                bpy.ops.view3d.walk("INVOKE_DEFAULT")
        return {"FINISHED"}


class APT_OT_camera_render_view(bpy.types.Operator):
    """Make this room's camera the active scene camera and look through it"""

    bl_idname = "apt.camera_view"
    bl_label = "Look through camera"
    camera: bpy.props.StringProperty()

    def execute(self, context):
        cam = bpy.data.objects.get(self.camera)
        area, region, space = _view3d(context)
        if not cam or not space:
            return {"CANCELLED"}
        context.scene.camera = cam
        space.region_3d.view_perspective = "CAMERA"
        return {"FINISHED"}


# --------------------------------------------------------------------------- sun
PRESETS = {
    "SUMMER": (6, 21),
    "WINTER": (12, 21),
    "SPRING": (3, 20),
    "AUTUMN": (9, 22),
}


class APT_OT_sun_preset(bpy.types.Operator):
    """Jump to a solstice / equinox (keeps the time of day)"""

    bl_idname = "apt.sun_preset"
    bl_label = "Sun preset"
    preset: bpy.props.EnumProperty(items=[(k, k.title(), "") for k in PRESETS])

    def execute(self, context):
        s = context.scene.apt
        s.month, s.day = PRESETS[self.preset]
        return {"FINISHED"}


class APT_OT_sun_well_lit(bpy.types.Operator):
    """Summer solstice at the hour the most daylight enters (sun on both facades) - to see the rooms well"""

    bl_idname = "apt.sun_well_lit"
    bl_label = "Well lit"

    def execute(self, context):
        from ._core import ensure_core

        s = context.scene.apt
        ensure_core(s.project_root)
        from pathlib import Path

        from apartment_core import load
        from apartment_core.daylight import brightest_time

        root = Path(s.project_root) if s.project_root else Path(__file__).resolve().parents[2]
        t = brightest_time(load(root / "data" / "apartment.toml"), s.year)
        s.month, s.day = t.month, t.day
        s.hour = t.hour + t.minute / 60
        s.sun_scale, s.sky_scale = 1.0, 1.5  # a brighter sky fill so shaded corners read too
        area, region, space = _view3d(context)
        if space:
            _ensure_lit_shading(space)
        self.report({"INFO"}, f"Well lit: {t:%d %b %H:%M} - sun on both facades")
        return {"FINISHED"}


class APT_OT_sun_now(bpy.types.Operator):
    """Set date and time to now"""

    bl_idname = "apt.sun_now"
    bl_label = "Now"

    def execute(self, context):
        s = context.scene.apt
        now = datetime.now()
        s.year, s.month, s.day = now.year, now.month, now.day
        s.hour = now.hour + now.minute / 60
        return {"FINISHED"}


class APT_OT_sun_animation(bpy.types.Operator):
    """Set the timeline so each frame is one time step through the day, and turn animation on"""

    bl_idname = "apt.sun_animation"
    bl_label = "Set up day animation"

    def execute(self, context):
        sc = context.scene
        s = sc.apt
        frames = int(math.ceil((s.anim_end - s.anim_start) * 60 / s.anim_step_minutes))
        sc.frame_start = 1
        sc.frame_end = 1 + frames
        sc.frame_current = 1
        s.animate_day = True
        s.hour = s.anim_start
        return {"FINISHED"}


# --------------------------------------------------------------------------- furniture variants
class APT_OT_set_variant(bpy.types.Operator):
    """Show this furniture variant (the view stays exactly where it is)"""

    bl_idname = "apt.set_variant"
    bl_label = "Show variant"
    bl_options = {"UNDO"}
    key: bpy.props.StringProperty()

    def execute(self, context):
        context.scene.apt.variant = self.key  # update callback applies it
        return {"FINISHED"}


class APT_OT_cycle_variant(bpy.types.Operator):
    """Previous / next layout (A, DEV, V1...; styles of a layout are in the Style dropdown). The view stays put"""

    bl_idname = "apt.cycle_variant"
    bl_label = "Cycle layout"
    bl_options = {"UNDO"}
    step: bpy.props.IntProperty(default=1)

    def execute(self, context):
        cols = variant_collections()
        keys = [c["variant_key"] for c in cols if not c.get("style_of")]
        if not keys:
            return {"CANCELLED"}
        s = context.scene.apt
        cur = next((layout_of(c) for c in cols if c["variant_key"] == s.variant), keys[0])
        i = keys.index(cur) if cur in keys else 0
        s.variant = keys[(i + self.step) % len(keys)]
        return {"FINISHED"}


_STYLE_ITEMS: list = []  # Blender needs the dynamic enum strings kept alive


def _style_items(self, context):
    _STYLE_ITEMS.clear()
    s = context.scene.apt if context else None
    cols = variant_collections()
    active = next((c for c in cols if s and c["variant_key"] == s.variant), None)
    if active is None:
        return [("NONE", "-", "")]
    for c in style_group(layout_of(active)):
        key, name = c["variant_key"], c.get("variant_name", "")
        label = f"Original - {name}" if not c.get("style_of") else name
        _STYLE_ITEMS.append((key, f"{label}  ({key})", c.get("description", "")))
    return _STYLE_ITEMS or [("NONE", "-", "")]


class APT_OT_set_style(bpy.types.Operator):
    """Show another style (colours / finishes) of the same layout - furniture and view stay exactly in place"""

    bl_idname = "apt.set_style"
    bl_label = "Style"
    bl_property = "key"
    bl_options = {"UNDO"}
    key: bpy.props.EnumProperty(name="Style", items=_style_items)

    def execute(self, context):
        if self.key != "NONE":
            context.scene.apt.variant = self.key
        return {"FINISHED"}


class APT_OT_cycle_style(bpy.types.Operator):
    """Previous / next style of this layout (the view stays exactly where it is)"""

    bl_idname = "apt.cycle_style"
    bl_label = "Cycle style"
    bl_options = {"UNDO"}
    step: bpy.props.IntProperty(default=1)

    def execute(self, context):
        s = context.scene.apt
        active = next((c for c in variant_collections() if c["variant_key"] == s.variant), None)
        if active is None:
            return {"CANCELLED"}
        keys = [c["variant_key"] for c in style_group(layout_of(active))]
        if len(keys) < 2:
            return {"CANCELLED"}
        s.variant = keys[(keys.index(s.variant) + self.step) % len(keys)]
        return {"FINISHED"}


def piece_of(obj):
    """The furniture piece of an object (itself, or the parent of a door / shelf)."""
    while obj is not None and "furniture_id" not in obj:
        obj = obj.parent
    return obj


class APT_OT_copy_furniture_id(bpy.types.Operator):
    """Copy the selected piece's id to the clipboard - paste it into your message to Claude"""

    bl_idname = "apt.copy_furniture_id"
    bl_label = "Copy id"

    @classmethod
    def poll(cls, context):
        return piece_of(context.active_object) is not None

    def execute(self, context):
        fid = piece_of(context.active_object)["furniture_id"]
        context.window_manager.clipboard = fid
        self.report({"INFO"}, f"Copied {fid}")
        return {"FINISHED"}


# --------------------------------------------------------------------------- storage (open / design)
def storage_root(obj):
    """The storage piece an object belongs to (itself, or the parent of a front / fitting)."""
    while obj is not None:
        if obj.get("storage"):
            return obj
        obj = obj.parent
    return None


def set_storage_open(root, amount: float) -> None:
    """Open the fronts of one storage piece: 0 = closed, 1 = fully open (doors ~100 deg, drawers out)."""
    amount = max(0.0, min(1.0, amount))
    root["open"] = amount
    for child in root.children:
        if not child.get("storage_front"):
            continue
        px, py, pz = child["pivot"]
        a = child["amount"] * amount
        child.location = (px, py, pz)
        child.rotation_euler = (0.0, 0.0, 0.0)
        if child["motion"] == "hinge":
            child.rotation_euler.z = a
        elif child["motion"] == "flap":
            child.rotation_euler.x = a
        elif child["motion"] == "slide":
            child.location = (px, py + a, pz)


def visible_storage_roots(context) -> list:
    return [o for o in context.view_layer.objects if o.get("storage") and o.visible_get()]


def apply_fronts_visible(context) -> None:
    show = context.scene.apt.show_fronts
    for o in bpy.data.objects:
        if o.get("storage_front"):
            o.hide_viewport = not show
            o.hide_render = not show


class APT_OT_storage_open(bpy.types.Operator):
    """Open / close the doors and drawers of the selected storage pieces (or all visible ones)"""

    bl_idname = "apt.storage_open"
    bl_label = "Open storage"
    bl_options = {"UNDO"}
    mode: bpy.props.EnumProperty(items=[("TOGGLE", "Toggle", ""), ("OPEN", "Open", ""), ("CLOSE", "Close", "")])
    scope: bpy.props.EnumProperty(items=[("SELECTED", "Selected", ""), ("ALL", "All visible", "")])

    def execute(self, context):
        if self.scope == "ALL":
            roots = visible_storage_roots(context)
        else:
            roots = list({r.name: r for o in context.selected_objects if (r := storage_root(o))}.values())
        if not roots:
            self.report({"WARNING"}, "Select a wardrobe / cabinet / drawer unit first")
            return {"CANCELLED"}
        amount = context.scene.apt.open_amount
        for r in roots:
            if self.mode == "TOGGLE":
                target = 0.0 if r.get("open", 0.0) > 0 else amount
            else:
                target = amount if self.mode == "OPEN" else 0.0
            set_storage_open(r, target)
        return {"FINISHED"}


class APT_OT_copy_part_id(bpy.types.Operator):
    """Copy the selected door / drawer / shelf address (e.g. DEV.wardrobe-living-1/m2) to the clipboard"""

    bl_idname = "apt.copy_part_id"
    bl_label = "Copy module id"
    module_only: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and "part_id" in context.active_object

    def execute(self, context):
        pid = context.active_object["part_id"]
        if self.module_only:
            pid = "/".join(pid.split("/")[:2])
        context.window_manager.clipboard = pid
        self.report({"INFO"}, f"Copied {pid}")
        return {"FINISHED"}


class APT_OT_price_list(bpy.types.Operator):
    """Cost estimate (low / mid / high, lei) of fitting out + furnishing the apartment with the shown
    variant - opens docs/prices/<variant>.html in the web browser"""

    bl_idname = "apt.price_list"
    bl_label = "Price list"

    def execute(self, context):
        import webbrowser
        from pathlib import Path

        from ._core import ensure_core

        s = context.scene.apt
        ensure_core(s.project_root)
        from apartment_core import load
        from apartment_core.furniture import load_variants
        from apartment_core.pricing import write_price_list

        root = Path(s.project_root) if s.project_root else Path(__file__).resolve().parents[2]
        variants = load_variants(root / "data" / "variants")
        variant = next((v for v in variants if v.key == s.variant), variants[0] if variants else None)
        if variant is None:
            self.report({"ERROR"}, "No furniture variants in data/variants")
            return {"CANCELLED"}
        try:  # read the data fresh, so the list follows edits made since the last build
            out = write_price_list(load(root / "data" / "apartment.toml"), variant,
                                   root / "docs" / "prices" / f"{variant.key}.html")
        except (KeyError, ValueError, OSError) as exc:
            self.report({"ERROR"}, f"Price list failed: {exc}")
            return {"CANCELLED"}
        webbrowser.open(out.resolve().as_uri())
        self.report({"INFO"}, f"Price list for variant {variant.key} opened in the browser")
        return {"FINISHED"}


CLASSES = (
    APT_OT_price_list,
    APT_OT_view_plan,
    APT_OT_view_overview,
    APT_OT_toggle_collection,
    APT_OT_goto_room,
    APT_OT_camera_render_view,
    APT_OT_sun_preset,
    APT_OT_sun_well_lit,
    APT_OT_sun_now,
    APT_OT_sun_animation,
    APT_OT_set_variant,
    APT_OT_cycle_variant,
    APT_OT_set_style,
    APT_OT_cycle_style,
    APT_OT_copy_furniture_id,
    APT_OT_storage_open,
    APT_OT_copy_part_id,
)
