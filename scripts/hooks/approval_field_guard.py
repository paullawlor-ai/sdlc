#!/usr/bin/env python3
"""PreToolUse hook: Approval Field Guard.

Blocks Write/Edit/MultiEdit on sdlc_artifacts/ files when the written
content contains human-only approval fields (Status: Approved, Approved by,
Current status: Accepted, Reviewed by, etc.).

Exit codes:
  0  - allow
  2  - block
"""

import json
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _fields import protected_approval_values  # noqa: E402

ARTIFACTS_PREFIXES = (
    "sdlc_artifacts" + os.sep,
    "sdlc_artifacts/",
)


def find_project_root() -> Path:
    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "sdlc").is_dir() or (candidate / "sdlc_artifacts").is_dir():
            return candidate
    return cwd


def is_artifact_file(file_path: str, project_root: Path) -> bool:
    try:
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = (Path.cwd() / file_path).resolve()
        rel = str(abs_path.relative_to(project_root))
    except ValueError:
        return False
    return any(rel.startswith(prefix) for prefix in ARTIFACTS_PREFIXES)


def protected_snapshot(content: str) -> Counter[str]:
    """Return normalized protected decisions present in artifact content."""
    return Counter(protected_approval_values(content))


def content_before_after(
    tool_name: str, tool_input: dict, file_path: str
) -> tuple[str, str]:
    """Return artifact content before and after the proposed tool operation.

    MultiEdit operations are applied sequentially so the snapshot matches the
    content the tool would produce.
    """
    try:
        before = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        before = ""

    if tool_name == "Write":
        return before, tool_input.get("content", "")

    if tool_name in ("Edit", "MultiEdit"):
        edits = [tool_input] if tool_name == "Edit" else tool_input.get("edits", [])
        after = before
        for edit in edits:
            old = edit.get("old_string", "")
            new = edit.get("new_string", "")
            if old and old in after:
                after = after.replace(old, new, 1)
            else:
                # A malformed edit should still be scanned for an attempted
                # protected value even though the underlying tool may reject it.
                after += "\n" + new
        return before, after

    return before, before


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    project_root = find_project_root()

    if not is_artifact_file(file_path, project_root):
        sys.exit(0)

    before, after = content_before_after(tool_name, tool_input, file_path)
    if not after:
        sys.exit(0)

    old_snapshot = protected_snapshot(before)
    new_snapshot = protected_snapshot(after)
    if old_snapshot != new_snapshot:
        added = list((new_snapshot - old_snapshot).elements())
        removed = list((old_snapshot - new_snapshot).elements())
        change = (added or removed or ["protected approval field"])[0]
        print(
            f"\n[SDLC] APPROVAL FIELD GUARD — BLOCKED\n"
            f"\nApproval fields are human-only. You attempted to change:\n"
            f"  {change}\n"
            f"\nTo proceed:\n"
            f"  1. Open  {file_path}  in your editor\n"
            f"  2. Set the field to the correct value yourself\n"
            f"  3. Save the file, then tell me to continue.\n",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
