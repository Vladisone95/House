"""Headless rendering script for the House project.
Usage: blender --background blend/house.blend --python scripts/render.py -- [exterior|interior|all]
"""
import bpy
import sys
import os


def setup_render():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'


def render_view(camera_name, output_path):
    scene = bpy.context.scene
    cam = bpy.data.objects.get(camera_name)
    if cam and cam.type == 'CAMERA':
        scene.camera = cam
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)
        print(f"Rendered: {output_path}")
    else:
        print(f"Camera '{camera_name}' not found, skipping")


def main():
    argv = sys.argv
    args = argv[argv.index("--") + 1:] if "--" in argv else ["all"]
    mode = args[0] if args else "all"

    project_dir = os.environ.get(
        "CLAUDE_PROJECT_DIR",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    setup_render()

    if mode in ("exterior", "all"):
        for cam_name in bpy.data.objects:
            if cam_name.type == 'CAMERA' and cam_name.name.startswith("Camera_Exterior"):
                suffix = cam_name.name.replace("Camera_Exterior_", "").lower()
                render_view(
                    cam_name.name,
                    os.path.join(project_dir, "renders", "exterior", f"{suffix}.png")
                )

    if mode in ("interior", "all"):
        for cam_name in bpy.data.objects:
            if cam_name.type == 'CAMERA' and cam_name.name.startswith("Camera_Interior"):
                suffix = cam_name.name.replace("Camera_Interior_", "").lower()
                render_view(
                    cam_name.name,
                    os.path.join(project_dir, "renders", "interior", f"{suffix}.png")
                )

    if mode not in ("exterior", "interior", "all"):
        # Render a specific camera by name
        render_view(mode, os.path.join(project_dir, "renders", f"{mode}.png"))


if __name__ == "__main__":
    main()
