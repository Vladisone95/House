import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty


def _on_sun_change(self, context):
    from .sun import update_sun

    update_sun(context.scene)


def _on_ceiling_mode(self, context):
    from .ops import apply_ceiling_mode

    apply_ceiling_mode(context.scene)


def _on_variant(self, context):
    from .ops import apply_variant

    apply_variant(context.scene)


def _on_open_amount(self, context):
    """Dragging the slider re-applies it to every piece that is currently open."""
    from .ops import set_storage_open, visible_storage_roots

    for r in visible_storage_roots(context):
        if r.get("open", 0.0) > 0:
            set_storage_open(r, self.open_amount)


def _on_show_fronts(self, context):
    from .ops import apply_fronts_visible

    apply_fronts_visible(context)


def _on_lights(self, context):
    from .ops import apply_lights

    apply_lights(context.scene)


def _redraw_views(self, context):
    for win in context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


class APT_Settings(bpy.types.PropertyGroup):
    project_root: StringProperty(name="Project folder", subtype="DIR_PATH")

    # site (written by the build script from data/apartment.toml)
    latitude: FloatProperty(name="Latitude", default=44.365, update=_on_sun_change)
    longitude: FloatProperty(name="Longitude", default=26.124, update=_on_sun_change)
    utc_offset_standard: FloatProperty(name="UTC offset (winter)", default=2.0, update=_on_sun_change)
    plus_y_bearing: FloatProperty(name="+Y bearing", default=294.0, description="Compass bearing of the model +Y axis", update=_on_sun_change)

    # sun study
    year: IntProperty(name="Year", default=2026, min=1900, max=2100, update=_on_sun_change)
    month: IntProperty(name="Month", default=6, min=1, max=12, update=_on_sun_change)
    day: IntProperty(name="Day", default=21, min=1, max=31, update=_on_sun_change)
    hour: FloatProperty(name="Time", default=17.0, min=0.0, max=23.99, step=25, precision=2,
                        description="Local wall-clock time (summer time applied automatically)",
                        update=_on_sun_change)
    sun_scale: FloatProperty(name="Sun strength", default=1.0, min=0.0, soft_max=3.0, update=_on_sun_change)
    sky_scale: FloatProperty(name="Sky strength", default=1.0, min=0.0, soft_max=3.0, update=_on_sun_change)

    animate_day: BoolProperty(name="Animate day on timeline", default=False,
                              description="Timeline frames drive the time of day")
    anim_start: FloatProperty(name="From", default=6.0, min=0, max=24)
    anim_end: FloatProperty(name="To", default=21.0, min=0, max=24)
    anim_step_minutes: IntProperty(name="Minutes / frame", default=15, min=1, max=120)

    ceiling_mode: EnumProperty(
        name="Ceiling",
        items=[
            ("SHOWN", "Shown", "Ceiling visible"),
            ("XRAY", "Invisible, keeps shadows", "Ceiling hidden from camera but still blocks sunlight (Rendered / Material Preview)"),
            ("HIDDEN", "Removed", "Ceiling fully hidden (also removes its shadow)"),
        ],
        default="SHOWN",
        update=_on_ceiling_mode,
    )

    # furniture variants (collections under 'Furniture', built from data/variants/*.toml)
    variant: StringProperty(name="Variant", description="Key of the furniture variant shown", update=_on_variant)
    show_ids: BoolProperty(name="Show IDs", default=False, update=_redraw_views,
                           description="Show each furniture piece's id in the 3D view (give it to Claude to change that piece)")

    lights_on: BoolProperty(name="Lights on", default=True, update=_on_lights,
                            description="Switch the variant's light fixtures (ceiling lights, pendants...) on / off")

    # storage pieces: open fronts, look inside (built from [items.storage] in the variant files)
    open_amount: FloatProperty(name="Open", default=1.0, min=0.0, max=1.0, subtype="FACTOR",
                               description="How far Open swings doors / pulls drawers (1 = fully)",
                               update=_on_open_amount)
    show_fronts: BoolProperty(name="Show doors & drawer fronts", default=True, update=_on_show_fronts,
                              description="Hide all fronts to see and design the inside of every cabinet")

    # read-only info, filled by update_sun()
    info_azimuth: FloatProperty(name="Azimuth")
    info_elevation: FloatProperty(name="Elevation")
    info_utc_offset: FloatProperty(name="UTC offset")
    info_events: StringProperty(name="Events")
    info_events_key: StringProperty()


def register():
    bpy.utils.register_class(APT_Settings)
    bpy.types.Scene.apt = bpy.props.PointerProperty(type=APT_Settings)


def unregister():
    del bpy.types.Scene.apt
    bpy.utils.unregister_class(APT_Settings)
