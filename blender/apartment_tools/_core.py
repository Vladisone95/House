"""Locate and import the pure-Python ``apartment_core`` package from the project's ``src/``."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_core(project_root: str | None = None) -> None:
    try:
        import apartment_core  # noqa: F401

        return
    except ImportError:
        pass
    candidates = [Path(__file__).resolve().parents[2] / "src"]  # resolves the add-on junction
    if project_root:
        candidates.insert(0, Path(project_root) / "src")
    for c in candidates:
        if (c / "apartment_core").is_dir():
            sys.path.insert(0, str(c))
            return
    raise ImportError("apartment_core not found - set the project folder in the Apartment panel")
