"""PostToolUse hook: after editing the layout data or the core package, re-validate the model.

Reads the hook JSON from stdin. Exit code 2 sends stderr back to Claude so it fixes the problem.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WATCH = ("data/", "src/apartment_core/")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    path = (payload.get("tool_input") or {}).get("file_path") or ""
    try:
        rel = Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return 0
    if not rel.startswith(WATCH):
        return 0

    checks = [["uv", "run", "apartment", "validate"]]
    if rel.startswith("src/"):
        checks.append(["uv", "run", "pytest", "-q", "-x"])
    for cmd in checks:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"`{' '.join(cmd)}` failed after editing {rel}:\n{r.stdout[-3000:]}{r.stderr[-1500:]}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
