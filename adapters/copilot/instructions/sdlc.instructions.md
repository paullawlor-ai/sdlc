---
applyTo: "**"
---

# Agentic SDLC — Implementation Gate

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

You MAY write to:
  Change proposals -> ## Implementation Gate, ## Completion Gate (model audit trail only)
  Reviews -> all sections EXCEPT ## Summary Verdict checkboxes and ## Approval
             (use ## Agent Recommendation for verdict text)

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

## SDLC Framework

- Read `sdlc_artifacts/STATE.md` and `sdlc_artifacts/context.md` before significant work.
- Use `sdlc/prompts/continue.md` to resume framework-guided work.
- Use `sdlc/prompts/onboard.md` before adopting an existing project into the framework.
- Use `sdlc/agents/` when the user asks for a specific SDLC role.
- Link tests to acceptance criteria where practical.
- Apply S0 security always, A0 for AI/LLM work, V0 for audit/compliance, C0 for cloud deployment.
- Do not edit `sdlc/` unless the task is to maintain the framework itself.

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

See `.cursor/rules/implementation-gate.mdc` for full steps and blocked message format.

## Active Change (multiple approved changes)

When more than one change proposal has `Status: Approved`, set exactly one in `sdlc_artifacts/STATE.md`:

```markdown
## Active Change
- **Change document**: sdlc_artifacts/changes/NNNN-short-description.md
```

Claude Code hooks enforce this. Cursor, Copilot, and Codex must follow the same rule.

## Artifact Storage — EXACT PATHS, NO EXCEPTIONS

ALL project artifacts go in `sdlc_artifacts/`, NOT in `sdlc/`. `sdlc/` is read-only framework infrastructure.

| Artifact type | Exact folder |
|---|---|
| Change proposals | `sdlc_artifacts/changes/` |
| Proposed ADRs | `sdlc_artifacts/decisions/proposed/` |
| Accepted ADRs | `sdlc_artifacts/decisions/accepted/` |
| Requirements | `sdlc_artifacts/requirements/` |
| Retrospectives | `sdlc_artifacts/retrospectives/` |
| Reviews | `sdlc_artifacts/reviews/` |
| State / context | `sdlc_artifacts/STATE.md`, `sdlc_artifacts/context.md` |

`sdlc/docs/` is framework documentation — never create project ADRs or decisions there.
