#!/usr/bin/env python3
"""Create a new retrospective document for the current iteration.

Usage:
  python sdlc/scripts/new_retrospective.py 1               # iteration 1
  python sdlc/scripts/new_retrospective.py 2 "Phase 2 MVP" # with custom name
"""

import os
import sys
from datetime import date
from pathlib import Path
from _paths import FRAMEWORK_ROOT, artifacts_root
from _artifacts import metadata_root, project_metadata_mode, sync_artifact_metadata

# Retrospectives are project artifacts because they capture what happened during
# a specific iteration of the host project. The reusable document shape lives in
# the framework template directory.
TEMPLATE = FRAMEWORK_ROOT / "templates" / "documents" / "retrospective.md"
RETRO_DIR = artifacts_root() / "retrospectives"


def main():
    # Retrospectives are tied to an iteration, so the first argument must be a
    # number. A free-form name is optional and becomes the title inside the file.
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    try:
        iter_num = int(sys.argv[1])
    except ValueError:
        print(
            f"Error: first argument must be the iteration number (integer), got: {sys.argv[1]}"
        )
        sys.exit(1)

    name = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else f"Iteration {iter_num}"
    today = date.today().isoformat()
    filename = f"{today}-iter-{iter_num}.md"

    # Ensure the artifact folder exists before writing the retrospective.
    os.makedirs(RETRO_DIR, exist_ok=True)
    out = RETRO_DIR / filename

    # Populate the template with the iteration metadata that should not need
    # manual editing. The retrospective content itself remains for the team or
    # agent to fill in honestly after the iteration.
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        body = f.read()

    body = body.replace("[Iteration Name / Date]", name)
    body = body.replace("Iteration**: [N]", f"Iteration**: {iter_num}")
    body = body.replace(
        "`sdlc_artifacts/retrospectives/[YYYY-MM-DD]-iter-[N].md`",
        f"`sdlc_artifacts/retrospectives/{filename}`",
    )
    temporary = Path(str(out) + ".sdlc-tmp")
    temporary.write_text(body, encoding="utf-8")
    temporary.replace(out)
    root = artifacts_root().parent
    if project_metadata_mode(root) == "required" or metadata_root(root).is_dir():
        sync_artifact_metadata(root, out)

    # Echo the created path and iteration identity for easy handoff notes.
    print(f"Created: {out}")
    print(f"Iteration: {iter_num}")
    print(f"Name: {name}")


if __name__ == "__main__":
    main()
