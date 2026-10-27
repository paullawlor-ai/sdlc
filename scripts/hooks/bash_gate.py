#!/usr/bin/env python3
"""PreToolUse hook: Bash Implementation Gate.

Detects Bash commands that write to product code files and blocks them when
the implementation gate would block a direct Write/Edit.

Exit codes:
  0  - allow
  2  - block
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _gate_common import (  # noqa: E402
    evaluate_implementation_gate,
    find_project_root,
    is_product_code,
)

_WRITE_SIGNAL = re.compile(
    r"\bsed\b[^\n]*(?:-[a-zA-Z]*i[a-zA-Z]*|--in-place)"
    r"|(?<![<])[>]{1,2}\s*[^\s|;&>/\n]"
    r"|\btee\b"
    r"|\bpatch\b"
    r"|\btruncate\b[^\n]*-s\s*0"
)


def extract_write_targets(command: str) -> list[str]:
    targets: list[str] = []
    for m in re.finditer(
        r"\bsed\b((?:\s+(?:-[^\s]*|-{2}\S+|'[^']*'|\"[^\"]*\"))*)\s+('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"|[^\s|;&'\"]+)\s+([^\s|;&'\"]+)",
        command,
    ):
        targets.append(m.group(3))
    for m in re.finditer(r"(?<![<2])[>]{1,2}\s*([^\s|;&><\n]+)", command):
        candidate = m.group(1)
        if not candidate.startswith("&") and candidate != "/dev/null":
            targets.append(candidate)
    for m in re.finditer(r"\btee\b(?:\s+-a)?\s+([^\s|;&\n]+)", command):
        targets.append(m.group(1))
    for m in re.finditer(
        r"\bpatch\b[^\n|;&]*\s([^\s|;&\n]+\.(?:py|js|ts|go|java|c|cpp|h|rs|rb|php|cs|sh|yaml|yml|toml|json|html|css))\b",
        command,
    ):
        targets.append(m.group(1))
    for m in re.finditer(r"\btruncate\b[^\n]*-s\s*0\s+([^\s|;&\n]+)", command):
        targets.append(m.group(1))
    return targets


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = payload.get("tool_input", {}).get("command", "")
    if not command or not _WRITE_SIGNAL.search(command):
        sys.exit(0)

    project_root = find_project_root()
    targets = extract_write_targets(command)
    product_targets = [t for t in targets if is_product_code(t, project_root)]
    if not product_targets:
        sys.exit(0)

    allowed, message = evaluate_implementation_gate(project_root)
    if not allowed:
        files_listed = ", ".join(product_targets[:3])
        print(
            message.replace(
                "[SDLC] IMPLEMENTATION GATE - BLOCKED",
                f"[SDLC] IMPLEMENTATION GATE - BLOCKED (Bash)\n\nDetected write to product code: {files_listed}",
                1,
            )
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
