#!/usr/bin/env python3
"""Check release-source consistency; does not publish or approve a release."""

from __future__ import annotations

import json
import re
from pathlib import Path

from _paths import FRAMEWORK_ROOT
from _policy import load_policy
from generate_adapters import outputs
from token_report import approximate_tokens


def release_errors(root: Path = FRAMEWORK_ROOT) -> list[str]:
    errors = []
    try:
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            errors.append(
                "VERSION must contain one semantic version (major.minor.patch)"
            )
        policy = load_policy(root / "policy/sdlc-policy.json")
        if policy["framework_version"] != version:
            errors.append("VERSION and policy framework_version differ")
        changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        if not re.search(rf"(?m)^## {re.escape(version)} - .+$", changelog):
            errors.append(f"CHANGELOG.md has no entry for {version}")
        for relative, content in outputs(policy).items():
            path = root / "adapters" / relative
            if path.read_text(encoding="utf-8") != content.rstrip() + "\n":
                errors.append(f"Generated adapter is stale: {relative.as_posix()}")
        budget = policy["token_budgets"]["always_on_adapter"]
        for path in (root / "adapters").rglob("*"):
            if (
                path.suffix in {".md", ".mdc"}
                and approximate_tokens(path.read_text(encoding="utf-8")) > budget
            ):
                errors.append(
                    f"Adapter exceeds {budget} tokens: {path.relative_to(root)}"
                )
        for name in ("upgrading.md", "releasing.md", "quality-and-security.md"):
            if not (root / "docs/framework" / name).is_file():
                errors.append(f"Missing release guidance: {name}")
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"Cannot verify release sources: {exc}")
    return errors


def main() -> int:
    errors = release_errors()
    print(
        json.dumps(
            {
                "ok": not errors,
                "errors": errors,
                "scope": "local release-source consistency",
            },
            indent=2,
        )
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
