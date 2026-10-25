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
from sdlc import (  # noqa: E402
    completion_gate,
    context_packet,
    finalization_diagnostics,
    implemented_review_diagnostics,
)
from tests.security_fixtures import write_scan_fixture  # noqa: E402


def complete_change(
    status: str = "Approved",
    blocking_adrs: str = "None",
    risk_class: str = "standard",
    profile: str = "standard",
) -> str:
    return (
        "# Change 0001 - Login\n## Summary\nImplement a secure login workflow.\n"
        f"## Scope\n- **Risk class**: {risk_class}\n- **Policy profile**: {profile}\n"
        "- **Components affected**: authentication service\n"
        f"## Dependencies\n- **Blocking ADRs**: {blocking_adrs}\n"
        "- **Blocking changes**: None\n- **External dependencies**: None\n"
        "## Proposed Approach\nAdd the workflow behind tested service boundaries.\n"
        "## Acceptance Criteria\n| ID | Criterion | Test |\n|---|---|---|\n"
        "| AC-01 | Given valid credentials, when submitted, then login succeeds | unit |\n"
        "## Testing\n- **Unit tests**: Cover authentication outcomes\n"
        "- **Integration tests**: Verify the login endpoint\n"
        "- **Negative / abuse cases**: Reject invalid credentials\n"
        f"## Approval\n- **Status**: {status}\n"
    )


def complete_adr(status: str = "Accepted") -> str:
    return (
        "# ADR-0001 - Authentication\n## Status\n"
        f"- **Current status**: {status}\n"
        "## Context\nAuthentication requires a consistent token strategy.\n"
        "## Decision Drivers\n1. Limit credential exposure\n2. Support reliable revocation\n"
        "## Options Considered\n### Option A: Signed tokens\n"
        "**Description**: Use short-lived signed access tokens.\n"
        "### Option B: Server sessions\n"
        "**Description**: Store opaque sessions on the server.\n"
        "## Decision\nUse short-lived signed access tokens.\n"
        "## Justification\nThis balances isolation, scalability, and operational control.\n"
        "## Consequences\n### Positive\n- Services can validate requests locally\n"
        "### Negative\n- Revocation requires additional coordination\n"
        "## Security Notes\n- **Threats considered**: Token theft and replay\n"
        "- **Mitigations required**: Short expiry and rotation\n"
        "- **Controls to implement**: Secure token storage\n"
        "## Rollback / Reversal Plan\nReturn clients to opaque server sessions.\n"
    )


