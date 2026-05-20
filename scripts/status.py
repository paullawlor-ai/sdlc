#!/usr/bin/env python3
"""Print a plain-text project status summary by reading framework artifacts.

No AI session required.

Usage:
  python sdlc/scripts/status.py
  python sdlc/scripts/status.py --brief    # phase + next action only
"""
import os
import re
import sys
from pathlib import Path
from typing import Optional
from _paths import FRAMEWORK_ROOT, artifacts_root


def find_root() -> Path:
    """Find the framework root.

    The status command can be run from the framework folder, from a host project
    root, or from tooling that has a different current directory. The candidates
    below cover those common cases.
    """
    script_grandparent = FRAMEWORK_ROOT
    candidates = [
        script_grandparent,
        Path.cwd(),
        Path.cwd() / "sdlc",
    ]
    for c in candidates:
        if (c / "agents").is_dir() and (c / "workflows").is_dir():
            return c
    return script_grandparent


def find_state(artifact_root: Path) -> Optional[Path]:
    """Find STATE.md in the SDLC artifact root.

    This function exists even though there is only one current candidate. It
    makes the lookup policy explicit and leaves room for future compatibility
    with older artifact layouts.
    """
    for candidate in [artifact_root / "STATE.md"]:
        if candidate.exists():
            return candidate
    return None


def parse_state(state_path: Path) -> dict:
    """Extract the few STATE.md fields needed for a quick terminal summary."""
    text = state_path.read_text(encoding="utf-8")

    # The state template uses markdown labels rather than a structured format.
    # Regex extraction is enough for this lightweight, no-dependencies command.
    phase_match = re.search(r"\*\*Phase\*\*:\s*(.+)", text)
    phase = phase_match.group(1).strip() if phase_match else "Unknown"

    left_off_match = re.search(r"\*\*Left off at\*\*:\s*\n(.+)", text)
    left_off = left_off_match.group(1).strip() if left_off_match else None

    date_match = re.search(r"\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})", text)
    last_date = date_match.group(1) if date_match else None

    # Count table rows in the Pending Approvals section. This is intentionally
    # approximate; it is a status hint, not a compliance parser.
    pending_match = re.search(r"### Pending Approvals.*?\n(.*?)###", text, re.DOTALL)
    pending_count = 0
    if pending_match:
        rows = [
            line for line in pending_match.group(1).splitlines()
            if line.strip().startswith("|")
            and not line.strip().startswith("| #")
            and "---" not in line
            and line.strip() != "|"
        ]
        pending_count = len(rows)

    return {
        "phase": phase,
        "left_off": left_off,
        "last_date": last_date,
        "pending_count": pending_count,
    }


def count_changes(changes_dir: Path) -> dict:
    """Count change proposals by lifecycle status."""
    counts = {"Proposed": 0, "Approved": 0, "Implemented": 0, "Rejected": 0, "Superseded": 0}
    if not changes_dir.exists():
        return counts
    for f in changes_dir.glob("*.md"):
        # Skip index/template files so only actual proposals are counted.
        if f.name.startswith("_") or f.name == "README.md":
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"\*\*Status\*\*:\s*(\w+)", text)
        if m and m.group(1) in counts:
            counts[m.group(1)] += 1
    return counts


def count_adrs(decisions_dir: Path) -> dict:
    """Count ADR files by folder-based status."""
    counts = {"accepted": 0, "proposed": 0, "superseded": 0}
    if not decisions_dir.exists():
        return counts
    for subdir in ("accepted", "proposed", "superseded"):
        d = decisions_dir / subdir
        if d.is_dir():
            counts[subdir] = len([f for f in d.glob("*.md") if not f.name.startswith(".")])
    return counts


def count_reviews(reviews_dir: Path) -> int:
    """Count completed review documents."""
    if not reviews_dir.exists():
        return 0
    return len([f for f in reviews_dir.glob("*.md") if not f.name.startswith("_")])


def check_stale_adrs(decisions_dir: Path) -> list:
    """Return ADR filenames whose review-by date has passed.

    ADRs are not meant to live forever without review. This check nudges teams
    to revisit old decisions when technologies, costs, or risks change.
    """
    from datetime import date
    stale = []
    accepted = decisions_dir / "accepted"
    if not accepted.is_dir():
        return stale
    today = date.today()
    for f in accepted.glob("*.md"):
        text = f.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"\*\*Review-by date\*\*:\s*(\d{4}-\d{2}-\d{2})", text)
        if m:
            try:
                review_date = date.fromisoformat(m.group(1))
                if review_date < today:
                    stale.append((f.name, m.group(1)))
            except ValueError:
                pass
    return stale


