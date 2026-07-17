"""IFC validation script. Checks that the model meets project standards.
Usage: blender --background --python scripts/validate_ifc.py -- ifc/house.ifc
"""
import sys
import os


def find_ifcopenshell():
    """Add Bonsai's bundled ifcopenshell to sys.path."""
    candidates = [
        os.path.expanduser(
            "~/AppData/Roaming/Blender Foundation/Blender/5.2/extensions/"
            ".local/lib/python3.13/site-packages"
        ),
    ]
    for path in candidates:
        if os.path.isdir(path):
            sys.path.insert(0, path)
            return
    # Also try Blender's own Python path
    try:
        import bpy
        blender_python = os.path.join(
            os.path.dirname(bpy.app.binary_path),
            "5.2", "python", "lib", "site-packages"
        )
        if os.path.isdir(blender_python):
            sys.path.insert(0, blender_python)
    except ImportError:
        pass


find_ifcopenshell()

try:
    import ifcopenshell
except ImportError:
    print("ERROR: ifcopenshell not found. Run this script via Blender:")
    print('  blender --background --python scripts/validate_ifc.py -- ifc/house.ifc')
    sys.exit(1)


def validate(ifc_path):
    print(f"Validating: {ifc_path}")

    if not os.path.isfile(ifc_path):
        print(f"ERROR: File not found: {ifc_path}")
        return False

    ifc = ifcopenshell.open(ifc_path)
    errors = []
    warnings = []

    # -- Project structure --
    projects = ifc.by_type("IfcProject")
    if len(projects) != 1:
        errors.append(f"Expected 1 IfcProject, found {len(projects)}")
    else:
        print(f"  Project: {projects[0].Name}")

    sites = ifc.by_type("IfcSite")
    if len(sites) < 1:
        errors.append("No IfcSite found")

    buildings = ifc.by_type("IfcBuilding")
    if len(buildings) < 1:
        errors.append("No IfcBuilding found")

    storeys = ifc.by_type("IfcBuildingStorey")
    if len(storeys) < 1:
        errors.append("No IfcBuildingStorey found")
    else:
        print(f"  Storeys: {[s.Name for s in storeys]}")

    # -- Elements --
    walls = ifc.by_type("IfcWall")
    print(f"  Walls: {len(walls)}")
    for wall in walls:
        if not wall.Name:
            warnings.append(f"Wall #{wall.id()} has no name")

    doors = ifc.by_type("IfcDoor")
    windows = ifc.by_type("IfcWindow")
    print(f"  Doors: {len(doors)}, Windows: {len(windows)}")

    slabs = ifc.by_type("IfcSlab")
    print(f"  Slabs: {len(slabs)}")

    roofs = ifc.by_type("IfcRoof")
    print(f"  Roofs: {len(roofs)}")

    stairs = ifc.by_type("IfcStair")
    print(f"  Stairs: {len(stairs)}")

    # -- Spaces --
    spaces = ifc.by_type("IfcSpace")
    print(f"  Spaces: {len(spaces)}")
    if len(spaces) < 1 and len(walls) > 0:
        warnings.append("No IfcSpace entities found -- rooms should have spaces defined")

    # -- Openings check --
    openings = ifc.by_type("IfcOpeningElement")
    if len(doors) + len(windows) > 0 and len(openings) == 0:
        warnings.append("Doors/windows exist but no IfcOpeningElement found -- "
                        "use proper IfcRelVoidsElement")

    # -- Report --
    print(f"\n{'=' * 50}")
    print(f"VALIDATION RESULTS")
    print(f"  Elements: {len(walls)} walls, {len(slabs)} slabs, "
          f"{len(doors)} doors, {len(windows)} windows, "
          f"{len(spaces)} spaces")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    for e in errors:
        print(f"  [ERROR]   {e}")
    for w in warnings:
        print(f"  [WARNING] {w}")

    if len(errors) == 0:
        print("\n  PASSED")
    else:
        print("\n  FAILED")

    return len(errors) == 0


if __name__ == "__main__":
    argv = sys.argv
    args = argv[argv.index("--") + 1:] if "--" in argv else []
    ifc_path = args[0] if args else "ifc/house.ifc"

    success = validate(ifc_path)
    sys.exit(0 if success else 1)
