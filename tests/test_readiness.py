from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _readiness import doctor_report, fixed_pytest_basetemps, git_state  # noqa: E402
from sdlc import evidence_readiness_diagnostics  # noqa: E402


def run_git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )


@unittest.skipUnless(shutil.which("git"), "Git is required for repository fixtures")
class GitReadinessTests(unittest.TestCase):
    def _repository(self, root: Path) -> None:
        run_git(root, "init")
        run_git(root, "config", "user.name", "SDLC Test")
        run_git(root, "config", "user.email", "sdlc@example.invalid")

    def test_repository_state_distinguishes_baseline_and_evidence_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._repository(root)
            artifacts = root / "sdlc_artifacts"
            artifacts.mkdir()
            state_file = artifacts / "STATE.md"
            state_file.write_text("# State\n", encoding="utf-8")

            initial = git_state(root)
            self.assertTrue(initial["is_repository"])
            self.assertIsNone(initial["baseline_commit"])
            self.assertEqual(initial["evidence_untracked"], ["sdlc_artifacts/STATE.md"])
            self.assertIn(
                "GIT_BASELINE_MISSING",
                {item.code for item in evidence_readiness_diagnostics(root)},
            )

            run_git(root, "add", "sdlc_artifacts/STATE.md")
            run_git(root, "commit", "-m", "Add state evidence")
            committed = git_state(root)
            self.assertRegex(str(committed["baseline_commit"]), r"^[0-9a-f]{40}$")
            self.assertEqual(committed["evidence_untracked"], [])
            self.assertEqual(committed["evidence_modified"], [])

            state_file.write_text("# Updated state\n", encoding="utf-8")
            self.assertEqual(
                git_state(root)["evidence_modified"], ["sdlc_artifacts/STATE.md"]
            )

    def test_regulated_finalization_promotes_durability_warnings_to_errors(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._repository(root)
            artifacts = root / "sdlc_artifacts"
            artifacts.mkdir()
            artifacts.joinpath("config.json").write_text(
                '{"profile": "regulated", "repository_mode": "git"}\n',
                encoding="utf-8",
            )
            diagnostics = evidence_readiness_diagnostics(
                root, finalization=True, profile="regulated"
            )
            self.assertTrue(diagnostics)
            self.assertTrue(all(item.severity == "error" for item in diagnostics))


class EnvironmentReadinessTests(unittest.TestCase):
    def test_doctor_reports_interpreter_and_unique_writable_temp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = doctor_report(Path(directory))
            second = doctor_report(Path(directory))
            self.assertTrue(first["ok"])
            self.assertEqual(first["python"]["executable"], sys.executable)
            self.assertTrue(first["temporary_directory"]["writable"])
            self.assertNotEqual(
                first["temporary_directory"]["path"],
                second["temporary_directory"]["path"],
            )

    def test_fixed_pytest_basetemp_is_reported_but_templates_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath("pytest.ini").write_text(
                '[pytest]\naddopts = --basetemp=".pytest temp"\n', encoding="utf-8"
            )
            root.joinpath("tox.ini").write_text(
                "[testenv]\ncommands = pytest --basetemp={envtmpdir}\n",
                encoding="utf-8",
            )
            self.assertEqual(
                fixed_pytest_basetemps(root),
                [{"path": "pytest.ini", "value": ".pytest temp"}],
            )

    @unittest.skipUnless(shutil.which("git"), "Git is required for revision fixture")
    def test_new_review_records_the_current_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_git(root, "init")
            run_git(root, "config", "user.name", "SDLC Test")
            run_git(root, "config", "user.email", "sdlc@example.invalid")
            root.joinpath("README.md").write_text("fixture\n", encoding="utf-8")
            run_git(root, "add", "README.md")
            run_git(root, "commit", "-m", "Create baseline")
            revision = run_git(root, "rev-parse", "HEAD").stdout.strip()

            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "new_review.py"), "revision evidence"],
                cwd=root,
                env={**os.environ, "SDLC_PROJECT_ROOT": str(root)},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            review = next((root / "sdlc_artifacts" / "reviews").glob("REV-*.md"))
            self.assertIn(
                f"**Reviewed revision**: {revision}",
                review.read_text(encoding="utf-8"),
            )

    def test_explicit_non_git_mode_suppresses_repository_failures(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            artifacts.mkdir()
            artifacts.joinpath("config.json").write_text(
                '{"profile": "regulated", "repository_mode": "non-git"}\n',
                encoding="utf-8",
            )
            self.assertEqual(
                evidence_readiness_diagnostics(
                    root, finalization=True, profile="regulated"
                ),
                [],
            )
            self.assertEqual(git_state(root)["mode"], "non-git")

    def test_invalid_repository_mode_is_a_configuration_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            artifacts.mkdir()
            artifacts.joinpath("config.json").write_text(
                '{"repository_mode": "sometimes"}\n', encoding="utf-8"
            )
            diagnostics = evidence_readiness_diagnostics(root)
            self.assertEqual(diagnostics[0].code, "CONFIG_REPOSITORY_MODE_INVALID")
            self.assertEqual(diagnostics[0].severity, "error")


if __name__ == "__main__":
    unittest.main()
