"""Dimensioned 2D floor plan (PNG) generated from the model. Requires Pillow (not available in Blender)."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .furniture import Variant, modules_of
from .geometry import door_swing, polygon_area, polygon_centroid
from .model import Apartment
from .validate import room_areas

FILL = {"wood": "#f1e2c4", "tiles": "#e3eef0", "outdoor_tiles": "#e4e4e4", "default": "#eeeeee"}
WALL = {"exterior": "#2b2b2b", "party": "#555555", "corridor": "#555555", "partition": "#3a3a3a"}
COLORS = {"window": "#1e88e5", "balcony_door": "#1e88e5", "door": "#e53935", "fixed_door": "#8e0000"}
# fixed service points (pipes, drains, vents) - one colour per kind
POINT_COLORS = {"water": "#0277bd", "wc": "#6d4c41", "washer": "#00897b", "hood": "#ef6c00", "shower": "#0097a7"}


def _font(size: int, bold: bool = False):
    for name in ("arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _rgb(hex_color: str, lighten: float = 0.0) -> tuple[int, int, int]:
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return tuple(round(c + (255 - c) * lighten) for c in (r, g, b))


def _local_to_world(it, x: float, y: float) -> tuple[float, float]:
    a = math.radians(it.rotation)
    return (it.position[0] + x * math.cos(a) - y * math.sin(a), it.position[1] + x * math.sin(a) + y * math.cos(a))


def _draw_furniture(dr: ImageDraw.ImageDraw, p, variant: Variant, font) -> None:
    """Footprints (front edge thicker) + local id on each piece; floor pieces first, wall pieces on top."""
    for it in sorted(variant.items, key=lambda i: (i.elevation, -i.size[0] * i.size[1])):
        fp = [p(*q) for q in it.footprint()]
        dr.polygon(fp, fill=_rgb(it.color, 0.45), outline="#555555", width=2)
        dr.line([fp[2], fp[3]], fill="#222222", width=4)  # front edge (local +Y side)
        if it.is_storage:  # module divisions, numbered from the viewer's left (local +x)
            w, d = it.size[0], it.size[1]
            x = w / 2
            for k, m in enumerate(modules_of(it), start=1):
                xa = x - m.width * w / sum(mm.width for mm in modules_of(it))
                if xa > -w / 2 + 1e-6:
                    dr.line([p(*_local_to_world(it, xa, -d / 2)), p(*_local_to_world(it, xa, d / 2))], fill="#555555", width=1)
                if len(modules_of(it)) > 1 and m.width >= 0.3:
                    dr.text(p(*_local_to_world(it, (x + xa) / 2, d / 2 - 0.1)), f"m{k}", font=font, fill="#555555", anchor="mm")
                x = xa
    for it in variant.items:
        cx, cy = p(*it.position)
        box = dr.textbbox((cx, cy), it.local_id, font=font, anchor="mm")
        dr.rectangle([box[0] - 3, box[1] - 2, box[2] + 3, box[3] + 2], fill="white", outline="#555555")
        dr.text((cx, cy), it.local_id, font=font, fill="black", anchor="mm")


def render_plan(apt: Apartment, out: Path, px_per_m: int = 80, sun=None, variant: Variant | None = None) -> Path:
    """Draw the plan. ``sun`` = optional SunPosition; ``variant`` = draw its furniture with ids."""
    xs = [v for w in apt.walls for v in (w.rect[0], w.rect[2])] + [p[0] for r in apt.all_rooms() for p in r.polygon]
    ys = [v for w in apt.walls for v in (w.rect[1], w.rect[3])] + [p[1] for r in apt.all_rooms() for p in r.polygon]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    margin_l, margin_r, margin_t, margin_b = 120, 380 if variant is None else 640, 130, 110
    W = int((maxx - minx) * px_per_m) + margin_l + margin_r
    H = int((maxy - miny) * px_per_m) + margin_t + margin_b

    def p(x: float, y: float) -> tuple[float, float]:
        return margin_l + (x - minx) * px_per_m, margin_t + (maxy - y) * px_per_m

    im = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(im)
    f, fb, ft = _font(14), _font(15, True), _font(22, True)

    areas = room_areas(apt)
    for r in apt.all_rooms():
        dr.polygon([p(*q) for q in r.polygon], fill=FILL.get(r.finish, FILL["default"]))
    if apt.balcony:
        b = apt.balcony.side_wall
        dr.rectangle([p(b[0], b[3]), p(b[2], b[1])], fill=WALL["exterior"])
        x1, y1, x2, y2 = apt.balcony.slab
        dr.line([p(x1, y1), p(x1, apt.balcony.side_wall[1])], fill="#777", width=3)
        dr.line([p(x1, y1), p(x2, y1)], fill="#777", width=3)
    for w in apt.walls:
        x1, y1, x2, y2 = w.rect
        dr.rectangle([p(x1, y2), p(x2, y1)], fill=WALL.get(w.type, "#333"))

    for o in apt.openings:
        w = apt.wall(o.wall)
        x1, y1, x2, y2 = w.rect
        c = COLORS["fixed_door"] if o.fixed else COLORS[o.kind]
        if w.horizontal:
            dr.rectangle([p(o.span[0], y2), p(o.span[1], y1)], fill="white")
            ym = (y1 + y2) / 2
            dr.line([p(o.span[0], ym), p(o.span[1], ym)], fill=c, width=5 if o.kind != "door" else 3)
        else:
            dr.rectangle([p(x1, o.span[1]), p(x2, o.span[0])], fill="white")
            xm = (x1 + x2) / 2
            dr.line([p(xm, o.span[0]), p(xm, o.span[1])], fill=c, width=5 if o.kind != "door" else 3)
        if o.kind == "door" and o.hinge:
            leaf, arc = door_swing(w.rect, w.horizontal, o.span, o.hinge, o.swing)
            dr.line([p(*q) for q in arc], fill=c, width=2)
            dr.line([p(*q) for q in leaf], fill=c, width=5 if o.fixed else 4)
        if o.fixed:
            mx, my = (o.span[0] + o.span[1]) / 2, (y1 + y2) / 2 if w.horizontal else (x1 + x2) / 2
            pos = p(mx, my - 0.45) if w.horizontal else p(my + 0.45, mx)
            dr.text(pos, "ENTRANCE (fixed)", font=_font(13, True), fill=c, anchor="mm")
        label = f"{o.id.split('_')[0]} {o.width:.2f}"
        if o.kind != "door":
            if w.horizontal:
                dr.text(p((o.span[0] + o.span[1]) / 2, y2 + 0.25), label, font=f, fill=c, anchor="mm")
            else:
                dr.text(p(x1 - 0.12, (o.span[0] + o.span[1]) / 2), label, font=f, fill=c, anchor="rm")

    for r in apt.all_rooms():
        cx, cy = polygon_centroid(r.polygon)
        if variant is not None:  # furniture plan: room names only, the ids are the content
            dr.text(p(cx, cy + 0.25), r.name.upper(), font=fb, fill="#9a9a9a", anchor="mm")
            continue
        a = areas[r.id]
        ok = abs(a - r.listed_area) / r.listed_area <= apt.area_tolerance
        dr.text(p(cx, cy + 0.25), r.name.upper(), font=fb, fill="black", anchor="mm")
        dr.text(p(cx, cy), f"{a:.2f} m2", font=f, fill="#1a7f37" if ok else "#c62828", anchor="mm")
        dr.text(p(cx, cy - 0.25), f"(listed {r.listed_area:.2f})", font=f, fill="#666", anchor="mm")
        if len(r.polygon) == 4:
            rx = [q[0] for q in r.polygon]
            ry = [q[1] for q in r.polygon]
            dr.text(p(cx, cy - 0.5), f"{max(rx) - min(rx):.2f} x {max(ry) - min(ry):.2f} m", font=f, fill="#333", anchor="mm")

    if variant is not None:
        _draw_furniture(dr, p, variant, _font(12))
    _draw_built_ins(dr, p, apt)
    _draw_fixed_points(dr, p, apt, px_per_m)

    # overall dimensions
    dr.line([p(minx, miny - 0.6), p(maxx, miny - 0.6)], fill="#333", width=1)
    dr.text(p((minx + maxx) / 2, miny - 0.85), f"{maxx - minx:.2f} m (incl. balcony)", font=f, fill="#333", anchor="mm")

    # north arrow - +Y points to bearing plus_y_bearing, so north is at -plus_y_bearing on screen
    cx, cy = W - 110, 90
    ang = math.radians(-apt.site.plus_y_bearing)
    dx, dy = math.sin(ang), -math.cos(ang)
    dr.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline="black", width=2)
    dr.line([(cx - dx * 32, cy - dy * 32), (cx + dx * 32, cy + dy * 32)], fill="black", width=3)
    dr.polygon([(cx + dx * 40, cy + dy * 40), (cx + dx * 18 - dy * 9, cy + dy * 18 + dx * 9), (cx + dx * 18 + dy * 9, cy + dy * 18 - dx * 9)], fill="black")
    dr.text((cx + dx * 56, cy + dy * 56), "N", font=ft, fill="black", anchor="mm")

    if sun is not None:
        sang = math.radians(sun.azimuth - apt.site.plus_y_bearing)
        sx, sy = math.sin(sang), -math.cos(sang)
        mx, my = p((minx + maxx) / 2, (miny + maxy) / 2)
        dr.line([(mx + sx * 330, my + sy * 330), (mx + sx * 150, my + sy * 150)], fill="#f9a825", width=6)
        dr.ellipse([mx + sx * 350 - 16, my + sy * 350 - 16, mx + sx * 350 + 16, my + sy * 350 + 16], fill="#fbc02d")
        local = sun.utc.replace(tzinfo=None) + __import__("datetime").timedelta(hours=sun.utc_offset)
        dr.text((W - 360, 170), f"Sun {local:%Y-%m-%d %H:%M}  az {sun.azimuth:.0f} / el {sun.elevation:.0f} deg", font=f, fill="#f57f17")

    usable = sum(areas[r.id] for r in apt.rooms)
    lx, ly = W - margin_r + 20, 210
    if variant is not None:
        dr.text((lx, ly - 40), f"Variant {variant.key} - {variant.name}", font=ft, fill="black")
        lines = [(f"{len(variant.items)} pieces - say e.g. \"move {variant.key}.<id> 30 cm left\"", f, "#333"),
                 ("thick dark edge = front of the piece; m1, m2 = storage modules", f, "#333"),
                 ("dots = fixed service points (sink, WC, MSR, hood)", f, "#333"), ("", f, "#333")]
        small = _font(12)
        lines += [(f"{it.id}   ({it.type}, {it.size[0]:.2f} x {it.size[1]:.2f} m)", small, "#222222")
                  for it in sorted(variant.items, key=lambda i: i.id)]
        if not variant.items:
            lines.append(("(no furniture yet)", f, "#999"))
        for text, fo, c in lines:
            dr.text((lx, ly), text, font=fo, fill=c)
            ly += 20 if fo is f else 17
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out)
        return out
    legend = [
        (apt.name, fb, "black"),
        (f"Usable {usable:.2f} m2 (listed {apt.listed_usable_area})", f, "#333"),
        (f"Ceiling {apt.levels.ceiling_height:.2f} m", f, "#333"),
        ("", f, "#333"),
        ("blue  = window / balcony door", f, COLORS["window"]),
        ("red    = door between rooms (leaf + swing)", f, COLORS["door"]),
        ("dark red = entrance door (fixed by the building)", f, COLORS["fixed_door"]),
        ("dots = fixed service points (pipes, drains, vents)", f, "#333"),
        ("green area = within tolerance of listing", f, "#1a7f37"),
        ("", f, "#333"),
    ] + [(f"{k}: {v:.3f} m", f, "#333") for k, v in apt.wall_types.items()]
    for text, fo, c in legend:
        dr.text((lx, ly), text, font=fo, fill=c)
        ly += 22
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    return out


def _draw_built_ins(dr: ImageDraw.ImageDraw, p, apt: Apartment) -> None:
    """Built-ins (boiler...): outline of the footprint (round types as an ellipse) + label, on every plan."""
    font = _font(12, True)
    for b in apt.built_ins:
        xs, ys = zip(*(p(*q) for q in b.footprint()), strict=True)
        bbox = [min(xs), min(ys), max(xs), max(ys)]
        if b.type.split("-")[-1] in ("boiler", "tank"):
            dr.ellipse(bbox, outline="#6d4c41", width=3)
        else:
            dr.rectangle(bbox, outline="#6d4c41", width=3)
        text = f"{b.label or b.type} (built-in)"
        dr.text(((bbox[0] + bbox[2]) / 2, bbox[3] + 10), text, font=font, fill="#6d4c41", anchor="mm")


def _draw_fixed_points(dr: ImageDraw.ImageDraw, p, apt: Apartment, px_per_m: int) -> None:
    """Fixed service points: a coloured dot, its tolerance circle and a short label."""
    font = _font(12, True)
    for fx in apt.fixed_points:
        c = POINT_COLORS.get(fx.kind, "#455a64")
        cx, cy = p(*fx.position)
        r, rr = 0.09 * px_per_m, fx.radius * px_per_m
        dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=c, width=1)
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c, outline="white", width=2)
        box = dr.textbbox((cx, cy - r - 9), fx.label, font=font, anchor="mm")
        dr.rectangle([box[0] - 3, box[1] - 1, box[2] + 3, box[3] + 1], fill=c)
        dr.text((cx, cy - r - 9), fx.label, font=font, fill="white", anchor="mm")


__all__ = ["render_plan", "polygon_area"]
