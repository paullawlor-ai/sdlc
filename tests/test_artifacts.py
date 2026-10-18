from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _artifacts import (  # noqa: E402
    artifact_index,
    metadata_path,
    migrate_metadata,
    rollback_metadata,
    validate_artifacts,
    write_index,
)


class ArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "sdlc_artifacts" / "changes").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_index_contains_structured_change(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text(
            "# Change 0001\n- **Risk class**: standard\n"
            "## Approval\n- **Status**: Approved\n",
            encoding="utf-8",
        )
        index = artifact_index(self.root)
        self.assertEqual(index["schema_version"], 1)
        self.assertEqual(index["artifacts"][0]["status"], "Approved")
        self.assertEqual(validate_artifacts(self.root), [])

    def test_invalid_status_is_reported(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text("## Approval\n- **Status**: Maybe\n", encoding="utf-8")
        self.assertIn("invalid change status", validate_artifacts(self.root)[0])

    def test_index_can_be_written(self) -> None:
        destination = write_index(self.root)
        data = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)

    def test_migration_writes_sidecars_and_detects_drift(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text("## Approval\n- **Status**: Approved\n", encoding="utf-8")
        preview = migrate_metadata(self.root)
        self.assertFalse(preview["applied"])
        self.assertEqual(len(preview["changes"]), 1)
        applied = migrate_metadata(self.root, apply=True)
        self.assertTrue(applied["applied"])
        artifact = artifact_index(self.root)["artifacts"][0]
        sidecar = self.root / "sdlc_artifacts" / ".sdlc" / "metadata" / "change-0001.json"
        self.assertTrue(sidecar.is_file())
        change.write_text("## Approval\n- **Status**: Implemented\n", encoding="utf-8")
        self.assertTrue(any("stale" in error for error in validate_artifacts(self.root)))

    def test_metadata_migration_backup_can_be_restored(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text("## Approval\n- **Status**: Approved\n", encoding="utf-8")
        migrate_metadata(self.root, apply=True)
        change.write_text("## Approval\n- **Status**: Implemented\n", encoding="utf-8")
        result = migrate_metadata(self.root, apply=True)
        self.assertIsNotNone(result["backup"])
        rollback_metadata(self.root, result["backup"])
        sidecar = self.root / "sdlc_artifacts" / ".sdlc" / "metadata" / "change-0001.json"
        self.assertEqual(json.loads(sidecar.read_text(encoding="utf-8"))["status"], "Approved")


if __name__ == "__main__":
    unittest.main()
