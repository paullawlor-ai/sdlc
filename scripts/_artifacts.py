"""Structured views and validation for human-readable SDLC artifacts."""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from dataclasses import asdict, dataclass
from pathlib import Path

from _fields import (
    STATUS_FIELDS as CANONICAL_STATUS_FIELDS,
    canonical_status,
    field_in_section,
    field_value,
    human_dates,
    section_text,
    status_declarations_outside_canonical,
)
from _policy import load_policy, project_profile

SCHEMA_VERSION = 1
STATUS_FIELDS = {
    kind: field
    for kind, (_heading, field) in CANONICAL_STATUS_FIELDS.items()
    if kind != "review"
}
VALID_STATUSES = {
    "change": {
        "Draft",
        "Proposed",
        "Approved",
        "Implemented",
        "Rejected",
        "Superseded",
    },
    "requirement": {"Draft", "Approved", "Rejected"},
    "adr": {"Draft", "Proposed", "Accepted", "Rejected", "Superseded"},
    "retrospective": {"Draft", "Accepted"},
    "review": {"Approved", "Approved with notes", "Needs changes", "Unknown"},
}

UNRESOLVED_TEMPLATE_MARKERS = (
    "What changed (1-3 sentences).",
    "Why is this needed? What risk/bug/requirement does it address?",
    "Describe the implementation at a high level.",
    "Given [context], when [action], then [result]",
    "What problem are we solving? What constraints matter",
    "Which option was chosen?",
    "Why this option wins given the decision drivers.",
    "How to revert the decision if it turns out to be wrong.",
    "Brief description of the requirement (1-2 sentences).",
)

PROPOSAL_REQUIRED_SECTIONS = {
    "change": (
        "Summary",
        "Scope",
        "Dependencies",
        "Proposed Approach",
        "Acceptance Criteria",
        "Testing",
    ),
    "adr": (
        "Context",
        "Decision Drivers",
        "Options Considered",
        "Decision",
        "Justification",
        "Consequences",
        "Security Notes",
        "Rollback / Reversal Plan",
    ),
}


@dataclass(frozen=True)
class Artifact:
    schema_version: int
    artifact_id: str
    artifact_type: str
    status: str
    path: str
    dependencies: tuple[str, ...]
    risk_class: str
    profile: str
    applicable_controls: tuple[str, ...]
    related_artifacts: tuple[str, ...]


@dataclass(frozen=True)
class Diagnostic:
    """One stable validation result suitable for humans and automation."""

    code: str
    severity: str
    message: str
    path: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return asdict(self)


def substantive_list_items(text: str | None) -> list[str]:
    """Return list items that are not empty template placeholders."""
    if not text:
        return []
    ignored = {"", "-", "n/a", "none", "no open findings"}
    items = []
    for line in text.splitlines():
        match = re.match(r"^\s*(?:[-*]|\d+[.)])\s*(.*?)\s*$", line)
        if not match:
            continue
        value = match.group(1).strip().strip("[]").strip()
        if value.lower() not in ignored and not re.fullmatch(r"\d+[.)]?", value):
            items.append(value)
    return items


def without_html_comments(text: str) -> str:
    return re.sub(r"(?s)<!--.*?-->", "", text)


def unresolved_template_markers(text: str) -> list[str]:
    """Return known scaffold prose that remains in substantive content."""
    visible = without_html_comments(text)
    return [marker for marker in UNRESOLVED_TEMPLATE_MARKERS if marker in visible]


def _raw_field_value(text: str, label: str) -> str | None:
    pattern = re.compile(
        rf"(?im)^[ \t]*[-*]?[ \t]*(?:\*\*)?{re.escape(label)}"
        rf"(?:\*\*)?[ \t]*:[ \t]*(.*?)[ \t]*$"
    )
    match = pattern.search(text)
    if not match:
        return None
    return without_html_comments(match.group(1)).strip().strip("`")


def _incomplete_value(value: str | None, *, allow_none: bool = False) -> bool:
    if value is None:
        return True
    normalized = without_html_comments(value).strip()
    if not normalized:
        return True
    lowered = normalized.lower()
    if allow_none and lowered in {"none", "n/a", "not applicable"}:
        return False
    if lowered in {"none", "n/a", "not applicable", "tbd", "todo", "-"}:
        return True
    if "|" in normalized or "xxxx" in lowered:
        return True
    return bool(
        re.search(
            r"<[^>]+>|\[(?:context|action|result|name|path|phase name)\]",
            normalized,
            re.I,
        )
    )


