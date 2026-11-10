"""Furniture variants - typed model of ``data/variants/<KEY>.toml`` (pure Python).

A *variant* is one complete furnishing of the fixed shell: its own pieces, colours and wall
paint. Every piece has an id that is unique across ALL variants and readable by a human:

    <VARIANT>.<type>-<room-slug>-<n>        e.g.  A.sofa-living-1, B.mirror-master-bathroom-1

Local frame of a piece: x along its width, y along its depth, back at -depth/2, front at
+depth/2. ``rotation`` turns it counter-clockwise (degrees): 0 = front faces +Y (towards
facade A), 90 = -X, 180 = -Y, 270 = +X. ``position`` is the centre of the footprint.

*Storage* pieces (wardrobes, cabinets, nightstands, vanities... see ``STORAGE_WORDS``) are made of
modules (left -> right as seen from the front), each with fronts (doors / drawers / flap / open)
and optional interior fittings (shelves, hanging rails, inner drawers, dividers). In Blender the
fronts open; parts are addressed as ``<id>/m<k>`` and ``<id>/m<k>/<kind>-<n>``, e.g.
``DEV.wardrobe-living-1/m2/shelf-1`` (ADR 0006).

*Fixed service points* (``[[fixed_points]]`` in apartment.toml: water/drains, WC stacks, the
washing-machine connection, the hood vent) are enforced here: a sink, WC, washing machine,
cooker hood... must sit on a point that serves its type, in every variant.
"""

from __future__ import annotations

import math
import re
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import NamedTuple

from .geometry import (
    convex_overlap,
    door_swing,
    offset_convex,
    point_polygon_distance,
    polygon_inside,
    rotated_rect,
)
from .model import PROJECT_ROOT, Apartment, FixedPoint, Point, parse_finish

VARIANTS_DIR = PROJECT_ROOT / "data" / "variants"
KEY_RE = re.compile(r"^[A-Z][A-Z0-9]{0,3}$")
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
SLUG_RE = re.compile(rf"^{SLUG}$")
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
DEFAULT_COLOR = "#b8b0a2"

Box = tuple[float, float, float, float, float, float]  # x1, y1, z1, x2, y2, z2 (local frame)
Point3 = tuple[float, float, float]

# last word of a type that makes a piece *storage* (openable fronts, designable interior)
STORAGE_WORDS = frozenset({
    "wardrobe", "cabinet", "cupboard", "closet", "nightstand", "dresser", "drawers", "chest",
    "sideboard", "console", "vanity", "bookcase", "unit", "pantry",
})
DRAWER_WORDS = frozenset({"nightstand", "dresser", "drawers", "chest", "console"})  # default front
FRONT_KINDS = ("door-left", "door-right", "doors", "drawer", "drawers", "flap", "panel", "open")
FINISHES = ("matte", "gloss", "wood", "glass", "mirror")
FITTING_KINDS = ("shelf", "rail", "drawer", "divider")
# shades the Blender build knows (material looks); colour comes from the piece unless fixed
SHADES = ("main", "soft", "dark", "front", "handle", "interior", "ceramic", "glass", "chrome", "black", "mirror", "plant",
          "emit", "sheer", "fabric", "smoked", "shag")
# last word of a type that makes a piece a *light fixture* (it lights the Blender scene)
LIGHT_WORDS = frozenset({"light", "lamp", "spotlight", "sconce", "strip", "pendant"})
LIGHT_KINDS = ("point", "spot", "area", "rect")  # rect = rectangle of the piece's width x depth (LED strips)
LIGHT_AIMS = ("down", "up")
WARM_WHITE = "#ffe2b8"  # ~3000 K
PANEL = 0.018  # carcass board
FRONT_T = 0.019  # front thickness
GAP = 0.003  # gap around fronts
BACK = 0.008  # back panel


BRASS = "#b08d57"  # the built-in fittings colour of shapes (taps, mirror frames, screen profiles, chair legs)
# built-in second colours a piece's ``accent`` replaces: sofa / armchair wooden base + feet, duvet linen, shower curb
ACCENTS = ("#6b4a33", "#e7dfd2", "#a89886")
CUSHIONS = ("#cdb79a", "#e9dfd0", "#a88f74")  # built-in throw-cushion tones (main, light, dark) a ``cushion`` replaces


def recolored_parts(it, parts: list) -> list:
    """The shape's parts with the piece's own metal / accent instead of the built-in brass / second colours."""
    out = []
    for p in parts:
        c = p.color.lower()
        if it.metal and c == BRASS:
            p = p._replace(color=it.metal)
        elif it.accent and c in ACCENTS:
            p = p._replace(color=it.accent)
        elif it.metal and "sink" in it.type and p.shade in ("chrome", "black"):  # the tap follows the metal
            p = p._replace(shade="handle", color=it.metal)
        elif it.cushion and c in CUSHIONS:
            p = p._replace(color=shift_color(it.cushion, CUSHIONS[0], c))  # same light / dark steps around it
        out.append(p)
    return out


class Part(NamedTuple):
    """One solid of a piece in its local frame. ``shape`` box | cyl (upright cylinder inscribed in the box)
    | ycyl (cylinder lying along y, e.g. a washer door or a shower head facing the room) | xcyl (lying along x)."""

    box: Box
    shade: str
    shape: str = "box"
    color: str = ""  # overrides the piece colour (fronts, handles)
    finish: str = ""  # fronts: matte | gloss | wood | glass | mirror


# --------------------------------------------------------------------------- data classes
@dataclass(frozen=True)
class Front:
    """One front in a module's stack (top -> bottom). ``height`` None = share the rest."""

    kind: str  # FRONT_KINDS
    height: float | None = None
    count: int = 1  # 'drawers': number of equal drawers


@dataclass(frozen=True)
class Fitting:
    """Interior element of a module. Heights are measured from the piece's underside."""

    kind: str  # shelf (z = top surface) | rail (z = axis) | drawer (z = bottom, height) | divider (x)
    z: float = 0.0
    height: float = 0.15
    x: float = 0.0  # divider: distance from the module's inner left side


@dataclass(frozen=True)
class Module:
    width: float
    fronts: tuple[Front, ...] = (Front("door-left"),)
    finish: str = "matte"
    front_color: str = ""  # "" = the piece's colour
    interior: tuple[Fitting, ...] = ()
    label: str = ""


@dataclass(frozen=True)
class Light:
    """The light a fixture gives. ``watts`` = Blender light power (not the bulb's rating)."""

    kind: str = "point"  # point | spot | area (area = disk of ``size`` m, facing down)
    watts: float = 40.0
    color: str = WARM_WHITE
    size: float = 0.3  # area: disk diameter; point/spot: soft radius
    spot_angle: float = 60.0  # spot: cone in degrees
    aim: str = "down"  # down | up (e.g. a cove strip on a wardrobe washing the ceiling)
    shadow: bool | None = None  # None = automatic (casts_shadow): only pendants cast shadows


@dataclass(frozen=True)
class TrackHead:
    """One spot on a track: ``x`` = distance along the rail from its centre (local +x), aimed at a world
    point ``aim`` = (x, y, z) - the light goes only where it is needed."""

    x: float
    aim: tuple[float, float, float]


@dataclass(frozen=True)
class Track:
    """Track lighting: spot heads on the rail (``track-light`` pieces)."""

    heads: tuple[TrackHead, ...] = ()
    watts: float = 12.0  # per head (Blender watts)
    beam: float = 30.0  # spot cone, degrees
    color: str = WARM_WHITE


@dataclass(frozen=True)
class Storage:
    modules: tuple[Module, ...] = ()  # empty = automatic modules from the width
    plinth: float | None = None  # None = 8 cm on the floor, 0 when hung (elevation > 0)
    handle_color: str = "#3a3a3a"
    handles: bool = True  # False = handle-less push-to-open fronts
    handle_length: float = 0.0  # > 0: long vertical bars of this length on tall doors, short doors push-to-open
    handles_low: bool = False  # handles at the bottom of every door (as low / reachable as possible)
    door_handles: bool = True  # False = only drawers keep handles; doors / flaps / panels are push-to-open
    interior_color: str = ""  # "" = the piece's colour


@dataclass(frozen=True)
class Item:
    id: str
    type: str
    room: str
    size: tuple[float, float, float]  # width, depth, height
    position: Point
    rotation: float = 0.0
    elevation: float = 0.0  # height of the underside (wall cabinets, shelves, mirrors)
    color: str = DEFAULT_COLOR
    label: str = ""
    status: str = "draft"
    note: str = ""
    mirror: bool = False  # mirror the shape left <-> right (e.g. the side of a corner sofa's chaise)
    storage: Storage | None = None  # storage types only; None = automatic modules
    light: Light | None = None  # light fixtures only; None = default light for the type
    track: Track | None = None  # track-light pieces: the spot heads
    tag: str = ""  # name written on the piece's front in 3D (e.g. "FRIDGE"), so appliances read at a glance
    tag_z: float = -1.0  # height of the tag above the underside; < 0 = automatic (near the top of the front)
    tag_color: str = ""  # colour of the tag letters (#rrggbb); "" = the plan-label colour. Beds: written flat on the duvet
    metal: str = ""  # recolours the shape's built-in brass fittings (taps, frames, legs...); "" = brass
    accent: str = ""  # recolours the shape's built-in second colour (ACCENTS: sofa base / feet, duvet, shower curb...)
    apron_color: str = ""  # tints the apron finish (wallpaper, backsplash, tub front) to this colour; "" = as the finish
    cushion: str = ""  # throw cushions on sofas / armchairs (CUSHIONS: three tones derived from it); "" = built-in
    apron: str = ""  # bathtubs / backsplashes: finish (apartment.toml [finishes]) tiling the front face

    @property
    def variant(self) -> str:
        return self.id.split(".", 1)[0]

    @property
    def local_id(self) -> str:
        return self.id.split(".", 1)[-1]

    @property
    def top(self) -> float:
        return self.elevation + self.size[2]

    @property
    def is_storage(self) -> bool:
        return is_storage(self.type)

    def footprint(self) -> list[Point]:
        return rotated_rect(self.position, self.size[0], self.size[1], self.rotation)

    def footprint_parts(self) -> list[list[Point]]:
        """Convex pieces of the real footprint: an L-shaped corner sofa is its seat band + its chaise
        (so things standing in the free corner in front of the seat are not reported as overlapping)."""
        words = self.type.split("-")
        if words[-1] != "sofa" or "corner" not in words:
            return [self.footprint()]
        w, d = self.size[0], self.size[1]
        band, chaise = ((min(1.0, d * 0.58), min(0.95, w * 0.35)) if {"tufted", "plush"} & set(words)
                        else (min(0.95, d * 0.6), 0.9))
        sign = -1 if self.mirror else 1  # chaise on the local left, mirror = right
        a = math.radians(self.rotation)
        out = []
        for lx, ly, rw, rd in ((0.0, -d / 2 + band / 2, w, band), (sign * (-w / 2 + chaise / 2), 0.0, chaise, d)):
            cx = self.position[0] + lx * math.cos(a) - ly * math.sin(a)
            cy = self.position[1] + lx * math.sin(a) + ly * math.cos(a)
            out.append(rotated_rect((cx, cy), rw, rd, self.rotation))
        return out


@dataclass(frozen=True)
class RoomFinish:
    """A variant's own surfaces for one room (``[rooms.<room id>]``): finish names from apartment.toml.

    ``floor`` replaces the room's floor, ``walls`` tiles its walls up to ``walls_height`` (0 = ceiling),
    ``ceiling`` tiles the ceiling. ``stretch_ceiling`` = floating Barrisol-type membrane ``stretch_drop`` under
    the slab, stopping ``stretch_gap`` short of every wall; the gap holds a warm LED line that grazes the walls
    (``stretch_led_w_per_m``). Ceiling-mounted fixtures in the room are lowered onto the membrane.
    ``paint`` = the room's own wall paint (a 2 mm painted skin on its walls; ignored where ``walls`` tiles them).
    """

    floor: str = ""
    walls: str = ""
    ceiling: str = ""
    walls_height: float = 0.0
    stretch_ceiling: bool = False
    stretch_color: str = "#f7f6f3"
    stretch_drop: float = 0.05
    stretch_gap: float = 0.05
    stretch_led_color: str = "#ffd9a8"
    stretch_led_w_per_m: float = 12.0
    skirting: str = ""  # skirting-board colour (#rrggbb) along the real walls; "" = none
    skirting_height: float = 0.08
    paint: str = ""  # this room's wall paint (#rrggbb) instead of the variant's wall_color; "" = wall_color
    floor_color: str = ""  # tints the floor finish to this colour (planks / tiles keep their pattern); "" = as is
    walls_color: str = ""  # tints the wall-tile finish; "" = as is


@dataclass
class Variant:
    key: str
    name: str
    description: str = ""
    based_on: str = ""
    wall_color: str = ""
    style_of: str = ""  # key of the variant whose layout this one restyles (colours / finishes only), "" = a layout
    true_colors: bool = False  # fabrics (soft / shag shades) show their colour as given, not lightened
    finishes: dict = field(default_factory=dict)  # the variant's own [finishes.<key>_...] (name -> Finish)
    owner_colors: list[str] = field(default_factory=list)  # colour paths the owner picked in Blender - kept
    # when the style is regenerated (get_color / set_color)
    items: list[Item] = field(default_factory=list)
    rooms: dict[str, RoomFinish] = field(default_factory=dict)
    source: Path | None = None

    def item(self, ref: str) -> Item:
        full = ref if "." in ref else f"{self.key}.{ref}"
        for it in self.items:
            if it.id == full:
                return it
        raise KeyError(ref)


def _last(type_: str) -> str:
    return type_.split("-")[-1]


def apron_box(item: Item) -> Box:
    """Tiled front panel of a built-in bathtub (local frame): just proud of the tub's front, inset at the
    ends and under the rim so no face is shared with the tub (no flicker)."""
    w, d, h = item.size
    return _box(-w / 2 + 0.001, d / 2 - 0.004, 0.0, w / 2 - 0.001, d / 2 + 0.008, h - 0.002)


def is_light(type_: str) -> bool:
    return _last(type_) in LIGHT_WORDS


def default_light(type_: str, size: tuple[float, float, float] = (0.3, 0.3, 0.1)) -> Light:
    """Light per fixture type (Blender watts, warm white): what a modern LED fixture of that kind gives."""
    words = type_.split("-")
    w = size[0]
    if _last(type_) == "strip":  # LED strip / profile: ~15 W per metre, a long thin rectangle
        return Light("rect", round(max(5.0, 15.0 * w), 1), size=w)
    if "ring" in words:  # LED ring: a glowing circle the size of the ring
        return Light("area", round(80.0 + 60.0 * w, 1), size=w)
    if "linear" in words:  # linear pendant bar
        return Light("rect", round(max(30.0, 45.0 * w), 1), size=w)
    if "picture" in words:  # picture light: wide soft spot washing the art below it
        return Light("spot", 12.0, size=0.02, spot_angle=100.0)
    if "globe" in words or "cluster" in words:  # opal globe(s): bigger soft source, a cluster gives more
        return Light("point", 60.0 if "cluster" in words else 35.0, size=0.12)
    if "recessed" in words or "spot" in words or _last(type_) == "spotlight":
        return Light("spot", 15.0, size=0.02, spot_angle=50.0)
    if "pendant" in words:
        return Light("point", 40.0, size=0.08)
    if "ceiling" in words or "panel" in words:
        return Light("area", 60.0, size=0.3)
    return Light("point", 25.0, size=0.1)  # floor / table / wall lamps


def light_of(item: Item) -> Light:
    return item.light or default_light(item.type, item.size)


def casts_shadow(item: Item) -> bool:
    """Shadows cost a shadow-map render per light; only the 'hero' pendants get them by default.

    Strips, downlights, panels, ceiling discs and lamps light the room just as well without - the
    eye does not miss their soft shadows, the viewport does feel each one (ADR 0008).
    """
    lt = light_of(item)
    if lt.shadow is not None:
        return lt.shadow
    return "pendant" in item.type.split("-")


