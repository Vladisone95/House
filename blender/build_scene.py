"""Generate models/apartment.blend from data/apartment.toml.

Run via:  uv run apartment build
   (=  blender -b --factory-startup --python blender/build_scene.py -- --out models/apartment.blend)

Everything in the output file is regenerated - never hand-edit generated objects;
change data/apartment.toml (or this script) and rebuild.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "blender"))

from apartment_core import load  # noqa: E402
from apartment_core.furniture import (  # noqa: E402
    Part,
    apron_box,
    casts_shadow,
    ceiling_mounted,
    is_light,
    item_parts,
    light_cutoff,
    light_of,
    light_source_pos,
    load_variants,
    merge_variant_finishes,
    recolored_parts,
    shift_color,
    storage_layout,
    tinted_finish,
    track_heads,
)
from apartment_core.geometry import (  # noqa: E402
    cladding_walls,
    door_swing,
    inset_rectilinear,
    inward_normals,
    polygon_area,
    polygon_centroid,
    scatter_trees,
    wall_boxes,
    walled_edges,
)

# fixed service points on the plan (same hues as plan2d.POINT_COLORS, linear)
POINT_COLORS = {"water": (0.0, 0.18, 0.55), "wc": (0.15, 0.07, 0.05), "washer": (0.0, 0.25, 0.2),
                "hood": (0.86, 0.15, 0.0), "shower": (0.0, 0.31, 0.38), "other": (0.06, 0.1, 0.12)}
EYE_HEIGHT = 1.60
LOOK_HEIGHT = 1.35
ROOM_LENS = 16.0  # mm, full-frame equivalent - wide interior view


# =============================================================================
#  scene / collections
# =============================================================================
def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.length_unit = "METERS"
    sc.unit_settings.scale_length = 1.0


def collection(name: str, parent: bpy.types.Collection | None = None) -> bpy.types.Collection:
    col = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(col)
    return col


def link(obj: bpy.types.Object, col: bpy.types.Collection) -> bpy.types.Object:
    col.objects.link(obj)
    return obj


# =============================================================================
#  materials
# =============================================================================
def principled(name: str, color, roughness=0.6, **kw) -> bpy.types.Material:
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    for k, v in kw.items():
        bsdf.inputs[k].default_value = v
    m.diffuse_color = (*color, 1.0)  # solid-mode colour
    return m


def wood_material() -> bpy.types.Material:
    """Oak plank floor: brick texture as planks (1.2 x 0.19 m) with per-plank tone variation."""
    m = principled("MAT_floor_wood", (0.45, 0.30, 0.17), roughness=0.45)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset, brick.squash = 0.37, 1.0
    brick.inputs["Color1"].default_value = (0.50, 0.34, 0.19, 1)
    brick.inputs["Color2"].default_value = (0.40, 0.26, 0.14, 1)
    brick.inputs["Mortar"].default_value = (0.22, 0.14, 0.08, 1)
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.002
    brick.inputs["Brick Width"].default_value = 1.2
    brick.inputs["Row Height"].default_value = 0.19
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 40.0
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.25
    nt.links.new(coord.outputs["Object"], brick.inputs["Vector"])
    nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], mix.inputs["A"])
    nt.links.new(noise.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    return m


def finish_material(f, vertical: bool = False) -> bpy.types.Material:
    """Surface from a [finishes] entry: parquet planks (staggered, two tones, grain), tiles (grid, speckle)
    or stone slabs (grid, soft clouding / veins).

    Brick texture on object coordinates (floors / wall tiles sit at the world origin, so sizes are true
    metres); ``vertical`` maps (x + y, z) for wall tiles, so either wall direction gets true-size slabs.
    The joint mask also drives a small bump so the gaps read in grazing light.
    """
    m = principled(f"MAT_{'wall' if vertical else 'floor'}_{f.name}", srgb_to_linear(f.color), roughness=f.roughness)
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    if f.kind == "parquet" and f.direction == "y" and not vertical:
        mapping.inputs["Rotation"].default_value[2] = math.pi / 2
    if vertical:  # wall plane -> (along the wall, up)
        sep, add, comb = (nt.nodes.new(t) for t in ("ShaderNodeSeparateXYZ", "ShaderNodeMath", "ShaderNodeCombineXYZ"))
        nt.links.new(coord.outputs["Object"], sep.inputs[0])
        nt.links.new(sep.outputs[0], add.inputs[0])
        nt.links.new(sep.outputs[1], add.inputs[1])
        nt.links.new(add.outputs[0], comb.inputs[0])
        nt.links.new(sep.outputs[2], comb.inputs[1])
        nt.links.new(comb.outputs[0], mapping.inputs["Vector"])
    else:
        nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset, brick.offset_frequency = (0.37, 1) if f.kind == "parquet" else (0.0, 1)
    brick.squash, brick.squash_frequency = 1.0, 1
    brick.inputs["Color1"].default_value = (*srgb_to_linear(f.color), 1)
    brick.inputs["Color2"].default_value = (*srgb_to_linear(f.color2 if f.kind == "parquet" else f.color, 0.0), 1)
    brick.inputs["Mortar"].default_value = (*srgb_to_linear(f.joint_color), 1)
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = f.joint
    brick.inputs["Mortar Smooth"].default_value = 0.0
    brick.inputs["Bias"].default_value = 0.0
    brick.inputs["Brick Width"].default_value = f.size[0]
    brick.inputs["Row Height"].default_value = f.size[1]
    nt.links.new(mapping.outputs["Vector"], brick.inputs["Vector"])
    color_out = brick.outputs["Color"]
    if f.kind == "parquet":  # wood grain: noise stretched along the planks, multiplied in
        stretch = nt.nodes.new("ShaderNodeMapping")
        stretch.inputs["Scale"].default_value = (1.5, 40.0, 1.0)
        nt.links.new(mapping.outputs["Vector"], stretch.inputs["Vector"])
        grain = nt.nodes.new("ShaderNodeTexNoise")
        grain.inputs["Scale"].default_value = 3.0
        grain.inputs["Detail"].default_value = 6.0
        nt.links.new(stretch.outputs["Vector"], grain.inputs["Vector"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
        mix.inputs["Factor"].default_value = 0.35
        nt.links.new(color_out, mix.inputs["A"])
        nt.links.new(grain.outputs["Color"], mix.inputs["B"])
        color_out = mix.outputs["Result"]
    elif f.kind == "stone":  # soft clouds + veins of color2 across each slab, grout from the brick mask
        cloud = nt.nodes.new("ShaderNodeTexNoise")
        cloud.inputs["Scale"].default_value = 2.2
        cloud.inputs["Detail"].default_value = 10.0
        cloud.inputs["Roughness"].default_value = 0.62
        cloud.inputs["Distortion"].default_value = 1.4
        nt.links.new(mapping.outputs["Vector"], cloud.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        lo, hi = ramp.color_ramp.elements
        lo.position, hi.position = 0.38, 0.78
        lo.color, hi.color = (*srgb_to_linear(f.color), 1), (*srgb_to_linear(f.color2), 1)
        nt.links.new(cloud.outputs["Fac"], ramp.inputs["Fac"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(brick.outputs["Fac"], mix.inputs["Factor"])
        nt.links.new(ramp.outputs["Color"], mix.inputs["A"])
        mix.inputs["B"].default_value = (*srgb_to_linear(f.joint_color), 1)
        color_out = mix.outputs["Result"]
    elif f.kind == "marble":  # Calacatta-like: warm clouded white, broken gold veins, faint grey hairlines
        color_out = _marble_color(nt, mapping.outputs["Vector"], f, brick.outputs["Fac"])
    elif f.kind == "ripple":  # sculpted sand-dune relief: soft horizontal ripples, monochrome, with a real bump
        color_out, height = _ripple(nt, mapping.outputs["Vector"], f)
        brick.inputs["Mortar Size"].default_value = 0.0
    elif f.kind == "chevron":  # wood-look panel mural: oak grain, panel seams, groups of fine grooves in V's
        color_out = _chevron_color(nt, mapping.outputs["Vector"], f)
        brick.inputs["Mortar Size"].default_value = 0.0
    elif f.kind == "watercolor":  # painted sky mural: soft layered clouds, color2 washes into color + a blush
        color_out = _watercolor_color(nt, mapping.outputs["Vector"], f)
        brick.inputs["Mortar Size"].default_value = 0.0
    elif f.kind == "mural":  # one continuous wallpaper mural: flowing diagonal waves (poured agate look), no seams
        color_out = _mural_color(nt, mapping.outputs["Vector"], f)
        brick.inputs["Mortar Size"].default_value = 0.0
    else:  # speckles: fine noise thresholded into flecks of color2 (not in the grout)
        speck = nt.nodes.new("ShaderNodeTexNoise")
        speck.inputs["Scale"].default_value = 220.0
        speck.inputs["Detail"].default_value = 2.0
        nt.links.new(mapping.outputs["Vector"], speck.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[1].position = 0.60, 0.66
        nt.links.new(speck.outputs["Fac"], ramp.inputs["Fac"])
        not_joint = nt.nodes.new("ShaderNodeMath")
        not_joint.operation = "SUBTRACT"
        not_joint.inputs[0].default_value = 1.0
        nt.links.new(brick.outputs["Fac"], not_joint.inputs[1])
        fac = nt.nodes.new("ShaderNodeMath")
        fac.operation = "MULTIPLY"
        nt.links.new(ramp.outputs["Color"], fac.inputs[0])
        nt.links.new(not_joint.outputs["Value"], fac.inputs[1])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(fac.outputs["Value"], mix.inputs["Factor"])
        nt.links.new(color_out, mix.inputs["A"])
        mix.inputs["B"].default_value = (*srgb_to_linear(f.color2), 1)
        color_out = mix.outputs["Result"]
    nt.links.new(color_out, bsdf.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.invert = True
    bump.inputs["Strength"].default_value = 0.25
    bump.inputs["Distance"].default_value = 0.001
    if f.kind == "ripple":  # relief from the ripple field instead of the tile joints
        bump.invert, bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = False, 0.6, 0.02
        nt.links.new(height, bump.inputs["Height"])
    else:
        nt.links.new(brick.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    m.diffuse_color = (*srgb_to_linear(f.color), 1.0)
    return m


def build_materials(finishes=None) -> dict[str, bpy.types.Material]:
    # thin glazing: alpha-blended (reliable in EEVEE + Cycles); shadows disabled per object.
    # Very clear (owner 2026-10-04: "more transparent") - the frames show where the glass is.
    glass = principled("MAT_glass", (0.93, 0.96, 0.98), roughness=0.0, Alpha=0.04)
    rail = principled("MAT_railing_glass", (0.85, 0.9, 0.92), roughness=0.02, Alpha=0.12)
    for m in (glass, rail):
        m.surface_render_method = "BLENDED"
    label = principled("MAT_label", (0.05, 0.05, 0.05), roughness=1.0)
    north = principled("MAT_north_arrow", (0.75, 0.05, 0.05), roughness=1.0)

    def flat(name, color, strength=1.0):  # self-lit plan graphics: same look at any sun time
        m = principled(name, (0, 0, 0), roughness=1.0, **{"Emission Color": (*color, 1.0), "Emission Strength": strength})
        m.diffuse_color = (*color, 1.0)
        return m

    floors = {name: finish_material(f) for name, f in (finishes or {}).items()}
    return {
        "plan_cut": flat("MAT_plan_cut", (1.0, 1.0, 1.0), 1.2),
        "plan_window": flat("MAT_plan_window", (0.02, 0.25, 0.8)),
        "plan_door": flat("MAT_plan_door", (0.85, 0.03, 0.03)),
        "plan_door_fixed": flat("MAT_plan_door_fixed", (0.35, 0.0, 0.0)),
        **{f"point_{k}": flat(f"MAT_point_{k}", c, 2.5) for k, c in POINT_COLORS.items()},
        "wall": principled("MAT_wall_paint", (0.85, 0.84, 0.81), roughness=0.85),
        "slab": principled("MAT_concrete", (0.55, 0.55, 0.53), roughness=0.9),
        "ceiling": principled("MAT_ceiling_paint", (0.9, 0.9, 0.89), roughness=0.9),
        "wood": wood_material(),
        "tiles": principled("MAT_floor_tiles", (0.78, 0.74, 0.66), roughness=0.35),
        "outdoor_tiles": principled("MAT_balcony_tiles", (0.45, 0.44, 0.42), roughness=0.7),
        "default": principled("MAT_floor_default", (0.7, 0.7, 0.7)),
        "frame": principled("MAT_window_frame", (0.06, 0.06, 0.07), roughness=0.4),
        "metal": principled("MAT_railing_metal", (0.08, 0.08, 0.08), roughness=0.35, Metallic=1.0),
        "glass": glass,
        "railing_glass": rail,
        "label": label,
        "north": north,
        **floors,  # [finishes] override the built-in wood / tiles
    }


# =============================================================================
#  mesh helpers
# =============================================================================
def boxes_object(name: str, boxes, material, col, origin=(0.0, 0.0, 0.0)) -> bpy.types.Object:
    """Boxes in world coordinates; ``origin`` = object origin (object-space textures start there)."""
    bm = bmesh.new()
    ox, oy, oz = origin
    for x1, y1, z1, x2, y2, z2 in ((b[0] - ox, b[1] - oy, b[2] - oz, b[3] - ox, b[4] - oy, b[5] - oz) for b in boxes):
        res = bmesh.ops.create_cube(bm, size=1.0)
        verts = res["verts"]
        bmesh.ops.scale(bm, vec=(x2 - x1, y2 - y1, z2 - z1), verts=verts)
        bmesh.ops.translate(bm, vec=((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2), verts=verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material)
    obj = link(bpy.data.objects.new(name, me), col)
    obj.location = origin
    return obj


def polygon_object(name: str, poly, z: float, material, col, origin=(0.0, 0.0)) -> bpy.types.Object:
    """Flat polygon at height z; ``origin`` = object origin in x/y (object-space textures start there)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x - origin[0], y - origin[1], 0.0) for x, y in poly], [], [list(range(len(poly)))])
    me.materials.append(material)
    obj = link(bpy.data.objects.new(name, me), col)
    obj.location = (origin[0], origin[1], z)
    return obj


