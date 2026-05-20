# Phase 3: Implementation Workflow

## Overview

The Implementation phase builds the software according to approved designs, following security guidelines and quality standards.

## Agent

**Primary**: Developer (`agents/developer.md`)

**Supporting**:
- Web Designer/Engineer (`agents/web-designer.md`) for browser-facing UI and frontend workflow implementation.
- Docs Writer (`agents/docs-writer.md`) when public APIs, configuration, user workflows, or project documentation change.

## Inputs

- Accepted ADRs from Phase 2
- Design documents
- Requirements with acceptance criteria
- Security baselines and controls

## Activities

### 1. Review Design

Before coding:
- Read accepted ADRs
- Understand design decisions
- Note security controls to implement
- Review coding standards

### 2. Create Change Proposal

**BEFORE writing code**, create a change proposal:

```bash
python sdlc/scripts/new_change.py "description"
```

Fill out:
- What will change
- Why it's needed
- Implementation approach
- Blocking ADRs and dependency status
- Security impact
- Acceptance criteria
- Testing plan
- Rollback procedure

### 3. Wait for Approval

**DO NOT code this specific change until the change proposal is approved and every blocking ADR is accepted. Independent work may continue.**

```markdown
[PAUSE] APPROVAL GATE: Change Proposal

Document: sdlc_artifacts/changes/NNNN-description.md
Blocked: Implementation of this change
Status: Proposed

To unblock: Review -> ask the human to change Status to "Approved" in the file and save -> tell me to continue.

While waiting, available independent work:
- [Other approved changes]
- [Tests for already-implemented changes]
- [Documentation updates]
```

### 4. Run Implementation Gate

Immediately before editing product code, verify the gate below. This gate applies to every agentic coding tool using the framework: Cursor, GitHub Copilot, Codex, Claude Code, and others.

> **Claude Code**: the gate is enforced automatically by `PreToolUse` hooks (`implementation_gate.py`, `bash_gate.py`). Hooks check: approved change exists, Active Change scoping when multiple are approved, and blocking ADRs are accepted. They do **not** check STATE.md pending/blocked, acceptance criteria, or test expectations — the model must verify those per the table below.

> **Cursor / Copilot / Codex**: instruction rules only — no tool-level block. The model must run the full checklist below before editing product code.

| Gate Check | Required Result | Hook-enforced (Claude Code) |
|------------|-----------------|------------------------------|
| Active change document exists | Yes | Partial — requires Approved change; Active Change when multiple approved |
| Change Approval status | `Approved` (human-set in file) | Yes |
| Blocking ADRs listed in the change proposal | All accepted or explicitly "None" | Yes |
| Item status in `STATE.md` | Not under Pending Approvals or Blocked | No (instruction only) |
| Acceptance criteria | Present and testable | No (instruction only) |
| Testing expectations | Unit/integration/negative cases described | No (instruction only) |

If any check fails:

```markdown
[PAUSE] IMPLEMENTATION GATE FAILED

Blocked: Implementation of this specific change
Reason: [missing approval / unaccepted ADR / missing ACs / pending state item]

Required before coding:
- [specific document/status update needed]

I will not edit product code for this change until the gate passes.
```

### 5. Implement

After approval:
1. Make the smallest diff that satisfies the change
2. Follow security guidelines
3. Write unit tests as you go
4. Handle errors appropriately
5. Add logging with correlation IDs

If the change includes browser-facing UI, invoke the Web Designer/Engineer agent
for the frontend slice or UI-heavy implementation details:

```text
Act as the Web Designer/Engineer agent.
Read agents/web-designer.md.
Implement the approved UI scope for this change and hand off interaction/accessibility notes to Tester.
```

### 6. Self-Review

Before handoff to Testing:
- [ ] Code matches change proposal
- [ ] Implementation Gate passed before coding
- [ ] Unit tests written and passing
- [ ] Security controls implemented
- [ ] No secrets in code or logs
- [ ] Error handling appropriate
- [ ] Code documented

### 7. Hand Off to Testing

Do **not** set Approval **Status** to `Implemented` here. That happens only after the **Completion Gate** (tests + security review).

```markdown
## Handoff: Implementation -> Testing

### Change
- Document: sdlc_artifacts/changes/NNNN-description.md
- Status: Approved (still — not Implemented)

### Changes Made
- [List of files and changes]

### Tests Added
- [List of test files]

### How to Test
[Testing instructions]

### Ready for: Testing phase
```

### 8. Completion Gate (after Testing)

**Mandatory** before the change is treated as complete or Approval **Status** becomes `Implemented`. See `.cursor/rules/implementation-gate.mdc` (Completion Gate section) and `workflows/05-security-review.md`.

