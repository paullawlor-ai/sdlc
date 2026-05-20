# Lifecycle Example

This example shows how a small feature moves through the framework. It is not
about the specific product; it is about the shape of traceability.

## Scenario

The project owner asks:

```text
Add password reset by email.
```

## 1. Requirements

The Requirements Analyst creates or updates a requirement:

```text
sdlc_artifacts/requirements/REQ-0007-password-reset.md
```

Example acceptance criteria:

| AC ID | Criterion |
|-------|-----------|
| AC-1 | Given a registered user, when they request a reset link, then a time-limited reset email is sent. |
| AC-2 | Given an unknown email address, when reset is requested, then the response does not reveal whether the account exists. |
| AC-3 | Given an expired or reused token, when reset is attempted, then the request is rejected. |

## 2. Design

The Architect decides whether an ADR is needed.

If the project already has email delivery and token storage patterns, no ADR may
be required. If the feature introduces a new email provider or token strategy,
create an ADR:

```text
sdlc_artifacts/decisions/proposed/ADR-0005-password-reset-token-strategy.md
```

The ADR is moved to `accepted/` only after human approval.

## 3. Change Proposal

Before implementation, the Developer creates:

```bash
python sdlc/scripts/new_change.py "password reset by email"
```

The change proposal records:

- Scope and files likely touched.
- Acceptance criteria table linked back to `REQ-0007`.
- Security impact: account enumeration, token lifetime, logging, rate limits.
- Test approach.
- Rollback plan.

Implementation waits until the proposal status is `Approved`.

## 4. Implementation

The Developer implements only the approved scope:

- API endpoint or UI route for requesting reset.
- Token creation and validation.
- Email dispatch integration.
- Tests for happy path, unknown email, expired token, reused token, and rate limits.

The change proposal is updated with actual hours and status `Implemented`.

## 5. Testing

The Tester creates or updates:

```text
sdlc_artifacts/test-plan.md
```

The test plan maps test IDs to acceptance criteria:

| Test ID | Acceptance Criteria | Evidence |
|---------|---------------------|----------|
| T-RESET-001 | AC-1 | Unit and integration test output |
| T-RESET-002 | AC-2 | Negative test output |
| T-RESET-003 | AC-3 | Token expiry/reuse test output |

## 6. Security Review

The Security Reviewer creates:

```text
sdlc_artifacts/reviews/REV-0003-password-reset.md
```

Checks include:

- S0: no account enumeration, no secrets in logs, safe error messages.
- A0: N/A unless AI is involved.
- V0: reset events audited if audit baseline applies.
- C0: email provider secrets managed securely if cloud baseline applies.

Must-fix findings block deployment until remediated or risk-accepted.

## 7. Deployment

The DevOps agent updates the runbook if needed:

```text
sdlc_artifacts/runbooks/deployment.md
```

Deployment evidence records:

- Migration steps, if any.
- Email provider configuration.
- Rollback procedure.
- Monitoring checks.

## 8. Iterate

The Orchestrator updates:

```text
sdlc_artifacts/STATE.md
```

The final "Left off at" sentence should be specific:

```text
Password reset is implemented, tested, security reviewed, and ready for the next iteration backlog selection.
```

## Traceability Chain

```text
Requirement -> Acceptance Criteria -> ADR if needed -> Change Proposal -> Tests -> Security Review -> Deployment Evidence -> STATE.md
```
