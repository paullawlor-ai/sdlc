# Changes (legacy location)

**Do not create change proposals here.** Use `sdlc_artifacts/changes/` instead.

This folder is a legacy placeholder from an earlier framework layout. All change proposals, approval tracking, and implementation gate checks use:

```text
sdlc_artifacts/changes/NNNN-short-description.md
```

## Create a change proposal

```bash
python sdlc/scripts/new_change.py "short description"
```

Template: `templates/documents/change-proposal.md`

Example reference: `examples/changes/0005-plant-health-log.md`

The `_template.md` file in this folder is **deprecated** — use the template under `templates/documents/` instead.
