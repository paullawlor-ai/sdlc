"""Canonical Markdown field, status, and human-approval parsing."""

from __future__ import annotations

import re

STATUS_FIELDS = {
    "change": ("Approval", "Status"),
    "requirement": ("Approval", "Status"),
    "adr": ("Status", "Current status"),
    "retrospective": ("Sign-off", "Status"),
    "review": ("Agent Recommendation", "Recommendation"),
}

KNOWN_STATUSES = (
    "Approved with notes",
    "Needs changes",
    "Implemented",
    "Superseded",
    "Proposed",
    "Approved",
    "Accepted",
    "Rejected",
    "Draft",
)

HUMAN_DECISIONS = {
    "Approved",
    "Accepted",
    "Implemented",
    "Rejected",
    "Superseded",
    "Complete",
}

PLACEHOLDER_VALUES = {
    "",
    "human | agent-reviewer",
    "human | agent-reviewer | both",
    "[name]",
    "[yyyy-mm-dd]",
}


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


def field_value(text: str, label: str) -> str | None:
    """Read one Markdown field without treating arbitrary prose as state."""
    pattern = re.compile(
        rf"(?im)^[ \t]*[-*]?[ \t]*(?:\*\*)?{re.escape(label)}"
        rf"(?:\*\*)?[ \t]*:[ \t]*(.*?)[ \t]*$"
    )
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1).strip().strip("`")
    return value.split("|")[0].strip() or None


def field_in_section(text: str, heading: str, label: str) -> str | None:
    """Read a field only from a named section, never from arbitrary prose."""
    section = section_text(text, heading)
    return field_value(section, label) if section is not None else None


def canonical_status(text: str, artifact_type: str) -> str:
    """Return the status from the one authoritative section for an artifact."""
    heading, label = STATUS_FIELDS[artifact_type]
    return field_in_section(text, heading, label) or "Unknown"


def human_dates(text: str) -> list[str]:
    """Return non-empty dates only from human-owned sections."""
    dates: list[str] = []
    for heading in ("Approval", "Status", "Sign-off"):
        value = field_in_section(text, heading, "Date")
        if value and value.strip().lower() not in PLACEHOLDER_VALUES:
            dates.append(value.strip())
    return dates


def status_declarations_outside_canonical(text: str, artifact_type: str) -> list[str]:
    """Return status-like values outside the artifact's authoritative section."""
    canonical_heading = STATUS_FIELDS[artifact_type][0].lower()
    statuses = "|".join(re.escape(value) for value in KNOWN_STATUSES)
    pattern = re.compile(rf"(?i)\b(?:current\s+)?status\s*:\s*({statuses})\b")
    current_heading = ""
    declarations: list[str] = []
    for line in text.splitlines():
        heading = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if heading:
            current_heading = heading.group(1).strip().lower()
        if current_heading == canonical_heading or line.lstrip().startswith("<!--"):
            continue
        declarations.extend(match.group(1) for match in pattern.finditer(line))
    return declarations


def protected_approval_values(text: str) -> list[str]:
    """Return normalized human-only values used by approval edit guards."""
    values: list[str] = []
    for heading in ("Approval", "Status", "Sign-off"):
        content = section_text(text, heading) or ""
        for label in ("Status", "Current status", "Sign-off"):
            value = field_value(content, label)
            if value in HUMAN_DECISIONS:
                values.append(f"{label.lower()}:{value.lower()}")
        for label in ("Approved by", "Reviewed by", "Reviewer"):
            value = field_value(content, label)
            if value and value.strip().lower() not in PLACEHOLDER_VALUES:
                values.append(f"{label.lower()}:{value.strip().lower()}")
        digest = field_value(content, "Approved source digest")
        if digest:
            values.append(f"approved source digest:{digest}")
        date = field_value(content, "Date")
        if date and date.strip().lower() not in PLACEHOLDER_VALUES:
            values.append(f"date:{date.strip().lower()}")

    for verdict in selected_review_verdicts(text):
        values.append(f"verdict:{verdict.lower()}")
    return values


def selected_review_verdicts(text: str) -> list[str]:
    """Return checked human verdicts from the canonical review section."""
    verdict = section_text(text, "Summary Verdict") or ""
    return [
        match.group(1)
        for match in re.finditer(
            r"(?im)^\s*[-*]\s*\[[xX]\]\s*"
            r"(Approved(?:\s+with\s+notes)?|Needs\s+changes|Rejected)\s*$",
            verdict,
        )
    ]
