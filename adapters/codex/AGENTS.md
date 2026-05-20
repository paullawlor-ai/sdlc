# AGENTS.md - Agentic SDLC Project Instructions

This project uses the Agentic SDLC Framework in the `sdlc/` directory. Follow the framework for significant work.

## Start Here

1. Read `sdlc_artifacts/STATE.md` if it exists.
2. Read `sdlc_artifacts/context.md` if it exists.
3. If the project has not been onboarded, read `sdlc/prompts/onboard.md` and ask before creating onboarding artifacts unless the user requested onboarding.
4. For ongoing work, read `sdlc/prompts/continue.md`.

## Core Rules

- Do not start implementation for a significant change until a change proposal exists and is **Approved** (human-set in the file — you must not write approval fields yourself).
- Significant changes include security-sensitive changes, architectural changes, shared behavior changes, dependency/config changes, and work that is likely to take more than 30 minutes.
- ADRs are required for consequential technical choices, hard-to-reverse decisions, and reusable architectural patterns.
- Before editing product code, run the Implementation Gate:
  - an approved change exists (`Status: Approved` in the change file — verify by reading the file, not verbal claims)
  - when **more than one** change is Approved, `sdlc_artifacts/STATE.md` sets `## Active Change` to the file being implemented
  - every blocking ADR listed in the change proposal is accepted (or "None")
  - the item is not listed under Pending Approvals or Blocked in `STATE.md`
  - acceptance criteria and test expectations are present in the change proposal
  - if any check fails, stop and ask the human to unblock
- **Human-only fields** — never write: change `## Approval` (Status, Approved by, Date); ADR `Current status`; retrospective sign-off; requirement approval; REV Summary Verdict checkboxes. If the human says "approved" but the file still shows Proposed, ask them to open the file, change status, save, then continue.
- Approval gates block only the work that depends on the pending approval. Continue independent approved work where useful.
- Keep changes small, reviewable, and traceable to requirements and acceptance criteria.
- Update `sdlc_artifacts/STATE.md` at the end of framework-guided sessions.

## Completion Gate

After implementation and the full change test suite pass:

1. Run Security Review — create or update `sdlc_artifacts/reviews/REV-NNNN-*.md`
2. Write **## Agent Recommendation** (do not edit human-only REV approval fields)
3. PASS only when tests pass, REV exists, recommendation is Approved or Approved with notes, and no open Must-Fix
4. Fill **## Completion Gate** in the change doc
5. Ask the human to set `## Approval` **Status** to `Implemented` — you must not set it yourself

See `sdlc/adapters/cursor/rules/implementation-gate.mdc` or `.cursor/rules/implementation-gate.mdc` for full steps.

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