def slab_from_cells(name: str, cells, z_top: float, thickness: float, material, col) -> bpy.types.Object:
    """Merge grid cells into one clean slab (single n-gon top) and give it thickness downward."""
    bm = bmesh.new()
    for x1, y1, x2, y2 in cells:
        vs = [bm.verts.new((x, y, z_top)) for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2))]
        bm.faces.new(vs)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts, edges=bm.edges)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material)
    obj = link(bpy.data.objects.new(name, me), col)
    mod = obj.modifiers.new("thickness", "SOLIDIFY")
    mod.thickness = abs(thickness)  # sign = direction: > 0 grows down (floor slab), < 0 grows up (ceiling)
    mod.offset = -1.0 if thickness > 0 else 1.0
    mod.use_even_offset = True
    return obj


def text_object(name: str, body: str, loc, size: float, material, col, rot_z: float = 0.0) -> bpy.types.Object:
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.materials.append(material)
    obj = link(bpy.data.objects.new(name, cu), col)
    obj.location = loc
    obj.rotation_euler.z = rot_z
    obj.hide_render = True
    return obj


# =============================================================================
#  builders
# =============================================================================
def _vein_mask(nt, vector, scale: float, width: float, seed: float, breakup: float):
    """Thin meandering lines: where a stretched, distorted noise crosses 0.5 (|n - 0.5| < width), optionally
    broken into fragments by a second noise. Returns a 0..1 mask socket (1 = vein)."""
    warp = nt.nodes.new("ShaderNodeMapping")  # diagonal, stretched along the vein direction
    warp.inputs["Location"].default_value = (seed, seed * 1.7, seed * 0.3)
    warp.inputs["Rotation"].default_value[2] = 0.55
    warp.inputs["Scale"].default_value = (1.0, 0.32, 1.0)
    nt.links.new(vector, warp.inputs["Vector"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 9.0
    noise.inputs["Roughness"].default_value = 0.58
    noise.inputs["Distortion"].default_value = 0.35
    nt.links.new(warp.outputs["Vector"], noise.inputs["Vector"])
    off = nt.nodes.new("ShaderNodeMath")
    off.operation = "SUBTRACT"
    off.inputs[1].default_value = 0.5
    nt.links.new(noise.outputs["Fac"], off.inputs[0])
    dist = nt.nodes.new("ShaderNodeMath")
    dist.operation = "ABSOLUTE"
    nt.links.new(off.outputs[0], dist.inputs[0])
    line = nt.nodes.new("ShaderNodeMapRange")  # 1 on the line, fading to 0 at `width`
    line.inputs["From Min"].default_value = width * 0.55  # crisp edge
    line.inputs["From Max"].default_value = width
    line.inputs["To Min"].default_value = 1.0
    line.inputs["To Max"].default_value = 0.0
    nt.links.new(dist.outputs[0], line.inputs["Value"])
    if not breakup:
        return line.outputs["Result"]
    frag = nt.nodes.new("ShaderNodeTexNoise")  # patches where the vein shows / widens (blotchy gold)
    frag.inputs["Scale"].default_value = scale * 2.6
    frag.inputs["Detail"].default_value = 4.0
    nt.links.new(warp.outputs["Vector"], frag.inputs["Vector"])
    keep = nt.nodes.new("ShaderNodeMapRange")
    keep.inputs["From Min"].default_value = 0.5 - breakup
    keep.inputs["From Max"].default_value = 0.5 + breakup
    nt.links.new(frag.outputs["Fac"], keep.inputs["Value"])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.use_clamp = True
    nt.links.new(line.outputs["Result"], mul.inputs[0])
    nt.links.new(keep.outputs["Result"], mul.inputs[1])
    return mul.outputs[0]


def _rel(f, hx: str, ref: str, ref2: str) -> str:
    """A shader's fixed tint ``hx`` (tuned for the original finish colours ``ref`` / ``ref2``) moved with the
    finish's own colours: shifted from whichever reference it is closest to - recoloured wallpapers keep their
    shading instead of falling back to the original palette."""
    def dist(a, b):
        return sum((int(a[i:i + 2], 16) - int(b[i:i + 2], 16)) ** 2 for i in (1, 3, 5))

    if dist(hx, ref) <= dist(hx, ref2):
        return shift_color(f.color, ref, hx)
    return shift_color(f.color2, ref2, hx)


def _ripple(nt, vector, f):
    """Ripple (Mourals): horizontal dune ridges (distorted wave bands along the height), ramped light -> shadow so
    every ridge has a lit face and a soft shadow line. Returns (colour socket, height socket for the bump)."""
    m = nt.nodes.new("ShaderNodeMapping")
    m.inputs["Rotation"].default_value[2] = 0.06
    m.inputs["Scale"].default_value = (0.45, 2.4, 1.0)
    nt.links.new(vector, m.inputs["Vector"])
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type, wave.bands_direction, wave.wave_profile = "BANDS", "Y", "SAW"
    wave.inputs["Scale"].default_value = 1.6
    wave.inputs["Distortion"].default_value = 2.8
    wave.inputs["Detail"].default_value = 2.0
    wave.inputs["Detail Scale"].default_value = 0.6
    nt.links.new(m.outputs["Vector"], wave.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    ref = ("#ece6dc", "#d6ccbd")  # the Ripple wallpaper the tints were tuned on
    stops = ((0.0, _rel(f, "#cbbfae", *ref)), (0.1, f.color), (0.7, _rel(f, "#e4dccf", *ref)), (1.0, f.color2))
    while len(els) < len(stops):
        els.new(0.5)
    for el, (pos, hx) in zip(els, stops, strict=True):
        el.position, el.color = pos, (*srgb_to_linear(hx), 1)
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    return ramp.outputs["Color"], wave.outputs["Fac"]


def _chevron_color(nt, vector, f):
    """Madera-like: x = along the wall, y = up. c = |fract(x / P) - 0.5| * P + 0.9 * y makes V-shaped diagonals;
    fine dark grooves where fract(c / 0.04) is small, only inside every other band (fract(c / 0.7) < 0.42);
    vertical panel seams every 0.6 m; oak colour with a vertical grain."""
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(vector, sep.inputs[0])

    def math(op, a, b=None, clamp=False):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation, n.use_clamp = op, clamp
        for i, val in enumerate((a, b)):
            if val is None:
                continue
            if isinstance(val, (int, float)):
                n.inputs[i].default_value = val
            else:
                nt.links.new(val, n.inputs[i])
        return n.outputs[0]

    x, y = sep.outputs[0], sep.outputs[1]
    period = 1.2
    v = math("MULTIPLY", math("ABSOLUTE", math("SUBTRACT", math("FRACT", math("DIVIDE", x, period)), 0.5)), period)
    c = math("ADD", v, math("MULTIPLY", y, 0.9))
    groove = math("LESS_THAN", math("FRACT", math("DIVIDE", c, 0.04)), 0.14)
    band = math("LESS_THAN", math("FRACT", math("DIVIDE", c, 0.7)), 0.42)
    seam = math("LESS_THAN", math("FRACT", math("DIVIDE", x, 0.6)), 0.006)
    dark = math("MAXIMUM", math("MULTIPLY", groove, band), seam)
    grain = nt.nodes.new("ShaderNodeTexNoise")  # vertical oak grain
    grain.inputs["Scale"].default_value = 6.0
    grain.inputs["Detail"].default_value = 8.0
    stretch = nt.nodes.new("ShaderNodeMapping")
    stretch.inputs["Scale"].default_value = (12.0, 0.6, 1.0)
    nt.links.new(vector, stretch.inputs["Vector"])
    nt.links.new(stretch.outputs["Vector"], grain.inputs["Vector"])
    wood = nt.nodes.new("ShaderNodeMix")
    wood.data_type = "RGBA"
    nt.links.new(grain.outputs["Fac"], wood.inputs["Factor"])
    wood.inputs["A"].default_value = (*srgb_to_linear(f.color), 1)
    wood.inputs["B"].default_value = (*srgb_to_linear(f.color2), 1)
    out = nt.nodes.new("ShaderNodeMix")
    out.data_type = "RGBA"
    nt.links.new(dark, out.inputs["Factor"])
    nt.links.new(wood.outputs["Result"], out.inputs["A"])
    out.inputs["B"].default_value = (*srgb_to_linear(f.joint_color), 1)
    return out.outputs["Result"]


def _watercolor_color(nt, vector, f):
    """Watercolour clouds: two soft noises (large drifts + smaller billows) ramped blue -> cream -> blush."""
    def noise(scale, detail, rough, distortion):
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough
        n.inputs["Distortion"].default_value = distortion
        nt.links.new(vector, n.inputs["Vector"])
        return n
    big, small = noise(0.35, 4.0, 0.55, 0.6), noise(1.4, 6.0, 0.6, 0.3)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "FLOAT"
    mix.inputs["Factor"].default_value = 0.35
    nt.links.new(big.outputs["Fac"], mix.inputs["A"])
    nt.links.new(small.outputs["Fac"], mix.inputs["B"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    ref = ("#ede6dc", "#7fa3ad")  # Delicate Blues, the mural the tints were tuned on
    stops = ((0.25, f.color2), (0.42, _rel(f, "#a9c2c8", *ref)), (0.52, f.color), (0.62, _rel(f, "#f3ece4", *ref)),
             (0.74, _rel(f, "#e6cfbd", *ref)))
    while len(els) < len(stops):
        els.new(0.5)
    for el, (pos, hx) in zip(els, stops, strict=True):
        el.position, el.color = pos, (*srgb_to_linear(hx), 1)
    nt.links.new(mix.outputs["Result"], ramp.inputs["Fac"])
    return ramp.outputs["Color"]


def _mural_color(nt, vector, f):
    """Flowing bands: distorted wave texture ramped cream -> sand -> caramel, then strand families that each
    run in their own direction through their own warped (domain-distorted) space, so they cross and swirl
    instead of running parallel."""
    def flow(rot, scale, warp_scale, warp_amp, seed):
        """Mapped vector rotated by `rot`, bent by a low-frequency noise (curving, non-parallel strands)."""
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = warp_scale
        n.inputs["Detail"].default_value = 2.0
        off = nt.nodes.new("ShaderNodeMapping")
        off.inputs["Location"].default_value = (seed, seed * 1.3, seed * 0.7)
        nt.links.new(vector, off.inputs["Vector"])
        nt.links.new(off.outputs["Vector"], n.inputs["Vector"])
        centred = nt.nodes.new("ShaderNodeVectorMath")
        centred.operation = "SUBTRACT"
        centred.inputs[1].default_value = (0.5, 0.5, 0.5)
        nt.links.new(n.outputs["Color"], centred.inputs[0])
        amp = nt.nodes.new("ShaderNodeVectorMath")
        amp.operation = "SCALE"
        amp.inputs["Scale"].default_value = warp_amp
        nt.links.new(centred.outputs[0], amp.inputs[0])
        bent = nt.nodes.new("ShaderNodeVectorMath")
        bent.operation = "ADD"
        nt.links.new(vector, bent.inputs[0])
        nt.links.new(amp.outputs[0], bent.inputs[1])
        m = nt.nodes.new("ShaderNodeMapping")
        m.inputs["Rotation"].default_value[2] = rot
        m.inputs["Scale"].default_value = scale
        nt.links.new(bent.outputs[0], m.inputs["Vector"])
        return m.outputs["Vector"]

    tilt = flow(-0.6, (0.35, 1.0, 1.0), 0.32, 3.2, 0.0)  # broad sweeps down from the top left, gently bent
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type, wave.bands_direction = "BANDS", "Y"
    wave.inputs["Scale"].default_value = 0.5
    wave.inputs["Distortion"].default_value = 3.5
    wave.inputs["Detail"].default_value = 3.0
    wave.inputs["Detail Scale"].default_value = 0.8
    nt.links.new(tilt, wave.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    ref = ("#efe6d8", "#c9a57e")  # Suave, the mural the tints were tuned on
    stops = ((0.0, f.color), (0.3, _rel(f, "#ead9c3", *ref)), (0.42, f.color2), (0.5, _rel(f, "#a87f58", *ref)),
             (0.6, _rel(f, "#e3cfb4", *ref)), (0.8, f.color), (1.0, _rel(f, "#dcc6a8", *ref)))
    while len(els) < len(stops):
        els.new(0.5)
    for el, (pos, hx) in zip(els, stops, strict=True):
        el.position, el.color = pos, (*srgb_to_linear(hx), 1)
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    out = ramp.outputs["Color"]

    def ramp_of(fac, stops_):
        r = nt.nodes.new("ShaderNodeValToRGB")
        e = r.color_ramp.elements
        while len(e) < len(stops_):
            e.new(0.5)
        for el_, (pos_, val) in zip(e, stops_, strict=True):
            el_.position, el_.color = pos_, (*((val,) * 3 if isinstance(val, float) else srgb_to_linear(val)), 1)
        nt.links.new(fac, r.inputs["Fac"])
        return r.outputs["Color"]

    def layer(base, color, mask, strength):
        amt = nt.nodes.new("ShaderNodeMath")
        amt.operation = "MULTIPLY"
        amt.inputs[1].default_value = strength
        nt.links.new(mask, amt.inputs[0])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(amt.outputs[0], mix.inputs["Factor"])
        nt.links.new(base, mix.inputs["A"])
        mix.inputs["B"].default_value = (*srgb_to_linear(color), 1)
        return mix.outputs["Result"]

    def strands(vec, scale, distortion):
        w_ = nt.nodes.new("ShaderNodeTexWave")
        w_.wave_type, w_.bands_direction = "BANDS", "Y"
        w_.inputs["Scale"].default_value = scale
        w_.inputs["Distortion"].default_value = distortion
        w_.inputs["Detail"].default_value = 3.0
        w_.inputs["Detail Scale"].default_value = 1.2
        nt.links.new(vec, w_.inputs["Vector"])
        return w_.outputs["Fac"]

    # strand families, each in its own direction and warp: they cross, fan out and curl
    fam_a = strands(flow(0.35, (0.5, 1.0, 1.0), 0.4, 1.6, 2.7), 1.5, 2.5)  # rising the other way
    fam_b = strands(flow(-1.35, (0.6, 1.0, 1.0), 0.55, 2.2, 5.1), 1.9, 3.0)  # steep, curling
    fam_c = strands(flow(1.05, (0.4, 1.0, 1.0), 0.3, 2.8, 8.4), 1.2, 2.0)  # long arcs across
    out = layer(out, _rel(f, "#8c6a4a", *ref), ramp_of(fam_a, ((0.47, 0.0), (0.5, 1.0), (0.535, 0.0))), 0.5)  # medium strands
    out = layer(out, _rel(f, "#6f5238", *ref), ramp_of(fam_b, ((0.80, 0.0), (0.805, 1.0), (0.812, 0.0))), 0.6)  # hairlines
    out = layer(out, _rel(f, "#9b7957", *ref), ramp_of(fam_c, ((0.30, 0.0), (0.315, 1.0), (0.34, 0.0))), 0.45)  # thick-ish arcs
    out = layer(out, _rel(f, "#7a5b40", *ref), ramp_of(fam_a, ((0.88, 0.0), (0.884, 1.0), (0.889, 0.0))), 0.5)  # fine hairlines
    gloss = ramp_of(wave.outputs["Fac"], ((0.62, 0.0), (0.64, 1.0), (0.67, 0.0)))  # bright highlight streak
    out = layer(out, _rel(f, "#fbf7f1", *ref), gloss, 0.7)
    # vague colour sprays on the white: big soft blotches of warm sand and blush
    spray = nt.nodes.new("ShaderNodeTexNoise")
    spray.inputs["Scale"].default_value = 0.6
    spray.inputs["Detail"].default_value = 3.0
    nt.links.new(vector, spray.inputs["Vector"])
    sand = ramp_of(spray.outputs["Fac"], ((0.55, 0.0), (0.72, 1.0)))
    blush = ramp_of(spray.outputs["Fac"], ((0.28, 1.0), (0.42, 0.0)))
    out = layer(out, _rel(f, "#d9b48e", *ref), sand, 0.30)
    out = layer(out, _rel(f, "#e7c3b4", *ref), blush, 0.25)
    return out


def _marble_color(nt, vector, f, joint_fac):
    """Marble colour: color base with soft warm clouding, color2 veins (broken), grey hairlines, then grout."""
    base, gold = srgb_to_linear(f.color), srgb_to_linear(f.color2)
    cloud_tint = tuple(b * 0.86 + g * 0.14 for b, g in zip(base, gold, strict=True))
    cloud = nt.nodes.new("ShaderNodeTexNoise")
    cloud.inputs["Scale"].default_value = 1.4
    cloud.inputs["Detail"].default_value = 5.0
    nt.links.new(vector, cloud.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    lo, hi = ramp.color_ramp.elements
    lo.position, hi.position = 0.5, 0.78
    lo.color, hi.color = (*base, 1), (*cloud_tint, 1)
    nt.links.new(cloud.outputs["Fac"], ramp.inputs["Fac"])
    out = ramp.outputs["Color"]
    layers = [(_vein_mask(nt, vector, 1.6, 0.006, 3.1, 0.0), (0.62, 0.62, 0.6), 0.3),  # faint grey hairlines
              (_vein_mask(nt, vector, 1.25, 0.013, 0.0, 0.2), gold, 0.75),  # main gold veins, broken
              (_vein_mask(nt, vector, 2.2, 0.009, 7.3, 0.25), gold, 0.45)]  # finer side veins, soft
    for mask, color, strength in layers:
        amt = nt.nodes.new("ShaderNodeMath")
        amt.operation = "MULTIPLY"
        amt.inputs[1].default_value = strength
        nt.links.new(mask, amt.inputs[0])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(amt.outputs[0], mix.inputs["Factor"])
        nt.links.new(out, mix.inputs["A"])
        mix.inputs["B"].default_value = (*color, 1)
        out = mix.outputs["Result"]
    grout = nt.nodes.new("ShaderNodeMix")
    grout.data_type = "RGBA"
    nt.links.new(joint_fac, grout.inputs["Factor"])
    nt.links.new(out, grout.inputs["A"])
    grout.inputs["B"].default_value = (*srgb_to_linear(f.joint_color), 1)
    return grout.outputs["Result"]


def build_walls(apt, mats, col) -> None:
    h = apt.levels.ceiling_height
    for w in apt.walls:
        ops = [(o.span[0], o.span[1], o.sill, o.head) for o in apt.openings_in(w.id)]
        obj = boxes_object(f"WALL_{w.id}", wall_boxes(w.rect, w.horizontal, h, ops), mats["wall"], col)
        obj["wall_id"], obj["wall_type"], obj["thickness"] = w.id, w.type, w.thickness


def _outer_side(apt, w) -> int:
    """+1 if the wall's outer face is at the max coordinate across its thickness, else -1."""
    xs = [p[0] for r in apt.rooms for p in r.polygon]
    ys = [p[1] for r in apt.rooms for p in r.polygon]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    x1, y1, x2, y2 = w.rect
    return (1 if (y1 + y2) / 2 > cy else -1) if w.horizontal else (1 if (x1 + x2) / 2 > cx else -1)


def build_door_frames(apt, col) -> None:
    """White door frames on every door opening (the leaves themselves are not modelled): a lining in the opening
    (two jambs + head) and a 7 cm architrave, 1.5 cm proud, on both faces of the wall."""
    white = principled("MAT_door_frame", (0.88, 0.88, 0.86), roughness=0.45)
    lin, arch, proud = 0.02, 0.07, 0.015
    for o in apt.openings:
        if o.kind != "door":
            continue
        w = apt.wall(o.wall)
        x1, y1, x2, y2 = w.rect
        t0, t1 = (y1, y2) if w.horizontal else (x1, x2)
        a0, a1, head = o.span[0], o.span[1], o.head

        def box(s, e, za, zb, ta, tb, w=w):
            return (s, ta, za, e, tb, zb) if w.horizontal else (ta, s, za, tb, e, zb)

        boxes = [box(a0, a0 + lin, 0, head, t0, t1), box(a1 - lin, a1, 0, head, t0, t1),
                 box(a0, a1, head - lin, head, t0, t1)]
        for ta, tb in ((t0 - proud, t0), (t1, t1 + proud)):  # architraves on both faces
            boxes += [box(a0 - arch, a0, 0, head + arch, ta, tb), box(a1, a1 + arch, 0, head + arch, ta, tb),
                      box(a0 - arch, a1 + arch, head, head + arch, ta, tb)]
        obj = boxes_object(f"DOORFRAME_{o.id}", boxes, white, col)
        obj["opening_id"], obj["kind"] = o.id, "door_frame"


def build_windows(apt, mats, col) -> None:
    d = apt.openings_defaults
    fw, fd = d.frame_width, d.frame_depth
    for o in apt.openings:
        if o.kind not in ("window", "balcony_door"):
            continue
        w = apt.wall(o.wall)
        x1, y1, x2, y2 = w.rect
        side = _outer_side(apt, w)
        # position of the frame centre across the wall thickness
        if w.horizontal:
            outer = y2 if side > 0 else y1
        else:
            outer = x2 if side > 0 else x1
        c = outer - side * (d.window_setback_from_outside + fd / 2)
        a0, a1, z0, z1 = o.span[0], o.span[1], o.sill, o.head
        n_panes = 2 if o.width > 1.2 else 1

        def box(s, e, za, zb, depth, w=w, c=c):
            if w.horizontal:
                return (s, c - depth / 2, za, e, c + depth / 2, zb)
            return (c - depth / 2, s, za, c + depth / 2, e, zb)

        frame = [
            box(a0, a1, z0, z0 + fw, fd), box(a0, a1, z1 - fw, z1, fd),
            box(a0, a0 + fw, z0, z1, fd), box(a1 - fw, a1, z0, z1, fd),
        ]
        if n_panes == 2:
            m = (a0 + a1) / 2
            frame.append(box(m - fw / 2, m + fw / 2, z0, z1, fd))
        fobj = boxes_object(f"FRAME_{o.id}", frame, mats["frame"], col)
        gobj = boxes_object(f"GLASS_{o.id}", [box(a0 + fw, a1 - fw, z0 + fw, z1 - fw, 0.024)], mats["glass"], col)
        gobj.visible_shadow = False  # let sunlight through in EEVEE and Cycles
        for obj in (fobj, gobj):
            obj["opening_id"], obj["kind"], obj["width"] = o.id, o.kind, o.width


def build_floors(apt, mats, col_floors, col_struct) -> None:
    for r in apt.rooms:
        obj = polygon_object(f"FLOOR_{r.id}", r.polygon, 0.002, mats.get(r.finish, mats["default"]), col_floors)
        obj["room_id"], obj["room_name"], obj["listed_area"] = r.id, r.name, r.listed_area
        obj["model_area"] = round(abs(polygon_area(r.polygon)), 3)
    slab_from_cells("SLAB_floor", apt.footprint_cells(), 0.0, apt.levels.slab_thickness, mats["slab"], col_struct)


def build_ceiling(apt, mats, col) -> None:
    h = apt.levels.ceiling_height
    obj = slab_from_cells("CEILING", apt.footprint_cells(), h, -apt.levels.slab_thickness, mats["ceiling"], col)
    obj["note"] = "Ceiling at clear height; use the Apartment panel to hide it (keeps sun shadows)"


def build_balcony(apt, mats, col, col_context) -> None:
    b = apt.balcony
    if not b:
        return
    z = apt.levels.balcony_floor_z
    sx1, sy1, sx2, sy2 = b.slab
    boxes_object("BALCONY_slab", [(sx1, sy1, z - 0.20, sx2, sy2, z)], mats["slab"], col)
    fl = polygon_object("FLOOR_balcony", b.polygon, z + 0.002, mats[b.finish], col)
    fl["room_id"], fl["room_name"], fl["listed_area"] = b.id, b.name, b.listed_area
    top = apt.levels.ceiling_height + apt.levels.slab_thickness + z  # finished floor of the balcony above
    w1, wy1, w2, wy2 = b.side_wall
    boxes_object("BALCONY_side_wall", [(w1, wy1, z, w2, wy2, top - 0.20)], mats["wall"], col)
    # railing along the outer edge (x = sx1) and the short end (y = sy1)
    rh, t = b.railing_height, 0.02
    glass = [(sx1, sy1, z + 0.05, sx1 + t, wy1, z + rh - 0.05), (sx1, sy1, z + 0.05, sx2, sy1 + t, z + rh - 0.05)]
    rail = boxes_object("BALCONY_railing_glass", glass, mats["railing_glass"], col)
    rail.visible_shadow = False
    boxes_object("BALCONY_handrail", [
        (sx1 - 0.02, sy1, z + rh - 0.05, sx1 + 0.04, wy1, z + rh),
        (sx1, sy1 - 0.02, z + rh - 0.05, sx2, sy1 + 0.04, z + rh),
    ], mats["metal"], col)
    if apt.levels.balcony_above:
        boxes_object("CONTEXT_balcony_above", [(sx1, sy1, top - 0.20, sx2, sy2, top)], mats["slab"], col_context)


def grass_material() -> bpy.types.Material:
    """Lawn seen from the 6th floor: two greens mixed by noise, matte."""
    m = principled("MAT_grass", (0.10, 0.22, 0.05), roughness=0.95)
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.6
    noise.inputs["Detail"].default_value = 8.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    lo, hi = ramp.color_ramp.elements
    lo.color, hi.color = (0.06, 0.15, 0.03, 1), (0.16, 0.28, 0.07, 1)
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def build_trees(trees, ground: float, col) -> None:
    """Simple deciduous trees on the lawn: bark trunk + two overlapping smooth crowns (one object)."""
    bark = principled("MAT_tree_bark", (0.12, 0.08, 0.05), roughness=0.9)
    leaves = principled("MAT_tree_leaves", (0.06, 0.16, 0.04), roughness=1.0, **{"Specular IOR Level": 0.0})
    bm = bmesh.new()
    face_mat = []
    for x, y, h, r in trees:
        before = len(bm.faces)
        verts = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.16, radius2=0.11, depth=h * 0.55)["verts"]
        bmesh.ops.translate(bm, vec=(x, y, ground + h * 0.275), verts=verts)
        face_mat += [0] * (len(bm.faces) - before)
        for dx, dy, dz, s in ((0, 0, h - r, 1.0), (r * 0.35, -r * 0.25, h - r * 1.45, 0.75)):
            before = len(bm.faces)
            verts = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r * s)["verts"]
            bmesh.ops.scale(bm, vec=(1.0, 1.0, 0.85), verts=verts)
            bmesh.ops.translate(bm, vec=(x + dx, y + dy, ground + dz), verts=verts)
            face_mat += [1] * (len(bm.faces) - before)
    me = bpy.data.meshes.new("CONTEXT_trees")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(bark)
    me.materials.append(leaves)
    for poly, idx in zip(me.polygons, face_mat, strict=True):
        poly.material_index = idx
        poly.use_smooth = idx == 1
    obj = link(bpy.data.objects.new("CONTEXT_trees", me), col)
    obj["trees"] = len(trees)


def build_building(apt, mats, col) -> None:
    """Context massing: gray block below the apartment down to the street, the neighbours on this floor
    (past the party / corridor walls), the floors above, and a lawn ring around it (ADR 0010)."""
    bd = apt.building
    if bd is None:
        return
    storey = apt.levels.ceiling_height + apt.levels.slab_thickness
    xs = [c for w in apt.walls for c in (w.rect[0], w.rect[2])]
    ys = [c for w in apt.walls for c in (w.rect[1], w.rect[3])]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)  # facade B = x0, facade A = y1 (outside); x1 / y0 party
    e = bd.party_extension
    fx0, fy0, fx1, fy1 = x0, y0 - e, x1 + e, y1  # whole block footprint
    ground = -bd.storeys_below * storey
    top = storey + bd.floors_above * storey
    gray = principled("MAT_building", (0.42, 0.42, 0.42), roughness=0.85)
    boxes = [(fx0, fy0, ground, fx1, fy1, -apt.levels.slab_thickness)]  # storeys below
    boxes += [(x1, fy0, -apt.levels.slab_thickness, fx1, fy1, storey),  # neighbours on this floor
              (x0, fy0, -apt.levels.slab_thickness, x1, y0, storey)]
    if bd.floors_above:
        boxes.append((fx0, fy0, storey, fx1, fy1, top))
    obj = boxes_object("CONTEXT_building", boxes, gray, col)
    obj["storeys_below"], obj["floors_above"], obj["ground_z"] = bd.storeys_below, bd.floors_above, ground
    if bd.trees and bd.grass_margin:
        build_trees(scatter_trees((fx0, fy0, fx1, fy1), bd.grass_margin, bd.trees), ground, col)
    m = bd.grass_margin
    if m:
        poly = [(fx0 - m, fy0 - m), (fx1 + m, fy0 - m), (fx1 + m, fy1 + m), (fx0 - m, fy1 + m)]
        g = polygon_object("CONTEXT_grass", poly, ground, grass_material(), col)
        g["grass_margin"] = m


def build_annotations(apt, mats, col) -> None:
    for r in apt.all_rooms():
        cx, cy = polygon_centroid(r.polygon)
        a = abs(polygon_area(r.polygon))
        text_object(f"LABEL_{r.id}", f"{r.name}\n{a:.2f} m²", (cx, cy, 0.01), 0.22, mats["label"], col)
    # north arrow outside the apartment (top-right)
    xs = [v for w in apt.walls for v in (w.rect[0], w.rect[2])]
    ys = [v for w in apt.walls for v in (w.rect[1], w.rect[3])]
    pos = Vector((max(xs) + 1.6, max(ys) - 1.2, 0.01))
    ang = math.radians(apt.site.plus_y_bearing)  # CCW rotation that turns +Y into true north
    me = bpy.data.meshes.new("NORTH_arrow")
    me.from_pydata([(0, 0.9, 0), (-0.3, -0.5, 0), (0, -0.25, 0), (0.3, -0.5, 0)], [], [[0, 1, 2], [0, 2, 3]])
    me.materials.append(mats["north"])
    arrow = link(bpy.data.objects.new("NORTH_arrow", me), col)
    arrow.location, arrow.rotation_euler.z = pos, ang
    arrow.hide_render = True
    north = Vector((-math.sin(ang), math.cos(ang), 0.0))
    text_object("NORTH_label", "N", pos + north * 1.3, 0.45, mats["north"], col)


def _strip(points, width: float, z: float):
    """Flat ribbon along a polyline: (verts, quads)."""
    verts, faces = [], []
    for (ax, ay), (bx, by) in zip(points, points[1:], strict=False):
        dx, dy = bx - ax, by - ay
        n = math.hypot(dx, dy) or 1.0
        ox, oy = -dy / n * width / 2, dx / n * width / 2
        i = len(verts)
        verts += [(ax - ox, ay - oy, z), (bx - ox, by - oy, z), (bx + ox, by + oy, z), (ax + ox, ay + oy, z)]
        faces.append((i, i + 1, i + 2, i + 3))
    return verts, faces


def build_plan_symbols(apt, mats, col) -> None:
    """Architectural door/window symbols for the top-down plan, just above the wall tops.

    From above, the wall over each opening (lintel up to the ceiling) hides it, so the plan
    gets a cut-out (white) with the window glazing line or the door leaf + swing arc.
    Self-lit (emission), no shadows; lives in Annotations so room views hide it.
    """
    z = apt.levels.ceiling_height + 0.02
    d = apt.openings_defaults
    for o in apt.openings:
        w = apt.wall(o.wall)
        x1, y1, x2, y2 = w.rect
        a0, a1 = o.span
        cut = [(a0, y1), (a1, y1), (a1, y2), (a0, y2)] if w.horizontal else [(x1, a0), (x2, a0), (x2, a1), (x1, a1)]
        strokes = []  # (polyline, width, z offset) drawn in the line colour
        if o.kind == "door":
            # doors between rooms: red leaf + swing + a red line across the opening;
            # the entrance (fixed by the building) in dark red, drawn heavier
            k = 1.5 if o.fixed else 1.0
            if o.hinge:
                leaf, arc = door_swing(w.rect, w.horizontal, o.span, o.hinge, o.swing, segments=24)
                strokes += [(arc, 0.03 * k, 0.004), (leaf, 0.06 * k, 0.006)]
            mid = (y1 + y2) / 2 if w.horizontal else (x1 + x2) / 2
            strokes.append(([(a0, mid), (a1, mid)] if w.horizontal else [(mid, a0), (mid, a1)], 0.04 * k, 0.005))
            line_mat = mats["plan_door_fixed" if o.fixed else "plan_door"]
        else:
            # glazing line at the frame position + the two wall faces
            side = _outer_side(apt, w)
            t_lo, t_hi = (y1, y2) if w.horizontal else (x1, x2)
            c = (t_hi if side > 0 else t_lo) - side * (d.window_setback_from_outside + d.frame_depth / 2)
            for t, width in ((c, 0.05), (t_lo, 0.02), (t_hi, 0.02)):
                strokes.append(([(a0, t), (a1, t)] if w.horizontal else [(t, a0), (t, a1)], width, 0.004))
            line_mat = mats["plan_window"]
        verts = [(x, y, z) for x, y in cut]
        faces, mat_idx = [(0, 1, 2, 3)], [0]
        for points, width, dz in strokes:
            v, f = _strip(points, width, z + dz)
            faces += [tuple(len(verts) + i for i in q) for q in f]
            verts += v
            mat_idx += [1] * len(f)
        me = bpy.data.meshes.new(f"PLAN_{o.id}")
        me.from_pydata(verts, [], faces)
        for poly, idx in zip(me.polygons, mat_idx, strict=True):
            poly.material_index = idx
        me.materials.append(mats["plan_cut"])
        me.materials.append(line_mat)
        obj = link(bpy.data.objects.new(f"PLAN_{o.id}", me), col)
        obj["opening_id"], obj["kind"], obj["fixed"] = o.id, o.kind, o.fixed
        obj.visible_shadow = False
        if o.fixed:  # label on the corridor side of the entrance
            if w.horizontal:
                pos = ((a0 + a1) / 2, y1 - 0.45, z + 0.01)
            else:
                pos = (x2 + 0.55, (a0 + a1) / 2, z + 0.01)
            t = text_object(f"PLAN_{o.id}_label", "ENTRANCE (fixed)", pos, 0.18, mats["plan_door_fixed"], col)
            t.hide_render = False


def _disc(name: str, center, radius: float, z: float, material, col, ring: float = 0.0, segments: int = 32):
    """Flat disc (ring > 0: an annulus of that width) for plan markers."""
    cx, cy = center
    ang = [2 * math.pi * i / segments for i in range(segments)]
    if ring:
        verts = [(cx + r * math.cos(a), cy + r * math.sin(a), z) for r in (radius - ring, radius) for a in ang]
        faces = [(i, (i + 1) % segments, segments + (i + 1) % segments, segments + i) for i in range(segments)]
    else:
        verts = [(cx + radius * math.cos(a), cy + radius * math.sin(a), z) for a in ang]
        faces = [tuple(range(segments))]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.materials.append(material)
    obj = link(bpy.data.objects.new(name, me), col)
    obj.visible_shadow = False
    return obj


def build_fixed_points(apt, mats, col) -> None:
    """Fixed service points (pipes, drains, vents) on the plan: dot + tolerance ring + label."""
    z = apt.levels.ceiling_height + 0.03
    for f in apt.fixed_points:
        mat = mats.get(f"point_{f.kind}", mats["point_other"])
        dot = _disc(f"FIXED_{f.id}", f.position, 0.09, z, mat, col)
        _disc(f"FIXED_{f.id}_ring", f.position, f.radius, z - 0.002, mat, col, ring=0.015)
        t = text_object(f"FIXED_{f.id}_label", f.label, (f.position[0], f.position[1] + 0.2, z + 0.002), 0.13, mat, col)
        t.hide_render = False
        for o in (dot, t):
            o["fixed_point_id"], o["kind"], o["serves"], o["note"] = f.id, f.kind, ", ".join(f.serves), f.note


def srgb_to_linear(hex_color: str, lighten: float = 0.0) -> tuple[float, float, float]:
    out = []
    for i in (1, 3, 5):
        c = int(hex_color[i : i + 2], 16) / 255
        c = c + (1 - c) * lighten
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


class FurnitureMaterials:
    """One material per (shade, colour, finish); shades/finishes are defined in apartment_core.furniture."""

    def __init__(self):
        self.cache: dict[tuple[str, str, str], bpy.types.Material] = {}

    true_colors = False  # set per variant while building it: fabrics (soft / shag / sheer) not lightened

    def get(self, shade: str, hex_color: str, finish: str = "") -> bpy.types.Material:
        true = self.true_colors and shade in ("soft", "shag", "sheer")
        key = (shade, hex_color.lower(), finish, true)
        if key in self.cache:
            return self.cache[key]
        name = f"MAT_furn_{shade}_{hex_color.lower()[1:]}" + (f"_{finish}" if finish else "") + ("_true" if true else "")
        c = srgb_to_linear(hex_color)
        blended = False
        if shade == "soft":
            m = principled(name, srgb_to_linear(hex_color, 0.0 if true else 0.55), roughness=0.8)
            if true:  # velvet / boucle feel without washing the colour out
                bsdf0 = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
                bsdf0.inputs["Sheen Weight"].default_value = 0.25
                bsdf0.inputs["Sheen Tint"].default_value = (*srgb_to_linear(hex_color), 1)
        elif shade == "dark":
            m = principled(name, tuple(v * 0.25 for v in c), roughness=0.6)
        elif shade == "interior":
            m = principled(name, srgb_to_linear(hex_color, 0.1), roughness=0.7)
        elif shade == "handle":
            m = principled(name, c, roughness=0.3, Metallic=0.8)
        elif shade == "ceramic":
            m = principled(name, c, roughness=0.08)
        elif shade == "glass":
            m, blended = principled(name, (0.8, 0.88, 0.9), roughness=0.02, Alpha=0.15), True
        elif shade == "smoked":  # dark smoked glass: the lit inside shows faintly through
            m, blended = principled(name, (0.015, 0.015, 0.018), roughness=0.04, Alpha=0.58), True
        elif shade == "shag":  # long-pile rug: fine fibre noise as colour variation + strong bump, soft sheen
            m = principled(name, srgb_to_linear(hex_color, 0.0 if true else 0.45), roughness=1.0,
                           **{"Sheen Weight": 0.6 if true else 1.0})
            if true:  # sheen in the rug's own colour - a white sheen washed every true-colour rug out
                bsdf0 = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
                bsdf0.inputs["Sheen Tint"].default_value = (*srgb_to_linear(hex_color), 1)
                bsdf0.inputs["Sheen Weight"].default_value = 0.3
            nt = m.node_tree
            bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
            coord = nt.nodes.new("ShaderNodeTexCoord")
            stretch = nt.nodes.new("ShaderNodeMapping")  # strands lie in one direction (combed)
            stretch.inputs["Scale"].default_value = (1.0, 0.35, 1.0)
            nt.links.new(coord.outputs["Object"], stretch.inputs["Vector"])
            fibre = nt.nodes.new("ShaderNodeTexNoise")
            fibre.inputs["Scale"].default_value = 160.0
            fibre.inputs["Detail"].default_value = 10.0
            fibre.inputs["Roughness"].default_value = 0.7
            fibre.inputs["Distortion"].default_value = 1.5
            nt.links.new(stretch.outputs["Vector"], fibre.inputs["Vector"])
            tone = nt.nodes.new("ShaderNodeMix")
            tone.data_type = "RGBA"
            nt.links.new(fibre.outputs["Fac"], tone.inputs["Factor"])
            lo, hi = (0.0, 0.18) if true else (0.25, 0.62)  # fibre tones around the colour
            tone.inputs["A"].default_value = (*srgb_to_linear(hex_color, lo), 1)
            tone.inputs["B"].default_value = (*srgb_to_linear(hex_color, hi), 1)
            nt.links.new(tone.outputs["Result"], bsdf.inputs["Base Color"])
            bump = nt.nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = 0.9
            bump.inputs["Distance"].default_value = 0.02
            nt.links.new(fibre.outputs["Fac"], bump.inputs["Height"])
            nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        elif shade == "sheer":  # white transparent silk: daylight glows through, soft sheen
            m, blended = principled(name, srgb_to_linear(hex_color, 0.0 if true else 0.3), roughness=0.55, Alpha=0.38,
                                    **{"Sheen Weight": 0.6}), True
        elif shade == "fabric":  # heavy curtain fabric: matte with a little sheen
            m = principled(name, c, roughness=0.9, **{"Sheen Weight": 0.5})
        elif shade == "chrome":
            m = principled(name, (0.8, 0.8, 0.82), roughness=0.15, Metallic=1.0)
        elif shade == "black":
            m = principled(name, (0.01, 0.01, 0.012), roughness=0.1)
        elif shade == "mirror":
            m = principled(name, srgb_to_linear(hex_color, 0.6), roughness=0.02, Metallic=1.0)
        elif shade == "plant":
            m = principled(name, c, roughness=0.8)
        elif shade == "emit":  # glowing diffuser of a light fixture
            m = principled(name, c, roughness=0.5, **{"Emission Color": (*c, 1.0), "Emission Strength": 4.0})
        elif shade == "front" and finish == "glass":  # tinted glass door: the interior shows through
            m, blended = principled(name, c, roughness=0.05, Alpha=0.82), True
        elif shade == "front" and finish == "mirror":
            m = principled(name, c, roughness=0.03, Metallic=1.0)
        elif shade == "front":
            m = principled(name, c, roughness={"gloss": 0.15, "wood": 0.45}.get(finish, 0.5))
        else:  # main
            m = principled(name, c, roughness=0.5)
        if blended:
            m.surface_render_method = "BLENDED"
            if hasattr(m, "use_transparent_shadow"):  # light passes through sheers / glass in EEVEE
                m.use_transparent_shadow = True
        self.cache[key] = m
        return m


def parts_mesh(name: str, parts, item_color: str, fmats: FurnitureMaterials) -> bpy.types.Mesh:
    """Mesh from apartment_core Part tuples (boxes and cylinders), one material slot per look."""
    bm = bmesh.new()
    slots: list[tuple[str, str, str]] = []
    face_slot: list[int] = []
    for part in parts:
        x1, y1, z1, x2, y2, z2 = part.box
        look = (part.shade, part.color or item_color, part.finish)
        if look not in slots:
            slots.append(look)
        before = len(bm.faces)
        if part.shape in ("cyl", "ycyl", "xcyl"):
            verts = bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=0.5, radius2=0.5, depth=1.0)["verts"]
            if part.shape == "ycyl":  # lay the unit cylinder along y before sizing it
                bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"), verts=verts)
            elif part.shape == "xcyl":  # ... or along x
                bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"), verts=verts)
        else:
            verts = bmesh.ops.create_cube(bm, size=1.0)["verts"]
        bmesh.ops.scale(bm, vec=(x2 - x1, y2 - y1, z2 - z1), verts=verts)
        bmesh.ops.translate(bm, vec=((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2), verts=verts)
        face_slot += [slots.index(look)] * (len(bm.faces) - before)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for shade, color, finish in slots:
        me.materials.append(fmats.get(shade, color, finish))
    for poly, idx in zip(me.polygons, face_slot, strict=True):
        poly.material_index = idx
    return me


def _child(name: str, me, parent, col, location) -> bpy.types.Object:
    obj = link(bpy.data.objects.new(name, me), col)
    obj.parent = parent
    obj.location = location
    return obj


def build_storage(it, root_name: str, fmats, col) -> bpy.types.Object:
    """Carcass = the piece's own object; fronts are children pivoting at their hinge (they open),
    interior fittings are children too. Custom props let the add-on open fronts and show part ids."""
    lay = storage_layout(it)
    root = link(bpy.data.objects.new(root_name, parts_mesh(root_name, lay.carcass, it.color, fmats)), col)
    interior_color = (it.storage.interior_color if it.storage else "") or it.color
    for mp in lay.fronts:
        name = f"FRONT_{it.id}_{mp.name}"
        obj = _child(name, parts_mesh(name, mp.parts, it.color, fmats), root, col, mp.pivot)
        obj["part_id"] = f"{it.id}/{mp.name.replace('-', '/', 1)}"
        obj["module"], obj["motion"], obj["amount"], obj["pivot"] = mp.module, mp.motion, mp.amount, list(mp.pivot)
        obj["storage_front"] = True
    for name, k, part in lay.interior:
        oname = f"INT_{it.id}_{name.replace('/', '_')}"
        obj = _child(oname, parts_mesh(oname, [part], interior_color, fmats), root, col, (0, 0, 0))
        obj["part_id"], obj["module"], obj["storage_interior"] = f"{it.id}/{name}", k, True
    w, d, h = it.size
    root["storage"] = True
    root["open"] = 0.0
    root["modules"] = len(lay.modules)
    root["module_centres"] = [[(xa + xb) / 2, d / 2 + 0.03, h * 0.5] for xa, xb in lay.modules]
    return root


LIGHT_TYPES = {"point": "POINT", "spot": "SPOT", "area": "AREA", "rect": "AREA"}


def add_light(it, obj, col) -> bpy.types.Object:
    """A real Blender light under a fixture (child of it, so it moves and hides with the piece)."""
    lt = light_of(it)
    data = bpy.data.lights.new(f"LIGHT_{it.id}", LIGHT_TYPES[lt.kind])
    data.energy = lt.watts
    data.color = srgb_to_linear(lt.color)
    if lt.kind == "area":
        data.shape, data.size = "DISK", lt.size
    elif lt.kind == "rect":  # LED strip / linear bar: a rectangle the size of the piece
        data.shape, data.size, data.size_y = "RECTANGLE", it.size[0], max(it.size[1], 0.01)
    else:
        data.shadow_soft_size = lt.size
    if lt.kind == "spot":
        data.spot_size, data.spot_blend = math.radians(lt.spot_angle), 0.4
    data.use_shadow = casts_shadow(it)  # performance: shadow maps only for the hero pendants
    data.use_custom_distance, data.cutoff_distance = True, light_cutoff(it)  # cost stays in its room
    lo = _child(f"LIGHT_{it.id}", data, obj, col, light_source_pos(it))
    if lt.aim == "up":  # area/spot lights shine along -Z; flip to wash the ceiling
        lo.rotation_euler.x = math.pi
    lo["furniture_light"], lo["part_id"] = True, f"{it.id}/light"
    return lo


def add_track_heads(it, col, fmats, z_offset: float = 0.0) -> None:
    """Spot heads of a track-light: stem from the rail, head body turned to its aim point, a narrow spot
    light in each (no shadows, short cut-off - ADR 0008). Objects TRACKHEAD_<id>_<k> / LIGHT_<id>_<k>."""
    tr = it.track
    rail_bottom = it.elevation + it.size[2] + z_offset - 0.035
    for k, ((px, py, pz), d) in enumerate(track_heads(it, z_offset), start=1):
        stem = parts_mesh(f"TRACKSTEM_{it.id}_{k}", [Part((-0.006, -0.006, 0.0, 0.006, 0.006, rail_bottom - pz),
                                                          "main", "cyl")], it.color, fmats)
        so = link(bpy.data.objects.new(f"TRACKSTEM_{it.id}_{k}", stem), col)
        so.location = (px, py, pz)
        body = [Part((-0.028, -0.028, -0.06, 0.028, 0.028, 0.035), "main", "cyl"),  # head in the track's colour
                Part((-0.02, -0.02, -0.062, 0.02, 0.02, -0.06), "emit", "cyl", tr.color)]
        ho = link(bpy.data.objects.new(f"TRACKHEAD_{it.id}_{k}", parts_mesh(f"TRACKHEAD_{it.id}_{k}", body,
                                                                               it.color, fmats)), col)
        ho.location = (px, py, pz)
        ho.rotation_mode = "QUATERNION"
        ho.rotation_quaternion = Vector(d).to_track_quat("-Z", "Y")
        data = bpy.data.lights.new(f"LIGHT_{it.id}_{k}", "SPOT")
        data.energy, data.color = tr.watts, srgb_to_linear(tr.color)
        data.spot_size, data.spot_blend, data.shadow_soft_size = math.radians(tr.beam), 0.35, 0.015
        data.use_shadow = False
        data.use_custom_distance, data.cutoff_distance = True, 5.0
        lo = link(bpy.data.objects.new(f"LIGHT_{it.id}_{k}", data), col)
        lo.location = Vector((px, py, pz)) + Vector(d) * 0.065
        lo.rotation_mode = "QUATERNION"
        lo.rotation_quaternion = ho.rotation_quaternion
        for o in (so, ho, lo):
            o["part_id"], o["variant"] = f"{it.id}/head-{k}", it.variant
        lo["furniture_light"] = True


def bird_of_paradise_mesh(name: str, it, fmats) -> bpy.types.Mesh:
    """Strelitzia in a tapered stone pot, as a real mesh: ~10 arching stems fanning out (golden-angle spread),
    each carrying a long tapered paddle leaf with a central fold that bends over at the tip. Deterministic per id."""
    import random

    rng = random.Random(sum(map(ord, it.id)))
    w, d, h = it.size
    pot_h, r_top = min(0.42, h * 0.24), min(w, d) * 0.33
    bm = bmesh.new()
    face_slot: list[int] = []

    def add(verts_faces_before, slot):
        face_slot.extend([slot] * (len(bm.faces) - verts_faces_before))

    n0 = len(bm.faces)  # pot, rim, soil
    v = bmesh.ops.create_cone(bm, cap_ends=True, segments=40, radius1=r_top * 0.78, radius2=r_top, depth=pot_h)["verts"]
    bmesh.ops.translate(bm, vec=(0, 0, pot_h / 2), verts=v)
    v = bmesh.ops.create_cone(bm, cap_ends=True, segments=40, radius1=r_top + 0.012, radius2=r_top + 0.012,
                              depth=0.03)["verts"]
    bmesh.ops.translate(bm, vec=(0, 0, pot_h - 0.015), verts=v)
    add(n0, 0)
    n0 = len(bm.faces)
    v = bmesh.ops.create_cone(bm, cap_ends=True, segments=40, radius1=r_top * 0.96, radius2=r_top * 0.96,
                              depth=0.012)["verts"]
    bmesh.ops.translate(bm, vec=(0, 0, pot_h + 0.002), verts=v)
    add(n0, 1)

    up = Vector((0, 0, 1))
    n_leaves = 10
    for i in range(n_leaves):
        az = i * 2.39996 + rng.uniform(-0.25, 0.25)
        inner = i / (n_leaves - 1)  # later leaves more upright and taller
        tilt = 0.55 - 0.42 * inner + rng.uniform(-0.06, 0.06)
        out = Vector((math.cos(az), math.sin(az), 0))
        base = Vector((rng.uniform(-0.03, 0.03), rng.uniform(-0.03, 0.03), pot_h))
        stem_len = (h - pot_h) * (0.42 + 0.22 * inner) * rng.uniform(0.92, 1.05)
        sdir = (out * math.sin(tilt) + up * math.cos(tilt)).normalized()
        pts = [base + sdir * stem_len * t + out * (0.10 * stem_len * t * t) for t in (k / 8 for k in range(9))]
        n0 = len(bm.faces)  # stem: thin tube along the curve
        rings = []
        for k, c in enumerate(pts):
            t = (pts[min(k + 1, 8)] - pts[max(k - 1, 0)]).normalized()
            a = t.cross(up if abs(t.z) < 0.95 else Vector((1, 0, 0))).normalized()
            b = t.cross(a)
            r = 0.011 - 0.004 * k / 8
            rings.append([bm.verts.new(c + (a * math.cos(j * math.pi / 3) + b * math.sin(j * math.pi / 3)) * r)
                          for j in range(6)])
        for k in range(8):
            for j in range(6):
                bm.faces.new((rings[k][j], rings[k][(j + 1) % 6], rings[k + 1][(j + 1) % 6], rings[k + 1][j]))
        add(n0, 2)
        # blade: starts at the stem tip, leans further out, arches down towards the tip
        tip = pts[-1]
        bdir = (out * math.sin(tilt + 0.35) + up * math.cos(tilt + 0.35)).normalized()
        blade = min(rng.uniform(0.42, 0.58), (h - tip.z) / max(bdir.z, 0.3) * 0.98)
        width = blade * rng.uniform(0.30, 0.36)
        side = bdir.cross(up).normalized()
        nrm = side.cross(bdir).normalized()
        twist = rng.uniform(-0.25, 0.25)
        nl, nw = 12, 4
        n0 = len(bm.faces)
        grid = []
        for a in range(nl + 1):
            u = a / nl
            c = tip + bdir * blade * u - up * (0.28 * blade * u * u)
            wu = width / 2 * (math.sin(math.pi * min(u * 1.02, 1.0)) ** 0.75) + (0.004 if u < 0.05 else 0.0)
            sd = (side * math.cos(twist * u) + nrm * math.sin(twist * u))
            row = []
            for b in range(-nw, nw + 1):
                vv = b / nw
                row.append(bm.verts.new(c + sd * vv * wu + nrm * (abs(vv) * wu * 0.22)))  # V fold along the midrib
            grid.append(row)
        for a in range(nl):
            for b in range(2 * nw):
                bm.faces.new((grid[a][b], grid[a][b + 1], grid[a + 1][b + 1], grid[a + 1][b]))
        add(n0, 3 if i % 3 else 4)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    leaf = it.color
    for shade, color in (("main", "#cfc6b8"), ("dark", "#4a3a2a"), ("plant", "#3e5a2a"), ("plant", leaf),
                         ("plant", "#4f7a3a")):
        me.materials.append(fmats.get(shade, color))
    for poly, idx in zip(me.polygons, face_slot, strict=True):
        poly.material_index = idx
        poly.use_smooth = True
    return me


def add_tag(it, obj, mats, col, fmats=None) -> None:
    """Name written upright on the piece's front (child of the piece): appliances read at a glance.
    On a bed the name is embroidered flat on the duvet, reading from the foot of the bed."""
    w, d, h = it.size
    mat = (fmats or FurnitureMaterials()).get("main", it.tag_color) if it.tag_color else mats["label"]
    if "bed" in it.type.split("-"):
        hb = min(0.08, d * 0.05)
        t = text_object(f"TAG_{it.id}", it.tag, (0.0, 0.0, 0.0), min(0.16, w * 0.14), mat, col)
        t.data.extrude = 0.0015
        t.parent = obj
        t.location = (0.0, (hb + 0.48) / 2 + 0.05, it.tag_z if it.tag_z >= 0 else h)  # middle of the duvet
        t.rotation_euler = (0.0, 0.0, math.pi)  # flat, upright for someone at the foot (+y)
        t.hide_render = False
        t["part_id"], t["tag"] = f"{it.id}/tag", it.tag
        return
    z = it.tag_z if it.tag_z >= 0 else (h - 0.08 if h > 0.25 else h + 0.03)
    size = max(0.035, min(0.07, w * 0.12))
    name = f"TAG_{it.id}"
    t = text_object(name, it.tag, (0.0, 0.0, 0.0), size, mat, col)
    t.parent = obj
    t.location = (0.0, d / 2 + 0.004, z)
    t.rotation_euler = (math.pi / 2, 0.0, math.pi)  # upright, reading from the front (+y)
    t.hide_render = False
    t["part_id"], t["tag"] = f"{it.id}/tag", it.tag


def add_apron(it, obj, mats, finishes, col) -> None:
    """Tiled front of a bathtub: own object (child) with the wall-tile material, origin at its left end
    so the tile layout starts there."""
    f = tinted_finish(finishes[it.apron], it.apron_color)  # the owner's / style's colour for this wallpaper
    key = f"wall_{f.name}"
    if key not in mats:
        mats[key] = finish_material(f, vertical=True)
    x1, y1, z1, x2, y2, z2 = apron_box(it)
    name = f"APRON_{it.id}"
    ap = boxes_object(name, [(x1, y1, z1, x2, y2, z2)], mats[key], col, (x1, y1, 0.0))
    ap.parent = obj
    ap["part_id"], ap["finish"] = f"{it.id}/apron", it.apron


def build_furniture(variants, mats, col, fmats: FurnitureMaterials, finishes=None, ceiling_height=2.7) -> None:
    """One child collection per variant ('Variant A'...), one FURN_<id> object per piece.

    Object origin = footprint centre on its underside, so location/rotation mirror the data.
    Storage pieces get openable fronts + interior fittings as child objects (build_storage).
    The add-on's variant switcher only toggles collection visibility - the view never moves.
    """
    for v in variants:
        vcol = collection(f"Variant {v.key}", col)
        vcol["variant_key"], vcol["variant_name"], vcol["wall_color"] = v.key, v.name, v.wall_color
        vcol["description"] = v.description
        vcol["style_of"] = v.style_of  # add-on: a style of that layout -> listed in the Style dropdown
        fmats.true_colors = v.true_colors
        drops = {rid: rf.stretch_drop for rid, rf in v.rooms.items() if rf.stretch_ceiling}
        for it in v.items:
            name = f"FURN_{it.id}"
            if it.is_storage:
                obj = build_storage(it, name, fmats, vcol)
            else:
                parts = item_parts(it.type, *it.size, mirror=it.mirror)
                if is_light(it.type):  # the diffuser glows in the light's colour
                    parts = [p._replace(color=light_of(it).color) if p.shade == "emit" else p for p in parts]
                parts = recolored_parts(it, parts)  # the piece's own metal / accent for the shape's built-in ones
                me = (bird_of_paradise_mesh(name, it, fmats) if it.type.endswith("bird-of-paradise")
                      else parts_mesh(name, parts, it.color, fmats))
                obj = link(bpy.data.objects.new(name, me), vcol)
                if it.track is not None:
                    drop = drops.get(it.room, 0.0) if ceiling_mounted(it, ceiling_height) else 0.0
                    add_track_heads(it, vcol, fmats, -drop)
                elif is_light(it.type):
                    add_light(it, obj, vcol)
                if it.apron:
                    add_apron(it, obj, mats, finishes or {}, vcol)
            drop = drops.get(it.room, 0.0) if ceiling_mounted(it, ceiling_height) else 0.0
            obj.location = (it.position[0], it.position[1], it.elevation - drop)  # onto a stretch ceiling
            obj.rotation_euler.z = math.radians(it.rotation)
            if drop:
                obj["lowered_by_stretch_ceiling"] = drop
            if it.tag:
                add_tag(it, obj, mats, vcol, fmats)
            obj["furniture_id"], obj["variant"], obj["type"], obj["room_id"] = it.id, v.key, it.type, it.room
            obj["label"], obj["status"], obj["size"] = it.label, it.status, list(it.size)
            if it.note:
                obj["note"] = it.note
    mats["wall"]["default_color"] = list(mats["wall"].diffuse_color)[:3]


def build_stretch_ceiling(apt, v, rid, rf, vcol, fmats) -> None:
    """Floating stretch (Barrisol-type) ceiling: white membrane rf.stretch_drop under the slab, short of every
    walled edge by rf.stretch_gap; in each gap a glowing LED line at the slab + a rectangle light grazing the
    wall. All parts carry ceiling_skin (they follow the ceiling mode); lights/glow follow 'Lights on'."""
    h = apt.levels.ceiling_height
    room = apt.room(rid)
    poly = list(room.polygon)
    walled = walled_edges(poly, [w.rect for w in apt.walls])
    gap = rf.stretch_gap
    inner = inset_rectilinear(poly, [gap if wd else 0.0 for wd in walled])
    z = h - rf.stretch_drop
    key = f"MAT_stretch_{rf.stretch_color[1:].lower()}"
    mat = bpy.data.materials.get(key) or principled(key, srgb_to_linear(rf.stretch_color), roughness=0.32)
    corner = (min(p[0] for p in poly), min(p[1] for p in poly))
    me = bpy.data.meshes.new(f"STRETCH_{v.key}_{rid}")  # thin slab: 1 cm membrane + profile
    bm = bmesh.new()
    vb = [bm.verts.new((x - corner[0], y - corner[1], 0.0)) for x, y in inner]
    face = bm.faces.new(vb)
    bmesh.ops.extrude_face_region(bm, geom=[face])
    for vert in bm.verts[len(vb):]:
        vert.co.z = 0.01
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    obj = link(bpy.data.objects.new(f"STRETCH_{v.key}_{rid}", me), vcol)
    obj.location = (corner[0], corner[1], z)
    obj["room_id"], obj["variant"], obj["ceiling_skin"], obj["stretch_ceiling"] = rid, v.key, True, True
    if not gap:
        return
    emit = fmats.get("emit", rf.stretch_led_color)
    for i, (a, b) in enumerate(zip(poly, [*poly[1:], poly[0]], strict=True)):
        if not walled[i]:
            continue
        n = inward_normals(poly)[i]
        length = math.dist(a, b)
        cx, cy = (a[0] + b[0]) / 2 + n[0] * gap / 2, (a[1] + b[1]) / 2 + n[1] * gap / 2
        along_x = abs(a[1] - b[1]) < 1e-6
        sx, sy = (length, gap) if along_x else (gap, length)
        name = f"STRETCH_LED_{v.key}_{rid}_{i + 1}"
        glow = boxes_object(name, [(cx - sx / 2, cy - sy / 2, h - 0.008, cx + sx / 2, cy + sy / 2, h - 0.002)], emit,
                            vcol, (cx, cy, 0.0))
        glow["ceiling_skin"], glow["room_id"], glow["variant"] = True, rid, v.key
        glow.visible_shadow = False
        data = bpy.data.lights.new(name.replace("STRETCH_LED", "LIGHT_STRETCH"), "AREA")
        data.shape, data.size, data.size_y = "RECTANGLE", sx, sy
        data.energy = rf.stretch_led_w_per_m * length
        data.color = srgb_to_linear(rf.stretch_led_color)
        data.use_shadow = False  # light budget (ADR 0008)
        data.use_custom_distance, data.cutoff_distance = True, 3.0
        lo = link(bpy.data.objects.new(data.name, data), vcol)
        lo.location = (cx, cy, z - 0.005)  # just under the membrane edge, shining down the wall
        lo["furniture_light"], lo["room_id"], lo["variant"] = True, rid, v.key


def build_variant_finishes(apt, variants, mats, furniture_col, fmats=None) -> None:
    """A variant's own floors / wall / ceiling tiles per room ([rooms.<id>], ADR 0009), in that variant's
    collection so the variant switch shows them with its furniture. Floor = room polygon just above the shell
    floor; walls = 1 cm tile skin inside the room up to walls_height (door openings left open); ceiling = room
    polygon just under the ceiling (prop ceiling_skin: it follows the add-on's ceiling mode like the ceiling)."""
    h = apt.levels.ceiling_height
    walls = [(w.rect, w.horizontal, [(o.span[0], o.span[1], o.sill, o.head) for o in apt.openings_in(w.id)])
             for w in apt.walls]
    for v in variants:
        vcol = furniture_col.children.get(f"Variant {v.key}")
        for rid, rf in v.rooms.items():
            room = apt.room(rid)
            corner = (min(p[0] for p in room.polygon), min(p[1] for p in room.polygon))  # layouts start here
            # balcony: a deck sits on its slab (z = balcony floor) and is raised to ~0, the furniture level
            fz = apt.levels.balcony_floor_z + 0.028 if apt.balcony and rid == apt.balcony.id else 0.004
            floor = rf.floor or (room.finish if rf.floor_color else "")
            if floor:
                ff = tinted_finish(apt.finishes[floor], rf.floor_color)
                if ff.name not in mats:
                    mats[ff.name] = finish_material(ff)
                obj = polygon_object(f"FINISH_{v.key}_floor_{rid}", room.polygon, fz, mats[ff.name], vcol, corner)
                obj["room_id"], obj["finish"], obj["variant"] = rid, floor, v.key
            if rf.walls:
                wf = tinted_finish(apt.finishes[rf.walls], rf.walls_color)
                key = f"wall_{wf.name}"
                if key not in mats:
                    mats[key] = finish_material(wf, vertical=True)
                skins = cladding_walls(room.polygon, walls, rf.walls_height or h, 0.01, walled_only=True)  # not across open passages
                for n, (o, boxes) in enumerate(skins, start=1):  # one object per wall: full tile at its corner
                    obj = boxes_object(f"FINISH_{v.key}_walls_{rid}_{n}", boxes, mats[key], vcol, (o[0], o[1], 0.0))
                    obj["room_id"], obj["finish"], obj["variant"] = rid, rf.walls, v.key
            elif rf.paint:  # the room's own wall colour: a 2 mm painted skin on real walls only (wallpaper panels,
                # 4 mm, stay in front; open passages between rooms - hall / living - stay open)
                key = f"paint_{rf.paint.lstrip('#').lower()}"
                if key not in mats:
                    mats[key] = principled(f"MAT_wall_paint_{rf.paint.lstrip('#').lower()}", srgb_to_linear(rf.paint),
                                           roughness=0.85)
                skins = cladding_walls(room.polygon, walls, h, 0.002, walled_only=True)  # open passages stay open
                for n, (o, boxes) in enumerate(skins, start=1):
                    obj = boxes_object(f"FINISH_{v.key}_paint_{rid}_{n}", boxes, mats[key], vcol, (o[0], o[1], 0.0))
                    obj["room_id"], obj["paint"], obj["variant"] = rid, rf.paint, v.key
            if rf.ceiling:
                obj = polygon_object(f"FINISH_{v.key}_ceiling_{rid}", room.polygon, h - 0.004, mats[rf.ceiling], vcol,
                                     corner)
                obj["room_id"], obj["finish"], obj["variant"], obj["ceiling_skin"] = rid, rf.ceiling, v.key, True
            if rf.stretch_ceiling:
                build_stretch_ceiling(apt, v, rid, rf, vcol, fmats or FurnitureMaterials())
            if rf.skirting:  # wooden skirting board along the real walls, cut at doors, none across open passages
                mat = (fmats or FurnitureMaterials()).get("main", rf.skirting)
                skirt = [b for _, bx in cladding_walls(room.polygon, walls, rf.skirting_height, 0.012, walled_only=True)
                         for b in bx]
                if skirt:
                    obj = boxes_object(f"SKIRTING_{v.key}_{rid}", skirt, mat, vcol)
                    obj["room_id"], obj["variant"], obj["skirting"] = rid, v.key, True


def build_built_ins(apt, col, fmats: FurnitureMaterials) -> None:
    """Equipment the apartment already has (boiler...) - outside the variants, so every variant shows it."""
    for b in apt.built_ins:
        name = f"BUILTIN_{b.id}"
        obj = link(bpy.data.objects.new(name, parts_mesh(name, item_parts(b.type, *b.size), b.color, fmats)), col)
        obj.location = (b.position[0], b.position[1], b.elevation)
        obj.rotation_euler.z = math.radians(b.rotation)
        obj["built_in_id"], obj["type"], obj["room_id"], obj["label"] = b.id, b.type, b.room, b.label
        obj["status"], obj["size"], obj["note"] = b.status, list(b.size), b.note


def look_at(obj, target: Vector) -> None:
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (target - obj.location).to_track_quat("-Z", "Y")


def build_cameras(apt, col) -> None:
    for i, r in enumerate(apt.all_rooms()):
        if not r.camera:
            continue
        cam = bpy.data.cameras.new(f"CAM_{r.id}")
        cam.lens, cam.clip_start, cam.clip_end = ROOM_LENS, 0.05, 100
        obj = link(bpy.data.objects.new(f"CAM_{r.id}", cam), col)
        z0 = apt.levels.balcony_floor_z if r.id == "balcony" else 0.0
        obj.location = (*r.camera.eye, z0 + EYE_HEIGHT)
        look_at(obj, Vector((*r.camera.look_at, z0 + LOOK_HEIGHT)))
        obj["room_id"], obj["room_name"], obj["order"] = r.id, r.name, i

    xs = [v for w in apt.walls for v in (w.rect[0], w.rect[2])] + [p[0] for r in apt.all_rooms() for p in r.polygon]
    ys = [v for w in apt.walls for v in (w.rect[1], w.rect[3])] + [p[1] for r in apt.all_rooms() for p in r.polygon]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    plan = bpy.data.cameras.new("CAM_plan")
    plan.type, plan.ortho_scale, plan.clip_end = "ORTHO", max(max(xs) - min(xs), max(ys) - min(ys)) * 1.08, 100
    obj = link(bpy.data.objects.new("CAM_plan", plan), col)
    obj.location = (cx, cy, 30.0)
    obj["view"] = "plan"

    ov = bpy.data.cameras.new("CAM_overview")
    ov.lens, ov.clip_end = 35, 200
    obj = link(bpy.data.objects.new("CAM_overview", ov), col)
    obj.location = (cx + 10.0, cy - 14.0, 17.0)
    look_at(obj, Vector((cx, cy, 0.5)))
    obj["view"] = "overview"
    bpy.context.scene.camera = obj


def build_reflection_probes(apt, col) -> None:
    """One sphere reflection probe per room so mirrors / glossy tiles reflect the room in EEVEE
    (screen-space reflections alone leave black patches where the reflected view is off screen)."""
    kinds = [i.identifier for i in bpy.types.LightProbe.bl_rna.properties["type"].enum_items]
    kind = "SPHERE" if "SPHERE" in kinds else "CUBE"
    for r in apt.rooms:
        cx, cy = polygon_centroid(r.polygon)
        xs, ys = [p[0] for p in r.polygon], [p[1] for p in r.polygon]
        data = bpy.data.lightprobes.new(f"PROBE_{r.id}", kind)
        data.influence_distance = max(max(xs) - min(xs), max(ys) - min(ys)) * 0.75
        obj = link(bpy.data.objects.new(f"PROBE_{r.id}", data), col)
        obj.location = (cx, cy, apt.levels.ceiling_height / 2)
        obj["room_id"] = r.id


def build_lighting(apt) -> None:
    sc = bpy.context.scene
    light = bpy.data.lights.new("Sun", "SUN")
    light.angle = math.radians(0.53)  # real solar disc -> realistic penumbra
    light.color = (1.0, 0.97, 0.92)
    sun = bpy.data.objects.new("Sun", light)
    col = bpy.data.collections.get("Lighting")
    col.objects.link(sun)

    world = bpy.data.worlds.new("World_sky")
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_disc = False  # direct sun comes from the Sun lamp
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    sc.world = world

    s = sc.apt
    s.project_root = str(ROOT)
    s.latitude, s.longitude = apt.site.latitude, apt.site.longitude
    s.utc_offset_standard, s.plus_y_bearing = apt.site.utc_offset_standard, apt.site.plus_y_bearing
    s.year, s.month, s.day, s.hour = 2026, 6, 21, 17.0


def configure_render() -> None:
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    ee = sc.eevee
    ee.use_shadows = True
    ee.use_raytracing = True
    ee.shadow_ray_count = 2
    ee.shadow_step_count = 8
    ee.taa_render_samples = 64
    # interactive budget (ADR 0008): many fixtures must stay smooth in Material Preview / Rendered.
    # render_views.py raises shadow resolution back to 1.0 for final images.
    ee.shadow_resolution_scale = 0.5
    ee.gi_cubemap_resolution = "256"
    ee.use_shadow_jitter_viewport = False
    ee.use_fast_gi = True
    ee.fast_gi_distance = 0.0  # unlimited bounce distance for interiors
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
    vs = sc.view_settings
    try:
        vs.view_transform = "AgX"
        vs.look = "AgX - Base Contrast"
    except TypeError:
        pass
    vs.exposure = 1.3
    if hasattr(vs, "use_white_balance"):  # neutralise the blue sky fill like a camera would
        vs.use_white_balance = True
        vs.white_balance_temperature = 7800
        vs.white_balance_tint = 0
    if hasattr(sc, "cycles"):
        sc.cycles.samples = 128
        sc.cycles.use_denoising = True
    # timeline for the day animation: 06:00 -> 21:00 every 15 min
    sc.frame_start, sc.frame_end = 1, 61


def configure_viewports(apt=None) -> None:
    """3D views: material shading, no gizmos; open at [start_view] (e.g. the entrance door) or the overview."""
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            sp = area.spaces.active
            sp.shading.type = "MATERIAL"
            sp.shading.use_scene_lights = True
            sp.shading.use_scene_world = True
            sp.clip_start = 0.05
            sp.overlay.show_floor = False
            sp.overlay.show_ortho_grid = False
            sp.overlay.show_axis_x = sp.overlay.show_axis_y = False
            sp.overlay.show_extras = False  # rule: no light / probe / camera gizmos (ADR 0008)
            rv = sp.region_3d
            rv.view_perspective = "PERSP"
            if apt is not None and apt.start_view is not None:  # standing in the doorway, eye height
                eye = Vector((*apt.start_view.eye, 1.6))
                target = Vector((*apt.start_view.look_at, 1.35))
                rv.view_rotation = (target - eye).to_track_quat("-Z", "Y")
                rv.view_distance = 0.5
                rv.view_location = eye + rv.view_rotation @ Vector((0, 0, -0.5))
                sp.lens = 18
                sp.clip_start = 0.02
                continue
            cam = bpy.data.objects["CAM_overview"]
            rv.view_rotation = cam.matrix_world.to_quaternion()
            rv.view_distance = 22.0
            rv.view_location = cam.matrix_world.translation + cam.matrix_world.to_quaternion() @ Vector((0, 0, -22.0))


# =============================================================================
def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="")
    ap.add_argument("--variants-dir", default="")
    ap.add_argument("--out", default=str(ROOT / "models" / "apartment.blend"))
    a = ap.parse_args(argv)

    apt = load(a.data or None)
    variants = load_variants(a.variants_dir or None)
    reset_scene()

    import apartment_tools  # the add-on (register it so its scene settings are saved in the file)

    try:
        apartment_tools.register()
    except ValueError:
        pass  # already registered

    root = collection("Apartment")
    cols = {name: collection(name, root)
            for name in ("Walls", "Floors", "Ceiling", "Openings", "Balcony", "Structure", "Built-ins")}
    cols["Context"] = collection("Context")
    cols["Annotations"] = collection("Annotations")
    cols["Furniture"] = collection("Furniture")
    cols["Cameras"] = collection("Cameras")
    cols["Lighting"] = collection("Lighting")

    merge_variant_finishes(apt, variants)  # variants' own [finishes] (validated by `apartment validate`)
    mats = build_materials(apt.finishes)
    build_walls(apt, mats, cols["Walls"])
    build_windows(apt, mats, cols["Openings"])
    build_door_frames(apt, cols["Openings"])
    build_floors(apt, mats, cols["Floors"], cols["Structure"])
    build_ceiling(apt, mats, cols["Ceiling"])
    build_balcony(apt, mats, cols["Balcony"], cols["Context"])
    build_building(apt, mats, cols["Context"])
    build_annotations(apt, mats, cols["Annotations"])
    build_plan_symbols(apt, mats, cols["Annotations"])
    build_fixed_points(apt, mats, cols["Annotations"])
    fmats = FurnitureMaterials()
    build_built_ins(apt, cols["Built-ins"], fmats)
    build_furniture(variants, mats, cols["Furniture"], fmats, apt.finishes, apt.levels.ceiling_height)
    build_variant_finishes(apt, variants, mats, cols["Furniture"], fmats)
    build_cameras(apt, cols["Cameras"])
    build_lighting(apt)
    build_reflection_probes(apt, cols["Lighting"])
    configure_render()
    configure_viewports(apt)

    from apartment_tools.sun import update_sun

    update_sun(bpy.context.scene)
    sc = bpy.context.scene
    if variants:
        from apartment_tools.ops import apply_variant

        keys = [v.key for v in variants]  # [start_view] variant, else the first one
        sc.apt.variant = apt.start_variant if apt.start_variant in keys else keys[0]
        apply_variant(sc)
    from apartment_tools.ops import apply_lights

    sc.apt.lights_on = True  # fixtures switched on in a fresh file (the panel toggles them)
    apply_lights(sc)
    sc["source"] = str(apt.source)
    if apt.start_view is not None:  # the add-on puts the 3D views here on every file load
        sc["start_view"] = [*apt.start_view.eye, 1.6, *apt.start_view.look_at, 1.35]
    sc["generated_by"] = "blender/build_scene.py - do not hand-edit generated objects"

    # cameras are used by the panel/renders, but their frames clutter the walk-through view
    vl = bpy.context.view_layer.layer_collection
    for name in ("Cameras",):
        vl.children[name].hide_viewport = True

    for o in bpy.data.objects:  # open with nothing selected (no orange outlines everywhere)
        o.select_set(False)
    bpy.context.view_layer.objects.active = None

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
    s = sc.apt
    print(f"[build] saved {out}  ({len(bpy.data.objects)} objects)  sun az {s.info_azimuth:.1f} el {s.info_elevation:.1f}")


if __name__ == "__main__":
    main()
