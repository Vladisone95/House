"""Typed model of ``data/apartment.toml``."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = PROJECT_ROOT / "data" / "apartment.toml"

Rect = tuple[float, float, float, float]
Point = tuple[float, float]


@dataclass(frozen=True)
class Site:
    city: str
    latitude: float
    longitude: float
    utc_offset_standard: float
    plus_y_bearing: float


@dataclass(frozen=True)
class Levels:
    ceiling_height: float
    slab_thickness: float
    balcony_floor_z: float
    balcony_above: bool


@dataclass(frozen=True)
class Wall:
    id: str
    type: str
    rect: Rect
    thickness: float

    @property
    def horizontal(self) -> bool:
        """True if the wall runs along X (its long axis is X)."""
        x1, y1, x2, y2 = self.rect
        return (x2 - x1) >= (y2 - y1)

    @property
    def axis_range(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.rect
        return (x1, x2) if self.horizontal else (y1, y2)


@dataclass(frozen=True)
class Opening:
    id: str
    wall: str
    kind: str  # window | door | balcony_door
    span: tuple[float, float]
    sill: float
    head: float
    status: str = "estimated"
    note: str = ""
    hinge: str = ""  # doors: "start" | "end" of the span (start = lower coordinate)
    swing: str = ""  # doors: side the leaf opens to, "+" (towards +X / +Y) | "-"
    fixed: bool = False  # forced by the building (entrance) - shown as fixed on the plans

    @property
    def width(self) -> float:
        return self.span[1] - self.span[0]


@dataclass(frozen=True)
class Camera:
    eye: Point
    look_at: Point


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    name_ro: str
    listed_area: float
    finish: str
    polygon: tuple[Point, ...]
    camera: Camera | None = None
    note: str = ""
    slug: str = ""  # readable room name used in furniture ids, e.g. "master-bathroom"


@dataclass(frozen=True)
class Balcony(Room):
    slab: Rect = (0, 0, 0, 0)
    side_wall: Rect = (0, 0, 0, 0)
    railing_height: float = 1.0


@dataclass(frozen=True)
class Finish:
    """A surface finish (``[finishes.<name>]``): parquet planks, tiles or stone slabs, sizes in metres.

    Rooms use one as their floor; a variant can put others on a room's floor / walls (ADR 0009).
    """

    name: str
    kind: str  # parquet | tiles | stone (soft clouding) | marble (white, thin sharp veins of color2)
    size: tuple[float, float]  # plank length x width, or tile x / y
    color: str  # main colour
    color2: str  # second tone (plank variation / tile speckle)
    joint_color: str
    joint: float = 0.002  # gap / grout width
    direction: str = "x"  # parquet: planks run along x or y
    roughness: float = 0.4
    note: str = ""


@dataclass(frozen=True)
class FixedPoint:
    """A service point the building forces (water/drain, WC stack, washer, hood vent...).

    Every furniture variant must put a piece of a ``serves`` type on it (see furniture.py).
    """

    id: str
    kind: str  # water | wc | washer | hood | shower | bath ... (drives the plan symbol)
    label: str  # short text on the plans, e.g. "SINK", "WC", "MSR"
    room: str
    position: Point
    serves: tuple[str, ...]  # furniture types that must sit on it (full type or last word)
    radius: float = 0.4  # a serving piece's footprint must come within this distance
    status: str = "estimated"
    note: str = ""


@dataclass(frozen=True)
class BuiltIn:
    """Equipment the apartment already has (e.g. the hot-water boiler): in every variant, never moved.

    Same geometry fields as a furniture piece (``type`` picks the shape, see furniture.item_parts).
    """

    id: str
    type: str
    room: str
    size: tuple[float, float, float]  # width, depth, height
    position: Point  # footprint centre
    rotation: float = 0.0  # deg CCW, 0 = front faces +Y
    elevation: float = 0.0  # underside height
    color: str = "#f2f2f2"
    label: str = ""
    status: str = "estimated"
    note: str = ""

    @property
    def top(self) -> float:
        return self.elevation + self.size[2]

    def footprint(self) -> list[Point]:
        from .geometry import rotated_rect

        return rotated_rect(self.position, self.size[0], self.size[1], self.rotation)


@dataclass(frozen=True)
class Building:
    """The block the apartment sits in, as simple context massing (``[building]``)."""

    storeys_below: int = 0  # full storeys between the street and this floor (etaj 6 = parter + 5 = 6)
    floors_above: int = 0
    party_extension: float = 10.0  # how far the block continues past the party / corridor walls (m)
    grass_margin: float = 30.0  # lawn around the block footprint (m); nothing beyond it
    trees: int = 0  # trees scattered on the lawn (deterministic)
    status: str = "estimated"
    note: str = ""


@dataclass(frozen=True)
class OpeningDefaults:
    window_sill: float
    window_head: float
    door_head: float
    frame_depth: float
    frame_width: float
    window_setback_from_outside: float


@dataclass
class Apartment:
    name: str
    listed_usable_area: float
    listed_total_area: float
    area_tolerance: float
    site: Site
    levels: Levels
    wall_types: dict[str, float]
    openings_defaults: OpeningDefaults
    walls: list[Wall]
    openings: list[Opening]
    rooms: list[Room]
    balcony: Balcony | None
    fixed_points: list[FixedPoint] = field(default_factory=list)
    finishes: dict[str, Finish] = field(default_factory=dict)
    built_ins: list[BuiltIn] = field(default_factory=list)
    building: Building | None = None
    start_view: Camera | None = None  # where Blender's 3D view opens (eye + look-at, eye height 1.60 m)
    start_variant: str = ""  # furniture variant shown when the file opens ([start_view] variant)
    source: Path = field(default=DEFAULT_DATA)

    def wall(self, wall_id: str) -> Wall:
        for w in self.walls:
            if w.id == wall_id:
                return w
        raise KeyError(wall_id)

    def openings_in(self, wall_id: str) -> list[Opening]:
        return sorted((o for o in self.openings if o.wall == wall_id), key=lambda o: o.span[0])

    def room(self, room_id: str) -> Room:
        for r in self.all_rooms():
            if r.id == room_id:
                return r
        raise KeyError(room_id)

    def all_rooms(self) -> list[Room]:
        return [*self.rooms, *([self.balcony] if self.balcony else [])]

    def footprint_cells(self) -> list[Rect]:
        """Apartment footprint (walls + rooms, excl. balcony) as non-overlapping grid cells."""
        from .geometry import footprint_cells

        return footprint_cells([w.rect for w in self.walls], [r.polygon for r in self.rooms])


def _camera(d: dict | None) -> Camera | None:
    if not d:
        return None
    return Camera(eye=tuple(d["eye"]), look_at=tuple(d["look_at"]))


def _room_kwargs(d: dict) -> dict:
    return dict(
        id=d["id"],
        name=d["name"],
        name_ro=d.get("name_ro", d["name"]),
        listed_area=float(d["listed_area"]),
        finish=d.get("finish", "default"),
        polygon=tuple(tuple(map(float, p)) for p in d["polygon"]),
        camera=_camera(d.get("camera")),
        note=d.get("note", ""),
        slug=d.get("slug", d["id"].replace("_", "-")),
    )


def parse_finish(name: str, f: dict) -> Finish:
    """One ``[finishes.<name>]`` table (apartment.toml, or a variant's own finishes)."""
    return Finish(
        name=name,
        kind=f["kind"],
        size=tuple(map(float, f["size"])),
        color=f["color"],
        color2=f.get("color2", f["color"]),
        joint_color=f.get("joint_color", "#808080"),
        joint=float(f.get("joint", 0.002)),
        direction=f.get("direction", "x"),
        roughness=float(f.get("roughness", 0.4)),
        note=f.get("note", ""),
    )


def load(path: str | Path | None = None) -> Apartment:
    path = Path(path) if path else DEFAULT_DATA
    with open(path, "rb") as fh:
        raw = tomllib.load(fh)

    wall_types = {k: float(v["thickness"]) for k, v in raw["wall_types"].items()}
    od = raw["openings_defaults"]
    defaults = OpeningDefaults(**{k: float(v) for k, v in od.items()})

    walls = [
        Wall(id=w["id"], type=w["type"], rect=tuple(map(float, w["rect"])), thickness=wall_types[w["type"]])
        for w in raw["walls"]
    ]

    openings = []
    for o in raw.get("openings", []):
        kind = o["kind"]
        if kind == "window":
            sill, head = defaults.window_sill, defaults.window_head
        elif kind == "balcony_door":
            sill, head = 0.0, defaults.window_head
        else:
            sill, head = 0.0, defaults.door_head
        openings.append(
            Opening(
                id=o["id"],
                wall=o["wall"],
                kind=kind,
                span=tuple(map(float, o["span"])),
                sill=float(o.get("sill", sill)),
                head=float(o.get("head", head)),
                status=o.get("status", "estimated"),
                note=o.get("note", ""),
                hinge=o.get("hinge", ""),
                swing=o.get("swing", ""),
                fixed=bool(o.get("fixed", False)),
            )
        )

    rooms = [Room(**_room_kwargs(r)) for r in raw["rooms"]]
    balcony = None
    if b := raw.get("balcony"):
        balcony = Balcony(
            **_room_kwargs(b),
            slab=tuple(map(float, b["slab"])),
            side_wall=tuple(map(float, b["side_wall"])),
            railing_height=float(b.get("railing_height", 1.0)),
        )

    fixed_points = [
        FixedPoint(
            id=f["id"],
            kind=f["kind"],
            label=f.get("label", f["kind"].upper()),
            room=f["room"],
            position=tuple(map(float, f["position"])),
            serves=tuple(f["serves"]),
            radius=float(f.get("radius", 0.4)),
            status=f.get("status", "estimated"),
            note=f.get("note", ""),
        )
        for f in raw.get("fixed_points", [])
    ]

    finishes = {name: parse_finish(name, f) for name, f in raw.get("finishes", {}).items()}

    built_ins = [
        BuiltIn(
            id=b["id"],
            type=b["type"],
            room=b["room"],
            size=tuple(map(float, b["size"])),
            position=tuple(map(float, b["position"])),
            rotation=float(b.get("rotation", 0.0)),
            elevation=float(b.get("elevation", 0.0)),
            color=b.get("color", "#f2f2f2"),
            label=b.get("label", ""),
            status=b.get("status", "estimated"),
            note=b.get("note", ""),
        )
        for b in raw.get("built_ins", [])
    ]

    bd = raw.get("building")
    building = Building(storeys_below=int(bd.get("storeys_below", 0)), floors_above=int(bd.get("floors_above", 0)),
                        party_extension=float(bd.get("party_extension", 10.0)),
                        grass_margin=float(bd.get("grass_margin", 30.0)), trees=int(bd.get("trees", 0)),
                        status=bd.get("status", "estimated"),
                        note=bd.get("note", "")) if bd else None

    p = raw["project"]
    s = raw["site"]
    lv = raw["levels"]
    return Apartment(
        name=p["name"],
        listed_usable_area=float(p["listed_usable_area"]),
        listed_total_area=float(p["listed_total_area"]),
        area_tolerance=float(p.get("area_tolerance", 0.03)),
        site=Site(
            city=s["city"],
            latitude=float(s["latitude"]),
            longitude=float(s["longitude"]),
            utc_offset_standard=float(s["utc_offset_standard"]),
            plus_y_bearing=float(s["plus_y_bearing"]),
        ),
        levels=Levels(
            ceiling_height=float(lv["ceiling_height"]),
            slab_thickness=float(lv["slab_thickness"]),
            balcony_floor_z=float(lv.get("balcony_floor_z", 0.0)),
            balcony_above=bool(lv.get("balcony_above", False)),
        ),
        wall_types=wall_types,
        openings_defaults=defaults,
        walls=walls,
        openings=openings,
        rooms=rooms,
        balcony=balcony,
        fixed_points=fixed_points,
        finishes=finishes,
        built_ins=built_ins,
        building=building,
        start_view=_camera(raw.get("start_view")),
        start_variant=raw.get("start_view", {}).get("variant", ""),
        source=path,
    )
