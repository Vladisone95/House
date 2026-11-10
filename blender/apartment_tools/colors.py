"""Colour picker for the owner (ADR 0011): recolour a piece or a room's floor / paint / wall tiles in Blender.

The change is shown at once (the piece's materials are copied and recoloured - other pieces sharing a material
keep theirs) and saved into data/variants/<KEY>.toml through apartment_core, listed in the variant's
``owner_colors`` so a regenerated style keeps it. The TOML stays the source of truth: a rebuild gives the same.
"""

from __future__ import annotations

from pathlib import Path

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatVectorProperty, StringProperty

from .ops import piece_of

MAX_FRONTS = 8
LIGHTEN = (0.0, 0.1, 0.18, 0.25, 0.3, 0.45, 0.55, 0.6, 0.62)  # every way the build derives a shade from a colour


# --------------------------------------------------------------------------- colour helpers
def _hex(rgb) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02x}" for c in rgb[:3])


def _rgb(hx: str) -> tuple[float, float, float]:
    return tuple(int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5))


def _lin(hx: str, lighten: float = 0.0, scale: float = 1.0) -> tuple[float, float, float]:
    out = []
    for c in _rgb(hx):
        c = c + (1 - c) * lighten
        out.append((c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4) * scale)
    return tuple(out)


def _variants():
    out = []
    for lt in LIGHTEN:
        out.append((lt, 1.0))
    out.append((0.0, 0.25))  # the "dark" shade
    return out


def _swap_in_material(mat, pairs: list[tuple[str, str]]) -> bool:
    """Replace every colour value derived from an old colour by the same derivation of the new one."""
    if not mat or not mat.use_nodes:
        return False
    table = [(_lin(o, lt, sc), _lin(n, lt, sc)) for o, n in pairs for lt, sc in _variants()]

    def match(val):
        for old, new in table:
            if all(abs(a - b) < 2e-3 for a, b in zip(val[:3], old, strict=True)):
                return new
        return None

    hit = False
    for node in mat.node_tree.nodes:
        for sock in node.inputs:
            if sock.type == "RGBA" and not sock.is_linked and (new := match(sock.default_value)):
                sock.default_value = (*new, sock.default_value[3])
                hit = True
        if node.type == "VALTORGB":
            for el in node.color_ramp.elements:
                if new := match(el.color):
                    el.color = (*new, el.color[3])
                    hit = True
    if hit and (new := match(mat.diffuse_color)):
        mat.diffuse_color = (*new, mat.diffuse_color[3])
    return hit


def recolor_objects(objs, pairs: list[tuple[str, str]]) -> int:
    """Recolour these objects only: each touched material is copied first (shared materials stay as they are)."""
    pairs = [(o.lower(), n.lower()) for o, n in pairs if o and n and o.lower() != n.lower()]
    if not pairs:
        return 0
    done = 0
    for ob in objs:
        for slot in getattr(ob, "material_slots", []):
            m = slot.material
            if m is None:
                continue
            probe = m.copy()
            if _swap_in_material(probe, pairs):
                probe.name = f"{m.name}~{pairs[0][1][1:]}"
                slot.material = probe
                done += 1
            else:
                bpy.data.materials.remove(probe)
    return done


# --------------------------------------------------------------------------- data (apartment_core)
def _core(context):
    from ._core import ensure_core

    ensure_core(context.scene.apt.project_root)
    from apartment_core import furniture, load

    return furniture, load


def _root(context) -> Path:
    s = context.scene.apt
    return Path(s.project_root) if s.project_root else Path(__file__).resolve().parents[2]


def _variant_file(context, key: str) -> Path:
    return _root(context) / "data" / "variants" / f"{key}.toml"


def _save(context, furniture, v, edits: list[tuple[str, str]]) -> None:
    for path, color in edits:
        furniture.set_color(v, path, color)
    _variant_file(context, v.key).write_text(furniture.variant_to_toml(v), encoding="utf-8")


