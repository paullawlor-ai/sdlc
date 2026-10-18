from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import _setup  # noqa: E402


class SetupTests(unittest.TestCase):
    def test_hook_command_quotes_executable_and_script(self) -> None:
        with patch.object(_setup.sys, "executable", r"C:\Program Files\Python\python.exe"):
            command = _setup.hook_command("implementation_gate.py")
        self.assertTrue(command.startswith('"C:\\Program Files\\Python\\python.exe"'))
        self.assertIn('"scripts/hooks/implementation_gate.py"', command)

    def test_merge_hooks_is_idempotent(self) -> None:
        additions = {
            "Stop": [{"hooks": [{"type": "command", "command": "state-hook"}]}]
        }
        once = _setup.merge_hooks({}, additions)
        twice = _setup.merge_hooks(once, additions)
        self.assertEqual(once, twice)

    def test_managed_section_preserves_user_content_and_upgrades(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            adapters = root / "sources"
            source = adapters / "codex" / "AGENTS.md"
            source.parent.mkdir(parents=True)
            source.write_text("version one", encoding="utf-8")
            lines = _setup.install_managed_adapters(root, adapters, {"codex"})
            self.assertIn("Installed", lines[0])
            destination = root / "AGENTS.md"
            destination.write_text(
                destination.read_text(encoding="utf-8") + "\nlocal content\n",
                encoding="utf-8",
            )
            source.write_text("version two", encoding="utf-8")
            lines = _setup.install_managed_adapters(
                root, adapters, {"codex"}, upgrade=True
            )
            self.assertIn("Updated", lines[0])
            installed = destination.read_text(encoding="utf-8")
            self.assertIn("version two", installed)
            self.assertIn("local content", installed)

    def test_managed_upgrade_rejects_edit_inside_managed_section(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            adapters = root / "sources"
            source = adapters / "codex" / "AGENTS.md"
            source.parent.mkdir(parents=True)
            source.write_text("version one", encoding="utf-8")
            _setup.install_managed_adapters(root, adapters, {"codex"})
            destination = root / "AGENTS.md"
            destination.write_text(
                destination.read_text(encoding="utf-8").replace("version one", "local managed edit"),
                encoding="utf-8",
            )
            source.write_text("version two", encoding="utf-8")
            lines = _setup.install_managed_adapters(root, adapters, {"codex"}, upgrade=True)
            self.assertIn("Skipped local modification", lines[0])
            self.assertIn("local managed edit", destination.read_text(encoding="utf-8"))

    def test_upgrade_backup_can_be_restored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            adapters = root / "sources"
            source = adapters / "codex" / "AGENTS.md"
            source.parent.mkdir(parents=True)
            source.write_text("version one", encoding="utf-8")
            _setup.install_managed_adapters(root, adapters, {"codex"})
            source.write_text("version two", encoding="utf-8")
            _setup.install_managed_adapters(root, adapters, {"codex"}, upgrade=True)
            restored = _setup.rollback_managed_adapters(root)
            self.assertEqual(restored, [".sdlc-install.json", "AGENTS.md"])
            self.assertIn("version one", root.joinpath("AGENTS.md").read_text(encoding="utf-8"))
            manifest = _setup.load_install_manifest(root)
            managed = _setup._extract_managed(root.joinpath("AGENTS.md").read_text(encoding="utf-8"))
            self.assertEqual(manifest["files"]["AGENTS.md"]["installed_sha256"], _setup._text_hash(managed))

    def test_all_file_assistants_install_selectively(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            adapters = root / "sources"
            files = (
                adapters / "codex" / "AGENTS.md",
                adapters / "copilot" / "copilot-instructions.md",
                adapters / "copilot" / "instructions" / "sdlc.instructions.md",
                adapters / "cursor" / "rules" / "core.mdc",
            )
            for path in files:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(path.name, encoding="utf-8")
            _setup.install_managed_adapters(
                root, adapters, {"codex", "copilot", "cursor"}
            )
            manifest = _setup.load_install_manifest(root)
            self.assertEqual(manifest["schema_version"], 2)
            self.assertEqual(manifest["assistants"], ["codex", "copilot", "cursor"])
            self.assertTrue(root.joinpath("AGENTS.md").is_file())
            self.assertTrue(root.joinpath(".github", "copilot-instructions.md").is_file())
            self.assertTrue(root.joinpath(".cursor", "rules", "core.mdc").is_file())


if __name__ == "__main__":
    unittest.main()
