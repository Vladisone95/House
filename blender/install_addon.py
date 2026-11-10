"""Link + enable the project's add-on in the user's Blender and harden the Blender MCP add-on.

Run via:  uv run apartment install-addon   (runs Blender headless with the user's preferences)

* creates a directory junction  <user scripts>/addons/apartment_tools -> <repo>/blender/apartment_tools
  (edits in the repo are live after a Blender restart)
* enables 'apartment_tools'
* Blender MCP add-on: turns telemetry OFF (it defaults to ON and would upload prompts/code/screenshots)
* saves user preferences
"""

import os
import subprocess
import sys
from pathlib import Path

import addon_utils
import bpy

SRC = Path(__file__).resolve().parent / "apartment_tools"
ADDONS = Path(bpy.utils.user_resource("SCRIPTS", path="addons", create=True))
DST = ADDONS / "apartment_tools"


def link() -> None:
    if DST.exists() or DST.is_symlink():
        if DST.resolve() == SRC.resolve():
            print(f"[install] already linked: {DST}")
            return
        sys.exit(f"[install] {DST} exists and points elsewhere - remove it manually first")
    if os.name == "nt":
        subprocess.check_call(["cmd", "/c", "mklink", "/J", str(DST), str(SRC)])
    else:
        DST.symlink_to(SRC, target_is_directory=True)
    print(f"[install] linked {DST} -> {SRC}")


def main() -> None:
    link()
    addon_utils.modules_refresh()
    addon_utils.enable("apartment_tools", default_set=True, persistent=True)
    print("[install] enabled apartment_tools")

    mcp = bpy.context.preferences.addons.get("blender_mcp_addon")
    if mcp and hasattr(mcp.preferences, "telemetry_consent"):
        mcp.preferences.telemetry_consent = False
        print("[install] Blender MCP telemetry disabled")
    bpy.ops.wm.save_userpref()
    print("[install] preferences saved")


main()
