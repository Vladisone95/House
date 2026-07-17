"""One-time script to install and enable the BlenderMCP addon.
Usage: blender --background --python scripts/install_blender_mcp.py
"""
import bpy
import os

addon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "scripts", "blender_mcp_addon.py")

print(f"Installing addon from: {addon_path}")

# Install the addon
bpy.ops.preferences.addon_install(filepath=addon_path, overwrite=True)

# The addon module name matches the filename without .py
bpy.ops.preferences.addon_enable(module="blender_mcp_addon")

# Save preferences so it persists across Blender sessions
bpy.ops.wm.save_userpref()

print("BlenderMCP addon installed and enabled successfully")