def light_cutoff(item: Item) -> float:
    """Distance (m) beyond which a fixture is ignored - keeps every light's cost inside its room."""
    return round(min(7.0, max(2.5, 1.0 + 0.55 * light_of(item).watts ** 0.5)), 2)


TRACK_HEAD_DROP = 0.06  # head pivot below the rail's top (stem + half the head)


def track_heads(item: Item, z_offset: float = 0.0) -> list[tuple[Point3, Point3]]:
    """(world position of each head's lens pivot, unit aim direction) for a track-light piece.

    ``z_offset`` = extra vertical shift of the whole piece (e.g. lowered onto a stretch ceiling)."""
    if item.track is None:
        return []
    a = math.radians(item.rotation)
    top = item.elevation + item.size[2] + z_offset
    out = []
    for hd in item.track.heads:
        px = item.position[0] + hd.x * math.cos(a)
        py = item.position[1] + hd.x * math.sin(a)
        pz = top - TRACK_HEAD_DROP
        dx, dy, dz = hd.aim[0] - px, hd.aim[1] - py, hd.aim[2] - pz
        n = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
        out.append(((px, py, pz), (dx / n, dy / n, dz / n)))
    return out


def ceiling_mounted(item: Item, ceiling_height: float) -> bool:
    """Hangs from / sits in the ceiling (recessed spots, panels, pendants): moves with a stretch ceiling."""
    return item.top >= ceiling_height - 0.011


def light_source_pos(item: Item) -> Point3:
    """Position of the Blender light in the fixture's local frame (x, y, z above its underside).

    Shadow-casting fixtures (pendants) keep it outside their own body; lamps without shadows may have it inside
    the shade. Library shapes whose bulb is off-centre (arc lamp, sconce, picture light) say where it is."""
    from .shapes_library import arc_geometry, sconce_geometry

    w, d, h = item.size
    words = item.type.split("-")
    if _last(item.type) == "lamp" and "arc" in words:
        g = arc_geometry(w, d, h)
        return (-g["sx"] if item.mirror else g["sx"], 0.0, g["shade_bottom"] + g["sh"] * 0.3)
    if _last(item.type) == "lamp" and "mushroom" in words:
        return (0.0, 0.0, h - min(w * 0.4, h * 0.4) * 0.7)
    if _last(item.type) == "sconce":
        return (0.0, sconce_geometry(w, d, h)[1], h / 2)
    if _last(item.type) == "light" and "picture" in words:
        return (0.0, d / 2 - 0.025, h - 0.065)
    return (0.0, 0.0, light_source_z(item))


def light_source_z(item: Item) -> float:
    """Height of the light source above the fixture's underside (outside its own body)."""
    words = item.type.split("-")
    h = item.size[2]
    if _last(item.type) == "lamp" and ("floor" in words or "table" in words):
        return h * 0.75 - 0.03  # just under the shade
    if _last(item.type) == "strip":
        return h + 0.003 if light_of(item).aim == "up" else -0.003
    return -0.03  # just under the diffuser / shade


def is_storage(type_: str) -> bool:
    return _last(type_) in STORAGE_WORDS


# --------------------------------------------------------------------------- ids
def make_id(key: str, type_: str, room_slug: str, n: int) -> str:
    return f"{key}.{type_}-{room_slug}-{n}"


def next_id(variant: Variant, type_: str, room_slug: str) -> str:
    """First free id for a new piece of this type in this room."""
    used = {it.id for it in variant.items}
    n = 1
    while make_id(variant.key, type_, room_slug, n) in used:
        n += 1
    return make_id(variant.key, type_, room_slug, n)


def find_item(variants: list[Variant], ref: str, active: str | None = None) -> Item:
    """Resolve 'A.sofa-living-1', or 'sofa-living-1' in the ``active`` variant.

    A part path ('A.wardrobe-living-1/m2/shelf-1') resolves to its piece.
    """
    ref = ref.split("/", 1)[0]
    if "." not in ref and active:
        ref = f"{active}.{ref}"
    for v in variants:
        for it in v.items:
            if it.id == ref:
                return it
    raise KeyError(ref)


# --------------------------------------------------------------------------- loading
def _fronts(d: dict) -> tuple[Front, ...]:
    if "fronts" in d:
        return tuple(Front(f["kind"], float(f["height"]) if "height" in f else None, int(f.get("count", 1)))
                     for f in d["fronts"])
    return (Front(d.get("front", "door-left"), None, int(d.get("drawers", 1))),)


def _module(d: dict) -> Module:
    return Module(
        width=float(d["width"]),
        fronts=_fronts(d),
        finish=d.get("finish", "matte"),
        front_color=d.get("front_color", ""),
        interior=tuple(Fitting(f["kind"], float(f.get("z", 0.0)), float(f.get("height", 0.15)), float(f.get("x", 0.0)))
                       for f in d.get("interior", [])),
        label=d.get("label", ""),
    )


def _storage(d: dict | None) -> Storage | None:
    if d is None:
        return None
    return Storage(
        modules=tuple(_module(m) for m in d.get("modules", [])),
        plinth=float(d["plinth"]) if "plinth" in d else None,
        handle_color=d.get("handle_color", "#3a3a3a"),
        handles=bool(d.get("handles", True)),
        handle_length=float(d.get("handle_length", 0.0)),
        handles_low=bool(d.get("handles_low", False)),
        door_handles=bool(d.get("door_handles", True)),
        interior_color=d.get("interior_color", ""),
    )


def _light(d: dict | None) -> Light | None:
    if d is None:
        return None
    return Light(kind=d.get("kind", "point"), watts=float(d.get("watts", 40.0)), color=d.get("color", WARM_WHITE),
                 size=float(d.get("size", 0.3)), spot_angle=float(d.get("spot_angle", 60.0)), aim=d.get("aim", "down"),
                 shadow=d.get("shadow"))


def _item(d: dict) -> Item:
    return Item(
        id=d["id"],
        type=d["type"],
        room=d["room"],
        size=tuple(float(v) for v in d["size"]),
        position=tuple(float(v) for v in d["position"]),
        rotation=float(d.get("rotation", 0.0)),
        elevation=float(d.get("elevation", 0.0)),
        color=d.get("color", DEFAULT_COLOR),
        label=d.get("label", ""),
        status=d.get("status", "draft"),
        note=d.get("note", ""),
        mirror=bool(d.get("mirror", False)),
        storage=_storage(d.get("storage")),
        light=_light(d.get("light")),
        apron=d.get("apron", ""),
        track=_track(d.get("track")),
        tag=d.get("tag", ""),
        tag_z=float(d.get("tag_z", -1.0)),
        tag_color=d.get("tag_color", ""),
        metal=d.get("metal", ""),
        accent=d.get("accent", ""),
        apron_color=d.get("apron_color", ""),
        cushion=d.get("cushion", ""),
    )


def _track(d: dict | None) -> Track | None:
    if d is None:
        return None
    heads = tuple(TrackHead(float(h["x"]), tuple(float(c) for c in (*h["aim"], 0.0)[:3])) for h in d.get("heads", []))
    return Track(heads=heads, watts=float(d.get("watts", 12.0)), beam=float(d.get("beam", 30.0)),
                 color=d.get("color", WARM_WHITE))


def _room_finish(r: dict) -> RoomFinish:
    d = RoomFinish()
    return RoomFinish(**{k: type(getattr(d, k))(r[k]) for k in RoomFinish.__dataclass_fields__ if k in r})


def merge_variant_finishes(apt: Apartment, variants: list) -> list[str]:
    """Add every variant's own finishes to ``apt.finishes`` (so rooms / aprons can use them); returns clashes.
    A variant's finish names must start with its key in lower case + '_' (e.g. ``d1_terrazzo``)."""
    problems = []
    for v in variants:
        for name, f in v.finishes.items():
            if not name.startswith(f"{v.key.lower()}_"):
                problems.append(f"{v.key}: own finish '{name}' must start with '{v.key.lower()}_'")
            elif name in apt.finishes and apt.finishes[name] != f:
                problems.append(f"{v.key}: finish '{name}' is already defined differently")
            else:
                apt.finishes[name] = f
    return problems


def load_variant(path: str | Path) -> Variant:
    path = Path(path)
    with open(path, "rb") as fh:
        raw = tomllib.load(fh)
    v = raw.get("variant", {})
    return Variant(
        key=v.get("key", path.stem),
        name=v.get("name", f"Variant {path.stem}"),
        description=v.get("description", ""),
        based_on=v.get("based_on", ""),
        wall_color=v.get("wall_color", ""),
        style_of=v.get("style_of", ""),
        true_colors=bool(v.get("true_colors", False)),
        finishes={n: parse_finish(n, f) for n, f in raw.get("finishes", {}).items()},
        owner_colors=list(v.get("owner_colors", [])),
        items=[_item(d) for d in raw.get("items", [])],
        rooms={rid: _room_finish(r) for rid, r in raw.get("rooms", {}).items()},
        source=path,
    )


def load_variants(directory: str | Path | None = None) -> list[Variant]:
    d = Path(directory) if directory else VARIANTS_DIR
    return sorted((load_variant(p) for p in d.glob("*.toml")), key=lambda v: v.key) if d.is_dir() else []


# --------------------------------------------------------------------------- writing / copying
def _q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _num(v: float) -> str:
    return f"{v:.3f}".rstrip("0").rstrip(".")  # mm precision, no trailing zeros


HEADER = """\
# Furniture variant {key} - generated by `apartment variant`, then edited by hand / by Claude.
# Schema and conventions: docs/decisions/0005-furniture-variants.md (+ 0006 storage, fixed points)
#   id        = "<VARIANT>.<type>-<room-slug>-<n>"  (unique across all variants)
#   size      = [width, depth, height] m      position = [x, y] centre of footprint (model metres)
#   rotation  = degrees CCW, 0 = front faces +Y (facade A), 90 = -X, 180 = -Y, 270 = +X
#   elevation = underside height (0 = on the floor)   color = "#rrggbb"   status = draft|approved
#   storage pieces: optional [items.storage] + [[items.storage.modules]] (fronts, interior)
"""


def _front_toml(f: Front) -> str:
    parts = [f"kind = {_q(f.kind)}"]
    if f.height is not None:
        parts.append(f"height = {_num(f.height)}")
    if f.count != 1:
        parts.append(f"count = {f.count}")
    return "{ " + ", ".join(parts) + " }"


def _fitting_toml(f: Fitting) -> str:
    parts = [f"kind = {_q(f.kind)}"]
    parts.append(f"x = {_num(f.x)}" if f.kind == "divider" else f"z = {_num(f.z)}")
    if f.kind == "drawer":
        parts.append(f"height = {_num(f.height)}")
    return "{ " + ", ".join(parts) + " }"


def _storage_toml(st: Storage) -> list[str]:
    lines = ["[items.storage]"]
    if st.plinth is not None:
        lines.append(f"plinth = {_num(st.plinth)}")
    lines.append(f"handle_color = {_q(st.handle_color)}")
    if not st.handles:
        lines.append("handles = false")
    if st.handle_length:
        lines.append(f"handle_length = {_num(st.handle_length)}")
    if st.handles_low:
        lines.append("handles_low = true")
    if not st.door_handles:
        lines.append("door_handles = false")
    if st.interior_color:
        lines.append(f"interior_color = {_q(st.interior_color)}")
    for m in st.modules:
        lines += ["[[items.storage.modules]]", f"width = {_num(m.width)}"]
        if len(m.fronts) == 1 and m.fronts[0].height is None:
            lines.append(f"front = {_q(m.fronts[0].kind)}")
            if m.fronts[0].count != 1:
                lines.append(f"drawers = {m.fronts[0].count}")
        else:
            lines.append("fronts = [" + ", ".join(_front_toml(f) for f in m.fronts) + "]")
        if m.finish != "matte":
            lines.append(f"finish = {_q(m.finish)}")
        if m.front_color:
            lines.append(f"front_color = {_q(m.front_color)}")
        if m.label:
            lines.append(f"label = {_q(m.label)}")
        lines.append("interior = [" + ", ".join(_fitting_toml(f) for f in m.interior) + "]")
    return lines


def variant_to_toml(v: Variant) -> str:
    lines = [HEADER.format(key=v.key), "[variant]", f"key = {_q(v.key)}", f"name = {_q(v.name)}"]
    for k in ("description", "based_on", "style_of", "wall_color"):
        if val := getattr(v, k):
            lines.append(f"{k} = {_q(val)}")
    if v.true_colors:
        lines.append("true_colors = true")
    if v.owner_colors:
        lines.append("owner_colors = [" + ", ".join(_q(c) for c in v.owner_colors) + "]")
    for name, f in v.finishes.items():
        lines += ["", f"[finishes.{name}]", f"kind = {_q(f.kind)}", f"size = [{_num(f.size[0])}, {_num(f.size[1])}]",
                  f"color = {_q(f.color)}", f"color2 = {_q(f.color2)}", f"joint_color = {_q(f.joint_color)}",
                  f"joint = {_num(f.joint)}", f"direction = {_q(f.direction)}", f"roughness = {_num(f.roughness)}"]
        if f.note:
            lines.append(f"note = {_q(f.note)}")
    for rid, rf in v.rooms.items():
        lines += ["", f"[rooms.{rid}]"]
        default = RoomFinish()
        for k in RoomFinish.__dataclass_fields__:
            val = getattr(rf, k)
            if val == getattr(default, k):
                continue
            lines.append(f"{k} = " + ("true" if val is True else "false" if val is False
                                      else _q(val) if isinstance(val, str) else _num(val)))
    for it in v.items:
        lines += ["", "[[items]]", f"id = {_q(it.id)}", f"type = {_q(it.type)}", f"room = {_q(it.room)}"]
        lines.append(f"size = [{', '.join(_num(x) for x in it.size)}]")
        lines.append(f"position = [{', '.join(_num(x) for x in it.position)}]")
        if it.rotation:
            lines.append(f"rotation = {_num(it.rotation)}")
        if it.elevation:
            lines.append(f"elevation = {_num(it.elevation)}")
        lines.append(f"color = {_q(it.color)}")
        if it.mirror:
            lines.append("mirror = true")
        if it.apron:
            lines.append(f"apron = {_q(it.apron)}")
        if it.tag:
            lines.append(f"tag = {_q(it.tag)}")
        if it.tag_z >= 0:
            lines.append(f"tag_z = {_num(it.tag_z)}")
        if it.tag_color:
            lines.append(f"tag_color = {_q(it.tag_color)}")
        if it.metal:
            lines.append(f"metal = {_q(it.metal)}")
        if it.accent:
            lines.append(f"accent = {_q(it.accent)}")
        if it.apron_color:
            lines.append(f"apron_color = {_q(it.apron_color)}")
        if it.cushion:
            lines.append(f"cushion = {_q(it.cushion)}")
        for k in ("label", "note"):
            if val := getattr(it, k):
                lines.append(f"{k} = {_q(val)}")
        lines.append(f"status = {_q(it.status)}")
        if it.storage is not None:
            lines += _storage_toml(it.storage)
        if it.light is not None:
            lt = it.light
            lines += ["[items.light]", f"kind = {_q(lt.kind)}", f"watts = {_num(lt.watts)}", f"color = {_q(lt.color)}",
                      f"size = {_num(lt.size)}"]
            if lt.kind == "spot":
                lines.append(f"spot_angle = {_num(lt.spot_angle)}")
            if lt.aim != "down":
                lines.append(f"aim = {_q(lt.aim)}")
            if lt.shadow is not None:
                lines.append(f"shadow = {'true' if lt.shadow else 'false'}")
        if it.track is not None:
            tr = it.track
            lines += ["[items.track]", f"watts = {_num(tr.watts)}", f"beam = {_num(tr.beam)}", f"color = {_q(tr.color)}"]
            lines.append("heads = [")
            lines += [f"  {{ x = {_num(hd.x)}, aim = [{', '.join(_num(c) for c in hd.aim)}] }}," for hd in tr.heads]
            lines.append("]")
    return "\n".join(lines) + "\n"


