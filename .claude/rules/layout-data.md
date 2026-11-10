---
paths: ["data/**"]
---
# Rules for editing data/apartment.toml

- Units are metres; keep 3 decimals (mm). Coordinates follow the model frame in CLAUDE.md.
- Walls are axis-aligned rectangles that **tile without overlapping**. Short side = the wall
  type's thickness (exterior 0.45, party/corridor 0.25, partition 0.125).
- Moving a wall means moving every rectangle, room polygon vertex and opening span that shares
  that line. Search for the old coordinate value across the whole file before saving.
- Room polygons are counter-clockwise clear interior outlines. Listed areas come from the sales
  sheet - never change `listed_area`; change geometry instead.
- Openings: `span` is absolute along the wall's long axis; keep ≥ 5 cm from wall ends and never
  cross a joining wall (validator: `opening_junction`).
- Owner-confirmed facts (see docs/decisions/0001) must not change without asking the owner.
- After editing: `uv run apartment validate` → `uv run apartment plan` → look at docs/plan.png →
  `uv run apartment build` → render and look. Log the change in docs/decisions/.
