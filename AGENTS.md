# AGENTS.md - Agentic SDLC Framework

This directory contains the Agentic SDLC Framework. It is a portable framework for running software projects through repeatable, change-controlled SDLC phases with AI coding assistants.

## Context Modes

### Maintaining This Framework

If the current task is about files inside `sdlc/` itself, treat this as framework maintenance.

- Do not write application code here.
- Edit framework documents, agents, workflows, templates, scripts, examples, and adapter files only.
- Preserve the framework's portability across Cursor, Claude Code, GitHub Copilot, Codex, and other assistants.
- Keep instructions concise enough for assistant context limits.
- Prefer ASCII in new framework files unless the file already deliberately uses non-ASCII.

Major framework structure changes should have an ADR in `sdlc_artifacts/decisions/` if this framework repository is being maintained as its own repo.

### Using This Folder Inside a Host Project

If this directory is named `sdlc/` inside another project, the host project is the product being built. Work from the host project root, not from inside `sdlc/`, unless the user is explicitly asking to change the framework.

Use these entry points:

| Situation | Prompt |
| --- | --- |
| New project | `Read sdlc/prompts/bootstrap.md and begin` |
| Existing project adoption | `Read sdlc/prompts/onboard.md and begin` |
| Resume work | `Read sdlc/prompts/continue.md and resume` |
| Quick status only | `Read sdlc/prompts/quick-status.md and report` |
| Specific phase | `Read sdlc/prompts/phase-specific/<phase>.md and begin` |
| Documentation update | `Read sdlc/prompts/phase-specific/docs.md and begin` |
| Browser UI work | `Read sdlc/prompts/phase-specific/web-design.md and begin` |

## Core Discipline

- Read `sdlc_artifacts/STATE.md` first when it exists.
- Read `sdlc_artifacts/context.md` next when it exists.
- Significant changes need a change proposal before implementation.
- Architectural decisions need ADRs before downstream work depends on them.
- Before editing product code for implementation, run the Implementation Gate:
  - Confirm the active change document exists and its Approval status is `Approved`.
  - Confirm every blocking ADR named by the change, `STATE.md`, or the design context is accepted and lives under `sdlc_artifacts/decisions/accepted/`.
  - Confirm the work is not listed under Pending Approvals or Blocked in `sdlc_artifacts/STATE.md`.
  - Confirm acceptance criteria and testing expectations are present.
  - If any check fails, stop and ask for approval; do not implement the dependent code.
- Approval gates block only the dependent work, not unrelated independent work.
- Preserve traceability from requirements to acceptance criteria, tests, reviews, and deployment evidence.
- Apply the relevant security baselines: S0 always, A0 for AI/LLM features, V0 for audit/compliance, C0 for cloud deployment.

## Framework Locations

| Path | Purpose |
| --- | --- |
| `agents/` | Specialized agent role definitions |
| `prompts/` | Start, continue, onboard, quick status, and phase prompts |
| `workflows/` | Phase-by-phase execution guides |
| `templates/` | Document and starter project templates |
| `sdlc_artifacts/changes/` | Change proposals |
| `sdlc_artifacts/decisions/` | ADRs |
| `sdlc_artifacts/` | Host project requirements, design, runbooks, retrospectives |
| `sdlc_artifacts/reviews/` | Security and quality review records |
| `catalogs/` | OWASP and SDLC reference material |
| `adapters/` | Assistant-specific steering file templates |

## Codex Working Notes

- Codex reads `AGENTS.md` and `AGENTS.override.md` automatically when they are on the project instruction path.
- If `sdlc/` is gitignored in a host project, copy or adapt `sdlc/adapters/codex/AGENTS.md` into the host project root as `AGENTS.md`.
- Keep this file focused on always-on behavior. Detailed phase behavior belongs in `prompts/`, `agents/`, and `workflows/`.
