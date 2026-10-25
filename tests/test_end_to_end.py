"""Actual CLI journeys in isolated embedded projects; human actions are simulated.

Scan reports in these fixtures are explicitly synthetic. Real scanner fixtures
and the release scan independently exercise the installed security tools.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from tests.security_fixtures import write_scan_fixture  # noqa: E402
from tests.test_lifecycle import complete_adr, complete_change  # noqa: E402


def embedded_framework(root: Path) -> Path:
    framework = root / "sdlc"
    framework.mkdir(parents=True)
    for name in ("scripts", "templates", "adapters", "policy"):
        shutil.copytree(
            ROOT / name,
            framework / name,
            ignore=shutil.ignore_patterns(
                "__pycache__", ".pytest_cache", ".ruff_cache"
            ),
        )
    shutil.copy2(ROOT / "VERSION", framework / "VERSION")
    return framework


class EndToEndTests(unittest.TestCase):
    def cli(self, root: Path, *arguments: str, expected: int = 0) -> str:
        result = subprocess.run(
            [sys.executable, str(root / "sdlc/scripts/sdlc.py"), *arguments],
            cwd=root,
            env={**os.environ, "SDLC_PROJECT_ROOT": str(root)},
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout

    def test_embedded_setup_to_finalization_for_every_profile(self) -> None:
        for profile in ("lite", "standard", "regulated"):
            with (
                self.subTest(profile=profile),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory) / "host project"
                embedded_framework(root)
                self.cli(root, "setup", "--assistant", "all", "--verify")
                artifacts = root / "sdlc_artifacts"
                config_path = artifacts / "config.json"
                config = json.loads(config_path.read_text(encoding="utf-8"))
                self.assertEqual(config["metadata_mode"], "required")
                config.update(profile=profile, repository_mode="non-git")
                config_path.write_text(json.dumps(config), encoding="utf-8")
                self.cli(root, "new", "requirement", "secure login")
                requirement = next((artifacts / "requirements").glob("REQ-*.md"))
                # Human approval is fixture input, never an assistant action.
                requirement.write_text(
                    "# REQ-0001 - Login\n## Summary\nAuthenticate registered users.\n"
                    "## Acceptance Criteria\n- AC-01: Valid credentials allow login.\n"
                    "## Approval\n- **Status**: Approved\n",
                    encoding="utf-8",
                )
                self.cli(root, "new", "adr", "authentication strategy")
                adr = next((artifacts / "decisions/proposed").glob("ADR-*.md"))
                self.cli(root, "propose", str(adr), expected=1)
                adr.write_text(complete_adr("Draft"), encoding="utf-8")
                self.cli(root, "propose", str(adr))
                adr.write_text(
                    adr.read_text(encoding="utf-8").replace(
                        "**Current status**: Proposed", "**Current status**: Accepted"
                    ),
                    encoding="utf-8",
                )
                accepted = artifacts / "decisions/accepted" / adr.name
                accepted.parent.mkdir(parents=True, exist_ok=True)
                adr.replace(accepted)
                self.cli(root, "new", "change", "secure login")
                change = next((artifacts / "changes").glob("*.md"))
                self.cli(root, "gate", "implementation", expected=2)
                change.write_text(
                    complete_change("Draft", "ADR-0001", "high-risk", profile),
                    encoding="utf-8",
                )
                self.cli(root, "propose", str(change))
                change.write_text(
                    change.read_text(encoding="utf-8").replace(
                        "**Status**: Proposed", "**Status**: Approved"
                    ),
                    encoding="utf-8",
                )
                (artifacts / "STATE.md").write_text(
                    "**Phase**: Implementation\n**Change class**: high-risk\n## Active Change\n"
                    f"- **Change document**: sdlc_artifacts/changes/{change.name}\n",
                    encoding="utf-8",
                )
                self.cli(root, "metadata", "sync", "--apply")
                self.cli(root, "gate", "implementation")
                (root / "app.py").write_text(
                    "def authenticate(valid):\n    return bool(valid)\n",
                    encoding="utf-8",
                )
                tested = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        "from app import authenticate; assert authenticate(True); assert not authenticate(False)",
                    ],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(tested.returncode, 0, tested.stderr)
                self.cli(root, "new", "review", "secure login")
                review = next((artifacts / "reviews").glob("REV-*.md"))
                review.write_text(
                    f"# REV-0001\n## Reviewed Artifacts\n- **Change docs**: {change.name}\n"
                    "- **Requirement**: REQ-0001\n- **ADR**: ADR-0001\n"
                    "## Agent Recommendation\n- **Recommendation**: Approved\n"
                    "## Findings\n### Must-Fix\nNone\n",
                    encoding="utf-8",
                )
                write_scan_fixture(root, review)
                change.write_text(
                    change.read_text(encoding="utf-8")
                    + "\n## Completion Gate\n- **Tests passing**: yes\n"
                    "- **Security review (REV)**: REV-0001\n"
                    "- **Agent recommendation**: Approved\n- **Open must-fix in REV**: 0\n",
                    encoding="utf-8",
                )
                self.cli(root, "metadata", "sync", "--apply")
                before = review.read_bytes()
                blocked = json.loads(
                    self.cli(root, "check", "--ready-to-finalize", "--json", expected=1)
                )
                self.assertFalse(blocked["ready_to_finalize"])
                self.assertIn(
                    "HUMAN_REVIEW_DIGEST_REQUIRED",
                    {item["code"] for item in blocked["diagnostics"]},
                )
                self.assertEqual(before, review.read_bytes())
                evidence = json.loads(
                    (artifacts / "evidence/security.json").read_text(encoding="utf-8")
                )
                review.write_text(
                    review.read_text(encoding="utf-8")
                    + "\n## Summary Verdict\n- [x] Approved\n## Approval\n"
                    "- **Reviewer**: Fixture human\n- **Date**: 2026-10-25\n"
                    f"- **Approved source digest**: {evidence['source_digest']}\n",
                    encoding="utf-8",
                )
                self.cli(root, "metadata", "sync", "--apply")
                self.cli(root, "gate", "completion")
                self.assertTrue(
                    json.loads(
                        self.cli(root, "check", "--ready-to-finalize", "--json")
                    )["ready_to_finalize"]
                )
                change.write_text(
                    change.read_text(encoding="utf-8").replace(
                        "**Status**: Approved", "**Status**: Implemented"
                    ),
                    encoding="utf-8",
                )
                self.cli(root, "metadata", "sync", "--apply")
                self.cli(root, "check", "--strict")
                self.cli(
                    root,
                    "handoff",
                    "--completed",
                    "REQ-0001 implemented and verified",
                    "--left-off",
                    "Ready for next change",
                    "--next-action",
                    "Select next change",
                )

    def test_existing_project_upgrade_preview_and_metadata_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "existing project"
            framework = embedded_framework(root)
            # Install a controlled 0.2.0 adapter fixture, then replace framework
            # sources with the prepared release as an owner would during upgrade.
            policy_path = framework / "policy/sdlc-policy.json"
            previous_policy = json.loads(policy_path.read_text(encoding="utf-8"))
            previous_policy["framework_version"] = "0.2.0"
            policy_path.write_text(json.dumps(previous_policy), encoding="utf-8")
            (framework / "VERSION").write_text("0.2.0\n", encoding="utf-8")
            generated = subprocess.run(
                [sys.executable, str(framework / "scripts/generate_adapters.py")],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            self.cli(root, "setup", "--assistant", "codex")
            shutil.copy2(ROOT / "VERSION", framework / "VERSION")
            shutil.copy2(ROOT / "policy/sdlc-policy.json", policy_path)
            shutil.copytree(
                ROOT / "adapters", framework / "adapters", dirs_exist_ok=True
            )
            (root / "AGENTS.md").write_text(
                (root / "AGENTS.md").read_text(encoding="utf-8")
                + "\nOwner instructions stay here.\n",
                encoding="utf-8",
            )
            artifacts = root / "sdlc_artifacts"
            config = artifacts / "config.json"
            legacy_config = '{"schema_version":1,"profile":"standard"}\n'
            config.write_text(legacy_config, encoding="utf-8")
            shutil.rmtree(artifacts / ".sdlc")
            (artifacts / "index.json").unlink()
            self.cli(root, "new", "change", "legacy approval")
            change = next((artifacts / "changes").glob("*.md"))
            change.write_text(
                complete_change()
                + "- **Approved by**: Fixture owner\n- **Date**: 21/10/2026\n",
                encoding="utf-8",
            )
            original = change.read_bytes()
            install = root / ".sdlc-install.json"
            before = (root / "AGENTS.md").read_bytes()
            self.cli(root, "upgrade")
            self.assertEqual((root / "AGENTS.md").read_bytes(), before)
            self.assertEqual(
                json.loads(install.read_text(encoding="utf-8"))["framework_version"],
                "0.2.0",
            )
            self.cli(root, "upgrade", "--apply")
            self.assertEqual(
                json.loads(install.read_text(encoding="utf-8"))["framework_version"],
                (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
            )
            self.assertIn(
                "Owner instructions stay here.",
                (root / "AGENTS.md").read_text(encoding="utf-8"),
            )
            preview = json.loads(self.cli(root, "metadata", "sync", "--json"))
            self.assertTrue(preview["mode_change"])
            self.assertEqual(config.read_text(encoding="utf-8"), legacy_config)
            self.cli(root, "metadata", "sync", "--apply")
            self.assertEqual(change.read_bytes(), original)
            self.assertEqual(
                json.loads(config.read_text(encoding="utf-8"))["metadata_mode"],
                "required",
            )
            self.cli(root, "migrate", "--rollback")
            self.assertEqual(config.read_text(encoding="utf-8"), legacy_config)
            self.assertEqual(change.read_bytes(), original)
            self.assertFalse((artifacts / ".sdlc/metadata").exists())
            self.cli(root, "upgrade", "--rollback")
            self.assertEqual((root / "AGENTS.md").read_bytes(), before)
            self.assertEqual(
                json.loads(install.read_text(encoding="utf-8"))["framework_version"],
                "0.2.0",
            )
            self.assertEqual(change.read_bytes(), original)
