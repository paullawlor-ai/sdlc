#!/usr/bin/env python3
"""Run security tools and write fail-closed, revision-bound JSON evidence.

Run with the development environment interpreter. Tool dependencies are optional
for framework use but mandatory for this command. Reports never contain source
lines or plaintext secrets. Dependency auditing requires network access.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from _readiness import current_revision
from _security import manifest_digest, source_manifest


def run_tool(
    root: Path, module: str, arguments: list[str]
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", module, *arguments],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )


def parse_findings(tool: str, payload: object) -> list[dict]:
    """Keep identifiers and locations, never source snippets or secret values."""
    if not isinstance(payload, dict):
        raise ValueError("Scanner output must be a JSON object")
    if tool == "bandit":
        if not isinstance(payload.get("results"), list):
            raise ValueError("Bandit results are missing")
        if payload.get("errors"):
            raise ValueError("Bandit could not scan every input")
        return [
            {
                "id": item["test_id"],
                "path": item["filename"],
                "line": item["line_number"],
                "severity": item["issue_severity"],
            }
            for item in payload["results"]
        ]
    if tool == "detect-secrets":
        if not isinstance(payload.get("results"), dict):
            raise ValueError("Secret scanner results are missing")
        return [
            {"id": item["type"], "path": path, "line": item["line_number"]}
            for path, items in payload["results"].items()
            for item in items
        ]
    if payload.get("fixes"):
        raise ValueError("Unexpected dependency modifications")
    findings = []
    for dependency in payload["dependencies"]:
        if dependency.get("skip_reason"):
            raise ValueError("A dependency could not be audited")
        findings.extend(
            {
                "id": vulnerability["id"],
                "package": dependency["name"],
                "version": dependency["version"],
                "fix_versions": vulnerability.get("fix_versions", []),
            }
            for vulnerability in dependency["vulns"]
        )
    return findings


def scan_project(root: Path) -> dict:
    manifest = source_manifest(root)
    revision = current_revision(root)
    scopes = {
        "bandit": sorted(
            p for p in manifest if p.endswith(".py") and "tests" not in Path(p).parts
        ),
        "detect-secrets": sorted(manifest),
        "pip-audit": sorted(
            p
            for p in manifest
            if Path(p).name in {"requirements.txt", "requirements-dev.txt"}
        ),
    }
    scans = []
    for tool, scope in scopes.items():
        scan = {
            "tool": tool,
            "version": None,
            "scope": scope,
            "status": "failed",
            "findings": [],
        }
        try:
            scan["version"] = importlib.metadata.version(tool)
            if tool == "bandit":
                # Chunk filenames to stay below Windows command-line limits.
                commands = [
                    (
                        "bandit",
                        [
                            "-f",
                            "json",
                            "-ll",
                            "-ii",
                            "--ignore-nosec",
                            *("./" + path for path in scope[i : i + 50]),
                        ],
                    )
                    for i in range(0, len(scope), 50)
                ]
            elif tool == "detect-secrets":
                commands = [
                    (
                        "detect_secrets",
                        [
                            "scan",
                            "--all-files",
                            "--no-verify",
                            *("./" + path for path in scope[i : i + 50]),
                        ],
                    )
                    for i in range(0, len(scope), 50)
                ]
            else:
                # Audit each starter independently to avoid mixing incompatible environments.
                commands = [
                    (
                        "pip_audit",
                        [
                            "--strict",
                            "--progress-spinner",
                            "off",
                            "-f",
                            "json",
                            "-r",
                            path,
                        ],
                    )
                    for path in scope
                ]
            for module, arguments in commands:
                result = run_tool(root, module, arguments)
                if result.returncode not in (
                    {0} if tool == "detect-secrets" else {0, 1}
                ):
                    raise ValueError(
                        "scanner execution failed (see tool locally for details)"
                    )
                payload = json.loads(result.stdout)
                findings = parse_findings(tool, payload)
                if result.returncode != 0 and not findings:
                    raise ValueError("nonzero scanner exit without a finding report")
                scan["findings"].extend(findings)
                if tool == "pip-audit":
                    for finding in findings:
                        finding["requirements"] = arguments[-1]
                    scan.setdefault("resolved_dependencies", []).append(
                        {
                            "requirements": arguments[-1],
                            "packages": [
                                {"name": item["name"], "version": item["version"]}
                                for item in payload["dependencies"]
                            ],
                        }
                    )
            scan["status"] = "findings" if scan["findings"] else "passed"
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            subprocess.TimeoutExpired,
            importlib.metadata.PackageNotFoundError,
        ) as exc:
            scan["error"] = (
                f"{type(exc).__name__}: scan incomplete; rerun {tool} locally"
            )
        scans.append(scan)
    stable = source_manifest(root) == manifest and current_revision(root) == revision
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "revision": revision,
        "source_manifest": manifest,
        "source_digest": manifest_digest(manifest),
        "scans": scans,
        "risk_exceptions": [],
        "inputs_stable": stable,
        "ok": stable and all(scan["status"] == "passed" for scan in scans),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output", type=Path, default=Path("sdlc_artifacts/evidence/security.json")
    )
    args = parser.parse_args()
    root = args.root.resolve()
    output = (root / args.output).resolve()
    # Keep reports outside the source snapshot to avoid self-invalidating output.
    output.relative_to(root / "sdlc_artifacts")
    report = scan_project(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output)
    for scan in report["scans"]:
        print(f"{scan['tool']}: {scan['status']} ({len(scan['findings'])} findings)")
    print(f"Evidence: {output}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
