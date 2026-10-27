#!/usr/bin/env python3
"""Unified command line interface for the Agentic SDLC Framework."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

from _artifacts import (
    Diagnostic,
    artifact_token_report,
    artifact_index,
    field_in_section,
    field_value,
    section_text,
    substantive_list_items,
    migrate_metadata,
    initialize_metadata,
    rollback_metadata,
    propose_artifact,
    validate_artifacts,
    validate_diagnostics,
    write_index,
)
from _paths import FRAMEWORK_ROOT, project_root
from _policy import change_requirements, concise_rules, load_policy, project_profile
from _fields import selected_review_verdicts
from _readiness import REPOSITORY_MODES, doctor_report, git_state, repository_mode
from _security import security_evidence_diagnostics


EVIDENCE_READINESS_CODES = {
    "GIT_UNAVAILABLE",
    "GIT_REPOSITORY_REQUIRED",
    "GIT_BASELINE_MISSING",
    "SDLC_EVIDENCE_UNTRACKED",
    "SDLC_EVIDENCE_UNCOMMITTED",
}


def active_change(root: Path) -> Path | None:
    hooks = FRAMEWORK_ROOT / "scripts" / "hooks"
    sys.path.insert(0, str(hooks))
    from _gate_common import active_change_path, resolve_gate_changes

    selected = active_change_path(root)
    if selected is not None:
        return selected
    changes, error = resolve_gate_changes(root)
    return changes[0] if not error and len(changes) == 1 else None


def project_change_class(root: Path) -> str:
    state = root / "sdlc_artifacts" / "STATE.md"
    try:
        selected = field_value(state.read_text(encoding="utf-8"), "Change class")
    except OSError:
        selected = None
    return selected if selected in {"trivial", "standard", "high-risk"} else "standard"


def effective_change_class(change: Path | None, fallback: str) -> str:
    """Use the more restrictive class when project state and artifact differ."""
    ranks = {"trivial": 0, "standard": 1, "high-risk": 2}
    selected = fallback if fallback in ranks else "standard"
    if change is None:
        return selected
    try:
        artifact_class = field_value(change.read_text(encoding="utf-8"), "Risk class")
    except (OSError, UnicodeError):
        return selected
    if artifact_class in ranks and ranks[artifact_class] > ranks[selected]:
        return artifact_class
    return selected


def implementation_gate(
    root: Path, change_class: str | None, profile: str | None
) -> tuple[bool, str]:
    selected_class = change_class or project_change_class(root)
    requirements = change_requirements(selected_class, profile or project_profile(root))
    if not requirements["requires_change"]:
        return (
            True,
            f"Allowed: {selected_class} work does not require a proposal under {requirements['profile']}.",
        )
    hooks = FRAMEWORK_ROOT / "scripts" / "hooks"
    sys.path.insert(0, str(hooks))
    from _gate_common import evaluate_implementation_gate

    return evaluate_implementation_gate(root)


def _human_review_diagnostics(review_text: str, path: str) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    verdicts = selected_review_verdicts(review_text)
    if not verdicts:
        diagnostics.append(
            Diagnostic(
                "HUMAN_REVIEW_VERDICT_REQUIRED",
                "error",
                "Select exactly one human Summary Verdict.",
                path,
            )
        )
    elif len(verdicts) > 1:
        diagnostics.append(
            Diagnostic(
                "HUMAN_REVIEW_VERDICT_CONFLICT",
                "error",
                "Select only one human Summary Verdict.",
                path,
            )
        )
    elif verdicts[0] not in {"Approved", "Approved with notes"}:
        diagnostics.append(
            Diagnostic(
                "HUMAN_REVIEW_NOT_APPROVED",
                "error",
                f"Human Summary Verdict is '{verdicts[0]}'.",
                path,
            )
        )

    reviewer = field_in_section(review_text, "Approval", "Reviewer")
    placeholders = {
        "",
        "human",
        "agent-reviewer",
        "human | agent-reviewer",
        "human | agent-reviewer | both",
        "[name]",
    }
    if not reviewer or reviewer.strip().lower() in placeholders:
        diagnostics.append(
            Diagnostic(
                "HUMAN_REVIEWER_REQUIRED",
                "error",
                "Record the human reviewer's name in the Approval section.",
                path,
            )
        )

    reviewed_at = field_in_section(review_text, "Approval", "Date")
    valid_date = bool(reviewed_at and re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed_at))
    if valid_date:
        try:
            date.fromisoformat(reviewed_at)
        except ValueError:
            valid_date = False
    if not valid_date:
        diagnostics.append(
            Diagnostic(
                "HUMAN_REVIEW_DATE_REQUIRED",
                "error",
                "Record the human review date in ISO YYYY-MM-DD format.",
                path,
            )
        )
    approved_digest = field_in_section(
        review_text, "Approval", "Approved source digest"
    )
    reviewed_digest = field_in_section(
        review_text, "Reviewed Artifacts", "Reviewed source digest"
    )
    if not approved_digest or approved_digest != reviewed_digest:
        diagnostics.append(
            Diagnostic(
                "HUMAN_REVIEW_DIGEST_REQUIRED",
                "error",
                "Human approval must record the reviewed source digest; refresh sign-off after source changes.",
                path,
            )
        )
    return diagnostics


def _completion_evidence_diagnostics(
    root: Path, change: Path, requirements: dict, *, check_freshness: bool = True
) -> list[Diagnostic]:
    # Use the same canonical spelling for the root and selected artifact.
    root = root.resolve()
    change = change.resolve()
    diagnostics: list[Diagnostic] = []
    change_path = change.relative_to(root).as_posix()
    try:
        text = change.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [
            Diagnostic(
                "COMPLETION_CHANGE_UNREADABLE",
                "error",
                f"Cannot read {change.name}: {exc}",
                change_path,
            )
        ]

    completion = section_text(text, "Completion Gate")
    if completion is None:
        return [
            Diagnostic(
                "COMPLETION_EVIDENCE_MISSING",
                "error",
                f"{change.name} has no Completion Gate section.",
                change_path,
            )
        ]
    tests = field_value(completion, "Tests passing")
    if (tests or "").strip().lower() not in {"yes", "true", "pass", "passed"}:
        diagnostics.append(
            Diagnostic(
                "COMPLETION_TESTS_REQUIRED",
                "error",
                "Record tests as passing in the change Completion Gate.",
                change_path,
            )
        )

    review_ref = field_value(completion, "Security review (REV)")
    if not review_ref:
        diagnostics.append(
            Diagnostic(
                "COMPLETION_REVIEW_REQUIRED",
                "error",
                "Link a security review in the change Completion Gate.",
                change_path,
            )
        )
        return diagnostics
    review_id_match = re.search(r"(?i)\bREV-\d{4}\b", review_ref)
    if not review_id_match:
        diagnostics.append(
            Diagnostic(
                "COMPLETION_REVIEW_INVALID",
                "error",
                "Security review must reference REV-NNNN.",
                change_path,
            )
        )
        return diagnostics
    review_id = review_id_match.group(0).upper()
    candidates = sorted((root / "sdlc_artifacts" / "reviews").glob(f"{review_id}-*.md"))
    if len(candidates) != 1:
        diagnostics.append(
            Diagnostic(
                "COMPLETION_REVIEW_NOT_FOUND",
                "error",
                f"Expected exactly one review for {review_id}.",
                "sdlc_artifacts/reviews",
            )
        )
        return diagnostics
    review = candidates[0]
    review_path = review.relative_to(root).as_posix()
    try:
        review_text = review.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        diagnostics.append(
            Diagnostic(
                "COMPLETION_REVIEW_UNREADABLE",
                "error",
                f"Cannot read {review.name}: {exc}",
                review_path,
            )
        )
        return diagnostics

    reviewed = section_text(review_text, "Reviewed Artifacts") or ""
    change_id = change.name.split("-", 1)[0]
    if change.name not in reviewed and change_id not in reviewed:
        diagnostics.append(
            Diagnostic(
                "COMPLETION_REVIEW_SCOPE_MISMATCH",
                "error",
                f"{review.name} does not identify {change.name}.",
                review_path,
            )
        )
    recommendation = field_in_section(
        review_text, "Agent Recommendation", "Recommendation"
    )
    if recommendation not in {"Approved", "Approved with notes"}:
        diagnostics.append(
            Diagnostic(
                "AGENT_RECOMMENDATION_REQUIRED",
                "error",
                f"{review_id} agent recommendation must be Approved or Approved with notes.",
                review_path,
            )
        )
    must_fix = substantive_list_items(section_text(review_text, "Must-Fix"))
    if must_fix:
        diagnostics.append(
            Diagnostic(
                "REVIEW_MUST_FIX_OPEN",
                "error",
                f"{review_id} has {len(must_fix)} open must-fix finding(s).",
                review_path,
            )
        )

    recorded_recommendation = field_value(completion, "Agent recommendation")
    if recorded_recommendation != recommendation:
        diagnostics.append(
            Diagnostic(
                "COMPLETION_RECOMMENDATION_MISMATCH",
                "error",
                "Recorded recommendation does not match the linked review.",
                change_path,
            )
        )
    open_must_fix = field_value(completion, "Open must-fix in REV")
    if (open_must_fix or "").strip().lower() not in {"0", "none", "no"}:
        diagnostics.append(
            Diagnostic(
                "COMPLETION_MUST_FIX_COUNT_INVALID",
                "error",
                "Open must-fix count in the Completion Gate must be zero.",
                change_path,
            )
        )
    if requirements["requires_human_review"]:
        diagnostics.extend(_human_review_diagnostics(review_text, review_path))
    diagnostics.extend(
        security_evidence_diagnostics(
            root,
            review_text,
            review_path,
            requirements,
            check_freshness=check_freshness,
        )
    )
    return diagnostics


def finalization_diagnostics(
    root: Path, change_class: str | None = None, profile: str | None = None
) -> list[Diagnostic]:
    """Return remaining evidence or human actions before marking Implemented."""
    change = active_change(root)
    if change is None:
        return [
            Diagnostic(
                "FINALIZATION_ACTIVE_CHANGE_REQUIRED",
                "error",
                "Set one approved Active Change in STATE.md before finalization.",
                "sdlc_artifacts/STATE.md",
            )
        ]
    selected_class = effective_change_class(
        change, change_class or project_change_class(root)
    )
    requirements = change_requirements(selected_class, profile or project_profile(root))
    if not requirements["requires_security_review"]:
        return []
    return _completion_evidence_diagnostics(root, change, requirements)


def evidence_readiness_diagnostics(
    root: Path, *, finalization: bool = False, profile: str | None = None
) -> list[Diagnostic]:
    """Report audit durability separately from artifact content validity."""
    mode = repository_mode(root)
    if not isinstance(mode, str) or mode not in REPOSITORY_MODES:
        return [
            Diagnostic(
                "CONFIG_REPOSITORY_MODE_INVALID",
                "error",
                "repository_mode must be one of: auto, git, non-git.",
                "sdlc_artifacts/config.json",
            )
        ]
    if mode == "non-git":
        return []

    selected_profile = profile or project_profile(root)
    policy_requires_git = bool(
        load_policy()["profiles"]
        .get(selected_profile, {})
        .get("require_committed_evidence", False)
    )
    enforce = finalization and policy_requires_git
    severity = "error" if enforce else "warning"
    state = git_state(root)
    if not state["git_available"]:
        if mode == "git" or enforce:
            return [
                Diagnostic(
                    "GIT_UNAVAILABLE",
                    severity,
                    "Git is unavailable; evidence durability cannot be verified.",
                )
            ]
        return []
    if not state["is_repository"]:
        if mode == "git" or enforce:
            return [
                Diagnostic(
                    "GIT_REPOSITORY_REQUIRED",
                    severity,
                    "No Git repository was found for this project.",
                )
            ]
        return []

    diagnostics: list[Diagnostic] = []
    if not state["baseline_commit"]:
        diagnostics.append(
            Diagnostic(
                "GIT_BASELINE_MISSING",
                severity,
                "The repository has no baseline commit to identify the tested revision.",
            )
        )
    untracked = list(state["evidence_untracked"])
    if untracked:
        diagnostics.append(
            Diagnostic(
                "SDLC_EVIDENCE_UNTRACKED",
                severity,
                f"{len(untracked)} SDLC evidence file(s) are untracked.",
                "sdlc_artifacts",
            )
        )
    modified = list(state["evidence_modified"])
    if modified:
        diagnostics.append(
            Diagnostic(
                "SDLC_EVIDENCE_UNCOMMITTED",
                severity,
                f"{len(modified)} tracked SDLC evidence file(s) have uncommitted changes.",
                "sdlc_artifacts",
            )
        )
    return diagnostics


def implemented_review_diagnostics(root: Path) -> list[Diagnostic]:
    """Reject Implemented high-assurance changes without required human evidence."""
    diagnostics: list[Diagnostic] = []
    selected_profile = project_profile(root)
    try:
        artifacts = artifact_index(root)["artifacts"]
    except (OSError, UnicodeError, ValueError):
        # Base artifact validation already reports the underlying read failure.
        return diagnostics
    for artifact in artifacts:
        if artifact["artifact_type"] != "change" or artifact["status"] != "Implemented":
            continue
        requirements = change_requirements(artifact["risk_class"], selected_profile)
        if not requirements["requires_security_review"]:
            continue
        change = root / artifact["path"]
        diagnostics.extend(
            _completion_evidence_diagnostics(
                root, change, requirements, check_freshness=False
            )
        )
    return diagnostics


def completion_gate(
    root: Path, change_class: str | None, profile: str | None
) -> tuple[bool, str]:
    change = active_change(root)
    selected_class = effective_change_class(
        change, change_class or project_change_class(root)
    )
    requirements = change_requirements(selected_class, profile or project_profile(root))
    if not requirements["requires_security_review"]:
        return (
            True,
            f"Allowed: no completion review required for {selected_class}/{requirements['profile']}.",
        )
    validation_errors = validate_artifacts(root)
    if validation_errors:
        return (
            False,
            "Completion Gate blocked: artifact validation failed: "
            + "; ".join(validation_errors),
        )
    if change is None:
        return (
            False,
            "Completion Gate blocked: set an approved Active Change in STATE.md.",
        )
    diagnostics = _completion_evidence_diagnostics(root, change, requirements)
    if diagnostics:
        return False, f"Completion Gate blocked: {diagnostics[0].message}"
    readiness = evidence_readiness_diagnostics(
        root, finalization=True, profile=requirements["profile"]
    )
    readiness_errors = [item for item in readiness if item.severity == "error"]
    if readiness_errors:
        return False, f"Completion Gate blocked: {readiness_errors[0].message}"
    suffix = (
        " and human review is recorded" if requirements["requires_human_review"] else ""
    )
    return True, f"Completion Gate passed; tests and review evidence pass{suffix}."


def _bounded_section(
    heading: str,
    content: str,
    limit: int,
    preferred_patterns: tuple[str, ...] = (),
) -> str:
    """Return a complete headed section capped without splitting a line."""
    prefix = f"\n{heading}\n"
    available = max(0, limit - len(prefix))
    visible = content.strip()
    if len(visible) <= available:
        return prefix + visible
    if preferred_patterns:
        preferred = [
            line
            for line in visible.splitlines()
            if any(re.search(pattern, line, re.I) for pattern in preferred_patterns)
        ]
        if preferred:
            visible = "\n".join(preferred) + "\n\n" + visible
    marker = "\n[Section compacted; open the source artifact for full detail]"
    available = max(0, available - len(marker))
    candidate = visible[:available]
    if "\n" in candidate:
        candidate = candidate.rsplit("\n", 1)[0]
    return prefix + candidate.rstrip() + marker


def context_packet(
    root: Path, phase: str | None, budget: int, extended_evidence: bool = False
) -> str:
    policy = load_policy()
    sections = [f"# SDLC Context ({phase or 'current phase'})"]
    project_artifacts = root / "sdlc_artifacts"
    state_path = project_artifacts / "STATE.md"
    deferred_state: list[str] = []
    if state_path.is_file():
        state = state_path.read_text(encoding="utf-8", errors="ignore")
        state_lines = []
        for label in ("Phase", "Goal", "Change class", "Change document"):
            value = field_value(state, label)
            if value:
                state_lines.append(f"- **{label}**: {value}")
        sections.append(
            _bounded_section("## Current State", "\n".join(state_lines), 700)
        )
        for heading in ("Blocked", "Next Action"):
            value = section_text(state, heading)
            if value and "<!-- Add rows only" not in value:
                sections.append(_bounded_section(f"## {heading}", value, 700))
        for heading in ("Pending Approvals", "Last Session Summary"):
            value = section_text(state, heading)
            if value and "<!-- Add rows only" not in value:
                if heading == "Last Session Summary" and len(value) > 700:
                    value = (
                        "[Oversized handoff omitted; run `sdlc handoff` to replace it "
                        "with a compact current summary]"
                    )
                deferred_state.append(_bounded_section(f"## {heading}", value, 700))
    change = active_change(root)
    if change:
        text = change.read_text(encoding="utf-8", errors="ignore")
        sections.append(f"\n## Active Change: {change.name}")
        for heading in (
            "Summary",
            "Dependencies",
            "Acceptance Criteria",
            "Completion Gate",
            "Testing",
            "Security Impact",
            "Scope",
        ):
            value = section_text(text, heading)
            if value:
                limits = {
                    "Summary": 700,
                    "Dependencies": 900,
                    "Acceptance Criteria": 1900,
                    "Completion Gate": 1100,
                    "Testing": 1000,
                    "Security Impact": 800,
                    "Scope": 700,
                }
                preferred = {
                    "Dependencies": (r"\*\*(?:Blocking|External)",),
                    "Acceptance Criteria": (r"\bAC-\d+\b",),
                    "Completion Gate": (
                        r"\*\*(?:Tests passing|Security review|Agent recommendation|Open must-fix|Gate result)",
                    ),
                    "Testing": (
                        r"\*\*(?:Unit tests|Integration tests|Negative / abuse cases)",
                    ),
                    "Security Impact": (
                        r"\*\*(?:Risks reduced|New risks introduced|OWASP mapping|Controls implemented)",
                    ),
                    "Scope": (
                        r"\*\*(?:Risk class|Policy profile|Components affected)",
                    ),
                }
                sections.append(
                    _bounded_section(
                        f"### Active Change - {heading}",
                        value,
                        limits[heading],
                        preferred.get(heading, ()),
                    )
                )
        if extended_evidence:
            for heading in (
                "Proposed Approach",
                "Why This Approach",
                "Performance & Reliability Impact",
                "Operational Notes",
                "Rollback Plan",
                "Evidence References",
            ):
                value = section_text(text, heading)
                if value:
                    deferred_state.append(
                        _bounded_section(
                            f"### Extended Evidence - {heading}", value, 1600
                        )
                    )
    sections.append(
        _bounded_section(
            "## Rules", "\n".join(f"- {rule}" for rule in concise_rules()), 1200
        )
    )
    sections.extend(deferred_state)
    context_path = project_artifacts / "context.md"
    if context_path.is_file():
        context = context_path.read_text(encoding="utf-8", errors="ignore")
        context_limit = 2400 if extended_evidence else 1200
        sections.append(_bounded_section("## Project Context", context, context_limit))
    sections.append(
        "\n## References\n"
        "Open detailed role, workflow, and security documents only when the current action requires them."
    )
    character_budget = budget * 4
    footer = "\n\n[Additional lower-priority context omitted to fit the token budget]\n"
    selected: list[str] = []
    used = 0
    omitted = False
    for section in sections:
        addition = section + "\n"
        if used + len(addition) <= character_budget - len(footer):
            selected.append(section)
            used += len(addition)
        else:
            omitted = True
    packet = "\n".join(selected)
    if omitted:
        packet = packet.rstrip() + footer
    configured = policy["token_budgets"]["resume_context"]
    if budget > configured:
        packet += f"\n[Requested budget {budget}; recommended resume budget is {configured}]\n"
    return packet


def _replace_markdown_section(text: str, heading: str, body: str) -> str:
    """Replace one Markdown section while preserving the surrounding document."""
    matches = list(re.finditer(r"(?m)^(#{1,6})\s+(.+?)\s*$", text))
    for index, match in enumerate(matches):
        if match.group(2).strip().casefold() != heading.casefold():
            continue
        level = len(match.group(1))
        end = len(text)
        for following in matches[index + 1 :]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        replacement = f"{match.group(1)} {heading}\n\n{body.strip()}\n\n"
        return text[: match.start()] + replacement + text[end:].lstrip("\n")
    suffix = "" if text.endswith("\n") else "\n"
    return text + suffix + f"\n## {heading}\n\n{body.strip()}\n"


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def record_handoff(
    root: Path,
    completed: list[str],
    left_off: str,
    next_action: str | None = None,
    handoff_date: str | None = None,
) -> dict[str, object]:
    """Replace the current handoff and archive its predecessor outside context."""
    state_path = root / "sdlc_artifacts" / "STATE.md"
    if not state_path.is_file():
        raise ValueError("sdlc_artifacts/STATE.md does not exist")
    selected_date = handoff_date or date.today().isoformat()
    try:
        date.fromisoformat(selected_date)
    except ValueError as exc:
        raise ValueError("handoff date must use ISO YYYY-MM-DD") from exc
    if not completed or not all(item.strip() for item in completed):
        raise ValueError("at least one non-empty completed item is required")
    if not left_off.strip():
        raise ValueError("left-off text is required")
    if next_action is not None and not next_action.strip():
        raise ValueError("next-action text cannot be empty")

    state = state_path.read_text(encoding="utf-8")
    previous = section_text(state, "Last Session Summary") or ""
    visible_previous = re.sub(r"(?s)<!--.*?-->", "", previous).strip()
    placeholders = ("[YYYY-MM-DD]", "[Concise list", "[One sentence")
    archive_previous = bool(visible_previous) and not any(
        marker in visible_previous for marker in placeholders
    )
    archive_path = root / "sdlc_artifacts" / "history" / "handoffs.md"
    if archive_previous:
        existing = (
            archive_path.read_text(encoding="utf-8")
            if archive_path.is_file()
            else "# Handoff History\n\n"
        )
        archived = (
            existing.rstrip()
            + f"\n\n## Archived before {selected_date}\n\n{previous.strip()}\n"
        )
        _atomic_write(archive_path, archived)

    completed_lines = "\n".join(f"- {item.strip()}" for item in completed)
    current = (
        f"**Date**: {selected_date}\n\n"
        f"**Completed**:\n{completed_lines}\n\n"
        f"**Left off at**:\n{left_off.strip()}"
    )
    updated = _replace_markdown_section(state, "Last Session Summary", current)
    if next_action is not None:
        updated = _replace_markdown_section(updated, "Next Action", next_action)
    _atomic_write(state_path, updated)
    return {
        "state": state_path.relative_to(root).as_posix(),
        "archived_previous": archive_previous,
        "archive": archive_path.relative_to(root).as_posix(),
    }


def run_legacy(script: str, arguments: list[str]) -> int:
    command = [sys.executable, str(FRAMEWORK_ROOT / "scripts" / script), *arguments]
    return subprocess.run(command, check=False).returncode


def strict_warning_failures(diagnostics: list[Diagnostic]) -> list[Diagnostic]:
    """Return warnings that canonical policy promotes to failures in strict mode."""
    strict_codes = set(load_policy().get("strict_warning_codes", []))
    return [
        item
        for item in diagnostics
        if item.severity == "warning" and item.code in strict_codes
    ]


def command_check(
    root: Path,
    write: bool,
    as_json: bool,
    strict: bool = False,
    ready_to_finalize: bool = False,
) -> int:
    from generate_adapters import generate
    from token_report import report

    diagnostics = validate_diagnostics(root)
    diagnostics.extend(implemented_review_diagnostics(root))
    diagnostics.extend(
        evidence_readiness_diagnostics(root, finalization=ready_to_finalize)
    )
    if ready_to_finalize:
        diagnostics.extend(finalization_diagnostics(root))
    config = root / "sdlc_artifacts" / "config.json"
    if config.is_file():
        try:
            config_data = json.loads(config.read_text(encoding="utf-8"))
            if config_data.get("profile") not in load_policy()["profiles"]:
                diagnostics.append(
                    Diagnostic(
                        "CONFIG_INVALID", "error", f"{config}: unknown policy profile"
                    )
                )
        except (json.JSONDecodeError, OSError) as exc:
            diagnostics.append(
                Diagnostic(
                    "CONFIG_INVALID", "error", f"{config}: invalid configuration: {exc}"
                )
            )
    try:
        generate(check=True)
    except SystemExit as exc:
        diagnostics.append(Diagnostic("ADAPTER_DRIFT", "error", str(exc)))
    token_data = report()
    if token_data["largest_adapter_tokens"] > token_data["adapter_budget"]:
        diagnostics.append(
            Diagnostic(
                "TOKEN_BUDGET_EXCEEDED",
                "error",
                "An adapter exceeds the configured token budget",
            )
        )
    if write:
        write_index(root)
    errors = [item for item in diagnostics if item.severity == "error"]
    warnings = [item for item in diagnostics if item.severity == "warning"]
    strict_failures = strict_warning_failures(diagnostics)
    ok = not errors and not (strict and strict_failures)
    result = {
        "ok": ok,
        "content_ok": not any(
            item.severity == "error" and item.code not in EVIDENCE_READINESS_CODES
            for item in diagnostics
        ),
        "evidence_ready": not any(
            item.severity in {"error", "warning"}
            and item.code in EVIDENCE_READINESS_CODES
            for item in diagnostics
        ),
        "evidence": git_state(root),
        "strict": strict,
        "ready_to_finalize": ok if ready_to_finalize else None,
        "finalization_action": (
            "Human may set the active change status to Implemented."
            if ready_to_finalize and ok
            else None
        ),
        "errors": [item.message for item in errors],
        "warnings": [item.message for item in warnings],
        "strict_failures": [item.as_dict() for item in strict_failures],
        "diagnostics": [item.as_dict() for item in diagnostics],
        "artifact_count": len(artifact_index(root)["artifacts"]),
        "artifact_tokens": artifact_token_report(root),
        "tokens": token_data,
    }
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print("SDLC check passed." if ok else "SDLC check failed.")
        for item in diagnostics:
            location = f" ({item.path})" if item.path else ""
            print(f"- [{item.severity.upper()}] {item.code}{location}: {item.message}")
        if ready_to_finalize and ok:
            print(
                "Ready to finalize: human may set the active change status to Implemented."
            )
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sdlc")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("next")
    context = sub.add_parser("context")
    context.add_argument("--phase")
    context.add_argument("--budget", type=int, default=2000)
    context.add_argument(
        "--extended-evidence",
        action="store_true",
        help="include bounded implementation and operational evidence",
    )
    handoff = sub.add_parser("handoff")
    handoff.add_argument(
        "--completed",
        action="append",
        required=True,
        help="completed outcome; repeat for multiple items",
    )
    handoff.add_argument("--left-off", required=True)
    handoff.add_argument("--next-action")
    handoff.add_argument("--date", dest="handoff_date")
    handoff.add_argument("--json", action="store_true")
    check = sub.add_parser("check")
    check.add_argument("--write-index", action="store_true")
    check.add_argument("--json", action="store_true")
    check.add_argument("--strict", action="store_true")
    check.add_argument(
        "--ready-to-finalize",
        action="store_true",
        help="report remaining evidence and human actions before Implemented",
    )
    doctor = sub.add_parser("doctor")
    doctor.add_argument("--json", action="store_true")
    gate = sub.add_parser("gate")
    gate.add_argument("gate_name", choices=("implementation", "completion"))
    gate.add_argument(
        "--class", dest="change_class", choices=("trivial", "standard", "high-risk")
    )
    gate.add_argument("--profile", choices=("lite", "standard", "regulated"))
    new = sub.add_parser("new")
    new.add_argument(
        "artifact", choices=("change", "adr", "requirement", "review", "retrospective")
    )
    new.add_argument("arguments", nargs=argparse.REMAINDER)
    propose = sub.add_parser("propose")
    propose.add_argument(
        "path", help="complete Draft change or ADR to validate and promote"
    )
    setup = sub.add_parser("setup")
    setup.add_argument("--dry-run", action="store_true")
    setup.add_argument("--skip-artifacts", action="store_true")
    setup.add_argument("--verify", action="store_true")
    setup.add_argument(
        "--assistant",
        action="append",
        choices=("codex", "cursor", "copilot", "claude", "all"),
    )
    setup.add_argument("--upgrade", action="store_true")
    setup.add_argument("--rollback", action="store_true")
    setup.add_argument("--backup")
    sub.add_parser("verify")
    migrate = sub.add_parser("migrate")
    migrate.add_argument("--json", action="store_true")
    migrate.add_argument(
        "--apply", action="store_true", help="Write metadata; default is a dry-run"
    )
    migrate.add_argument(
        "--rollback", action="store_true", help="Restore the latest metadata backup"
    )
    migrate.add_argument(
        "--backup", help="Specific metadata backup directory to restore"
    )
    metadata = sub.add_parser("metadata")
    metadata.add_argument("action", choices=("sync",))
    metadata.add_argument(
        "--apply", action="store_true", help="Write metadata; default is a dry-run"
    )
    metadata.add_argument("--json", action="store_true")
    metadata.add_argument(
        "--mode",
        choices=("required",),
        default="required",
        help="target metadata mode (sync adopts required mode by default)",
    )
    upgrade = sub.add_parser("upgrade")
    upgrade.add_argument("--apply", action="store_true")
    upgrade.add_argument("--rollback", action="store_true")
    upgrade.add_argument("--backup")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    root = project_root()
    if args.command == "status":
        raise SystemExit(run_legacy("status.py", []))
    if args.command == "next":
        allowed, message = implementation_gate(root, None, None)
        print("Continue the active approved change." if allowed else message)
        raise SystemExit(0)
    if args.command == "context":
        print(context_packet(root, args.phase, args.budget, args.extended_evidence))
        return
    if args.command == "handoff":
        try:
            result = record_handoff(
                root,
                args.completed,
                args.left_off,
                args.next_action,
                args.handoff_date,
            )
        except (OSError, UnicodeError, ValueError) as exc:
            print(f"Handoff failed: {exc}")
            raise SystemExit(1) from exc
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            archive_note = (
                f" Previous handoff archived in {result['archive']}."
                if result["archived_previous"]
                else ""
            )
            print(f"Handoff recorded in {result['state']}.{archive_note}")
        return
    if args.command == "check":
        raise SystemExit(
            command_check(
                root,
                args.write_index,
                args.json,
                args.strict,
                args.ready_to_finalize,
            )
        )
    if args.command == "doctor":
        report = doctor_report(root)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            python = report["python"]
            project = report["project"]
            temporary = report["temporary_directory"]
            git = report["git"]
            print(f"Python: {python['version']} ({python['command']})")
            print(
                "Virtual environment: "
                + ("active" if python["virtual_environment"] else "not active")
            )
            print(f"Project writable: {'yes' if project['writable'] else 'no'}")
            print(
                f"Temporary directory writable: {'yes' if temporary['writable'] else 'no'}"
            )
            print(f"Repository mode: {git['mode']}")
            if git["mode"] == "non-git":
                print("Git evidence: not applicable (declared non-Git)")
            elif not git["git_available"]:
                print("Git evidence: Git is unavailable")
            elif not git["is_repository"]:
                print("Git evidence: no repository found")
            else:
                print(f"Git baseline: {git['baseline_commit'] or 'missing'}")
                print(
                    "SDLC evidence changes: "
                    f"{len(git['evidence_untracked'])} untracked, "
                    f"{len(git['evidence_modified'])} modified"
                )
            for finding in report["fixed_pytest_basetemps"]:
                print(
                    "Warning: fixed pytest --basetemp "
                    f"'{finding['value']}' in {finding['path']} can collide across runs."
                )
            if not project["writable"]:
                print(f"Project write error: {project['error']}")
            if not temporary["writable"]:
                print(f"Temporary directory error: {temporary['error']}")
        raise SystemExit(0 if report["ok"] else 1)
    if args.command == "gate":
        gate_fn = (
            implementation_gate
            if args.gate_name == "implementation"
            else completion_gate
        )
        allowed, message = gate_fn(root, args.change_class, args.profile)
        print(message or "Gate passed.")
        raise SystemExit(0 if allowed else 2)
    if args.command == "new":
        scripts = {
            "change": "new_change.py",
            "adr": "new_adr.py",
            "requirement": "new_requirement.py",
            "review": "new_review.py",
            "retrospective": "new_retrospective.py",
        }
        raise SystemExit(run_legacy(scripts[args.artifact], args.arguments))
    if args.command == "propose":
        diagnostics = propose_artifact(root, Path(args.path))
        if diagnostics:
            for item in diagnostics:
                print(f"[{item.severity.upper()}] {item.code}: {item.message}")
            raise SystemExit(1)
        print(f"Proposed: {args.path}")
        return
    if args.command == "setup":
        arguments: list[str] = []
        if args.dry_run:
            arguments.append("--dry-run")
        if args.skip_artifacts:
            arguments.append("--skip-artifacts")
        if args.verify:
            arguments.append("--verify")
        for assistant in args.assistant or []:
            arguments.extend(("--assistant", assistant))
        if args.upgrade:
            arguments.append("--upgrade")
        if args.rollback:
            arguments.append("--rollback")
        if args.backup:
            arguments.extend(("--backup", args.backup))
        raise SystemExit(run_legacy("setup_project.py", arguments))
    if args.command == "verify":
        raise SystemExit(run_legacy("verify_setup.py", []))
    if args.command == "migrate":
        if args.rollback:
            try:
                result = rollback_metadata(root, args.backup)
            except ValueError as exc:
                print(str(exc))
                raise SystemExit(1) from exc
            print(
                json.dumps(result, indent=2)
                if args.json
                else f"Restored: {result['restored']}"
            )
            return
        errors = validate_artifacts(root)
        errors = [error for error in errors if "structured metadata" not in error]
        if errors:
            print(
                json.dumps({"ok": False, "errors": errors}, indent=2)
                if args.json
                else "\n".join(errors)
            )
            raise SystemExit(1)
        result = migrate_metadata(root, apply=args.apply)
        result["ok"] = True
        if args.json:
            print(json.dumps(result, indent=2))
        elif args.apply:
            print(f"Migrated {len(result['changes'])} metadata file(s).")
        else:
            print(
                f"Would migrate {len(result['changes'])} metadata file(s); add --apply to write."
            )
        return
    if args.command == "metadata":
        errors = [
            error
            for error in validate_artifacts(root)
            if "structured metadata" not in error.lower()
        ]
        if errors:
            result = {"ok": False, "errors": errors}
            print(json.dumps(result, indent=2) if args.json else "\n".join(errors))
            raise SystemExit(1)
        try:
            result = migrate_metadata(root, apply=args.apply, target_mode=args.mode)
            if args.apply:
                initialize_metadata(root)
        except (OSError, UnicodeError, ValueError) as exc:
            result = {"ok": False, "errors": [str(exc)]}
            print(json.dumps(result, indent=2) if args.json else str(exc))
            raise SystemExit(1) from exc
        result["ok"] = True
        if args.json:
            print(json.dumps(result, indent=2))
        elif args.apply:
            print(
                f"Synchronized {len(result['changes'])} metadata file(s); "
                f"metadata mode is {result['mode']}."
            )
        else:
            mode_note = (
                " and set metadata mode to required" if result["mode_change"] else ""
            )
            print(
                f"Would synchronize {len(result['changes'])} metadata file(s)"
                f"{mode_note}; add --apply to write."
            )
        return
    if args.command == "upgrade":
        if args.rollback:
            arguments = ["--rollback"]
            if args.backup:
                arguments.extend(["--backup", args.backup])
            raise SystemExit(run_legacy("setup_project.py", arguments))
        arguments = ["--upgrade"]
        if not args.apply:
            arguments.append("--dry-run")
        raise SystemExit(run_legacy("setup_project.py", arguments))


if __name__ == "__main__":
    main()
