# STATE.md - Project State

> **Maintained by**: Orchestrator agent. Updated at the end of every session.  
> **Purpose**: Single source of truth for project phase and open work. Agents read this first on every session start.

---

## Current Phase

<!-- One of: Requirements | Design | Implementation | Testing | Security Review | Deployment | Iterate -->
**Phase**: [phase name]

**Started**: [YYYY-MM-DD]  
**Goal for this phase**: [1-sentence description of what "done" looks like]

---

## Active Change

<!-- Set when implementing a specific approved change. Required when more than one change is Approved. -->
- **Change document**: [none | sdlc_artifacts/changes/NNNN-short-description.md]

---

## Open Items

### Pending Approvals
<!-- Items that cannot proceed until a human approves them -->
| # | Document | Type | Location | Waiting Since |
|---|----------|------|----------|---------------|
| 1 | [name] | Change / ADR | [path] | [YYYY-MM-DD] |

### In Progress
<!-- Work that is approved and actively underway -->
| # | Item | Owner Agent | Started | Notes |
|---|------|-------------|---------|-------|
| 1 | [description] | Developer / Tester / etc. | [YYYY-MM-DD] | |

### Blocked
<!-- Work that cannot proceed due to a dependency or blocker -->
| # | Item | Blocked By | Since |
|---|------|-----------|-------|
| 1 | [description] | [what is blocking it] | [YYYY-MM-DD] |

### Available (Independent Work)
<!-- Work that can proceed without waiting for any pending approval -->
| # | Item | Type |
|---|------|------|
| 1 | [description] | Docs / Tests / Other approved change |

---

## Phase Completion Checklist

<!-- Tick off as each is completed. Replace with the relevant checklist for the current phase. -->
- [ ] [Completion criterion 1]
- [ ] [Completion criterion 2]
- [ ] [Completion criterion 3]

---

## Last Session Summary

**Date**: [YYYY-MM-DD]  
**Agent(s) active**: [Orchestrator / Developer / Tester / etc.]

**Completed this session**:
- [Item completed]

**Decisions made**:
- [Any decision taken that future agents should know]

**Left off at**:
[One sentence describing exactly where work stopped, so the next session can resume without re-reading everything]

---

## Stale ADR Flags

<!-- Orchestrator populates this during orientation. Clear entries once reviewed. -->
| ADR | Review-By Date | Status |
|-----|---------------|--------|
| [ADR-XXXX title] | [YYYY-MM-DD] | Overdue / Due soon |

---

## Notes

<!-- Anything that doesn't fit above - temporary context, human instructions, links -->
