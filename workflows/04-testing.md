# Phase 4: Testing Workflow

## Overview

The Testing phase verifies that implementations meet requirements, work correctly, and handle edge cases appropriately.

## Agent

**Primary**: Tester (`agents/tester.md`)

## Inputs

- Implemented code from Phase 3
- Requirements and acceptance criteria
- Change documents
- Unit tests (from developer)

## Activities

### 1. Create Test Plan

Create a test plan covering:
- Functional tests
- Edge case tests
- Negative tests
- Security tests

Use `templates/documents/test-plan.md`.

### 2. Map Acceptance Criteria

For each AC row in the change document or requirement:
- Create the corresponding test
- Fill in the **Test ID** column in the AC table (function name, pytest node ID, or test marker)
- This is the traceability record - don't skip it

### 3. Write Tests

Create:
- Integration tests
- End-to-end tests (for critical flows)
- Negative tests (error handling)
- Security tests (control verification)

### 4. Execute Tests

Run all tests:
- Unit tests (from developer)
- Integration tests
- End-to-end tests

Track results and coverage.

### 5. Report Results

Document:
- Pass/fail status
- Coverage metrics
- Any failures
- Recommendations

## Outputs

| Output | Location |
|--------|----------|
| Test plan | `sdlc_artifacts/` |
| Test code | Test directories |
| Test results | Test reports |
| Coverage report | Test reports |

## Quality Checklist

Before completing this phase:

- [ ] Test plan created
- [ ] All acceptance criteria have test cases
- [ ] Integration tests written
- [ ] Negative/error tests written
- [ ] Security control tests included
- [ ] All tests passing
- [ ] Coverage meets threshold
- [ ] Results documented

## Test Types

### Unit Tests
(Created by Developer)
- Individual function/method tests
- Isolated, fast, deterministic

### Integration Tests
- Component interaction tests
- API endpoint tests
- Database interaction tests

### End-to-End Tests
- Full user flow tests
- Critical path verification

### Negative Tests
- Invalid input handling
- Unauthorized access attempts
- Error conditions
- Rate limit testing

### Security Tests
- Authentication verification
- Authorization verification
- Input validation effectiveness
- Injection attempt handling

## Acceptance Criteria Testing

For criteria in Given/When/Then format:

```python
def test_user_login():
    """
    Given a registered user with valid credentials,
    When they submit the login form,
    Then they should be authenticated.
    """
    # Given
    user = create_test_user()
    
    # When
    response = client.post("/login", json={...})
    
    # Then
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Test Results Format

```markdown
## Test Results: [Feature Name]

### Summary
- Total tests: X
- Passed: X
- Failed: X
- Coverage: X%

### Acceptance Criteria
| Criterion | Status | Test(s) |
|-----------|--------|---------|
| AC-1 | [OK] Pass | TC-001 |
| AC-2 | [X] Fail | TC-003 |

### Failures
#### TC-003: [Name]
- Expected: [result]
- Actual: [result]
- Root cause: [if known]

### Recommendations
- [Action items]

### Verdict
- [x] Ready for Security Review
- [ ] Needs fixes
```

## No Formal Approval Gate

Testing doesn't have a formal approval gate, but:
- All tests must pass before proceeding
- Coverage thresholds must be met
- Failures return to Developer for fixes

## Phase Transition

**Next Phase**: Security Review (mandatory — not optional)

**Transition Trigger**: All tests passing, coverage adequate

The Tester does **not** mark the change `Implemented`. After tests pass:

1. Invoke Security Reviewer (or run Completion Gate per `implementation-gate.mdc`).
2. Create or update `sdlc_artifacts/reviews/REV-NNNN-*.md` with **Agent Recommendation**.
3. Fill `## Completion Gate` in the change document.
4. Human sets Approval **Status** to `Implemented` only when Completion Gate **PASS**.

See `agents/tester.md` for handoff templates and `workflows/05-security-review.md` for the review workflow.

## Tips

1. **Test Behavior**: Verify what code does, not how
2. **Independent Tests**: Each test runs alone
3. **Clear Names**: Names describe scenarios
4. **Clean Data**: Isolated test data, cleanup after
5. **Prioritize**: Focus on critical paths first