# --------------------------------------------------------------------------- piece colours
class APT_OT_piece_colors(bpy.types.Operator):
    """Change the selected piece's colours (body, fronts, handles, metal, accent, wallpaper / tiles) - shown at once
    and saved into its variant file"""

    bl_idname = "apt.piece_colors"
    bl_label = "Piece colours"
    bl_options = {"REGISTER", "UNDO"}

    piece_id: StringProperty()
    main: FloatVectorProperty(name="Colour", subtype="COLOR_GAMMA", min=0, max=1)
    accent: FloatVectorProperty(name="Accent (base / feet / duvet / curb)", subtype="COLOR_GAMMA", min=0, max=1)
    cushion: FloatVectorProperty(name="Throw cushions", subtype="COLOR_GAMMA", min=0, max=1)
    has_cushion: BoolProperty()
    metal: FloatVectorProperty(name="Metal (taps, frames, legs)", subtype="COLOR_GAMMA", min=0, max=1)
    apron: FloatVectorProperty(name="Wallpaper / tiles", subtype="COLOR_GAMMA", min=0, max=1)
    handle: FloatVectorProperty(name="Handles", subtype="COLOR_GAMMA", min=0, max=1)
    interior: FloatVectorProperty(name="Inside", subtype="COLOR_GAMMA", min=0, max=1)
    has_accent: BoolProperty()
    has_metal: BoolProperty()
    has_apron: BoolProperty()
    has_storage: BoolProperty()
    n_fronts: bpy.props.IntProperty()
    initial: StringProperty()  # "field=#hex;..." as loaded
    for _k in range(MAX_FRONTS):
        __annotations__[f"front{_k}"] = FloatVectorProperty(name=f"Fronts m{_k + 1}", subtype="COLOR_GAMMA", min=0,
                                                            max=1)
    del _k

    @classmethod
    def poll(cls, context):
        return piece_of(context.active_object) is not None

    def _current(self, furniture, apt, it) -> dict[str, str]:
        from apartment_core.furniture import ACCENTS, BRASS, CUSHIONS, item_parts

        cur = {"color": it.color}
        builtin = set() if it.is_storage else {p.color.lower() for p in item_parts(it.type, *it.size, mirror=it.mirror)}
        if BRASS in builtin:
            cur["metal"] = it.metal or BRASS
        if builtin & set(ACCENTS):
            cur["accent"] = it.accent or next(c for c in ACCENTS if c in builtin)
        if builtin & set(CUSHIONS):
            cur["cushion"] = it.cushion or CUSHIONS[0]
        if it.apron and it.apron in apt.finishes:
            cur["apron_color"] = it.apron_color or apt.finishes[it.apron].color
        if it.is_storage and it.storage is not None:
            st = it.storage
            cur["handle_color"] = st.handle_color
            cur["interior_color"] = st.interior_color or it.color
            for k, m in enumerate(st.modules[:MAX_FRONTS]):
                cur[f"front_color:{k}"] = m.front_color or it.color
        return cur

    def invoke(self, context, event):
        furniture, load = _core(context)
        piece = piece_of(context.active_object)
        self.piece_id = piece["furniture_id"]
        key = self.piece_id.split(".", 1)[0]
        v = furniture.load_variant(_variant_file(context, key))
        apt = load(_root(context) / "data" / "apartment.toml")
        furniture.merge_variant_finishes(apt, [v])
        it = v.item(self.piece_id)
        if it.is_storage and it.storage is None:
            self.report({"WARNING"}, "Automatic storage modules: colour of the whole piece only")
        cur = self._current(furniture, apt, it)
        self.initial = ";".join(f"{k}={c}" for k, c in cur.items())
        self.main = _rgb(cur["color"])
        self.has_metal, self.has_accent, self.has_cushion = "metal" in cur, "accent" in cur, "cushion" in cur
        self.has_apron, self.has_storage = "apron_color" in cur, "handle_color" in cur
        for k, attr in (("metal", "metal"), ("accent", "accent"), ("cushion", "cushion"), ("apron_color", "apron"),
                        ("handle_color", "handle"), ("interior_color", "interior")):
            if k in cur:
                setattr(self, attr, _rgb(cur[k]))
        self.n_fronts = sum(1 for k in cur if k.startswith("front_color:"))
        for k in range(self.n_fronts):
            setattr(self, f"front{k}", _rgb(cur[f"front_color:{k}"]))
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        lay = self.layout
        lay.label(text=self.piece_id, icon="OBJECT_DATA")
        lay.prop(self, "main")
        for flag, attr in (("has_accent", "accent"), ("has_cushion", "cushion"), ("has_metal", "metal"),
                           ("has_apron", "apron")):
            if getattr(self, flag):
                lay.prop(self, attr)
        if self.has_storage:
            for k in range(self.n_fronts):
                lay.prop(self, f"front{k}")
            lay.prop(self, "handle")
            lay.prop(self, "interior")
        lay.label(text="Saved into the variant file (kept when styles regenerate)", icon="INFO")

    def execute(self, context):
        furniture, load = _core(context)
        initial = dict(kv.split("=") for kv in self.initial.split(";") if kv)
        picked = {"color": _hex(self.main)}
        for k, attr in (("metal", "metal"), ("accent", "accent"), ("cushion", "cushion"), ("apron_color", "apron"),
                        ("handle_color", "handle"), ("interior_color", "interior")):
            if k in initial:
                picked[k] = _hex(getattr(self, attr))
        for k in range(self.n_fronts):
            picked[f"front_color:{k}"] = _hex(getattr(self, f"front{k}"))
        changed = {k: c for k, c in picked.items() if c.lower() != initial.get(k, "").lower()}
        if not changed:
            return {"CANCELLED"}
        key, local = self.piece_id.split(".", 1)
        v = furniture.load_variant(_variant_file(context, key))
        _save(context, furniture, v, [(f"{local}/{k}", c) for k, c in changed.items()])
        piece = bpy.data.objects.get(f"FURN_{self.piece_id}")
        objs = [piece, *piece.children_recursive] if piece else []
        pairs = []
        for k, c in changed.items():
            if k == "accent":
                from apartment_core.furniture import ACCENTS

                pairs += [(a, c) for a in ACCENTS]
            elif k == "cushion":
                from apartment_core.furniture import CUSHIONS, shift_color

                old = initial[k]
                pairs += [(shift_color(old, CUSHIONS[0], t), shift_color(c, CUSHIONS[0], t)) for t in CUSHIONS]
            elif k == "apron_color":
                objs_ap = [o for o in objs if o.name.startswith("APRON_")]
                apt = load(_root(context) / "data" / "apartment.toml")
                furniture.merge_variant_finishes(apt, [v])
                it = v.item(self.piece_id)
                f = apt.finishes[it.apron]
                old = furniture.tinted_finish(f, initial[k])
                new = furniture.tinted_finish(f, c)
                recolor_objects(objs_ap, [(old.color, new.color), (old.color2, new.color2),
                                          (old.joint_color, new.joint_color)])
            else:
                pairs.append((initial[k], c))
        recolor_objects([o for o in objs if not o.name.startswith("APRON_")], pairs)
        self.report({"INFO"}, f"{self.piece_id}: {', '.join(changed)} saved to {key}.toml")
        return {"FINISHED"}


