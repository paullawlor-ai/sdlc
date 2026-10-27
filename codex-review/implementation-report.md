# Remediation Implementation Report

> Historical 0.2.0 record. Baselines, versions, and verification counts below
> describe that work, not the current release candidate. See the
> [changelog](../CHANGELOG.md) and [release checklist](../docs/framework/releasing.md)
> for current status.

**Date:** 2026-10-18  
**Branch:** `codex-review/remediation-plan`  
**Framework version:** 0.2.0

## Delivered

### Correctness and Enforcement

- Approval protection now compares protected section values before and after an
  edit, so approved artifacts can receive ordinary evidence updates.
- Multi-edit operations are evaluated sequentially.
- Human-only review verdicts, identities, dates, statuses, and sign-offs are
  protected only in their canonical sections.
- Active Change paths must remain under `sdlc_artifacts/changes/` and belong to
  the approved proposal set.
- Gate-critical unreadable ADRs fail closed.
- Onboarding creates retroactive ADRs as Proposed for human batch review.
- The review template includes the Agent Recommendation required by Completion Gate.
- Hook command paths are quoted for installations under paths containing spaces.
- Shell detection is documented as best-effort defence in depth rather than a
  complete security boundary.

### Canonical Policy and Portability

- `policy/sdlc-policy.json` defines change classes, profiles, human-only fields,
  security baselines, token budgets, and stable rule IDs.
- Codex, Cursor, and Copilot adapters are generated from the canonical policy.
- Agent invocation has a portable fallback for assistants without subagent support.
- `STATE.md` records the active change class; `config.json` records the project profile.
- Direct hooks and instruction-based assistants evaluate the same policy model.

### CLI and Structured State

- Added the unified `scripts/sdlc.py` command with `status`, `next`, `context`,
  `check`, `gate`, `new`, `setup`, `verify`, `migrate`, and `upgrade` commands.
- Added bounded assistant context generation.
- Added versioned per-artifact sidecars, a compact index, drift validation,
  migration previews, backups, and rollback while retaining Markdown review.
- Added validation for statuses, duplicate IDs, dependencies, profiles, adapter
  generation, and token budgets.
- Added `new_review.py` and retained all existing script entry points.

### Installation and Lifecycle

- Added selective setup for Codex, Cursor, Copilot, and Claude.
- Added `.sdlc-install.json` manifests with framework versions and adapter hashes.
- Shared instructions use managed sections; upgrades preserve user content,
  back up changed files, detect managed-section conflicts, and support rollback.
- Verification detects missing, modified, and stale managed adapters.
- Added version, changelog, contribution guidance, upgrade documentation, and a
  release checklist.

### Testing and Templates

- Added Windows/Linux CI for Python 3.10 through 3.13.
- Added 38 tests covering gates, approval fields, policy, adapters, setup,
  structured artifacts, CLI budgets, starter templates, and an end-to-end lifecycle.
- Starter projects are installed and smoke-tested in CI; sources and dependency
  files also receive fast local validation.
- Corrected the FastAPI starter's duplicate dependency and clarified that its
  simple LLM pattern screening is demonstration code, not injection prevention.

## Token Results

The same approximate `ceil(characters / 4)` measurement is used before and after.

| Measure | Before | After | Result |
| --- | ---: | ---: | ---: |
| All adapter source files | 11,038 | 3,596 | 67.4% reduction |
| Largest generated adapter | Not bounded | 770 | Under 800-token budget |
| Resume packet | Unbounded reads | At most 2,000 | Enforced by CLI |
| Adapter plus resume packet | About 12,313 typical | At most 2,770 | Up to 77.5% reduction |

Long-form roles, workflows, catalogs, and security references remain available
but are no longer intended to be loaded automatically for ordinary work.

## Verification

The following checks pass under Python 3.12.4:

```text
python -m unittest discover -s tests -v          38 tests passed
python scripts/generate_adapters.py --check      all generated files current
python scripts/sdlc.py check --json              ok: true
python -m compileall -q scripts tests templates/projects
```

## Owner Decisions And External Verification

- Shell command detection remains best effort. Direct tool hooks are enforceable;
  a local framework cannot be a security sandbox for arbitrary command execution.
- A public redistribution licence was not selected automatically. The repository
  owner must choose one before public package or archive distribution.
- CI configuration is present, but its hosted Windows/Linux jobs will run only
  after the branch is pushed to a Git hosting service.
- Public package versus copied-folder distribution remains an owner decision.
- Final acceptance should include a manual run in each assistant the owner uses.
