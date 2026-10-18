# SDLC Framework Remediation Plan

**Prepared:** 2026-10-18  
**Branch:** `codex-review/remediation-plan`  
**Status:** Technical remediation implemented and locally verified  
**Scope:** Correctness, cross-assistant consistency, token efficiency, testing,
installation, upgrades, and long-term maintainability.

## Objectives

1. Correct contradictions and bypasses in the current approval and gate logic.
2. Give every supported coding assistant the same policy and outcomes.
3. Reduce framework context consumption without weakening governance.
4. Replace fragile Markdown scanning with deterministic validation.
5. Add automated tests, CI, versioning, and a safe upgrade path.
6. Preserve the framework's standard-library-only setup experience where practical.

## Current Baseline

- The repository contains 17 framework Python files, all of which parse under
  Python 3.12.4.
- The framework Markdown corpus is approximately 79,000 tokens using a rough
  character-based estimate.
- A typical implementation path can load approximately 12,000 framework tokens
  before product code is read.
- The starter projects have tests, but the framework scripts, parsers, setup
  logic, and hooks do not have a dedicated automated test suite.
- Adapter installation is additive, but existing adapters are skipped and are
  not checked for version or content drift.

## Priority Defects

The following defects should be fixed before larger architectural changes:

1. The approval-field guard scans the whole post-edit document, so an unrelated
   edit to an already approved artifact can be blocked by the approval value that
   was already present.
2. Onboarding instructs assistants to create retroactive ADRs as Accepted, while
   adapter policy prohibits assistants from setting an ADR to Accepted.
3. The canonical review template does not contain the `Agent Recommendation`
   section required by the Completion Gate.
4. Active Change resolution can accept an absolute or otherwise external file
   rather than requiring a known proposal under `sdlc_artifacts/changes/`.
5. Some gate operations fail open when files cannot be read.
6. The approval guard does not enforce every human-only field claimed by the
   documentation, including review verdict checkboxes.
7. Shell enforcement detects only selected command patterns, while the
   documentation can be read as promising comprehensive hard enforcement.
8. Codex and Copilot apply materially different thresholds for when a change
   proposal is required.

## Phase 1: Establish a Safety Net

Build the framework test harness before changing gate behaviour.

### Work

- Add tests for root-template and embedded installation layouts.
- Test project-root and artifact-root discovery from multiple working directories.
- Test environment-variable overrides and paths containing spaces.
- Test setup merging, idempotence, dry-run behaviour, and malformed settings.
- Test each hook with permitted, blocked, malformed, and missing-file inputs.
- Add fixture projects for Codex, Cursor, Copilot, and Claude configurations.
- Add a token-footprint measurement script and commit a baseline report.
- Add CI on Windows and Linux for the supported Python versions.
- Prefer the standard library's `unittest` initially so framework setup remains
  dependency-free. A development-only test dependency may be considered later.

### Acceptance Criteria

- Tests reproduce the approval-guard and Active Change defects before they are fixed.
- All existing scripts pass their baseline tests under Python 3.12.4.
- CI exercises both root-template and embedded layouts.
- Tests do not modify a developer's real project or global assistant settings.

## Phase 2: Correct Gate and Onboarding Behaviour

Fix known defects without redesigning the full policy model.

### Work

- Change the approval-field guard to compare protected values before and after
  an edit instead of scanning the entire resulting document.
- Apply multi-edit operations sequentially when computing the resulting content.
- Protect review verdict checkboxes and every documented human-only field.
- Require Active Change to resolve beneath `sdlc_artifacts/changes/`.
- Require Active Change to be a member of the discovered approved-change set.
- Reject symlink or path-traversal escapes from the artifact directory.
- Fail closed when a gate-critical change or ADR cannot be read.
- Add `Agent Recommendation` to the canonical review template.
- Add a `new_review.py` scaffold command.
- Make onboarding create retroactive ADRs as Proposed, followed by an explicit
  human review and acceptance step. Document a batch-review workflow for larger
  existing projects.
- Quote Python executable and hook script paths in generated configuration.
- Update enforcement documentation to distinguish tool hooks, instruction-only
  rules, and best-effort shell command detection.

### Acceptance Criteria

- Assistants can update non-protected evidence in an approved artifact.
- Any attempted assistant change to a protected approval value is blocked.
- External, missing, unreadable, and unapproved Active Change paths are rejected.
- Onboarding can complete without asking an assistant to violate approval policy.
- A review created from the canonical template can satisfy the Completion Gate.
- Documentation makes no enforcement claim that the implementation cannot meet.

