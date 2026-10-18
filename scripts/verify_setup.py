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
from _setup import (
    _extract_managed,
    _sha256,
    _text_hash,
    adapter_mappings,
    hook_command,
    load_install_manifest,
)

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
    manifest = load_install_manifest(root)
    selected = set(manifest.get("assistants", []))
    legacy_all = not selected

    # Cursor rules
    for name in REQUIRED_CURSOR_RULES if legacy_all or "cursor" in selected else ():
        path = root / ".cursor" / "rules" / name
        ok, line = _check(f".cursor/rules/{name}", path.is_file(), "run setup_project.py")
        lines.append(line)
        all_ok &= ok

    # Copilot
    for rel in REQUIRED_COPILOT if legacy_all or "copilot" in selected else ():
        path = root / Path(rel)
        ok, line = _check(rel, path.is_file(), "run setup_project.py")
        lines.append(line)
        all_ok &= ok

    # Claude hooks
    settings_path = root / ".claude" / "settings.json"
    if (legacy_all or "claude" in selected) and not settings_path.is_file():
        ok, line = _check(".claude/settings.json", False, "run setup_project.py")
        lines.append(line)
        all_ok &= ok
    elif legacy_all or "claude" in selected:
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

    if (legacy_all or "codex" in selected) and not (root / "AGENTS.md").is_file():
        ok, line = _check("AGENTS.md", False, "run setup_project.py --assistant codex")
        lines.append(line)
        all_ok &= ok

    if selected:
        installed_version = manifest.get("framework_version")
        current_version = (FRAMEWORK_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        ok, line = _check(
            ".sdlc-install.json version",
            installed_version == current_version,
            f"installed {installed_version}, framework {current_version}; run setup_project.py --upgrade",
        )
        lines.append(line)
        all_ok &= ok

        expected_sources = {
            dst.relative_to(root).as_posix(): src
            for src, dst, _assistant in adapter_mappings(
                root, FRAMEWORK_ROOT / "adapters", selected
            )
        }
        for rel, record in manifest.get("files", {}).items():
            installed = root / rel
            recorded_hash = record.get("installed_sha256")
            present = installed.is_file()
            if present and record.get("mode") == "section":
                managed = _extract_managed(installed.read_text(encoding="utf-8"))
                unmodified = managed is not None and _text_hash(managed) == recorded_hash
            else:
                unmodified = present and _sha256(installed) == recorded_hash
            source = expected_sources.get(rel)
            if source is None:
                current = True
            elif record.get("mode") == "section":
                current = source.is_file() and _text_hash(
                    source.read_text(encoding="utf-8").rstrip() + "\n"
                ) == recorded_hash
            else:
                current = source.is_file() and _sha256(source) == recorded_hash
            ok, line = _check(
                f"managed adapter {rel}",
                present and unmodified and current,
                "missing, locally modified, or stale; run setup_project.py --upgrade",
            )
            lines.append(line)
            all_ok &= ok

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