def main():
    # `--brief` is useful for scripts or assistants that only need phase and
    # next-action orientation without the full artifact breakdown.
    brief = "--brief" in sys.argv
    root = find_root()
    artifact_root = artifacts_root()
    state_path = find_state(artifact_root)

    print("=" * 60)
    print("  SDLC Project Status")
    print("=" * 60)

    state = {}
    if not state_path:
        # Missing state usually means the project has not been bootstrapped or
        # onboarded into the framework yet.
        print("\n  [WARN]  STATE.md not found")
        print(f"     Searched: {artifact_root / 'STATE.md'}")
        print("     Run: python sdlc/scripts/new_state.py")
    else:
        state = parse_state(state_path)
        print(f"\n  Phase         : {state['phase']}")
        if state.get("last_date"):
            print(f"  Last session  : {state['last_date']}")
        if state.get("pending_count"):
            print(f"  Pending approvals : {state['pending_count']}")
        if state.get("left_off"):
            # Keep the terminal output compact; STATE.md contains the full text.
            left_off = state["left_off"]
            if len(left_off) > 52:
                left_off = left_off[:49] + "..."
            print(f"\n  Left off at   : {left_off}")

    if brief:
        print()
        return

    print()
    print("-" * 60)
    print("  Artifacts")
    print("-" * 60)
    print(f"\n  Framework root : {root}")
    print(f"  Artifact root  : {artifact_root}")

    changes = count_changes(artifact_root / "changes")
    total_changes = sum(changes.values())
    if total_changes:
        print(f"\n  Changes  ({total_changes} total)")
        for status, count in changes.items():
            if count:
                indicator = "  [PAUSE] " if status == "Proposed" else "  -> " if status == "Approved" else "    "
                print(f"  {indicator}{status:<15} {count}")
    else:
        print("\n  Changes        (none)")

    adrs = count_adrs(artifact_root / "decisions")
    total_adrs = sum(adrs.values())
    if total_adrs:
        print(f"\n  ADRs     ({total_adrs} total)")
        for status, count in adrs.items():
            if count:
                print(f"    {status:<15} {count}")
    else:
        print("\n  ADRs           (none)")

    review_count = count_reviews(artifact_root / "reviews")
    print(f"\n  Security reviews : {review_count}")

    stale = check_stale_adrs(artifact_root / "decisions")
    if stale:
        print(f"\n  [WARN]  Stale ADRs ({len(stale)}) - review-by date passed:")
        for name, date_str in stale:
            print(f"     {name}  (was due {date_str})")

    print()
    print("-" * 60)
    print("  Next Actions")
    print("-" * 60)

    if not state_path:
        # The best next action for a missing STATE.md is to create it, then let
        # an agent or human fill in the honest current phase.
        print("\n  1. Run: python sdlc/scripts/new_state.py")
        print("  2. Fill in sdlc_artifacts/STATE.md with current phase and open items")
    elif changes.get("Proposed", 0):
        # Proposed changes are approval gates. They block only the relevant
        # implementation work, not all other independent project activity.
        n = changes["Proposed"]
        print(f"\n  [PAUSE]  {n} change proposal{'s' if n > 1 else ''} awaiting approval")
        print("     Review sdlc_artifacts/changes/ and set Status to Approved to unblock implementation")
    elif changes.get("Approved", 0):
        # Approved changes are ready for developer-agent implementation.
        n = changes["Approved"]
        print(f"\n  ->  {n} change{'s' if n > 1 else ''} approved and ready to implement")
        print("     Start a session: Read sdlc/prompts/continue.md and resume")
    elif stale:
        print("\n  ->  Review stale ADRs listed above before the next iteration")
    else:
        phase = state.get("phase", "")
        if phase and phase not in ("Unknown", "[phase name]"):
            print(f"\n  ->  Continue {phase} phase:")
        else:
            print("\n  ->  Start an AI session:")
        print("     Read sdlc/prompts/continue.md and resume")

    print()


if __name__ == "__main__":
    main()

