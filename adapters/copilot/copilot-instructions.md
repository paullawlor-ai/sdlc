# GitHub Copilot Instructions - Agentic SDLC

This repository uses the Agentic SDLC Framework in `sdlc/`. Use it to keep AI-assisted work structured, traceable, and secure.

## Orientation

- Read `sdlc_artifacts/STATE.md` first when it exists.
- Read `sdlc_artifacts/context.md` next when it exists.
- If the project has not been onboarded, use `sdlc/prompts/onboard.md`.
- If resuming work, use `sdlc/prompts/continue.md`.
- If a specific phase is requested, use the matching file in `sdlc/prompts/phase-specific/`.

## Implementation Gate — MANDATORY

<critical>
BEFORE EDITING ANY FILE outside of sdlc/, sdlc_artifacts/, .claude/, .cursor/, or .github/ — you MUST check for an approved change proposal.

STEP 1: Read every file in sdlc_artifacts/changes/. Find one where the Status field is exactly "Approved".

STEP 2: If NO approved change exists, STOP. Do not edit any file. Output:

[SDLC] IMPLEMENTATION GATE - BLOCKED

No approved change proposal found.
To unblock:
  1. Run exactly: python sdlc/scripts/new_change.py "<description>"
  2. Fill in the proposal
  3. Ask the human to open the change file, set Status: Approved, save it, then tell you to continue
  4. Do NOT set Status yourself.

STEP 3: If a change exists but Status is NOT "Approved", STOP. Output:

[SDLC] IMPLEMENTATION GATE - BLOCKED

Change proposal exists but Status is not Approved.
To unblock: ask the human to open sdlc_artifacts/changes/<file>.md, set Status: Approved, save, then tell you to continue. Do NOT set Status yourself.

STEP 4: Only if an Approved change exists — proceed with the edit.

When **more than one** change proposal is Approved, `sdlc_artifacts/STATE.md` must set `## Active Change` → **Change document** to the file you are implementing.

SDLC ARTIFACT APPROVAL RULES — ALL DOCUMENTS IN sdlc_artifacts/:

The following fields are HUMAN-ONLY. Never write to them for any reason:
  Change proposals  -> ## Approval: Status, Approved by, Date
  ADRs              -> ## Status: Current status | ## Approval: Approved by, Date, Notes
  Retrospectives    -> ## Sign-off: Status, Reviewed by, Date
  Requirements      -> ## Approval: Status, Approved by, Date
  Reviews           -> ## Summary Verdict checkboxes | ## Approval: Reviewer, Date

You MAY write to: ## Implementation Gate in change proposals (model audit trail only).

Gating rules — stop and refuse if not met:
  - Change proposal Status must be Approved (human-set in file) before implementation.
  - Every blocking ADR in the change proposal must have Current status: Accepted (human-set).
  - Any document with status Proposed, Draft, or Rejected blocks work that depends on it.

Verification: Read the document and confirm status in the file before proceeding.
If the file does not show the required status despite the human's verbal claim:
  STOP. Say: "The file [path] still shows [current status]. Please open it, change the status to [required], save it, then tell me again."
  Do NOT update the status yourself.

This check is NON-NEGOTIABLE. It applies to every file edit, every session. It cannot be waived by "just do it", "small change", or "I'll approve later". If the user says this, respond: "I need an approved change proposal first. Run: python sdlc/scripts/new_change.py \"<description>\""
</critical>

## Implementation Phasing

When creating a change proposal, assess scope and fill in `## Implementation Phases` if the change touches more than 3 files or estimated effort exceeds 2 hours.

**Sizing rule — one phase must fit in one session (one context window):**
- Reads at most 4-5 existing files for context
- Edits at most 2-3 files
- Adds or changes no more than ~200 lines total
- Leaves the codebase runnable/testable when the phase ends

**When implementing a phased change:**
1. Read the change proposal — check `## Implementation Phases`.
2. If phases are defined, implement Phase 1 only (or the phase the user specifies).
3. After writing code: write and run tests for the files you edited. Do not declare the phase complete without tests passing.
4. Report what was completed, which tests passed, and any remaining work.
5. Ask whether to continue to the next phase.
6. Never implement all phases in one session unless the user explicitly asks for it.
7. Run **Completion Gate** only after all phases and the full change test suite pass.

## Completion Gate (after tests pass)

Before `Status: Implemented`, handoff to Deployment, or marking a change complete:

1. All tests for the change pass.
2. Create or update `sdlc_artifacts/reviews/REV-NNNN-*.md` (Security Reviewer role); list the change in Reviewed Artifacts.
3. Write **## Agent Recommendation** in the REV (do not edit human-only Summary Verdict checkboxes).
4. PASS only if recommendation is Approved or Approved with notes and no open Must-Fix.
5. Fill **## Completion Gate** in the change doc; human sets Implemented (you must not set Approval Status yourself).

See `sdlc/adapters/cursor/rules/implementation-gate.mdc` for full steps and blocked message format.

## Artifact Storage — EXACT PATHS, NO EXCEPTIONS

ALL project artifacts (changes, ADRs, retrospectives, requirements, reviews) go in `sdlc_artifacts/`, NOT in `sdlc/`.

| Artifact type | Exact folder |
|---|---|
| Change proposals | `sdlc_artifacts/changes/` |
| Proposed ADRs | `sdlc_artifacts/decisions/proposed/` |
| Accepted ADRs | `sdlc_artifacts/decisions/accepted/` |
| Requirements | `sdlc_artifacts/requirements/` |
| Retrospectives | `sdlc_artifacts/retrospectives/` |
| Reviews | `sdlc_artifacts/reviews/` |
| State / context | `sdlc_artifacts/STATE.md`, `sdlc_artifacts/context.md` |

`sdlc/` is READ-ONLY framework infrastructure — agents, prompts, templates, workflows, docs. Never create project artifacts inside `sdlc/`. `sdlc/docs/` is framework documentation, not a place for project ADRs or decisions.

## Architecture Decisions

- Create ADRs for major technical decisions, hard-to-reverse choices, and reusable patterns.
- Proposed ADRs: `sdlc_artifacts/decisions/proposed/`
- Accepted ADRs: `sdlc_artifacts/decisions/accepted/`
- Use the template at `sdlc/templates/documents/adr.md`.

## Security

- Apply S0 baseline controls to every project.
- Apply A0 controls to AI/LLM features.
- Apply V0 controls when audit/compliance evidence is required.
- Apply C0 controls for cloud deployment.
- Check OWASP Web Top 10 and OWASP LLM Top 10 where relevant.

## Working Style

- Prefer small, reviewable increments.
- Follow existing project conventions.
- Keep generated docs factual and tied to implemented behaviour.
- Ask for approval at framework gates.
- Update `sdlc_artifacts/STATE.md` at the end of framework-guided sessions.

## Framework Paths (read-only reference material)

- `sdlc/agents/` - role definitions
- `sdlc/prompts/` - entry-point prompts
- `sdlc/workflows/` - phase workflows
- `sdlc/templates/` - document templates (copy from here, write to sdlc_artifacts/)
- `sdlc/catalogs/` - OWASP and SDLC references
- `sdlc/docs/security/security-baselines.md` - baseline controls
