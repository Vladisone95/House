# IFC Conventions

## Project Hierarchy
- IfcProject: "House with Garden"
- IfcSite: "Residential Plot"
- IfcBuilding: "Main House"
- IfcBuildingStorey: "Ground Floor" (elevation 0.0m), "First Floor" (3.0m), "Roof" (6.0m)

## Naming Conventions
- Walls: "EXT-GF-001" (exterior, ground floor, sequential), "INT-GF-001" (interior)
- Doors: "DR-GF-001" (door, ground floor, sequential)
- Windows: "WN-GF-001" (window, ground floor, sequential)
- Slabs: "SLB-GF-001" (slab, ground floor)
- Spaces: Descriptive names ("Living Room", "Kitchen")

## Required IFC Relationships
- Every wall opening: IfcRelVoidsElement connecting IfcOpeningElement to IfcWall
- Every door/window in opening: IfcRelFillsElement connecting IfcDoor/IfcWindow to IfcOpeningElement
- Every space boundary: IfcRelSpaceBoundary connecting IfcSpace to bounding elements
- Slab-wall connections: IfcRelConnectsElements
- Element-to-storey: IfcRelContainedInSpatialStructure
- Element types: IfcRelDefinesByType linking instances to their IfcWallType/IfcSlabType

## Quantity Sets (Required)
- Walls: Qto_WallBaseQuantities (Length, Height, Width, GrossArea, NetArea, GrossVolume)
- Slabs: Qto_SlabBaseQuantities (GrossArea, NetArea, Width, GrossVolume)
- Doors: Qto_DoorBaseQuantities (Height, Width, Area)
- Windows: Qto_WindowBaseQuantities (Height, Width, Area)
- Spaces: Qto_SpaceBaseQuantities (GrossFloorArea, NetFloorArea, Height, GrossVolume)

## IFC File Management
- Schema: IFC4 (not IFC2x3)
- Save to ifc/house.ifc after significant modeling changes
- Always save IFC before generating drawings
- Use bpy.ops.bim.save_project() for IFC export