def _substantive_prose(text: str | None) -> bool:
    if text is None:
        return False
    visible = without_html_comments(text).strip()
    if _incomplete_value(visible):
        return False
    if unresolved_template_markers(visible):
        return False
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]*", visible)
    return len(words) >= 3


def _complete_acceptance_criteria(text: str | None) -> bool:
    if text is None:
        return False
    visible = without_html_comments(text)
    for line in visible.splitlines():
        if not re.search(r"\bAC-\d+\b", line, re.I):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        criterion = cells[1] if len(cells) > 1 else line
        if not _incomplete_value(criterion) and len(re.findall(r"\w+", criterion)) >= 4:
            return True
    return False


def _complete_adr_options(text: str | None) -> bool:
    if text is None:
        return False
    visible = without_html_comments(text)
    headings = list(re.finditer(r"(?im)^###\s+(Option\s+[^\r\n]+)\s*$", visible))
    complete = 0
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(visible)
        title = match.group(1)
        body = visible[match.end() : end]
        if _incomplete_value(title) or _incomplete_value(
            _raw_field_value(body, "Description")
        ):
            continue
        complete += 1
    return complete >= 2


def proposal_completeness_diagnostics(
    text: str, kind: str, path: str
) -> list[Diagnostic]:
    """Validate reviewable content required before a change or ADR is Proposed."""
    diagnostics: list[Diagnostic] = []
    sections: dict[str, str] = {}
    for heading in PROPOSAL_REQUIRED_SECTIONS[kind]:
        content = section_text(text, heading)
        if content is None:
            diagnostics.append(
                Diagnostic(
                    "ARTIFACT_SECTION_MISSING",
                    "error",
                    f"Required section is missing: {heading}.",
                    path,
                )
            )
        else:
            sections[heading] = content

    if kind == "change":
        for heading in ("Summary", "Proposed Approach"):
            if heading in sections and not _substantive_prose(sections[heading]):
                diagnostics.append(
                    Diagnostic(
                        "ARTIFACT_CONTENT_INCOMPLETE",
                        "error",
                        f"{heading} must contain substantive, non-template content.",
                        path,
                    )
                )
        scope = sections.get("Scope")
        if scope is not None:
            required_scope = {
                "Risk class": {"trivial", "standard", "high-risk"},
                "Policy profile": {"lite", "standard", "regulated"},
                "Components affected": None,
            }
            for label, allowed in required_scope.items():
                value = _raw_field_value(scope, label)
                invalid = _incomplete_value(value) or (
                    allowed is not None and value.lower() not in allowed
                )
                if invalid:
                    diagnostics.append(
                        Diagnostic(
                            "ARTIFACT_FIELD_INCOMPLETE",
                            "error",
                            f"Scope field must be completed: {label}.",
                            path,
                        )
                    )
        dependencies = sections.get("Dependencies")
        if dependencies is not None:
            for label in ("Blocking ADRs", "Blocking changes", "External dependencies"):
                if _incomplete_value(
                    _raw_field_value(dependencies, label), allow_none=True
                ):
                    diagnostics.append(
                        Diagnostic(
                            "ARTIFACT_FIELD_INCOMPLETE",
                            "error",
                            f"Dependencies field must name blockers or state None: {label}.",
                            path,
                        )
                    )
        if "Acceptance Criteria" in sections and not _complete_acceptance_criteria(
            sections["Acceptance Criteria"]
        ):
            diagnostics.append(
                Diagnostic(
                    "ARTIFACT_CONTENT_INCOMPLETE",
                    "error",
                    "Acceptance Criteria must include at least one concrete AC-NNN criterion.",
                    path,
                )
            )
        testing = sections.get("Testing")
        if testing is not None:
            for label in ("Unit tests", "Integration tests", "Negative / abuse cases"):
                if _incomplete_value(_raw_field_value(testing, label)):
                    diagnostics.append(
                        Diagnostic(
                            "ARTIFACT_FIELD_INCOMPLETE",
                            "error",
                            f"Testing expectation must be concrete or explain why it is not applicable: {label}.",
                            path,
                        )
                    )
    else:
        for heading in (
            "Context",
            "Decision",
            "Justification",
            "Rollback / Reversal Plan",
        ):
            if heading in sections and not _substantive_prose(sections[heading]):
                diagnostics.append(
                    Diagnostic(
                        "ARTIFACT_CONTENT_INCOMPLETE",
                        "error",
                        f"{heading} must contain substantive, non-template content.",
                        path,
                    )
                )
        drivers = sections.get("Decision Drivers")
        if drivers is not None and len(substantive_list_items(drivers)) < 2:
            diagnostics.append(
                Diagnostic(
                    "ARTIFACT_CONTENT_INCOMPLETE",
                    "error",
                    "Decision Drivers must contain at least two substantive items.",
                    path,
                )
            )
        if "Options Considered" in sections and not _complete_adr_options(
            sections["Options Considered"]
        ):
            diagnostics.append(
                Diagnostic(
                    "ARTIFACT_CONTENT_INCOMPLETE",
                    "error",
                    "Options Considered must describe at least two named options.",
                    path,
                )
            )
        consequences = sections.get("Consequences")
        if consequences is not None:
            if not substantive_list_items(
                section_text(text, "Positive")
            ) or not substantive_list_items(section_text(text, "Negative")):
                diagnostics.append(
                    Diagnostic(
                        "ARTIFACT_CONTENT_INCOMPLETE",
                        "error",
                        "Consequences must include positive and negative effects.",
                        path,
                    )
                )
        security = sections.get("Security Notes")
        if security is not None:
            for label in (
                "Threats considered",
                "Mitigations required",
                "Controls to implement",
            ):
                if _incomplete_value(_raw_field_value(security, label)):
                    diagnostics.append(
                        Diagnostic(
                            "ARTIFACT_FIELD_INCOMPLETE",
                            "error",
                            f"Security Notes field must be completed: {label}.",
                            path,
                        )
                    )
    return diagnostics


