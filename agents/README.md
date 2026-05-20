# Agents

Specialized agent definitions for the Agentic SDLC Framework.

## Available Agents

| Agent | File | Purpose |
|-------|------|---------|
| Orchestrator | `orchestrator.md` | Coordinates all agents, manages SDLC flow |
| Requirements Analyst | `requirements-analyst.md` | Clarifies and documents requirements |
| Architect | `architect.md` | Designs systems, creates ADRs |
| Developer | `developer.md` | Implements code, creates change proposals |
| Tester | `tester.md` | Creates test plans, writes tests |
| Security Reviewer | `security-reviewer.md` | Reviews for security issues |
| DevOps | `devops.md` | Handles CI/CD, deployment |
| Docs Writer | `docs-writer.md` | Maintains documentation |
| Web Designer/Engineer | `web-designer.md` | Designs and implements browser-facing UI |

The Requirements Analyst, Architect, Developer, Tester, Security Reviewer,
DevOps, and Orchestrator map directly to SDLC phases. Docs Writer and Web
Designer/Engineer are supporting specialists: invoke them when documentation or
browser UI work is part of the current phase.

## How to Use

### Via Orchestrator (Recommended)
The orchestrator automatically invokes the right agent:
```
Read prompts/bootstrap.md and begin
```

### Direct Invocation
For specific tasks:
```
Act as the [Agent Name] agent. Read agents/[file].md and [task].
```

Example:
```
Act as the Security Reviewer agent. Read agents/security-reviewer.md and review the current changes.
```

## Agent Workflow

Each agent follows a structured workflow:
1. Read context (requirements, design, code)
2. Perform their specialized task
3. Produce outputs (documents, code, reviews)
4. Hand off to next agent or orchestrator

See `docs/framework/agent-system.md` for details.
