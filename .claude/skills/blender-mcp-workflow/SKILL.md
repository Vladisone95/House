---
name: blender-mcp-workflow
description: How to safely use the Blender MCP server (mcp__blender__*) to inspect, screenshot or experiment in the owner's live Blender session. Use before calling any mcp__blender__ tool.
---

# Blender MCP workflow

The MCP server (`.mcp.json` → `uvx blender-mcp==2.0.0`, telemetry disabled) talks to the
**BlenderMCP add-on inside the owner's running Blender** over localhost:9876.

## Prerequisites (tell the owner if a call fails to connect)
1. Blender is open with `models/apartment.blend` (`uv run apartment open`).
2. In the 3D viewport sidebar (N) → **BlenderMCP** tab → **Connect to MCP server**.
   Leave Poly Haven / Hyper3D / Sketchfab / Hunyuan unchecked unless the owner wants them.
3. Claude Code must have approved the project server `blender` (`/mcp` shows it connected).

## Rules
- **Read first**: `get_scene_info`, `get_object_info`, `get_viewport_screenshot` (pre-approved).
- `execute_blender_code` is allowed without a prompt (owner 2026-10-04). Keep snippets small, idempotent, and explain
  what they do before running. Never delete or rename generated objects - they are rebuilt from
  `data/apartment.toml` anyway; persistent changes go into the TOML / `blender/build_scene.py`.
- Use the add-on's operators instead of re-implementing them, e.g.
  `bpy.ops.apt.view_plan()`, `bpy.context.scene.apt.hour = 9.5`, `apt.sun_preset(preset='WINTER')`.
  Operators that need a 3D view must run with `bpy.context.temp_override(area=..., region=...)`.
- Do not save the .blend from MCP (`models/` is a build output). If the owner wants to keep a
  manual tweak, port it to code and rebuild.
- Cloud asset/generation tools (Hyper3D, Hunyuan) are denied in `.claude/settings.json`.
  Poly Haven (CC0) may be used in the furniture phase only with the owner's OK.
- After any visual change take `get_viewport_screenshot` and describe what you see.

## Useful snippets
```python
# jump the owner's viewport to a room at eye height
import bpy
area = next(a for a in bpy.context.screen.areas if a.type == "VIEW_3D")
region = next(r for r in area.regions if r.type == "WINDOW")
with bpy.context.temp_override(area=area, region=region):
    bpy.ops.apt.goto_room(camera="CAM_living")
```
```python
# sun at a given moment (summer time handled automatically)
s = bpy.context.scene.apt; s.month, s.day, s.hour = 12, 21, 12.0
print(s.info_azimuth, s.info_elevation, s.info_events)
```
