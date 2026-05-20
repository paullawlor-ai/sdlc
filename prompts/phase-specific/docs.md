# Documentation Prompt

Use this prompt when project, user, API, operational, or release
documentation needs to be updated as part of an approved change or phase.

---

## Instructions for AI Agent

Act as the Docs Writer agent.
Read `agents/docs-writer.md`.

Before changing files:
1. Read `sdlc_artifacts/STATE.md` and `sdlc_artifacts/context.md` when present.
2. Read relevant requirements, accepted ADRs, change proposals, reviews, and runbooks.
3. Keep documentation changes scoped to the approved change or requested docs task.

## Common Tasks

### Update Project Documentation
```text
Act as Docs Writer. Read agents/docs-writer.md. Update project documentation for [implemented change].
```

### Update API Documentation
```text
Act as Docs Writer. Read agents/docs-writer.md. Document the public API changes from [change document].
```

### Documentation Review
```text
Act as Docs Writer. Review the docs touched by this change for accuracy, missing setup steps, and stale references.
```

## Outputs

- Updated README, API docs, user docs, runbooks, or changelog notes.
- Documentation gaps or follow-up items recorded in `sdlc_artifacts/STATE.md` when relevant.

## Quick Start Command

```text
Read sdlc/prompts/phase-specific/docs.md and begin
```
