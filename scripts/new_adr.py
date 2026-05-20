#!/usr/bin/env python3
"""Create a new numbered Architecture Decision Record (ADR).

Usage:
  python sdlc/scripts/new_adr.py "use FastAPI for API layer"
"""
import os
import re
import sys
from _paths import FRAMEWORK_ROOT, artifacts_root

# ADRs are project evidence, so they are written to sdlc_artifacts. The template
# remains in the immutable framework folder.
TEMPLATE = FRAMEWORK_ROOT / "templates" / "documents" / "adr.md"
DECISIONS_DIR = artifacts_root() / "decisions"
ADR_DIR = DECISIONS_DIR / "proposed"


def slugify(s: str) -> str:
    """Convert a human title into a stable filename fragment.

    The number remains the durable identifier. The slug is just for readability
    in diffs, links, and pull requests.
    """
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:60] or "decision"


def next_num() -> int:
    """Get the next ADR number by scanning all status directories.

    ADRs move from proposed -> accepted -> superseded over their lifecycle. We
    scan every status folder so an accepted ADR number is never reused.
    """
    nums = []
    for subdir in ["proposed", "accepted", "superseded"]:
        path = DECISIONS_DIR / subdir
        if path.exists():
            for fn in os.listdir(path):
                m = re.match(r"^ADR-(\d{4})-", fn)
                if m:
                    nums.append(int(m.group(1)))
    
    return (max(nums) + 1) if nums else 1


def main():
    # A title is required because it is used in both the document body and the
    # filename. If missing, print the module docstring as a mini help page.
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    title = " ".join(sys.argv[1:])
    n = next_num()
    slug = slugify(title)
    out = ADR_DIR / f"ADR-{n:04d}-{slug}.md"

    # New ADRs always start in `proposed`. Human approval moves them to
    # `accepted`; this preserves the framework's approval gate.
    os.makedirs(ADR_DIR, exist_ok=True)

    # Fill only mechanical fields. The architectural reasoning should be written
    # by the agent/human after the scaffold is created.
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        body = f.read()

    body = body.replace("XXXX", f"{n:04d}")
    body = body.replace("<title>", title)

    with open(out, "w", encoding="utf-8") as f:
        f.write(body)

    # Print the important identifiers so scripts, agents, or humans can paste
    # them into status reports.
    print(f"Created: {out}")
    print(f"ADR number: {n:04d}")
    print(f"Title: {title}")
    print(f"Status: Proposed")


if __name__ == "__main__":
    main()
