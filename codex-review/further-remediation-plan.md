# SDLC Harness Further Remediation Plan

**Prepared:** 2026-10-22  
**Target release:** 0.3.0  
**Baseline branch:** `codex-review/remediation-plan`  
**Evidence source:** Trial use in `ai-security-literature`

## Purpose

The 0.2.0 remediation established deterministic gates, canonical policy,
structured metadata support, bounded context generation, managed adapters, and
an automated test suite. Real project use confirmed that those controls work,
including correctly blocking completion when live broker evidence was absent.

This follow-up hardens the lifecycle around incomplete drafts, human-owned
fields, audit readiness, metadata adoption, execution environments, and context
growth. It deliberately distinguishes blocking errors from actionable warnings
so exploratory projects are not governed like regulated deployments.

## Observed Baseline

- `sdlc check` passed and the implementation gate allowed an approved change.
- The Completion Gate correctly blocked a `Needs changes` review.
- The project test suite independently produced 297 passed and one skipped.
- A newly created change briefly existed as an untouched template while still
  passing artifact validation.
- Approval dates used `DD/MM/YYYY`, while the approval guard protected only
  `YYYY-MM-DD` dates.
- A requirement described itself as Draft in prose while its canonical Approval
  section was Approved.
- Structured metadata remained in optional compatibility mode.
- Human review verdict and reviewer fields remained empty after an implemented
  change.
- `STATE.md` accumulated several session summaries and displaced active-change
  detail from a 2,000-token context packet.
- The project had no Git baseline, so code and evidence were entirely untracked.
- A fixed project-local pytest base directory collided across Windows execution
  identities; a fresh temporary directory produced the expected passing suite.

## Design Principles

1. Gate-critical contradictions are errors and fail closed.
2. Audit and operational readiness concerns are warnings unless the selected
   profile explicitly elevates them.
3. Assistants may prepare Draft and Proposed material but never supply human
   approval, acceptance, or sign-off.
4. Markdown remains the human record; structured metadata is a deterministic
   derived representation, not independent proof of approval.
5. Current work always receives context priority over historical narrative.
6. Existing 0.2.0 projects receive diagnostics and an explicit migration path;
   human-owned fields are never rewritten automatically.

## Workstream 1: Structured Diagnostics

Introduce a diagnostic model with a stable code, severity, message, and optional
artifact path. Support `error`, `warning`, and `info`, expose all diagnostics in
JSON output, and add `sdlc check --strict` to elevate selected warnings.

Initial diagnostic codes:

- `ARTIFACT_PLACEHOLDER`
- `ARTIFACT_INCOMPLETE`
- `STATUS_CONFLICT`
- `NON_ISO_APPROVAL_DATE`
- `METADATA_COMPATIBILITY_MODE`
- `MISSING_REVIEW_SIGNOFF`
- `VCS_NO_BASELINE`
- `VCS_UNTRACKED_EVIDENCE`
- `STATE_CONTEXT_OVERSIZE`
- `SHARED_TEST_TEMP`

### Acceptance Criteria

- Existing callers can still obtain the legacy list of error strings.
- Human-readable output separates errors and warnings.
- JSON output includes structured diagnostics and remains deterministic.
- Normal checks fail only on errors; strict checks may elevate configured warnings.

## Workstream 2: Canonical Status and Date Handling

- Protect every non-empty date in human-only sections regardless of formatting.
- Require ISO `YYYY-MM-DD` dates for newly completed approvals and reviews.
- Warn on legacy date formats without rewriting them.
- Use shared parsing for the approval guard, status command, gates, and artifact
  validation.
- Detect canonical lifecycle declarations outside their authoritative section and
  report contradictory values.

### Acceptance Criteria

- Editing `21/10/2026` is blocked exactly like editing `2026-10-21`.
- Non-ISO dates produce a human-actionable warning.
- A document cannot silently claim both Draft and Approved lifecycle states.
- Session dates outside human-only sections remain agent-editable.

## Workstream 3: Draft Lifecycle and Artifact Completeness

- Add an agent-writable Draft state for changes and ADRs.
- Make `sdlc new` create Draft artifacts with one literal status, not an option
  list that the parser truncates.
