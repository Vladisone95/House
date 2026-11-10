"""What the owner pays on top of the developer's turnkey delivery, for one variant (ADR 0011).

The apartment comes turnkey: tiles, parquet, doors, paint, sanitary ware, installations are the
developer's (``[turnkey]`` in ``data/prices.toml``). A surface the variant keeps as delivered costs
nothing; a surface it changes costs (material - developer allowance) per m2 when the developer lays it,
full price otherwise. Pieces the developer supplies (bathtub, WC, basin, 1 AC...) become credits
against the variant's chosen pieces, so a better shower costs only the difference. Furniture is never
included. Quantities come from the plan and the variant; prices are [low, mid, high] RON incl. VAT.
"""

from __future__ import annotations

import html
import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .furniture import Item, RoomFinish, Variant
from .geometry import point_in_polygon, polygon_area, walled_edges
from .model import PROJECT_ROOT, Apartment, Room

DEFAULT_PRICES = PROJECT_ROOT / "data" / "prices.toml"
TIERS = ("low", "mid", "high")
CATEGORIES = {  # order on the page
    "kitchen": "Kitchen furniture",
    "storage": "Storage & carpentry",
    "furniture": "Furniture",
    "appliances": "Appliances & climate",
    "bathroom": "Bathroom sanitary ware",
    "lighting": "Lighting",
    "textiles": "Curtains, rugs & textiles",
    "decor": "Decor & plants",
}
UNIT_TEXT = {"pc": "pc", "m": "m", "m2": "m²", "m2_floor": "m²", "lump": "lump"}
TILE_KINDS = {"tiles", "stone", "marble"}
ZERO = (0.0, 0.0, 0.0)

Triple = tuple[float, float, float]


def _t(v) -> Triple:
    """A number or a [low, mid, high] list -> triple."""
    return tuple(float(x) for x in v) if isinstance(v, list | tuple) else (float(v),) * 3


@dataclass(frozen=True)
class Price:
    label: str
    price: Triple
    unit: str = "pc"
    category: str = ""
    status: str = "estimated"
    key: str = ""
    material: Triple = ZERO  # finishes: material (incl. adhesive / accessories) per m2
    labour: Triple = ZERO  # finishes: laying per m2
    allowance: float = 0.0  # developer's budget per unit (fit-out works, e.g. interior doors)


@dataclass(frozen=True)
class Allowance:
    """A surface the developer finishes: we pay (material - allowance) per m2, laying included."""

    label: str
    surface: str  # floor | walls
    rooms: tuple[str, ...]
    allowance: float


@dataclass(frozen=True)
class Supplied:
    """Pieces the developer supplies: a credit of up to ``amount x pieces`` per room (or per apartment)."""

    label: str
    types: tuple[str, ...]
    amount: Triple
    rooms: tuple[str, ...] = ()
    pieces: int = 1


@dataclass
class Catalogue:
    eur_rate: float
    waste: float
    contingency: float
    as_of: str
    finishes: dict[str, Price]
    fitout: dict[str, Price]
    items: dict[str, Price]
    included: list[str] = field(default_factory=list)
    surfaces: list[Allowance] = field(default_factory=list)
    supplied: list[Supplied] = field(default_factory=list)
    standard_tile_max: float = 0.60
    turnkey_note: str = ""

    def item_price(self, type_: str) -> Price | None:
        """Whole type first, then without its leading words: plush-corner-sofa -> corner-sofa -> sofa."""
        words = type_.split("-")
        for i in range(len(words)):
            if p := self.items.get("-".join(words[i:])):
                return p
        return None

    def surface_allowance(self, room_id: str, surface: str) -> Allowance | None:
        return next((a for a in self.surfaces if a.surface == surface and room_id in a.rooms), None)


