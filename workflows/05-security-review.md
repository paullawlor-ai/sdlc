# Phase 5: Security Review Workflow

## Overview

The Security Review phase verifies that implementations meet security requirements, follow OWASP guidelines, and implement required controls.

**Completion Gate**: This phase is required when the effective change class and
project profile require a security review. After Testing passes, create or
update a REV document, record the result in the change's `## Completion Gate`
section, then the human sets **Status: Implemented**.

## Agent

**Primary**: Security Reviewer (`agents/security-reviewer.md`)

## Inputs

- Implemented and tested code
- Change documents
- Security baselines
- OWASP guidelines

## Activities

### 1. Review Against OWASP

Check against:
- `catalogs/owasp-top10-web-summary.md`
- `catalogs/owasp-llm-top10-summary.md` (if AI features)
- `catalogs/owasp-secure-coding-100.md`

### 2. Verify Security Baselines

Check applicable baselines:

**S0 (Always)**:
- [ ] Authentication
- [ ] Authorization
- [ ] Input validation
- [ ] Output encoding
- [ ] Secrets handling
- [ ] TLS
- [ ] Error handling
- [ ] Dependencies

**A0 (AI features)**:
- [ ] Model output handling
- [ ] Prompt injection controls
- [ ] Tool safety
- [ ] Data boundaries
- [ ] Output controls
- [ ] Cost controls

**V0 (Audit)**:
- [ ] Event logging
- [ ] Tamper evidence

**C0 (Cloud)**:
- [ ] IAM
- [ ] KMS
- [ ] Network security

### 3. Document Findings

Create or update review document in `sdlc_artifacts/reviews/`. The agent writes all sections **except** human-only `## Summary Verdict` checkboxes and `## Approval`. Put the agent's verdict in **`## Agent Recommendation`** (used by Completion Gate).

Create review document:

```markdown
# REV-XXXX - Security Review of [Change]

## Reviewed Artifacts
- Change docs: [list]
- Code files: [list]

## Findings

### Must-Fix
[Critical issues]

### Should-Fix
[Important issues]

### Nice-to-Have
[Suggestions]

## Baseline Verification
- S0: [OK]/[WARN]/[X]
- A0: [OK]/[WARN]/[X]/N/A
...

## Agent Recommendation
- **Verdict**: Approved | Approved with notes | Needs changes
- **Rationale**: [why]

## Summary Verdict
<!-- Human checks boxes after reading Agent Recommendation -->
```

### 4. Record Completion Gate

Fill `## Completion Gate` in the linked change proposal(s). Gate **PASS** only if Agent Recommendation is Approved or Approved with notes and there are no open Must-Fix items.

### 5. Report Results

If must-fix items exist, block deployment until addressed.

## Outputs

| Output | Location |
|--------|----------|
| Security review | `sdlc_artifacts/reviews/` |
| Findings | In review document |
| Recommendations | In review document |

## Security Checklist

### Authentication (Controls 19-26)
- [ ] Single consistent approach
- [ ] No verbose failures
- [ ] MFA if required
- [ ] Secure credential transport
- [ ] Proper token validation

### Authorization (Controls 33-38)
- [ ] Enforced on every endpoint
- [ ] Deny by default
- [ ] Object-level checks
- [ ] Centralized policy
- [ ] Admin actions gated

### Input Validation (Controls 1-10)
- [ ] Server-side validation
- [ ] Allowlist approach
- [ ] Redirect validation
- [ ] Safe deserialization

### Output & Injection (Controls 11-18)
- [ ] Parameterized queries
- [ ] Safe command execution
- [ ] Context encoding
- [ ] Strict CORS

### Error Handling (Controls 45-50)
- [ ] Generic client errors
- [ ] No debug in production
- [ ] Security event logging
- [ ] Data redaction

### AI Features (Controls 82-87)
- [ ] Untrusted retrieval
- [ ] Tool allowlists
- [ ] Output policy
- [ ] Token limits
- [ ] AI action logging
- [ ] Data boundaries

## Severity Levels

### Must-Fix (Critical/High)
- Exploitable vulnerabilities
- Auth/authz bypass
- Injection flaws
- Data exposure
- Missing core controls

### Should-Fix (Medium)
- Defense-in-depth gaps
- Logging gaps
- Config weaknesses

### Nice-to-Have (Low)
- Code improvements
- Additional hardening
- Documentation

## Approval Gate

**Conditional**: Must-fix items block deployment

```markdown
[PAUSE] SECURITY GATE: Must-Fix Items Found

Review: sdlc_artifacts/reviews/REV-XXXX-...md

Must-Fix Items:
1. [Item 1]
2. [Item 2]

These must be addressed before deployment.

Options:
1. Return to Developer for fixes
2. Accept risk (document justification)
```

If approved:
```markdown
[OK] SECURITY REVIEW: Approved

Review: sdlc_artifacts/reviews/REV-XXXX-...md
Verdict: Approved

Ready for deployment.
```

## Phase Transition

**Next Phase**: Deployment

**Transition Trigger**: Completion Gate PASS (tests + REV + Agent Recommendation Approved or Approved with notes; no open must-fix)

**If Approved**:
```markdown
## Handoff: Security Review -> Human (Implemented) -> Deployment

### Review Summary
- Document: sdlc_artifacts/reviews/REV-XXXX-...md
- Agent Recommendation: Approved [with notes]

### Completion Gate
- Recorded in change: sdlc_artifacts/changes/NNNN-....md
- Gate result: PASS

### Human action
Set change Approval **Status** to `Implemented`, then proceed to Deployment when ready.

### Baselines Verified
- S0: [OK]
- [Others as applicable]
```

**If Fixes Needed**:
```markdown
## Handoff: Security Review -> Developer

### Review Summary
- Document: sdlc_artifacts/reviews/REV-XXXX-...md
- Verdict: Needs Changes

### Required Fixes
1. [Must-fix 1]
2. [Must-fix 2]

### Returning to Developer.
```

## Tips

1. **Be Specific**: Exact files, lines, fixes
2. **Prioritize**: Exploitable issues first
3. **Context Matters**: Internal vs public differs
4. **Check Obvious**: Common issues are common
5. **Think Attacker**: What would you exploit?

