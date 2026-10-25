#!/usr/bin/env python3
"""Create a new numbered change document.

Usage:
  python sdlc/scripts/new_change.py "add rate limit middleware"
"""

import os
import re
import sys
from pathlib import Path
from _paths import FRAMEWORK_ROOT, artifacts_root
from _artifacts import metadata_root, project_metadata_mode, sync_artifact_metadata

# Change proposals are project-specific evidence. The framework owns the
# template, while the host project owns the generated files.
TEMPLATE = FRAMEWORK_ROOT / "templates" / "documents" / "change-proposal.md"
CHANGES_DIR = artifacts_root() / "changes"


def slugify(s: str) -> str:
    """Convert a human description into a readable filename slug."""
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:60] or "change"


def next_num() -> int:
    """Get the next change number from existing proposal filenames.

    Change numbers are sequential within a project. They make discussion easier
    than long filenames and remain stable even if the title is edited later.
    """
    nums = []
    if not CHANGES_DIR.exists():
        return 1
    for fn in os.listdir(CHANGES_DIR):
        m = re.match(r"^(\d{4})-", fn)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


def main():
    # Require a title because a change proposal should always be about a named,
    # reviewable increment of work.
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    title = " ".join(sys.argv[1:])
    n = next_num()
    slug = slugify(title)
    out = CHANGES_DIR / f"{n:04d}-{slug}.md"

    # The artifact directory may not exist yet in a freshly adopted project.
    os.makedirs(CHANGES_DIR, exist_ok=True)

    # The template has placeholders for the numeric ID and short title. Agents
    # then fill in motivation, scope, security impact, ACs, and rollback plan.
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        body = f.read()

    body = body.replace("XXXX", f"{n:04d}")
    body = body.replace("<short title>", title)

    temporary = Path(str(out) + ".sdlc-tmp")
    temporary.write_text(body, encoding="utf-8")
    temporary.replace(out)
    root = artifacts_root().parent
    if project_metadata_mode(root) == "required" or metadata_root(root).is_dir():
        sync_artifact_metadata(root, out)

    # Keep output deliberately plain so it works well in terminals and agent logs.
    print(f"Created: {out}")
    print(f"Change number: {n:04d}")
    print(f"Title: {title}")
    print("Status: Draft")


if __name__ == "__main__":
    main()