def artifact_type(path: Path) -> str | None:
    parts = {part.lower() for part in path.parts}
    name = path.name.lower()
    if "changes" in parts and re.match(r"\d{4}-", name):
        return "change"
    if "requirements" in parts and name.startswith("req-"):
        return "requirement"
    if "decisions" in parts and name.startswith("adr-"):
        return "adr"
    if "reviews" in parts and name.startswith("rev-"):
        return "review"
    if "retrospectives" in parts and name.endswith(".md"):
        return "retrospective"
    return None


def artifact_id(path: Path, kind: str) -> str:
    name = path.stem
    patterns = {
        "change": r"^(\d{4})-",
        "requirement": r"^(REQ-\d{4})-",
        "adr": r"^(ADR-\d{4})-",
        "review": r"^(REV-\d{4})-",
        "retrospective": r"^(\d{4}-\d{2}-\d{2}-iter-\d+)$",
    }
    match = re.match(patterns[kind], name, re.IGNORECASE)
    return match.group(1).upper() if match else name


def review_status(text: str) -> str:
    recommendation = canonical_status(text, "review")
    if recommendation in VALID_STATUSES["review"]:
        return recommendation
    return "Unknown"


def parse_artifact(path: Path, root: Path) -> Artifact:
    text = path.read_text(encoding="utf-8")
    kind = artifact_type(path)
    if kind is None:
        raise ValueError(f"Unsupported artifact path: {path}")
    status = review_status(text) if kind == "review" else canonical_status(text, kind)
    dependencies = tuple(sorted(set(re.findall(r"(?i)\b(?:ADR|REQ)-\d{4}\b", text))))
    risk = (field_value(text, "Risk class") or "standard").lower()
    profile = (field_value(text, "Policy profile") or "standard").lower()
    controls = tuple(sorted(set(re.findall(r"(?i)\b[ASVC]\d+\b", text))))
    related = tuple(
        sorted(
            set(re.findall(r"(?i)\b(?:(?:ADR|REQ|REV)-\d{4}|Change\s+\d{4})\b", text))
        )
    )
    return Artifact(
        schema_version=SCHEMA_VERSION,
        artifact_id=artifact_id(path, kind),
        artifact_type=kind,
        status=status,
        path=path.relative_to(root).as_posix(),
        dependencies=dependencies,
        risk_class=risk,
        profile=profile,
        applicable_controls=controls,
        related_artifacts=related,
    )


