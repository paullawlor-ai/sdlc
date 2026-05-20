"""Shared project setup helpers for adapter installation and Claude hooks."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from _paths import FRAMEWORK_ROOT, project_root


def framework_subdir_name() -> str:
    """Return the directory name of the framework relative to the project root."""
    root = project_root()
    if FRAMEWORK_ROOT == root:
        return "."
    if FRAMEWORK_ROOT.parent == root:
        return FRAMEWORK_ROOT.name
    return FRAMEWORK_ROOT.name


def hook_command(hook_filename: str) -> str:
    """Build a hook command path for the current install layout."""
    subdir = framework_subdir_name()
    if subdir == ".":
        rel = f"scripts/hooks/{hook_filename}"
    else:
        rel = f"{subdir}/scripts/hooks/{hook_filename}"
    return f"{sys.executable} {rel}"


def sdlc_hooks() -> dict:
    """Return the SDLC hooks block with paths resolved for this project."""
    return {
        "PreToolUse": [
            {
                "matcher": "Write|Edit|MultiEdit",
                "hooks": [
                    {
                        "type": "command",
                        "command": hook_command("implementation_gate.py"),
                    },
                    {
                        "type": "command",
                        "command": hook_command("approval_field_guard.py"),
                    },
                ],
            },
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": hook_command("bash_gate.py"),
                    }
                ],
            },
        ],
        "Stop": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": hook_command("session_end_reminder.py"),
                    }
                ]
            }
        ],
    }


def _hook_commands(entries: list) -> set[str]:
    cmds: set[str] = set()
    for entry in entries:
        for hook in entry.get("hooks", []):
            if hook.get("command"):
                cmds.add(hook["command"])
    return cmds


def merge_hooks(existing: dict, additions: dict) -> dict:
    """Merge SDLC hook entries into existing hooks config without duplicates."""
    merged = dict(existing)
    for event, new_entries in additions.items():
        if event not in merged:
            merged[event] = new_entries
            continue
        existing_cmds = _hook_commands(merged[event])
        for entry in new_entries:
            entry_cmds = _hook_commands([entry])
            if not entry_cmds.issubset(existing_cmds):
                merged[event].append(entry)
    return merged


def copy_if_missing(src: Path, dst: Path, *, dry_run: bool = False) -> str:
    """Copy src to dst when dst does not exist. Returns action label."""
    if dst.exists():
        return "skipped"
    if dry_run:
        return "would_install"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return "installed"


def _format_action(action: str, label: str) -> str:
    if action == "installed":
        return f"  Installed: {label}"
    if action == "would_install":
        return f"  Would install: {label}"
    return f"  Skipped (exists): {label}"


def install_cursor_rules(root: Path, adapters: Path, *, dry_run: bool = False) -> list[str]:
    """Install Cursor rules from adapters/cursor/rules/ into .cursor/rules/."""
    lines: list[str] = []
    rules_src = adapters / "cursor" / "rules"
    rules_dst = root / ".cursor" / "rules"
    if not rules_src.is_dir():
        lines.append("WARN: no Cursor rules found in adapters/cursor/rules/")
        return lines

    for src in sorted(rules_src.glob("*.mdc")):
        dst = rules_dst / src.name
        action = copy_if_missing(src, dst, dry_run=dry_run)
        lines.append(_format_action(action, f".cursor/rules/{src.name}"))
    return lines


def install_copilot_instructions(root: Path, adapters: Path, *, dry_run: bool = False) -> list[str]:
    """Install Copilot instruction files into .github/ (creates folder if needed)."""
    lines: list[str] = []
    mappings = [
        (
            adapters / "copilot" / "copilot-instructions.md",
            root / ".github" / "copilot-instructions.md",
        ),
        (
            adapters / "copilot" / "instructions" / "sdlc.instructions.md",
            root / ".github" / "instructions" / "sdlc.instructions.md",
        ),
    ]
    for src, dst in mappings:
        if not src.is_file():
            lines.append(f"WARN: missing adapter file: {src.relative_to(adapters)}")
            continue
        action = copy_if_missing(src, dst, dry_run=dry_run)
        rel = dst.relative_to(root).as_posix()
        lines.append(_format_action(action, rel))
    return lines


def install_codex_agents(root: Path, adapters: Path, *, dry_run: bool = False) -> list[str]:
    """Install Codex AGENTS.md at project root when absent."""
    src = adapters / "codex" / "AGENTS.md"
    dst = root / "AGENTS.md"
    if not src.is_file():
        return ["WARN: missing adapters/codex/AGENTS.md"]
    action = copy_if_missing(src, dst, dry_run=dry_run)
    return [_format_action(action, "AGENTS.md")]


def install_claude_hooks(root: Path, *, dry_run: bool = False) -> list[str]:
    """Merge SDLC hooks into .claude/settings.json."""
    settings_path = root / ".claude" / "settings.json"
    if dry_run:
        if settings_path.exists():
            return [
                "  Would update: .claude/settings.json",
                "    Hooks: implementation_gate, approval_field_guard, bash_gate, session_end_reminder",
            ]
        return [
            "  Would create: .claude/settings.json",
            "    Hooks: implementation_gate, approval_field_guard, bash_gate, session_end_reminder",
        ]

    claude_dir = root / ".claude"
    settings_path = claude_dir / "settings.json"
    claude_dir.mkdir(exist_ok=True)

    if settings_path.exists():
        try:
            config = json.loads(settings_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            return [f"ERROR: could not read {settings_path}: {exc}"]
        config["hooks"] = merge_hooks(config.get("hooks", {}), sdlc_hooks())
        action = "Updated"
    else:
        config = {"hooks": sdlc_hooks()}
        action = "Created"

    settings_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return [
        f"  {action}: .claude/settings.json",
        "    Hooks: implementation_gate, approval_field_guard, bash_gate, session_end_reminder",
    ]


def ensure_artifacts_root(*, dry_run: bool = False) -> list[str]:
    """Create sdlc_artifacts/ and STATE.md when missing."""
    from _paths import artifacts_root

    out = artifacts_root() / "STATE.md"
    if out.exists():
        return [f"  Exists: {out.relative_to(project_root())}"]

    if dry_run:
        return [f"  Would create: {out.relative_to(project_root())}"]

    template = FRAMEWORK_ROOT / "templates" / "documents" / "state.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
    return [f"  Created: {out.relative_to(project_root())}"]