def _price(key: str, d: dict, unit: str = "pc") -> Price:
    material, labour = _t(d.get("material", 0)), _t(d.get("labour", 0))
    price = _t(d["price"]) if "price" in d else tuple(m + lab for m, lab in zip(material, labour, strict=True))
    return Price(label=d["label"], price=price, unit=d.get("unit", unit), category=d.get("category", ""),
                 status=d.get("status", "estimated"), key=key, material=material, labour=labour,
                 allowance=float(d.get("allowance", 0.0)))


def load_prices(path: str | Path | None = None) -> Catalogue:
    with open(Path(path) if path else DEFAULT_PRICES, "rb") as fh:
        raw = tomllib.load(fh)
    m, tk = raw["meta"], raw.get("turnkey", {})
    return Catalogue(
        eur_rate=float(m["eur_rate"]),
        waste=float(m.get("waste", 0.0)),
        contingency=float(m.get("contingency", 0.0)),
        as_of=m.get("as_of", ""),
        finishes={k: _price(k, v, "m2") for k, v in raw.get("finish", {}).items()},
        fitout={k: _price(k, v) for k, v in raw.get("fitout", {}).items()},
        items={k: _price(k, v) for k, v in raw.get("items", {}).items()},
        included=list(tk.get("included", [])),
        surfaces=[Allowance(s["label"], s["surface"], tuple(s["rooms"]), float(s["allowance"]))
                  for s in tk.get("surface", [])],
        supplied=[Supplied(s["label"], tuple(s["types"]), _t(s["amount"]), tuple(s.get("rooms", ())),
                           int(s.get("pieces", 1))) for s in tk.get("piece", [])],
        standard_tile_max=float(tk.get("standard_tile_max", 0.60)),
        turnkey_note=tk.get("note", ""),
    )


@dataclass
class Line:
    label: str
    qty: float
    unit: str
    unit_price: Triple
    detail: str = ""
    status: str = "estimated"

    @property
    def total(self) -> Triple:
        return tuple(self.qty * p for p in self.unit_price)


@dataclass
class Section:
    title: str
    lines: list[Line] = field(default_factory=list)

    @property
    def total(self) -> Triple:
        return _sum(ln.total for ln in self.lines)


@dataclass
class Estimate:
    variant: Variant
    catalogue: Catalogue
    fitout: list[Section]
    furniture: list[Section]
    unpriced: list[str]
    personal: list[str]
    unused: list[str]  # developer-supplied pieces the variant does not use (no credit)

    @property
    def fitout_total(self) -> Triple:
        return _sum(s.total for s in self.fitout)

    @property
    def furniture_total(self) -> Triple:
        return _sum(s.total for s in self.furniture)

    @property
    def total(self) -> Triple:
        return _sum((self.fitout_total, self.furniture_total))


def _sum(triples) -> Triple:
    out = [0.0, 0.0, 0.0]
    for t in triples:
        for i in range(3):
            out[i] += t[i]
    return tuple(out)


# --------------------------------------------------------------------------- quantities
def _edges(poly):
    return list(zip(poly, [*poly[1:], poly[0]], strict=True))


def _perimeter(room: Room, walls: list | None = None) -> float:
    """Room perimeter; with ``walls``, only the edges that have a wall (the hall is open to the living)."""
    edges = _edges(room.polygon)
    walled = walled_edges(room.polygon, walls) if walls is not None else [True] * len(edges)
    return sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for (a, b), w in zip(edges, walled, strict=True) if w)


def _opening_rooms(apt: Apartment) -> dict[str, list[str]]:
    """Rooms each opening opens into: probe 5 cm beyond both faces of its wall at the opening's middle."""
    out = {}
    for o in apt.openings:
        x1, y1, x2, y2 = apt.wall(o.wall).rect
        mid = sum(o.span) / 2
        probes = ([(mid, y1 - 0.05), (mid, y2 + 0.05)] if apt.wall(o.wall).horizontal
                  else [(x1 - 0.05, mid), (x2 + 0.05, mid)])
        out[o.id] = [r.id for r in apt.rooms for p in probes if point_in_polygon(p, r.polygon)]
    return out


