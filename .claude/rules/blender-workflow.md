---
paths:
  - "scripts/**/*.py"
  - "blend/**/*.blend"
---

# Blender Workflow Rules

## MCP Operations
- All Blender Python code must be executed via blender-mcp execute_blender_code tool
- Blender must be open with BlenderMCP addon active (sidebar > BlenderMCP > "Connect to Claude")
- For headless operations (render, validate), use --background flag with --python scripts
- Always import bpy at the start of Blender scripts

## Bonsai BIM Operations
- Use bpy.ops.bim.* operators for all building elements (walls, slabs, doors, windows, roofs)
- Never use raw Blender geometry (cubes, planes) for architectural elements
- Never use Blender Boolean modifiers for structural operations -- use IFC clipping
- Always save IFC file before creating drawings
- Delete drawing cache (*.h5) if results look stale

## Script Execution
- Always check bpy.context.mode before operations that require specific modes
- Use bpy.ops.object.select_all(action='DESELECT') before selecting specific objects
- Wrap long operations in try/except to prevent Blender state corruption

## File Output
- .blend files: blend/ directory
- .ifc files: ifc/ directory (via bpy.ops.bim.save_project)
- Renders: renders/exterior/ and renders/interior/
- Drawing SVGs: drawings/plans/, drawings/sections/, drawings/elevations/

## Camera Setup
- Name cameras descriptively: Camera_Exterior_Front, Camera_Interior_Living, etc.
- Exterior cameras: positioned to capture full building elevation
- Interior cameras: eye-height (1.6m) with appropriate field of view
- Set Cycles as render engine for final renders
