# Agent System

The Agentic SDLC Framework uses specialized agents coordinated by an orchestrator to handle different aspects of software development.

In this framework, an "agent" is a role definition plus a workflow. Some AI
assistants implement that as a true sub-agent; others implement it as a prompt
or instruction file that the current assistant reads before acting. The process
is the same either way.

## Architecture Overview

```
+-------------------------------------------------------------+
|                    ORCHESTRATOR AGENT                        |
|  - Reads project state and requirements                      |
|  - Determines current SDLC phase                             |
|  - Delegates to specialized agents                           |
|  - Ensures documentation is maintained                       |
+-------------------------------------------------------------+
                              |
        +---------------------+---------------------+
        v                     v                     v
+---------------+    +---------------+    +---------------+
|  REQUIREMENTS |    |   ARCHITECT   |    |   DEVELOPER   |
|    ANALYST    |    |               |    |               |
+---------------+    +---------------+    +---------------+
        |                     |                     |
        v                     v                     v
+---------------+    +---------------+    +---------------+
|    TESTER     |    |   SECURITY    |    |    DEVOPS     |
|               |    |   REVIEWER    |    |               |
+---------------+    +---------------+    +---------------+
                              |
              +---------------+---------------+
              v                               v
    +---------------+               +---------------+
    |  DOCS WRITER  |               | WEB DESIGNER  |
    |               |               |  / ENGINEER   |
    +---------------+               +---------------+
```

## Agent Definitions

### Orchestrator Agent

**Location**: `agents/orchestrator.md`

**Responsibilities**:
- Initialize new projects from requirements
- Determine which SDLC phase to execute next
- Delegate tasks to specialized agents
- Track overall project progress
- Ensure all artifacts are properly documented
- Coordinate handoffs between phases

**Triggers**:
- Bootstrap prompt (`prompts/bootstrap.md`)
- Continue prompt (`prompts/continue.md`)
- Onboard prompt (`prompts/onboard.md`)
- Manual invocation

### Requirements Analyst Agent

**Location**: `agents/requirements-analyst.md`

**Responsibilities**:
- Clarify ambiguous requirements
- Break down high-level requirements into user stories
- Define acceptance criteria
- Identify missing requirements
- Create requirements documentation

**Inputs**: Raw requirements, stakeholder notes, feature requests
**Outputs**: User stories, acceptance criteria, requirements docs in `sdlc_artifacts/requirements/`

### Architect Agent

**Location**: `agents/architect.md`

**Responsibilities**:
- Design system architecture
- Create Architecture Decision Records (ADRs)
- Define API contracts and interfaces
- Create system diagrams
- Evaluate technology choices

**Inputs**: Requirements, constraints, existing system context
**Outputs**: ADRs in `sdlc_artifacts/decisions/`, design docs in `sdlc_artifacts/design/`

### Developer Agent

**Location**: `agents/developer.md`

**Responsibilities**:
- Implement features according to design
- Create change proposals before coding
- Write unit tests
- Follow coding standards and security guidelines
- Update documentation

**Inputs**: Approved designs, change proposals, coding standards
**Outputs**: Code, tests, change docs in `sdlc_artifacts/changes/`

### Tester Agent

**Location**: `agents/tester.md`

**Responsibilities**:
- Create test plans
- Write integration tests
- Define test cases from acceptance criteria
- Run tests and report results
- Track test coverage

**Inputs**: Requirements, acceptance criteria, implemented code
**Outputs**: Test plans, test code, coverage reports

### Security Reviewer Agent

**Location**: `agents/security-reviewer.md`

**Responsibilities**:
- Review code against OWASP guidelines
- Identify security vulnerabilities
- Map risks to controls
- Suggest mitigations
- Verify security requirements are met

**Inputs**: Code changes, change proposals, security baselines
**Outputs**: Security review docs in `sdlc_artifacts/reviews/`, findings

### DevOps Agent

**Location**: `agents/devops.md`

**Responsibilities**:
- Create CI/CD pipelines
- Define deployment configurations
- Write deployment runbooks
- Set up monitoring and alerting
- Document rollback procedures

**Inputs**: Application code, deployment requirements
**Outputs**: CI/CD configs, runbooks in `sdlc_artifacts/runbooks/`

### Supporting Specialist Agents

These agents do not own a whole SDLC phase. The orchestrator invokes them when
their specialty is relevant to the current phase or change.

### Docs Writer Agent

**Location**: `agents/docs-writer.md`

**Responsibilities**:
- Keep documentation up to date
- Generate API documentation
- Update README files
- Create user guides
- Maintain changelog

**Inputs**: Code changes, feature additions
**Outputs**: Updated documentation

**When to invoke**: After implementation or deployment, when public APIs, configuration options, or user-facing behaviour changed. Can run in parallel with testing.

### Web Designer/Engineer Agent

**Location**: `agents/web-designer.md`

**Responsibilities**:
- Design and implement browser-facing UI
- Connect frontend to backend services
- Maintain UX consistency across pages
- Build management/configuration interfaces

**Inputs**: Approved design ADRs, requirements, existing frontend code
**Outputs**: Frontend templates, updated views, design notes in `sdlc_artifacts/design/`

**When to invoke**: Optional - only for projects with a browser UI. Invoke after design ADRs are accepted, before or during the implementation phase for UI-heavy features.

## Agent Handoff Protocol

When one agent completes its work, it hands off to the next agent:

1. **Complete current task**: Finish all outputs for the current phase
2. **Update artifacts**: Ensure all documents are saved
3. **Signal completion**: Mark phase as complete in project state
4. **Provide context**: Summarize what was done and what's next
5. **Invoke next agent**: Orchestrator triggers the appropriate agent

## Agent Invocation

Agents can be invoked in several ways:

### Via Orchestrator (Recommended)
The orchestrator automatically invokes the right agent based on project state.

### Direct Invocation
For specific tasks, invoke an agent directly:
```
Act as the Security Reviewer agent. Read agents/security-reviewer.md and review the current changes.
```

### Phase-Specific Prompts
Use prompts in `prompts/phase-specific/` for targeted work:
```
Read prompts/phase-specific/security-review.md and begin
```

## State Management

The framework tracks project state through:

1. **Change Documents** (`sdlc_artifacts/changes/`): Track what's proposed, approved, implemented
2. **ADRs** (`sdlc_artifacts/decisions/`): Track architectural decisions
3. **Reviews** (`sdlc_artifacts/reviews/`): Track review outcomes
4. **Project Docs** (`sdlc_artifacts/`): Track requirements and design

The orchestrator reads these to determine project state and next steps.

## Best Practices

1. **Let the orchestrator coordinate**: Don't bypass the orchestrator for complex tasks
2. **Use direct invocation for focused work**: For quick tasks, invoke agents directly
3. **Review agent outputs**: Agents make proposals; humans approve
4. **Maintain documentation**: Agents depend on accurate documentation
5. **Follow the handoff protocol**: Don't skip phases or artifacts