def _wall_area(apt: Apartment, room: Room, opening_rooms: dict[str, list[str]]) -> float:
    """Net wall area of a room: walled perimeter x height minus its windows and doors."""
    gross = _perimeter(room, [w.rect for w in apt.walls]) * apt.levels.ceiling_height
    holes = sum(o.width * (o.head - o.sill) for o in apt.openings if room.id in opening_rooms[o.id])
    return max(gross - holes, 0.0)


def _pretty(name: str) -> str:
    return name.replace("_", " ").capitalize()


def _finish_price(cat: Catalogue, apt: Apartment, name: str) -> Price:
    f = apt.finishes.get(name)
    p = cat.finishes.get(name) or (cat.finishes.get(f.kind) if f else None)
    if p is None:
        raise KeyError(f"no price for finish {name!r} (kind {f.kind if f else '?'}) in prices.toml")
    return p


def _surface_line(cat: Catalogue, apt: Apartment, room: Room, surface: str, finish: str,
                  area: float) -> tuple[Line, float]:
    """Line for a surface the variant changes + m2 that need the large-format laying surcharge."""
    p = _finish_price(cat, apt, finish)
    what = f"{room.name}{' walls' if surface == 'walls' else ''}: {_pretty(finish)}"
    qty = area * (1 + cat.waste)
    base = f"{area:.1f} m² + {cat.waste:.0%} cuts · {p.label}"
    a = cat.surface_allowance(room.id, surface)
    if a is None:
        return Line(what, qty, "m2", p.price, f"{base} · supply + laying (not in the turnkey delivery)",
                    p.status), 0.0
    unit = tuple(max(0.0, m - a.allowance) for m in p.material)
    f = apt.finishes.get(finish)
    big = f is not None and f.kind in TILE_KINDS and max(f.size) > cat.standard_tile_max + 1e-6
    return Line(f"{what} (upgrade)", qty, "m2", unit,
                f"{base} · material over the developer's {a.label} budget of {a.allowance:g} lei/m², "
                f"laying included", p.status), area if big else 0.0


def _fit(cat: Catalogue, key: str, qty: float, detail: str = "", label: str = "") -> Line:
    p = cat.fitout[key]
    unit = tuple(max(0.0, v - p.allowance) for v in p.price)
    return Line(label or p.label, qty, p.unit, unit, detail, p.status)


def fitout_sections(apt: Apartment, variant: Variant, cat: Catalogue) -> list[Section]:
    """Only what the variant changes or adds: a surface it leaves as delivered costs nothing."""
    opening_rooms = _opening_rooms(apt)
    floors, walls, ceilings = Section("Floors"), Section("Wall coverings"), Section("Ceilings")
    large = 0.0
    for room in apt.all_rooms():
        rf = variant.rooms.get(room.id, RoomFinish())
        area = abs(polygon_area(room.polygon))
        if rf.floor and rf.floor != room.finish:
            line, big = _surface_line(cat, apt, room, "floor", rf.floor, area)
            floors.lines.append(line)
            large += big
        if room is apt.balcony:
            continue
        if rf.walls:
            h = apt.levels.ceiling_height
            tiled = _wall_area(apt, room, opening_rooms) * (min(rf.walls_height, h) / h if rf.walls_height else 1.0)
            line, big = _surface_line(cat, apt, room, "walls", rf.walls, tiled)
            walls.lines.append(line)
            large += big
        if rf.ceiling:
            p = _finish_price(cat, apt, rf.ceiling)
            ceilings.lines.append(Line(f"{room.name} ceiling: {_pretty(rf.ceiling)}", area * (1 + cat.waste),
                                       "m2", p.price, p.label, p.status))
        elif rf.stretch_ceiling:
            ceilings.lines.append(_fit(cat, "stretch_ceiling", area, label=f"{room.name}: stretch ceiling"))
            ceilings.lines.append(_fit(cat, "stretch_led", _perimeter(room),
                                       label=f"{room.name}: stretch ceiling LED gap"))
    if large:
        floors.lines.append(_fit(cat, "large_format", large, "the developer lays 25x30 ... 60x60 as standard"))
    doors = [o for o in apt.openings if o.kind == "door" and not o.fixed]
    p = cat.fitout["interior_door"]
    other = Section("Doors & site", lines=[
        _fit(cat, "interior_door", len(doors), f"{', '.join(o.id for o in doors)} · price minus the "
             f"developer's {p.allowance:g} lei door budget (low = keep the developer's door)"),
        _fit(cat, "site", 1),
    ])
    sections = [s for s in (floors, walls, ceilings, other) if s.lines]
    works = _sum(s.total for s in sections)
    sections.append(Section("Contingency", lines=[
        Line(f"Reserve {cat.contingency:.0%} of the extra works", 1, "lump",
             tuple(cat.contingency * t for t in works), "surprises, small extras, price changes")]))
    return sections


