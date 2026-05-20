#!/usr/bin/env python3
"""Verify SDLC adapter installation at the project root.

Usage:
    python sdlc/scripts/verify_setup.py

Exit codes:
    0 — all required checks passed (warnings may still be printed)
    1 — one or more required checks failed
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from _paths import FRAMEWORK_ROOT, project_root
from _setup import hook_command

REQUIRED_CURSOR_RULES = (
    "implementation-gate.mdc",
    "core.mdc",
    "security.mdc",
    "agents.mdc",
)

REQUIRED_HOOKS = (
    "implementation_gate.py",
    "approval_field_guard.py",
    "bash_gate.py",
    "session_end_reminder.py",
)

REQUIRED_COPILOT = (
    ".github/copilot-instructions.md",
    ".github/instructions/sdlc.instructions.md",
)


def _check(label: str, ok: bool, detail: str = "") -> tuple[bool, str]:
    status = "OK" if ok else "FAIL"
    line = f"  [{status}] {label}"
    if detail and not ok:
        line += f" — {detail}"
    return ok, line


def verify_setup() -> tuple[bool, list[str]]:
    root = project_root()
    lines: list[str] = [f"Project root: {root}", f"Framework:    {FRAMEWORK_ROOT}", ""]
    all_ok = True

    # Cursor rules
    for name in REQUIRED_CURSOR_RULES:
        path = root / ".cursor" / "rules" / name
        ok, line = _check(f".cursor/rules/{name}", path.is_file(), "run setup_project.py")
        lines.append(line)
        all_ok &= ok

    # Copilot
    for rel in REQUIRED_COPILOT:
        path = root / Path(rel)
        ok, line = _check(rel, path.is_file(), "run setup_project.py")
        lines.append(line)
        all_ok &= ok

    # Claude hooks
    settings_path = root / ".claude" / "settings.json"
    if not settings_path.is_file():
        ok, line = _check(".claude/settings.json", False, "run setup_project.py")
        lines.append(line)
        all_ok &= ok
    else:
        try:
            config = json.loads(settings_path.read_text(encoding="utf-8"))
            hooks = config.get("hooks", {})
            commands = []
            for entries in hooks.values():
                if isinstance(entries, list):
                    for entry in entries:
                        for hook in entry.get("hooks", []):
                            cmd = hook.get("command", "")
                            if cmd:
                                commands.append(cmd)
            missing_hooks = []
            for hook_file in REQUIRED_HOOKS:
                expected = hook_command(hook_file)
                if not any(hook_file in c for c in commands):
                    missing_hooks.append(hook_file)
            ok = not missing_hooks
            detail = "missing: " + ", ".join(missing_hooks) if missing_hooks else "all four hooks present"
            ok, line = _check(".claude/settings.json hooks", ok, detail)
            lines.append(line)
            all_ok &= ok
        except (json.JSONDecodeError, OSError) as exc:
            ok, line = _check(".claude/settings.json", False, str(exc))
            lines.append(line)
            all_ok &= ok

    # Artifacts
    state = root / "sdlc_artifacts" / "STATE.md"
    ok, line = _check("sdlc_artifacts/STATE.md", state.is_file(), "run setup_project.py or new_state.py")
    lines.append(line)
    all_ok &= ok

    if not (root / "AGENTS.md").is_file():
        lines.append("  [INFO] AGENTS.md not at project root (optional for Codex)")

    return all_ok, lines


def main() -> None:
    ok, lines = verify_setup()
    print("\n".join(lines))
    print()
    if ok:
        print("Setup verification passed.")
    else:
        print("Setup verification failed. Run: python sdlc/scripts/setup_project.py")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
