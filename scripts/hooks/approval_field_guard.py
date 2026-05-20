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
import re
import sys
from pathlib import Path

# Patterns that match human-only approval field values being set by the AI.
# All share the same structure: field-name + separator + value.
APPROVAL_PATTERNS = [
    r"(?im)^\s*[-*]?\s*[*_]*status[*_]*\s*[:\|]\s*(Approved|Accepted|Implemented|Rejected|Superseded)\b",
    r"(?im)^\s*[-*]?\s*[*_]*current\s+status[*_]*\s*[:\|]\s*(Accepted|Approved|Implemented|Rejected|Superseded)\b",
    r"(?im)^\s*[-*]?\s*[*_]*approved\s+by[*_]*\s*[:\|]\s*\S+",
    r"(?im)^\s*[-*]?\s*[*_]*reviewed\s+by[*_]*\s*[:\|]\s*\S+",
    r"(?im)^\s*[-*]?\s*[*_]*sign[- ]?off[*_]*\s*[:\|]\s*(Approved|Accepted|Complete)\b",
]

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


def first_approval_match(content: str) -> str | None:
    for pattern in APPROVAL_PATTERNS:
        m = re.search(pattern, content)
        if m:
            return m.group().strip()
    return None


def content_to_check(tool_name: str, tool_input: dict, file_path: str) -> str:
    """Return text to scan.

    For Write: full new content.
    For Edit/MultiEdit: reconstruct the post-edit lines that will contain the
    changed text, by splicing new_string into the line(s) surrounding old_string
    in the existing file. Falls back to just the new_string if the file can't be
    read or the old_string isn't found.
    """
    if tool_name == "Write":
        return tool_input.get("content", "")

    if tool_name in ("Edit", "MultiEdit"):
        edits = (
            [tool_input]
            if tool_name == "Edit"
            else tool_input.get("edits", [])
        )
        parts = []
        try:
            existing = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            existing = ""

        for edit in edits:
            old = edit.get("old_string", "")
            new = edit.get("new_string", "")
            if old and existing and old in existing:
                # Replace in the existing content and return the surrounding lines
                replaced = existing.replace(old, new, 1)
                parts.append(replaced)
            else:
                parts.append(new)
        return "\n".join(parts)

    return ""


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

    text = content_to_check(tool_name, tool_input, file_path)
    if not text:
        sys.exit(0)

    match = first_approval_match(text)
    if match:
        print(
            f"\n[SDLC] APPROVAL FIELD GUARD — BLOCKED\n"
            f"\nApproval fields are human-only. You attempted to write:\n"
            f"  {match}\n"
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
