from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _artifacts import (  # noqa: E402
    artifact_token_report,
    artifact_index,
    metadata_root,
    initialize_metadata,
    migrate_metadata,
    propose_artifact,
    rollback_metadata,
    validate_artifacts,
    validate_diagnostics,
    sync_artifact_metadata,
    write_index,
)


def complete_change(status: str = "Draft", date: str | None = None) -> str:
    approval_date = f"- **Date**: {date}\n" if date else ""
    return (
        "# Change 0001 - Validate artifacts\n"
        "## Summary\nValidate reviewable artifacts before implementation begins.\n"
        "## Scope\n- **Risk class**: standard\n- **Policy profile**: standard\n"
        "- **Components affected**: SDLC validation\n"
        "## Dependencies\n- **Blocking ADRs**: None\n- **Blocking changes**: None\n"
        "- **External dependencies**: None\n"
        "## Proposed Approach\nApply deterministic completeness checks at proposal time.\n"
        "## Acceptance Criteria\n"
        "| ID | Criterion | Test ID |\n|---|---|---|\n"
        "| AC-01 | Given a complete draft, when proposed, then promotion succeeds | unit |\n"
        "## Testing\n- **Unit tests**: Exercise complete and incomplete drafts\n"
        "- **Integration tests**: Verify the CLI promotion command\n"
        "- **Negative / abuse cases**: Reject missing and placeholder content\n"
        f"## Approval\n- **Status**: {status}\n{approval_date}"
    )


