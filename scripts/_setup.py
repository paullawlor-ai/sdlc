"""Shared project setup helpers for adapter installation and Claude hooks."""
from __future__ import annotations

import json
import hashlib
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from _paths import FRAMEWORK_ROOT, project_root

INSTALL_MANIFEST = ".sdlc-install.json"
MANAGED_START = "<!-- SDLC MANAGED START -->"
MANAGED_END = "<!-- SDLC MANAGED END -->"


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
    # Quote both components so hooks continue to work when Python or the project
    # lives under a directory containing spaces.
    return f'"{sys.executable}" "{rel}"'


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
    merged = {event: list(entries) for event, entries in existing.items()}
    for event, new_entries in additions.items():
        if event not in merged:
            merged[event] = new_entries
            continue
        new_commands = _hook_commands(new_entries)
        hook_names = {
            Path(command.replace('"', "").split()[-1]).name for command in new_commands
        }
        cleaned = []
        for entry in merged[event]:
            hooks = [
                hook
                for hook in entry.get("hooks", [])
                if not any(name in hook.get("command", "") for name in hook_names)
            ]
            if hooks:
                cleaned.append({**entry, "hooks": hooks})
        merged[event] = cleaned
        existing_cmds = _hook_commands(merged[event])
        for entry in new_entries:
            entry_cmds = _hook_commands([entry])
            if not entry_cmds.issubset(existing_cmds):
                merged[event].append(entry)
    return merged


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _managed_section(source: str) -> str:
    return f"{MANAGED_START}\n{source.rstrip()}\n{MANAGED_END}\n"


def _extract_managed(text: str) -> str | None:
    start = text.find(MANAGED_START)
    end = text.find(MANAGED_END, start + len(MANAGED_START))
    if start < 0 or end < 0:
        return None
    return text[start + len(MANAGED_START) : end].strip() + "\n"


def _replace_managed(text: str, source: str) -> str:
    start = text.find(MANAGED_START)
    end = text.find(MANAGED_END, start + len(MANAGED_START))
    replacement = _managed_section(source).rstrip()
    if not text:
        return replacement + "\n"
    if start < 0 or end < 0:
        separator = "\n" if text.endswith("\n") else "\n\n"
        return text + separator + replacement + "\n"
    end += len(MANAGED_END)
    return text[:start] + replacement + text[end:]


def _shared_adapter(rel: str) -> bool:
    return rel in {"AGENTS.md", ".github/copilot-instructions.md"}


def _backup_file(root: Path, rel: str, path: Path, timestamp: str) -> None:
    if not path.is_file():
        return
    destination = root / ".sdlc-backups" / timestamp / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)


def _atomic_write_text(path: Path, content: str) -> None:
    temporary = path.with_name(path.name + ".sdlc-tmp")
    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_copy(source: Path, destination: Path) -> None:
    temporary = destination.with_name(destination.name + ".sdlc-tmp")
    try:
        shutil.copy2(source, temporary)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def _framework_version() -> str:
    return (FRAMEWORK_ROOT / "VERSION").read_text(encoding="utf-8").strip()


def _manifest_path(root: Path) -> Path:
    return root / INSTALL_MANIFEST


def load_install_manifest(root: Path) -> dict:
    path = _manifest_path(root)
    if not path.is_file():
        return {"schema_version": 2, "framework_version": None, "assistants": [], "files": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"schema_version": 2, "framework_version": None, "assistants": [], "files": {}}


def adapter_mappings(root: Path, adapters: Path, assistants: set[str]) -> list[tuple[Path, Path, str]]:
    mappings: list[tuple[Path, Path, str]] = []
    if "cursor" in assistants:
        for src in sorted((adapters / "cursor" / "rules").glob("*.mdc")):
            mappings.append((src, root / ".cursor" / "rules" / src.name, "cursor"))
    if "copilot" in assistants:
        mappings.extend(
            [
                (
                    adapters / "copilot" / "copilot-instructions.md",
                    root / ".github" / "copilot-instructions.md",
                    "copilot",
                ),
                (
                    adapters / "copilot" / "instructions" / "sdlc.instructions.md",
                    root / ".github" / "instructions" / "sdlc.instructions.md",
                    "copilot",
                ),
            ]
        )
    if "codex" in assistants:
        mappings.append((adapters / "codex" / "AGENTS.md", root / "AGENTS.md", "codex"))
    return mappings


