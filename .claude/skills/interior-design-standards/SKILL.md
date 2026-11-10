---
name: interior-design-standards
description: Ergonomic clearances, standard furniture sizes and planning rules for residential interiors. Use in the furniture/layout phase - when proposing, checking or placing furniture, kitchens, wardrobes, bathrooms, lighting or circulation paths in this apartment.
---

# Residential interior design standards (planning reference)

Values are widely used planning guidelines (metric, Europe). They are starting points — always
fit them to the real room dimensions in `data/apartment.toml` and the owner's preferences.

## Circulation
| Situation | Minimum | Comfortable |
|---|---|---|
| Main walkway / corridor | 0.90 m | 1.10–1.20 m |
| Passage between furniture | 0.60 m | 0.75–0.90 m |
| In front of wardrobe (doors open) | 0.70 m | 0.90 m |
| Door swing zone | keep clear of leaf width | — |
| Wheel-chair turning circle | 1.50 m Ø | — |

## Living room
- Sofa depth 0.90–1.00 m; 3-seat length 2.0–2.4 m; corner sofa 2.6–3.0 m.
- Coffee table 0.40–0.45 m from sofa edge.
- TV viewing distance ≈ 1.2–1.6 × screen diagonal (4K); TV centre ≈ 1.0–1.1 m above floor.
- Keep the balcony-door path (0.90 m) and the WNW window clear for daylight.

## Dining (kitchen here)
- Space per seat 0.60 m wide × 0.40 m deep table edge; table 0.75 m high.
- Chair pull-out zone behind the table edge: 0.75 m min, 0.90 m with passage behind.

## Kitchen
- Base cabinets 0.60 m deep (0.65 with worktop overhang), worktop 0.90–0.92 m high.
- Wall cabinets 0.35 m deep, bottom at 1.40–1.50 m (0.50–0.60 m above worktop).
- Clear floor in front of counters: 1.00–1.20 m (0.90 absolute minimum).
- Work triangle (sink–hob–fridge) sum 4.0–7.0 m; worktop ≥ 0.40 m beside the hob and ≥ 0.60 m
  between sink and hob. Owner note: 0.60 m reserved beside the kitchen door for a cabinet.

## Bedrooms
- Beds: double 1.60 × 2.00 m (+ ~0.10 headboard), king 1.80 × 2.00 m, single 0.90 × 2.00 m.
- Clearance around bed sides and foot: 0.60 m min, 0.70–0.90 m comfortable.
- Bedside tables 0.40–0.50 m wide. Wardrobes 0.60 m deep (sliding doors save swing space).
- Owner notes: bedroom 2 suite has a 3 × 60 cm wardrobe zone at the entrance and wardrobes on
  the bath-2 wall (1.80 m); bedroom 1 has wardrobes on the bath-1 wall (1.80 m).

## Bathrooms
- WC: 0.20 m min from side wall to bowl edge (0.40 m to axis), 0.60 m clear in front.
- Washbasin: 0.60 m wide typical, 0.85 m high, 0.70 m clear in front.
- Shower ≥ 0.90 × 0.90 m (walk-in 1.20 × 0.90), bathtub 1.70 × 0.75 m.
- Washing machine (owner render shows one in bath 1): 0.60 × 0.60 m footprint.

## Lighting / electrical (planning level)
- Switches at 0.90–1.10 m, beside the door handle side. Sockets 0.30 m (0.10 above worktop).
- Ceiling 2.70 m: pendants ≥ 2.10 m above floor in walkways, 0.70–0.80 m above dining table.
- Use the sun studies (skill `sun-study`) before placing desks/TVs (glare from WNW evening sun).

## Process for the furniture phase
1. Agree a brief with the owner (who lives here, uses, must-keep items, style, budget).
2. Propose 2–3 layouts per room as images (top-down) with dimensions and clearances listed.
3. After approval, add furniture as **data** in `data/variants/<KEY>.toml` (skill
   `furniture-variants`, ADR 0005) — never hand-placed geometry.
