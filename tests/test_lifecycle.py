from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
HOOKS = SCRIPTS / "hooks"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HOOKS))

from _artifacts import artifact_index, validate_artifacts  # noqa: E402
from _gate_common import evaluate_implementation_gate  # noqa: E402
from sdlc import completion_gate  # noqa: E402


class LifecycleTests(unittest.TestCase):
    def _write_completion_fixture(self, root: Path, must_fix: str = "None") -> None:
        artifacts = root / "sdlc_artifacts"
        changes = artifacts / "changes"
        reviews = artifacts / "reviews"
        changes.mkdir(parents=True)
        reviews.mkdir(parents=True)
        changes.joinpath("0001-login.md").write_text(
            "## Approval\n- **Status**: Approved\n"
            "## Completion Gate\n- **Tests passing**: yes\n"
            "- **Security review (REV)**: REV-0001\n"
            "- **Agent recommendation**: Approved\n"
            "- **Open must-fix in REV**: 0\n",
            encoding="utf-8",
        )
        reviews.joinpath("REV-0001-login.md").write_text(
            "## Reviewed Artifacts\n- **Change docs**: 0001-login.md\n"
            "## Agent Recommendation\n- **Recommendation**: Approved\n"
            f"## Findings\n### Must-Fix\n{must_fix}\n",
            encoding="utf-8",
        )
        artifacts.joinpath("STATE.md").write_text(
            "**Change class**: standard\n## Active Change\n"
            "- **Change document**: sdlc_artifacts/changes/0001-login.md\n",
            encoding="utf-8",
        )

    def test_requirement_to_completion_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            requirements = artifacts / "requirements"
            decisions = artifacts / "decisions" / "accepted"
            changes = artifacts / "changes"
            reviews = artifacts / "reviews"
            for folder in (requirements, decisions, changes, reviews):
                folder.mkdir(parents=True, exist_ok=True)

            requirements.joinpath("REQ-0001-login.md").write_text(
                "# REQ-0001\n## Approval\n- **Status**: Approved\n",
                encoding="utf-8",
            )
            decisions.joinpath("ADR-0001-auth.md").write_text(
                "# ADR-0001\n## Status\n- **Current status**: Accepted\n",
                encoding="utf-8",
            )
            change = changes / "0001-login.md"
            change.write_text(
                "# Change 0001\n"
                "- **Risk class**: standard\n"
                "- **Blocking ADRs**: ADR-0001\n"
                "- **Requirement**: REQ-0001\n"
                "## Approval\n- **Status**: Approved\n"
                "## Completion Gate\n"
                "- **Tests passing**: yes\n"
                "- **Security review (REV)**: REV-0001\n"
                "- **Agent recommendation**: Approved\n"
                "- **Open must-fix in REV**: 0\n"
                "- **Gate result**: PASS\n",
                encoding="utf-8",
            )
            reviews.joinpath("REV-0001-login.md").write_text(
                "# REV-0001\n## Reviewed Artifacts\n"
                "- **Change docs**: 0001-login.md\n"
                "## Agent Recommendation\n- **Recommendation**: Approved\n"
                "## Findings\n### Must-Fix\nNone\n",
                encoding="utf-8",
            )
            artifacts.joinpath("STATE.md").write_text(
                "**Change class**: standard\n"
                "## Active Change\n"
                "- **Change document**: sdlc_artifacts/changes/0001-login.md\n",
                encoding="utf-8",
            )
            artifacts.joinpath("config.json").write_text(
                '{"schema_version": 1, "profile": "standard"}\n',
                encoding="utf-8",
            )

            self.assertEqual(validate_artifacts(root), [])
            self.assertEqual(len(artifact_index(root)["artifacts"]), 4)
            self.assertTrue(evaluate_implementation_gate(root)[0])
            self.assertTrue(completion_gate(root, None, None)[0])

    def test_completion_gate_does_not_trust_typed_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            changes = root / "sdlc_artifacts" / "changes"
            changes.mkdir(parents=True)
            changes.joinpath("0001-incomplete.md").write_text(
                "## Approval\n- **Status**: Approved\n"
                "## Completion Gate\n- **Gate result**: PASS\n",
                encoding="utf-8",
            )
            root.joinpath("sdlc_artifacts", "STATE.md").write_text(
                "**Change class**: standard\n"
                "## Active Change\n- **Change document**: sdlc_artifacts/changes/0001-incomplete.md\n",
                encoding="utf-8",
            )
            allowed, message = completion_gate(root, None, None)
            self.assertFalse(allowed)
            self.assertIn("tests", message)

    def test_completion_gate_blocks_open_must_fix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_completion_fixture(root, "1. Fix authorization bypass")
            allowed, message = completion_gate(root, None, None)
            self.assertFalse(allowed)
            self.assertIn("must-fix", message)


if __name__ == "__main__":
    unittest.main()
