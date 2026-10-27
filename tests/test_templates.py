from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TemplateTests(unittest.TestCase):
    def test_starter_quality_configuration_matches_framework(self) -> None:
        for starter in (ROOT / "templates/projects").iterdir():
            for name in ("ruff.toml", "requirements-dev.txt"):
                self.assertEqual(
                    (starter / name).read_bytes(), (ROOT / name).read_bytes()
                )

    def test_all_template_python_parses(self) -> None:
        files = list((ROOT / "templates" / "projects").rglob("*.py"))
        self.assertTrue(files)
        for path in files:
            with self.subTest(path=path):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_requirements_do_not_repeat_packages(self) -> None:
        for path in (ROOT / "templates" / "projects").rglob("requirements.txt"):
            names = []
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.split("#", 1)[0].strip()
                if not line:
                    continue
                names.append(re.split(r"[<>=!~\[]", line, maxsplit=1)[0].lower())
            with self.subTest(path=path):
                self.assertEqual(len(names), len(set(names)))

    def test_review_template_contains_agent_recommendation(self) -> None:
        review = (ROOT / "templates" / "documents" / "review.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("## Agent Recommendation", review)
        self.assertIn("never a human sign-off", review)
        self.assertIn(
            "required for regulated profiles and every high-risk change", review
        )

    def test_governed_templates_use_compact_summary_and_linked_evidence(self) -> None:
        templates = {
            "requirement.md": "## Summary",
            "adr.md": "## Decision Summary",
            "change-proposal.md": "## Summary",
            "review.md": "## Agent Recommendation",
            "test-plan.md": "## Overview",
        }
        root = ROOT / "templates" / "documents"
        for filename, summary_heading in templates.items():
            with self.subTest(filename=filename):
                text = root.joinpath(filename).read_text(encoding="utf-8")
                self.assertIn(summary_heading, text)
                self.assertIn("## Evidence References", text)
                self.assertRegex(text, r"(?i)(link|ordinary-context)")


if __name__ == "__main__":
    unittest.main()
