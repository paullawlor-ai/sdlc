#!/usr/bin/env python3
"""Initialise or reset the project STATE.md file.

Usage:
  python sdlc/scripts/new_state.py
  python sdlc/scripts/new_state.py --reset   # overwrite existing STATE.md
"""
import os
import sys
from _paths import FRAMEWORK_ROOT, artifacts_root

# STATE.md is the main handoff file for agents. It is project-specific, so it is
# written into sdlc_artifacts rather than inside the framework runtime.
TEMPLATE = FRAMEWORK_ROOT / "templates" / "documents" / "state.md"
OUT = artifacts_root() / "STATE.md"


def main():
    # By default, preserve an existing state file. It may contain the only
    # concise record of where the previous agent session stopped.
    reset = "--reset" in sys.argv

    if os.path.exists(OUT) and not reset:
        print(f"STATE.md already exists at: {OUT}")
        print("Use --reset to overwrite it.")
        sys.exit(0)

    # The artifact root may not exist yet, especially during onboarding.
    os.makedirs(OUT.parent, exist_ok=True)

    # Copy the template verbatim. Agents then fill the phase, open items, and
    # last-session summary based on the actual project state.
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        body = f.read()

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(body)

    action = "Reset" if reset else "Created"
    print(f"{action}: {OUT}")
    print("Fill in the current phase and open items before starting work.")


if __name__ == "__main__":
    main()
