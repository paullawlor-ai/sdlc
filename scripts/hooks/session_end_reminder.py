#!/usr/bin/env python3
"""Stop hook: session-end STATE.md reminder.

Fires when Claude Code is about to end a session. Prints a reminder to stdout
so Claude sees it as a follow-up task and updates STATE.md before finishing.

Checks stop_hook_active to prevent infinite loops (Claude updates STATE.md,
tries to stop again, hook fires again, repeat).
"""
import json
import sys
from pathlib import Path


def find_project_root() -> Path:
    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "sdlc_artifacts").is_dir():
            return candidate
    return cwd


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    # Prevent re-triggering: if we are already inside a stop-hook sequence, exit silently.
    if payload.get("stop_hook_active"):
        sys.exit(0)

    project_root = find_project_root()
    state_file = project_root / "sdlc_artifacts" / "STATE.md"
    if not state_file.is_file():
        sys.exit(0)

    print(
        "[SDLC] Before ending this session, update sdlc_artifacts/STATE.md:\n"
        "  - Current phase\n"
        "  - Pending Approvals / In Progress / Blocked tables\n"
        "  - 'Left off at' sentence precise enough to resume cold\n"
    )


if __name__ == "__main__":
    main()