# --------------------------------------------------------------------------- room colours
def _room_items(self, context):
    try:
        furniture, load = _core(context)
        apt = load(_root(context) / "data" / "apartment.toml")
        return [(r.id, r.name, "") for r in apt.all_rooms()]
    except Exception:  # noqa: BLE001 - the menu must always draw
        return [("living", "Living", "")]


class APT_OT_room_colors(bpy.types.Operator):
    """Change a room's floor, wall paint or wall-tile colour in the shown variant - shown at once, saved"""

    bl_idname = "apt.room_colors"
    bl_label = "Room colours"
    bl_options = {"REGISTER", "UNDO"}

    room: EnumProperty(name="Room", items=_room_items)
    floor: FloatVectorProperty(name="Floor", subtype="COLOR_GAMMA", min=0, max=1)
    paint: FloatVectorProperty(name="Wall paint", subtype="COLOR_GAMMA", min=0, max=1)
    tiles: FloatVectorProperty(name="Wall tiles", subtype="COLOR_GAMMA", min=0, max=1)
    has_tiles: BoolProperty()
    initial: StringProperty()

    def _load(self, context):
        furniture, load = _core(context)
        key = context.scene.apt.variant
        v = furniture.load_variant(_variant_file(context, key))
        apt = load(_root(context) / "data" / "apartment.toml")
        furniture.merge_variant_finishes(apt, [v])
        return furniture, apt, v

    def invoke(self, context, event):
        furniture, apt, v = self._load(context)
        rf = v.rooms.get(self.room, furniture.RoomFinish())
        room = apt.room(self.room)
        floor_name = rf.floor or room.finish
        cur = {"floor_color": rf.floor_color or (apt.finishes[floor_name].color if floor_name in apt.finishes
                                                 else "#cccccc"),
               "paint": rf.paint or v.wall_color or "#d9d6cf"}
        self.has_tiles = bool(rf.walls)
        if rf.walls:
            cur["walls_color"] = rf.walls_color or apt.finishes[rf.walls].color
            self.tiles = _rgb(cur["walls_color"])
        self.floor, self.paint = _rgb(cur["floor_color"]), _rgb(cur["paint"])
        self.initial = ";".join(f"{k}={c}" for k, c in cur.items())
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        lay = self.layout
        lay.label(text=f"{context.scene.apt.variant} - {self.room}", icon="HOME")
        lay.prop(self, "floor")
        if self.has_tiles:
            lay.prop(self, "tiles")
        else:
            lay.prop(self, "paint")

    def execute(self, context):
        furniture, apt, v = self._load(context)
        initial = dict(kv.split("=") for kv in self.initial.split(";") if kv)
        picked = {"floor_color": _hex(self.floor)}
        picked["walls_color" if self.has_tiles else "paint"] = _hex(self.tiles if self.has_tiles else self.paint)
        changed = {k: c for k, c in picked.items() if c.lower() != initial.get(k, "").lower()}
        if not changed:
            return {"CANCELLED"}
        rf = v.rooms.get(self.room, furniture.RoomFinish())
        _save(context, furniture, v, [(f"rooms.{self.room}/{k}", c) for k, c in changed.items()])
        key, missing = v.key, []
        for k, c in changed.items():
            if k == "paint":
                objs = [o for o in bpy.data.objects if o.name.startswith(f"FINISH_{key}_paint_{self.room}_")]
                if objs:
                    recolor_objects(objs, [(initial[k], c)])
                else:
                    missing.append("paint")
                continue
            prefix = f"FINISH_{key}_floor_{self.room}" if k == "floor_color" else f"FINISH_{key}_walls_{self.room}_"
            objs = [o for o in bpy.data.objects if o.name.startswith(prefix)]
            name = (rf.floor or apt.room(self.room).finish) if k == "floor_color" else rf.walls
            f = apt.finishes.get(name)
            if not objs or f is None:
                missing.append(k)
                continue
            old, new = furniture.tinted_finish(f, initial[k]), furniture.tinted_finish(f, c)
            recolor_objects(objs, [(old.color, new.color), (old.color2, new.color2), (old.joint_color, new.joint_color)])
        msg = f"{key} {self.room}: {', '.join(changed)} saved"
        if missing:
            msg += f" - rebuild to see {', '.join(missing)} (uv run apartment build)"
        self.report({"INFO"}, msg)
        return {"FINISHED"}


CLASSES = (APT_OT_piece_colors, APT_OT_room_colors)
