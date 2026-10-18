from __future__ import annotations

import sys
import json
import tempfile
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "scripts" / "hooks"
sys.path.insert(0, str(HOOKS))

from _gate_common import (  # noqa: E402
    active_change_path,
    adr_is_accepted,
    evaluate_implementation_gate,
    resolve_gate_changes,
)


class GateCommonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.changes = self.root / "sdlc_artifacts" / "changes"
        self.changes.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_change(self, name: str, status: str = "Approved") -> Path:
        path = self.changes / name
        path.write_text(
            f"# Change\n## Approval\n- **Status**: {status}\n",
            encoding="utf-8",
        )
        return path

    def write_state(self, value: str) -> None:
        (self.root / "sdlc_artifacts" / "STATE.md").write_text(
            "## Active Change\n" f"- **Change document**: {value}\n",
            encoding="utf-8",
        )

    def install_policy(self) -> None:
        policy_dir = self.root / "sdlc" / "policy"
        policy_dir.mkdir(parents=True)
        policy_dir.joinpath("sdlc-policy.json").write_text(
            json.dumps(
                {
                    "default_profile": "standard",
                    "profiles": {"standard": {}},
                    "change_classes": {
                        "trivial": {"requires_change": False},
                        "standard": {"requires_change": True},
                    },
                }
            ),
            encoding="utf-8",
        )

    def test_active_change_resolves_known_change(self) -> None:
        change = self.write_change("0001-safe.md")
        self.write_state("sdlc_artifacts/changes/0001-safe.md")
        self.assertEqual(active_change_path(self.root), change.resolve())

    def test_active_change_rejects_external_absolute_path(self) -> None:
        external = self.root / "approved-looking.md"
        external.write_text("- **Status**: Approved\n", encoding="utf-8")
        self.write_state(str(external))
        self.assertIsNone(active_change_path(self.root))
        changes, error = resolve_gate_changes(self.root)
        self.assertEqual(changes, [])
        self.assertEqual(error[0], "active_change_not_approved")

    def test_external_path_does_not_fall_back_to_matching_local_basename(self) -> None:
        local = self.write_change("0001-safe.md")
        external_dir = self.root / "external"
        external_dir.mkdir()
        external = external_dir / local.name
        external.write_text("- **Status**: Approved\n", encoding="utf-8")
        self.write_state(str(external))
        self.assertIsNone(active_change_path(self.root))

    def test_active_change_must_be_in_approved_set(self) -> None:
        self.write_change("0001-approved.md")
        proposed = self.write_change("0002-proposed.md", "Proposed")
        self.write_state(str(proposed))
        changes, error = resolve_gate_changes(self.root)
        self.assertEqual(changes, [])
        self.assertEqual(error[0], "active_change_not_approved")

    def test_gate_allows_single_approved_change(self) -> None:
        self.write_change("0001-approved.md")
        allowed, message = evaluate_implementation_gate(self.root)
        self.assertTrue(allowed)
        self.assertEqual(message, "")

    def test_unreadable_adr_fails_closed(self) -> None:
        self.assertFalse(adr_is_accepted(self.root / "missing.md"))

    def test_trivial_active_work_does_not_require_proposal(self) -> None:
        self.install_policy()
        (self.root / "sdlc_artifacts" / "STATE.md").write_text(
            "**Change class**: trivial\n", encoding="utf-8"
        )
        allowed, message = evaluate_implementation_gate(self.root)
        self.assertTrue(allowed)
        self.assertEqual(message, "")


if __name__ == "__main__":
    unittest.main()
