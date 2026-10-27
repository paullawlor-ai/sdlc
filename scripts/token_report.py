#!/usr/bin/env python3
"""Measure approximate framework token footprint without external packages."""

from __future__ import annotations

import json

from _paths import FRAMEWORK_ROOT
from _policy import load_policy

GROUPS = ("adapters", "agents", "prompts", "workflows", "docs", "catalogs", "templates")


def approximate_tokens(text: str) -> int:
    return (len(text) + 3) // 4


def report() -> dict:
    groups = {}
    for group in GROUPS:
        files = list((FRAMEWORK_ROOT / group).rglob("*.md"))
        files += list((FRAMEWORK_ROOT / group).rglob("*.mdc"))
        groups[group] = {
            "files": len(files),
            "approx_tokens": sum(
                approximate_tokens(path.read_text(encoding="utf-8")) for path in files
            ),
        }
    adapters = list((FRAMEWORK_ROOT / "adapters").rglob("*.md"))
    adapters += list((FRAMEWORK_ROOT / "adapters").rglob("*.mdc"))
    return {
        "method": "ceil(characters / 4)",
        "groups": groups,
        "largest_adapter_tokens": max(
            approximate_tokens(path.read_text(encoding="utf-8")) for path in adapters
        ),
        "adapter_budget": load_policy()["token_budgets"]["always_on_adapter"],
    }


def main() -> None:
    print(json.dumps(report(), indent=2))


if __name__ == "__main__":
    main()
