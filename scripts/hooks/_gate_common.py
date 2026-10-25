"""Shared helpers for SDLC implementation gate hooks."""

from __future__ import annotations

import os
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _artifacts import validate_artifacts  # noqa: E402
from _fields import canonical_status, field_in_section, field_value  # noqa: E402

EXCLUDED_PREFIXES = (
    "sdlc" + os.sep,
    "sdlc/",
    "sdlc_artifacts" + os.sep,
    "sdlc_artifacts/",
    ".claude" + os.sep,
    ".claude/",
    ".cursor" + os.sep,
    ".cursor/",
    ".github" + os.sep,
    ".github/",
    ".git" + os.sep,
    ".git/",
)


def find_project_root() -> Path:
    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "sdlc").is_dir() or (candidate / "sdlc_artifacts").is_dir():
            return candidate
    return cwd


def is_product_code(file_path: str, project_root: Path) -> bool:
    try:
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = (Path.cwd() / file_path).resolve()
        rel = str(abs_path.relative_to(project_root))
    except ValueError:
        return False
    return not any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES)


def _is_within(path: Path, directory: Path) -> bool:
    """Return whether a resolved path is contained by a resolved directory."""
    try:
        path.resolve().relative_to(directory.resolve())
        return True
    except (OSError, ValueError):
        return False


def artifacts_dir(project_root: Path) -> Path:
    return project_root / "sdlc_artifacts"


def effective_policy(project_root: Path) -> tuple[str, str, dict]:
    """Return active change class, profile, and canonical policy data."""
    framework = project_root / "sdlc"
    if not (framework / "policy" / "sdlc-policy.json").is_file():
        framework = Path(__file__).resolve().parents[2]
    policy_path = framework / "policy" / "sdlc-policy.json"
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # A missing policy must not make a required gate less restrictive.
        return "standard", "standard", {}
    profile = policy.get("default_profile", "standard")
    config_path = artifacts_dir(project_root) / "config.json"
    try:
        configured = json.loads(config_path.read_text(encoding="utf-8")).get("profile")
        if configured in policy.get("profiles", {}):
            profile = configured
    except (OSError, json.JSONDecodeError):
        pass
    change_class = "standard"
    state_path = artifacts_dir(project_root) / "STATE.md"
    try:
        selected = field_value(state_path.read_text(encoding="utf-8"), "Change class")
        if selected in policy.get("change_classes", {}):
            change_class = selected
    except OSError:
        pass
    return change_class, profile, policy


def script_prefix(project_root: Path) -> str:
    """Return sdlc/ or empty for new_state.py style messages."""
    if (project_root / "sdlc" / "scripts").is_dir():
        return "sdlc/"
    return ""


def approved_change_files(project_root: Path) -> list[Path]:
    changes_dir = artifacts_dir(project_root) / "changes"
    if not changes_dir.is_dir():
        return []
    found: list[Path] = []
    for md in sorted(changes_dir.glob("*.md")):
        try:
            text = md.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if canonical_status(text, "change") == "Approved":
            found.append(md)
    return found


