from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sdlc import (  # noqa: E402
    command_check,
    context_packet,
    project_change_class,
    record_handoff,
)
from token_report import report  # noqa: E402
from tests.security_fixtures import write_scan_fixture  # noqa: E402


def complete_change(status: str, date: str | None = None) -> str:
    approval_date = f"- **Date**: {date}\n" if date else ""
    return (
        "## Summary\nValidate artifacts before implementation begins.\n"
        "## Scope\n- **Risk class**: standard\n- **Policy profile**: standard\n"
        "- **Components affected**: validation CLI\n"
        "## Dependencies\n- **Blocking ADRs**: None\n- **Blocking changes**: None\n"
        "- **External dependencies**: None\n"
        "## Proposed Approach\nRun deterministic checks during proposal.\n"
        "## Acceptance Criteria\n| ID | Criterion | Test |\n|---|---|---|\n"
        "| AC-01 | Given valid content, when checked, then validation passes | unit |\n"
        "## Testing\n- **Unit tests**: Validate strict diagnostics\n"
        "- **Integration tests**: Exercise command output\n"
        "- **Negative / abuse cases**: Reject incomplete content\n"
        f"## Approval\n- **Status**: {status}\n{approval_date}"
    )


class CliTests(unittest.TestCase):
    def test_context_packet_obeys_budget(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact_root = root / "sdlc_artifacts"
            artifact_root.mkdir()
            artifact_root.joinpath("STATE.md").write_text(
                "**Phase**: Implementation\n" + ("detail " * 5000),
                encoding="utf-8",
            )
            packet = context_packet(root, "implementation", 500)
            self.assertLessEqual(len(packet), 500 * 4)
            self.assertNotIn("detail detail", packet)

    def test_context_packet_keeps_critical_state_without_mid_section_slice(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            artifacts.mkdir()
            artifacts.joinpath("STATE.md").write_text(
                "**Phase**: Testing\n**Goal**: release safely\n"
                "## Next Action\nRun the completion gate.\n",
                encoding="utf-8",
            )
            artifacts.joinpath("context.md").write_text(
                "low priority " * 5000, encoding="utf-8"
            )
            packet = context_packet(root, "testing", 250)
            self.assertIn("release safely", packet)
            self.assertIn("Run the completion gate", packet)
            self.assertNotIn("low priority", packet)
            self.assertLessEqual(len(packet), 1000)

    def test_context_prioritizes_active_acceptance_over_long_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            changes = artifacts / "changes"
            changes.mkdir(parents=True)
            change = changes / "0001-current.md"
            change.write_text(
                "## Summary\nCurrent bounded work.\n"
                "## Acceptance Criteria\nAC-01: preserve the critical criterion.\n"
                "## Approval\n- **Status**: Approved\n",
                encoding="utf-8",
            )
            artifacts.joinpath("STATE.md").write_text(
                "**Phase**: Implementation\n**Goal**: current work\n"
                "## Active Change\n"
                "- **Change document**: sdlc_artifacts/changes/0001-current.md\n"
                "## Last Session Summary\n" + ("old history " * 2000),
                encoding="utf-8",
            )
            packet = context_packet(root, "implementation", 500)
            self.assertIn("preserve the critical criterion", packet)
            self.assertNotIn("old history old history", packet)
            self.assertLessEqual(len(packet), 2000)

    def test_context_compacts_sections_without_losing_gate_headings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            change = artifacts / "changes" / "0001-current.md"
            change.parent.mkdir(parents=True)
            change.write_text(
                "## Summary\n" + ("summary detail " * 1000) + "\n"
                "## Dependencies\n- None\n"
                "## Acceptance Criteria\nAC-01: preserve this active criterion.\n"
                + ("criterion evidence " * 1000)
                + "\n## Completion Gate\n- **Tests passing**: pending\n"
                + ("gate evidence " * 1000)
                + "\n## Testing\nRun focused tests.\n"
                "## Approval\n- **Status**: Approved\n",
                encoding="utf-8",
            )
            artifacts.joinpath("STATE.md").write_text(
                "**Phase**: Implementation\n**Goal**: ship safely\n"
                "## Active Change\n"
                "- **Change document**: sdlc_artifacts/changes/0001-current.md\n"
                "## Next Action\nImplement AC-01.\n",
                encoding="utf-8",
            )
            packet = context_packet(root, "implementation", 2000)
            self.assertIn("Active Change - Acceptance Criteria", packet)
            self.assertIn("preserve this active criterion", packet)
            self.assertIn("Active Change - Completion Gate", packet)
            self.assertIn("Tests passing", packet)
            self.assertIn("Section compacted", packet)
            self.assertLessEqual(len(packet), 8000)

    def test_extended_evidence_is_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            change = artifacts / "changes" / "0001-current.md"
            change.parent.mkdir(parents=True)
            change.write_text(
                "## Summary\nCompact outcome.\n"
                "## Proposed Approach\nDetailed implementation evidence.\n"
                "## Approval\n- **Status**: Approved\n",
                encoding="utf-8",
            )
            artifacts.joinpath("STATE.md").write_text(
                "## Active Change\n"
                "- **Change document**: sdlc_artifacts/changes/0001-current.md\n",
                encoding="utf-8",
            )
            self.assertNotIn(
                "Detailed implementation evidence",
                context_packet(root, None, 2000),
            )
            self.assertIn(
                "Detailed implementation evidence",
                context_packet(root, None, 2000, extended_evidence=True),
            )

    def test_handoff_replaces_current_summary_and_archives_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            artifacts.mkdir()
            state = artifacts / "STATE.md"
            state.write_text(
                "# Project State\n\n## Next Action\nOld next step.\n\n"
                "## Last Session Summary\n\n**Date**: 2026-10-20\n\n"
                "**Completed**:\n- Initial setup\n\n"
                "**Left off at**:\nFirst stopping point.\n",
                encoding="utf-8",
            )
            first = record_handoff(
                root,
                ["Validated context"],
                "Ready to implement tests.",
                "Write the regression tests.",
                "2026-10-24",
            )
            self.assertTrue(first["archived_previous"])
            second = record_handoff(
                root,
                ["Added regression tests"],
                "Ready to run the suite.",
                handoff_date="2026-10-25",
            )
            self.assertTrue(second["archived_previous"])
            current = state.read_text(encoding="utf-8")
            history = artifacts.joinpath("history", "handoffs.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Added regression tests", current)
            self.assertNotIn("Validated context", current)
            self.assertIn("Write the regression tests", current)
            self.assertIn("Initial setup", history)
            self.assertIn("Validated context", history)
            self.assertNotIn("Initial setup", context_packet(root, None, 2000))

    def test_handoff_cli_records_json_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            artifacts.mkdir()
            artifacts.joinpath("STATE.md").write_text(
                "# Project State\n\n## Last Session Summary\n\n"
                "**Date**: [YYYY-MM-DD]\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "sdlc.py"),
                    "handoff",
                    "--completed",
                    "Completed CLI coverage",
                    "--left-off",
                    "Ready for the next increment.",
                    "--date",
                    "2026-10-25",
                    "--json",
                ],
                cwd=root,
                env={**os.environ, "SDLC_PROJECT_ROOT": str(root)},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse(json.loads(result.stdout)["archived_previous"])
            self.assertIn(
                "Completed CLI coverage",
                artifacts.joinpath("STATE.md").read_text(encoding="utf-8"),
            )

    def test_adapter_reduction_meets_baseline_target(self) -> None:
        baseline = json.loads(
            (ROOT / "policy" / "token-baseline.json").read_text(encoding="utf-8")
        )
        current = report()["groups"]["adapters"]["approx_tokens"]
        previous = baseline["before"]["adapter_tokens"]
        reduction = (previous - current) * 100 / previous
        self.assertGreaterEqual(
            reduction, baseline["targets"]["adapter_reduction_percent"]
        )

    def test_change_class_is_read_from_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            artifacts.mkdir()
            artifacts.joinpath("STATE.md").write_text(
                "**Change class**: trivial\n", encoding="utf-8"
            )
            self.assertEqual(project_change_class(root), "trivial")

    def test_strict_check_elevates_artifact_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            changes = root / "sdlc_artifacts" / "changes"
            changes.mkdir(parents=True)
            changes.joinpath("0001-example.md").write_text(
                complete_change("Approved", "21/10/2026"),
                encoding="utf-8",
            )
            self.assertEqual(command_check(root, False, False, strict=False), 0)
            self.assertEqual(command_check(root, False, False, strict=True), 1)

    def test_strict_mode_only_elevates_policy_selected_warnings(self) -> None:
        from _artifacts import Diagnostic
        from sdlc import strict_warning_failures

        diagnostics = [
            Diagnostic("NON_ISO_APPROVAL_DATE", "warning", "selected"),
            Diagnostic("FUTURE_ADVISORY", "warning", "not selected"),
            Diagnostic("NON_ISO_APPROVAL_DATE", "info", "not a warning"),
        ]
        self.assertEqual(
            [item.message for item in strict_warning_failures(diagnostics)],
            ["selected"],
        )

    def test_json_diagnostics_are_stable_and_include_codes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            changes = root / "sdlc_artifacts" / "changes"
            changes.mkdir(parents=True)
            changes.joinpath("0001-example.md").write_text(
                "## Approval\n- **Status**: Maybe\n",
                encoding="utf-8",
            )
            outputs = []
            for _ in range(2):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(command_check(root, False, True), 1)
                outputs.append(output.getvalue())
            self.assertEqual(outputs[0], outputs[1])
            result = json.loads(outputs[0])
            self.assertEqual(
                result["diagnostics"][0]["code"], "INVALID_ARTIFACT_STATUS"
            )
            self.assertEqual(
                [item["code"] for item in result["strict_failures"]],
                ["METADATA_COMPATIBILITY_MODE"],
            )

    def test_propose_command_promotes_complete_draft(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            change = root / "sdlc_artifacts" / "changes" / "0001-example.md"
            change.parent.mkdir(parents=True)
            change.write_text(complete_change("Draft"), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "sdlc.py"), "propose", str(change)],
                cwd=root,
                env={**os.environ, "SDLC_PROJECT_ROOT": str(root)},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Proposed:", result.stdout)
            self.assertIn("**Status**: Proposed", change.read_text(encoding="utf-8"))

    def test_metadata_sync_adopts_required_mode_and_scaffolds_stay_current(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            changes = artifacts / "changes"
            changes.mkdir(parents=True)
            config = artifacts / "config.json"
            config.write_text(
                '{"schema_version": 1, "profile": "standard", '
                '"metadata_mode": "compatibility"}\n',
                encoding="utf-8",
            )
            changes.joinpath("0001-existing.md").write_text(
                "## Approval\n- **Status**: Draft\n", encoding="utf-8"
            )
            env = {**os.environ, "SDLC_PROJECT_ROOT": str(root)}

            preview = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "sdlc.py"),
                    "metadata",
                    "sync",
                    "--json",
                ],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertTrue(json.loads(preview.stdout)["mode_change"])
            self.assertFalse(artifacts.joinpath(".sdlc", "metadata").exists())
            self.assertEqual(
                json.loads(config.read_text(encoding="utf-8"))["metadata_mode"],
                "compatibility",
            )

            applied = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "sdlc.py"),
                    "metadata",
                    "sync",
                    "--apply",
                    "--json",
                ],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            self.assertEqual(
                json.loads(config.read_text(encoding="utf-8"))["metadata_mode"],
                "required",
            )

            created = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "sdlc.py"),
                    "new",
                    "change",
                    "metadata scaffold coverage",
                ],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            self.assertTrue(
                artifacts.joinpath(".sdlc", "metadata", "change-0002.json").is_file()
            )
            index = json.loads(
                artifacts.joinpath("index.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(index["artifacts"]), 2)

    def test_new_project_setup_initializes_required_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "sdlc.py"),
                    "setup",
                    "--assistant",
                    "codex",
                ],
                cwd=root,
                env={**os.environ, "SDLC_PROJECT_ROOT": str(root)},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            artifacts = root / "sdlc_artifacts"
            self.assertEqual(
                json.loads(
                    artifacts.joinpath("config.json").read_text(encoding="utf-8")
                )["metadata_mode"],
                "required",
            )
            self.assertTrue(artifacts.joinpath(".sdlc", "metadata").is_dir())
            self.assertTrue(artifacts.joinpath("index.json").is_file())
            verified = subprocess.run(
                [sys.executable, str(SCRIPTS / "sdlc.py"), "verify"],
                cwd=root,
                env={**os.environ, "SDLC_PROJECT_ROOT": str(root)},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
            self.assertIn("required structured metadata", verified.stdout)

    def test_existing_project_setup_preserves_implicit_compatibility_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            artifacts.mkdir()
            artifacts.joinpath("STATE.md").write_text(
                "# Project State\n", encoding="utf-8"
            )
            config = artifacts / "config.json"
            config.write_text(
                '{"schema_version": 1, "profile": "standard"}\n',
                encoding="utf-8",
            )
            env = {**os.environ, "SDLC_PROJECT_ROOT": str(root)}
            setup = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "sdlc.py"),
                    "setup",
                    "--assistant",
                    "codex",
                ],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(setup.returncode, 0, setup.stdout + setup.stderr)
            self.assertNotIn(
                "metadata_mode", json.loads(config.read_text(encoding="utf-8"))
            )
            self.assertFalse(artifacts.joinpath(".sdlc", "metadata").exists())

            verified = subprocess.run(
                [sys.executable, str(SCRIPTS / "sdlc.py"), "verify"],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)

    def test_ready_to_finalize_command_reports_human_action(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            change = artifacts / "changes" / "0001-example.md"
            review = artifacts / "reviews" / "REV-0001-example.md"
            change.parent.mkdir(parents=True)
            review.parent.mkdir(parents=True)
            change.write_text(
                complete_change("Approved")
                + "## Completion Gate\n- **Tests passing**: yes\n"
                "- **Security review (REV)**: REV-0001\n"
                "- **Agent recommendation**: Approved\n"
                "- **Open must-fix in REV**: 0\n",
                encoding="utf-8",
            )
            review.write_text(
                "## Reviewed Artifacts\n- **Change docs**: 0001-example.md\n"
                "## Agent Recommendation\n- **Recommendation**: Approved\n"
                "## Findings\n### Must-Fix\nNone\n",
                encoding="utf-8",
            )
            artifacts.joinpath("STATE.md").write_text(
                "**Change class**: standard\n## Active Change\n"
                "- **Change document**: sdlc_artifacts/changes/0001-example.md\n",
                encoding="utf-8",
            )
            artifacts.joinpath("config.json").write_text(
                '{"schema_version": 1, "profile": "standard"}\n',
                encoding="utf-8",
            )
            write_scan_fixture(root, review)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "sdlc.py"),
                    "check",
                    "--ready-to-finalize",
                    "--json",
                ],
                cwd=root,
                env={**os.environ, "SDLC_PROJECT_ROOT": str(root)},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ready_to_finalize"])
            self.assertIn("Human may set", payload["finalization_action"])


if __name__ == "__main__":
    unittest.main()
