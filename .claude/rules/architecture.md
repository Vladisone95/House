# Architectural Modeling Rules

## Wall Construction
- Exterior walls: IfcWall, WAL200 type (200mm concrete block + 100mm insulation + 12.5mm plasterboard)
- Interior load-bearing: IfcWall, WAL200 type (200mm concrete block + plaster)
- Interior partitions: IfcWall, WAL100 type (100mm lightweight block + plaster)
- All walls must have mitered corners (use bonsai-walls skill)
- Wall height matches floor-to-ceiling: 2.7m default
- Material layer sets: IfcMaterialLayerSet with proper layer names and thicknesses

## Openings
- Doors: IfcDoor with proper IfcRelVoidsElement + IfcRelFillsElement
- Windows: IfcWindow with Frame/Glass/Panel sub-elements and IfcSurfaceStyle
- Opening dimensions from specs/dimensions.md
- Use equal-spacing rules for window arrays (bonsai-openings skill)
- Minimum lintel height above openings

## Structural Elements
- Ground floor slab: IfcSlab, FLR200 type (200mm reinforced concrete on DPM on 150mm hardcore)
- Upper floor slab: IfcSlab, FLR200 type (200mm reinforced concrete)
- Roof: Use appropriate topology via bonsai-roofs skill (gable, hip, mono-pitch, flat)
- Fit walls to roof underside using IFC clipping (IfcBooleanClippingResult + IfcHalfSpaceSolid)
- Foundation: IfcFooting elements below ground slab

## Spaces
- Every room must have an IfcSpace entity with proper boundary relations (IfcRelSpaceBoundary)
- Space names follow function: "Living Room", "Kitchen", "Bedroom 1", etc.
- Populate Qto_SpaceBaseQuantities for all spaces
- Spaces aggregated into their respective storey

## Stairs
- Use bonsai-stairs skill for parametric IfcStair
- Include stairwell void (IfcOpeningElement) in upper slab
- Include IfcRailing around opening
- Standard rise: 190mm, going: 250mm
