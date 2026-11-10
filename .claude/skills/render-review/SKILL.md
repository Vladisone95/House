---
name: render-review
description: Render the apartment's camera views headless and visually check them for geometry, lighting and data problems. Use after every build, after changing build/render code, or when the owner asks to "see" the apartment.
---

# Render & review

1. `uv run apartment build` (only if data or build code changed).
2. `uv run apartment render --views plan,overview,<rooms> --samples 32 --res 1200`
   (room ids: living, kitchen, bedroom_1, bath_1, hall, bedroom_2, bath_2, balcony).
3. **Read every PNG** you rendered and check:
   - plan: all rooms present with labels + areas; walls closed; openings where `docs/plan.png`
     shows them; no z-fighting/flicker patterns; balcony aligned with living.
   - overview: wall heights uniform, windows have frames + glass, no floating/missing pieces.
   - rooms: camera inside the room at eye height, not clipping a wall; window views show sky;
     sun patches fall on the side opposite to the sun (sanity-check with `uv run apartment sun`).
4. Report findings with file paths; fix code/data issues and re-render. Show the owner the best
   images (`cmd //c start "" <png>`).

Lighting reference: EEVEE (default) is the interactive approximation; Cycles
(`--engine cycles --samples 128`) is the physically based reference used for decisions.