def complete_adr(status: str = "Draft") -> str:
    return (
        "# ADR-0001 - Metadata strategy\n## Status\n"
        f"- **Current status**: {status}\n"
        "## Context\nArtifact metadata needs deterministic machine-readable state.\n"
        "## Decision Drivers\n1. Preserve human-readable Markdown\n2. Detect metadata drift\n"
        "## Options Considered\n### Option A: Derived sidecars\n"
        "**Description**: Generate JSON metadata from Markdown.\n"
        "### Option B: Embedded front matter\n"
        "**Description**: Store machine fields inside Markdown.\n"
        "## Decision\nUse derived JSON sidecars for metadata.\n"
        "## Justification\nThis preserves the existing human review surface.\n"
        "## Consequences\n### Positive\n- Automation gets deterministic fields\n"
        "### Negative\n- Sidecars require synchronization\n"
        "## Security Notes\n- **Threats considered**: Metadata tampering\n"
        "- **Mitigations required**: Drift validation\n"
        "- **Controls to implement**: Atomic sidecar writes\n"
        "## Rollback / Reversal Plan\nRemove sidecars and continue from Markdown.\n"
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
        change.write_text(complete_change("Approved"), encoding="utf-8")
        index = artifact_index(self.root)
        self.assertEqual(index["schema_version"], 1)
        self.assertEqual(index["artifacts"][0]["status"], "Approved")
        self.assertEqual(validate_artifacts(self.root), [])

    def test_invalid_status_is_reported(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text("## Approval\n- **Status**: Maybe\n", encoding="utf-8")
        self.assertIn("invalid change status", validate_artifacts(self.root)[0])
        diagnostics = validate_diagnostics(self.root)
        self.assertEqual(diagnostics[0].code, "INVALID_ARTIFACT_STATUS")
        self.assertEqual(diagnostics[0].path, "sdlc_artifacts/changes/0001-example.md")

    def test_unresolved_dependency_has_stable_diagnostic(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text(
            "## Dependencies\n- REQ-9999\n## Approval\n- **Status**: Draft\n",
            encoding="utf-8",
        )
        diagnostics = validate_diagnostics(self.root)
        self.assertTrue(
            any(item.code == "UNRESOLVED_DEPENDENCY" for item in diagnostics)
        )

    def test_non_iso_human_date_is_warning(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text(complete_change("Approved", "21/10/2026"), encoding="utf-8")
        diagnostics = validate_diagnostics(self.root)
        self.assertTrue(
            any(item.code == "NON_ISO_APPROVAL_DATE" for item in diagnostics)
        )
        self.assertEqual(validate_artifacts(self.root), [])

    def test_conflicting_status_text_is_warning(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text(
            "## Summary\nStatus: Draft.\n"
            "## Approval\n- **Status**: Approved\n- **Date**: 2026-10-22\n",
            encoding="utf-8",
        )
        diagnostics = validate_diagnostics(self.root)
        self.assertTrue(any(item.code == "STATUS_CONFLICT" for item in diagnostics))

    def test_draft_template_is_allowed_but_proposed_template_is_rejected(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text(
            "## Summary\nWhat changed (1-3 sentences).\n"
            "## Approval\n- **Status**: Draft\n",
            encoding="utf-8",
        )
        self.assertEqual(validate_artifacts(self.root), [])
        change.write_text(
            change.read_text(encoding="utf-8").replace("Draft", "Proposed"),
            encoding="utf-8",
        )
        self.assertTrue(
            any(
                "unresolved template placeholder" in item
                for item in validate_artifacts(self.root)
            )
        )

    def test_incomplete_proposed_artifact_reports_required_sections(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text(
            "## Summary\nImplement validation consistently.\n"
            "## Approval\n- **Status**: Proposed\n",
            encoding="utf-8",
        )
        codes = [item.code for item in validate_diagnostics(self.root)]
        self.assertIn("ARTIFACT_SECTION_MISSING", codes)

    def test_choice_lists_empty_fields_and_sample_criteria_are_incomplete(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        content = complete_change("Proposed")
        content = content.replace(
            "- **Risk class**: standard",
            "- **Risk class**: trivial | standard | high-risk",
        )
        content = content.replace(
            "- **Components affected**: SDLC validation",
            "- **Components affected**:",
        )
        content = content.replace(
            "Given a complete draft, when proposed, then promotion succeeds",
            "Given [context], when [action], then [result]",
        )
        change.write_text(content, encoding="utf-8")
        codes = [item.code for item in validate_diagnostics(self.root)]
        self.assertIn("ARTIFACT_FIELD_INCOMPLETE", codes)
        self.assertIn("ARTIFACT_CONTENT_INCOMPLETE", codes)

    def test_approval_queue_excludes_drafts(self) -> None:
        draft = self.root / "sdlc_artifacts" / "changes" / "0001-draft.md"
        proposed = self.root / "sdlc_artifacts" / "changes" / "0002-proposed.md"
        draft.write_text(complete_change(), encoding="utf-8")
        proposed.write_text(complete_change("Proposed"), encoding="utf-8")
        index = artifact_index(self.root)
        self.assertEqual(len(index["artifacts"]), 2)
        self.assertEqual(
            [item["artifact_id"] for item in index["approval_queue"]], ["0002"]
        )

    def test_propose_rejects_scaffold_and_promotes_completed_draft(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text(
            "## Summary\nWhat changed (1-3 sentences).\n"
            "## Approval\n- **Status**: Draft\n",
            encoding="utf-8",
        )
        self.assertEqual(
            propose_artifact(self.root, change)[0].code, "ARTIFACT_PLACEHOLDER"
        )
        change.write_text(complete_change(), encoding="utf-8")
        self.assertEqual(propose_artifact(self.root, change), [])
        self.assertIn("**Status**: Proposed", change.read_text(encoding="utf-8"))

    def test_propose_promotes_complete_adr(self) -> None:
        adr = (
            self.root
            / "sdlc_artifacts"
            / "decisions"
            / "proposed"
            / "ADR-0001-metadata.md"
        )
        adr.parent.mkdir(parents=True)
        adr.write_text(complete_adr(), encoding="utf-8")
        self.assertEqual(propose_artifact(self.root, adr), [])
        self.assertIn("**Current status**: Proposed", adr.read_text(encoding="utf-8"))

    def test_propose_normalizes_project_root_for_changes_and_adrs(self) -> None:
        (self.root / "alternate spelling").mkdir()
        alias = self.root / "alternate spelling" / ".."
        for relative, content in (
            ("changes/0001-example.md", complete_change()),
            ("decisions/proposed/ADR-0001-metadata.md", complete_adr()),
        ):
            with self.subTest(relative=relative):
                artifact = self.root / "sdlc_artifacts" / relative
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_text(content, encoding="utf-8")
                self.assertEqual(propose_artifact(alias, artifact.resolve()), [])
                self.assertIn(": Proposed", artifact.read_text(encoding="utf-8"))

    def test_propose_reports_incomplete_artifact_under_noncanonical_root(self) -> None:
        (self.root / "alternate spelling").mkdir()
        alias = self.root / "alternate spelling" / ".."
        artifact = self.root / "sdlc_artifacts/changes/0001-example.md"
        artifact.write_text(
            "## Summary\nWhat changed (1-3 sentences).\n"
            "## Approval\n- **Status**: Draft\n",
            encoding="utf-8",
        )
        before = artifact.read_bytes()
        diagnostic = propose_artifact(alias, artifact.resolve())[0]
        self.assertEqual(diagnostic.code, "ARTIFACT_PLACEHOLDER")
        self.assertEqual(diagnostic.path, "sdlc_artifacts/changes/0001-example.md")
        self.assertEqual(artifact.read_bytes(), before)

    def test_propose_keeps_artifact_boundary_under_noncanonical_root(self) -> None:
        (self.root / "alternate spelling").mkdir()
        alias = self.root / "alternate spelling" / ".."
        outside = self.root / "outside.md"
        outside.write_text(complete_change(), encoding="utf-8")
        before = outside.read_bytes()
        diagnostic = propose_artifact(alias, alias / "outside.md")[0]
        self.assertEqual(diagnostic.code, "ARTIFACT_PATH_INVALID")
        self.assertEqual(outside.read_bytes(), before)

    def test_oversized_state_is_warning(self) -> None:
        state = self.root / "sdlc_artifacts" / "STATE.md"
        state.write_text("# State\n" + ("history " * 700), encoding="utf-8")
        diagnostics = validate_diagnostics(self.root)
        self.assertTrue(
            any(item.code == "STATE_CONTEXT_OVERSIZE" for item in diagnostics)
        )

    def test_oversized_artifact_reports_measured_and_target_tokens(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text(
            "## Summary\n"
            + ("detailed evidence " * 800)
            + "\n## Approval\n- **Status**: Draft\n",
            encoding="utf-8",
        )
        measurements = artifact_token_report(self.root)
        self.assertEqual(measurements[0]["artifact_type"], "change")
        self.assertGreater(measurements[0]["approx_tokens"], 2500)
        self.assertEqual(
            measurements[0]["approx_tokens"],
            measurements[0]["context_approx_tokens"],
        )
        self.assertGreaterEqual(
            measurements[0]["total_approx_tokens"],
            measurements[0]["context_approx_tokens"],
        )
        diagnostic = next(
            item
            for item in validate_diagnostics(self.root)
            if item.code == "ARTIFACT_CONTEXT_OVERSIZE"
        )
        self.assertEqual(diagnostic.severity, "warning")
        self.assertIn("target 1200", diagnostic.message)
        self.assertIn("warning threshold 2500", diagnostic.message)

    def test_detailed_requirement_is_not_penalized_for_authoritative_length(
        self,
    ) -> None:
        requirement = (
            self.root
            / "sdlc_artifacts"
            / "requirements"
            / "REQ-0001-detailed-design.md"
        )
        requirement.parent.mkdir(parents=True)
        requirement.write_text(
            "## Summary\nPreserve the nuanced product boundary.\n"
            "## Description\n"
            + ("Detailed stakeholder nuance and edge case. " * 800)
            + "\n## Approval\n- **Status**: Draft\n",
            encoding="utf-8",
        )
        measurement = next(
            item
            for item in artifact_token_report(self.root)
            if item["artifact_type"] == "requirement"
        )
        self.assertGreater(measurement["total_approx_tokens"], 3000)
        self.assertLess(measurement["context_approx_tokens"], 1500)
        self.assertFalse(
            any(
                item.code == "ARTIFACT_CONTEXT_OVERSIZE"
                and item.path
                == "sdlc_artifacts/requirements/REQ-0001-detailed-design.md"
                for item in validate_diagnostics(self.root)
            )
        )

    def test_requirement_context_limit_remains_informational_when_regulated(
        self,
    ) -> None:
        artifacts = self.root / "sdlc_artifacts"
        artifacts.joinpath("config.json").write_text(
            '{"schema_version": 1, "profile": "regulated"}\n',
            encoding="utf-8",
        )
        requirement = artifacts / "requirements" / "REQ-0001-summary.md"
        requirement.parent.mkdir(parents=True)
        requirement.write_text(
            "## Summary\n"
            + ("summary repetition " * 800)
            + "\n## Approval\n- **Status**: Draft\n",
            encoding="utf-8",
        )
        diagnostic = next(
            item
            for item in validate_diagnostics(self.root)
            if item.code == "ARTIFACT_CONTEXT_OVERSIZE"
        )
        self.assertEqual(diagnostic.severity, "info")
        self.assertIn("Preserve authoritative detail", diagnostic.message)

    def test_regulated_profile_enforces_artifact_context_limit(self) -> None:
        artifacts = self.root / "sdlc_artifacts"
        artifacts.joinpath("config.json").write_text(
            '{"schema_version": 1, "profile": "regulated"}\n',
            encoding="utf-8",
        )
        artifacts.joinpath("changes", "0001-example.md").write_text(
            "## Summary\n"
            + ("detailed evidence " * 800)
            + "\n## Approval\n- **Status**: Draft\n",
            encoding="utf-8",
        )
        diagnostic = next(
            item
            for item in validate_diagnostics(self.root)
            if item.code == "ARTIFACT_CONTEXT_OVERSIZE"
        )
        self.assertEqual(diagnostic.severity, "error")

    def test_compatibility_mode_warns_without_blocking(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text("## Approval\n- **Status**: Draft\n", encoding="utf-8")
        diagnostics = validate_diagnostics(self.root)
        self.assertTrue(
            any(item.code == "METADATA_COMPATIBILITY_MODE" for item in diagnostics)
        )
        self.assertEqual(validate_artifacts(self.root), [])

    def test_invalid_metadata_mode_has_stable_error(self) -> None:
        artifacts = self.root / "sdlc_artifacts"
        artifacts.joinpath("config.json").write_text(
            '{"schema_version": 1, "profile": "standard", '
            '"metadata_mode": "requiredd"}\n',
            encoding="utf-8",
        )
        artifacts.joinpath("changes", "0001-example.md").write_text(
            "## Approval\n- **Status**: Draft\n", encoding="utf-8"
        )
        diagnostic = next(
            item
            for item in validate_diagnostics(self.root)
            if item.code == "CONFIG_METADATA_MODE_INVALID"
        )
        self.assertEqual(diagnostic.severity, "error")
        self.assertEqual(diagnostic.path, "sdlc_artifacts/config.json")

    def test_required_metadata_must_be_initialized_and_current(self) -> None:
        artifacts = self.root / "sdlc_artifacts"
        artifacts.joinpath("config.json").write_text(
            '{"schema_version": 1, "profile": "standard", "metadata_mode": "required"}\n',
            encoding="utf-8",
        )
        change = artifacts / "changes" / "0001-example.md"
        change.write_text("## Approval\n- **Status**: Draft\n", encoding="utf-8")
        self.assertTrue(
            any("not initialized" in item for item in validate_artifacts(self.root))
        )
        self.assertEqual(validate_diagnostics(self.root)[0].code, "METADATA_REQUIRED")
        initialize_metadata(self.root)
        self.assertTrue(
            any(
                "missing structured metadata" in item
                for item in validate_artifacts(self.root)
            )
        )
        self.assertTrue(
            any(
                item.code == "METADATA_MISSING"
                for item in validate_diagnostics(self.root)
            )
        )
        migrate_metadata(self.root, apply=True)
        self.assertEqual(validate_artifacts(self.root), [])

    def test_single_artifact_sync_does_not_hide_other_drift(self) -> None:
        first = self.root / "sdlc_artifacts" / "changes" / "0001-first.md"
        second = self.root / "sdlc_artifacts" / "changes" / "0002-second.md"
        first.write_text(complete_change(), encoding="utf-8")
        second.write_text(complete_change(), encoding="utf-8")
        migrate_metadata(self.root, apply=True)
        first.write_text(complete_change("Proposed"), encoding="utf-8")
        second.write_text(complete_change("Proposed"), encoding="utf-8")
        sync_artifact_metadata(self.root, second)
        errors = validate_artifacts(self.root)
        self.assertTrue(
            any(
                "0001-first.md: structured metadata is stale" in item for item in errors
            )
        )
        self.assertFalse(
            any(
                "0002-second.md: structured metadata is stale" in item
                for item in errors
            )
        )
        diagnostics = validate_diagnostics(self.root)
        self.assertEqual(
            [item.code for item in diagnostics if item.severity == "error"],
            ["METADATA_STALE"],
        )

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
        sidecar = (
            self.root / "sdlc_artifacts" / ".sdlc" / "metadata" / "change-0001.json"
        )
        self.assertTrue(sidecar.is_file())
        change.write_text("## Approval\n- **Status**: Implemented\n", encoding="utf-8")
        self.assertTrue(
            any("stale" in error for error in validate_artifacts(self.root))
        )

    def test_metadata_migration_backup_can_be_restored(self) -> None:
        change = self.root / "sdlc_artifacts" / "changes" / "0001-example.md"
        change.write_text("## Approval\n- **Status**: Approved\n", encoding="utf-8")
        migrate_metadata(self.root, apply=True)
        change.write_text("## Approval\n- **Status**: Implemented\n", encoding="utf-8")
        result = migrate_metadata(self.root, apply=True)
        self.assertIsNotNone(result["backup"])
        rollback_metadata(self.root, result["backup"])
        sidecar = (
            self.root / "sdlc_artifacts" / ".sdlc" / "metadata" / "change-0001.json"
        )
        self.assertEqual(
            json.loads(sidecar.read_text(encoding="utf-8"))["status"], "Approved"
        )
        index = json.loads(
            self.root.joinpath("sdlc_artifacts", "index.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(index["artifacts"][0]["status"], "Approved")

    def test_required_mode_adoption_dry_run_apply_and_rollback(self) -> None:
        artifacts = self.root / "sdlc_artifacts"
        config = artifacts / "config.json"
        config.write_text(
            '{"schema_version": 1, "profile": "standard", '
            '"metadata_mode": "compatibility"}\n',
            encoding="utf-8",
        )
        artifacts.joinpath("changes", "0001-example.md").write_text(
            "## Approval\n- **Status**: Draft\n", encoding="utf-8"
        )
        preview = migrate_metadata(self.root, target_mode="required")
        self.assertTrue(preview["mode_change"])
        self.assertFalse(preview["applied"])
        self.assertFalse(metadata_root(self.root).exists())
        self.assertIn("compatibility", config.read_text(encoding="utf-8"))

        applied = migrate_metadata(self.root, apply=True, target_mode="required")
        self.assertIsNotNone(applied["backup"])
        self.assertEqual(
            json.loads(config.read_text(encoding="utf-8"))["metadata_mode"],
            "required",
        )
        self.assertTrue(metadata_root(self.root).is_dir())
        self.assertTrue(artifacts.joinpath("index.json").is_file())

        rollback_metadata(self.root, applied["backup"])
        self.assertEqual(
            json.loads(config.read_text(encoding="utf-8"))["metadata_mode"],
            "compatibility",
        )
        self.assertFalse(metadata_root(self.root).exists())
        self.assertFalse(artifacts.joinpath("index.json").exists())


if __name__ == "__main__":
    unittest.main()
