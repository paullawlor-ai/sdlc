"""Controlled scan evidence for lifecycle tests (no network or third-party tools)."""

import json
from datetime import datetime, timezone
from pathlib import Path

from _readiness import current_revision
from _security import manifest_digest, source_manifest


def write_scan_fixture(root: Path, review: Path) -> dict:
    manifest = source_manifest(root)
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
    report = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "revision": current_revision(root),
        "source_manifest": manifest,
        "source_digest": manifest_digest(manifest),
        "risk_exceptions": [],
        "scans": [
            {
                "tool": name,
                "scope": scope,
                "version": "fixture",
                "status": "passed",
                "findings": [],
            }
            for name, scope in scopes.items()
        ],
        "ok": True,
        "inputs_stable": True,
    }
    evidence = root / "sdlc_artifacts" / "evidence" / "security.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(report), encoding="utf-8")
    text = review.read_text(encoding="utf-8")
    if "- [x] Approved" in text:
        text = text.replace(
            "## Approval\n",
            f"## Approval\n- **Approved source digest**: {report['source_digest']}\n",
        )
    text = text.replace(
        "## Reviewed Artifacts\n",
        "## Reviewed Artifacts\n"
        f"- **Reviewed revision**: {report['revision']}\n"
        f"- **Reviewed source digest**: {report['source_digest']}\n",
    )
    review.write_text(
        text + "\n## Evidence References\n"
        "- **Security evidence**: sdlc_artifacts/evidence/security.json\n",
        encoding="utf-8",
    )
    return report
