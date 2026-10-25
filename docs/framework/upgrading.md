# Upgrading the Framework

## Upgrading 0.2.0 Projects to 0.3.0

Back up the project or commit its current state first. Replace only the framework
folder with the prepared 0.3.0 source; retain host `sdlc_artifacts/`, owner
instructions, `.sdlc-install.json`, and adapter/metadata backups. Reconcile local
framework edits before replacement. Do not copy the framework's own development
environment, test output, or release scan records into the host project.

From the host project root:

```bash
python sdlc/scripts/sdlc.py doctor --json
python sdlc/scripts/sdlc.py upgrade                # preview; writes nothing
python sdlc/scripts/sdlc.py upgrade --apply        # back up and update managed adapters
python sdlc/scripts/sdlc.py verify
python sdlc/scripts/sdlc.py check --json           # normal diagnostics first
python sdlc/scripts/sdlc.py metadata sync --json   # preview required-mode adoption
python sdlc/scripts/sdlc.py metadata sync --apply
python sdlc/scripts/sdlc.py check --strict --json
```

Address reported content errors before metadata migration. Complete incomplete
Proposed documents; a template can no longer stand in for a finished proposal.
New changes and ADRs start as Draft and are promoted with `sdlc.py propose PATH`.
Preserve existing accepted decisions and approval records. Non-ISO approval
dates are warnings normally and fail selected strict checks; the human corrects
these dates if needed. Never rewrite a protected legacy date automatically.

Replacing framework files or upgrading adapters does not adopt required metadata
for an existing configuration. Explicit sync does, and snapshots sidecars, index,
and configuration together. It preserves Markdown byte-for-byte. After subsequent
human status/sign-off edits, sync derived metadata again before gate checks.

Review finalization follows the project's profile/class. A required REV now
links fresh scan JSON, reviewed source digest, and Git revision when available.
Regulated and high-risk sign-off additionally needs a human-approved digest.
Scans expire for active work after seven days; source changes require refreshed
checks and review. Historical implemented reviews keep their snapshots rather
than being compared to every future source revision. Older records without the
required evidence are reported, not auto-approved or assigned fabricated scans.
Prepare an honest current review and have the owner decide how to link it while
retaining the historical record. See `quality-and-security.md` for details.

Git remains advisory for ordinary profiles. Regulated projects require committed
evidence, unless they explicitly declare `"repository_mode": "non-git"`.
Detailed requirements and design reasoning stay intact; only selected ordinary
context surfaces are budgeted. Requirements/ADR size guidance never blocks
strict checks. `sdlc.py handoff` archives the previous handoff outside normal
context instead of growing `STATE.md` indefinitely.

## Rolling Back a 0.3.0 Adoption

Before rolling back tools, restore the relevant snapshots with the new tools:

```bash
python sdlc/scripts/sdlc.py migrate --rollback --backup METADATA_BACKUP
python sdlc/scripts/sdlc.py upgrade --rollback --backup ADAPTER_BACKUP
```

Metadata backups are under `sdlc_artifacts/.sdlc/backups/`; adapter backups are
under `.sdlc-backups/`. Select the snapshot for this adoption rather than assuming
the latest belongs to it. Restore the saved 0.2.0 framework files afterward.
Do not delete newer Markdown, approval history, or evidence to make an older
validator pass. New 0.3.0 features may be unreadable to older tools; retain the
backup and resolve that compatibility deliberately.

## Adapter Installation and Existing Rollback Support

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
python sdlc/scripts/sdlc.py metadata sync          # preview compatibility migration
python sdlc/scripts/sdlc.py metadata sync --apply  # explicitly adopt required mode
python sdlc/scripts/sdlc.py check
python -m unittest discover -s sdlc/tests -v
```

Replacing the framework folder or upgrading adapters does not silently change an
existing project's metadata mode. Projects without `metadata_mode` continue in
compatibility mode and receive a warning until the explicit sync is applied.
Apply preserves Markdown and creates a rollback snapshot of metadata, the index,
and project configuration. Undo it with:

```bash
python sdlc/scripts/sdlc.py migrate --rollback
```
