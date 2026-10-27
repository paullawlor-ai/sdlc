"""Repository and local-environment readiness without external dependencies."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPOSITORY_MODES = {"auto", "git", "non-git"}


def repository_mode(root: Path) -> object:
    config = root / "sdlc_artifacts" / "config.json"
    if not config.is_file():
        return "auto"
    try:
        return json.loads(config.read_text(encoding="utf-8")).get(
            "repository_mode", "auto"
        )
    except (json.JSONDecodeError, OSError):
        return "auto"


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str] | None:
    executable = shutil.which("git")
    if not executable:
        return None
    try:
        return subprocess.run(
            [executable, *arguments],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def git_state(root: Path) -> dict[str, object]:
    """Return Git availability, baseline, and SDLC evidence durability."""
    mode = repository_mode(root)
    result: dict[str, object] = {
        "mode": mode,
        "git_available": shutil.which("git") is not None,
        "is_repository": False,
        "repository_root": None,
        "baseline_commit": None,
        "evidence_untracked": [],
        "evidence_modified": [],
    }
    if mode == "non-git":
        return result
    repository = _git(root, "rev-parse", "--show-toplevel")
    if repository is None or repository.returncode != 0:
        return result
    result["is_repository"] = True
    result["repository_root"] = repository.stdout.strip()
    revision = _git(root, "rev-parse", "--verify", "HEAD")
    if revision is not None and revision.returncode == 0:
        result["baseline_commit"] = revision.stdout.strip()
    status = _git(
        root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        "sdlc_artifacts",
    )
    if status is not None and status.returncode == 0:
        untracked: list[str] = []
        modified: list[str] = []
        for line in status.stdout.splitlines():
            if not line.strip():
                continue
            path = line[3:].strip()
            if line.startswith("??"):
                untracked.append(path)
            else:
                modified.append(path)
        result["evidence_untracked"] = untracked
        result["evidence_modified"] = modified
    return result


def current_revision(root: Path) -> str | None:
    revision = git_state(root).get("baseline_commit")
    return str(revision) if revision else None


def fixed_pytest_basetemps(root: Path) -> list[dict[str, str]]:
    """Find fixed pytest base-temp settings that can collide across runs."""
    findings: list[dict[str, str]] = []
    for name in ("pyproject.toml", "pytest.ini", "setup.cfg", "tox.ini"):
        path = root / name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        pattern = r"""(?im)--basetemp(?:=|[ \t]+)(?:"([^"]+)"|'([^']+)'|([^\s]+))"""
        for match in re.finditer(pattern, text):
            value = next(group for group in match.groups() if group is not None).strip()
            if any(marker in value for marker in ("{", "}", "$", "%")):
                continue
            findings.append({"path": path.relative_to(root).as_posix(), "value": value})
    return findings


def doctor_report(root: Path) -> dict[str, object]:
    """Return deterministic environment diagnostics and a usable Python command."""
    project_write_error = None
    try:
        descriptor, probe = tempfile.mkstemp(prefix=".sdlc-write-", dir=root)
        os.close(descriptor)
        os.unlink(probe)
        project_writable = True
    except OSError as exc:
        project_writable = False
        project_write_error = str(exc)

    temporary_error = None
    temporary_path = None
    try:
        with tempfile.TemporaryDirectory(prefix="sdlc-doctor-") as directory:
            temporary_path = directory
            Path(directory, "probe").write_text("ok", encoding="utf-8")
        temporary_writable = True
    except OSError as exc:
        temporary_writable = False
        temporary_error = str(exc)

    fixed = fixed_pytest_basetemps(root)
    return {
        "ok": project_writable and temporary_writable,
        "python": {
            "executable": sys.executable,
            "command": f'"{sys.executable}"',
            "version": ".".join(str(item) for item in sys.version_info[:3]),
            "virtual_environment": sys.prefix != sys.base_prefix,
            "prefix": sys.prefix,
            "base_prefix": sys.base_prefix,
        },
        "project": {
            "root": str(root),
            "writable": project_writable,
            "error": project_write_error,
        },
        "temporary_directory": {
            "path": temporary_path,
            "writable": temporary_writable,
            "error": temporary_error,
            "unique_per_run": True,
        },
        "git": git_state(root),
        "fixed_pytest_basetemps": fixed,
    }
