"""Drive the Sun light + sky from date/time/location stored on the scene."""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta

import bpy
from mathutils import Vector

from ._core import ensure_core

SUN_OBJECT = "Sun"
SUN_STRENGTH = 6.0  # W/m2 (Blender units) at high sun - calibrated for AgX, exposure 0
SKY_STRENGTH = 0.10


def _sun_object() -> bpy.types.Object | None:
    obj = bpy.data.objects.get(SUN_OBJECT)
    return obj if obj and obj.type == "LIGHT" else None


def _sky_node(scene) -> bpy.types.Node | None:
    world = scene.world
    if not world or not world.use_nodes:
        return None
    return next((n for n in world.node_tree.nodes if n.type == "TEX_SKY"), None)


def _background_node(scene):
    world = scene.world
    if not world or not world.use_nodes:
        return None
    return next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)


def local_datetime(s) -> datetime:
    day = date(s.year, s.month, min(s.day, _days_in_month(s.year, s.month)))
    minutes = round(s.hour * 60)
    return datetime.combine(day, datetime.min.time()) + timedelta(minutes=minutes)


def _days_in_month(y: int, m: int) -> int:
    nxt = date(y + (m == 12), m % 12 + 1, 1)
    return (nxt - timedelta(days=1)).day


def update_sun(scene) -> None:
    """Recompute sun direction/intensity for ``scene.apt`` and apply it."""
    s = scene.apt
    ensure_core(s.project_root)
    from apartment_core.solar import direction_in_plan, sun_events, sun_position_local

    t = local_datetime(s)
    pos = sun_position_local(t, s.latitude, s.longitude, s.utc_offset_standard)
    d = Vector(direction_in_plan(pos, s.plus_y_bearing))

    # intensity: fade in over the first degrees above the horizon
    k = max(0.0, min(1.0, (pos.elevation + 0.5) / 6.0))
    sun = _sun_object()
    if sun:
        sun.rotation_mode = "QUATERNION"
        sun.rotation_quaternion = (-d).to_track_quat("-Z", "Y")
        sun.data.energy = SUN_STRENGTH * s.sun_scale * k
        sun.location = Vector((5.0, 6.0, 0.0)) + d * 25.0  # cosmetic: place the lamp where the sun is

    sky = _sky_node(scene)
    if sky:
        sky.sun_elevation = math.radians(max(pos.elevation, -5.0))
        # Blender sky: sun_rotation 0 = sun towards +Y, increasing clockwise (towards +X).
        # Verified empirically in Blender 5.2 (see docs/decisions/0003-sun-simulation.md)
        sky.sun_rotation = math.atan2(d.x, d.y)
    bg = _background_node(scene)
    if bg:
        twilight = max(0.03, min(1.0, (pos.elevation + 6.0) / 12.0))
        bg.inputs["Strength"].default_value = SKY_STRENGTH * s.sky_scale * twilight

    s.info_azimuth = pos.azimuth
    s.info_elevation = pos.elevation
    s.info_utc_offset = pos.utc_offset
    key = t.date().isoformat()
    if s.info_events_key != key:
        ev = sun_events(t.date(), s.latitude, s.longitude, s.utc_offset_standard)
        s.info_events = "  ".join(f"{k.replace('_', ' ')} {v:%H:%M}" for k, v in ev.items() if v)
        s.info_events_key = key


def hour_from_frame(scene, frame: int) -> float:
    s = scene.apt
    return min(s.anim_end, s.anim_start + (frame - scene.frame_start) * s.anim_step_minutes / 60.0)
