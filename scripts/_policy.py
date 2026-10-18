"""Load and query the canonical SDLC policy."""
from __future__ import annotations

import json
from pathlib import Path

from _paths import FRAMEWORK_ROOT

POLICY_PATH = FRAMEWORK_ROOT / "policy" / "sdlc-policy.json"


def load_policy(path: Path = POLICY_PATH) -> dict:
    """Return validated policy data from the canonical JSON document."""
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {"schema_version", "framework_version", "change_classes", "profiles", "rules"}
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"Policy is missing required keys: {', '.join(missing)}")
    if data["default_profile"] not in data["profiles"]:
        raise ValueError("Policy default_profile does not name a defined profile")
    return data


def change_requirements(change_class: str, profile: str | None = None) -> dict:
    """Return effective gate requirements for a class/profile pair."""
    policy = load_policy()
    selected_profile = profile or policy["default_profile"]
    if change_class not in policy["change_classes"]:
        raise ValueError(f"Unknown change class: {change_class}")
    if selected_profile not in policy["profiles"]:
        raise ValueError(f"Unknown policy profile: {selected_profile}")
    result = dict(policy["change_classes"][change_class])
    result["profile"] = selected_profile
    result["requires_security_review"] = (
        change_class in policy["profiles"][selected_profile]["completion_review_for"]
    )
    return result


def project_profile(root: Path) -> str:
    """Return a project's configured profile or the policy default."""
    policy = load_policy()
    config = root / "sdlc_artifacts" / "config.json"
    if not config.is_file():
        return policy["default_profile"]
    try:
        selected = json.loads(config.read_text(encoding="utf-8")).get("profile")
    except (json.JSONDecodeError, OSError):
        return policy["default_profile"]
    return selected if selected in policy["profiles"] else policy["default_profile"]


def concise_rules() -> list[str]:
    policy = load_policy()
    return [f"{rule_id}: {text}" for rule_id, text in policy["rules"].items()]