def _qty(unit: str, size: tuple[float, float, float]) -> float:
    w, d, h = size
    return {"m": w, "m2": w * h, "m2_floor": w * d}.get(unit, 1.0)


def _credits(variant: Variant, cat: Catalogue, priced: list[tuple[Item, Price]],
             rooms: dict[str, str]) -> tuple[list[tuple[str, Line]], list[str]]:
    """(category, credit line) for every developer-supplied piece the variant uses + unused ones."""
    out, unused = [], []
    for s in cat.supplied:
        for room in s.rooms or ("",):
            match = [(it, p) for it, p in priced if p.key in s.types and (not room or it.room == room)]
            where = f" ({rooms.get(room, room)})" if room else ""
            if not match:
                unused.append(f"{s.label}{where}")
                continue
            value = _sum(tuple(_qty(p.unit, it.size) * v for v in p.price) for it, p in match)
            cap = tuple(a * s.pieces for a in s.amount)
            credit = tuple(-min(v, c) for v, c in zip(value, cap, strict=True))
            ids = ", ".join(it.id.split(".", 1)[1] for it, _ in match)
            out.append((match[0][1].category, Line(
                f"Included by the developer: {s.label}{where}", 1, "lump", credit,
                f"turnkey budget {_money(cap)} lei, deducted from {ids}", "confirmed")))
    return out, unused


def _money(t: Triple) -> str:
    return _ron(t[0]) if t[0] == t[1] == t[2] else " / ".join(_ron(v) for v in t)


def furniture_sections(apt: Apartment, variant: Variant, cat: Catalogue
                       ) -> tuple[list[Section], list[str], list[str], list[str]]:
    groups: dict[tuple[str, str], list] = {}
    priced, unpriced, personal = [], [], []
    for it in variant.items:
        p = cat.item_price(it.type)
        if p is None:
            unpriced.append(f"{it.id} ({it.type})")
        elif p.category == "personal":
            personal.append(it.id)
        else:
            priced.append((it, p))
            groups.setdefault((p.category, p.label), []).append((it, p))
    sections = {k: Section(v) for k, v in CATEGORIES.items()}
    for (category, label), pieces in groups.items():
        p = pieces[0][1]
        qty = sum(_qty(p.unit, it.size) for it, _ in pieces)
        unit_txt = "" if p.unit == "pc" else f" · {qty:.2f} {UNIT_TEXT[p.unit]}"
        detail = f"{len(pieces)} pc{unit_txt}: " + ", ".join(it.id.split(".", 1)[1] for it, _ in pieces)
        sections.setdefault(category, Section(category.title())).lines.append(
            Line(label, qty, p.unit, p.price, detail, p.status))
    credits, unused = _credits(variant, cat, priced, {r.id: r.name for r in apt.all_rooms()})
    for category, line in credits:
        sections[category].lines.append(line)
    for s in sections.values():
        s.lines.sort(key=lambda ln: -ln.total[1])
    return [s for s in sections.values() if s.lines], unpriced, personal, unused