def copy_variant(src: Variant, key: str, name: str = "") -> Variant:
    """New variant with every piece copied and re-keyed (A.sofa-living-1 -> B.sofa-living-1)."""
    items = [replace(it, id=f"{key}.{it.local_id}", status="draft") for it in src.items]
    return Variant(key=key, name=name or f"Variant {key}", description=f"Copy of {src.key}", based_on=src.key,
                   wall_color=src.wall_color, items=items, rooms=dict(src.rooms))


# --------------------------------------------------------------------------- shapes (local boxes)
def _box(x1, y1, z1, x2, y2, z2) -> Box:
    return (x1, y1, z1, x2, y2, z2)


def _legs(w, d, h, t=0.05, inset=0.04) -> list[Box]:
    xs, ys = (-w / 2 + inset, w / 2 - inset - t), (-d / 2 + inset, d / 2 - inset - t)
    return [_box(x, y, 0, x + t, y + t, h) for x in xs for y in ys]


def _basin(x1, y1, x2, y2, z1, z2, wall=0.015) -> list[Part]:
    """Open-topped vessel (sink, bathtub): bottom + 4 walls."""
    return [Part(_box(x1, y1, z1, x2, y2, z1 + wall * 2), "ceramic"),
            Part(_box(x1, y1, z1, x1 + wall, y2, z2), "ceramic"), Part(_box(x2 - wall, y1, z1, x2, y2, z2), "ceramic"),
            Part(_box(x1, y1, z1, x2, y1 + wall, z2), "ceramic"), Part(_box(x1, y2 - wall, z1, x2, y2, z2), "ceramic")]


def _pill(w: float, h: float, y1: float, y2: float, shade: str, color: str = "", z0: float = 0.0,
          n: int = 48) -> list[Part]:
    """Upright capsule (rounded top and bottom) w wide, h tall, in the x-z plane between y1 and y2."""
    r = min(w, h) / 2
    parts = [Part(_box(-w / 2, y1, z0 + r, w / 2, y2, z0 + h - r), shade, color=color)] if h > w else []
    for i in range(n):  # caps as thin horizontal slices following the circle
        za, zb = r * i / n, r * (i + 1) / n
        half = math.sqrt(max(r * r - (r - (za + zb) / 2) ** 2, 0.0)) + (w / 2 - r)
        parts += [Part(_box(-half, y1, z0 + za, half, y2, z0 + zb), shade, color=color),
                  Part(_box(-half, y1, z0 + h - zb, half, y2, z0 + h - za), shade, color=color)]
    return parts


def _wave(w: float, d: float, h: float, pitch: float, shade: str) -> list[Part]:
    """Wave-fold (ripple) curtain: soft upright half-overlapping cylinders alternating front / back, so the
    fabric snakes along the track; full height h, depth d (front-to-back of the folds)."""
    n = max(2, round(w / pitch))
    step = w / n
    parts = []
    for i in range(n):
        cx = -w / 2 + step * (i + 0.5)
        cy = d / 4 if i % 2 else -d / 4
        parts.append(Part(_box(cx - step * 0.62, cy - d / 4, 0, cx + step * 0.62, cy + d / 4, h), shade, "cyl"))
    return parts


def _tuft(x1, y1, z1, x2, y2, z2, facing: str = "up", g: float = 0.012) -> list[Part]:
    """One boucle block with a soft puffed face; the gaps between blocks read as the tufting channels."""
    if facing == "up":
        return [Part(_box(x1 + g / 2, y1 + g / 2, z1, x2 - g / 2, y2 - g / 2, z2 - 0.022), "soft"),
                Part(_box(x1 + 0.035, y1 + 0.035, z2 - 0.03, x2 - 0.035, y2 - 0.035, z2), "soft")]  # puffed crown
    return [Part(_box(x1 + g / 2, y1, z1 + g / 2, x2 - g / 2, y2 - 0.022, z2 - g / 2), "soft"),  # facing +y
            Part(_box(x1 + 0.035, y2 - 0.03, z1 + 0.035, x2 - 0.035, y2, z2 - 0.035), "soft")]


def _grid(a0: float, a1: float, cell: float) -> list[tuple[float, float]]:
    n = max(1, round((a1 - a0) / cell))
    step = (a1 - a0) / n
    return [(a0 + i * step, a0 + (i + 1) * step) for i in range(n)]


def _bedding(hw: float, hd: float, hb: float, top: float) -> list[Part]:
    """Linen duvet draped over the sides (lower 2/3), white sheet turned down at its top, pillows at the head."""
    linen, white = "#e7dfd2", "#fbfaf7"
    y0 = -hd + hb + 0.48  # duvet starts below the pillows
    parts = [Part(_box(-hw - 0.012, y0, top, hw + 0.012, hd + 0.012, top + 0.045), "soft", color=linen),
             Part(_box(-hw - 0.012, y0, top - 0.17, -hw, hd + 0.012, top), "soft", color=linen),  # side drapes
             Part(_box(hw, y0, top - 0.17, hw + 0.012, hd + 0.012, top), "soft", color=linen),
             Part(_box(-hw, hd, top - 0.17, hw, hd + 0.012, top), "soft", color=linen),
             Part(_box(-hw - 0.014, y0, top + 0.045, hw + 0.014, y0 + 0.16, top + 0.06), "soft", color=white)]  # fold
    n = 2 if hw * 2 >= 1.3 else 1
    pw = min(0.62, (hw * 2 - 0.12) / n - 0.04)
    for k in range(n):
        cx = (-hw + (k + 0.5) * (hw * 2) / n)
        parts.append(Part(_box(cx - pw / 2, -hd + hb + 0.04, top, cx + pw / 2, -hd + hb + 0.40, top + 0.13), "soft",
                          color=white))
    return parts


def _plush_corner_sofa(w: float, d: float, h: float) -> list[Part]:
    """Cloud-like L sofa: low recessed base, thick seat cushions with a rolled front edge, leaning back cushions with
    rounded tops, a rolled arm on the non-chaise end, one long chaise cushion, three throw pillows."""
    hw, hd = w / 2, d / 2
    back, arm, seat, base = 0.30, 0.26, 0.47, 0.30
    seat_d, chaise = min(1.0, d * 0.58), min(0.95, w * 0.35)
    yb, yf = -hd + back, -hd + seat_d
    parts = [Part(_box(-hw + 0.06, -hd + 0.06, 0, hw - 0.06, yf - 0.06, 0.06), "main", color="#6b4a33"),  # recessed base
             Part(_box(-hw + 0.06, yf - 0.1, 0, -hw + chaise - 0.06, hd - 0.06, 0.06), "main", color="#6b4a33"),
             Part(_box(-hw, -hd, 0.06, hw, yf, base), "soft"), Part(_box(-hw, yf - 0.02, 0.06, -hw + chaise, hd, base), "soft"),
             Part(_box(-hw, -hd, base, hw, -hd + 0.12, h - 0.10), "soft")]  # back frame behind the cushions

    def cushion(x1, x2, y1, y2):  # seat cushion + rolled front edge (towards +y)
        return [Part(_box(x1 + 0.008, y1, base, x2 - 0.008, y2 - 0.07, seat), "soft"),
                Part(_box(x1 + 0.008, y2 - 0.14, base, x2 - 0.008, y2, seat), "soft", "xcyl")]
    span = hw - arm - (-hw + chaise)
    n = max(1, round(span / 0.8))
    for k in range(n):
        x1 = -hw + chaise + k * span / n
        parts += cushion(x1, x1 + span / n, yb, yf)
        parts += [Part(_box(x1 + 0.02, -hd + 0.10, seat - 0.02, x1 + span / n - 0.02, yb + 0.04, h - 0.12), "soft"),
                  Part(_box(x1 + 0.02, -hd + 0.08, h - 0.22, x1 + span / n - 0.02, yb + 0.06, h), "soft", "xcyl")]
    parts += cushion(-hw, -hw + chaise, yb, hd)  # long chaise cushion
    parts += [Part(_box(-hw + 0.02, -hd + 0.10, seat - 0.02, -hw + chaise - 0.02, yb + 0.04, h - 0.12), "soft"),
              Part(_box(-hw + 0.02, -hd + 0.08, h - 0.22, -hw + chaise - 0.02, yb + 0.06, h), "soft", "xcyl")]
    parts += [Part(_box(hw - arm, -hd, 0.06, hw, yf, 0.56), "soft"),  # arm + rolled top
              Part(_box(hw - arm, -hd, 0.48, hw, yf, 0.66), "soft", "ycyl")]
    for k, cx in enumerate((-hw + chaise * 0.5, -hw + chaise + span * 0.3, hw - arm - 0.3)):  # throw pillows
        parts.append(Part(_box(cx - 0.22, yb + 0.02, seat, cx + 0.22, yb + 0.16, seat + 0.40 - 0.04 * k), "soft",
                          color=("#cdb79a", "#e9dfd0", "#a88f74")[k]))
    return parts


def _tufted_corner_sofa(w: float, d: float, h: float) -> list[Part]:
    hw, hd = w / 2, d / 2
    feet, seat, back, arm = 0.05, 0.42, 0.30, 0.24
    seat_d, chaise = min(1.0, d * 0.58), min(0.95, w * 0.35)
    parts = [Part(_box(x - 0.03, y - 0.03, 0, x + 0.03, y + 0.03, feet), "main", color="#6b4a33")  # wooden feet
             for x, y in ((-hw + 0.08, -hd + 0.08), (hw - 0.08, -hd + 0.08), (hw - 0.08, -hd + seat_d - 0.08),
                          (-hw + 0.08, hd - 0.08), (-hw + chaise - 0.08, hd - 0.08))]
    parts += [Part(_box(-hw + 0.02, -hd + 0.02, feet, hw - 0.02, -hd + seat_d - 0.02, seat - 0.05), "soft"),  # cores
              Part(_box(-hw + 0.02, -hd + seat_d - 0.03, feet, -hw + chaise - 0.02, hd - 0.02, seat - 0.05), "soft"),
              Part(_box(-hw + 0.02, -hd + 0.02, feet, hw - 0.02, -hd + back - 0.04, h - 0.05), "soft")]
    for y1, y2 in _grid(-hd + back, -hd + seat_d, 0.34):  # main seat
        for x1, x2 in _grid(-hw + chaise, hw - arm, 0.34):
            parts += _tuft(x1, y1, feet, x2, y2, seat)
    for y1, y2 in _grid(-hd + back, hd, 0.34):  # chaise
        for x1, x2 in _grid(-hw, -hw + chaise, 0.32):
            parts += _tuft(x1, y1, feet, x2, y2, seat)
    for z1, z2 in _grid(feet, h, 0.26):  # back, puffed towards the seat
        for x1, x2 in _grid(-hw, hw, 0.34):
            parts += _tuft(x1, -hd, z1, x2, -hd + back, z2, "front")
    for y1, y2 in _grid(-hd + back, -hd + seat_d, 0.36):  # arm (non-chaise end), rounded top
        for z1, z2 in _grid(feet, 0.62, 0.29):
            parts += _tuft(hw - arm, y1, z1, hw, y2, z2, "up" if z2 > 0.6 else "front")
    for k, (x1, x2) in enumerate(_grid(-hw + 0.2, hw - arm - 0.1, 0.62)):  # loose throw cushions on the back
        cx = (x1 + x2) / 2
        parts.append(Part(_box(cx - 0.23, -hd + back, seat, cx + 0.23, -hd + back + 0.14, seat + 0.40 - 0.03 * (k % 2)),
                          "soft"))
    return parts


def _plush_armchair(w: float, d: float, h: float) -> list[Part]:
    """Plush lounge chair: recessed dark base, soft body, thick seat cushion with a rolled front edge, leaning back
    cushion with a rolled top, two rolled arms, one throw pillow - the plush sofa's language in one seat."""
    hw, hd = w / 2, d / 2
    arm, back, base, seat = min(0.2, w * 0.22), 0.24, 0.28, 0.45
    return [Part(_box(-hw + 0.06, -hd + 0.06, 0, hw - 0.06, hd - 0.06, 0.06), "main", color="#6b4a33"),
            Part(_box(-hw, -hd, 0.06, hw, hd, base), "soft"),
            Part(_box(-hw + arm, -hd + back, base, hw - arm, hd - 0.07, seat), "soft"),  # seat + rolled front
            Part(_box(-hw + arm, hd - 0.15, base, hw - arm, hd, seat), "soft", "xcyl"),
            Part(_box(-hw, -hd, base, hw, -hd + 0.12, h - 0.10), "soft"),  # back frame
            Part(_box(-hw + arm, -hd + 0.10, seat - 0.02, hw - arm, -hd + back + 0.04, h - 0.12), "soft"),
            Part(_box(-hw + arm, -hd + 0.08, h - 0.22, hw - arm, -hd + back + 0.06, h), "soft", "xcyl"),
            *(p for sx in (-1, 1) for p in (  # arms + rolled tops
                Part(_box(min(sx * hw, sx * (hw - arm)), -hd, 0.06, max(sx * hw, sx * (hw - arm)), hd, h - 0.20), "soft"),
                Part(_box(min(sx * hw, sx * (hw - arm)), -hd, h - 0.30, max(sx * hw, sx * (hw - arm)), hd, h - 0.12),
                     "soft", "ycyl"))),
            Part(_box(-0.2, -hd + back + 0.02, seat, 0.2, -hd + back + 0.16, seat + 0.34), "soft", color="#cdb79a")]


def _tub_armchair(w: float, d: float, h: float) -> list[Part]:
    hw, hd = w / 2, d / 2
    body, tube, parts = 0.40, min(0.19, w * 0.2), []
    for i in range(7):  # bulging drum base
        f = 0.88 + 0.12 * math.sin(math.pi * (i + 0.5) / 7)
        parts.append(Part(_box(-hw * f, -hd * f, body * i / 7, hw * f, hd * f, body * (i + 1) / 7), "soft", "cyl"))
    rx, ry = hw - tube / 2, hd - tube / 2
    for k in range(64):  # rolled horseshoe back + sides, open at the front (+y)
        a = math.radians(125 + 290 * k / 63)
        cx, cy = rx * math.cos(a), ry * math.sin(a)
        parts.append(Part(_box(cx - tube / 2, cy - tube / 2, body - 0.04, cx + tube / 2, cy + tube / 2, h - 0.05),
                          "soft", "cyl"))
        parts.append(Part(_box(cx - tube * 0.4, cy - tube * 0.4, h - 0.06, cx + tube * 0.4, cy + tube * 0.4, h),
                          "soft", "cyl"))
    inner = min(rx, ry) - tube * 0.45
    parts.append(Part(_box(-inner, -inner * hd / hw, body - 0.02, inner, inner * hd / hw, body + 0.09), "soft", "cyl"))
    parts.append(Part(_box(-0.17, -hd + tube, body + 0.09, 0.17, -hd + tube + 0.11, body + 0.29), "soft"))  # lumbar
    return parts


def _mirror_parts(parts: list[Part]) -> list[Part]:
    return [p._replace(box=(-p.box[3], p.box[1], p.box[2], -p.box[0], p.box[4], p.box[5])) for p in parts]


def item_parts(type_: str, w: float, d: float, h: float, mirror: bool = False) -> list[Part]:
    """Simple recognisable shapes per type (non-storage pieces), local frame, front = +y.

    Unknown types are a plain box, so any furniture can be placed before it has a shape.
    """
    from .shapes_library import library_parts  # the extra shape library (imports this module)

    parts = library_parts(type_, w, d, h)
    if parts is None:
        parts = _parts(type_, w, d, h)
    return _mirror_parts(parts) if mirror else parts


