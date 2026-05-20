#!/usr/bin/env python3
"""Install SDLC adapters into a host project (embedded sdlc/ layout).

Typical workflow after copying the sdlc/ folder into your project:

    cd your-project-root
    python sdlc/scripts/setup_project.py

Preview without writing files:

    python sdlc/scripts/setup_project.py --dry-run

Safe to re-run:
  - Never overwrites existing adapter files at the project root
  - Merges Claude Code hooks into .claude/settings.json
"""
from __future__ import annotations

import argparse
import sys

from _paths import FRAMEWORK_ROOT, project_root
from _setup import (
    ensure_artifacts_root,
    install_claude_hooks,
    install_codex_agents,
    install_copilot_instructions,
    install_cursor_rules,
)


def _validate_layout() -> None:
    root = project_root()
    if FRAMEWORK_ROOT == root:
        print(
            "NOTE: Running from the framework repository root.\n"
            "This script is intended for host projects with an embedded sdlc/ folder.\n"
            "Adapters will be installed into this directory.\n"
        )
    elif not (root / "sdlc").is_dir() and FRAMEWORK_ROOT.name != "sdlc":
        print(
            "ERROR: Could not find an embedded sdlc/ folder in the project root.\n"
            "Run this script from your project root after copying sdlc/ into it.",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Install SDLC adapters into the host project.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be installed without writing files",
    )
    parser.add_argument(
        "--skip-artifacts",
        action="store_true",
        help="Do not create sdlc_artifacts/STATE.md when missing",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run verify_setup.py after installation",
    )
    args = parser.parse_args()

    _validate_layout()
    root = project_root()
    adapters = FRAMEWORK_ROOT / "adapters"
    dry = args.dry_run

    print(f"Project root: {root}")
    print(f"Framework:    {FRAMEWORK_ROOT}")
    if dry:
        print("Mode:         dry-run (no files will be changed)")
    print()

    print("Cursor rules (.cursor/rules/):")
    print("\n".join(install_cursor_rules(root, adapters, dry_run=dry)))
    print()

    print("GitHub Copilot (.github/):")
    print("\n".join(install_copilot_instructions(root, adapters, dry_run=dry)))
    print()

    print("Codex:")
    print("\n".join(install_codex_agents(root, adapters, dry_run=dry)))
    print()

    print("Claude Code hooks (.claude/settings.json):")
    print("\n".join(install_claude_hooks(root, dry_run=dry)))
    print()

    if not args.skip_artifacts:
        print("Artifacts:")
        print("\n".join(ensure_artifacts_root(dry_run=dry)))
        print()

    if dry:
        print("Dry-run complete. Re-run without --dry-run to apply.")
    else:
        print("Done.")
        print()
        print("Existing project files were not overwritten.")
        print("If adapter files already existed, compare them with sdlc/adapters/ and merge manually if needed.")

    print()
    print("Next steps:")
    print("  1. Run: python sdlc/scripts/verify_setup.py")
    print("  2. Open the project in your AI assistant")
    print("  3. Run: Read sdlc/prompts/onboard.md and begin   (existing project)")
    print("     or: Read sdlc/prompts/bootstrap.md and begin   (new project)")

    if args.verify and not dry:
        print()
        from verify_setup import verify_setup

        ok, lines = verify_setup()
        print("\n".join(lines))
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
