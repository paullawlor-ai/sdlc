"""Structured views and validation for human-readable SDLC artifacts."""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from dataclasses import asdict, dataclass
from pathlib import Path

SCHEMA_VERSION = 1
STATUS_FIELDS = {
    "change": "Status",
    "requirement": "Status",
    "adr": "Current status",
    "retrospective": "Status",
}
VALID_STATUSES = {
    "change": {"Proposed", "Approved", "Implemented", "Rejected", "Superseded"},
    "requirement": {"Draft", "Approved", "Rejected"},
    "adr": {"Proposed", "Accepted", "Rejected", "Superseded"},
    "retrospective": {"Draft", "Accepted"},
    "review": {"Approved", "Approved with notes", "Needs changes", "Unknown"},
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


def field_value(text: str, label: str) -> str | None:
    """Read one Markdown field without treating arbitrary prose as state."""
    pattern = re.compile(
        rf"(?im)^\s*[-*]?\s*(?:\*\*)?{re.escape(label)}(?:\*\*)?\s*:\s*(.+?)\s*$"
    )
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1).strip().strip("`")
    return value.split("|")[0].strip()


def section_text(text: str, heading: str) -> str | None:
    """Return one exact Markdown section, stopping at its next peer heading."""
    lines = text.splitlines()
    target = heading.strip().lower()
    start = None
    level = 0
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match and match.group(2).strip().lower() == target:
            start = index + 1
            level = len(match.group(1))
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start, len(lines)):
        match = re.match(r"^(#{1,6})\s+", lines[index])
        if match and len(match.group(1)) <= level:
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def field_in_section(text: str, heading: str, label: str) -> str | None:
    """Read a field only from a named section, never from arbitrary prose."""
    section = section_text(text, heading)
    return field_value(section, label) if section is not None else None


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
    recommendation = field_in_section(text, "Agent Recommendation", "Recommendation")
    if recommendation in VALID_STATUSES["review"]:
        return recommendation
    return "Unknown"


def parse_artifact(path: Path, root: Path) -> Artifact:
    text = path.read_text(encoding="utf-8")
    kind = artifact_type(path)
    if kind is None:
        raise ValueError(f"Unsupported artifact path: {path}")
    if kind == "review":
        status = review_status(text)
    else:
        section = "Status" if kind == "adr" else "Sign-off" if kind == "retrospective" else "Approval"
        status = field_in_section(text, section, STATUS_FIELDS[kind]) or "Unknown"
    dependencies = tuple(sorted(set(re.findall(r"(?i)\b(?:ADR|REQ)-\d{4}\b", text))))
    risk = (field_value(text, "Risk class") or "standard").lower()
    profile = (field_value(text, "Policy profile") or "standard").lower()
    controls = tuple(sorted(set(re.findall(r"(?i)\b[ASVC]\d+\b", text))))
    related = tuple(sorted(set(re.findall(r"(?i)\b(?:(?:ADR|REQ|REV)-\d{4}|Change\s+\d{4})\b", text))))
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


def migrate_metadata(root: Path, *, apply: bool = False) -> dict:
    """Plan or write versioned per-artifact metadata, backing up replaced data."""
    artifacts = collect_artifacts(root)
    changes: list[str] = []
    writes: list[tuple[Path, str]] = []
    for artifact in artifacts:
        destination = metadata_path(root, artifact)
        content = json.dumps(_metadata_payload(artifact), indent=2) + "\n"
        current = destination.read_text(encoding="utf-8") if destination.is_file() else None
        if current != content:
            changes.append(destination.relative_to(root).as_posix())
            writes.append((destination, content))
    backup = None
    if apply and writes:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_dir = root / "sdlc_artifacts" / ".sdlc" / "backups" / timestamp
        existing = metadata_root(root)
        if existing.is_dir():
            backup = backup_dir / "metadata"
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(existing, backup)
        for destination, content in writes:
            destination.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write(destination, content)
        write_index(root)
    return {
        "schema_version": SCHEMA_VERSION,
        "applied": apply,
        "artifacts": len(artifacts),
        "changes": changes,
        "backup": str(backup) if backup else None,
    }


def rollback_metadata(root: Path, backup: str | None = None) -> dict:
    backups = root / "sdlc_artifacts" / ".sdlc" / "backups"
    selected = Path(backup) if backup else None
    if selected is None:
        candidates = sorted(backups.glob("*/metadata")) if backups.is_dir() else []
        selected = candidates[-1] if candidates else None
    if selected is None or not selected.is_dir():
        raise ValueError("No metadata backup is available to restore")
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


def validate_artifacts(root: Path) -> list[str]:
    errors: list[str] = []
    seen: dict[str, str] = {}
    try:
        artifacts = collect_artifacts(root)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)]
    ids = {artifact.artifact_id for artifact in artifacts}
    for artifact in artifacts:
        if artifact.artifact_id in seen:
            errors.append(
                f"Duplicate artifact ID {artifact.artifact_id}: "
                f"{seen[artifact.artifact_id]} and {artifact.path}"
            )
        seen[artifact.artifact_id] = artifact.path
        allowed = VALID_STATUSES[artifact.artifact_type]
        if artifact.status not in allowed:
            errors.append(
                f"{artifact.path}: invalid {artifact.artifact_type} status "
                f"'{artifact.status}'"
            )
        if artifact.risk_class not in {"trivial", "standard", "high-risk"}:
            errors.append(f"{artifact.path}: invalid risk class '{artifact.risk_class}'")
        if artifact.profile not in {"lite", "standard", "regulated"}:
            errors.append(f"{artifact.path}: invalid policy profile '{artifact.profile}'")
        path_parts = Path(artifact.path).parts
        if artifact.artifact_type == "adr" and "accepted" in path_parts and artifact.status != "Accepted":
            errors.append(f"{artifact.path}: ADR in accepted folder must have Accepted status")
        if artifact.artifact_type == "adr" and "proposed" in path_parts and artifact.status != "Proposed":
            errors.append(f"{artifact.path}: ADR in proposed folder must have Proposed status")
        for dependency in artifact.dependencies:
            if dependency not in ids:
                errors.append(f"{artifact.path}: unresolved dependency {dependency}")
        sidecar = metadata_path(root, artifact)
        if metadata_root(root).is_dir():
            if not sidecar.is_file():
                errors.append(f"{artifact.path}: missing structured metadata")
            else:
                try:
                    recorded = json.loads(sidecar.read_text(encoding="utf-8"))
                    if recorded != _metadata_payload(artifact):
                        errors.append(f"{artifact.path}: structured metadata is stale")
                except (json.JSONDecodeError, OSError) as exc:
                    errors.append(f"{sidecar}: invalid structured metadata: {exc}")
    if metadata_root(root).is_dir():
        expected = {metadata_path(root, artifact).resolve() for artifact in artifacts}
        for sidecar in metadata_root(root).glob("*.json"):
            if sidecar.resolve() not in expected:
                errors.append(f"{sidecar}: orphaned structured metadata")
    return errors


def artifact_index(root: Path) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifacts": [asdict(artifact) for artifact in collect_artifacts(root)],
    }


def write_index(root: Path) -> Path:
    destination = root / "sdlc_artifacts" / "index.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(destination, json.dumps(artifact_index(root), indent=2) + "\n")
    return destination
