# ADR 0002 — Data-driven Blender project

- Status: accepted · Date: 2026-10-04

## Decision
- `data/apartment.toml` is the single source of truth; `models/apartment.blend` is a
  **generated, git-ignored artefact** (`uv run apartment build`).
- Geometry/validation/sun maths live in a **pure-Python package** (`src/apartment_core`) shared by
  the CLI, the tests, the headless Blender scripts and the Blender add-on.
- TOML (not YAML) because Blender's bundled Python has `tomllib` but no YAML parser.
- Walls are axis-aligned rectangles that tile without overlap; openings are spans on a wall.
  Walls are built as boxes around openings (no Boolean modifiers) → clean, fast, exact.
- Plain Blender geometry rather than IFC/Bonsai: lighter, robust headless, easy for agents.
  An IFC export can be added later from the same data if needed.
- Viewer features ship as a Blender add-on (`blender/apartment_tools`) linked into the user's
  Blender by a directory junction, so repo edits are live.
- Claude Code: project `CLAUDE.md`, path-scoped `.claude/rules`, project skills/agents, a
  PostToolUse validation hook, and a project-scoped Blender MCP with telemetry disabled.

## Consequences
- Manual tweaks in Blender are lost on rebuild → port them to data/code (documented in CLAUDE.md).
- Furniture follows the same pattern: `data/variants/<KEY>.toml` + builder (ADR 0005).
