---
paths: ["src/**", "tests/**"]
---
# Rules for the pure-Python core

- No `bpy`, `mathutils`, numpy or other heavy deps in `src/apartment_core` (Pillow only in
  `plan2d.py`, which is never imported by Blender code).
- Every behaviour change gets a test in `tests/`. Solar code is checked against published
  Bucharest sunrise/sunset and noon elevations - keep those tests.
- Keep the validator strict: new geometric rules -> new `Issue` codes with clear messages.
- Run `uv run pytest` and `uv run ruff check .` before declaring done.