def proposed_change_names(project_root: Path) -> list[str]:
    changes_dir = artifacts_dir(project_root) / "changes"
    if not changes_dir.is_dir():
        return []
    proposed = []
    for path in sorted(changes_dir.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if canonical_status(text, "change") == "Proposed":
            proposed.append(path.name)
    return proposed


def _is_template_placeholder(value: str) -> bool:
    v = value.strip().lower()
    if not v or v in {"none", "n/a", "-", "—", "[path]", "[phase name]"}:
        return True
    if "nnnn" in v or "[none" in v:
        return True
    if v.startswith("[") and v.endswith("]") and "|" in v:
        return True
    return False


def active_change_path(project_root: Path) -> Path | None:
    """Return the active change file from STATE.md, if set and resolvable."""
    state_file = artifacts_dir(project_root) / "STATE.md"
    if not state_file.is_file():
        return None
    try:
        text = state_file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    raw_value = field_in_section(text, "Active Change", "Change document")
    if raw_value is None:
        return None
    raw = raw_value.strip().strip("`")
    if _is_template_placeholder(raw):
        return None
    changes_dir = artifacts_dir(project_root) / "changes"
    candidate = Path(raw)
    if candidate.is_absolute():
        candidates = [candidate]
    elif candidate.parent == Path("."):
        candidates = [changes_dir / candidate.name]
    else:
        candidates = [project_root / candidate]
    for possible in candidates:
        try:
            resolved = possible.resolve()
        except OSError:
            continue
        if _is_within(resolved, changes_dir) and resolved.is_file():
            return resolved
    return None


def resolve_gate_changes(
    project_root: Path,
) -> tuple[list[Path], tuple[str, str] | None]:
    """Return approved changes that satisfy active-change scoping.

    Returns (changes, error_message). error_message is set when gate should block.
    """
    approved = approved_change_files(project_root)
    active = active_change_path(project_root)
    if active is not None:
        approved_resolved = {path.resolve() for path in approved}
        if active not in approved_resolved:
            return [], (
                "active_change_not_approved",
                "The active change in STATE.md is not one of the approved "
                f"change proposals:\n  {active}",
            )
        return [active], None

    # Active change named in STATE but path did not resolve
    state_file = artifacts_dir(project_root) / "STATE.md"
    if state_file.is_file():
        text = state_file.read_text(encoding="utf-8", errors="ignore")
        raw_value = field_in_section(text, "Active Change", "Change document")
        if raw_value is not None:
            raw = raw_value.strip().strip("`")
            if not _is_template_placeholder(raw):
                return [], (
                    "active_change_not_approved",
                    f"STATE.md lists an active change that could not be resolved:\n  {raw}",
                )

    if not approved:
        return [], None

    if len(approved) == 1:
        return approved, None

    names = ", ".join(p.name for p in approved)
    return [], (
        "multiple_approved",
        "Multiple approved change proposals exist. Set exactly one in STATE.md:\n"
        "  ## Active Change\n"
        "  - **Change document**: sdlc_artifacts/changes/<file>.md\n\n"
        f"Approved changes: {names}",
    )


def blocking_adrs_from_change(change_file: Path) -> list[str]:
    try:
        text = change_file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    value = field_in_section(text, "Dependencies", "Blocking ADRs")
    if value is None:
        return []
    value = value.strip()
    if re.search(r"(?i)\bnone\b", value) or value.startswith("<!--"):
        return []
    return re.findall(r"(?i)(ADR-\d+)", value)


def find_adr_file(adr_id: str, project_root: Path) -> Path | None:
    decisions_dir = artifacts_dir(project_root) / "decisions"
    if not decisions_dir.is_dir():
        return None
    num = re.sub(r"[^0-9]", "", adr_id).lstrip("0") or "0"
    for search_dir in [
        decisions_dir,
        decisions_dir / "proposed",
        decisions_dir / "accepted",
    ]:
        if not search_dir.is_dir():
            continue
        for md in search_dir.glob("*.md"):
            if re.search(r"(?i)adr[^0-9]*0*" + re.escape(num) + r"\b", md.name):
                return md
    return None


def adr_is_accepted(adr_file: Path) -> bool:
    try:
        text = adr_file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        # Gate-critical evidence must be readable. Failing closed prevents an
        # unavailable ADR from being treated as accepted.
        return False
    return canonical_status(text, "adr") in {"Accepted", "Approved"}


def check_blocking_adrs(approved: list[Path], project_root: Path) -> list[str]:
    unaccepted: list[str] = []
    for change_file in approved:
        for adr_id in blocking_adrs_from_change(change_file):
            adr_file = find_adr_file(adr_id, project_root)
            if adr_file is None:
                unaccepted.append(
                    f"{adr_id} (file not found in sdlc_artifacts/decisions/)"
                )
            elif not adr_is_accepted(adr_file):
                unaccepted.append(f"{adr_id} ({adr_file.name})")
    return unaccepted


def gate_block_message(project_root: Path, reason: str, detail: str = "") -> str:
    prefix = script_prefix(project_root)
    if reason == "not_bootstrapped":
        return (
            "\n[SDLC] IMPLEMENTATION GATE - BLOCKED\n\n"
            "sdlc_artifacts/ not found — framework not bootstrapped.\n\n"
            "To unblock:\n"
            f"  1. Run: python {prefix}scripts/setup_project.py\n"
            f"     or: python {prefix}scripts/new_state.py\n"
            "  2. Retry the edit.\n"
        )
    if reason == "proposed_exists":
        proposed = proposed_change_names(project_root)
        first = proposed[0] if proposed else "<file>.md"
        return (
            "\n[SDLC] IMPLEMENTATION GATE - BLOCKED\n\n"
            "A change proposal exists but its Status is not 'Approved'.\n\n"
            "To unblock:\n"
            f"  1. Open sdlc_artifacts/changes/{first}\n"
            "  2. Set  Status: Approved  (human edit only)\n"
            "  3. Tell me you have approved it, then retry.\n"
        )
    if reason == "no_change":
        return (
            "\n[SDLC] IMPLEMENTATION GATE - BLOCKED\n\n"
            "No approved change proposal found for this work.\n\n"
            "To unblock:\n"
            f'  1. Run: python {prefix}scripts/new_change.py "<short description>"\n'
            "  2. Fill in the proposal and set  Status: Approved  (human edit only)\n"
            "  3. Tell me you have approved it, then retry.\n"
        )
    if reason == "blocking_adrs":
        return (
            "\n[SDLC] IMPLEMENTATION GATE - BLOCKED\n\n"
            "Change proposal is approved but has blocking ADRs that are not Accepted:\n"
            + detail
            + "\nTo unblock:\n"
            "  1. Open each ADR file in sdlc_artifacts/decisions/\n"
            "  2. Set  Current status: Accepted  (human edit only)\n"
            "  3. Tell me you have accepted the ADR(s), then retry.\n"
        )
    if reason in {"multiple_approved", "active_change_not_approved"}:
        return (
            "\n[SDLC] IMPLEMENTATION GATE - BLOCKED\n\n"
            + detail
            + "\n\nThen retry the edit.\n"
        )
    return f"\n[SDLC] IMPLEMENTATION GATE - BLOCKED\n\n{detail}\n"


def evaluate_implementation_gate(project_root: Path) -> tuple[bool, str]:
    """Return (allowed, block_message). block_message empty when allowed."""
    if not artifacts_dir(project_root).is_dir():
        return False, gate_block_message(project_root, "not_bootstrapped")

    validation_errors = validate_artifacts(project_root)
    if validation_errors:
        detail = "Artifact validation failed:\n" + "".join(
            f"  - {error}\n" for error in validation_errors
        )
        return False, gate_block_message(project_root, "validation", detail)

    change_class, _profile, policy = effective_policy(project_root)
    requirements = policy.get("change_classes", {}).get(change_class, {})
    if requirements.get("requires_change") is False:
        return True, ""

    approved, scope_error = resolve_gate_changes(project_root)
    if scope_error:
        reason, detail = scope_error
        return False, gate_block_message(project_root, reason, detail)

    if not approved:
        proposed = proposed_change_names(project_root)
        if proposed:
            return False, gate_block_message(project_root, "proposed_exists")
        return False, gate_block_message(project_root, "no_change")

    unaccepted = check_blocking_adrs(approved, project_root)
    if unaccepted:
        adr_list = "".join(f"  - {a}\n" for a in unaccepted)
        return False, gate_block_message(project_root, "blocking_adrs", adr_list)

    return True, ""