def metadata_root(root: Path) -> Path:
    return root / "sdlc_artifacts" / ".sdlc" / "metadata"


def project_metadata_mode(root: Path) -> str:
    value = configured_metadata_mode(root)
    return value if value in {"compatibility", "required"} else "compatibility"


def configured_metadata_mode(root: Path) -> object | None:
    """Return the configured value verbatim so validation can reject typos."""
    config = root / "sdlc_artifacts" / "config.json"
    if not config.is_file():
        return None
    try:
        return json.loads(config.read_text(encoding="utf-8")).get("metadata_mode")
    except (json.JSONDecodeError, OSError):
        return None


def metadata_path(root: Path, artifact: Artifact) -> Path:
    return metadata_root(root) / f"{artifact.artifact_type}-{artifact.artifact_id}.json"


def _metadata_payload(artifact: Artifact) -> dict:
    payload = asdict(artifact)
    payload["dependencies"] = list(artifact.dependencies)
    payload["applicable_controls"] = list(artifact.applicable_controls)
    payload["related_artifacts"] = list(artifact.related_artifacts)
    return payload


def _atomic_write(path: Path, content: str) -> None:
    temporary = path.with_name(path.name + ".sdlc-tmp")
    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def migrate_metadata(
    root: Path, *, apply: bool = False, target_mode: str | None = None
) -> dict:
    """Plan or atomically snapshot and write metadata, index, and mode config."""
    if target_mode not in {None, "compatibility", "required"}:
        raise ValueError(f"Invalid metadata mode: {target_mode}")
    artifacts = collect_artifacts(root)
    changes: list[str] = []
    writes: list[tuple[Path, str]] = []
    for artifact in artifacts:
        destination = metadata_path(root, artifact)
        content = json.dumps(_metadata_payload(artifact), indent=2) + "\n"
        current = (
            destination.read_text(encoding="utf-8") if destination.is_file() else None
        )
        if current != content:
            changes.append(destination.relative_to(root).as_posix())
            writes.append((destination, content))
    config = root / "sdlc_artifacts" / "config.json"
    configured = configured_metadata_mode(root)
    mode_change = target_mode is not None and configured != target_mode
    config_data = None
    if mode_change:
        try:
            config_data = (
                json.loads(config.read_text(encoding="utf-8"))
                if config.is_file()
                else {"schema_version": SCHEMA_VERSION, "profile": "standard"}
            )
        except (json.JSONDecodeError, OSError) as exc:
            raise ValueError(
                f"Cannot update invalid project configuration: {exc}"
            ) from exc
    backup = None
    if apply and (writes or mode_change):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = root / "sdlc_artifacts" / ".sdlc" / "backups" / timestamp
        existing = metadata_root(root)
        index = root / "sdlc_artifacts" / "index.json"
        backup_dir.mkdir(parents=True, exist_ok=False)
        snapshot = {
            "schema_version": SCHEMA_VERSION,
            "metadata_existed": existing.is_dir(),
            "index_existed": index.is_file(),
            "config_existed": config.is_file(),
        }
        if existing.is_dir():
            backup = backup_dir / "metadata"
            shutil.copytree(existing, backup)
        if index.is_file():
            shutil.copy2(index, backup_dir / "index.json")
        if config.is_file():
            shutil.copy2(config, backup_dir / "config.json")
        (backup_dir / "snapshot.json").write_text(
            json.dumps(snapshot, indent=2) + "\n", encoding="utf-8"
        )
        backup = backup_dir
        for destination, content in writes:
            destination.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write(destination, content)
        if mode_change:
            assert config_data is not None
            config_data["metadata_mode"] = target_mode
            config.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write(config, json.dumps(config_data, indent=2) + "\n")
        write_index(root)
    return {
        "schema_version": SCHEMA_VERSION,
        "applied": apply,
        "artifacts": len(artifacts),
        "changes": changes,
        "mode": target_mode or project_metadata_mode(root),
        "mode_change": mode_change,
        "backup": str(backup) if backup else None,
    }


