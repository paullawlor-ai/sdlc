# AGENTS.md - Agentic SDLC Project Instructions

This project uses the Agentic SDLC Framework in the `sdlc/` directory. Follow the framework for significant work.

## Start Here

1. Read `sdlc_artifacts/STATE.md` if it exists.
2. Read `sdlc_artifacts/context.md` if it exists.
3. If the project has not been onboarded, read `sdlc/prompts/onboard.md` and ask before creating onboarding artifacts unless the user requested onboarding.
4. For ongoing work, read `sdlc/prompts/continue.md`.

## Core Rules

- Do not start implementation for a significant change until a change proposal exists and is approved.
- Significant changes include security-sensitive changes, architectural changes, shared behavior changes, dependency/config changes, and work that is likely to take more than 30 minutes.
- ADRs are required for consequential technical choices, hard-to-reverse decisions, and reusable architectural patterns.
- Before editing product code for implementation, run the Implementation Gate:
  - active change exists and Approval status is `Approved`
  - every blocking ADR listed by the change, `STATE.md`, or design context is accepted
  - the item is not listed under Pending Approvals or Blocked in `STATE.md`
  - acceptance criteria and test expectations are present
  - if any check fails, stop and ask for approval
- Approval gates block only the work that depends on the pending approval. Continue independent approved work where useful.
- Keep changes small, reviewable, and traceable to requirements and acceptance criteria.
- Update `sdlc_artifacts/STATE.md` at the end of framework-guided sessions.

## Phase Entry Points

| Need | File |
| --- | --- |
| Adopt an existing codebase | `sdlc/prompts/onboard.md` |
| Start a new project | `sdlc/prompts/bootstrap.md` |
| Resume work | `sdlc/prompts/continue.md` |
| Quick status | `sdlc/prompts/quick-status.md` |
| Requirements | `sdlc/prompts/phase-specific/requirements.md` |
| Design | `sdlc/prompts/phase-specific/design.md` |
| Implementation | `sdlc/prompts/phase-specific/implementation.md` |
| Testing | `sdlc/prompts/phase-specific/testing.md` |
| Security review | `sdlc/prompts/phase-specific/security-review.md` |
| Deployment | `sdlc/prompts/phase-specific/deployment.md` |
| Documentation | `sdlc/prompts/phase-specific/docs.md` |
| Browser UI | `sdlc/prompts/phase-specific/web-design.md` |

## Agent Roles

Specialized role definitions live in `sdlc/agents/`.

- Orchestrator coordinates state, phase transitions, and handoffs.
- Requirements Analyst turns needs into stories and acceptance criteria.
- Architect creates design docs and ADRs.
- Developer implements approved changes.
- Tester links tests to acceptance criteria.
- Security Reviewer checks OWASP and baseline compliance.
- DevOps prepares CI/CD, deployment, monitoring, and rollback.
- Docs Writer maintains user and project documentation.
- Web Designer/Engineer handles browser-facing UI and frontend workflows when applicable.

When the user asks you to act as one of these roles, read the matching file before working.

## Security Baselines

Apply:

- S0 for every project.
- A0 for AI/LLM features.
- V0 when auditability or compliance evidence is required.
- C0 for cloud deployment.

Use `sdlc/docs/security/security-baselines.md` and the catalogs in `sdlc/catalogs/` as references.

## Codex Notes

- Prefer repository conventions over framework defaults when implementing product code.
- Avoid editing `sdlc/` unless the user is changing the framework itself.
- If `sdlc/` is gitignored, generated SDLC artifacts such as `sdlc_artifacts/STATE.md`, project context, requirements, ADRs, change proposals, reviews, and runbooks should live in the host project locations expected by the framework.
