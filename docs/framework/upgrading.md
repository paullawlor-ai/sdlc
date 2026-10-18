# Upgrading the Framework

Version 0.2 introduces selective, manifest-backed adapter installation.

```bash
python sdlc/scripts/setup_project.py --assistant codex
python sdlc/scripts/setup_project.py --assistant cursor --assistant claude
python sdlc/scripts/setup_project.py --upgrade --dry-run
python sdlc/scripts/setup_project.py --upgrade
# unified CLI previews by default; add --apply to write
python sdlc/scripts/sdlc.py upgrade --apply
python sdlc/scripts/verify_setup.py
```

`.sdlc-install.json` records the framework version, ownership mode, and hashes of
managed adapter content. Shared `AGENTS.md` and Copilot instruction files use an
SDLC-managed section, so user-authored content outside that section survives an
upgrade. Edits inside a managed section are reported as conflicts.

Changed files are backed up under `.sdlc-backups/<timestamp>/`. Restore the latest
backup with `python sdlc/scripts/sdlc.py upgrade --rollback`, or pass
`--backup PATH` to select one explicitly.

Projects installed before 0.2 have no manifest. Run setup with the assistants
actually used by the project. Identical adapters are adopted into the manifest;
different existing files remain untouched for manual reconciliation.

After upgrading, run:

```bash
python sdlc/scripts/sdlc.py check --write-index
python -m unittest discover -s sdlc/tests -v
```
