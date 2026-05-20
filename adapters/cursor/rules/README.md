# Cursor Rules

These MDC files are source templates for Cursor. They are **not** loaded from inside `sdlc/` — Cursor reads rules from the host project root at `.cursor/rules/`.

Install them with:

```bash
python sdlc/scripts/setup_project.py
```

The setup script copies missing rule files into `.cursor/rules/` without overwriting files you already have.

## Files

| File | Purpose |
|------|---------|
| `implementation-gate.mdc` | **Implementation Gate** and **Completion Gate** — mandatory checks before product-code edits and before marking a change Implemented |
| `core.mdc` | Core framework orientation (always active) |
| `security.mdc` | Security guidelines and OWASP rules |
| `agents.mdc` | Agent orchestration and coordination |

All four rules use `alwaysApply: true`.

## Implementation Gate (`implementation-gate.mdc`)

This is the most important rule. It defines two gates:

### Implementation Gate (before every product-code edit)

Before editing any file outside `sdlc/`, `sdlc_artifacts/`, `.claude/`, `.cursor/`, or `.github/`:

1. Find a change proposal in `sdlc_artifacts/changes/` with `Status: Approved` (human-set — verify by reading the file)
2. If none exists, **stop** and output `[SDLC] IMPLEMENTATION GATE - BLOCKED`
3. When **more than one** change is Approved, verify `sdlc_artifacts/STATE.md` → `## Active Change` points to the change being implemented
4. Verify blocking ADRs listed in the change proposal are `Accepted`

The gate cannot be waived for "small changes" or verbal approval — the status must be set in the file by a human in their editor.

### Completion Gate (after implementation, before Implemented)

Before treating a change as done or asking the human to set `Status: Implemented`:

1. All tests for the change must pass
2. A security review document (`REV-NNNN-*.md`) must exist in `sdlc_artifacts/reviews/`
3. `## Agent Recommendation` in the REV must be `Approved` or `Approved with notes`
4. No open Must-Fix findings for this change
5. Fill `## Completion Gate` in the change document (model audit trail)

Human-only fields the model must never write:

- Change proposals: `## Approval` (Status, Approved by, Date)
- ADRs: `## Status`, `## Approval`
- Reviews: `## Summary Verdict`, `## Approval`

## How It Works

Cursor loads `.mdc` files from `.cursor/rules/` at the project root based on:

- The `globs` pattern (which files they apply to)
- The `alwaysApply` setting

## Customizing

To customize rules for your project:

1. Edit the files in `.cursor/rules/` at your project root (after setup)
2. Keep `implementation-gate.mdc` intact unless you intentionally change gate behaviour
3. Adjust glob patterns if needed for project-specific rules

To refresh SDLC rules after a framework update, compare your `.cursor/rules/` with `sdlc/adapters/cursor/rules/` and merge changes manually — setup will not overwrite existing files.