## Phase 3: Define One Cross-Assistant Policy

Replace independently maintained adapter policy with one authoritative model.

### Work

- Define change classes:
  - `trivial`: documentation, comments, formatting, and isolated low-risk fixes.
  - `standard`: ordinary behaviour, feature, configuration, and dependency changes.
  - `high-risk`: authentication, authorization, secrets, migrations, architecture,
    production infrastructure, sensitive data, and AI safety controls.
- Define governance profiles:
  - `lite`: solo or exploratory projects with lightweight evidence.
  - `standard`: the recommended default with normal approval and completion gates.
  - `regulated`: stronger audit, review, and evidence requirements.
- Decide the artifacts and gates required for every class/profile combination.
- Store canonical policy in a versioned JSON file readable by the Python standard
  library and understandable by other tooling.
- Generate Codex, Cursor, and Copilot instruction files from canonical policy.
- Generate Claude hook configuration from the same policy where applicable.
- Add a drift check that fails when generated adapters are stale.
- Define agent invocation portably: assistants may spawn a subagent when supported
  or adopt the named role in the current session when it is not.

### Acceptance Criteria

- Equivalent requests receive equivalent gating decisions across assistants.
- No adapter maintains an independent copy of core gate policy.
- A profile can change process strictness without manual prompt editing.
- Generated files clearly identify their source and framework version.

## Phase 4: Create a Unified CLI

Turn the separate scripts into a coherent command surface while retaining
compatibility wrappers for existing users.

### Proposed Commands

```text
sdlc status
sdlc next
sdlc context --phase implementation --budget 2000
sdlc check
sdlc gate implementation
sdlc gate completion
sdlc new change|adr|requirement|review|retrospective
sdlc setup
sdlc verify
sdlc upgrade
```

### Work

- Implement a single command dispatcher with consistent exit codes and errors.
- Make `status` return deterministic project state.
- Make `next` report the next permitted action and exact blockers.
- Make `context` produce a bounded assistant packet containing only current work,
  applicable policy, and references needed for the requested phase.
- Make `check` validate schemas, statuses, dependencies, links, and stale state.
- Make gate commands usable directly by hooks and CI.
- Retain current script names as thin compatibility wrappers.
- Add optional machine-readable JSON output for automation.

### Acceptance Criteria

- A resume session needs only project state and one generated context packet.
- Assistants do not scan every proposal and ADR to identify active work.
- Humans and assistants receive consistent results from the same commands.
- Existing documented script commands continue to work during migration.

## Phase 5: Introduce Structured Artifact Metadata

Keep Markdown for human reasoning and review, but stop using flexible prose as the
only source for gate-critical state.

### Work

- Write an ADR selecting the structured metadata representation.
- Add a schema version to requirements, ADRs, changes, reviews, retrospectives,
  and project state.
- Store stable fields including ID, artifact type, status, dependencies, risk
  class, profile, applicable controls, and related artifacts.
- Provide a migration command for existing Markdown-only artifacts.
- Retain compatibility parsing for a documented transition period.
- Validate duplicate IDs, invalid statuses, broken links, unresolved dependencies,
  and inconsistent folder/status combinations.
- Generate a compact project artifact index.
- Exclude completed and superseded detail from ordinary runtime context unless
  explicitly requested.

### Acceptance Criteria

- Gate decisions do not depend on broad regex searches through arbitrary prose.
- Existing projects can migrate without losing narrative or Git history.
- Markdown remains the primary human review format.
- Schema changes are versioned and migration-tested.

## Phase 6: Reduce Token Consumption

Use progressive disclosure so assistants receive only what the current task needs.

### Token Targets

| Content | Target |
| --- | ---: |
| Always-on adapter | 500-800 tokens |
| Resume/context packet | Under 2,000 tokens |
| Ordinary implementation framework context | Under 4,000 tokens |
| Detailed catalogs and security guidance | Loaded only when applicable |

### Work

- Reduce always-on adapters to orientation, classification, critical prohibitions,
  and the commands used to obtain current context.
- Replace repeated gate prose with stable rule IDs and concise summaries.
- Split role documents into compact runtime instructions and optional references.
- Remove copied templates and full report formats from prompts where a canonical
  template or CLI output already exists.
- Select security controls by technology, risk class, and profile.
- Keep `STATE.md` limited to phase, active work, blockers, next action, and the
  last-session handoff.