def install_managed_adapters(
    root: Path,
    adapters: Path,
    assistants: set[str],
    *,
    upgrade: bool = False,
    dry_run: bool = False,
    backup_id: str | None = None,
) -> list[str]:
    """Install or safely upgrade selected adapter files and their manifest."""
    manifest = load_install_manifest(root)
    file_records = dict(manifest.get("files", {}))
    lines: list[str] = []
    timestamp = backup_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    for src, dst, assistant in adapter_mappings(root, adapters, assistants):
        rel = dst.relative_to(root).as_posix()
        if not src.is_file():
            lines.append(f"  ERROR: missing source adapter {src}")
            continue
        source_text = src.read_text(encoding="utf-8")
        shared = _shared_adapter(rel)
        source_hash = _text_hash(source_text.rstrip() + "\n") if shared else _sha256(src)
        action = "skipped"
        if not dst.exists():
            action = "would_install" if dry_run else "installed"
        elif shared:
            destination_text = dst.read_text(encoding="utf-8")
            managed = _extract_managed(destination_text)
            previous = file_records.get(rel, {}).get("installed_sha256")
            if managed is not None and _text_hash(managed) == source_hash:
                action = "current"
            elif managed is None:
                action = "would_update" if dry_run else "updated"
            elif upgrade and previous and previous == _text_hash(managed):
                action = "would_update" if dry_run else "updated"
            else:
                action = "conflict"
        elif _sha256(dst) == _sha256(src):
            action = "current"
        elif upgrade:
            previous = file_records.get(rel, {}).get("installed_sha256")
            if previous and previous == _sha256(dst):
                action = "would_update" if dry_run else "updated"
            else:
                action = "conflict"
        if action in {"installed", "updated"}:
            dst.parent.mkdir(parents=True, exist_ok=True)
            _backup_file(root, rel, dst, timestamp)
            if shared:
                existing = dst.read_text(encoding="utf-8") if dst.exists() else ""
                _atomic_write_text(dst, _replace_managed(existing, source_text))
            else:
                _atomic_copy(src, dst)
        if action in {"installed", "updated", "current"}:
            file_records[rel] = {
                "assistant": assistant,
                "installed_sha256": source_hash,
                "mode": "section" if shared else "file",
            }
        labels = {
            "installed": "Installed",
            "would_install": "Would install",
            "updated": "Updated",
            "would_update": "Would update",
            "current": "Current",
            "conflict": "Skipped local modification",
            "skipped": "Skipped",
        }
        lines.append(f"  {labels[action]}: {rel}")
    if not dry_run:
        _backup_file(root, INSTALL_MANIFEST, _manifest_path(root), timestamp)
        updated_manifest = {
            "schema_version": 2,
            "framework_version": _framework_version(),
            "assistants": sorted(set(manifest.get("assistants", [])) | assistants),
            "files": file_records,
        }
        _atomic_write_text(
            _manifest_path(root), json.dumps(updated_manifest, indent=2) + "\n"
        )
    return lines


def rollback_managed_adapters(root: Path, backup: str | None = None) -> list[str]:
    """Restore adapter files from a selected or latest setup backup."""
    backup_root = root / ".sdlc-backups"
    selected = Path(backup) if backup else None
    if selected is None:
        candidates = sorted(path for path in backup_root.iterdir() if path.is_dir()) if backup_root.is_dir() else []
        selected = candidates[-1] if candidates else None
    if selected is None or not selected.is_dir():
        raise ValueError("No adapter backup is available to restore")
    restored = []
    for source in sorted(path for path in selected.rglob("*") if path.is_file()):
        relative = source.relative_to(selected)
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        restored.append(relative.as_posix())
    return restored


def record_install_selection(
    root: Path, assistants: set[str], *, dry_run: bool = False
) -> None:
    """Record selected hook-only assistants as well as file adapters."""
    if dry_run:
        return
    manifest = load_install_manifest(root)
    manifest.update(
        {
            "schema_version": 2,
            "framework_version": _framework_version(),
            "assistants": sorted(set(manifest.get("assistants", [])) | assistants),
            "files": manifest.get("files", {}),
        }
    )
    _atomic_write_text(_manifest_path(root), json.dumps(manifest, indent=2) + "\n")


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


def install_claude_hooks(
    root: Path, *, dry_run: bool = False, backup_id: str | None = None
) -> list[str]:
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

    timestamp = backup_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    _backup_file(root, ".claude/settings.json", settings_path, timestamp)
    _atomic_write_text(settings_path, json.dumps(config, indent=2) + "\n")
    return [
        f"  {action}: .claude/settings.json",
        "    Hooks: implementation_gate, approval_field_guard, bash_gate, session_end_reminder",
    ]


def ensure_artifacts_root(*, dry_run: bool = False) -> list[str]:
    """Create the project state and policy profile config when missing."""
    from _paths import artifacts_root

    mappings = (
        (FRAMEWORK_ROOT / "templates" / "documents" / "state.md", artifacts_root() / "STATE.md"),
        (FRAMEWORK_ROOT / "templates" / "documents" / "config.json", artifacts_root() / "config.json"),
    )
    lines = []
    for template, out in mappings:
        relative = out.relative_to(project_root())
        if out.exists():
            lines.append(f"  Exists: {relative}")
        elif dry_run:
            lines.append(f"  Would create: {relative}")
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
            lines.append(f"  Created: {relative}")
    return lines
