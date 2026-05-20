# Change XXXX - <short title>

## Summary
What changed (1-3 sentences).

## Motivation
Why is this needed? What risk/bug/requirement does it address?

## Scope
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

## Approval
- **Status**: Proposed | Approved | Rejected | Superseded
- **Approved by**:
- **Date**:

## Implementation Gate
<!-- Developer fills this immediately before editing product code. -->
- **Gate checked by**:
- **Gate checked at**:
- **Change status is Approved**: Yes | No
- **Blocking ADRs accepted**: Yes | No | N/A
- **Not pending/blocked in STATE.md**: Yes | No
- **Acceptance criteria present**: Yes | No
- **Testing expectations present**: Yes | No
- **Gate result**: Pass | Fail