- Add token-budget regression tests for adapters and generated context packets.

### Acceptance Criteria

- Ordinary implementation uses at least 60 percent less framework context than
  the recorded baseline.
- No gate depends on the assistant remembering an unloaded long-form document.
- Detailed guidance remains available through explicit references and CLI output.

## Phase 7: Add Versioned Installation and Upgrades

Replace copy-and-forget installation with managed, inspectable updates.

### Work

- Add framework version metadata and a semantic versioning policy.
- Add an installation manifest with installed adapters, source version, and hashes.
- Support `setup --assistant codex|cursor|copilot|claude|all`.
- Use managed sections where framework and user instructions share a file.
- Preserve user-authored content outside managed sections.
- Make `verify` detect missing, stale, modified, and incompatible adapters.
- Add `upgrade --dry-run` with a readable report before any changes are made.
- Document `python`, `python3`, `py`, and direct venv invocation consistently.
- Test upgrade paths from at least the previous supported framework version.

### Acceptance Criteria

- Upgrading the framework cannot silently leave stale adapter policy active.
- Users can install only the assistants they use.
- User-authored instructions are preserved.
- Upgrade and rollback behaviour is covered by integration tests.

## Phase 8: Complete Repository and Template Quality

Prepare the framework for repeatable maintenance and distribution.

### Work

- Add a changelog, contribution guide, release checklist, and licence if the
  framework is intended for redistribution.
- Validate generated adapters and token budgets in release checks.
- Smoke-test every starter project.
- Give starter projects a documented compatibility and dependency-update policy.
- Remove or qualify security claims in examples where the sample only detects or
  logs a condition rather than enforcing a control.
- Separate educational examples from production-oriented starter templates.
- Add one end-to-end fixture demonstrating requirement, ADR, change, tests,
  review, Completion Gate, and final human approval.

### Acceptance Criteria

- A release can be produced from a documented, automated checklist.
- Every starter template installs, imports, and passes its smoke tests.
- Examples clearly distinguish demonstration code from production controls.
- The end-to-end fixture passes on Windows and Linux CI.

## Delivery Increments

Implement the work as reviewable changes in this order:

| Increment | Deliverable | Depends On |
| --- | --- | --- |
| Change 0001 | Framework test harness, fixtures, baseline, and CI | None |
| Change 0002 | Approval guard, gate hardening, review template, and onboarding fixes | Change 0001 |
| ADR 0001 | Canonical policy, change classes, and governance profiles | Change 0002 |
| Change 0003 | Canonical policy source and generated adapters | ADR 0001 |
| ADR 0002 | Structured artifact metadata and migration strategy | Change 0003 |
| Change 0004 | Unified CLI, schemas, validation, and compatibility wrappers | ADR 0002 |
| Change 0005 | Compact context generation and token budgets | Change 0004 |
| Change 0006 | Versioned setup, verification, and upgrade support | Change 0004 |
| Change 0007 | Documentation, release process, and template hardening | Changes 0005-0006 |

## Definition of Done

The remediation programme is complete when:

- All identified correctness defects have regression tests.
- Gate-critical state is validated deterministically and fails closed.
- All supported assistants use one canonical policy.
- Ordinary framework context is reduced by at least 60 percent.
- Setup and upgrade operations are version-aware, selective, and reversible.
- CI validates supported platforms, layouts, adapters, migrations, and templates.
- Long-form documentation remains available without being loaded by default.
- Human approval remains explicit and cannot be silently substituted by an agent.

## Closure Status

All technical items in this plan are implemented in the branch working tree.
The Completion Gate derives its result from tests, a linked review, an acceptable
recommendation, and zero open must-fix findings. Migrated projects use versioned
artifact sidecars with drift validation, backup, and rollback. Shared adapter
files use managed sections, and upgrades preserve user-authored content outside
those sections. Context packets select high-priority fields and sections before
optional project detail. CI covers Python 3.10-3.13 and installs and tests every
starter template.

The remaining release actions require repository-owner or hosted-service input:
select a redistribution licence, choose package versus copied-folder distribution,
push the branch to execute hosted CI, perform manual acceptance in the assistants
actually used, and commit/tag the release.

## Recommended Starting Point

Begin with Change 0001 and Change 0002. They create the safety net and remove
contradictory behaviour. Do not begin the policy, metadata, or token architecture
until those changes pass on both Windows and Linux fixtures.
