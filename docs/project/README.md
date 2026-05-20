# Project documentation (legacy location)

**Use `sdlc_artifacts/` for all project-specific SDLC documents.**

This folder predates the `sdlc_artifacts/` layout. The framework no longer writes requirements, design notes, or runbooks here. All active agent and workflow references point to `sdlc_artifacts/` instead.

## Where documents live now

| Former intent | Current location |
|---------------|------------------|
| Requirements / specs | `sdlc_artifacts/requirements/` |
| Design documents, API specs, UI notes | `sdlc_artifacts/design/` |
| Deployment and ops runbooks | `sdlc_artifacts/runbooks/` |
| Architecture decisions | `sdlc_artifacts/decisions/` |
| Change proposals | `sdlc_artifacts/changes/` |
| Security reviews | `sdlc_artifacts/reviews/` |
| Project state and stack context | `sdlc_artifacts/STATE.md`, `sdlc_artifacts/context.md` |

## Starting specs

If you want the AI assistant to begin from a written spec:

1. Place requirements in `sdlc_artifacts/requirements/` using `templates/documents/requirement.md`
2. Run `python sdlc/scripts/new_state.py` if `sdlc_artifacts/STATE.md` does not exist yet
3. Start with `Read sdlc/prompts/onboard.md and begin` (existing code) or `Read sdlc/prompts/bootstrap.md and begin` (greenfield)

The empty subfolders here (`requirements/`, `design/`, `runbooks/`) are retained only as historical placeholders and can be ignored.
