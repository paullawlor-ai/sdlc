#!/usr/bin/env python3
"""Unified command line interface for the Agentic SDLC Framework."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from _artifacts import (
    artifact_index,
    field_in_section,
    field_value,
    section_text,
    substantive_list_items,
    migrate_metadata,
    rollback_metadata,
    validate_artifacts,
    write_index,
)
from _paths import FRAMEWORK_ROOT, project_root
from _policy import change_requirements, concise_rules, load_policy, project_profile


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


def implementation_gate(root: Path, change_class: str | None, profile: str | None) -> tuple[bool, str]:
    selected_class = change_class or project_change_class(root)
    requirements = change_requirements(selected_class, profile or project_profile(root))
    if not requirements["requires_change"]:
        return True, f"Allowed: {selected_class} work does not require a proposal under {requirements['profile']}."
    hooks = FRAMEWORK_ROOT / "scripts" / "hooks"
    sys.path.insert(0, str(hooks))
    from _gate_common import evaluate_implementation_gate

    return evaluate_implementation_gate(root)


def completion_gate(root: Path, change_class: str | None, profile: str | None) -> tuple[bool, str]:
    selected_class = change_class or project_change_class(root)
    requirements = change_requirements(selected_class, profile or project_profile(root))
    if not requirements["requires_security_review"]:
        return True, f"Allowed: no completion review required for {selected_class}/{requirements['profile']}."
    validation_errors = validate_artifacts(root)
    if validation_errors:
        return False, "Completion Gate blocked: artifact validation failed: " + "; ".join(validation_errors)
    change = active_change(root)
    if change is None:
        return False, "Completion Gate blocked: set an approved Active Change in STATE.md."
    try:
        text = change.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return False, f"Completion Gate blocked: cannot read {change.name}: {exc}"

    completion = section_text(text, "Completion Gate")
    if completion is None:
        return False, f"Completion Gate blocked: {change.name} has no Completion Gate section."
    tests = field_value(completion, "Tests passing")
    if (tests or "").strip().lower() not in {"yes", "true", "pass", "passed"}:
        return False, "Completion Gate blocked: tests are not recorded as passing."

    review_ref = field_value(completion, "Security review (REV)")
    if not review_ref:
        return False, "Completion Gate blocked: no security review is linked."
    review_id_match = re.search(r"(?i)\bREV-\d{4}\b", review_ref)
    if not review_id_match:
        return False, "Completion Gate blocked: security review must reference REV-NNNN."
    review_id = review_id_match.group(0).upper()
    candidates = sorted((root / "sdlc_artifacts" / "reviews").glob(f"{review_id}-*.md"))
    if len(candidates) != 1:
        return False, f"Completion Gate blocked: expected exactly one review for {review_id}."
    review = candidates[0]
    try:
        review_text = review.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return False, f"Completion Gate blocked: cannot read {review.name}: {exc}"

    reviewed = section_text(review_text, "Reviewed Artifacts") or ""
    change_id = change.name.split("-", 1)[0]
    if change.name not in reviewed and change_id not in reviewed:
        return False, f"Completion Gate blocked: {review.name} does not identify {change.name}."
    recommendation = field_in_section(
        review_text, "Agent Recommendation", "Recommendation"
    )
    if recommendation not in {"Approved", "Approved with notes"}:
        return False, f"Completion Gate blocked: {review_id} recommendation is not acceptable."
    must_fix = substantive_list_items(section_text(review_text, "Must-Fix"))
    if must_fix:
        return False, f"Completion Gate blocked: {review_id} has {len(must_fix)} open must-fix finding(s)."

    recorded_recommendation = field_value(completion, "Agent recommendation")
    if recorded_recommendation != recommendation:
        return False, "Completion Gate blocked: recorded recommendation does not match the review."
    open_must_fix = field_value(completion, "Open must-fix in REV")
    if (open_must_fix or "").strip().lower() not in {"0", "none", "no"}:
        return False, "Completion Gate blocked: open must-fix count must be zero."
    return True, f"Completion Gate passed using {review_id}; tests pass and no must-fix findings remain."


def context_packet(root: Path, phase: str | None, budget: int) -> str:
    policy = load_policy()
    sections = [f"# SDLC Context ({phase or 'current phase'})"]
    project_artifacts = root / "sdlc_artifacts"
    state_path = project_artifacts / "STATE.md"
    if state_path.is_file():
        state = state_path.read_text(encoding="utf-8", errors="ignore")
        state_lines = []
        for label in ("Phase", "Goal", "Change class", "Change document"):
            value = field_value(state, label)
            if value:
                state_lines.append(f"- **{label}**: {value}")
        for heading in ("Pending Approvals", "Blocked", "Next Action", "Last Session Summary"):
            value = section_text(state, heading)
            if value and "<!-- Add rows only" not in value:
                state_lines.append(f"\n### {heading}\n{value}")
        sections.append("\n## Current State\n" + "\n".join(state_lines))
    change = active_change(root)
    if change:
        text = change.read_text(encoding="utf-8", errors="ignore")
        change_parts = [f"\n## Active Change: {change.name}"]
        for heading in (
            "Summary",
            "Scope",
            "Dependencies",
            "Acceptance Criteria",
            "Testing",
            "Security Impact",
            "Completion Gate",
        ):
            value = section_text(text, heading)
            if value:
                change_parts.append(f"\n### {heading}\n{value}")
        sections.append("\n".join(change_parts))
    context_path = project_artifacts / "context.md"
    if context_path.is_file():
        context = context_path.read_text(encoding="utf-8", errors="ignore")
        sections.append("\n## Project Context\n" + context)
    sections.append("\n## Rules\n" + "\n".join(f"- {rule}" for rule in concise_rules()))
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


def run_legacy(script: str, arguments: list[str]) -> int:
    command = [sys.executable, str(FRAMEWORK_ROOT / "scripts" / script), *arguments]
    return subprocess.run(command, check=False).returncode


def command_check(root: Path, write: bool, as_json: bool) -> int:
    from generate_adapters import generate
    from token_report import report

    errors = validate_artifacts(root)
    config = root / "sdlc_artifacts" / "config.json"
    if config.is_file():
        try:
            config_data = json.loads(config.read_text(encoding="utf-8"))
            if config_data.get("profile") not in load_policy()["profiles"]:
                errors.append(f"{config}: unknown policy profile")
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"{config}: invalid configuration: {exc}")
    try:
        generate(check=True)
    except SystemExit as exc:
        errors.append(str(exc))
    token_data = report()
    if token_data["largest_adapter_tokens"] > token_data["adapter_budget"]:
        errors.append("An adapter exceeds the configured token budget")
    if write:
        write_index(root)
    result = {
        "ok": not errors,
        "errors": errors,
        "artifact_count": len(artifact_index(root)["artifacts"]),
        "tokens": token_data,
    }
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print("SDLC check passed." if not errors else "SDLC check failed.")
        for error in errors:
            print(f"- {error}")
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sdlc")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("next")
    context = sub.add_parser("context")
    context.add_argument("--phase")
    context.add_argument("--budget", type=int, default=2000)
    check = sub.add_parser("check")
    check.add_argument("--write-index", action="store_true")
    check.add_argument("--json", action="store_true")
    gate = sub.add_parser("gate")
    gate.add_argument("gate_name", choices=("implementation", "completion"))
    gate.add_argument("--class", dest="change_class", choices=("trivial", "standard", "high-risk"))
    gate.add_argument("--profile", choices=("lite", "standard", "regulated"))
    new = sub.add_parser("new")
    new.add_argument("artifact", choices=("change", "adr", "requirement", "review", "retrospective"))
    new.add_argument("arguments", nargs=argparse.REMAINDER)
    setup = sub.add_parser("setup")
    setup.add_argument("arguments", nargs=argparse.REMAINDER)
    sub.add_parser("verify")
    migrate = sub.add_parser("migrate")
    migrate.add_argument("--json", action="store_true")
    migrate.add_argument("--apply", action="store_true", help="Write metadata; default is a dry-run")
    migrate.add_argument("--rollback", action="store_true", help="Restore the latest metadata backup")
    migrate.add_argument("--backup", help="Specific metadata backup directory to restore")
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
        print(context_packet(root, args.phase, args.budget))
        return
    if args.command == "check":
        raise SystemExit(command_check(root, args.write_index, args.json))
    if args.command == "gate":
        gate_fn = implementation_gate if args.gate_name == "implementation" else completion_gate
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
    if args.command == "setup":
        raise SystemExit(run_legacy("setup_project.py", args.arguments))
    if args.command == "verify":
        raise SystemExit(run_legacy("verify_setup.py", []))
    if args.command == "migrate":
        if args.rollback:
            try:
                result = rollback_metadata(root, args.backup)
            except ValueError as exc:
                print(str(exc))
                raise SystemExit(1)
            print(json.dumps(result, indent=2) if args.json else f"Restored: {result['restored']}")
            return
        errors = validate_artifacts(root)
        errors = [error for error in errors if "structured metadata" not in error]
        if errors:
            print(json.dumps({"ok": False, "errors": errors}, indent=2) if args.json else "\n".join(errors))
            raise SystemExit(1)
        result = migrate_metadata(root, apply=args.apply)
        result["ok"] = True
        if args.json:
            print(json.dumps(result, indent=2))
        elif args.apply:
            print(f"Migrated {len(result['changes'])} metadata file(s).")
        else:
            print(f"Would migrate {len(result['changes'])} metadata file(s); add --apply to write.")
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
