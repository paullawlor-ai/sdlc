from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sdlc import context_packet, project_change_class  # noqa: E402
from token_report import report  # noqa: E402


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

    def test_context_packet_keeps_critical_state_without_mid_section_slice(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            artifacts.mkdir()
            artifacts.joinpath("STATE.md").write_text(
                "**Phase**: Testing\n**Goal**: release safely\n"
                "## Next Action\nRun the completion gate.\n",
                encoding="utf-8",
            )
            artifacts.joinpath("context.md").write_text("low priority " * 5000, encoding="utf-8")
            packet = context_packet(root, "testing", 250)
            self.assertIn("release safely", packet)
            self.assertIn("Run the completion gate", packet)
            self.assertNotIn("low priority", packet)
            self.assertLessEqual(len(packet), 1000)

    def test_adapter_reduction_meets_baseline_target(self) -> None:
        baseline = json.loads(
            (ROOT / "policy" / "token-baseline.json").read_text(encoding="utf-8")
        )
        current = report()["groups"]["adapters"]["approx_tokens"]
        previous = baseline["before"]["adapter_tokens"]
        reduction = (previous - current) * 100 / previous
        self.assertGreaterEqual(reduction, baseline["targets"]["adapter_reduction_percent"])

    def test_change_class_is_read_from_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "sdlc_artifacts"
            artifacts.mkdir()
            artifacts.joinpath("STATE.md").write_text(
                "**Change class**: trivial\n", encoding="utf-8"
            )
            self.assertEqual(project_change_class(root), "trivial")


if __name__ == "__main__":
    unittest.main()
