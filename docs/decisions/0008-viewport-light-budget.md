# ADR 0008 — No light gizmos; a performance budget for lights

- Status: accepted · Date: 2026-10-04

## Context
With ~25 fixtures per variant the viewport was crowded by the lights' radius circles and became
laggy with *Lights on*. Owner: hide the circles in every schema as a general rule; bake the light
or optimise otherwise (real time not required).

## Measurement (EEVEE, night, DEV, 2 views 1280x800, 32 samples)
| | lights in depsgraph | with shadows | render time |
|---|---|---|---|
| before | 55 (DEV + V1 + sun) | 55 | 5.79 s |
| after | 28 (DEV + sun) | 3 (sun + 2 pendants) | 1.78 s |
Images compared side by side: equivalent (the floor lamp no longer throws a hard shadow).

## Decision
- **Gizmos**: 3D views have Overlays > *Extras* off (lights, probes, cameras, sun line) - set by the
  build and re-applied by the add-on on every file load (`ops.hide_gizmos`). Turn on temporarily
  via the viewport Overlays menu if needed.
- **Why not bake**: EEVEE (Blender 5.2) bakes only indirect light (volume probes); fixture light is
  always computed live. Baking indirect would also go stale with every sun time / variant change.
  The real costs are shadow maps (one per shadowed light) and per-pixel light count.
- **Budget**:
  - shadows only for statement pendants (`furniture.casts_shadow`; `[items.light] shadow = true`
    overrides);
  - every fixture has a cut-off distance 2.5-7 m from its power (`light_cutoff`);
  - inactive variants are *excluded* from the view layer (not just hidden), so their lights and
    meshes leave the depsgraph;
  - `shadow_resolution_scale` 0.5 and 256 px reflection probes for interaction; renders
    (`render_views.py`) restore shadow resolution 1.0.
- If it is still slow on this machine: use Material Preview instead of Rendered, or switch
  *Lights on* off while navigating.