def initialize_metadata(root: Path) -> None:
    """Create an empty managed metadata store for a newly configured project."""
    metadata_root(root).mkdir(parents=True, exist_ok=True)
    write_index(root)


def sync_artifact_metadata(root: Path, path: Path) -> None:
    """Update one derived sidecar without masking drift in other artifacts."""
    artifact = parse_artifact(path, root)
    destination = metadata_path(root, artifact)
    destination.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(destination, json.dumps(_metadata_payload(artifact), indent=2) + "\n")
    write_index(root)


def rollback_metadata(root: Path, backup: str | None = None) -> dict:
    backups = root / "sdlc_artifacts" / ".sdlc" / "backups"
    selected = Path(backup) if backup else None
    if selected is None:
        candidates = (
            sorted(path for path in backups.iterdir() if path.is_dir())
            if backups.is_dir()
            else []
        )
        selected = candidates[-1] if candidates else None
    if selected is None or not selected.is_dir():
        raise ValueError("No metadata backup is available to restore")
    snapshot_path = selected / "snapshot.json"
    if snapshot_path.is_file():
        try:
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise ValueError(f"Invalid metadata backup snapshot: {exc}") from exc
        destination = metadata_root(root)
        if destination.exists():
            shutil.rmtree(destination)
        if snapshot.get("metadata_existed"):
            shutil.copytree(selected / "metadata", destination)
        artifacts = root / "sdlc_artifacts"
        restored: list[str] = []
        for name, existed in (
            ("index.json", snapshot.get("index_existed")),
            ("config.json", snapshot.get("config_existed")),
        ):
            target = artifacts / name
            source = selected / name
            if existed:
                shutil.copy2(source, target)
                restored.append(target.relative_to(root).as_posix())
            else:
                target.unlink(missing_ok=True)
        if snapshot.get("metadata_existed"):
            restored.append(destination.relative_to(root).as_posix())
        return {"restored": str(selected), "paths": restored}

    # Backward-compatible restore for pre-snapshot metadata-only backups.
    if selected.name != "metadata" and (selected / "metadata").is_dir():
        selected = selected / "metadata"
    destination = metadata_root(root)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(selected, destination)
    write_index(root)
    return {"restored": str(selected), "destination": str(destination)}


def collect_artifacts(root: Path) -> list[Artifact]:
    artifact_root = root / "sdlc_artifacts"
    if not artifact_root.is_dir():
        return []
    artifacts = []
    for path in sorted(artifact_root.rglob("*.md")):
        if artifact_type(path):
            artifacts.append(parse_artifact(path, root))
    return artifacts