def estimate(apt: Apartment, variant: Variant, cat: Catalogue | None = None) -> Estimate:
    cat = cat or load_prices()
    from .furniture import merge_variant_finishes

    merge_variant_finishes(apt, [variant])  # the variant's own [finishes.<key>_...] are priced by their kind
    furniture, unpriced, personal, unused = furniture_sections(apt, variant, cat)
    return Estimate(variant, cat, fitout_sections(apt, variant, cat), furniture, unpriced, personal, unused)


# --------------------------------------------------------------------------- HTML page
def _ron(v: float) -> str:
    return f"{round(v):,}".replace(",", " ").replace("-", "−")


def _eur(v: float, rate: float) -> str:
    return "€ " + f"{round(v / rate / 100) * 100:,}".replace(",", " ")


def _rows(section: Section) -> str:
    rows = []
    for ln in section.lines:
        unit = UNIT_TEXT.get(ln.unit, ln.unit)
        qty = "" if ln.unit == "lump" else f"{ln.qty:.2f}".rstrip("0").rstrip(".") + f" {unit}"
        each = "" if ln.unit == "lump" else " / ".join(_ron(p) for p in ln.unit_price)
        tag = ' <span class="tag">quote</span>' if ln.status == "quoted" else ""
        cls = ' class="credit"' if ln.total[1] < 0 else ""
        rows.append(
            f'<tr{cls}><td><div class="lbl">{html.escape(ln.label)}{tag}</div>'
            f'<div class="det">{html.escape(ln.detail)}</div></td>'
            f'<td class="num">{qty}</td><td class="num each">{each}</td>'
            + "".join(f'<td class="num t{i}">{_ron(t)}</td>' for i, t in enumerate(ln.total)) + "</tr>")
    return "\n".join(rows)


def _section_html(s: Section) -> str:
    tot = "".join(f'<td class="num t{i}">{_ron(t)}</td>' for i, t in enumerate(s.total))
    return (f'<tbody class="sec"><tr class="sh"><th colspan="3">{html.escape(s.title)}</th>{tot}</tr>'
            f"{_rows(s)}</tbody>")


def _group_html(title: str, sections: list[Section], total: Triple, rate: float) -> str:
    head = ('<thead><tr><th>Item</th><th class="num">Qty</th><th class="num">Unit price<br>'
            'low / mid / high</th><th class="num">Low</th><th class="num">Mid</th>'
            '<th class="num">High</th></tr></thead>')
    foot = ("<tfoot><tr><th colspan=3>" + html.escape(title) + " total</th>"
            + "".join(f'<td class="num t{i}">{_ron(t)}<div class="eur">{_eur(t, rate)}</div></td>'
                      for i, t in enumerate(total)) + "</tr></tfoot>")
    body = "".join(_section_html(s) for s in sections)
    return f'<h2>{html.escape(title)}</h2><div class="wrap"><table>{head}{body}{foot}</table></div>'


CSS = """
:root{--bg:#f7f5f1;--card:#fff;--ink:#22201c;--mute:#78726a;--line:#e6e1d8;--accent:#8a5a3b;--sec:#f1ece4;
--ok:#2f7d4f}
@media (prefers-color-scheme:dark){:root{--bg:#1b1a18;--card:#252320;--ink:#ece8e1;--mute:#a39c92;
--line:#3a3631;--accent:#d29a72;--sec:#2e2b27;--ok:#7cc79a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.45 "Segoe UI",system-ui,sans-serif}main{max-width:1100px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 10px}.sub{color:var(--mute)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:22px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card .k{color:var(--mute);font-size:13px}.card .v{font-size:24px;font-weight:600;margin-top:2px}
.card.mid{border-color:var(--accent)}.card .e{color:var(--mute)}
.wrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%;min-width:760px}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
thead th{font-size:12px;color:var(--mute);font-weight:600;text-transform:uppercase;letter-spacing:.03em}
.num{text-align:right;white-space:nowrap}.each{color:var(--mute);font-size:13px}
.t1{font-weight:600}.sh th,.sh td{background:var(--sec);font-weight:600}
.credit td{color:var(--ok)}.credit .det{color:var(--ok);opacity:.8}
.det{color:var(--mute);font-size:12.5px}.eur{color:var(--mute);font-size:12px;font-weight:400}
tfoot th,tfoot td{font-size:16px;border-bottom:none}
.tag{background:var(--accent);color:#fff;border-radius:4px;font-size:11px;padding:1px 5px;margin-left:4px}
.note{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 18px 12px 34px;
color:var(--mute);font-size:14px}.note li{margin:3px 0}.warn{border-color:#c0392b;color:inherit}
@media print{body{background:#fff}.wrap,.card,.note{border-color:#ccc}}
"""


