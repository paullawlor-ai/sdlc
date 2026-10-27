# Change XXXX - <short title>

## Summary
<!-- Ordinary-context layer. State the outcome in 1-3 sentences; do not repeat linked artifact prose. -->
What changed (1-3 sentences).

## Motivation
Why is this needed? What risk/bug/requirement does it address?

## Scope
- **Risk class**: trivial | standard | high-risk
- **Policy profile**: lite | standard | regulated
- **Components affected**:
- **Files likely touched**:
- **Backwards compatibility**:

## Dependencies
- **Blocking ADRs**: <!-- ADR-NNNN - title - Accepted/Proposed, or "None" -->
- **Blocking changes**: <!-- Change NNNN - title - Approved/Proposed, or "None" -->
- **External dependencies**: <!-- team/service/tooling dependency, or "None" -->

Implementation must not begin until every blocking ADR is accepted and every blocking change is approved.

## Proposed Approach
Describe the implementation at a high level.

## Why This Approach
Alternatives considered and why they were rejected.

## Implementation Phases

<!--
  Fill this section when the change touches more than 3 files OR estimated effort exceeds 2 hours.
  Leave blank (keep the header) for single-file or trivial changes.

  SIZING RULE — one phase = one session:
    - Reads at most 4-5 existing files for context
    - Edits at most 2-3 files
    - Adds or changes no more than ~200 lines total
    - Leaves the codebase in a runnable/testable state when done

  COMPLETION RULE — do not declare a phase complete until:
    - Code is written and imports/syntax verified
    - Tests are written and passing (unit tests minimum; integration if practical)
    - Any security notes from the proposal are addressed
    - The phase exit state is verifiable (codebase runs, no crashes)

  CHANGE COMPLETION — after all phases (or for single-phase changes):
    - Full change test suite passes
    - Completion Gate passes (REV doc + Agent Recommendation — see ## Completion Gate)
    - Human sets Approval Status to Implemented only after Completion Gate PASS

  Order phases by dependency: config and interfaces before modules that use them;
  core logic before report generation; unit before integration.
-->

| Phase | Files touched | Deliverable / exit state | Tests required | Est. hours |
|-------|--------------|--------------------------|---|------------|
| 1 | | | | |
| 2 | | | | |

**Phase dependencies**: <!-- any ordering constraints between phases -->

## Security Impact
- **Risks reduced**:
- **New risks introduced**:
- **OWASP mapping** (from `catalogs/`):
- **Controls implemented** (reference by number):

## Performance & Reliability Impact
- **Latency / resource considerations**:
- **Failure modes**:

## Acceptance Criteria

<!-- Define before implementing. Tester fills in Test ID column after writing tests. -->
| ID | Criterion (Given / When / Then) | Test ID |
|----|--------------------------------|---------|
| AC-01 | Given [context], when [action], then [result] | |
| AC-02 | | |

## Effort

- **Estimated hours**: <!-- Developer fills in before implementation -->
- **Actual hours**: <!-- Developer fills in when marking Implemented -->

## Testing
- **Unit tests**:
- **Integration tests**:
- **Negative / abuse cases**:

## Operational Notes
- **Config knobs / flags**:
- **Metrics / logs added**:
- **Alerts to consider**:

## Rollback Plan
Exact rollback steps (toggle/flag/revert).
Expected side effects of rollback.

## Evidence References
<!-- Link durable detail and raw evidence. Normal context excludes this section unless explicitly requested. -->
- **Requirements**:
- **ADRs**:
- **Tests / results**:
- **Review**:
- **Detailed evidence**:

## Approval
<!-- HUMAN-ONLY SECTION. The model must not edit Status, Approved by, or Date. -->
<!-- Model creates this document as Draft and uses `sdlc propose` when it is complete. Human reviews subsequent status changes. -->
- **Status**: Draft
  <!-- Implemented: human sets only after Completion Gate PASS (tests + REV). -->
- **Approved by**:
- **Date**:

## Implementation Gate
<!-- Model fills this section immediately before editing product code. Human does not edit this section. -->
<!-- Fill in each field with the actual value at the time of the check — do not leave placeholders. -->
- **Gate checked by**:
- **Gate checked at**:
- **Change status is Approved**:
- **Blocking ADRs accepted**:
- **Not pending/blocked in STATE.md**:
- **Acceptance criteria present**:
- **Testing expectations present**:
- **Gate result**:

## Completion Gate
<!-- Model fills after tests pass and security review. Human sets Approval Status: Implemented only after PASS. -->
- **Gate checked by**:
- **Gate checked at**:
- **Tested revision**:
- **Tests passing**:
- **Security review (REV)**:
- **Agent recommendation**:
- **Open must-fix in REV**:
- **Gate result**:

---
*Template: `templates/documents/change-proposal.md`*
