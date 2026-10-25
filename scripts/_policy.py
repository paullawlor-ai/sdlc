"""Load and query the canonical SDLC policy."""

from __future__ import annotations

import json
from pathlib import Path

from _paths import FRAMEWORK_ROOT

POLICY_PATH = FRAMEWORK_ROOT / "policy" / "sdlc-policy.json"


def load_policy(path: Path = POLICY_PATH) -> dict:
    """Return validated policy data from the canonical JSON document."""
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "framework_version",
        "change_classes",
        "profiles",
        "rules",
        "strict_warning_codes",
    }
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"Policy is missing required keys: {', '.join(missing)}")
    if data["default_profile"] not in data["profiles"]:
        raise ValueError("Policy default_profile does not name a defined profile")
    security = data.get("security_evidence", {})
    if (
        security.get("allow_risk_exceptions") is not False
        or type(security.get("max_age_days")) is not int
        or security["max_age_days"] < 1
        or set(security.get("required_tools", []))
        != {"bandit", "detect-secrets", "pip-audit"}
    ):
        raise ValueError(
            "Invalid security evidence policy; risk exceptions are not supported"
        )
    valid_signoffs = {
        "agent_recommendation",
        "human_change_transition",
        "human_review",
    }
    for name, profile in data["profiles"].items():
        if profile.get("review_signoff") not in valid_signoffs:
            raise ValueError(f"Policy profile {name} has an invalid review_signoff")
        if not isinstance(profile.get("require_committed_evidence"), bool):
            raise ValueError(
                f"Policy profile {name} must define require_committed_evidence"
            )
    strict_codes = data["strict_warning_codes"]
    if not isinstance(strict_codes, list) or not all(
        isinstance(code, str) and code for code in strict_codes
    ):
        raise ValueError(
            "Policy strict_warning_codes must be a list of diagnostic codes"
        )
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
    signoff = policy["profiles"][selected_profile]["review_signoff"]
    if result.get("requires_human_review"):
        signoff = "human_review"
    result["review_signoff"] = signoff
    result["security_evidence_max_age_days"] = policy["security_evidence"][
        "max_age_days"
    ]
    result["requires_human_review"] = signoff == "human_review"
    result["require_committed_evidence"] = policy["profiles"][selected_profile][
        "require_committed_evidence"
    ]
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