def render_html(est: Estimate, apt: Apartment) -> str:
    cat, v = est.catalogue, est.variant
    rate = cat.eur_rate
    cards = "".join(
        f'<div class="card {t}"><div class="k">{t.title()}</div><div class="v">{_ron(x)} lei</div>'
        f'<div class="e">{_eur(x, rate)}</div></div>' for t, x in zip(TIERS, est.total, strict=True))
    usable = sum(abs(polygon_area(r.polygon)) for r in apt.rooms)
    included = "".join(f"<li>{html.escape(x)}</li>" for x in cat.included)
    notes = []
    if cat.turnkey_note:
        notes.append(f"<li>{html.escape(cat.turnkey_note)}</li>")
    if est.unused:
        notes.append(f"<li><b>Developer pieces this variant does not use</b> (no credit): "
                     f"{html.escape('; '.join(est.unused))}.</li>")
    if est.personal:
        notes.append(f"<li><b>Your own things, not counted:</b> {len(est.personal)} props "
                     f"(tableware, PC, shoes...).</li>")
    warn = ""
    if est.unpriced:
        warn = (f'<div class="note warn"><b>Not priced yet ({len(est.unpriced)}):</b> '
                f"{html.escape(', '.join(est.unpriced))} - add these types to data/prices.toml.</div>")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Price list {html.escape(v.key)}</title><style>{CSS}</style></head><body><main>
<h1>Price list - variant {html.escape(v.key)}: {html.escape(v.name)}</h1>
<div class="sub">{html.escape(apt.name)} · {usable:.1f} m² usable · what you pay <b>on top of the turnkey
delivery</b> · Bucharest prices {html.escape(cat.as_of)} · lei incl. VAT · 1 EUR = {rate:.2f} lei ·
generated {date.today():%d %b %Y}</div>
<div class="cards">{cards}</div>
{warn}
{_group_html("Upgrades & extra works", est.fitout, est.fitout_total, rate)}
{_group_html("Furniture, appliances, sanitary & lighting", est.furniture, est.furniture_total, rate)}
<h2>Already in the turnkey delivery (not counted)</h2><ul class="note">{included}</ul>
<h2>How to read this</h2><ul class="note">
<li><b>Low</b> = DIY-store / IKEA ranges, melamine carpentry · <b>Mid</b> = typical Bucharest workshop,
painted MDF, mid brands · <b>High</b> = premium custom carpentry and brands.</li>
<li>Surfaces the variant keeps as delivered cost nothing. Changed tiles / parquet cost only the material
above the developer's budget per m² (the developer still lays them); green lines are developer-supplied
pieces deducted from what you choose, so a better shower or basin costs only the difference.</li>
<li>Quantities are measured from the 3D model; unit prices are <b>estimates</b>, not quotes - replace
them in data/prices.toml with real offers (marked <span class="tag">quote</span>).</li>
{"".join(notes)}
<li>Not included: design fees, moving, the notary / bank costs of the purchase.</li></ul>
</main></body></html>"""


def write_price_list(apt: Apartment, variant: Variant, out: Path, cat: Catalogue | None = None) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(estimate(apt, variant, cat), apt), encoding="utf-8")
    return out