- Add `sdlc propose` to validate required content before Draft becomes Proposed.
- Define required sections and fields per artifact type.
- Detect unresolved template instructions, option lists, sample criteria, and
  empty required values for Proposed or later artifacts.
- Exclude Draft artifacts from gates and pending-approval counts.
- Use atomic writes for generated artifacts.

### Acceptance Criteria

- A raw scaffold may exist as Draft but cannot satisfy a gate.
- An untouched template cannot be considered a valid Proposed artifact.
- Proposed artifacts have substantive summary, scope or context, dependencies,
  acceptance criteria where applicable, and testing expectations.

## Workstream 4: Profile-Driven Human Review

- Define review sign-off requirements in canonical policy.
- `lite`: agent recommendation is sufficient.
- `standard`: agent recommendation plus the human change transition to
  Implemented is sufficient; optional review fields are clearly labelled.
- `regulated`, and configured high-risk projects: require a selected human
  verdict, reviewer, and ISO date before Implemented status is valid.
- Add `sdlc check --ready-to-finalize` to explain remaining human actions without
  modifying any human-owned field.

### Acceptance Criteria

- Templates do not imply mandatory fields that policy ignores.
- High-assurance profiles retain a complete human review trail.
- Agent recommendation is never represented as human sign-off.

## Workstream 5: Metadata Adoption and Synchronisation

- Add `metadata_mode` (`compatibility` or `required`) to project configuration.
- Default new standard and regulated projects to required mode.
- Preserve compatibility mode for upgraded projects until explicitly migrated.
- Add `sdlc metadata sync`, dry-run by default, to update sidecars and the index.
- Update metadata atomically from artifact creation and proposal commands.
- Report compatibility mode explicitly instead of silently treating it as the
  strongest validation mode.
- Preserve migration backup and rollback behaviour.

### Acceptance Criteria

- New governed projects exercise metadata validation from their first artifact.
- Existing projects can migrate without losing Markdown or Git history.
- Creating an artifact does not immediately leave required metadata stale.

## Workstream 6: Context and Handoff Compaction

Context selection priority becomes:

1. Phase, goal, change class, and active change.
2. Blockers and next action.
3. Active-change summary, dependencies, acceptance criteria, testing, and
   security impact.
4. Pending approvals.
5. One compact handoff.
6. Optional project context and references.

Add bounded per-section selection, keep only one current handoff in `STATE.md`,
and add `sdlc handoff` to replace the current handoff while archiving the previous
entry outside normal runtime context.

### Acceptance Criteria

- A 2,000-token packet always retains the active acceptance and gate information.
- Repeated sessions do not continually enlarge default context.
- Historical handoffs remain available but are not loaded automatically.
- Realistic oversized-state fixtures cover priority and truncation behaviour.

## Workstream 7: Repository and Evidence Readiness

- Detect Git when available without requiring it for all projects.
- Warn when a repository has no baseline commit or SDLC evidence is untracked.
- Record the current commit SHA in generated evidence when available.
- Permit regulated policy to require committed evidence before finalisation.
- Keep Git checks advisory for lite and explicitly non-Git projects.

### Acceptance Criteria

- Content validity and audit durability are reported separately.
- Evidence can be tied to the code revision that was tested.
- Non-Git projects can explicitly opt out without false failures.

## Workstream 8: Environment Diagnostics and Test Isolation

- Add `sdlc doctor` to report Python executable/version, virtual environment,
  project write access, writable temporary directory, and Git baseline state.
- Warn about common fixed project-local pytest base directories.
- Use unique per-run temporary paths in framework testing guidance and examples.
- Keep environment/setup failures distinct from product test failures.

### Acceptance Criteria

- User and sandbox test runs do not collide over a shared temporary root.
- Doctor output provides a known-good interpreter command.
- Windows and Linux fixtures exercise environment diagnostics.

## Workstream 9: Regression and End-to-End Coverage

Add regression tests for every observed issue, including legacy approval dates,
conflicting statuses, raw templates, Draft gate exclusion, profile-specific review
requirements, required metadata, context prioritisation, missing Git baselines,
untracked evidence, and shared pytest temporary directories.

The end-to-end fixture must continue to demonstrate requirement, ADR, change,
tests, review, deterministic Completion Gate, and final human approval on Windows
and Linux.

