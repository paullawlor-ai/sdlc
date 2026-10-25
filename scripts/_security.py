"""Revision-bound security evidence with no third-party runtime dependencies."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from _artifacts import Diagnostic
from _fields import field_in_section
from _readiness import _git, current_revision

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    ".quality-venv",
    "venv",
    "env",
    "ENV",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".uv-cache",
    ".uv-python",
    "sdlc_artifacts",
    ".tmp-script-artifacts",
    "htmlcov",
}
REQUIRED_SCANS = {"bandit", "detect-secrets", "pip-audit"}


def source_manifest(root: Path) -> dict[str, str]:
    """Hash project inputs, including new/deleted files and scan configuration.

    Evidence and lifecycle documents are excluded to avoid self-invalidating
    reports. Environment/build/cache directories are not product inputs.
    """
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        dirs[:] = sorted(
            name
            for name in dirs
            if name not in EXCLUDED_DIRS and not (parent / name).is_symlink()
        )
        # Virtual environments can have arbitrary names.
        dirs[:] = [
            name for name in dirs if not (parent / name / "pyvenv.cfg").is_file()
        ]
        for name in sorted(files):
            path = parent / name
            if name in {".coverage", "Thumbs.db", ".DS_Store"} or path.suffix in {
                ".pyc",
                ".log",
                ".tmp",
                ".temp",
            }:
                continue
            if path.is_symlink():
                raise ValueError(f"Scan scope contains a file symlink: {path}")
            result[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return result


def manifest_digest(manifest: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()


def security_evidence_diagnostics(
    root: Path,
    review_text: str,
    review_path: str,
    requirements: dict,
    *,
    check_freshness: bool = True,
) -> list[Diagnostic]:
    """Validate mandatory scans and freshness; exceptions are disabled by policy."""
    reference = field_in_section(
        review_text, "Evidence References", "Security evidence"
    )
    required = requirements["requires_security_review"]
    if not reference:
        return (
            [
                Diagnostic(
                    "SECURITY_EVIDENCE_REQUIRED",
                    "error",
                    "Link a security scan JSON report in Evidence References.",
                    review_path,
                )
            ]
            if required
            else []
        )
    try:
        path = (root / reference).resolve()
        path.relative_to((root / "sdlc_artifacts").resolve())
        report = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or report.get("schema_version") != 1:
            raise ValueError("unsupported security report schema")
        if report.get("risk_exceptions"):
            raise ValueError(
                "policy does not permit security risk exceptions; resolve findings"
            )
        manifest = report.get("source_manifest")
        if (
            not isinstance(manifest, dict)
            or not all(
                isinstance(name, str)
                and isinstance(digest, str)
                and re.fullmatch(r"[0-9a-f]{64}", digest)
                for name, digest in manifest.items()
            )
            or report.get("source_digest") != manifest_digest(manifest)
        ):
            raise ValueError("source manifest or digest is invalid")
        if check_freshness and source_manifest(root) != manifest:
            return [
                Diagnostic(
                    "SECURITY_EVIDENCE_STALE",
                    "error",
                    "Project inputs changed; rerun scans and refresh the review.",
                    review_path,
                )
            ]
        revision = current_revision(root)
        reviewed_revision = field_in_section(
            review_text, "Reviewed Artifacts", "Reviewed revision"
        )
        scanned_revision = report.get("revision")
        revision_valid = scanned_revision is None and revision is None
        if (
            revision
            and isinstance(scanned_revision, str)
            and re.fullmatch(r"[0-9a-f]{40,64}", scanned_revision)
        ):
            ancestor = _git(
                root, "merge-base", "--is-ancestor", scanned_revision, revision
            )
            revision_valid = (
                ancestor is not None
                and ancestor.returncode == 0
                and reviewed_revision == scanned_revision
            )
        if not revision_valid:
            return [
                Diagnostic(
                    "REVIEW_REVISION_STALE",
                    "error",
                    "Review must identify the scanned Git revision in current history.",
                    review_path,
                )
            ]
        reviewed_digest = field_in_section(
            review_text, "Reviewed Artifacts", "Reviewed source digest"
        )
        if reviewed_digest != report["source_digest"]:
            raise ValueError("review must record the scan report source_digest")
        generated = datetime.fromisoformat(report["generated_at"])
        if generated.tzinfo is None:
            raise ValueError("scan timestamp must include a timezone")
        age = (datetime.now(timezone.utc) - generated).total_seconds()
        if age < 0 or (
            check_freshness
            and age > requirements["security_evidence_max_age_days"] * 86400
        ):
            raise ValueError("scan evidence expired or has a future date; rerun scans")
        scans = report["scans"]
        if (
            not isinstance(scans, list)
            or not all(isinstance(scan, dict) for scan in scans)
            or {scan["tool"] for scan in scans} != REQUIRED_SCANS
        ):
            raise ValueError("report must contain all required security tools")
        for scan in scans:
            if not scan.get("version") or not isinstance(scan.get("scope"), list):
                raise ValueError("scan tool version and scope are required")
            if scan.get("status") != "passed" or scan.get("findings") != []:
                raise ValueError(
                    f"{scan['tool']} failed or has unresolved findings; refresh security evidence"
                )
        # Scope is derived, not trusted from a report's 'passed' label.
        expected = {
            "bandit": sorted(
                p
                for p in manifest
                if p.endswith(".py") and "tests" not in Path(p).parts
            ),
            "detect-secrets": sorted(manifest),
            "pip-audit": sorted(
                p
                for p in manifest
                if Path(p).name in {"requirements.txt", "requirements-dev.txt"}
            ),
        }
        if len(scans) != len(REQUIRED_SCANS) or any(
            scan["scope"] != expected[scan["tool"]] for scan in scans
        ):
            raise ValueError("scan scope does not cover current project inputs")
        if report.get("ok") is not True or report.get("inputs_stable") is not True:
            raise ValueError("security report did not succeed")
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, IndexError) as exc:
        return [
            Diagnostic(
                "SECURITY_EVIDENCE_INVALID",
                "error",
                f"Invalid security evidence: {exc}",
                review_path,
            )
        ]
    return []
