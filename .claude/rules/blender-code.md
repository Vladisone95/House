---
paths: ["blender/**"]
---
# Rules for Blender code (Blender 5.2, Python 3.13)

- Build/render scripts run headless: `blender -b [--factory-startup] --python <script> -- <args>`.
  Parse args after `--`. Never rely on `bpy.context` UI areas existing in background mode.
- Use `bmesh`/`mesh.from_pydata` for geometry, not `bpy.ops.mesh.*` (needs UI context, slow).
- Render engine id is `BLENDER_EEVEE` (5.x). Sky texture type `MULTIPLE_SCATTERING`.
  Sky `sun_rotation`: 0 = towards +Y, increases clockwise (verified, ADR 0003).
- Light: one `Sun` lamp (direct) + sky with `sun_disc=False` (fill). Glass objects have
  `visible_shadow=False` so sunlight passes in EEVEE and Cycles.
- `World/Material.use_nodes` is deprecated (removal in 6.0) but still required in 5.2.
- The add-on (`blender/apartment_tools`) is linked into Blender via a junction — edits are
  live after restarting Blender. Keep `bl_info` and register/unregister symmetric.
- Add-on code imports `apartment_core` through `_core.ensure_core()`; never duplicate core logic.
- After changing build code: rebuild, render `plan,overview` + one room, and inspect the PNGs.
