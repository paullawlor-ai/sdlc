#!/usr/bin/env python3
"""Create a new numbered review document."""

from __future__ import annotations

import re
import sys

from _paths import FRAMEWORK_ROOT, artifacts_root
from _artifacts import metadata_root, project_metadata_mode, sync_artifact_metadata
from _readiness import current_revision, repository_mode

TEMPLATE = FRAMEWORK_ROOT / "templates" / "documents" / "review.md"
REVIEWS_DIR = artifacts_root() / "reviews"


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:60] or "review"


def next_num() -> int:
    numbers = []
    if REVIEWS_DIR.is_dir():
        for path in REVIEWS_DIR.glob("REV-*.md"):
            match = re.match(r"REV-(\d{4})-", path.name, re.IGNORECASE)
            if match:
                numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: new_review.py "change or review title"')
        raise SystemExit(1)
    title = " ".join(sys.argv[1:])
    number = next_num()
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    destination = REVIEWS_DIR / f"REV-{number:04d}-{slugify(title)}.md"
    root = artifacts_root().parent
    revision = current_revision(root)
    if revision is None:
        revision = (
            "not applicable (declared non-Git)"
            if repository_mode(root) == "non-git"
            else "unavailable (no Git baseline)"
        )
    content = TEMPLATE.read_text(encoding="utf-8")
    content = (
        content.replace("XXXX", f"{number:04d}")
        .replace("<change/ADR>", title)
        .replace("{{CURRENT_REVISION}}", revision)
    )
    temporary = destination.with_name(destination.name + ".sdlc-tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(destination)
    if project_metadata_mode(root) == "required" or metadata_root(root).is_dir():
        sync_artifact_metadata(root, destination)
    print(f"Created: {destination}")


if __name__ == "__main__":
    main()
