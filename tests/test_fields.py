from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _fields import (  # noqa: E402
    canonical_status,
    field_in_section,
    human_dates,
    protected_approval_values,
    status_declarations_outside_canonical,
)


class CanonicalFieldTests(unittest.TestCase):
    def test_status_comes_only_from_authoritative_section(self) -> None:
        text = "## Summary\nStatus: Draft.\n## Approval\n- **Status**: Approved\n"
        self.assertEqual(canonical_status(text, "change"), "Approved")
        self.assertEqual(
            status_declarations_outside_canonical(text, "change"), ["Draft"]
        )

    def test_review_recommendation_uses_agent_section(self) -> None:
        text = "## Agent Recommendation\n- **Recommendation**: Approved with notes\n"
        self.assertEqual(canonical_status(text, "review"), "Approved with notes")

    def test_human_dates_ignore_session_handoff(self) -> None:
        text = (
            "## Approval\n- **Date**: 21/10/2026\n"
            "## Last Session Summary\n- **Date**: 2026-10-25\n"
        )
        self.assertEqual(human_dates(text), ["21/10/2026"])
        self.assertEqual(
            field_in_section(text, "Last Session Summary", "Date"), "2026-10-25"
        )

    def test_blank_review_date_does_not_consume_notes_field(self) -> None:
        text = (
            "## Approval\n"
            "<!-- HUMAN-ONLY reviewer fields. -->\n"
            "- **Reviewer**:\n"
            "- **Date**:\n"
            "- **Notes**:\n"
        )
        self.assertIsNone(field_in_section(text, "Approval", "Date"))
        self.assertEqual(human_dates(text), [])

    def test_protected_values_include_legacy_date_identity_and_verdict(self) -> None:
        text = (
            "## Summary Verdict\n- [x] Approved with notes\n"
            "## Approval\n- **Status**: Approved\n"
            "- **Reviewer**: Paul\n- **Date**: 21/10/2026\n"
        )
        values = protected_approval_values(text)
        self.assertIn("status:approved", values)
        self.assertIn("reviewer:paul", values)
        self.assertIn("date:21/10/2026", values)
        self.assertIn("verdict:approved with notes", values)

    def test_approved_digest_is_human_only_but_reviewed_digest_is_agent_writable(
        self,
    ) -> None:
        text = "## Reviewed Artifacts\n- **Reviewed source digest**: new\n"
        self.assertEqual(protected_approval_values(text), [])
        text += "## Approval\n- **Approved source digest**: previous\n"
        self.assertIn(
            "approved source digest:previous", protected_approval_values(text)
        )


if __name__ == "__main__":
    unittest.main()