def _artifact_error_diagnostics(root: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    seen: dict[str, str] = {}
    try:
        artifacts = collect_artifacts(root)
    except (OSError, UnicodeError, ValueError) as exc:
        return [Diagnostic("ARTIFACT_READ_ERROR", "error", str(exc))]
    ids = {artifact.artifact_id for artifact in artifacts}
    if project_metadata_mode(root) == "required" and not metadata_root(root).is_dir():
        diagnostics.append(
            Diagnostic(
                "METADATA_REQUIRED",
                "error",
                "Required structured metadata is not initialized; "
                "run `sdlc metadata sync --apply`",
                "sdlc_artifacts/.sdlc/metadata",
            )
        )
    for artifact in artifacts:
        if artifact.artifact_id in seen:
            diagnostics.append(
                Diagnostic(
                    "DUPLICATE_ARTIFACT_ID",
                    "error",
                    f"Duplicate artifact ID {artifact.artifact_id}: "
                    f"{seen[artifact.artifact_id]} and {artifact.path}",
                    artifact.path,
                )
            )
        seen[artifact.artifact_id] = artifact.path
        allowed = VALID_STATUSES[artifact.artifact_type]
        if artifact.status not in allowed:
            diagnostics.append(
                Diagnostic(
                    "INVALID_ARTIFACT_STATUS",
                    "error",
                    f"{artifact.path}: invalid {artifact.artifact_type} status "
                    f"'{artifact.status}'",
                    artifact.path,
                )
            )
        if artifact.risk_class not in {"trivial", "standard", "high-risk"}:
            diagnostics.append(
                Diagnostic(
                    "INVALID_RISK_CLASS",
                    "error",
                    f"{artifact.path}: invalid risk class '{artifact.risk_class}'",
                    artifact.path,
                )
            )
        if artifact.profile not in {"lite", "standard", "regulated"}:
            diagnostics.append(
                Diagnostic(
                    "INVALID_POLICY_PROFILE",
                    "error",
                    f"{artifact.path}: invalid policy profile '{artifact.profile}'",
                    artifact.path,
                )
            )
        path_parts = Path(artifact.path).parts
        if (
            artifact.artifact_type == "adr"
            and "accepted" in path_parts
            and artifact.status != "Accepted"
        ):
            diagnostics.append(
                Diagnostic(
                    "ADR_FOLDER_STATUS_MISMATCH",
                    "error",
                    f"{artifact.path}: ADR in accepted folder must have Accepted status",
                    artifact.path,
                )
            )
        if (
            artifact.artifact_type == "adr"
            and "proposed" in path_parts
            and artifact.status not in {"Draft", "Proposed"}
        ):
            diagnostics.append(
                Diagnostic(
                    "ADR_FOLDER_STATUS_MISMATCH",
                    "error",
                    f"{artifact.path}: ADR in proposed folder must have Draft or Proposed status",
                    artifact.path,
                )
            )
        if artifact.status != "Draft":
            artifact_text = (root / artifact.path).read_text(encoding="utf-8")
            markers = unresolved_template_markers(artifact_text)
            if markers:
                diagnostics.append(
                    Diagnostic(
                        "ARTIFACT_PLACEHOLDER",
                        "error",
                        f"{artifact.path}: unresolved template placeholder: {markers[0]}",
                        artifact.path,
                    )
                )
            if (
                artifact.artifact_type in PROPOSAL_REQUIRED_SECTIONS
                and artifact.status in VALID_STATUSES[artifact.artifact_type]
            ):
                diagnostics.extend(
                    proposal_completeness_diagnostics(
                        artifact_text, artifact.artifact_type, artifact.path
                    )
                )
        for dependency in artifact.dependencies:
            if dependency not in ids:
                diagnostics.append(
                    Diagnostic(
                        "UNRESOLVED_DEPENDENCY",
                        "error",
                        f"{artifact.path}: unresolved dependency {dependency}",
                        artifact.path,
                    )
                )
        sidecar = metadata_path(root, artifact)
        if metadata_root(root).is_dir():
            if not sidecar.is_file():
                diagnostics.append(
                    Diagnostic(
                        "METADATA_MISSING",
                        "error",
                        f"{artifact.path}: missing structured metadata",
                        artifact.path,
                    )
                )
            else:
                try:
                    recorded = json.loads(sidecar.read_text(encoding="utf-8"))
                    if recorded != _metadata_payload(artifact):
                        diagnostics.append(
                            Diagnostic(
                                "METADATA_STALE",
                                "error",
                                f"{artifact.path}: structured metadata is stale",
                                artifact.path,
                            )
                        )
                except (json.JSONDecodeError, OSError) as exc:
                    diagnostics.append(
                        Diagnostic(
                            "METADATA_INVALID",
                            "error",
                            f"{sidecar}: invalid structured metadata: {exc}",
                            sidecar.relative_to(root).as_posix(),
                        )
                    )
    if metadata_root(root).is_dir():
        expected = {metadata_path(root, artifact).resolve() for artifact in artifacts}
        for sidecar in sorted(metadata_root(root).glob("*.json")):
            if sidecar.resolve() not in expected:
                diagnostics.append(
                    Diagnostic(
                        "METADATA_ORPHANED",
                        "error",
                        f"{sidecar}: orphaned structured metadata",
                        sidecar.relative_to(root).as_posix(),
                    )
                )
    return diagnostics


def validate_artifacts(root: Path) -> list[str]:
    """Return blocking validation messages for legacy callers."""
    return [item.message for item in _artifact_error_diagnostics(root)]


def _context_surface(text: str, artifact_type: str) -> str:
    """Return only the sections eligible for ordinary assistant context."""
    if artifact_type == "requirement":
        headings = ("Summary",)
    elif artifact_type == "adr":
        headings = ("Decision Summary",)
        if section_text(text, "Decision Summary") is None:
            headings = ("Decision", "Consequences")
    elif artifact_type == "change":
        headings = (
            "Summary",
            "Scope",
            "Dependencies",
            "Acceptance Criteria",
            "Testing",
            "Security Impact",
            "Completion Gate",
        )
    elif artifact_type == "review":
        headings = ("Reviewed Artifacts", "Agent Recommendation", "Must-Fix")
    elif artifact_type == "test_summary":
        headings = ("Overview", "Acceptance Criteria Mapping", "Risks and Mitigations")
    else:
        return text
    selected = []
    for heading in headings:
        value = section_text(text, heading)
        if value:
            selected.append(f"## {heading}\n{value}")
    return "\n\n".join(selected)


def _token_measurement(
    path: Path, root: Path, artifact_type: str, budget: dict
) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    context = (
        text if artifact_type == "state" else _context_surface(text, artifact_type)
    )
    context_tokens = (len(context) + 3) // 4
    return {
        "path": path.relative_to(root).as_posix(),
        "artifact_type": artifact_type,
        "approx_tokens": context_tokens,
        "context_approx_tokens": context_tokens,
        "total_approx_tokens": (len(text) + 3) // 4,
        "measurement_scope": "complete artifact"
        if artifact_type == "state"
        else "default context surface",
        "target_tokens": budget["target"],
        "warning_tokens": budget["warning"],
        "enforcement": budget.get("enforcement", "regulated"),
    }


def artifact_token_report(root: Path) -> list[dict[str, object]]:
    """Measure total size and the smaller surface eligible for default context."""
    budgets = load_policy().get("artifact_context_budgets", {})
    measured: list[dict[str, object]] = []
    seen: set[Path] = set()
    for artifact in collect_artifacts(root):
        path = root / artifact.path
        seen.add(path.resolve())
        budget = budgets.get(artifact.artifact_type)
        if not budget:
            continue
        measured.append(_token_measurement(path, root, artifact.artifact_type, budget))

    state = root / "sdlc_artifacts" / "STATE.md"
    if state.is_file() and "state" in budgets:
        budget = budgets["state"]
        measured.append(_token_measurement(state, root, "state", budget))

    artifact_root = root / "sdlc_artifacts"
    if artifact_root.is_dir() and "test_summary" in budgets:
        budget = budgets["test_summary"]
        for path in sorted(artifact_root.rglob("*.md")):
            normalized = path.stem.lower().replace("_", "-")
            if path.resolve() in seen or not any(
                name in normalized for name in ("test-summary", "test-results")
            ):
                continue
            measured.append(_token_measurement(path, root, "test_summary", budget))
    return measured


def validate_diagnostics(root: Path) -> list[Diagnostic]:
    """Return errors plus non-blocking artifact quality diagnostics."""
    diagnostics = _artifact_error_diagnostics(root)
    try:
        artifacts = collect_artifacts(root)
    except (OSError, UnicodeError, ValueError):
        return diagnostics

    configured_mode = configured_metadata_mode(root)
    if configured_mode not in {None, "compatibility", "required"}:
        diagnostics.append(
            Diagnostic(
                "CONFIG_METADATA_MODE_INVALID",
                "error",
                "metadata_mode must be 'compatibility' or 'required'; "
                f"found {configured_mode!r}.",
                "sdlc_artifacts/config.json",
            )
        )
    if (
        artifacts
        and configured_mode in {None, "compatibility"}
        and not metadata_root(root).is_dir()
    ):
        diagnostics.append(
            Diagnostic(
                "METADATA_COMPATIBILITY_MODE",
                "warning",
                "Artifacts are using Markdown compatibility mode; run "
                "`sdlc metadata sync --apply` to create sidecars and adopt required mode.",
                "sdlc_artifacts/config.json",
            )
        )

    for artifact in artifacts:
        path = root / artifact.path
        text = path.read_text(encoding="utf-8")
        for date in human_dates(text):
            if date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                diagnostics.append(
                    Diagnostic(
                        "NON_ISO_APPROVAL_DATE",
                        "warning",
                        "Human-owned approval dates should use YYYY-MM-DD; "
                        f"found '{date}'.",
                        artifact.path,
                    )
                )
                break

        outside_statuses = status_declarations_outside_canonical(
            text, artifact.artifact_type
        )
        conflicts = sorted(
            {value for value in outside_statuses if value != artifact.status}
        )
        if conflicts:
            diagnostics.append(
                Diagnostic(
                    "STATUS_CONFLICT",
                    "warning",
                    f"Canonical status is '{artifact.status}', but status-like text "
                    f"elsewhere declares {', '.join(conflicts)}.",
                    artifact.path,
                )
            )
    regulated = project_profile(root) == "regulated"
    for measurement in artifact_token_report(root):
        if measurement["approx_tokens"] <= measurement["warning_tokens"]:
            continue
        kind = measurement["artifact_type"]
        code = (
            "STATE_CONTEXT_OVERSIZE" if kind == "state" else "ARTIFACT_CONTEXT_OVERSIZE"
        )
        enforcement = measurement["enforcement"]
        if enforcement == "informational":
            severity = "info"
        else:
            severity = "error" if regulated else "warning"
        diagnostics.append(
            Diagnostic(
                code,
                severity,
                f"{kind} default context surface is approximately "
                f"{measurement['context_approx_tokens']} tokens "
                f"({measurement['total_approx_tokens']} total); "
                f"target {measurement['target_tokens']} and warning threshold "
                f"{measurement['warning_tokens']}. Preserve authoritative detail; "
                "consider shortening the summary, removing duplication, or splitting "
                "focused child artifacts with stable links.",
                str(measurement["path"]),
            )
        )
    return diagnostics


def propose_artifact(root: Path, path: Path) -> list[Diagnostic]:
    """Promote a complete Draft change or ADR to Proposed atomically."""
    resolved = path if path.is_absolute() else root / path
    try:
        # Windows may spell the same root with either short or long names.
        root = root.resolve()
        resolved = resolved.resolve(strict=True)
        resolved.relative_to((root / "sdlc_artifacts").resolve())
    except (OSError, ValueError):
        return [
            Diagnostic(
                "ARTIFACT_PATH_INVALID",
                "error",
                "Artifact must exist beneath sdlc_artifacts.",
                str(path),
            )
        ]
    kind = artifact_type(resolved)
    if kind not in {"change", "adr"}:
        return [
            Diagnostic(
                "ARTIFACT_TYPE_INVALID",
                "error",
                "Only Draft changes and ADRs can be proposed.",
                resolved.relative_to(root).as_posix(),
            )
        ]
    text = resolved.read_text(encoding="utf-8")
    heading = "Status" if kind == "adr" else "Approval"
    label = STATUS_FIELDS[kind]
    if field_in_section(text, heading, label) != "Draft":
        return [
            Diagnostic(
                "ARTIFACT_NOT_DRAFT",
                "error",
                "Only an artifact with canonical status Draft can be proposed.",
                resolved.relative_to(root).as_posix(),
            )
        ]
    markers = unresolved_template_markers(text)
    if markers:
        return [
            Diagnostic(
                "ARTIFACT_PLACEHOLDER",
                "error",
                f"Replace scaffold content before proposing: {markers[0]}",
                resolved.relative_to(root).as_posix(),
            )
        ]
    completeness = proposal_completeness_diagnostics(
        text, kind, resolved.relative_to(root).as_posix()
    )
    if completeness:
        return completeness
    status_pattern = re.compile(
        rf"(?im)^(\s*[-*]?\s*(?:\*\*)?{re.escape(label)}(?:\*\*)?\s*:\s*)Draft\s*$"
    )
    candidate, count = status_pattern.subn(r"\1Proposed", text, count=1)
    if count != 1:
        return [
            Diagnostic(
                "ARTIFACT_STATUS_INVALID",
                "error",
                "Could not update canonical Draft status.",
            )
        ]
    _atomic_write(resolved, candidate)
    if metadata_root(root).is_dir():
        sync_artifact_metadata(root, resolved)
    return []


def artifact_index(root: Path) -> dict:
    artifacts = collect_artifacts(root)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifacts": [asdict(artifact) for artifact in artifacts],
        "approval_queue": [
            asdict(artifact)
            for artifact in artifacts
            if artifact.artifact_type in {"change", "adr"}
            and artifact.status == "Proposed"
        ],
    }


def write_index(root: Path) -> Path:
    destination = root / "sdlc_artifacts" / "index.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(destination, json.dumps(artifact_index(root), indent=2) + "\n")
    return destination
