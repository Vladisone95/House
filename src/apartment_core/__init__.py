"""Pure-Python core for the apartment model.

No dependency on ``bpy`` - everything here runs in plain CPython (tests, CLI)
and inside Blender's bundled Python (build script, add-on).
"""

from .model import Apartment, load

__all__ = ["Apartment", "load"]
