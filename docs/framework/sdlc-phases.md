# SDLC Phases

The framework organizes software development into seven phases. Each phase has defined inputs, outputs, and quality gates.

## Phase Overview

```
+--------------+   +--------------+   +--------------+
| Requirements | -> |    Design    | -> |Implementation|
+--------------+   +--------------+   +--------------+
                                              |
+--------------+   +--------------+   +--------------+
|   Iterate    | <- |  Deployment  | <- |   Testing    |
+--------------+   +--------------+   +--------------+
                          ^
                   +--------------+
                   |   Security   |
                   |    Review    |
                   +--------------+
```

## Phase 1: Requirements

**Workflow**: `workflows/01-requirements.md`
**Agent**: Requirements Analyst

### Purpose
Transform raw ideas and stakeholder input into clear, actionable requirements.

### Inputs
- Initial project description
- Stakeholder notes
- Feature requests
- Constraints and preferences

### Activities
1. Clarify ambiguous requirements
2. Identify stakeholders and their needs
3. Break down into user stories
4. Define acceptance criteria
5. Prioritize features (MVP vs future)
6. Document non-functional requirements

### Outputs
- User stories with acceptance criteria
- Requirements documentation in `sdlc_artifacts/requirements/`
- Prioritized backlog
- Identified risks and constraints

### Quality Gate
- [ ] All user stories have acceptance criteria
- [ ] Non-functional requirements documented
- [ ] MVP scope clearly defined
- [ ] Stakeholder approval obtained

## Phase 2: Design

**Workflow**: `workflows/02-design.md`
**Agent**: Architect
**Supporting agents**: Web Designer/Engineer for browser UI design, when applicable

### Purpose
Create a technical design that satisfies requirements while following best practices.

### Inputs
- Approved requirements
- Technical constraints
- Existing system context (if any)
- Security baselines (S0, A0, V0, C0)

### Activities
1. Define system architecture
2. Create ADRs for key decisions
3. Design API contracts
4. Create data models
5. Define component boundaries
6. Plan integration points

### Outputs
- Architecture Decision Records in `sdlc_artifacts/decisions/`
- System diagrams in `sdlc_artifacts/design/`
- API specifications
- Data model documentation
- Component interfaces
- UI route and interaction design, when applicable

### Quality Gate
- [ ] ADRs created for major decisions
- [ ] Security baselines addressed in design
- [ ] API contracts defined
- [ ] Human approval on ADRs

## Phase 3: Implementation

**Workflow**: `workflows/03-implementation.md`
**Agent**: Developer
**Supporting agents**: Web Designer/Engineer for frontend work; Docs Writer for documentation updates

### Purpose
Build the software according to the approved design.

### Inputs
- Approved design and ADRs
- Coding standards
- Security guidelines
- Change proposal template

### Activities
1. Create change proposal before coding
2. Wait for change approval and acceptance of blocking ADRs
3. Run the Implementation Gate immediately before editing product code
4. Implement in small increments
5. Write unit tests
6. Follow security guidelines
7. Update middleware registry if needed
8. Document code

### Outputs
- Working code
- Unit tests
- Change documents in `sdlc_artifacts/changes/`
- Updated documentation
- Frontend implementation notes, when browser UI is in scope

### Quality Gate
- [ ] Change proposal approved before implementation
- [ ] Blocking ADRs accepted before implementation
- [ ] Implementation Gate passed
- [ ] Unit tests pass
- [ ] Code follows standards
- [ ] Documentation updated

## Phase 4: Testing

**Workflow**: `workflows/04-testing.md`
**Agent**: Tester

### Purpose
Verify the software meets requirements and works correctly.

### Inputs
- Implemented code
- Acceptance criteria
- Test plan template

### Activities
1. Create test plan
2. Write integration tests
3. Write end-to-end tests
4. Test edge cases and error handling
5. Verify acceptance criteria
6. Report coverage

### Outputs
- Test plan in `sdlc_artifacts/`
- Integration tests
- Test results
- Coverage report

### Quality Gate
- [ ] All acceptance criteria tested
- [ ] Integration tests pass
- [ ] Coverage meets threshold
- [ ] Edge cases covered

## Phase 5: Security Review

**Workflow**: `workflows/05-security-review.md`
**Agent**: Security Reviewer

### Purpose
Verify the software meets security requirements and follows best practices.

### Inputs
- Code changes
- Change proposals
- OWASP guidelines
- Security baselines

### Activities
1. Review against OWASP Top 10
2. Review against OWASP LLM Top 10 (if AI features)
3. Check secure coding controls
4. Verify security baseline compliance
5. Identify vulnerabilities
6. Create security review document

### Outputs
- Security review in `sdlc_artifacts/reviews/`
- Findings categorized (must-fix, should-fix, nice-to-have)
- Risk mappings
- Remediation suggestions

### Quality Gate
- [ ] No must-fix findings unaddressed
- [ ] Security baselines verified
- [ ] Rollback plan credible
- [ ] Policy-required human review evidence recorded for regulated/high-risk work

## Phase 6: Deployment

**Workflow**: `workflows/06-deployment.md`
**Agent**: DevOps

### Purpose
Prepare and execute deployment of the software.

### Inputs
- Tested, reviewed code
- Deployment requirements
- Infrastructure constraints

### Activities
1. Create/update CI/CD pipeline
2. Configure deployment targets
3. Write deployment runbook
4. Set up monitoring and alerts
5. Document rollback procedure
6. Execute deployment

### Outputs
- CI/CD configuration
- Deployment runbook in `sdlc_artifacts/runbooks/`
- Monitoring configuration
- Rollback procedure

### Quality Gate
- [ ] CI/CD pipeline works
- [ ] Deployment runbook complete
- [ ] Rollback tested
- [ ] Monitoring in place

## Phase 7: Iterate

**Workflow**: `workflows/07-iterate.md`
**Agent**: Orchestrator

### Purpose
Learn from the cycle and plan the next iteration.

### Inputs
- Completed deployment
- Feedback and metrics
- Backlog

### Activities
1. Conduct retrospective
2. Gather feedback
3. Review metrics
4. Update backlog
5. Prioritize next iteration
6. Archive completed items

### Outputs
- Retrospective notes
- Updated backlog
- Next iteration plan
- Lessons learned

### Quality Gate
- [ ] Retrospective completed
- [ ] Backlog updated
- [ ] Next iteration scoped
- [ ] Documentation current

## Phase Transitions

### Normal Flow
Requirements -> Design -> Implementation -> Testing -> Security Review -> Deployment -> Iterate

### Iteration Triggers
- Security findings require implementation changes
- Test failures require fixes
- Design changes require re-review

### Skip Conditions
- Small changes may skip full design phase
- Hotfixes may have abbreviated review
- Document all skips with justification

## Applying Security Baselines

Each phase should consider the baselines selected in
`sdlc_artifacts/context.md`. S0 always applies; A0, V0, and C0 apply only when
the project profile calls for them.

| Phase | S0 | A0 | V0 | C0 |
|-------|----|----|----|----|
| Requirements | Required | If applicable | If applicable | If applicable |
| Design | Required | If applicable | If applicable | If applicable |
| Implementation | Required | If applicable | If applicable | If applicable |
| Testing | Required | If applicable | If applicable | If applicable |
| Security Review | Required | If applicable | If applicable | If applicable |
| Deployment | Required | If applicable | If applicable | If applicable |
| Iterate | Review changes | Review changes | Review changes | Review changes |

Legend:
- **S0**: Base security controls
- **A0**: AI/LLM security controls
- **V0**: Audit/evidence controls
- **C0**: Cloud deployment controls
