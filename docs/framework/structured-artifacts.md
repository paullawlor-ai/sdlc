# Structured Artifact Index

Framework artifacts remain Markdown so humans can review them naturally. The
CLI converts their stable fields into versioned sidecars under
`sdlc_artifacts/.sdlc/metadata/` and a compact `sdlc_artifacts/index.json`.
Once sidecars exist, validation and gates fail on missing, malformed, orphaned,
or stale metadata.

Generate or refresh it with:

```bash
python sdlc/scripts/sdlc.py check --write-index
# or use the explicit compatibility migration command
python sdlc/scripts/sdlc.py migrate          # preview
python sdlc/scripts/sdlc.py migrate --apply  # write sidecars and index
```

Each sidecar records schema version, artifact ID, type, status, path,
dependencies, risk class, profile, applicable controls, and related artifacts.
Markdown remains the human review surface; sidecars provide a deterministic
machine contract and must be refreshed after a human changes stable fields.

Migration does not rewrite Markdown. Replacing existing metadata creates a
timestamped backup under `sdlc_artifacts/.sdlc/backups/`. Restore the newest or a
specific backup with `migrate --rollback [--backup PATH]`. Commit the sidecars and
index when enabling structured validation for a project.
