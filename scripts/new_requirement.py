#!/usr/bin/env python3
"""Create a new numbered requirement document.

Usage:
  python sdlc/scripts/new_requirement.py "user authentication"
"""
import os
import re
import sys
from _paths import FRAMEWORK_ROOT, artifacts_root

# Requirements belong to the host project and are generated under
# sdlc_artifacts. The reusable template stays in the framework folder.
TEMPLATE = FRAMEWORK_ROOT / "templates" / "documents" / "requirement.md"
REQ_DIR = artifacts_root() / "requirements"


def slugify(s: str) -> str:
    """Convert a requirement title into a readable filename slug."""
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:60] or "requirement"


def next_num() -> int:
    """Get the next requirement number from existing REQ documents.

    Requirement IDs are used later by change proposals, tests, and reviews, so
    the script scans existing files instead of relying on an external counter.
    """
    nums = []
    if os.path.exists(REQ_DIR):
        for fn in os.listdir(REQ_DIR):
            m = re.match(r"^REQ-(\d{4})-", fn)
            if m:
                nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


def main():
    # A requirement title is required because it becomes the human-readable
    # anchor for the generated REQ document.
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    title = " ".join(sys.argv[1:])
    n = next_num()
    slug = slugify(title)
    out = os.path.join(REQ_DIR, f"REQ-{n:04d}-{slug}.md")

    # First-time projects may not have any artifact directories yet.
    os.makedirs(REQ_DIR, exist_ok=True)

    # Only fill mechanical placeholders. The requirement content should be
    # written from actual stakeholder/project context.
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        body = f.read()

    body = body.replace("XXXX", f"{n:04d}")
    body = body.replace("<requirement title>", title)

    with open(out, "w", encoding="utf-8") as f:
        f.write(body)

    print(f"Created: {out}")
    print(f"Requirement number: REQ-{n:04d}")
    print(f"Title: {title}")


if __name__ == "__main__":
    main()
