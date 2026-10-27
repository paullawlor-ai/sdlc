from __future__ import annotations

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _policy import change_requirements  # noqa: E402
from _security import security_evidence_diagnostics, source_manifest  # noqa: E402
from security_scan import parse_findings, run_tool, scan_project  # noqa: E402
from tests.security_fixtures import write_scan_fixture  # noqa: E402
from tests import test_lifecycle  # noqa: E402
from sdlc import implemented_review_diagnostics, finalization_diagnostics  # noqa: E402


class SecurityEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        test_lifecycle.LifecycleTests()._write_completion_fixture(self.root)
        self.code = self.root / "app.py"
        self.code.write_text("print('safe')\n", encoding="utf-8")
        self.review = self.root / "sdlc_artifacts/reviews/REV-0001-login.md"
        # Replace the initial fixture before generating a source-bound report.
        text = self.review.read_text(encoding="utf-8").split("## Evidence References")[
            0
        ]
        text = "\n".join(
            line
            for line in text.splitlines()
            if "Reviewed source digest" not in line and "Reviewed revision" not in line
        )
        self.review.write_text(text, encoding="utf-8")
        self.report = write_scan_fixture(self.root, self.review)
        self.evidence = self.root / "sdlc_artifacts/evidence/security.json"

    def diagnostics(self) -> list:
        return security_evidence_diagnostics(
            self.root,
            self.review.read_text(encoding="utf-8"),
            str(self.review.relative_to(self.root)),
            change_requirements("standard"),
        )

    def save(self, report: object) -> None:
        self.evidence.write_text(json.dumps(report), encoding="utf-8")

    def test_current_non_git_evidence_passes_without_editing_human_fields(self) -> None:
        before = self.review.read_bytes()
        self.assertEqual(self.diagnostics(), [])
        self.assertEqual(self.review.read_bytes(), before)

    def test_code_edits_additions_and_deletions_invalidate_evidence(self) -> None:
        for operation in ("edit", "add", "delete"):
            with self.subTest(operation=operation):
                if operation == "edit":
                    self.code.write_text("print('changed')\n", encoding="utf-8")
                elif operation == "add":
                    (self.root / "new.py").write_text("", encoding="utf-8")
                else:
                    self.code.unlink()
                self.assertEqual(self.diagnostics()[0].code, "SECURITY_EVIDENCE_STALE")

    def test_missing_failed_partial_expired_and_exception_reports_block(self) -> None:
        mutations = [
            lambda d: d.update(ok=False),
            lambda d: d.update(inputs_stable=False),
            lambda d: d.update(generated_at="2000-01-01T00:00:00Z"),
            lambda d: d.update(generated_at="2999-01-01T00:00:00Z"),
            lambda d: d.update(
                risk_exceptions=[
                    {"owner": "Human", "expiry": "2999-01-01", "approved": True}
                ]
            ),
            lambda d: d["scans"].pop(),
            lambda d: d["scans"][0].update(status="failed"),
            lambda d: d["scans"][0].update(scope=[]),
            lambda d: d["scans"][0].update(findings=[{"id": "B307"}]),
            lambda d: d["scans"][0].update(version=None),
            lambda d: d["scans"].append(d["scans"][0]),
        ]
        for index, mutation in enumerate(mutations):
            with self.subTest(case=index):
                report = copy.deepcopy(self.report)
                mutation(report)
                self.save(report)
                self.assertEqual(
                    self.diagnostics()[0].code, "SECURITY_EVIDENCE_INVALID"
                )
        self.evidence.unlink()
        self.assertEqual(self.diagnostics()[0].code, "SECURITY_EVIDENCE_INVALID")

    def test_malformed_and_external_reports_fail_closed(self) -> None:
        for value in ([], None, {"schema_version": 1}, {"schema_version": 99}):
            self.save(value)
            self.assertTrue(self.diagnostics())
        text = self.review.read_text(encoding="utf-8").replace(
            "sdlc_artifacts/evidence/security.json", "../outside.json"
        )
        self.review.write_text(text, encoding="utf-8")
        self.assertTrue(self.diagnostics())

    def test_required_review_cannot_omit_security_reference(self) -> None:
        self.review.write_text("## Evidence References\n", encoding="utf-8")
        self.assertEqual(self.diagnostics()[0].code, "SECURITY_EVIDENCE_REQUIRED")

    def test_environment_and_evidence_updates_do_not_change_source_digest(self) -> None:
        before = source_manifest(self.root)
        environment = self.root / "custom-env"
        environment.mkdir()
        (environment / "pyvenv.cfg").write_text("home=fixture", encoding="utf-8")
        (environment / "lib.py").write_text("ignored", encoding="utf-8")
        (self.root / "sdlc_artifacts/STATE.md").write_text(
            "Updated handoff", encoding="utf-8"
        )
        self.assertEqual(source_manifest(self.root), before)

    def test_historical_implemented_review_survives_later_changes(self) -> None:
        change = self.root / "sdlc_artifacts/changes/0001-login.md"
        change.write_text(
            change.read_text(encoding="utf-8").replace(
                "**Status**: Approved", "**Status**: Implemented"
            ),
            encoding="utf-8",
        )
        self.code.write_text("print('next change')", encoding="utf-8")
        report = copy.deepcopy(self.report)
        report["generated_at"] = "2000-01-01T00:00:00+00:00"
        self.save(report)
        self.assertEqual(implemented_review_diagnostics(self.root), [])
        self.assertTrue(self.diagnostics())

    def test_human_signoff_cannot_be_reused_for_a_different_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            test_lifecycle.LifecycleTests()._write_completion_fixture(
                root, profile="regulated", human_review=True
            )
            review = root / "sdlc_artifacts/reviews/REV-0001-login.md"
            text = review.read_text(encoding="utf-8")
            text = text.replace(
                "**Approved source digest**:", "**Previous source digest**:"
            )
            review.write_text(text, encoding="utf-8")
            self.assertIn(
                "HUMAN_REVIEW_DIGEST_REQUIRED",
                {item.code for item in finalization_diagnostics(root)},
            )

    @unittest.skipUnless(shutil.which("git"), "Git required")
    def test_git_revision_and_evidence_only_commit(self) -> None:
        def git(*args: str) -> str:
            return subprocess.run(
                ["git", *args],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

        (self.root / "sdlc_artifacts/config.json").write_text(
            '{"repository_mode":"git"}', encoding="utf-8"
        )
        git("init")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        git("add", "app.py")
        git("commit", "-m", "Source baseline")
        text = self.review.read_text(encoding="utf-8").split("## Evidence References")[
            0
        ]
        text = "\n".join(
            line
            for line in text.splitlines()
            if "Reviewed source digest" not in line and "Reviewed revision" not in line
        )
        self.review.write_text(text, encoding="utf-8")
        write_scan_fixture(self.root, self.review)
        self.assertEqual(self.diagnostics(), [])
        git("add", "sdlc_artifacts")
        git("commit", "-m", "Store reviewed evidence")
        self.assertEqual(self.diagnostics(), [])
        report = json.loads(self.evidence.read_text(encoding="utf-8"))
        report["revision"] = "f" * 40
        self.save(report)
        self.assertEqual(self.diagnostics()[0].code, "REVIEW_REVISION_STALE")


class ScannerTests(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("SDLC_LIVE_AUDIT") == "1"
        and importlib.util.find_spec("pip_audit"),
        "live advisory service test is opt-in",
    )
    def test_real_dependency_scanner_detects_known_vulnerable_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "fixture.txt").write_text(
                "requests" + "==2.19.1\n", encoding="utf-8"
            )
            result = run_tool(
                root,
                "pip_audit",
                [
                    "--no-deps",
                    "--disable-pip",
                    "--progress-spinner",
                    "off",
                    "-f",
                    "json",
                    "-r",
                    "fixture.txt",
                ],
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertTrue(parse_findings("pip-audit", json.loads(result.stdout)))

    def test_dependency_and_secret_findings_are_preserved_without_source(self) -> None:
        findings = parse_findings(
            "pip-audit",
            {
                "dependencies": [
                    {
                        "name": "fixture",
                        "version": "1",
                        "vulns": [{"id": "CVE-fixture"}],
                    }
                ]
            },
        )
        self.assertEqual(findings[0]["id"], "CVE-fixture")
        secret = parse_findings(
            "detect-secrets",
            {
                "results": {
                    "app.py": [
                        {
                            "type": "Secret",
                            "line_number": 1,
                            "raw_source": "never export this",
                        }
                    ]
                }
            },
        )
        self.assertNotIn("never export", json.dumps(secret))
        with self.assertRaises(ValueError):
            parse_findings(
                "pip-audit", {"dependencies": [{"skip_reason": "unsupported"}]}
            )

    def test_scan_errors_never_pass_as_empty_findings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "app.py").write_text("print('safe')", encoding="utf-8")
            with patch(
                "security_scan.importlib.metadata.version", return_value="fixture"
            ):
                for result in (
                    subprocess.CompletedProcess([], 2, "", "error"),
                    subprocess.CompletedProcess([], 0, "not json", ""),
                    subprocess.CompletedProcess(
                        [], 1, '{"results":[],"errors":[]}', ""
                    ),
                ):
                    with patch("security_scan.run_tool", return_value=result):
                        report = scan_project(root)
                    self.assertFalse(report["ok"])
                    self.assertTrue(
                        any(scan["status"] == "failed" for scan in report["scans"])
                    )

    @unittest.skipUnless(
        importlib.util.find_spec("bandit"), "development tools not installed"
    )
    def test_real_bandit_detects_insecure_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "unsafe.py").write_text(
                "def execute(user_input):\n    return eval(user_input)\n",
                encoding="utf-8",
            )
            result = run_tool(root, "bandit", ["-f", "json", "-ll", "-ii", "unsafe.py"])
            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "B307",
                {
                    item["id"]
                    for item in parse_findings("bandit", json.loads(result.stdout))
                },
            )

    @unittest.skipUnless(
        importlib.util.find_spec("detect_secrets"), "development tools not installed"
    )
    def test_real_secret_scanner_detects_synthetic_credential(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Construct a fake credential at runtime; no usable secret is committed.
            fake = "ghp_" + "".join(chr(65 + index % 26) for index in range(36))
            (root / "secret.txt").write_text("token=" + fake, encoding="utf-8")
            result = run_tool(
                root,
                "detect_secrets",
                ["scan", "--all-files", "--no-verify", "secret.txt"],
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(parse_findings("detect-secrets", json.loads(result.stdout)))


if __name__ == "__main__":
    unittest.main()
