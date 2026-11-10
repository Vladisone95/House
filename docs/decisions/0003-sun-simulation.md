# ADR 0003 — Sun simulation

- Status: accepted · Date: 2026-10-04

## Decision
- Sun position: NOAA solar-calculator algorithm in `apartment_core/solar.py` (no dependency on
  Blender's optional Sun Position extension). EU summer-time rule implemented explicitly
  (Windows has no tz database by default). Tests compare with published Bucharest values
  (June 21: sunrise ≈ 05:31, solar noon ≈ 13:17, sunset ≈ 21:02 EEST).
- Model orientation: `site.plus_y_bearing = 294°` (+Y = facade A outward normal = WNW), read
  from the developer key plan (navigation-style north arrow ~24° left of "up", apartment in the
  bottom-left corner of the building) and confirmed by the owner.
- Lighting: one Sun lamp (angle 0.53° = real solar disc) for direct light + a
  `MULTIPLE_SCATTERING` sky without sun disc as fill. Glass has `visible_shadow = False`.
- Blender sky `sun_rotation` convention was **measured** (Blender 5.2, Cycles probe renders):
  0 rad points the sun to +Y, positive values rotate clockwise towards +X.
  Hence `sun_rotation = atan2(dx, dy)`.
- Calibration: sun 6.0, sky 0.10, AgX, exposure +1.3, white balance 7800 K
  (neutralises the blue sky fill, like a camera's daylight WB). Cycles is the reference;
  EEVEE is the interactive preview.
- Context modelled: balcony of the floor above (shades the living balcony door).
  NOT modelled: neighbouring buildings, trees, the rest of this building. Results are therefore
  an upper bound of direct sun.

## How to use
CLI `uv run apartment sun|render|sun-study`, or Blender sidebar → Apartment → Sun study.
