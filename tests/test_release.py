from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from release_check import release_errors  # noqa: E402


class ReleaseTests(unittest.TestCase):
    def test_release_sources_agree(self) -> None:
        self.assertEqual(release_errors(), [])

    def test_version_drift_and_missing_release_notes_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("adapters", "policy", "docs"):
                shutil.copytree(ROOT / name, root / name)
            shutil.copy2(ROOT / "CHANGELOG.md", root / "CHANGELOG.md")
            (root / "VERSION").write_text("9.9.9\n", encoding="utf-8")
            errors = release_errors(root)
            self.assertIn("VERSION and policy framework_version differ", errors)
            self.assertIn("CHANGELOG.md has no entry for 9.9.9", errors)

    def test_stale_adapter_and_invalid_version_fail_release_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("adapters", "policy", "docs"):
                shutil.copytree(ROOT / name, root / name)
            shutil.copy2(ROOT / "CHANGELOG.md", root / "CHANGELOG.md")
            (root / "VERSION").write_text("not a version", encoding="utf-8")
            policy_path = root / "policy/sdlc-policy.json"
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            policy["rules"]["R1"] = "Modified policy without regenerating adapters."
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            errors = release_errors(root)
            self.assertTrue(any("semantic version" in item for item in errors))
            self.assertTrue(any("adapter is stale" in item for item in errors))