| Step | Requirement |
|------|-------------|
| 1 | All tests for this change pass (Tester or Developer runs them) |
| 2 | Create or update `sdlc_artifacts/reviews/REV-NNNN-*.md` referencing this change |
| 3 | **Agent Recommendation** in REV is `Approved` or `Approved with notes`; no open Must-Fix |
| 4 | Fill `## Completion Gate` in the change document |
| 5 | Human sets Approval **Status** to `Implemented` |

If Completion Gate fails, return to Developer for fixes or complete the security review — do not mark Implemented.

## Outputs

| Output | Location |
|--------|----------|
| Change documents | `sdlc_artifacts/changes/` |
| Application code | Project directories |
| Unit tests | Test directories |
| Updated documentation | As needed |

## Quality Checklist

Before completing this phase:

- [ ] Change proposal approved before coding
- [ ] Blocking ADRs accepted before coding
- [ ] Implementation Gate result recorded in the change/session notes
- [ ] Implementation matches proposal
- [ ] Unit tests written and passing
- [ ] Security controls from catalog implemented
- [ ] No secrets in code or logs
- [ ] Error handling in place
- [ ] Code is self-documenting
- [ ] Middleware registry updated (if middleware added)
- [ ] Handed off to Testing (Status remains `Approved` until Completion Gate)

## Security During Implementation

Apply controls from `catalogs/owasp-secure-coding-100.md`:

### Input Validation (Controls 1-10)
- Validate all inputs server-side
- Use allowlists
- Centralized validation

### Output Encoding (Controls 11-18)
- Parameterized queries
- Context-appropriate encoding
- Safe serializers

### Error Handling (Controls 45-50)
- Generic errors to clients
- Details logged server-side
- Correlation IDs

### For AI Features (Controls 82-87)
- Treat model output as untrusted
- Validate tool parameters
- Implement token limits
- Log AI actions

## Approval Gate

**Required**: change proposal approval and acceptance of blocking ADRs before implementation.

```markdown
[PAUSE] APPROVAL GATE: Change Proposal

A change proposal has been created.

Document: sdlc_artifacts/changes/NNNN-description.md
Status: Proposed

To proceed:
1. Review the change proposal
2. **You** open the file, set status to "Approved", and save (human edit only — the model must not write approval fields)
3. Tell me to continue

Waiting for approval...
```

## Implementation Gate

This final check happens after approval and immediately before product-code edits:

```markdown
## Implementation Gate Result

- Change: sdlc_artifacts/changes/NNNN-description.md
- Change status: Approved
- Blocking ADRs: [ADR list or None]
- ADR status: Accepted / Not accepted
- STATE.md pending/blocked status: Clear / Blocked
- Acceptance criteria present: Yes / No
- Test expectations present: Yes / No

Result: PASS / FAIL
```

Only proceed when the result is `PASS`.

## Docs Writer (Optional, Parallel)

After implementation is complete, the Docs Writer agent can run in parallel with testing to keep documentation in sync. See `agents/docs-writer.md` - invoke it when: a public API changed, configuration options were added, or user-facing behaviour changed.

## Web Designer/Engineer (Optional)

Use the Web Designer/Engineer agent when a change includes browser-facing UI.
This role may run during design for UI structure, during implementation for
frontend work, and during testing handoff for interaction states,
accessibility notes, and visual regression coverage.

## Phase Transition

**Next Phase**: Testing

**Transition Trigger**: Implementation complete, unit tests passing

**Handoff to Tester**:
```markdown
## Handoff: Implementation -> Testing

### Change
- Document: sdlc_artifacts/changes/NNNN-description.md
- Status: Approved

### Code Changes
- [Summary of what was built]

### Unit Test Coverage
- [What's covered]

### Acceptance Criteria to Verify
From the AC table in `sdlc_artifacts/changes/NNNN-description.md`:
| ID | Criterion | Test ID (Tester fills this in) |
|----|-----------|-------------------------------|
| AC-01 | [criterion] | |
| AC-02 | [criterion] | |

### How to Test
[Testing instructions]

### Ready for testing phase.
```

**After Testing passes** — run Security Review (REV), then Completion Gate, then the human sets `Status: Implemented`. See `workflows/04-testing.md` and `workflows/05-security-review.md`.

## Change Proposal Format

See `sdlc/templates/documents/change-proposal.md` for the full template and `agents/developer.md` for field-by-field guidance.

## Tips

1. **Small Changes**: Easier to review and safer to deploy
2. **Test First**: Consider how to test before coding
3. **Security by Default**: Apply controls from the start
4. **Document Intent**: Comments explain why, not what
5. **Ask Questions**: When unclear, ask rather than assume