## Workstream 10: Concise Artifacts and Progressive Evidence

Long-lived artifacts must retain decisions and evidence without repeatedly loading
model-generated narrative. Each artifact should have a compact decision layer for
ordinary context and linked supporting evidence that is loaded only when needed.

### Default-Context Token Budgets

| Artifact | Normal target | Warning threshold |
| --- | ---: | ---: |
| Requirement | 1,500 tokens | 3,000 tokens |
| ADR | 700 tokens | 1,500 tokens |
| Change proposal | 1,200 tokens | 2,500 tokens |
| Review | 1,200 tokens | 2,500 tokens |
| Test summary | 800 tokens | 1,500 tokens |
| `STATE.md` | 500 tokens | 1,000 tokens |

These budgets apply only to compact summaries and gate-bearing sections selected
for ordinary model context. Complete requirements, design reasoning, ADR context,
machine-readable evidence, detailed cases, raw logs, research, and exploratory
discussion are not length-limited. `sdlc check --json` reports total size for
visibility but does not judge the authoritative detail by that number.

Requirements and ADRs receive informational summary-surface guidance only, even
under strict or regulated operation. Operational context surfaces may remain
warning-level in ordinary profiles and enforceable in regulated operation. No
accepted artifact is automatically rewritten; any meaning-bearing compaction is
proposed separately and reviewed by a human.

### Work

- Add approximate total and default-context token measurements to `sdlc check`.
- Emit `ARTIFACT_CONTEXT_OVERSIZE` only when the selected context surface exceeds
  its threshold; do not diagnose a detailed source artifact merely for being long.
- Keep requirement and ADR guidance informational. Make operational context
  thresholds advisory in ordinary profiles and enforceable in regulated operation.
- Add a compact decision-summary layer to requirement, ADR, change, review, and
  test templates.
- Keep durable content in the primary artifact: purpose, scope, decision,
  dependencies, acceptance criteria, consequences, evidence references, rollback,
  and canonical status.
- Move detailed commands, raw output, hashes, exhaustive test cases, control
  catalogues, and implementation diaries to linked evidence files.
- Replace repeated requirement, design, test, and review prose with stable artifact
  references and one-line outcomes.
- Make context generation load only compact summary sections by default.
- Add an explicit context option for extended evidence when a task genuinely
  requires it.
- Add template guidance that discourages repeating the same scope, exclusion,
  limitation, or test result across several artifacts.
- Add regression fixtures based on the long artifacts observed in
  `ai-security-literature` and verify that compact equivalents preserve all
  gate-critical information.

### Acceptance Criteria

- Normal context packets do not load full ADRs, changes, reviews, or test evidence.
- A concise Change can identify its linked requirement, ADR, test, and review
  without reproducing their contents.
- Machine evidence remains available and verifiable but is excluded from default
  context selection.
- Oversized default-context surfaces produce actionable diagnostics containing
  context, total, and target token counts without asking users to delete detail.
- Arbitrarily long requirement/design detail produces no size failure when its
  ordinary-context summary remains bounded.
- Requirement and ADR context guidance never blocks strict or regulated checks.
- Compact fixtures satisfy the same implementation and completion gates as their
  verbose equivalents.
- Artifact compaction reduces the representative active-change context by at
  least 40 percent without removing a gate-critical fact.

## Workstream 11: Security Review Evidence and Automated Linting

Added 2026-10-25 following review of the existing Phase 5 workflow and CI.
Security review is defined, but CI has no security scanning step. Starter
dependencies include Ruff, but linting and formatting checks are not enforced.

### Work

- Add dedicated CI checks for secrets, vulnerable dependencies, and insecure
  Python patterns, covering the framework and starter projects as applicable.
- Feed scan results into Phase 5 review evidence alongside assessment of
  authorization, data boundaries, business logic, and AI tool access.
- Record the reviewed commit, scan scope and tool versions, applicable controls,
  findings, and evidence references in the review template.
- Block completion on unresolved Must-Fix findings. Define any policy-permitted
  risk exception with a named owner, rationale, approval, and expiry date;
  preserve human-only approval fields.
- Detect changes to reviewed code after evidence was produced and require
  affected checks and review to be refreshed before completion.
