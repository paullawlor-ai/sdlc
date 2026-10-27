from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _policy import change_requirements, load_policy  # noqa: E402
from generate_adapters import generate, outputs  # noqa: E402


class PolicyTests(unittest.TestCase):
    def test_policy_loads(self) -> None:
        policy = load_policy()
        self.assertEqual(policy["schema_version"], 1)
        self.assertIn(policy["default_profile"], policy["profiles"])

    def test_profile_adjusts_completion_review(self) -> None:
        self.assertFalse(
            change_requirements("trivial", "standard")["requires_security_review"]
        )
        self.assertTrue(
            change_requirements("trivial", "regulated")["requires_security_review"]
        )
        self.assertFalse(
            change_requirements("standard", "standard")["require_committed_evidence"]
        )
        self.assertTrue(
            change_requirements("standard", "regulated")["require_committed_evidence"]
        )

    def test_human_review_is_required_by_profile_or_risk(self) -> None:
        self.assertEqual(
            change_requirements("standard", "lite")["review_signoff"],
            "agent_recommendation",
        )
        self.assertEqual(
            change_requirements("standard", "standard")["review_signoff"],
            "human_change_transition",
        )
        self.assertTrue(
            change_requirements("standard", "regulated")["requires_human_review"]
        )
        self.assertTrue(
            change_requirements("high-risk", "lite")["requires_human_review"]
        )

    def test_all_generated_adapters_fit_budget(self) -> None:
        policy = load_policy()
        budget = policy["token_budgets"]["always_on_adapter"]
        for path, content in outputs(policy).items():
            estimate = len(content) // 4
            self.assertLessEqual(estimate, budget, str(path))

    def test_checked_in_adapters_are_generated(self) -> None:
        self.assertTrue(generate(check=True))


if __name__ == "__main__":
    unittest.main()
