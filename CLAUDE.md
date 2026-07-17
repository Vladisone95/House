# House Project -- Architectural BIM Model

## Project Overview
Professional architectural BIM project modeling a residential house with garden using Blender 5.2 and Bonsai BIM addon. All modeling follows IFC4 standards with real-world dimensions and proper structural specifications.

## Tools
- **Blender 5.2 LTS**: `"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"`
- **Bonsai BIM 0.8.5**: IFC-standard architectural modeling (already enabled)
- **blender-mcp**: AI control of Blender via MCP (localhost:9876)
- **IFC schema**: IFC4

## Key Commands
```bash
# Headless render
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background blend/house.blend --python scripts/render.py -- exterior

# Validate IFC model
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --python scripts/validate_ifc.py -- ifc/house.ifc

# Open Blender with project file
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" blend/house.blend
```

## Modeling Standards
- All dimensions in **meters** (SI units). 1 Blender unit = 1 meter
- Exterior walls: 200mm (0.2m) concrete block + insulation
- Interior partitions: 100mm (0.1m) lightweight block
- Floor-to-ceiling height: 2.7m
- Standard storey height: 3.0m (including 200mm slab)
- Use Bonsai operators (`bpy.ops.bim.*`) for all structural elements
- Every element MUST be a real IFC entity (IfcWall, IfcSlab, IfcDoor, IfcWindow, etc.)

## IFC Conventions
- Project hierarchy: IfcProject > IfcSite > IfcBuilding > IfcBuildingStorey
- Use proper relationships: IfcRelVoidsElement, IfcRelFillsElement, IfcRelSpaceBoundary
- Populate Qto_*BaseQuantities for all elements
- Never use Blender Boolean modifiers for structural operations -- use IFC clipping
- Save IFC to `ifc/` directory

## File Organization
- `blend/` -- Blender scene files (.blend)
- `ifc/` -- IFC model exports (.ifc)
- `renders/exterior/`, `renders/interior/` -- Rendered images
- `drawings/plans/`, `drawings/sections/`, `drawings/elevations/` -- SVG drawings
- `scripts/` -- Automation scripts (render, validate)
- `specs/` -- Design specifications (dimensions, structural, materials)

## Git Workflow
- Remote: https://github.com/Vladisone95/House.git (HTTPS)
- Auto-commits via hooks on file edits and session end
- Binary files (.blend, .ifc, .png) tracked via Git LFS
- Commit messages should describe architectural changes

## Design Specifications
@specs/dimensions.md
@specs/structural.md
@specs/materials.md
