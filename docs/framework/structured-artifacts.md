# Structured Artifact Index

Framework artifacts remain Markdown so humans can review them naturally. The
CLI converts their stable fields into versioned sidecars under
`sdlc_artifacts/.sdlc/metadata/` and a compact `sdlc_artifacts/index.json`.
Once sidecars exist, validation and gates fail on missing, malformed, orphaned,
or stale metadata.

Generate or refresh it with:

```bash
python sdlc/scripts/sdlc.py metadata sync          # dry-run
python sdlc/scripts/sdlc.py metadata sync --apply  # sidecars, index, required mode
```

New projects start in required mode. Existing projects remain in compatibility
mode until the explicit `metadata sync --apply` command succeeds. Apply snapshots
existing sidecars, `index.json`, and `config.json` beneath
`sdlc_artifacts/.sdlc/backups/<timestamp>/`, then writes sidecars, the index, and
`metadata_mode: required`. It never rewrites Markdown or human-owned fields.

Each sidecar records schema version, artifact ID, type, status, path,
dependencies, risk class, profile, applicable controls, and related artifacts.
The generated index retains all artifacts under `artifacts` and exposes the
human approval worklist separately as `approval_queue`. Drafts remain indexed
for traceability but are excluded from that queue until `sdlc propose` succeeds.
Markdown remains the human review surface; sidecars provide a deterministic
machine contract and must be refreshed after a human changes stable fields.

Restore the newest migration snapshot with
`python sdlc/scripts/sdlc.py migrate --rollback`, or select one with
`--backup PATH`. Rollback restores the prior metadata directory, index, and
configuration, including returning a newly adopted project to compatibility
mode. Commit the sidecars, index, and configuration together after validation.

Artifact creation and `sdlc propose` synchronise the affected sidecar
immediately whenever required metadata is active. They do not refresh unrelated
artifacts, so existing drift remains visible rather than being accidentally
hidden.

## Context Budgets

`sdlc check --json` includes `artifact_tokens`, using the documented
`ceil(characters / 4)` approximation. It reports both `total_approx_tokens` and
`context_approx_tokens`. Budgets apply only to the summary and gate-bearing
sections eligible for ordinary assistant context, never to the complete source
artifact. Targets and thresholds live in `policy/sdlc-policy.json` under
`artifact_context_budgets`.

Requirements and ADRs may retain as much authoritative detail as the work
needs. Their context-surface diagnostics are informational, including in strict
and regulated operation. Do not remove nuance merely to satisfy a token target.
When a summary becomes difficult to navigate, shorten only the summary, remove
genuine duplication, or split focused child requirements/decisions with stable
IDs and links. Preserve the original detail and have a human review any rewrite
that could alter meaning.

Operational artifacts can still be enforced under the regulated profile:
active changes, reviews, test summaries, and `STATE.md` directly affect routine
execution and handoff context. Ordinary profiles receive warnings, while strict
mode promotes policy-selected warnings.

Keep the summary or decision-summary section as the ordinary context layer.
Link raw commands, logs, hashes, exhaustive cases, benchmarks, and scanner
output from `Evidence References` instead of reproducing them in several
artifacts. Default `sdlc context` selects bounded current-state and gate-bearing
sections. Use `sdlc context --extended-evidence` only when implementation,
operational, rollback, or linked evidence detail is needed.