- Add shared Ruff configuration for framework scripts, tests, and starter
  projects, initially covering errors, unused imports, and common bugs.
- Run `ruff check` and `ruff format --check` in a dedicated CI job, with matching
  documented local commands and an optional pre-commit hook.
- Keep linting within implementation/testing and preserve profile-driven
  security review requirements; no additional human lint approval is needed.
- Keep quality tools in development/CI dependencies so framework setup retains
  its standard-library-only runtime experience.
- Update implementation, testing, security review, and release guidance to define
  required evidence, failures, exceptions, and stale-review handling.

### Acceptance Criteria

- CI fails on lint or formatting violations and reports actionable locations.
- Security checks detect representative secret, dependency, and insecure-code
  findings using controlled fixtures without committing real credentials.
- Scan failures cannot silently count as successful security evidence.
- Required reviews reference the tested revision and automated findings while
  retaining assessment of risks beyond scanner coverage.
- Unresolved Must-Fix findings, expired or invalid exceptions, and stale review
  evidence prevent completion according to canonical policy.
- Local quality commands match CI scope and configuration; starter projects
  document how to run them.
- Regression coverage verifies evidence freshness and exception handling under
  the applicable profiles, with concise summaries linked to detailed evidence.

## Delivery Increments

| Increment | Deliverable | Depends On |
| --- | --- | --- |
| Change 0008 | Diagnostics, canonical dates, and status consistency | 0.2.0 baseline |
| Change 0009 | Draft lifecycle and artifact completeness | Change 0008 |
| Change 0010 | Profile-driven human review semantics | Changes 0008-0009 |
| Change 0011 | Context prioritisation and handoff archive | Change 0008 |
| Change 0012 | Metadata mode and synchronisation | Changes 0008-0009 |
| Change 0013 | VCS readiness, doctor, and test isolation | Change 0008 |
| Change 0014 | Concise templates, artifact budgets, and progressive evidence loading | Changes 0008, 0011 |
| Change 0016 | Automated security checks, review evidence freshness, and Ruff enforcement | Changes 0010, 0013 |
| Change 0015 | End-to-end fixtures, migration docs, and 0.3.0 release | All prior, including Change 0016 |

## Implementation Progress

Updated 2026-10-25.

| Increment | Status | Delivered so far |
| --- | --- | --- |
| Change 0008 | Complete | Shared canonical field parser across validation, hooks, gates, and status output; stable diagnostic codes and paths; policy-selected `check --strict`; deterministic text/JSON diagnostics; legacy-date protection and quality warnings; blank human fields cannot consume the following Markdown field |
| Change 0009 | Complete | Agent-writable Draft lifecycle; atomic scaffolds and promotion; substantive change/ADR completeness rules; placeholder, option-list, empty-field, acceptance-criteria, and testing validation; Draft exclusion from approval queues and counts; documented and end-to-end tested `sdlc propose` |
| Change 0010 | Complete | Canonical profile sign-off policy; distinct lite, standard, regulated, and high-risk review semantics; explicit human-verdict, reviewer, and ISO-date validation; post-Implemented high-assurance audit; non-mutating `check --ready-to-finalize` with text/JSON output |
| Change 0011 | Complete | Bounded section-level context prioritisation; acceptance and Completion Gate retention; `sdlc handoff` replacement with archived history; extended evidence opt-in; oversized-state and repeated-session regressions |
| Change 0012 | Complete | Explicit mode validation; new-project required metadata and existing-project compatibility preservation; dry-run adoption and transactional apply across sidecars, index, and configuration; exact snapshot rollback; immediately synchronized artifact scaffolds; setup verification and migration guidance |
| Change 0013 | Complete | Separate content-validity and evidence-durability reporting; advisory Git baseline/untracked/modified evidence diagnostics; regulated committed-evidence enforcement with explicit non-Git opt-out; revision capture in review/change evidence; `sdlc doctor`; fixed pytest base-temp detection; unique-temp guidance; Windows/Linux Git and environment fixtures |
| Change 0014 | Complete | Budgets apply to default-context surfaces rather than authoritative artifact length; `check --json` reports context and total measurements; requirement/ADR guidance is informational in every profile while operational surfaces remain regulated-enforceable; compact summaries, linked evidence, progressive loading, and equivalent-gate compaction fixtures are covered |
| Change 0016 | Complete (hosted CI pending) | Dedicated Ruff and security CI jobs; Bandit, detect-secrets, and independent transitive dependency audits; redacted source/revision-bound JSON reports with scope and tool versions; seven-day active evidence expiry; source-digest-bound human sign-off; stale/failed/partial evidence blocking; canonical no-waiver policy and exception rejection; standalone starter quality configuration; vulnerable/unused starter dependency remediation; local commands and security fixtures |
| Change 0015 | Local preparation complete; owner/hosted acceptance pending | Prepared source version 0.3.0 with Unreleased changelog; regenerated policy adapters; release-source consistency CLI and regressions; real embedded CLI journeys for all profiles; controlled 0.2.0 adapter upgrade and adapter/metadata rollback with legacy approval preservation; updated migration, prompts, lifecycle examples, and contributor guidance; Windows/Linux starter smoke matrix; explicit release and manual assistant acceptance checklist |

