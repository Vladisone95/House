---
name: sun-study
description: Answer questions about sunlight in the apartment - which rooms get direct sun, when, how deep, at which date/time; produce sun-study renders or timelines. Use for any daylight, orientation, shading, glare or "where should X go given the sun" question.
---

# Sun studies

## Facts
- Location ≈ 44.365 N, 26.124 E (Bucharest S4). EET UTC+2, EU summer time UTC+3 (auto).
- **Facade A faces WNW 294°** → living W1 + bedroom 1 W2: afternoon/evening sun, strongest
  in summer (sun sets ~300° in June).
- **Facade B faces SSW 204°** → balcony door (living), kitchen W3, bedroom 2 W4: midday and
  afternoon sun all year; in winter the low sun reaches deep into the rooms.
- The living-room balcony door is shaded by the balcony above (`levels.balcony_above`) and the
  balcony's side wall — mostly in summer at high sun.
- Morning sun (E/SE) does not reach any window. No window faces N/NE/E.
- Solar maths: `apartment_core.solar` (NOAA, ±0.01°), tested against published Bucharest data.

## Quick answers (numbers)
`uv run apartment sun "2026-12-21 13:00"` → azimuth/elevation, sunrise/noon/sunset, and whether
each facade gets direct sun. A facade gets direct sun when the sun's elevation > 0 and the sun is
within ±90° of the facade normal (294° or 204°); in practice < ~75° gives meaningful sun.

## Visual answers
- Single moment: `uv run apartment render --views plan,living --time "2026-12-21 13:00"`
  (plan view hides the ceiling from the camera but keeps its shadows).
- Through a day: `uv run apartment sun-study --date 2026-06-21 --views plan --step 60`
  → `renders/sun_study_<date>/<view>/HHMM.png`. Use `--engine cycles --samples 128` for
  physically accurate light (slower); EEVEE (default) is right for shadows/patches.
- In Blender: sidebar → Apartment → Sun study (date, time slider, presets, day animation on
  the timeline; set viewport shading to *Rendered* for the most faithful preview).

## Reporting
Give the owner times in local clock time, name the rooms and windows, and include at least one
image (open it with `cmd //c start "" file.png`). State that the model ignores surrounding
buildings/trees (not modelled) - real sun can be blocked by neighbours.
