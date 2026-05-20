#!/usr/bin/env python3
"""PreToolUse hook: Implementation Gate.

Blocks Write/Edit/MultiEdit on product code when gate checks fail.

Exit codes:
  0  - allow the tool call to proceed
  2  - block the tool call (Claude Code PreToolUse convention)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _gate_common import (  # noqa: E402
    evaluate_implementation_gate,
    find_project_root,
    is_product_code,
)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    project_root = find_project_root()
    if not is_product_code(file_path, project_root):
        sys.exit(0)

    allowed, message = evaluate_implementation_gate(project_root)
    if not allowed:
        print(message)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
