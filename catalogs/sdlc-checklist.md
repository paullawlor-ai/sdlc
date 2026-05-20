# SDLC Phase Checklist

A comprehensive checklist for each phase of the Software Development Lifecycle.

## Phase 1: Requirements

### Gathering
- [ ] Initial project description documented
- [ ] Stakeholders identified
- [ ] User types/personas defined
- [ ] Constraints documented (technical, business, time)

### User Stories
- [ ] All major features have user stories
- [ ] Each story follows: As a [user], I want [feature], so that [benefit]
- [ ] Stories are sized appropriately (not too large)

### Acceptance Criteria
- [ ] Each story has acceptance criteria
- [ ] Criteria use Given/When/Then format
- [ ] Criteria are testable and measurable
- [ ] Edge cases identified

### Non-Functional Requirements
- [ ] Performance requirements defined
- [ ] Scalability requirements defined
- [ ] Availability requirements defined
- [ ] Security requirements identified

### Security Requirements
- [ ] Applicable baselines identified (S0, A0, V0, C0)
- [ ] Authentication requirements documented
- [ ] Authorization requirements documented
- [ ] Data sensitivity classification done
- [ ] Compliance requirements noted

### Prioritization
- [ ] MVP scope clearly defined
- [ ] Features prioritized (Must/Should/Could/Won't)
- [ ] Dependencies identified
- [ ] Risks documented

### Approval
- [ ] Stakeholder review completed
- [ ] Requirements documented in `sdlc_artifacts/requirements/`

## Phase 2: Design

### Architecture
- [ ] High-level architecture defined
- [ ] Component breakdown documented
- [ ] Data flow documented
- [ ] Integration points identified

### ADRs
- [ ] Key decisions documented as ADRs
- [ ] Each ADR has alternatives considered
- [ ] Each ADR has security notes
- [ ] ADRs approved and in `sdlc_artifacts/decisions/accepted/`

### Interfaces
- [ ] API contracts defined
- [ ] Data models documented
- [ ] Component interfaces specified

### Security Design
- [ ] Authentication strategy chosen
- [ ] Authorization model designed
- [ ] Data protection approach defined
- [ ] For AI: A0 controls designed

### Approval
- [ ] Design reviewed
- [ ] ADRs accepted
- [ ] Ready for implementation

## Phase 3: Implementation

### Change Proposal
- [ ] Change proposal created before coding
- [ ] Scope clearly defined
- [ ] Blocking ADRs/dependencies listed, or explicitly marked "None"
- [ ] Security impact documented
- [ ] Rollback plan documented
- [ ] Change proposal approved
- [ ] Blocking ADRs accepted

### Coding
- [ ] Implementation Gate passed immediately before product-code edits
- [ ] Follows approved design
- [ ] Follows coding standards
- [ ] Follows security controls from catalog
- [ ] No secrets in code or logs
- [ ] Appropriate error handling

### Unit Tests
- [ ] Unit tests written
- [ ] Happy path covered
- [ ] Edge cases covered
- [ ] Error conditions covered
- [ ] Tests passing

### Documentation
- [ ] Code is self-documenting
- [ ] Public APIs documented
- [ ] README updated if needed

### Self-Review
- [ ] Code matches change proposal
- [ ] Implementation Gate result recorded
- [ ] Security controls implemented
- [ ] No obvious issues

## Phase 4: Testing

### Test Plan
- [ ] Test plan created
- [ ] Scope defined (in/out)
- [ ] Test types identified

### Functional Tests
- [ ] All acceptance criteria have tests
- [ ] Integration tests written
- [ ] End-to-end tests for critical paths

### Edge Case Tests
- [ ] Boundary conditions tested
- [ ] Invalid inputs tested
- [ ] Error conditions tested

### Security Tests
- [ ] Authentication tests
- [ ] Authorization tests
- [ ] Input validation tests
- [ ] For AI: Injection tests

### Results
- [ ] All tests passing
- [ ] Coverage meets threshold
- [ ] Results documented
- [ ] Ready for security review

## Phase 5: Security Review

### OWASP Review
- [ ] Reviewed against OWASP Top 10
- [ ] Reviewed against OWASP LLM Top 10 (if AI)
- [ ] Checked secure coding controls

### Baseline Verification
- [ ] S0 baseline verified
- [ ] A0 baseline verified (if AI)
- [ ] V0 baseline verified (if audit required)
- [ ] C0 baseline verified (if cloud)

### Findings
- [ ] Must-fix items identified
- [ ] Should-fix items identified
- [ ] Nice-to-have suggestions noted
- [ ] Review document created

### Resolution
- [ ] Must-fix items addressed
- [ ] Rollback plan credible
- [ ] Review approved
- [ ] Ready for deployment

## Phase 6: Deployment

### Pre-Deployment
- [ ] All tests passing in CI
- [ ] Security review approved
- [ ] Change proposal approved
- [ ] Secrets configured
- [ ] Database backup taken (if applicable)

### CI/CD
- [ ] Pipeline configured
- [ ] Build stage working
- [ ] Test stage working
- [ ] Security scan stage working
- [ ] Deploy stage working

### Runbook
- [ ] Deployment runbook created
- [ ] Pre-deployment steps documented
- [ ] Deployment steps documented
- [ ] Verification steps documented
- [ ] Rollback steps documented

### Monitoring
- [ ] Health checks configured
- [ ] Metrics configured
- [ ] Alerts configured
- [ ] Dashboard available

### Execution
- [ ] Deployment initiated
- [ ] Deployment successful
- [ ] Health checks passing
- [ ] Smoke tests passing
- [ ] No error spikes

### Post-Deployment
- [ ] Change status updated
- [ ] Stakeholders notified
- [ ] Monitoring verified

## Phase 7: Iterate

### Retrospective
- [ ] What went well documented
- [ ] What could improve documented
- [ ] Action items created
- [ ] Lessons learned captured

### Metrics Review
- [ ] Performance metrics reviewed
- [ ] Error rates reviewed
- [ ] User feedback collected

### Backlog Update
- [ ] New items added
- [ ] Completed items closed
- [ ] Priorities updated

### Next Iteration
- [ ] Scope defined
- [ ] Timeline estimated
- [ ] Team aligned

---

## Quick Reference: Minimum Viable Checklist

For smaller changes, use this abbreviated checklist:

### Before Coding
- [ ] Change proposal created and approved
- [ ] Blocking ADRs accepted
- [ ] Implementation Gate passed

### During Coding
- [ ] Follows security controls
- [ ] Unit tests written
- [ ] No secrets in code

### Before Merge
- [ ] Tests passing
- [ ] Security review done (for security-relevant changes)
- [ ] Rollback plan documented

### After Deployment
- [ ] Health checks passing
- [ ] No errors in logs

---

## Security Baseline Quick Checks

### S0 (All Projects)
- [ ] Auth enforced on all endpoints
- [ ] Input validation centralized
- [ ] Output encoding appropriate
- [ ] No secrets in logs/code
- [ ] TLS everywhere
- [ ] Dependencies scanned

### A0 (AI Projects)
- [ ] Model output untrusted
- [ ] Prompt injection controls
- [ ] Tool permissions restricted
- [ ] Output validation
- [ ] Token limits configured

### V0 (Audit Required)
- [ ] Event logging implemented
- [ ] Trace IDs included
- [ ] Tamper evidence (if required)

### C0 (Cloud Deployment)
- [ ] IAM least privilege
- [ ] Secrets in KMS
- [ ] Private networking
- [ ] Central logging