Current verification baseline: 116 unit/integration tests (the live advisory
fixture is opt-in outside the security CI job), plus 16 starter smoke tests.
Ruff lint/format, compilation, strict framework validation, adapter drift, token
budgets, and diff checks are part of local verification. The full network audit
and source snapshot for 0.3.0 are recorded in
`sdlc_artifacts/evidence/security-0.3.0.json`. The earlier Change 0016 report is
retained separately in `sdlc_artifacts/evidence/security.json`.
Hosted Windows/Linux CI remains an owner action after pushing.

Change 0016 deliberately permits no risk waivers in any profile: every exception
entry is invalid, including claimed approvals and expired/future-dated entries.
Human sign-off now includes a protected approved source digest. Historical
implemented reviews retain their original snapshots; later changes and age do
not invalidate a completed review, while active completion evidence must remain
current. See `docs/framework/quality-and-security.md` for scope and migration.

## Consolidated Outstanding Work

This is the authoritative remaining-work list across the original remediation
plan and this follow-up plan. The original plan's technical implementation is
closed; only its owner/release actions remain. Technical changes below belong to
the 0.3.0 follow-up.

### Technical Work Still Outstanding

| Priority | Source | Outstanding task | Completion evidence |
| --- | --- | --- | --- |
| - | Change 0015 | Local technical preparation is complete. Release publication remains pending the owner/hosted acceptance below. | See `docs/framework/releasing.md`; no hosted CI or manual assistant pass is claimed by local fixtures |

### Original Plan Owner and Release Actions

These tasks were intentionally not automated by the 0.2.0 remediation and remain
repository-owner decisions:

1. Select a redistribution licence before publishing a package or release archive.
2. Choose the supported distribution model: copied `sdlc/` folder, packaged tool,
   or both, including the support and upgrade commitment for each.
3. Run and review hosted Windows/Linux CI after the completed 0.3.0 branch is pushed.
4. Perform manual acceptance in each supported assistant actually used: Codex,
   Claude Code, Cursor, and Copilot as applicable.
5. Commit the completed remediation, merge it under the repository's chosen review
   process, and create the release tag only after version and migration checks pass.

### Recommended Execution Order

1. Follow `docs/framework/releasing.md` to record hosted CI and manual assistant
   acceptance for the prepared 0.3.0 source.
2. Resolve the licence/distribution decisions, review and commit the work, then
   date the Unreleased changelog and tag/publish only after acceptance passes.

## Definition of Done

- Every finding from the trial project has a regression test.
- Raw templates cannot pass as finished proposals.
- Human fields are protected regardless of locale-specific date formatting.
- Gate-critical state has one canonical interpretation.
- Context packets prioritise current work over session history.
- Artifact summaries remain concise, and detailed evidence is loaded only on demand.
- Representative active-change context is at least 40 percent smaller without
  weakening gate outcomes.
- Metadata and human-review requirements are explicit and profile-driven.
- Functional tests run consistently across user and sandbox environments.
- Ruff linting and formatting checks pass locally and in CI.
- Automated security findings feed revision-bound review evidence, with blocking
  findings, stale evidence, and risk exceptions handled by explicit policy.
- Existing 0.2.0 projects upgrade without automatic changes to human-owned fields.
- CI passes on supported Windows and Linux Python versions.

