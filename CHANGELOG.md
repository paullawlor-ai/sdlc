# Changelog

## 0.3.0 - Unreleased

- Removed retired folder placeholders, unused internal setup helpers and starter
  models/dependencies; corrected stale starter and approval instructions and
  added ignore rules for backups, temporary writes, and private notes.

- Added structured errors, warnings, informational diagnostics, and policy-driven
  strict checks; shared canonical status/date parsing protects legacy approvals.
- New changes and ADRs start as Draft. `sdlc propose` validates completeness before
  promotion to Proposed; drafts cannot satisfy approval or implementation gates.
- Added profile-driven human review, source-digest-bound sign-off, and non-writing
  finalization checks. Human approval fields remain human-owned.
- New projects initialize required metadata. Upgrades preserve compatibility mode
  until explicit transactional migration, with exact backup and rollback.
- Prioritized active acceptance criteria and gate data in bounded context packets;
  added archived handoffs and explicit extended-evidence loading. Detailed
  requirements and design records remain unrestricted.
- Added Git/evidence durability diagnostics, explicit non-Git operation, `doctor`,
  revision capture, and isolated testing guidance.
- Added Ruff, security CI, redacted scan evidence, active-review freshness checks,
  dependency audits, and a canonical no-waiver policy.
- Updated starter dependencies and separate development tools; removed unused
  vector-store/model and JWT dependencies from implementation placeholders.
- Added embedded-install lifecycle and upgrade regression fixtures, migration and
  assistant acceptance guidance, release consistency checks, and a release checklist.

Publication, hosted CI, assistant acceptance, and the release tag remain pending.

## 0.2.0 - 2026-10-18

- Added framework regression tests and cross-platform CI.
- Fixed approval-field diffing, Active Change containment, and fail-open ADR reads.
- Added policy profiles, change classes, and generated compact adapters.
- Added the unified `sdlc.py` CLI, structured artifact index, and token reporting.
- Added selective manifest-backed setup and conflict-aware upgrades.
- Aligned onboarding, review templates, and Completion Gate evidence.
- Derived Completion Gate results from linked tests and review findings.
- Added versioned artifact sidecars, migration previews, backups, and rollback.
- Added managed instruction sections with adapter upgrade backups and rollback.
- Added priority-aware context packets and installed starter-template smoke tests.

## 0.1.0

- Initial framework release.
