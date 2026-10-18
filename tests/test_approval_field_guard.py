from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "scripts" / "hooks"
sys.path.insert(0, str(HOOKS))

from approval_field_guard import (  # noqa: E402
    content_before_after,
    protected_snapshot,
)


class ApprovalFieldGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "change.md"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_unrelated_edit_preserves_approved_snapshot(self) -> None:
        self.path.write_text(
            "## Summary\nOld text\n## Approval\n- **Status**: Approved\n",
            encoding="utf-8",
        )
        before, after = content_before_after(
            "Edit",
            {"old_string": "Old text", "new_string": "New text"},
            str(self.path),
        )
        self.assertEqual(protected_snapshot(before), protected_snapshot(after))

    def test_status_change_is_detected(self) -> None:
        self.path.write_text("## Approval\n- **Status**: Proposed\n", encoding="utf-8")
        before, after = content_before_after(
            "Edit",
            {"old_string": "Proposed", "new_string": "Approved"},
            str(self.path),
        )
        self.assertNotEqual(protected_snapshot(before), protected_snapshot(after))

    def test_checked_review_verdict_is_protected(self) -> None:
        before = "## Summary Verdict\n- [ ] Approved\n"
        after = "## Summary Verdict\n- [x] Approved\n"
        self.assertNotEqual(protected_snapshot(before), protected_snapshot(after))

    def test_session_date_is_not_an_approval_field(self) -> None:
        before = "## Last Session Summary\n**Date**: 2026-10-17\n"
        after = "## Last Session Summary\n**Date**: 2026-10-18\n"
        self.assertEqual(protected_snapshot(before), protected_snapshot(after))

    def test_ordinary_approved_checkbox_is_not_a_verdict(self) -> None:
        before = "## Checklist\n- [ ] Approved dependency is present\n"
        after = "## Checklist\n- [x] Approved dependency is present\n"
        self.assertEqual(protected_snapshot(before), protected_snapshot(after))

    def test_multi_edit_operations_are_sequential(self) -> None:
        self.path.write_text("alpha beta", encoding="utf-8")
        before, after = content_before_after(
            "MultiEdit",
            {
                "edits": [
                    {"old_string": "alpha", "new_string": "gamma"},
                    {"old_string": "gamma beta", "new_string": "done"},
                ]
            },
            str(self.path),
        )
        self.assertEqual(before, "alpha beta")
        self.assertEqual(after, "done")


if __name__ == "__main__":
    unittest.main()
