#!/usr/bin/env python3
"""Install Claude Code hooks for the SDLC framework.

Run once from the project root after adding the sdlc/ framework:

    python sdlc/scripts/install_hooks.py

Safe to re-run: merges hooks into an existing .claude/settings.json without
clobbering other settings (permissions, env vars, model, etc.).

Prefer `python sdlc/scripts/setup_project.py` for a full adapter install.
"""
import sys
from pathlib import Path

from _paths import project_root
from _setup import install_claude_hooks


def main() -> None:
    root = project_root()
    print(f"Project root: {root}")
    print()
    lines = install_claude_hooks(root)
    print("\n".join(lines))
    print()
    print("Hooks installed:")
    print("  PreToolUse (Write|Edit|MultiEdit) -> implementation_gate.py")
    print("                                    -> approval_field_guard.py")
    print("  PreToolUse (Bash)                 -> bash_gate.py")
    print("  Stop                              -> session_end_reminder.py")
    print()
    print("To pass the implementation gate, a human must set Status: Approved on the change proposal.")
    print("To remove hooks permanently, delete the relevant entries from .claude/settings.json.")
    print()
    print("For Cursor rules, Copilot instructions, and Codex AGENTS.md, run:")
    print("  python sdlc/scripts/setup_project.py")


if __name__ == "__main__":
    main()