def _parts(type_: str, w: float, d: float, h: float) -> list[Part]:  # noqa: C901 - a catalogue of shapes
    hw, hd = w / 2, d / 2
    words = type_.split("-")
    t = words[-1]  # dining-table -> table, corner-sofa -> sofa
    if t == "bed" and "floating" in words:  # frame + mattress hovering on a hidden recessed plinth, LED glow under
        hb, lift, inset = min(0.08, d * 0.05), 0.22, min(0.38, w * 0.25)  # base well inside: clear overhang
        return [Part(_box(-hw + inset, -hd + hb, 0, hw - inset, hd - inset, lift - 0.01), "black"),
                Part(_box(-hw + inset - 0.012, -hd + hb, lift - 0.01, hw - inset + 0.012, hd - inset + 0.012, lift),
                     "emit", color="#ffd29e"),  # LED line under the frame
                Part(_box(-hw, -hd + hb, lift, hw, hd, 0.34), "main"),  # wood frame (piece colour)
                Part(_box(-hw + 0.02, -hd + hb, 0.34, hw - 0.02, hd - 0.02, 0.56), "soft", color="#f4f3f0"),  # mattress
                Part(_box(-hw, -hd, lift, hw, -hd + hb, h), "main"),  # headboard floats too
                *_bedding(hw, hd, hb, 0.56)]
    if t == "door" and "entrance" in words:  # entrance-door leaf (local +x = towards the latch): metallic slab
        return [Part(_box(-hw, -hd, 0, hw, hd, h), "handle"),
                *(Part(_box(-hw + 0.06, -hd - 0.001, z, hw - 0.06, hd + 0.001, z + 0.006), "dark")  # grooves
                  for z in (0.45, 0.9, 1.35, 1.8)),
                Part(_box(hw - 0.2, hd, 1.02, hw - 0.06, hd + 0.05, 1.05), "handle", color="#3a2a1e"),  # levers
                Part(_box(hw - 0.2, -hd - 0.05, 1.02, hw - 0.06, -hd, 1.05), "handle", color="#3a2a1e"),
                Part(_box(-0.008, -hd - 0.002, 1.5, 0.008, hd + 0.002, 1.516), "black", "ycyl")]  # peephole
    if t == "bed":
        hb = min(0.08, d * 0.05)
        return [Part(_box(-hw, -hd + hb, 0, hw, hd, 0.30), "main"),
                Part(_box(-hw + 0.02, -hd + hb, 0.30, hw - 0.02, hd - 0.02, 0.52), "soft"),
                Part(_box(-hw, -hd, 0, hw, -hd + hb, h), "main")]
    if t == "sofa" and "plush" in words:  # plush-corner-sofa: overstuffed cushions with rolled edges, L + chaise
        return _plush_corner_sofa(w, d, h)
    if t == "sofa" and "tufted" in words:  # tufted-corner-sofa (Tribeca-like): chunky boucle blocks in a grid,
        return _tufted_corner_sofa(w, d, h)  # L with the chaise on the local left (mirror = right)
    if t == "armchair" and "plush" in words:  # matches the plush sofa: rolled arms, overstuffed cushions
        return _plush_armchair(w, d, h)
    if t == "armchair" and "tub" in words:  # round boucle tub chair: bulging drum, rolled horseshoe back, cushion
        return _tub_armchair(w, d, h)
    if t == "paradise" and "bird" in words:  # bird-of-paradise (Strelitzia): stone pot, stems, big paddle leaves
        pot = min(0.42, h * 0.24)
        parts = [Part(_box(-hw * 0.55, -hd * 0.55, 0, hw * 0.55, hd * 0.55, pot), "main", "cyl", "#cfc6b8"),
                 Part(_box(-hw * 0.5, -hd * 0.5, pot, hw * 0.5, hd * 0.5, pot + 0.01), "dark", "cyl", "#4a3a2a")]
        leaves = ((0.10, 0.05, 0.98, "y"), (-0.12, 0.02, 0.86, "x"), (0.03, -0.13, 0.92, "x"), (-0.06, 0.12, 0.78, "y"),
                  (0.14, -0.06, 0.72, "x"), (-0.15, -0.08, 0.66, "y"), (0.0, 0.0, 1.0, "x"))  # x, y (x hw), top (x h)
        for lx, ly, top, axis in leaves:
            x, y, zt = lx * hw * 4, ly * hd * 4, top * h
            blade = min(0.62, zt - pot - 0.25)
            parts.append(Part(_box(x - 0.008, y - 0.008, pot, x + 0.008, y + 0.008, zt - blade + 0.05), "plant", "cyl"))
            lw, lt = 0.19, 0.012  # paddle: long ellipse, thin
            box = (_box(x - lw / 2, y - lt, zt - blade, x + lw / 2, y + lt, zt) if axis == "y"
                   else _box(x - lt, y - lw / 2, zt - blade, x + lt, y + lw / 2, zt))
            parts.append(Part(box, "plant", "ycyl" if axis == "y" else "xcyl"))
        return parts
    if t == "tree" and "lemon" in words:  # small potted lemon tree: anthracite pot, slim trunk, round crown, lemons
        pot, r = h * 0.3, min(hw, hd, h * 0.24)
        c = h - r
        parts = [Part(_box(-hw * 0.7, -hd * 0.7, 0, hw * 0.7, hd * 0.7, pot), "main", "cyl", "#3b3b3d"),
                 Part(_box(-hw * 0.64, -hd * 0.64, pot, hw * 0.64, hd * 0.64, pot + 0.01), "dark", "cyl", "#4a3a2a"),
                 Part(_box(-0.018, -0.018, pot, 0.018, 0.018, c), "main", "cyl", "#6b5236")]
        for i in range(8):  # round crown from stacked discs
            za, zb = c - r + 2 * r * i / 8, c - r + 2 * r * (i + 1) / 8
            f = math.sqrt(max(1 - ((za + zb) / 2 - c) ** 2 / r ** 2, 0.05))
            parts.append(Part(_box(-r * f, -r * f, za, r * f, r * f, zb), "plant", "cyl"))
        for k in range(9):  # lemons on the crown surface
            a, z = 2 * math.pi * k / 9 + 0.3, c + r * (0.55 * math.sin(k * 1.7))
            rr = math.sqrt(max(r * r - (z - c) ** 2, 0)) * 0.98
            x, y = rr * math.cos(a), rr * math.sin(a)
            parts.append(Part(_box(x - 0.028, y - 0.028, z - 0.035, x + 0.028, y + 0.028, z + 0.035), "main", "cyl",
                              "#e8c32a"))
        return parts
    if t == "table" and "outdoor" in words:  # modern outdoor table: anthracite aluminium frame, teak slat top
        frame, top, leg = "#2a2a2c", 0.03, 0.045
        parts = [Part(_box(x, y, 0, x + leg, y + leg, h - top), "main", color=frame)
                 for x in (-hw + 0.03, hw - 0.03 - leg) for y in (-hd + 0.03, hd - 0.03 - leg)]
        parts += [Part(_box(-hw + 0.03, -hd + 0.03, h - top - 0.05, hw - 0.03, hd - 0.03, h - top), "main", color=frame)]
        n = max(3, round(d / 0.08))
        for i in range(n):  # teak slats (the piece's colour) with small gaps
            y1 = -hd + i * d / n
            parts.append(Part(_box(-hw, y1 + 0.006, h - top, hw, y1 + d / n - 0.006, h), "main"))
        return parts
    if t == "chair" and "outdoor" in words:  # modern outdoor chair: aluminium frame, rope-woven seat/back, teak arms
        frame, rope, seat = "#2a2a2c", "#cbbfa8", 0.44
        parts = [Part(_box(x, y, 0, x + 0.035, y + 0.035, seat), "main", color=frame)
                 for x in (-hw + 0.03, hw - 0.065) for y in (-hd + 0.03, hd - 0.065)]
        parts += [Part(_box(-hw + 0.03, -hd + 0.03, seat - 0.04, hw - 0.03, hd - 0.03, seat - 0.02), "main",
                       color=frame),
                  Part(_box(-hw + 0.05, -hd + 0.05, seat - 0.02, hw - 0.05, hd - 0.05, seat + 0.05), "soft",
                       color=rope),  # rope seat + cushion
                  Part(_box(-hw + 0.04, -hd + 0.02, seat, hw - 0.04, -hd + 0.06, h), "soft", color=rope),  # back
                  Part(_box(-hw + 0.03, -hd + 0.03, seat, -hw + 0.065, -hd + 0.065, h), "main", color=frame),
                  Part(_box(hw - 0.065, -hd + 0.03, seat, hw - 0.03, -hd + 0.065, h), "main", color=frame),
                  Part(_box(-hw + 0.01, -hd + 0.03, seat + 0.2, -hw + 0.07, hd - 0.05, seat + 0.23), "main"),  # teak arms
                  Part(_box(hw - 0.07, -hd + 0.03, seat + 0.2, hw - 0.01, hd - 0.05, seat + 0.23), "main"),
                  Part(_box(-hw + 0.03, hd - 0.1, seat, -hw + 0.06, hd - 0.07, seat + 0.2), "main", color=frame),
                  Part(_box(hw - 0.06, hd - 0.1, seat, hw - 0.03, hd - 0.07, seat + 0.2), "main", color=frame)]
        return parts
    if t == "blind" and "venetian" in words:  # horizontal slat blind, slats half tilted: light in thin lines
        head, pitch = 0.05, 0.032
        parts = [Part(_box(-hw, -hd, h - head, hw, hd, h), "main"),  # head rail
                 Part(_box(-hw + 0.01, -hd + 0.01, 0, hw - 0.01, hd - 0.01, 0.02), "main")]  # bottom rail
        z = 0.03
        while z + 0.02 < h - head:
            parts.append(Part(_box(-hw + 0.01, -0.012, z, hw - 0.01, 0.012, z + 0.006), "main"))  # open slats
            z += pitch
        return parts
    if t == "vent" and "recovery" in words:  # heat-recovery-vent: square cover over a 160 mm wall core, round grille
        r = min(0.08, w * 0.4)  # 160 mm core
        return [Part(_box(-hw, -hd, 0, hw, hd - 0.006, h), "main"),
                Part(_box(-r - 0.006, hd - 0.006, h / 2 - r - 0.006, r + 0.006, hd + 0.001, h / 2 + r + 0.006), "dark",
                     "ycyl"),
                Part(_box(-r * 0.8, hd - 0.004, h / 2 - r * 0.8, r * 0.8, hd + 0.003, h / 2 + r * 0.8), "main", "ycyl"),
                Part(_box(-0.02, hd - 0.004, h / 2 - 0.02, 0.02, hd + 0.005, h / 2 + 0.02), "dark", "ycyl")]
    if t == "setting" and "place" in words:  # place-setting (diner on the +y side): plate, fork, knife, glass
        pr = min(0.135, hd * 0.95)
        return [Part(_box(-pr, -pr + hd * 0.1, 0, pr, pr + hd * 0.1, 0.012), "ceramic", "cyl"),
                Part(_box(-pr * 0.7, -pr * 0.7 + hd * 0.1, 0.012, pr * 0.7, pr * 0.7 + hd * 0.1, 0.018), "ceramic",
                     "cyl"),
                Part(_box(-pr - 0.05, -0.09, 0, -pr - 0.035, 0.11, 0.006), "chrome"),  # fork (diner's left)
                Part(_box(pr + 0.035, -0.10, 0, pr + 0.052, 0.11, 0.006), "chrome"),  # knife
                Part(_box(pr - 0.01, -hd, 0, pr + 0.06, -hd + 0.07, h), "glass", "cyl")]  # water glass
    if t == "bowl":  # serving-bowl with fruit
        return [Part(_box(-hw, -hd, 0, hw, hd, h * 0.6), "ceramic", "cyl"),
                *(Part(_box(x - 0.035, y - 0.035, h * 0.45, x + 0.035, y + 0.035, h * 0.45 + 0.07), "main", "cyl", c)
                  for x, y, c in ((-0.05, 0.0, "#d9b23a"), (0.04, 0.03, "#7aa83a"), (0.02, -0.05, "#c94a3a")))]
    if t == "visor" and "hood" in words:  # hood-visor: slim pull-out front of an integrated hood under a cabinet
        return [Part(_box(-hw, -hd, 0, hw, hd, h), "main"),
                Part(_box(-hw + 0.02, hd - 0.004, h * 0.3, hw - 0.02, hd + 0.001, h * 0.7), "dark")]
    if t == "notebooks":  # small stack of notebooks, each a different colour, slightly offset
        cols, th = ("#3d6fa8", "#d9a441", "#c9543f"), h / 3
        return [Part(_box(-hw + 0.01 * k, -hd + 0.006 * k, k * th, hw - 0.01 * (2 - k), hd - 0.006 * (2 - k),
                          (k + 1) * th - 0.001), "main", color=c) for k, c in enumerate(cols)]
    if t == "pencils":  # a few loose coloured pencils lying side by side
        cols = ("#d9a441", "#3d8a5a", "#c9543f", "#3d6fa8")
        return [Part(_box(-hw, -hd + k * d / 4 + 0.001, 0, hw, -hd + (k + 1) * d / 4 - 0.001, h), "main", color=c)
                for k, c in enumerate(cols)]
    if t == "case" and "pencil" in words:  # pencil-case standing upright, pencils sticking out
        body = h * 0.55
        parts = [Part(_box(-hw, -hd, 0, hw, hd, body), "main", "cyl")]
        cols = ("#d9a441", "#3d8a5a", "#c9543f", "#3d6fa8", "#e8d36a", "#8a4fa8")
        for k, c in enumerate(cols):
            a = 2 * math.pi * k / len(cols)
            x, y = hw * 0.45 * math.cos(a), hd * 0.45 * math.sin(a)
            parts.append(Part(_box(x - 0.0035, y - 0.0035, body * 0.5, x + 0.0035, y + 0.0035, h - 0.01 * (k % 3)), "main",
                              "cyl", c))
        return parts
    if t == "shoes":  # a pair: two low shoes side by side, rounded toes towards local +y
        sw, parts = w / 2 - 0.015, []
        for cx in (-w / 4, w / 4):
            parts += [Part(_box(cx - sw / 2, -hd, 0, cx + sw / 2, hd - sw / 2, h * 0.75), "main"),  # body + heel
                      Part(_box(cx - sw / 2, hd - sw, 0, cx + sw / 2, hd, h * 0.55), "main", "cyl"),  # rounded toe
                      Part(_box(cx - sw / 2 + 0.008, -hd + 0.03, h * 0.75, cx + sw / 2 - 0.008, -hd + 0.12, h), "main"),
                      Part(_box(cx - sw / 2, -hd, 0, cx + sw / 2, hd, 0.012), "dark")]  # sole
        return parts
    if t == "vase":  # ceramic vase: bulging body, narrow neck
        n, parts = 7, []
        for i in range(n):
            u = (i + 0.5) / n
            f = 0.55 + 0.45 * math.sin(math.pi * min(u * 1.25, 1.0)) if u < 0.8 else 0.38
            parts.append(Part(_box(-hw * f, -hd * f, h * i / n, hw * f, hd * f, h * (i + 1) / n), "ceramic", "cyl"))
        return parts
    if t == "niche":  # wall-niche (soap / shampoo): tiled frame, dark recess look, LED at the top, a few bottles
        f = 0.03
        parts = [Part(_box(-hw, -hd, 0, hw, -hd + 0.004, h), "dark"),  # recess back
                 Part(_box(-hw, -hd, 0, hw, hd, f), "main"), Part(_box(-hw, -hd, h - f, hw, hd, h), "main"),
                 Part(_box(-hw, -hd, 0, -hw + f, hd, h), "main"), Part(_box(hw - f, -hd, 0, hw, hd, h), "main"),
                 Part(_box(-hw + f, -hd, h - f - 0.008, hw - f, hd - 0.004, h - f), "emit", color="#ffd29e")]
        for x, bh, c in ((-0.17, 0.19, "#6b4a2e"), (-0.08, 0.15, "#2b2b2b"), (0.02, 0.21, "#c79a52"),
                         (0.13, 0.12, "#e9e4dc")):
            if abs(x) < hw - f - 0.03:
                parts.append(Part(_box(x - 0.025, -hd + 0.006, f, x + 0.025, -hd + 0.056, f + min(bh, h - 2 * f - 0.02)),
                                  "main", "cyl", c))
        return parts
    if t == "holder" and "paper" in words:  # toilet-paper-holder: wall plate + arm + white roll (along x)
        r = min(hd, h) * 0.5
        return [Part(_box(-0.03, -hd, h / 2 - 0.03, 0.03, -hd + 0.012, h / 2 + 0.03), "main"),
                Part(_box(-hw * 0.9, -hd + 0.012, h / 2 - 0.008, hw * 0.9, -hd + 0.03, h / 2 + 0.008), "main"),
                Part(_box(-hw * 0.75, -hd + 0.02, h / 2 - r * 0.9, hw * 0.75, -hd + 0.02 + 2 * r * 0.9, h / 2 + r * 0.9),
                     "soft", "xcyl", "#fbfaf7")]
    if t == "brush":  # toilet-brush in a cylinder holder
        return [Part(_box(-hw, -hd, 0, hw, hd, h * 0.45), "main", "cyl"),
                Part(_box(-0.008, -0.008, h * 0.45, 0.008, 0.008, h - 0.03), "main", "cyl"),
                Part(_box(-0.02, -0.02, h - 0.03, 0.02, 0.02, h), "main", "cyl")]
    if t == "stand" and "roll" in words:  # toilet-roll-stand: weighted base, rod, three spare rolls
        rr = min(hw, hd) * 0.85
        parts = [Part(_box(-hw, -hd, 0, hw, hd, 0.02), "main", "cyl"), Part(_box(-0.007, -0.007, 0, 0.007, 0.007, h), "main", "cyl")]
        for k in range(3):
            parts.append(Part(_box(-rr, -rr, 0.025 + k * 0.105, rr, rr, 0.12 + k * 0.105), "soft", "cyl", "#fbfaf7"))
        return parts
    if t == "mug":  # coffee mug: round body, handle, coffee inside
        return [Part(_box(-hw * 0.8, -hd * 0.8, 0, hw * 0.8, hd * 0.8, h), "ceramic", "cyl"),
                Part(_box(-hw * 0.68, -hd * 0.68, h - 0.015, hw * 0.68, hd * 0.68, h + 0.001), "main", "cyl", "#3b2416"),
                Part(_box(hw * 0.75, -0.006, h * 0.25, hw, 0.006, h * 0.8), "ceramic")]
    if t == "conditioner":  # air-conditioner: slim wall split unit, lighter front panel, outlet + louvre, display
        return [Part(_box(-hw, -hd, 0.03, hw, hd - 0.012, h), "main"),
                Part(_box(-hw + 0.005, hd - 0.012, 0.07, hw - 0.005, hd, h - 0.005), "main", color="#b4b7bb"),
                Part(_box(-hw + 0.04, -hd + 0.03, 0.0, hw - 0.04, hd - 0.02, 0.03), "black"),  # air outlet
                Part(_box(-hw + 0.05, hd - 0.03, 0.035, hw - 0.05, hd + 0.005, 0.05), "dark"),  # louvre
                Part(_box(hw - 0.16, hd, h * 0.45, hw - 0.08, hd + 0.002, h * 0.45 + 0.025), "emit", color="#bfe3ff")]
    if t in ("backsplash", "wallpaper"):  # thin wall panel; its surface comes from `apron` ([finishes]) in the build
        return [Part(_box(-hw, -hd, 0, hw, hd, h), "main")]
    if t == "bonsai":  # shallow pot, twisted trunk, flat foliage pads
        pot = min(0.07, h * 0.2)
        return [Part(_box(-hw, -hd, 0, hw, hd, pot), "main", color="#3b3b3d"),
                Part(_box(-hw + 0.01, -hd + 0.01, pot, hw - 0.01, hd - 0.01, pot + 0.008), "dark", color="#4a3a2a"),
                Part(_box(-0.016, -0.016, pot, 0.016, 0.016, h * 0.55), "main", "cyl", "#5a3d2b"),
                Part(_box(0.01, -0.012, h * 0.42, 0.04, 0.012, h * 0.72), "main", "cyl", "#5a3d2b"),
                Part(_box(-0.05, -0.01, h * 0.55, -0.02, 0.01, h * 0.8), "main", "cyl", "#5a3d2b"),
                Part(_box(-0.02, -hd * 0.8, h * 0.62, hw * 0.95, hd * 0.75, h * 0.74), "plant", "cyl"),
                Part(_box(-hw * 0.95, -hd * 0.7, h * 0.76, 0.03, hd * 0.6, h * 0.88), "plant", "cyl"),
                Part(_box(-hw * 0.5, -hd * 0.55, h * 0.88, hw * 0.45, hd * 0.55, h), "plant", "cyl")]
    if t == "sofa" and "corner" in words:  # L: seat along the back, chaise on the local left
        seat_d, back, arm = min(0.95, d * 0.6), 0.22, 0.18
        return [Part(_box(-hw, -hd + back, 0, hw, -hd + seat_d, 0.42), "soft"),
                Part(_box(-hw, -hd + seat_d, 0, -hw + 0.9, hd, 0.42), "soft"),
                Part(_box(-hw, -hd, 0, hw, -hd + back, h), "main"),
                Part(_box(-hw, -hd, 0, -hw + arm * 0.6, hd, 0.55), "main"),
                Part(_box(hw - arm, -hd, 0, hw, -hd + seat_d, 0.62), "main")]
    if t in ("sofa", "armchair"):
        back, arm = min(0.22, d * 0.25), min(0.18, w * 0.15)
        return [Part(_box(-hw, -hd + back, 0, hw, hd, 0.42), "soft"),
                Part(_box(-hw, -hd, 0, hw, -hd + back, h), "main"),
                Part(_box(-hw, -hd, 0, -hw + arm, hd, 0.62), "main"),
                Part(_box(hw - arm, -hd, 0, hw, hd, 0.62), "main")]
    if t in ("table", "desk"):
        top = 0.04
        if "round" in words:
            return [Part(_box(-hw, -hd, h - top, hw, hd, h), "main", "cyl"),
                    Part(_box(-0.06, -0.06, 0, 0.06, 0.06, h - top), "main", "cyl")]
        if "panel" in words:  # panel-desk: top in the piece's colour on two solid slab legs (dark shade)
            slab, inset = 0.05, 0.06
            return [Part(_box(-hw, -hd, h - top, hw, hd, h), "main"),
                    Part(_box(-hw + inset, -hd + 0.04, 0, -hw + inset + slab, hd - 0.04, h - top), "dark"),
                    Part(_box(hw - inset - slab, -hd + 0.04, 0, hw - inset, hd - 0.04, h - top), "dark")]
        return [Part(_box(-hw, -hd, h - top, hw, hd, h), "main"), *(Part(b, "main") for b in _legs(w, d, h - top))]
    if t == "curtain":  # sheer-curtain: transparent fabric in wave folds, ceiling to just above the floor
        return _wave(w, d, h, 0.10, "sheer" if "sheer" in words else "fabric")
    if t == "drape":  # heavy curtain stacked open: deeper, denser folds
        return _wave(w, d, h, 0.075, "fabric")
    if t == "chair" and "upholstered" in words:  # premium dining chair: slim brass legs, padded seat, one-piece
        seat, brass, parts = 0.47, "#b08d57", []  # upholstered shell back curving into low arms, rolled edges
        for x in (-hw + 0.05, hw - 0.05):
            for y in (-hd + 0.06, hd - 0.06):
                parts.append(Part(_box(x - 0.014, y - 0.014, 0.0, x + 0.014, y + 0.014, seat - 0.09), "handle", "cyl",
                                  color=brass))
        sh, arm_top = 0.07, seat + 0.20
        parts += [Part(_box(-hw + 0.005, -hd + 0.02, seat - 0.09, hw - 0.005, hd - 0.08, seat), "soft"),  # padded seat
                  Part(_box(-hw + 0.005, hd - 0.15, seat - 0.09, hw - 0.005, hd - 0.005, seat), "soft", "xcyl"),
                  Part(_box(-hw, -hd, seat - 0.09, hw, -hd + sh, h - 0.05), "soft"),  # shell back
                  Part(_box(-hw, -hd, h - 0.10, hw, -hd + sh, h), "soft", "xcyl"),  # rolled top
                  *(p for x1, x2 in ((-hw, -hw + sh), (hw - sh, hw)) for p in (  # low side wings + rolled tops
                      Part(_box(x1, -hd, seat - 0.09, x2, hd * 0.25, arm_top - 0.035), "soft"),
                      Part(_box(x1, -hd, arm_top - 0.07, x2, hd * 0.25, arm_top), "soft", "ycyl")))]
        return parts
    if t == "chair" and "gaming" in words:  # 5-star base, gas column, bolstered seat, tall back + headrest, arms
        seat, parts = 0.48, []
        for k in range(5):
            a = 2 * math.pi * k / 5
            x, y = math.cos(a) * hw * 0.62, math.sin(a) * hd * 0.62
            parts.append(Part(_box(min(0, x) - 0.025, min(0, y) - 0.025, 0.06, max(0, x) + 0.025, max(0, y) + 0.025,
                                   0.09), "dark"))
            parts.append(Part(_box(x - 0.03, y - 0.03, 0, x + 0.03, y + 0.03, 0.06), "black", "cyl"))  # caster
        parts.append(Part(_box(-0.03, -0.03, 0.09, 0.03, 0.03, seat - 0.08), "chrome", "cyl"))
        sw, back = min(0.52, w * 0.8), -hd + 0.06
        parts += [Part(_box(-sw / 2, back, seat - 0.08, sw / 2, hd - 0.04, seat), "main"),  # seat
                  Part(_box(-sw / 2, back, seat, -sw / 2 + 0.06, hd - 0.06, seat + 0.05), "main"),  # side bolsters
                  Part(_box(sw / 2 - 0.06, back, seat, sw / 2, hd - 0.06, seat + 0.05), "main"),
                  Part(_box(-sw / 2, -hd, seat, sw / 2, back, h - 0.18), "main"),  # backrest
                  Part(_box(-sw / 2 + 0.07, -hd, h - 0.18, sw / 2 - 0.07, back, h), "main"),  # headrest part
                  Part(_box(-sw / 2 - 0.02, -0.1, seat + 0.18, -sw / 2 + 0.04, 0.16, seat + 0.22), "dark"),  # arms
                  Part(_box(sw / 2 - 0.04, -0.1, seat + 0.18, sw / 2 + 0.02, 0.16, seat + 0.22), "dark"),
                  Part(_box(-sw / 2 - 0.0, -0.06, seat, -sw / 2 + 0.03, -0.02, seat + 0.18), "dark"),
                  Part(_box(sw / 2 - 0.03, -0.06, seat, sw / 2, -0.02, seat + 0.18), "dark")]
        return parts
    if t in ("chair", "stool"):
        seat = min(0.46, h)
        parts = [Part(_box(-hw, -hd, seat - 0.04, hw, hd, seat), "main"),
                 *(Part(b, "main") for b in _legs(w, d, seat - 0.04, 0.035, 0.02))]
        if t == "chair" and h > seat:
            parts.append(Part(_box(-hw, -hd, seat, hw, -hd + 0.04, h), "main"))
        return parts
    if t == "frame" and "vanity" in words:  # C-shaped floating vanity (90 deg corners): thick top under the
        top, thin = min(0.18, h * 0.4), min(0.04, h * 0.15)  # basin, thin side panel + thin bottom shelf
        return [Part(_box(-hw, -hd, h - top, hw, hd, h), "main"),
                Part(_box(hw - thin, -hd, thin, hw, hd, h - top), "main"),  # side: viewer's left (mirror = right)
                Part(_box(-hw, -hd, 0, hw, hd, thin), "main")]
    if t == "towels":  # folded towels: stacks ~30 cm wide, 3 folded layers each
        n = max(1, round(w / 0.32))
        sw, lh, parts = w / n, h / 3, []
        for i in range(n):
            x1, x2 = -hw + i * sw + 0.01, -hw + (i + 1) * sw - 0.01
            for k in range(3):
                e = 0.006 * (k % 2)  # alternate layers slightly inset, like real folds
                parts.append(Part(_box(x1 + e, -hd + e, k * lh, x2 - e, hd - e, (k + 1) * lh - 0.003), "soft"))
        return parts
    if t == "rug" and "organic" in words:  # modern pebble rug: overlapping soft ellipses = asymmetric outline
        blobs = ((0.0, 0.0, 0.40, 0.38), (-0.24, 0.10, 0.26, 0.34), (0.26, -0.08, 0.24, 0.36),
                 (0.06, 0.26, 0.32, 0.22), (-0.12, -0.24, 0.30, 0.24))  # centre x, y, radius x, y (fractions)
        top = max(h, 0.008)
        shade = "shag" if "shag" in words else "soft"  # organic-shag-rug: long-pile texture
        return [Part(_box((cx - rx) * w, (cy - ry) * d, 0, (cx + rx) * w, (cy + ry) * d, top * (0.86 + 0.035 * i)),
                     shade, "cyl") for i, (cx, cy, rx, ry) in enumerate(blobs)]  # 0.3 mm steps: no flicker
    if t == "rug":
        return [Part(_box(-hw, -hd, 0, hw, hd, max(h, 0.005)), "soft")]
    if t in ("toilet", "wc"):  # wall-hung: rounded bowl off the floor, carrier in the wall, flush plate
        top = 0.40
        return [Part(_box(-min(hw, 0.17), -hd, 0.25, min(hw, 0.17), -hd + 0.16, top), "ceramic"),
                Part(_box(-hw, -hd + 0.04, 0.20, hw, hd, top), "ceramic", "cyl"),
                Part(_box(-hw + 0.005, -hd + 0.05, top, hw - 0.005, hd - 0.005, top + 0.03), "ceramic", "cyl"),
                Part(_box(-0.12, -hd, min(0.95, h - 0.17), 0.12, -hd + 0.02, min(h, 1.12)), "chrome")]
    if t == "screen" and "slat" in words:  # slat-screen: free-standing vertical slats with small see-through gaps,
        slat, gap = 0.03, 0.015  # held by two thin battens at the back (top and bottom)
        n = max(1, int((w + gap) // (slat + gap)))
        x0 = -(n * slat + (n - 1) * gap) / 2
        parts = [Part(_box(x0 + i * (slat + gap), -hd + 0.006, 0, x0 + i * (slat + gap) + slat, hd, h), "main")
                 for i in range(n)]
        return parts + [Part(_box(-hw, -hd, z, hw, -hd + 0.006, z + 0.04), "dark") for z in (0.05, h - 0.09)]
    if t == "screen":  # bath-screen / shower-screen: fixed glass panel, thin brass profiles (wall side = -x)
        brass = "#b08d57"
        return [Part(_box(-hw + 0.012, -hd, 0.0, hw, hd, h - 0.012), "glass"),
                Part(_box(-hw, -hd - 0.004, 0.0, -hw + 0.012, hd + 0.004, h), "handle", color=brass),
                Part(_box(-hw + 0.012, -hd - 0.002, h - 0.012, hw, hd + 0.002, h), "handle", color=brass)]
    if t == "head" and "shower" in words:  # wall bar shower: mixer at the bottom, riser, arm, rain head
        brass, back = "#b08d57", -hd
        rr = min(hw, 0.15)
        return [Part(_box(-0.07, back, 0.0, 0.07, back + 0.03, 0.08), "handle", color=brass),  # mixer plate
                Part(_box(-0.025, back + 0.03, 0.02, 0.025, back + 0.08, 0.06), "handle", "ycyl", brass),  # knob
                Part(_box(-0.012, back + 0.035, 0.08, 0.012, back + 0.06, h - 0.02), "handle", "cyl", brass),
                Part(_box(-0.012, back + 0.035, h - 0.035, 0.012, hd - rr, h - 0.01), "handle", color=brass),
                Part(_box(-rr, hd - 2 * rr, h - 0.045, rr, hd, h - 0.035), "handle", "cyl", brass)]  # rain head
    if t in ("bathtub", "bath"):
        return _basin(-hw, -hd, hw, hd, 0, h, wall=0.06)
    if t == "shower":  # tray + glass on front and both sides + head on the back wall
        g = 0.008
        top = h if h >= 2.4 else min(h, 2.0)  # a ceiling-height piece gets floor-to-ceiling glass
        base = ([Part(_box(-hw + 0.05, -hd + 0.03, 0.0, hw - 0.05, -hd + 0.07, 0.006), "black"),  # linear drain,
                 Part(_box(-hw + 0.01, hd - 0.045, 0.0, hw, hd - 0.005, 0.03), "main", color="#a89886")]  # tile-colour
                if "walk" in words else [Part(_box(-hw, -hd, 0, hw, hd, 0.04), "ceramic")])  # curb on the open edge
        return [*base,
                Part(_box(-hw, hd - g, 0.04, hw - 0.6, hd, top), "glass"),
                Part(_box(-hw, -hd, 0.04, -hw + g, hd, top), "glass"),
                Part(_box(hw - g, -hd, 0.04, hw, hd, top), "glass"),
                *([] if "walk" in words else [Part(_box(-0.15, -hd, h - 0.03, 0.15, -hd + 0.3, h), "chrome")])]
    if t == "sink" and "vessel" in words:  # round bowl standing on the top + brass spout from the wall
        n, parts = 6, []
        for i in range(n):  # narrow foot widening to the rim
            f = 0.55 + 0.45 * math.sin(math.pi / 2 * (i + 1) / n)
            parts.append(Part(_box(-hw * f, -hd * f, h * i / n, hw * f, hd * f, h * (i + 1) / n), "ceramic", "cyl"))
        parts.append(Part(_box(-hw * 0.88, -hd * 0.88, h * 0.7, hw * 0.88, hd * 0.88, h + 0.001), "ceramic",
                          "cyl"))  # inside of the bowl (the sink's colour; within the widest slices)
        brass = "#b08d57"
        parts += [Part(_box(-0.03, -hd - 0.055, h + 0.06, 0.03, -hd - 0.045, h + 0.16), "handle", "box", brass),
                  Part(_box(-0.012, -hd - 0.05, h + 0.10, 0.012, -hd + 0.11, h + 0.122), "handle", "box", brass),
                  Part(_box(0.06, -hd - 0.05, h + 0.095, 0.075, -hd + 0.0, h + 0.11), "handle", "box", brass)]
        return parts
    if t == "sink":  # basin(s) - 'double-sink' gets two
        n = 2 if "double" in words else 1
        bw, parts = w / n, []
        for i in range(n):
            x1 = -hw + i * bw + 0.03
            parts += _basin(x1, -hd + 0.06, x1 + bw - 0.06, hd, 0, h)
            tap = "black" if "black" in words else "chrome"  # black-sink: matte black faucet
            parts.append(Part(_box(x1 + bw / 2 - 0.045, -hd, 0, x1 + bw / 2 - 0.015, -hd + 0.05,
                                   h + (0.30 if tap == "black" else 0.18)), tap))
            if "black" in words:  # gooseneck spout reaching over the bowl
                parts.append(Part(_box(x1 + bw / 2 - 0.045, -hd + 0.05, h + 0.27, x1 + bw / 2 - 0.015, -hd + 0.2,
                                       h + 0.30), tap))
        return parts
    if t == "machine":  # washing-machine / drying-machine: body, control strip, round door
        # details stand proud of the body's front (no coplanar faces -> no flicker), slightly inset from the
        # sides and top so no edge is shared with the body
        f, door_z = hd - 0.032, min(h * 0.42, h - 0.33)  # body front (details reach hd), door centre
        r = min(0.2, hw - 0.06, door_z - 0.03)
        return [Part(_box(-hw, -hd, 0.01, hw, f, h), "ceramic"),
                Part(_box(-hw + 0.01, -hd + 0.01, 0.0, hw - 0.01, f - 0.03, 0.01), "dark"),  # recessed feet line
                Part(_box(-hw + 0.012, f - 0.01, h - 0.13, hw - 0.012, f + 0.006, h - 0.015), "ceramic",
                     color="#e3e3e1"),  # control strip
                Part(_box(-hw + 0.04, f + 0.006, h - 0.10, -hw + 0.20, f + 0.008, h - 0.05), "black"),  # drawer
                Part(_box(0.02, f + 0.006, h - 0.095, 0.15, f + 0.009, h - 0.05), "black"),  # display
                Part(_box(hw - 0.12, f + 0.006, h - 0.115, hw - 0.05, f + 0.03, h - 0.045), "chrome", "ycyl"),
                Part(_box(-r, f - 0.01, door_z - r, r, f + 0.022, door_z + r), "chrome", "ycyl"),  # door ring
                Part(_box(-r * 0.78, f - 0.01, door_z - r * 0.78, r * 0.78, f + 0.03, door_z + r * 0.78), "black",
                     "ycyl")]  # glass
    if t == "fridge" and "glass" in words:  # glass-fridge: 2 tall smoked-glass doors, lit shelves + food inside
        f, k = hd - 0.025, 0.02  # inner front plane, wall thickness
        parts = [Part(_box(-hw, -hd, 0, hw, -hd + k, h), "black"), Part(_box(-hw, -hd, 0, -hw + k, f, h), "black"),
                 Part(_box(hw - k, -hd, 0, hw, f, h), "black"), Part(_box(-hw, -hd, h - k, hw, f, h), "black"),
                 Part(_box(-hw, -hd, 0, hw, f, 0.10), "black"),  # plinth / base
                 Part(_box(-hw + k, -hd + k, 0.10, hw - k, -hd + k + 0.005, h - k), "soft", color="#d9d9d6"),  # back
                 Part(_box(-hw + k, -hd + k, h - k - 0.012, hw - k, f - 0.02, h - k), "emit", color="#f2f6ff")]
        for z in (0.55, 0.95, 1.30, 1.62):  # glass shelves
            parts.append(Part(_box(-hw + k, -hd + k, z, hw - k, f - 0.03, z + 0.008), "chrome"))
        food = ((-0.16, 0.10, 0.08, 0.20, "#f4f4f2"), (0.05, 0.12, 0.10, 0.14, "#c94a3a"), (-0.12, 0.96, 0.12, 0.10, "#e3c75a"),
                (0.12, 0.96, 0.09, 0.16, "#5c8a3a"), (0.0, 1.31, 0.18, 0.08, "#d9a066"), (-0.15, 1.63, 0.08, 0.22, "#f4f4f2"))
        for x, z, fw, fh, col in food:
            parts.append(Part(_box(x - fw / 2, -0.12, z + 0.56 if z < 0.5 else z, x + fw / 2, 0.02,
                                   (z + 0.56 if z < 0.5 else z) + fh), "main", color=col))
        for x1, x2 in ((-hw, -0.002), (0.002, hw)):  # two doors: smoked glass in a thin black frame
            parts += [Part(_box(x1 + 0.012, f, 0.10, x2 - 0.012, hd - 0.004, h - 0.012), "smoked"),
                      Part(_box(x1, f, 0.10, x2, hd, 0.112), "black"), Part(_box(x1, f, h - 0.012, x2, hd, h), "black"),
                      Part(_box(x1, f, 0.10, x1 + 0.012, hd, h), "black"), Part(_box(x2 - 0.012, f, 0.10, x2, hd, h), "black")]
        parts += [Part(_box(-0.035, hd, 0.75, -0.022, hd + 0.03, 1.55), "black"),  # bar handles at the meeting stiles
                  Part(_box(0.022, hd, 0.75, 0.035, hd + 0.03, 1.55), "black")]
        return parts
    if t in ("fridge", "freezer"):
        return [Part(_box(-hw, -hd, 0, hw, hd - 0.02, h), "main"),
                Part(_box(-hw, hd - 0.02, 0, hw - 0.07, hd, h), "main"),
                Part(_box(hw - 0.06, hd - 0.02, min(0.9, h * 0.5), hw - 0.04, hd, min(1.3, h * 0.9)), "handle")]
    if t == "oven":
        return [Part(_box(-hw, -hd, 0, hw, hd - 0.01, h), "main"),
                Part(_box(-hw + 0.01, hd - 0.01, 0.02, hw - 0.01, hd, h - 0.1), "black"),
                Part(_box(-hw + 0.01, hd - 0.01, h - 0.09, hw - 0.01, hd, h - 0.01), "dark")]
    if t in ("cooktop", "hob"):
        return [Part(_box(-hw, -hd, 0, hw, hd, h), "black")]
    if t == "hood":  # cooker-hood: canopy + chimney up to its height
        return [Part(_box(-hw, -hd, 0, hw, hd, 0.08), "main"),
                Part(_box(-0.13, -hd, 0.08, 0.13, -hd + 0.25, h), "main")]
    if t == "monitor":  # computer screen on a stand: thin panel at the back, neck, flat foot
        panel_z = min(0.12, h * 0.25)
        return [Part(_box(-hw, -hd, panel_z, hw, -hd + 0.025, h), "black"),
                Part(_box(-0.03, -hd + 0.025, 0.01, 0.03, -hd + 0.05, panel_z + 0.08), "dark"),
                Part(_box(-0.11, -hd, 0, 0.11, hd, 0.012), "dark")]
    if t == "mouse":  # rounded mouse
        return [Part(_box(-hw, -hd, 0, hw, hd, h), "main", "cyl")]
    if t == "tv" and "wall" in words:  # wall-tv: slim panel on a flush bracket, thin bezel
        return [Part(_box(-0.2, -hd, 0.25 * h, 0.2, -hd + 0.012, 0.75 * h), "dark"),
                Part(_box(-hw, -hd + 0.012, 0, hw, hd, h), "black"),
                Part(_box(-hw + 0.006, hd - 0.001, 0.006, hw - 0.006, hd + 0.001, h - 0.006), "dark")]
    if t == "tv":
        return [Part(_box(-hw, -hd, 0.06, hw, hd, h), "black"), Part(_box(-0.15, -0.1, 0, 0.15, 0.1, 0.06), "dark")]
    if t == "panel" and "slat" in words:  # wooden slats on a dark backing
        parts, x, slat = [Part(_box(-hw, -hd, 0, hw, -hd + 0.01, h), "dark")], -hw, 0.03
        while x + slat <= hw + 1e-9:
            parts.append(Part(_box(x, -hd + 0.01, 0, x + slat, hd, h), "main"))
            x += slat * 2
        return parts
    if t == "plant":
        pot = min(0.35, h * 0.35)
        return [Part(_box(-hw * 0.6, -hd * 0.6, 0, hw * 0.6, hd * 0.6, pot), "dark", "cyl"),
                Part(_box(-hw, -hd, pot, hw, hd, h), "plant", "cyl")]
    if t in LIGHT_WORDS:
        if "track" in words:  # slim rail on the ceiling; the spot heads are built per [track] head
            return [Part(_box(-hw, -hd, h - 0.035, hw, hd, h), "main"),  # rail in the piece's colour (V1: black)
                    Part(_box(-hw + 0.004, -hd * 0.4, h - 0.037, hw - 0.004, hd * 0.4, h - 0.035), "dark")]
        if t == "strip":  # LED strip in an aluminium profile: all of it glows
            return [Part(_box(-hw, -hd, 0, hw, hd, h), "emit")]
        if "infinity" in words:  # twisted 3D figure-eight LED band (lemniscate), glowing underneath, on 3 cables
            n, band, parts = 120, 0.035, []
            amp = min(0.10, h * 0.2)  # how far the loops twist up / down
            mid = band + amp

            def pt(a):
                q = 1 + math.sin(a) ** 2
                return (hw * 0.96 * math.cos(a) / q, hd * 0.96 * math.sin(a) * math.cos(a) / q / 0.3536,
                        mid + amp * math.sin(a))
            for i in range(n):
                (x1, y1, z1), (x2, y2, z2) = pt(2 * math.pi * i / n), pt(2 * math.pi * (i + 1) / n)
                cx, cy, cz = (x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2
                ex, ey = abs(x2 - x1) / 2 + 0.012, abs(y2 - y1) / 2 + 0.012
                parts.append(Part(_box(cx - ex, cy - ey, cz - band / 2 + 0.006, cx + ex, cy + ey, cz + band / 2), "main"))
                parts.append(Part(_box(cx - ex * 0.8, cy - ey * 0.8, cz - band / 2, cx + ex * 0.8, cy + ey * 0.8,
                                       cz - band / 2 + 0.006), "emit"))
            for k in range(3):  # cables to the ceiling
                x, y, z = pt(2 * math.pi * k / 3 + 0.4)
                parts.append(Part(_box(x - 0.002, y - 0.002, z + band / 2, x + 0.002, y + 0.002, h), "black"))
            return parts
        if "ring" in words:  # LED ring (pendant on 3 cables, or flush on the ceiling)
            ring_h, n, parts = min(0.05, h), 36, []
            seg = math.pi * (w + d) / 2 / n * 0.62  # half-length of one segment
            rx, ry = hw - seg - 0.026, hd - seg - 0.026  # ellipse that stays inside the footprint
            for i in range(n):
                a = 2 * math.pi * i / n
                cx, cy = rx * math.cos(a), ry * math.sin(a)
                ex, ey = abs(math.cos(a)) * seg + abs(math.sin(a)) * 0.025, abs(math.sin(a)) * seg + abs(math.cos(a)) * 0.025
                parts.append(Part(_box(cx - ex, cy - ey, 0.012, cx + ex, cy + ey, ring_h), "main"))
                parts.append(Part(_box(cx - ex * 0.8, cy - ey * 0.8, 0.0, cx + ex * 0.8, cy + ey * 0.8, 0.012), "emit"))
            if "pendant" in words:
                for i in range(3):
                    a = 2 * math.pi * i / 3 + math.pi / 2
                    cx, cy = rx * math.cos(a), ry * math.sin(a)
                    parts.append(Part(_box(cx - 0.003, cy - 0.003, ring_h, cx + 0.003, cy + 0.003, h), "black"))
            return parts
        if "linear" in words:  # linear LED bar on two cables
            bar = min(0.06, h)
            return [Part(_box(-hw, -hd, 0.015, hw, hd, bar), "main"),
                    Part(_box(-hw + 0.01, -hd + 0.005, 0, hw - 0.01, hd - 0.005, 0.015), "emit"),
                    Part(_box(-hw * 0.8, -0.003, bar, -hw * 0.8 + 0.006, 0.003, h), "black"),
                    Part(_box(hw * 0.8 - 0.006, -0.003, bar, hw * 0.8, 0.003, h), "black")]
        if "panel" in words:  # square LED panel: thin frame, glowing face
            return [Part(_box(-hw, -hd, min(0.008, h / 2), hw, hd, h), "main"),
                    Part(_box(-hw + 0.015, -hd + 0.015, 0, hw - 0.015, hd - 0.015, min(0.008, h / 2)), "emit")]
        if "recessed" in words:  # flush downlight: only the glowing lens shows
            return [Part(_box(-hw, -hd, 0, hw, hd, h), "main", "cyl"),
                    Part(_box(-hw * 0.7, -hd * 0.7, 0, hw * 0.7, hd * 0.7, min(0.005, h)), "emit", "cyl")]
        if "pendant" in words:  # cord from the ceiling + shade, glowing underside
            sh = min(0.3, h * 0.3)
            return [Part(_box(-0.006, -0.006, sh, 0.006, 0.006, h), "black"),
                    Part(_box(-hw, -hd, 0.02, hw, hd, sh), "main", "cyl"),
                    Part(_box(-hw * 0.8, -hd * 0.8, 0.0, hw * 0.8, hd * 0.8, 0.02), "emit", "cyl")]
        if t == "lamp" and ("floor" in words or "table" in words):
            sh = h * 0.25
            return [Part(_box(-hw * 0.5, -hd * 0.5, 0, hw * 0.5, hd * 0.5, 0.03), "dark", "cyl"),
                    Part(_box(-0.012, -0.012, 0.03, 0.012, 0.012, h - sh), "dark", "cyl"),
                    Part(_box(-hw, -hd, h - sh, hw, hd, h), "soft", "cyl"),
                    Part(_box(-hw * 0.7, -hd * 0.7, h - sh - 0.005, hw * 0.7, hd * 0.7, h - sh), "emit", "cyl")]
        # ceiling / wall / spot fixture: body + glowing diffuser underneath
        return [Part(_box(-hw, -hd, min(0.01, h / 2), hw, hd, h), "main", "cyl"),
                Part(_box(-hw * 0.9, -hd * 0.9, 0, hw * 0.9, hd * 0.9, min(0.01, h / 2)), "emit", "cyl")]
    if t == "mirror" and "backlit" in words:  # pill mirror, thin brass frame, LED halo glowing on the wall
        return [*_pill(w + 0.05, h + 0.05, -hd, -hd + 0.004, "emit", WARM_WHITE, z0=-0.025),
                *_pill(w + 0.012, h + 0.012, -hd + 0.004, hd - 0.004, "handle", "#b08d57", z0=-0.006),
                *_pill(w, h, -hd + 0.008, hd, "mirror")]
    if t == "mirror":
        return [Part(_box(-hw, -hd, 0, hw, hd, h), "mirror")]
    if t == "boiler":  # wall-hung hot-water tank: upright cylinder with domed ends + thermostat
        dome, n = min(hw, hd, h / 4) * 0.6, 14
        parts = [Part(_box(-hw, -hd, dome, hw, hd, h - dome), "main", "cyl")]
        for i in range(n):
            za, zb = dome * i / n, dome * (i + 1) / n
            f = math.sqrt(max(1 - (1 - (za + zb) / 2 / dome) ** 2, 0.0)) * 0.85 + 0.15
            parts += [Part(_box(-hw * f, -hd * f, za, hw * f, hd * f, zb), "main", "cyl"),
                      Part(_box(-hw * f, -hd * f, h - zb, hw * f, hd * f, h - za), "main", "cyl")]
        parts += [Part(_box(-0.07, hd - 0.03, h * 0.18, 0.07, hd + 0.005, h * 0.18 + 0.12), "dark"),
                  Part(_box(-0.10, -0.012, -0.08, -0.076, 0.012, dome), "chrome", "cyl"),
                  Part(_box(0.076, -0.012, -0.08, 0.10, 0.012, dome), "chrome", "cyl")]
        return parts
    return [Part(_box(-hw, -hd, 0, hw, hd, h), "main")]


# --------------------------------------------------------------------------- storage
def auto_modules(type_: str, w: float, h: float) -> tuple[Module, ...]:
    """Default modules when a storage piece has none: doors <= 60 cm (pairs above), or drawers.

    Library defaults: ``open-...`` (open-shelf-unit) = open modules with evenly spaced shelves; ``toy-chest`` =
    one flap front; ``mirror-...`` (mirror-cabinet) = mirror doors."""
    words = type_.split("-")
    if "open" in words:
        n = max(1, math.ceil(w / 0.9 - 1e-6))
        k = min(5, max(2, round(h / 0.38) - 1))  # inner shelves (+ bottom + top = 4-7 surfaces)
        shelves = tuple(Fitting("shelf", round(h * (i + 1) / (k + 1), 3)) for i in range(k))
        return tuple(Module(w / n, (Front("open"),), interior=shelves) for _ in range(n))
    if "toy" in words and _last(type_) == "chest":
        return (Module(w, (Front("flap"),)),)
    if _last(type_) in DRAWER_WORDS:
        n = max(1, math.ceil(w / 0.9 - 1e-6))
        count = max(1, min(6, round(h / 0.25)))
        return tuple(Module(w / n, (Front("drawers", None, count),)) for _ in range(n))
    n = max(1, math.ceil(w / 0.6 - 1e-6))
    kinds = ["door-left", "door-right"]
    finish = "mirror" if "mirror" in words else "matte"
    return tuple(Module(w / n, (Front(kinds[i % 2] if n > 1 else "door-left"),), finish=finish) for i in range(n))


def default_storage(type_: str) -> Storage:
    """Storage settings when a piece has no [storage]: mirror cabinets are push-to-open (no handles)."""
    return Storage(handles=False) if "mirror" in type_.split("-") else Storage()


def modules_of(item: Item) -> tuple[Module, ...]:
    if item.storage and item.storage.modules:
        return item.storage.modules
    return auto_modules(item.type, item.size[0], item.size[2])


def plinth_of(item: Item) -> float:
    if item.storage and item.storage.plinth is not None:
        return item.storage.plinth
    return 0.08 if item.elevation == 0 else 0.0


@dataclass(frozen=True)
class MovingPart:
    """A front that opens. Boxes are relative to ``pivot`` (local frame of the piece).

    motion: 'hinge' (rotate about the vertical pivot axis by ``amount`` rad, + = CCW),
            'flap' (rotate about the horizontal x axis), 'slide' (move +y by ``amount`` m), 'none'.
    """

    name: str  # e.g. "m2-door-left", "m1-drawer-3"
    module: int  # 1-based
    parts: tuple[Part, ...]
    pivot: tuple[float, float, float]
    motion: str
    amount: float


@dataclass(frozen=True)
class StorageLayout:
    carcass: tuple[Part, ...]
    fronts: tuple[MovingPart, ...]
    interior: tuple[tuple[str, int, Part], ...]  # (part name e.g. "m2/shelf-1", module, part)
    modules: tuple[tuple[float, float], ...]  # x range of each module (local)


def _handle_z(za: float, zb: float, elevation: float, long: float = 0.0) -> tuple[float, float] | None:
    """Vertical handle span on a door: at hand height for tall doors, near the edge otherwise.
    ``long`` > 0: a long bar of that length on tall doors only (None = no handle, push-to-open)."""
    if long:
        if zb - za <= 1.2:
            return None
        length = min(long, (zb - za) * 0.6)
        c = min(max(1.05 - elevation, za + length / 2 + 0.05), zb - length / 2 - 0.05)
        return c - length / 2, c + length / 2
    length = min(0.30, (zb - za) * 0.5)
    if zb - za > 1.2:  # tall door: centred about 1.05 m above the floor
        c = min(max(1.05 - elevation, za + length / 2 + 0.05), zb - length / 2 - 0.05)
    elif elevation > 1.0:  # wall cabinet: near the bottom edge
        c = za + 0.06 + length / 2
    else:  # base cabinet: near the top edge
        c = zb - 0.06 - length / 2
    return c - length / 2, c + length / 2


def _stack(fronts: tuple[Front, ...], z0: float, z1: float) -> list[tuple[Front, float, float]]:
    """Assign z ranges to a module's fronts, top -> bottom; fronts without height share the rest."""
    fixed = sum(f.height for f in fronts if f.height is not None)
    free = [f for f in fronts if f.height is None]
    share = max(0.0, (z1 - z0 - fixed) / len(free)) if free else 0.0
    out, top = [], z1
    for f in fronts:
        hgt = f.height if f.height is not None else share
        out.append((f, top - hgt, top))
        top -= hgt
    return out


def storage_layout(item: Item) -> StorageLayout:
    """Carcass, openable fronts and interior fittings of a storage piece (local frame)."""
    w, d, h = item.size
    hw, hd = w / 2, d / 2
    st = item.storage or default_storage(item.type)
    mods = modules_of(item)
    p = plinth_of(item)
    yc0, yc1 = -hd, hd - FRONT_T  # carcass depth (fronts sit in front of it)
    yf = hd - FRONT_T / 2  # front mid-plane
    zi0, zi1 = p + PANEL, h - PANEL  # inner height

    carcass = [Part(_box(-hw, yc0, p, -hw + PANEL, yc1, h), "main"), Part(_box(hw - PANEL, yc0, p, hw, yc1, h), "main"),
               Part(_box(-hw, yc0, p, hw, yc1, p + PANEL), "main"), Part(_box(-hw, yc0, h - PANEL, hw, yc1, h), "main"),
               Part(_box(-hw, yc0, p, hw, yc0 + BACK, h), "main")]
    if p > 0:
        carcass.append(Part(_box(-hw + 0.01, yc0 + 0.02, 0, hw - 0.01, yc1 - 0.04, p), "dark"))

    total = sum(m.width for m in mods)
    scale = w / total if total > 0 else 1.0  # tolerate rounding; the validator reports real mismatches
    fronts: list[MovingPart] = []
    interior: list[tuple[str, int, Part]] = []
    ranges = []
    x = hw  # module 1 is on the viewer's left = local +x (the viewer faces -y)
    for k, m in enumerate(mods, start=1):
        xa, xb = x - m.width * scale, x
        x = xa
        ranges.append((xa, xb))
        if k < len(mods):
            carcass.append(Part(_box(xa - PANEL / 2, yc0 + BACK, zi0, xa + PANEL / 2, yc1, zi1), "main"))
        il = xa + (PANEL if k == len(mods) else PANEL / 2)  # inner low-x side (viewer's right)
        ir = xb - (PANEL if k == 1 else PANEL / 2)  # inner high-x side (viewer's left)
        color = m.front_color or item.color

        def fp(x1, x2, z1, z2, color=color, finish=m.finish):
            return Part(_box(x1, -FRONT_T / 2, z1, x2, FRONT_T / 2, z2), "front", color=color, finish=finish)

        def handle(x1, x2, z1, z2, drawer=False):
            if not st.handles or not (drawer or st.door_handles):  # push-to-open: no handle (dropped below)
                return None
            return Part(_box(x1, FRONT_T / 2, z1, x2, FRONT_T / 2 + 0.025, z2), "handle", color=st.handle_color)

        counts: dict[str, int] = {}
        stack = _stack(m.fronts, p + GAP, h - GAP)
        for (fa, za_, _), (fb, _, _) in zip(stack, stack[1:], strict=False):  # fixed shelf where two fronts meet:
            if fa.kind != fb.kind or "open" in (fa.kind, fb.kind):  # closes an open niche over / under drawers
                carcass.append(Part(_box(il, yc0 + BACK, za_ - PANEL / 2, ir, yc1, za_ + PANEL / 2), "main"))
        for f, za, zb in stack:
            za, zb = za + GAP / 2, zb - GAP / 2
            if f.kind == "open":
                continue
            leaves = []
            # (name, x1, x2, sign): hinge on the viewer's left = high x, opens clockwise (sign -1)
            if f.kind in ("door-left", "doors"):
                lo = (xa + xb) / 2 + GAP / 2 if f.kind == "doors" else xa + GAP
                leaves.append(("door-left", lo, xb - GAP, -1))
            if f.kind in ("door-right", "doors"):
                hi = (xa + xb) / 2 - GAP / 2 if f.kind == "doors" else xb - GAP
                leaves.append(("door-right", xa + GAP, hi, +1))
            for name, x1, x2, sign in leaves:
                pivot_x = x1 if sign > 0 else x2
                hz = ((za + 0.04, za + 0.04 + min(0.30, (zb - za) * 0.5)) if st.handles_low
                      else _handle_z(za, zb, item.elevation, st.handle_length))
                hx = (x2 - 0.06, x2 - 0.045) if sign > 0 else (x1 + 0.045, x1 + 0.06)
                parts = tuple(q for q in (fp(x1 - pivot_x, x2 - pivot_x, za, zb),
                                          handle(hx[0] - pivot_x, hx[1] - pivot_x, *hz) if hz else None) if q)
                counts[name] = counts.get(name, 0) + 1
                fronts.append(MovingPart(f"m{k}-{name}-{counts[name]}", k, parts, (pivot_x, yf, 0.0), "hinge",
                                         sign * math.radians(100)))
            if f.kind in ("drawer", "drawers"):
                n = f.count if f.kind == "drawers" else 1
                dh = (zb - za) / n
                for i in range(n):
                    z1, z2 = zb - (i + 1) * dh + GAP / 2, zb - i * dh - GAP / 2
                    cx = (xa + xb) / 2
                    hl = min(0.3, (xb - xa) * 0.5)
                    parts = [fp(xa + GAP - cx, xb - GAP - cx, z1, z2),
                             handle(-hl / 2, hl / 2, z2 - 0.05, z2 - 0.035, True) if z2 - z1 > 0.12 else
                             handle(-hl / 2, hl / 2, (z1 + z2) / 2 - 0.008, (z1 + z2) / 2 + 0.008, True)]
                    parts = [q for q in parts if q]
                    # drawer body behind the front (bottom + sides + back)
                    bx1, bx2 = il + 0.012 - cx, ir - 0.012 - cx
                    by1, by2 = yc0 + BACK + 0.03 - yf, -FRONT_T / 2
                    bz1, bz2 = z1 + 0.02, z2 - 0.03
                    if bz2 > bz1 + 0.02:
                        parts += [Part(_box(bx1, by1, bz1, bx2, by2, bz1 + 0.012), "interior"),
                                  Part(_box(bx1, by1, bz1, bx1 + 0.012, by2, bz2), "interior"),
                                  Part(_box(bx2 - 0.012, by1, bz1, bx2, by2, bz2), "interior"),
                                  Part(_box(bx1, by1, bz1, bx2, by1 + 0.012, bz2), "interior")]
                    counts["drawer"] = counts.get("drawer", 0) + 1
                    fronts.append(MovingPart(f"m{k}-drawer-{counts['drawer']}", k, tuple(parts), (cx, yf, 0.0), "slide",
                                             0.75 * (yc1 - yc0)))
            if f.kind == "flap":
                parts = tuple(q for q in (fp(xa + GAP - xa, xb - GAP - xa, za - zb, 0.0),
                                          handle((xb - xa) / 2 - 0.15, (xb - xa) / 2 + 0.15, za - zb + 0.03,
                                                 za - zb + 0.045)) if q)
                counts["flap"] = counts.get("flap", 0) + 1
                fronts.append(MovingPart(f"m{k}-flap-{counts['flap']}", k, parts, (xa, yf, zb), "flap", math.radians(100)))
            if f.kind == "panel":  # fixed front (appliance door, blind panel)
                cx = (xa + xb) / 2
                counts["panel"] = counts.get("panel", 0) + 1
                hl = min(0.3, (xb - xa) * 0.5)  # integrated appliance: horizontal bar along the top edge
                parts = tuple(q for q in (fp(xa + GAP - cx, xb - GAP - cx, za, zb),
                                          handle(-hl / 2, hl / 2, zb - 0.05, zb - 0.035)) if q)
                fronts.append(MovingPart(f"m{k}-panel-{counts['panel']}", k, parts, (cx, yf, 0.0), "none", 0.0))

        n_by_kind: dict[str, int] = {}
        for fit in sorted(m.interior, key=lambda f: (f.kind, f.x if f.kind == "divider" else f.z)):
            n_by_kind[fit.kind] = n_by_kind.get(fit.kind, 0) + 1
            name = f"m{k}/{fit.kind}-{n_by_kind[fit.kind]}"
            if fit.kind == "shelf":
                part = Part(_box(il, yc0 + BACK, fit.z - PANEL, ir, yc1 - 0.02, fit.z), "interior")
            elif fit.kind == "rail":
                yc = (yc0 + yc1) / 2
                part = Part(_box(il, yc - 0.0125, fit.z - 0.0125, ir, yc + 0.0125, fit.z + 0.0125), "chrome")
            elif fit.kind == "divider":
                xd = ir - fit.x  # measured from the viewer's left
                part = Part(_box(xd - PANEL / 2, yc0 + BACK, zi0, xd + PANEL / 2, yc1 - 0.02, zi1), "interior")
            else:  # inner drawer
                part = Part(_box(il + 0.01, yc0 + BACK + 0.03, fit.z, ir - 0.01, yc1 - 0.03, fit.z + fit.height), "interior")
            interior.append((name, k, part))
    return StorageLayout(tuple(carcass), tuple(fronts), tuple(interior), tuple(ranges))


# --------------------------------------------------------------------------- validation
# last words of pieces that lie on / in others (rugs, sinks in counters) or are paint / panels on the wall:
# never reported as overlapping
FLAT_OR_ON_OTHERS = frozenset({"rug", "doormat", "towels", "strip", "wallpaper", "head", "niche", "sink", "arch",
                               "block", "panelling", "paneling"})


def _door_zone(apt: Apartment, o) -> list[Point]:
    """The quarter-circle a door leaf sweeps (convex polygon), or [] if its swing is unknown."""
    if not o.hinge:
        return []
    w = apt.wall(o.wall)
    leaf, arc = door_swing(w.rect, w.horizontal, o.span, o.hinge, o.swing, segments=8)
    return [leaf[0], *arc]


def serves(point: FixedPoint, item: Item) -> bool:
    """True if ``item``'s type is one the fixed point is for (full type or its last word)."""
    return item.type in point.serves or _last(item.type) in point.serves


def on_point(point: FixedPoint, item: Item) -> bool:
    return item.room == point.room and point_polygon_distance(point.position, item.footprint()) <= point.radius + 1e-9


def _validate_storage(it: Item, err) -> None:
    h = it.size[2]
    st = it.storage
    if st is None:
        return
    for c in (st.handle_color, *([st.interior_color] if st.interior_color else [])):
        if not COLOR_RE.match(c):
            err("storage", f"{it.id}: colour '{c}' is not #rrggbb")
    if not st.modules:
        return
    total = sum(m.width for m in st.modules)
    if abs(total - it.size[0]) > 0.01:
        err("storage", f"{it.id}: module widths add up to {total:.3f} m, the piece is {it.size[0]:.3f} m wide")
    for k, m in enumerate(st.modules, start=1):
        where = f"{it.id}/m{k}"
        if m.width <= 0.05:
            err("storage", f"{where}: width {m.width} m is too small")
        if m.finish not in FINISHES:
            err("storage", f"{where}: finish '{m.finish}' - use one of {', '.join(FINISHES)}")
        if m.front_color and not COLOR_RE.match(m.front_color):
            err("storage", f"{where}: front_color '{m.front_color}' is not #rrggbb")
        for f in m.fronts:
            if f.kind not in FRONT_KINDS:
                err("storage", f"{where}: front '{f.kind}' - use one of {', '.join(FRONT_KINDS)}")
            if f.count < 1 or (f.height is not None and f.height <= 0):
                err("storage", f"{where}: front '{f.kind}' needs a positive height / count")
        if sum(f.height or 0 for f in m.fronts) > h + 1e-6:
            err("storage", f"{where}: front heights exceed the piece height {h:.2f} m")
        for fit in m.interior:
            if fit.kind not in FITTING_KINDS:
                err("storage", f"{where}: interior '{fit.kind}' - use one of {', '.join(FITTING_KINDS)}")
            elif fit.kind == "divider" and not 0 < fit.x < m.width:
                err("storage", f"{where}: divider x={fit.x} m is outside the module (0..{m.width:.2f})")
            elif fit.kind != "divider" and not 0 < fit.z < h:
                err("storage", f"{where}: {fit.kind} at z={fit.z} m is outside the piece (0..{h:.2f})")


def validate_variants(apt: Apartment, variants: list[Variant]):  # noqa: C901 - one pass, many rules
    """Issues for all variants (imports Issue lazily to avoid a cycle with validate.py)."""
    from .validate import Issue

    issues: list[Issue] = []
    err = lambda c, m: issues.append(Issue("error", c, m))  # noqa: E731
    warn = lambda c, m: issues.append(Issue("warning", c, m))  # noqa: E731
    rooms = {r.id: r for r in apt.all_rooms()}
    h = apt.levels.ceiling_height
    doors = [(o, z) for o in apt.openings if o.kind == "door" and (z := _door_zone(apt, o))]
    points = apt.fixed_points

    keys = [v.key for v in variants]
    by_key = {v.key: v for v in variants}
    for clash in merge_variant_finishes(apt, variants):
        err("finish", clash)
    for dup in sorted({k for k in keys if keys.count(k) > 1}):
        err("variant_key", f"variant key {dup} is used by more than one file")
    seen: dict[str, str] = {}
    for v in variants:
        src = v.source.name if v.source else v.key
        if not KEY_RE.match(v.key):
            err("variant_key", f"{src}: key '{v.key}' must be 1-4 capitals/digits starting with a letter (A, B, C2...)")
        if v.source and v.source.stem != v.key:
            err("variant_key", f"{src}: file name must be {v.key}.toml")
        if v.style_of and (v.style_of not in by_key or by_key[v.style_of].style_of or v.style_of == v.key):
            err("variant_style", f"{v.key}: style_of = '{v.style_of}' must be the key of another layout variant "
                                 "(not itself a style)")
        if v.wall_color and not COLOR_RE.match(v.wall_color):
            err("furniture_color", f"{v.key}: wall_color '{v.wall_color}' is not #rrggbb")
        for rid, rf in v.rooms.items():
            if rid not in rooms:
                err("finish", f"{v.key}: [rooms.{rid}] - unknown room (use a room id from apartment.toml)")
            for what, name in (("floor", rf.floor), ("walls", rf.walls), ("ceiling", rf.ceiling)):
                if name and name not in apt.finishes:
                    err("finish", f"{v.key}: [rooms.{rid}] {what} = '{name}' is not in [finishes] of apartment.toml")
            if not 0 <= rf.walls_height <= h:
                err("finish", f"{v.key}: [rooms.{rid}] walls_height must be 0 (= ceiling) .. {h}")
            if rf.skirting and (not COLOR_RE.match(rf.skirting) or not 0.03 <= rf.skirting_height <= 0.2):
                err("finish", f"{v.key}: [rooms.{rid}] skirting needs a #rrggbb colour and a height of 0.03-0.2 m")
            for k in ("paint", "floor_color", "walls_color"):
                if getattr(rf, k) and not COLOR_RE.match(getattr(rf, k)):
                    err("finish", f"{v.key}: [rooms.{rid}] {k} '{getattr(rf, k)}' is not #rrggbb")
            if rf.stretch_ceiling and rf.ceiling:
                err("finish", f"{v.key}: [rooms.{rid}] has both ceiling tiles and a stretch ceiling - pick one")
            if rf.stretch_ceiling and not (0.02 <= rf.stretch_drop <= 0.3 and 0.0 <= rf.stretch_gap <= 0.2
                                           and COLOR_RE.match(rf.stretch_color)
                                           and COLOR_RE.match(rf.stretch_led_color)):
                err("finish", f"{v.key}: [rooms.{rid}] stretch ceiling needs drop 0.02-0.3, gap 0-0.2, #rrggbb colours")
        stretch = {rid: h - rf.stretch_drop for rid, rf in v.rooms.items() if rf.stretch_ceiling}
        for b in apt.built_ins:
            if b.room in stretch and b.top > stretch[b.room] + 1e-6:
                warn("stretch_ceiling", f"{v.key}: built-in {b.id} (top {b.top:.2f}) pokes through the stretch "
                                        f"ceiling of {b.room} at {stretch[b.room]:.2f}")
        for it in v.items:
            if not re.match(rf"^{re.escape(v.key)}\.{SLUG}-\d+$", it.id):
                err("furniture_id", f"{it.id}: must look like {v.key}.<type>-<room>-<n> (lowercase, hyphens)")
            if it.id in seen:
                err("furniture_id", f"{it.id}: duplicate id (also in variant {seen[it.id]})")
            seen[it.id] = v.key
            if not SLUG_RE.match(it.type):
                err("furniture_type", f"{it.id}: type '{it.type}' must be lowercase words with hyphens")
            if it.storage is not None and not it.is_storage:
                err("storage", f"{it.id}: [storage] only applies to storage types ({', '.join(sorted(STORAGE_WORDS))})")
            room = rooms.get(it.room)
            if room is None:
                err("furniture_room", f"{it.id}: unknown room '{it.room}' (use a room id from apartment.toml)")
                continue
            if len(it.size) != 3 or min(it.size) <= 0 or len(it.position) != 2:
                err("furniture_size", f"{it.id}: size must be 3 positive numbers, position 2 numbers")
                continue
            if it.elevation < 0 or it.top > h + 1e-6:
                err("furniture_size", f"{it.id}: spans {it.elevation:.2f}-{it.top:.2f} m, outside floor..ceiling {h}")
            if not COLOR_RE.match(it.color):
                err("furniture_color", f"{it.id}: color '{it.color}' is not #rrggbb")
            for k in ("metal", "accent", "apron_color", "cushion"):
                if getattr(it, k) and not COLOR_RE.match(getattr(it, k)):
                    err("furniture_color", f"{it.id}: {k} '{getattr(it, k)}' is not #rrggbb")
            _validate_storage(it, err)
            if it.apron and (_last(it.type) not in ("bathtub", "bath", "backsplash", "wallpaper")
                             or it.apron not in apt.finishes):
                err("finish", f"{it.id}: apron = '{it.apron}' needs a bathtub / backsplash and a finish from [finishes]")
            if it.track is not None and "track" not in it.type.split("-"):
                err("light", f"{it.id}: [track] only applies to track-light pieces")
            if it.track is not None:
                tr = it.track
                if not tr.heads or tr.watts <= 0 or not 5 <= tr.beam <= 120 or not COLOR_RE.match(tr.color):
                    err("light", f"{it.id}: track needs heads, watts > 0, beam 5-120 and a #rrggbb colour")
                if any(abs(hd.x) > it.size[0] / 2 + 1e-6 for hd in tr.heads):
                    err("light", f"{it.id}: a head's x is off the {it.size[0]:.2f} m rail")
                if any(d[2] > -0.05 for _, d in track_heads(it)):
                    warn("light", f"{it.id}: a head aims upwards / horizontally - check its aim point")
            if it.light is not None and not is_light(it.type):
                err("light", f"{it.id}: [light] only applies to light fixtures ({', '.join(sorted(LIGHT_WORDS))})")
            if it.light is not None:
                lt = it.light
                if (lt.kind not in LIGHT_KINDS or lt.aim not in LIGHT_AIMS or lt.watts <= 0 or lt.size <= 0
                        or not 1 <= lt.spot_angle <= 180):
                    err("light", f"{it.id}: light needs kind {'|'.join(LIGHT_KINDS)}, aim {'|'.join(LIGHT_AIMS)}, "
                                 "watts > 0, size > 0, spot_angle 1-180")
                if not COLOR_RE.match(lt.color):
                    err("light", f"{it.id}: light color '{lt.color}' is not #rrggbb")
            expected = rf"^{re.escape(it.type)}-{re.escape(room.slug)}-\d+$"
            if not re.match(expected, it.local_id):
                warn("furniture_id_name", f"{it.id}: name should be {it.type}-{room.slug}-<n> (type/room changed?)")
            fp = offset_convex(it.footprint(), -0.01)
            if it.room in stretch and stretch[it.room] + 1e-6 < it.top < h - 0.011:
                warn("stretch_ceiling", f"{it.id}: top {it.top:.2f} pokes through the stretch ceiling at "
                                        f"{stretch[it.room]:.2f} (ceiling-mounted pieces are lowered automatically)")
            if not polygon_inside(fp, room.polygon):
                warn("furniture_outside", f"{it.id}: footprint leaves room '{it.room}'")
            if it.elevation < 2.0 and it.top > 0.015:  # mats / rugs lie under a door leaf
                for o, zone in doors:
                    if convex_overlap(fp, zone):
                        warn("furniture_door", f"{it.id}: blocks the swing of door {o.id}")
            for b in apt.built_ins:  # the boiler & co. are in every variant - nothing may go through them
                if (b.room == it.room and it.elevation < b.top - 1e-6 and b.elevation < it.top - 1e-6
                        and convex_overlap(fp, offset_convex(b.footprint(), -0.01))):
                    warn("furniture_built_in", f"{it.id}: runs into the built-in {b.id} ({b.label or b.type})")
            # pieces bound to the building's pipes / vents must sit on a matching fixed point
            candidates = [pt for pt in points if serves(pt, it)]
            if candidates and not any(on_point(pt, it) for pt in candidates):
                near = min(candidates, key=lambda pt: point_polygon_distance(pt.position, it.footprint()))
                dist = point_polygon_distance(near.position, it.footprint())
                where = "" if near.room == it.room else f" (it is in {near.room})"
                err("fixed_point", f"{it.id}: a {it.type} must sit on a fixed service point - nearest is "
                                   f"{near.id} '{near.label}', {dist:.2f} m away{where}")
        if v.items:  # an empty (new) variant is not nagged
            for pt in points:
                if not any(serves(pt, it) and on_point(pt, it) for it in v.items):
                    warn("fixed_point_unused", f"{v.key}: nothing on fixed point {pt.id} '{pt.label}' "
                                               f"(expects {' / '.join(pt.serves)} in {pt.room})")
        for i, a in enumerate(v.items):
            for b in v.items[i + 1 :]:
                if FLAT_OR_ON_OTHERS & {_last(a.type), _last(b.type)}:  # on / in others, or paint on the wall
                    continue
                if a.elevation >= b.top - 1e-6 or b.elevation >= a.top - 1e-6:
                    continue  # one sits above the other (wall cabinet over a worktop)
                if any(convex_overlap(offset_convex(pa, -0.01), offset_convex(pb, -0.01))
                       for pa in a.footprint_parts() for pb in b.footprint_parts()):
                    warn("furniture_overlap", f"{a.id} overlaps {b.id}")
    return issues


# --------------------------------------------------------------------------- colour edits (add-on colour picker)
def shift_color(new: str, old: str, old2: str) -> str:
    """``old2`` moved the way ``new`` moved from ``old`` (keeps a finish's second tone / grout contrast)."""
    out = []
    for i in (1, 3, 5):
        a, b, n = (int(h[i:i + 2], 16) for h in (old, old2, new))
        out.append(min(255, max(0, n + b - a)))
    return "#" + "".join(f"{v:02x}" for v in out)


def tinted_finish(f, color: str):
    """Finish ``f`` recoloured to ``color``; second tone and grout keep their offset. Name ``<name>@<hex>``."""
    if not color or color.lower() == f.color.lower():
        return f
    return replace(f, name=f"{f.name}@{color.lstrip('#').lower()}", color=color,
                   color2=shift_color(color, f.color, f.color2), joint_color=shift_color(color, f.color, f.joint_color))


def get_color(v: Variant, path: str) -> str:
    """Colour at ``path``: ``<local id>/<field>`` (color, accent, metal, apron_color, tag_color, handle_color,
    interior_color, front_color:<module index>) or ``rooms.<room id>/<field>`` (paint, floor_color, walls_color)."""
    target, fld = path.rsplit("/", 1)
    if target.startswith("rooms."):
        rf = v.rooms.get(target[6:])
        return getattr(rf, fld) if rf else ""
    it = v.item(target)
    if fld.startswith("front_color:"):
        return it.storage.modules[int(fld.split(":")[1])].front_color if it.storage else ""
    if fld in ("handle_color", "interior_color"):
        return getattr(it.storage, fld) if it.storage else ""
    return getattr(it, fld)


def set_color(v: Variant, path: str, color: str, owner: bool = True) -> None:
    """Set the colour at ``path`` (see ``get_color``) in place; ``owner`` records it in ``owner_colors``."""
    target, fld = path.rsplit("/", 1)
    if target.startswith("rooms."):
        rid = target[6:]
        v.rooms[rid] = replace(v.rooms.get(rid, RoomFinish()), **{fld: color})
        local = path
    else:
        i = next(n for n, it in enumerate(v.items) if target in (it.local_id, it.id))
        it = v.items[i]
        if fld.startswith("front_color:") or fld in ("handle_color", "interior_color"):
            st = it.storage or Storage()
            if fld.startswith("front_color:"):
                k = int(fld.split(":")[1])
                mods = list(st.modules)
                mods[k] = replace(mods[k], front_color=color)
                st = replace(st, modules=type(st.modules)(mods))
            else:
                st = replace(st, **{fld: color})
            v.items[i] = replace(it, storage=st)
        else:
            v.items[i] = replace(it, **{fld: color})
        local = f"{it.local_id}/{fld}"
    if owner and local not in v.owner_colors:
        v.owner_colors.append(local)
