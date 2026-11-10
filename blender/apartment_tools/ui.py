import bpy

from .ops import (
    CAMERAS_COLLECTION,
    LABELS_COLLECTION,
    layout_of,
    piece_of,
    room_cameras,
    storage_root,
    style_group,
    variant_collections,
)


def _hhmm(h: float) -> str:
    m = round(h * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


class APT_PT_main(bpy.types.Panel):
    bl_label = "Apartment"
    bl_idname = "APT_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Apartment"

    def draw(self, context):
        s = context.scene.apt
        col = self.layout.column(align=True)
        row = col.row(align=True)
        row.operator("apt.view_plan", icon="VIEW_ORTHO")
        row.operator("apt.view_overview", icon="VIEW_PERSPECTIVE")
        col.prop(s, "ceiling_mode", text="Ceiling")
        row = col.row(align=True)
        op = row.operator("apt.toggle_collection", text="Labels", icon="FONT_DATA")
        op.collection = LABELS_COLLECTION
        op = row.operator("apt.toggle_collection", text="Floor above", icon="MOD_BUILD")
        op.collection = "Context"
        col.operator("apt.price_list", text=f"Price list ({s.variant or 'variant'})", icon="SPREADSHEET")


class APT_PT_rooms(bpy.types.Panel):
    bl_label = "Rooms (eye height 1.60 m)"
    bl_parent_id = "APT_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Apartment"

    def draw(self, context):
        cams = room_cameras()
        if not cams:
            self.layout.label(text=f"No cameras in '{CAMERAS_COLLECTION}'", icon="ERROR")
            return
        col = self.layout.column(align=True)
        for cam in cams:
            row = col.row(align=True)
            op = row.operator("apt.goto_room", text=cam.get("room_name", cam.name), icon="HOME")
            op.camera, op.walk = cam.name, False
            op = row.operator("apt.goto_room", text="", icon="MOD_DYNAMICPAINT")
            op.camera, op.walk = cam.name, True
            op = row.operator("apt.camera_view", text="", icon="OUTLINER_OB_CAMERA")
            op.camera = cam.name
        self.layout.label(text="Walk: WASD, mouse look, Q/E down/up, Tab gravity", icon="INFO")


class APT_PT_sun(bpy.types.Panel):
    bl_label = "Sun study"
    bl_parent_id = "APT_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Apartment"

    def draw(self, context):
        s = context.scene.apt
        lay = self.layout
        row = lay.row()
        row.scale_y = 1.4
        row.operator("apt.sun_well_lit", text="Well lit (brightest summer sun)", icon="LIGHT_SUN")
        row = lay.row(align=True)
        row.prop(s, "day")
        row.prop(s, "month")
        row.prop(s, "year")
        row = lay.row(align=True)
        row.prop(s, "hour", slider=True)
        row.label(text=_hhmm(s.hour))
        row = lay.row(align=True)
        for key, label in (("SPRING", "Mar 20"), ("SUMMER", "Jun 21"), ("AUTUMN", "Sep 22"), ("WINTER", "Dec 21")):
            row.operator("apt.sun_preset", text=label).preset = key
        lay.operator("apt.sun_now", icon="TIME")
        box = lay.box()
        box.label(text=f"Azimuth {s.info_azimuth:.1f}°   Elevation {s.info_elevation:.1f}°", icon="LIGHT_SUN")
        box.label(text=f"Local time UTC{s.info_utc_offset:+.0f}   {s.info_events}")
        if s.info_elevation <= 0:
            box.label(text="Sun is below the horizon", icon="ERROR")
        col = lay.column(align=True)
        col.prop(s, "sun_scale")
        col.prop(s, "sky_scale")
        lay.separator()
        col = lay.column(align=True)
        col.label(text="Day animation (scrub the timeline)")
        row = col.row(align=True)
        row.prop(s, "anim_start")
        row.prop(s, "anim_end")
        col.prop(s, "anim_step_minutes")
        row = col.row(align=True)
        row.operator("apt.sun_animation", icon="PLAY")
        row.prop(s, "animate_day", text="", icon="ANIM")
        lay.label(text="Tip: viewport shading 'Rendered' = most accurate", icon="SHADING_RENDERED")


class APT_PT_furniture(bpy.types.Panel):
    bl_label = "Furniture variants"
    bl_parent_id = "APT_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Apartment"

    def draw(self, context):
        s = context.scene.apt
        lay = self.layout
        cols = variant_collections()
        if not cols:
            lay.label(text="No variants - add data/variants/*.toml and rebuild", icon="INFO")
            return
        active = next((c for c in cols if c["variant_key"] == s.variant), cols[0])
        layouts = [c for c in cols if not c.get("style_of")]
        current_layout = layout_of(active)
        lay.label(text="Layout")
        row = lay.row(align=True)
        row.operator("apt.cycle_variant", text="", icon="TRIA_LEFT").step = -1
        flow = row.grid_flow(row_major=True, columns=min(len(layouts), 6), even_columns=True, align=True)
        for c in layouts:
            key = c["variant_key"]
            flow.operator("apt.set_variant", text=key, depress=key == current_layout).key = key
        row.operator("apt.cycle_variant", text="", icon="TRIA_RIGHT").step = 1
        group = style_group(current_layout)
        if len(group) > 1:  # this layout has colour / finish styles: pick one from the dropdown
            row = lay.row(align=True)
            row.label(text="Style", icon="COLOR")
            row.operator("apt.cycle_style", text="", icon="TRIA_LEFT").step = -1
            text = "Original" if not active.get("style_of") else active.get("variant_name", active["variant_key"])
            row.operator_menu_enum("apt.set_style", "key", text=f"{text}  ({active['variant_key']})")
            row.operator("apt.cycle_style", text="", icon="TRIA_RIGHT").step = 1
        n = sum(1 for o in active.all_objects if "furniture_id" in o)
        box = lay.box()
        box.label(text=f"{active['variant_key']}: {active.get('variant_name', '')}  ({n} pieces)", icon="OUTLINER_COLLECTION")
        if desc := active.get("description", ""):
            box.label(text=desc)
        row = lay.row(align=True)
        row.prop(s, "show_ids", toggle=True, icon="HIDE_OFF" if s.show_ids else "HIDE_ON")
        row.prop(s, "lights_on", toggle=True, icon="OUTLINER_OB_LIGHT" if s.lights_on else "LIGHT")
        obj = context.active_object
        piece = piece_of(obj)
        if piece is not None and obj.select_get():
            box = lay.box()
            box.label(text=piece["furniture_id"], icon="OBJECT_DATA")
            box.label(text=f"{piece.get('type', '')} in {piece.get('room_id', '')}")
            if note := piece.get("note", ""):
                box.label(text=note, icon="INFO")
            row = box.row(align=True)
            row.operator("apt.copy_furniture_id", icon="COPYDOWN")
            row.operator("apt.piece_colors", text="Colours...", icon="COLOR")
        else:
            lay.label(text="Click a piece to see / copy its id or change its colours", icon="RESTRICT_SELECT_OFF")
        lay.operator_menu_enum("apt.room_colors", "room", text="Room colours (floor / walls)...", icon="HOME")


class APT_PT_storage(bpy.types.Panel):
    bl_label = "Storage (open / look inside)"
    bl_parent_id = "APT_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Apartment"

    def draw(self, context):
        s = context.scene.apt
        lay = self.layout
        col = lay.column(align=True)
        row = col.row(align=True)
        op = row.operator("apt.storage_open", text="Open / close selected", icon="FILE_FOLDER")
        op.mode, op.scope = "TOGGLE", "SELECTED"
        row = col.row(align=True)
        op = row.operator("apt.storage_open", text="Open all", icon="UNLOCKED")
        op.mode, op.scope = "OPEN", "ALL"
        op = row.operator("apt.storage_open", text="Close all", icon="LOCKED")
        op.mode, op.scope = "CLOSE", "ALL"
        col.prop(s, "open_amount", slider=True)
        lay.prop(s, "show_fronts", toggle=True, icon="HIDE_OFF" if s.show_fronts else "HIDE_ON")
        obj = context.active_object
        root = storage_root(obj)
        if root is None or not obj.select_get():
            lay.label(text="Click a wardrobe / cabinet, then Open", icon="RESTRICT_SELECT_OFF")
            return
        box = lay.box()
        box.label(text=f"{root['furniture_id']}  ({root.get('modules', 0)} modules)", icon="MOD_BUILD")
        if "part_id" in obj:
            pid = obj["part_id"]
            box.label(text=f"Module: {'/'.join(pid.split('/')[:2])}", icon="MESH_GRID")
            box.label(text=f"Part: {pid}")
            row = box.row(align=True)
            row.operator("apt.copy_part_id", text="Copy module id", icon="COPYDOWN").module_only = True
            row.operator("apt.copy_part_id", text="Copy part id").module_only = False
        else:
            box.label(text="Click a door or drawer to get its module id (m1 = leftmost)")
        lay.label(text='Tell Claude e.g. "3 shelves in <module id>"', icon="INFO")


class APT_PT_site(bpy.types.Panel):
    bl_label = "Site"
    bl_parent_id = "APT_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Apartment"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        s = context.scene.apt
        col = self.layout.column(align=True)
        for p in ("latitude", "longitude", "utc_offset_standard", "plus_y_bearing", "project_root"):
            col.prop(s, p)


CLASSES = (APT_PT_main, APT_PT_rooms, APT_PT_furniture, APT_PT_storage, APT_PT_sun, APT_PT_site)
