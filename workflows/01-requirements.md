# Phase 1: Requirements Workflow

## Overview

The Requirements phase transforms raw ideas and stakeholder input into clear, documented, and testable requirements.

## Agent

**Primary**: Requirements Analyst (`agents/requirements-analyst.md`)

## Inputs

- Initial project description or idea
- Stakeholder notes and feedback
- Feature requests
- Constraints (technical, business, time)

## Activities

### 1. Gather Information

Collect all available input:
- Read any existing documentation
- Note stakeholder requirements
- Identify constraints and preferences

Ask clarifying questions:
- Who are the users?
- What problem does this solve?
- What does success look like?
- What are the constraints?

### 2. Analyze Requirements

For each requirement:
- Determine type (functional, non-functional, security, compliance)
- Assess priority (MVP vs. future)
- Identify dependencies
- Note risks and assumptions

### 3. Create User Stories

Transform requirements into user stories:

```
As a [user type],
I want [feature/capability],
So that [benefit/value].
```

Add acceptance criteria:

```
Given [initial context],
When [action is performed],
Then [expected result].
```

### 4. Document Requirements

Create requirement documents:
```bash
python sdlc/scripts/new_requirement.py "requirement title"
```

For complex features, create detailed requirement docs in `sdlc_artifacts/requirements/`.

### 5. Review and Validate

Ensure:
- All user stories have acceptance criteria
- Each criterion is testable
- Edge cases are identified
- Security considerations are noted
- MVP scope is clear

## Outputs

| Output | Location |
|--------|----------|
| User stories | `sdlc_artifacts/requirements/` |
| Requirement documents | `sdlc_artifacts/requirements/` |
| Prioritized backlog | `sdlc_artifacts/requirements/` |

## Quality Checklist

Before completing this phase:

- [ ] All major features have user stories
- [ ] Each user story has acceptance criteria
- [ ] Acceptance criteria are testable (Given/When/Then)
- [ ] Edge cases and error scenarios documented
- [ ] Non-functional requirements identified
- [ ] Security considerations noted
- [ ] MVP scope clearly defined
- [ ] Dependencies identified
- [ ] Stakeholder approval obtained (if applicable)

## Security Considerations

During requirements gathering, identify:
- Which security baselines apply (S0, A0, V0, C0)
- Authentication and authorization requirements
- Data sensitivity and handling requirements
- Audit and compliance requirements
- AI/LLM specific requirements (if applicable)

## Approval Gate

No formal approval gate for requirements, but:
- Stakeholder review is recommended
- MVP scope should be agreed upon

## Phase Transition

**Next Phase**: Design

**Transition Trigger**: Requirements documented with acceptance criteria

**Handoff to Architect**:
```markdown
## Handoff: Requirements -> Design

### Requirements Summary
- Total requirements: [count]
- MVP scope: [list]
- Security baselines: S0 [A0, V0, C0 if applicable]

### Key Documents
- [List of requirement documents]

### Open Questions for Design
- [Any unresolved technical questions]

### Ready for design phase.
```

## Common Patterns

### For AI/LLM Features

Always include requirements for:
- Input validation and sanitization
- Output handling and filtering
- Rate limiting and cost controls
- Data boundaries and access control
- Human oversight needs

### For Authentication

Always include:
- Login/logout flows
- Session management
- Password policies (if applicable)
- MFA requirements
- Account recovery

### For Data Handling

Always include:
- Data classification
- Access control requirements
- Retention policies
- Privacy considerations

## Tips

1. **Be Specific**: Vague requirements lead to vague implementations
2. **Think Negative**: What should NOT happen is important too
3. **Consider Scale**: How will this work at 10x load?
4. **Ask Why**: Understanding motivation helps make better decisions
5. **Document Assumptions**: Make implicit assumptions explicit

