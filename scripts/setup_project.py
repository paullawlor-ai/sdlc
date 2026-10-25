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
from datetime import datetime, timezone

from _paths import FRAMEWORK_ROOT, project_root
from _setup import (
    ensure_artifacts_root,
    install_managed_adapters,
    install_claude_hooks,
    record_install_selection,
    rollback_managed_adapters,
)
from _artifacts import initialize_metadata, project_metadata_mode


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
    parser = argparse.ArgumentParser(
        description="Install SDLC adapters into the host project."
    )
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
    parser.add_argument(
        "--assistant",
        action="append",
        choices=("codex", "cursor", "copilot", "claude", "all"),
        help="Install only selected assistant integration(s); repeat as needed",
    )
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Update unmodified managed adapters and report local conflicts",
    )
    parser.add_argument(
        "--rollback", action="store_true", help="Restore the latest adapter backup"
    )
    parser.add_argument("--backup", help="Specific adapter backup directory to restore")
    args = parser.parse_args()

    _validate_layout()
    root = project_root()
    if args.rollback:
        try:
            restored = rollback_managed_adapters(root, args.backup)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        print(f"Restored {len(restored)} adapter file(s).")
        for path in restored:
            print(f"  Restored: {path}")
        return
    adapters = FRAMEWORK_ROOT / "adapters"
    dry = args.dry_run
    requested = set(args.assistant or ["all"])
    assistants = (
        {"codex", "cursor", "copilot", "claude"} if "all" in requested else requested
    )
    backup_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    print(f"Project root: {root}")
    print(f"Framework:    {FRAMEWORK_ROOT}")
    if dry:
        print("Mode:         dry-run (no files will be changed)")
    print()

    file_assistants = assistants & {"codex", "cursor", "copilot"}
    if file_assistants:
        print("Managed assistant adapters:")
        print(
            "\n".join(
                install_managed_adapters(
                    root,
                    adapters,
                    file_assistants,
                    upgrade=args.upgrade,
                    dry_run=dry,
                    backup_id=backup_id,
                )
            )
        )
        print()

    if "claude" in assistants:
        print("Claude Code hooks (.claude/settings.json):")
        print("\n".join(install_claude_hooks(root, dry_run=dry, backup_id=backup_id)))
        print()

    record_install_selection(root, assistants, dry_run=dry)

    if not args.skip_artifacts:
        print("Artifacts:")
        print("\n".join(ensure_artifacts_root(dry_run=dry)))
        if not dry and project_metadata_mode(root) == "required":
            initialize_metadata(root)
            print("[OK] structured metadata initialized")
        print()

    if dry:
        print("Dry-run complete. Re-run without --dry-run to apply.")
    else:
        print("Done.")
        print()
        print("Locally modified adapter files were preserved.")
        print("Run with --upgrade to update adapters tracked by .sdlc-install.json.")

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
