# Cursor Rules

These files are generated from `policy/sdlc-policy.json`. Cursor reads installed
copies from the host project's `.cursor/rules/` directory.

```bash
python sdlc/scripts/setup_project.py --assistant cursor
python sdlc/scripts/setup_project.py --assistant cursor --upgrade --dry-run
```

## Files

| File | Loading | Purpose |
| --- | --- | --- |
| `core.mdc` | Always | Orientation, classification, and canonical rules |
| `implementation-gate.mdc` | Always | CLI entry points for both gates |
| `agents.mdc` | On demand | Portable role selection and handoffs |
| `security.mdc` | On demand | Contextual security baseline selection |

Before policy-governed product edits, Cursor runs or follows:

```bash
python sdlc/scripts/sdlc.py gate implementation
```

Before completion, it runs:

```bash
python sdlc/scripts/sdlc.py gate completion
```

Exit code `0` permits progress. Exit code `2` means stop and report the blocker.
The active change class is recorded in `sdlc_artifacts/STATE.md`; the project
profile is recorded in `sdlc_artifacts/config.json`.

Do not edit these source rules directly. Change the canonical policy or adapter
generator, regenerate with `python scripts/generate_adapters.py`, and run the
framework tests. Installed local modifications are preserved during upgrades and
reported as conflicts through `.sdlc-install.json`.
