# Architecture Decision Records (legacy location)

**Do not create ADRs here.** Use `sdlc_artifacts/decisions/` instead.

This folder is a legacy placeholder from an earlier framework layout. All ADRs belong under:

```text
sdlc_artifacts/decisions/proposed/   — under consideration
sdlc_artifacts/decisions/accepted/  — in effect
sdlc_artifacts/decisions/superseded/ — replaced
```

## Create an ADR

```bash
python sdlc/scripts/new_adr.py "decision title"
```

Template: `templates/documents/adr.md`

Example reference: `examples/adr/ADR-0004-notification-delivery.md`

The `_template.md` file in this folder is **deprecated** — use the template under `templates/documents/` instead.

Never create project ADRs under `sdlc/docs/decisions/` — that path is framework documentation only.