class LifecycleTests(unittest.TestCase):
    def _write_completion_fixture(
        self,
        root: Path,
        must_fix: str = "None",
        *,
        profile: str = "standard",
        change_class: str = "standard",
        human_review: bool = False,
        status: str = "Approved",
    ) -> None:
        artifacts = root / "sdlc_artifacts"
        changes = artifacts / "changes"
        reviews = artifacts / "reviews"
        changes.mkdir(parents=True)
        reviews.mkdir(parents=True)
        changes.joinpath("0001-login.md").write_text(
            complete_change(
                status=status,
                risk_class=change_class,
                profile=profile,
            )
            + "## Completion Gate\n- **Tests passing**: yes\n"
            "- **Security review (REV)**: REV-0001\n"
            "- **Agent recommendation**: Approved\n"
            "- **Open must-fix in REV**: 0\n",
            encoding="utf-8",
        )
        reviews.joinpath("REV-0001-login.md").write_text(
            "## Reviewed Artifacts\n- **Change docs**: 0001-login.md\n"
            "## Agent Recommendation\n- **Recommendation**: Approved\n"
            f"## Findings\n### Must-Fix\n{must_fix}\n"
            + (
                "## Summary Verdict\n- [x] Approved\n- [ ] Approved with notes\n"
                "- [ ] Needs changes\n- [ ] Rejected\n"
                "## Approval\n### Reviewer Information\n"
                "- **Reviewer**: Paul Lawlor\n- **Date**: 2026-10-25\n"
                if human_review
                else ""
            ),
            encoding="utf-8",
        )
        artifacts.joinpath("STATE.md").write_text(
            f"**Change class**: {change_class}\n## Active Change\n"
            "- **Change document**: sdlc_artifacts/changes/0001-login.md\n",
            encoding="utf-8",
        )
        artifacts.joinpath("config.json").write_text(
            f'{{"schema_version": 1, "profile": "{profile}", '
            '"repository_mode": "non-git"}\n',
            encoding="utf-8",
        )
        write_scan_fixture(root, reviews / "REV-0001-login.md")

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
                complete_adr(),
                encoding="utf-8",
            )
            change = changes / "0001-login.md"
            change.write_text(
                complete_change(blocking_adrs="ADR-0001") + "## Completion Gate\n"
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

            write_scan_fixture(root, reviews / "REV-0001-login.md")
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
                complete_change() + "## Completion Gate\n- **Gate result**: PASS\n",
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

    def test_standard_review_does_not_require_optional_human_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_completion_fixture(root)
            self.assertTrue(completion_gate(root, None, None)[0])
            self.assertEqual(finalization_diagnostics(root), [])

    def test_regulated_review_requires_human_verdict_reviewer_and_date(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_completion_fixture(root, profile="regulated")
            review = root / "sdlc_artifacts" / "reviews" / "REV-0001-login.md"
            before = review.read_text(encoding="utf-8")
            diagnostics = finalization_diagnostics(root)
            self.assertEqual(
                {item.code for item in diagnostics},
                {
                    "HUMAN_REVIEW_VERDICT_REQUIRED",
                    "HUMAN_REVIEWER_REQUIRED",
                    "HUMAN_REVIEW_DATE_REQUIRED",
                    "HUMAN_REVIEW_DIGEST_REQUIRED",
                },
            )
            self.assertEqual(review.read_text(encoding="utf-8"), before)
            self.assertFalse(completion_gate(root, None, None)[0])

    def test_regulated_review_passes_with_complete_human_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_completion_fixture(root, profile="regulated", human_review=True)
            self.assertEqual(finalization_diagnostics(root), [])
            self.assertTrue(completion_gate(root, None, None)[0])

    def test_regulated_review_rejects_conflicting_verdict_and_invalid_date(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_completion_fixture(root, profile="regulated", human_review=True)
            review = root / "sdlc_artifacts" / "reviews" / "REV-0001-login.md"
            text = review.read_text(encoding="utf-8")
            text = text.replace("- [ ] Needs changes", "- [x] Needs changes")
            text = text.replace("2026-10-25", "2026-02-30")
            review.write_text(text, encoding="utf-8")
            codes = {item.code for item in finalization_diagnostics(root)}
            self.assertIn("HUMAN_REVIEW_VERDICT_CONFLICT", codes)
            self.assertIn("HUMAN_REVIEW_DATE_REQUIRED", codes)

    def test_high_risk_lite_review_still_requires_human_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_completion_fixture(
                root, profile="lite", change_class="high-risk"
            )
            state = root / "sdlc_artifacts" / "STATE.md"
            state.write_text(
                state.read_text(encoding="utf-8").replace(
                    "**Change class**: high-risk", "**Change class**: standard"
                ),
                encoding="utf-8",
            )
            codes = {item.code for item in finalization_diagnostics(root)}
            self.assertIn("HUMAN_REVIEW_VERDICT_REQUIRED", codes)

    def test_implemented_regulated_change_without_signoff_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_completion_fixture(
                root, profile="regulated", status="Implemented"
            )
            codes = {item.code for item in implemented_review_diagnostics(root)}
            self.assertIn("HUMAN_REVIEW_VERDICT_REQUIRED", codes)

    def test_compact_artifacts_preserve_gates_and_reduce_active_context(self) -> None:
        with (
            tempfile.TemporaryDirectory() as compact_dir,
            tempfile.TemporaryDirectory() as verbose_dir,
        ):
            compact_root = Path(compact_dir)
            verbose_root = Path(verbose_dir)
            self._write_completion_fixture(compact_root)
            self._write_completion_fixture(verbose_root)

            verbose_change = (
                verbose_root / "sdlc_artifacts" / "changes" / "0001-login.md"
            )
            text = verbose_change.read_text(encoding="utf-8")
            for heading, detail in (
                ("## Summary\n", "background narrative " * 500),
                ("## Dependencies\n", "dependency analysis " * 500),
                ("## Acceptance Criteria\n", "acceptance evidence " * 500),
                ("## Testing\n", "raw test output " * 500),
            ):
                text = text.replace(heading, heading + detail + "\n", 1)
            verbose_change.write_text(text, encoding="utf-8")

            for root in (compact_root, verbose_root):
                self.assertTrue(evaluate_implementation_gate(root)[0])
                self.assertTrue(completion_gate(root, None, None)[0])

            compact_context = context_packet(compact_root, "implementation", 2000)
            verbose_context = context_packet(verbose_root, "implementation", 2000)
            compact_artifact = (
                compact_root / "sdlc_artifacts" / "changes" / "0001-login.md"
            ).read_text(encoding="utf-8")
            self.assertLessEqual(len(compact_artifact), len(text) * 0.60)
            for fact in ("AC-01", "Tests passing", "REV-0001"):
                self.assertIn(fact, compact_context)
                self.assertIn(fact, verbose_context)


if __name__ == "__main__":
    unittest.main()
