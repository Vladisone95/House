# ADR 0011 - Price list (fit-out + furniture cost estimate)

Date: 2026-10-04 · Status: accepted

## Context
The owner asked for a "Price list" button in the Apartment panel: a summary of what it would cost
to build the apartment out, with Romanian (Bucharest) prices.

## Decisions (owner, 2026-10-04)
- **Scope: fit-out + furniture only.** The shell as bought (structure, facade, windows, balcony
  door, entrance door, the 180 L boiler) already exists and is listed as "not counted".
- **Priced from the active variant** - switching variant and pressing the button again compares them.
- **Three tiers** side by side: low (DIY-store / IKEA, small crews), mid (typical Bucharest
  contractor, mid brands), high (custom carpentry, premium brands).
- **Opens in the web browser**: `docs/prices/<KEY>.html` (also `uv run apartment prices --variant V1 --open`).

## How it works
- `data/prices.toml` is the price catalogue: `[finish.<name|kind>]` per m², `[fitout.<work>]`,
  `[items.<type>]` with unit `pc | m | m2 (front) | m2_floor`. RON incl. 21 % VAT, supply + install.
  An item type falls back by dropping leading words (`plush-corner-sofa` -> `corner-sofa`).
- `apartment_core/pricing.py` measures quantities from the model: floor area per room x the
  variant's floor finish (+10 % cuts); walled perimeter x 2.70 m minus openings for paint / wall
  tiles (`[rooms.<id>] walls`); stretch ceilings + LED gap per room perimeter; skirting in parquet
  rooms; electrics per m² usable; plumbing per fixed point; one interior door per non-fixed door;
  a sill per window; site costs; 10 % contingency on the fit-out works.
- Personal props (tableware, PC, shoes...) are category `personal`: shown as excluded, cost 0.
  Types with no entry are listed in red as "not priced"; a test keeps every current variant fully priced.

## Provenance
All prices are `status = "estimated"` (Claude's market estimate, autumn 2026), **not quotes**.
When the owner gets a real offer, put it in `data/prices.toml` with `status = "quoted"` - the page
tags those lines. EUR shown at 5.10 lei (estimated, `[meta] eur_rate`).

## Update 2026-10-04 - turnkey delivery (owner)
- The apartment is delivered **turnkey**: the developer's finishing budget (Art. 1) includes paint,
  windows, entrance door, underfloor heating, boiler, electrics, plumbing, tiles (gresie 110 lei/m²,
  faianta 110 lei/m²), parquet (95 lei/m², 30 of it accessories), interior doors (800 lei/pc), bathroom
  sets (bathtub 900, shower tray 800, WC 800, basin + cabinet 800 lei), towel radiators - plus, per the
  owner, **1 AC unit and 2 heat-recovery ventilation units**. Recorded in `[turnkey]`, status confirmed.
- The list now prices only what the owner pays **on top**: a surface the variant keeps costs nothing;
  a changed developer surface costs material minus the allowance (laying included) + a surcharge for
  tiles over 60 x 60; other surfaces full price. Developer pieces are credits against the variant's
  chosen pieces (`[[turnkey.piece]]`), so upgrades cost the difference. **Furniture is never included.**
- Reading of the developer's number list (`800 900 800 800 900 800 800 800 800 800`) in document
  order: door 800; 3-room bath tub 900 / WC 800 / basin 800; service bath shower 800 / WC 800 / basin
  800. To confirm with the developer. Values of the included AC (2 800) and vents (1 600 each) estimated.
- Owner: first prices looked low; EUR = 5.36 lei. Item prices raised 20-40 % per category, checked
  against brig.ro 2026 guides (custom kitchen 1 500-2 800 / 2 800-4 000 / 5 000-10 000 lei per metre).
