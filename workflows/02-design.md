# Phase 2: Design Workflow

## Overview

The Design phase creates a technical architecture that satisfies requirements while following best practices and security guidelines.

## Agent

**Primary**: Architect (`agents/architect.md`)

**Supporting**: Web Designer/Engineer (`agents/web-designer.md`) when the
project includes browser-facing UI, interaction design, or frontend workflow
decisions.

## Inputs

- Documented requirements from Phase 1
- Security baselines (`docs/security/security-baselines.md`)
- OWASP guidelines (`catalogs/`)
- Technical constraints

## Activities

### 1. Understand Requirements

Read all requirements:
- User stories and acceptance criteria
- Non-functional requirements
- Security requirements
- Constraints

### 2. Design Architecture

Create a high-level design covering:
- Component breakdown
- Data flow
- Integration points
- Security boundaries
- Technology choices

### 3. Make Key Decisions

For each significant decision, create an ADR:

```bash
python sdlc/scripts/new_adr.py "decision title"
```

ADRs are required for:
- Technology choices (framework, database, etc.)
- Architecture patterns
- Security approaches
- Integration strategies

Complete each generated Draft, then validate and promote it before requesting
human acceptance:

```bash
python sdlc/scripts/sdlc.py propose sdlc_artifacts/decisions/proposed/ADR-NNNN-title.md
```

### 4. Define Interfaces

Document:
- API contracts (endpoints, methods, payloads)
- Data models (schemas, relationships)
- Component interfaces
- UI routes, screens, navigation, and interaction contracts where applicable

### 4a. Design Browser-Facing UI (If Applicable)

For projects with a web interface, invoke the Web Designer/Engineer agent to
shape frontend architecture and UX details before implementation:

```text
Act as the Web Designer/Engineer agent.
Read agents/web-designer.md.
Based on the accepted requirements and design direction, define the browser UI structure, key screens, interaction states, and frontend handoff notes.
```

Capture outputs in `sdlc_artifacts/design/` and reference any consequential UI
or frontend architecture decisions from ADRs.

### 5. Address Security

For each applicable baseline, document how it's addressed:
- S0: Authentication, authorization, input validation, etc.
- A0: AI controls (if applicable)
- V0: Audit logging (if applicable)
- C0: Cloud security (if applicable)

### 6. Get Approval

Present design and ADRs for approval.

## Outputs

| Output | Location |
|--------|----------|
| Architecture Decision Records | `sdlc_artifacts/decisions/proposed/` -> `accepted/` |
| Design documents | `sdlc_artifacts/design/` |
| API specifications | `sdlc_artifacts/design/` |
| Data models | `sdlc_artifacts/design/` |
| UI / frontend design notes | `sdlc_artifacts/design/` |

## Quality Checklist

Before completing this phase:

- [ ] Major decisions documented as ADRs
- [ ] ADRs include alternatives considered
- [ ] ADRs include security notes
- [ ] Component interfaces defined
- [ ] Data models documented
- [ ] Security baselines addressed in design
- [ ] API contracts specified
- [ ] UI contracts specified when browser-facing UI is in scope
- [ ] Integration points identified

## Security in Design

Address these areas:

### Authentication
- Strategy chosen (OIDC, API keys, etc.)
- Implementation approach
- Session management

### Authorization
- Access control model
- Where enforced
- Least privilege approach

### Data Protection
- Sensitive data identified
- Encryption approach
- Data boundaries

### For AI Features
- Input sanitization approach
- Tool permission model
- Output validation
- Cost control strategy

## Approval Gate

**Required**: ADR approval before implementation

```markdown
[PAUSE] APPROVAL GATE: Architecture Decision Records

The following ADRs require approval:

1. sdlc_artifacts/decisions/proposed/ADR-0001-[title].md
2. sdlc_artifacts/decisions/proposed/ADR-0002-[title].md

To proceed:
1. Review each ADR
2. Move approved ADRs to sdlc_artifacts/decisions/accepted/
3. Update status to "Accepted"
4. Tell me to continue

Waiting for approval...
```

## Phase Transition

**Next Phase**: Implementation

**Transition Trigger**: Key ADRs accepted

**Handoff to Developer**:
```markdown
## Handoff: Design -> Implementation

### Approved Design
- ADRs: [List of accepted ADRs]
- Design docs: [List of design documents]

### Implementation Order
1. [First component to build]
2. [Second component to build]

### Key Interfaces
- [Interface summaries]

### Security Controls to Implement
- [List from baselines]

### Suggested First Change
[Recommendation for first change proposal]
```

## ADR Format Reference

```markdown
# ADR-XXXX - [Title]

## Status
- **Current status**: Draft

## Context
[Problem being solved, constraints]

## Decision Drivers
1. [Driver 1]
2. [Driver 2]

## Options Considered

### Option A
- Description
- Pros
- Cons
- Risks

### Option B
- Description
- Pros
- Cons
- Risks

## Decision
[Which option and why]

## Consequences
- Positive:
- Negative:
- Follow-up:

## Security Notes
- Threats:
- Mitigations:
- Controls:
```

## Tips

1. **Start Simple**: Add complexity only when justified
2. **Document Why**: The rationale matters more than the choice
3. **Think Failure**: Design for what goes wrong
4. **Consider Ops**: How will this be deployed and monitored?
5. **Review Security Early**: Cheaper to fix in design than code
