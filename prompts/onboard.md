# Onboard Prompt

Use this prompt to adopt the Agentic SDLC Framework into an **existing project** that has not previously used it.

---

## Instructions for AI Agent

You are onboarding an existing project into the **Agentic SDLC Framework**. The codebase already exists. Do NOT start the SDLC from scratch - your task is archaeology: reconstruct framework artifacts that reflect current reality, then position sdlc_artifacts/STATE.md at the honest current phase so future sessions can use `continue.md` normally.

### Step 0: Confirm Project Setup

Before touching artifacts or product code, confirm adapters are installed at the **host project root**:

```bash
python scripts/verify_setup.py
# or, in embedded mode:
python sdlc/scripts/verify_setup.py
```

If verification fails, ask the human to run once from the project root:

```bash
python scripts/setup_project.py
# or, in embedded mode:
python sdlc/scripts/setup_project.py
```

Do not proceed until setup passes or the human confirms they have run it.

### Step 1: Read the Framework

Read these files to understand the framework before touching anything (use `sdlc/` prefix when embedded):

**Embedded layout:**
- `sdlc/agents/orchestrator.md` - your role and how sdlc_artifacts/STATE.md works
- `sdlc/docs/framework/sdlc-phases.md` - phase definitions and quality gates
- `sdlc/docs/security/security-baselines.md` - security requirements

**Root-template** (framework is repo root): same paths without the `sdlc/` prefix.

### Step 2: Explore the Existing Project

Read the codebase to understand what was built and how. Focus on:

```
Priority reads (do these first):
- README.md (or equivalent) at the project root
- Any existing docs, wikis, or design notes
- Entry point files (main.py, index.ts, app.py, etc.)
- Configuration files (pyproject.toml, package.json, Dockerfile, CI/CD config)
- Test files - how much coverage exists?
- Historical change, fix, remediation, incident, or patch logs (for example `changes/`, `fixes/`, `incidents/`, `remediations/`, `patches/`, `reviews/`)
- Any existing requirements, specs, or tickets referenced in comments/docs
```

Do not read every source file. Sample enough to answer:
1. What does this project do? (purpose and key features)
2. What is the technology stack? (language, frameworks, databases, infrastructure)
3. What architectural decisions were made? (framework choice, data model, auth approach, API style, etc.)
4. What is the current state of testing? (none / partial / good coverage)
5. Has a security review ever been done?
6. Is this deployed? If so, how?
7. Are there historical fixes/remediations/incidents that should be preserved as V0 evidence or regression-risk context?

### Step 3: Create `sdlc_artifacts/context.md`

Create this file from `templates/documents/project-context.md`. Fill in everything you can infer from the codebase. Flag any fields you cannot determine with `[UNKNOWN - ask owner]`.

This file is essential - all agents read it on every session start.

### Step 4: Reconstruct Requirements

Run `sdlc.py new requirement "existing project behavior"` and complete the
generated numbered requirement with current user stories and acceptance criteria.
Keep its approval fields for the human to complete.

- Derive these from the code, README, and any existing docs - not from imagination
- Only document what is demonstrably implemented
- Note gaps where acceptance criteria cannot be inferred: `[AC unknown - needs clarification]`
- Do not invent requirements for features that don't exist yet

### Step 5: Reconstruct Architecture Decisions as ADRs

For each major technical decision already made (language, framework, database, auth, API style, deployment target, etc.), create a retroactive ADR in `sdlc_artifacts/decisions/proposed/` using the template at `templates/documents/adr.md`.

Rules for retroactive ADRs:
- Start as **Draft**, complete the reconstructed record, and run `sdlc.py propose
  PATH` to validate it before presenting it as **Proposed**. The
  decision may already be implemented, but the assistant must not self-accept
  the new evidence document.
- Record an estimated historical decision date in Context if known; leave
  human-owned approval/status dates blank until the human signs off.
- Do not second-guess decisions - document what was chosen and the likely rationale
- Flag decisions that look problematic with a note, but leave them Proposed for
  human review like every other reconstructed ADR
- Aim for 3-7 ADRs covering the most consequential decisions; don't over-document obvious defaults
- Present the retroactive ADRs as one review batch. The human accepts each ADR
  by editing its Current status and moving it to `decisions/accepted/`.

### Step 5a: Preserve Historical Changes, Fixes, and Remediations

For upgrades, follow `docs/framework/upgrading.md`: preserve existing approvals,
preview adapter and metadata changes, and adopt required metadata explicitly.
Do not manufacture retrospective scan evidence or human sign-off. Report missing
evidence honestly and prepare a new review of the current snapshot where needed.

Look for existing project history folders and documents, including but not limited to:

- `changes/`
- `fixes/`
- `incidents/`
- `remediations/`
- `patches/`
- `reviews/`
- release notes, changelogs, postmortems, hotfix logs, or audit logs

If historical fix/remediation records exist:

1. Create `sdlc_artifacts/fixes/` if needed.
2. Create `sdlc_artifacts/fixes/historical-fixes.md` as an index/ledger.
3. For each historical fix/remediation, record:
   - source file/path
   - fix identifier and date if available
   - title/summary
   - affected subsystem
   - status/approval if available
   - verification evidence if available
   - security, reliability, data integrity, or regression-risk notes
4. Do not rewrite history or mark incomplete fixes complete unless the source record says so.
5. Preserve the original files as authoritative detail and link back to them.
6. If V0 applies, mention this ledger in `sdlc_artifacts/context.md` and `sdlc_artifacts/STATE.md` so future agents use it as audit/evidence context.

### Step 6: Assess Gap Against SDLC Quality Gates

For each phase, check whether its quality gate would pass given what exists today:

| Phase | Quality Gate | Status |
|-------|-------------|--------|
| Requirements | User stories with acceptance criteria exist | [OK] / Partial / [X] |
| Design | Key ADRs documented and accepted | [OK] / Partial / [X] |
| Implementation | Code exists, change proposals and historical fixes/remediations are indexed where available | [OK] (code) / Partial / N/A (no prior proposals) |
| Testing | Tests exist, acceptance criteria covered | [OK] / Partial / [X] |
| Security Review | OWASP review completed, no must-fix items open | [OK] / [X] |
| Deployment | Runbook exists, CI/CD configured | [OK] / Partial / [X] |

**Note**: Missing change proposals for past work are expected and acceptable - the change-proposal gate applies to future work only.

### Step 7: Determine the Honest Current Phase

Use this decision table:

| Condition | Recommended Phase |
|-----------|------------------|
| Project is actively deployed and receiving changes | **Iterate** - treat next feature as a new iteration |
| Code is complete but no security review done | **Security Review** |
| Code is complete but tests are missing or thin | **Testing** |
| Code is in active development | **Implementation** |
| Code is very early / mostly scaffolding | **Design** |

When in doubt, choose the earlier phase - it is safer to review more than to skip a gate.

### Step 8: Initialise sdlc_artifacts/STATE.md

Run:

```bash
python sdlc/scripts/new_state.py
```

Then fill in sdlc_artifacts/STATE.md to reflect current reality:
- **Current Phase**: from the decision table above
- **Pending Approvals**: any decisions or work that needs human sign-off now
- **In Progress**: work actively underway
- **Blocked**: known blockers
- **Available**: work that can proceed immediately
- **Phase Completion Checklist**: copy from `docs/framework/sdlc-phases.md` for the current phase; tick what is already done
- **Last Session Summary / Left off at**: run `python sdlc/scripts/sdlc.py handoff`
  with a concise completed outcome and exact resume point; use `--next-action`
  to set the next permitted action

### Step 8a: Check for Missing Security Hygiene Files

Note in the onboarding report if any of these are absent from the project root:

| File | Purpose | Template |
|------|---------|----------|
| `SECURITY.md` | Vulnerability disclosure policy | `sdlc/templates/documents/security-policy.md` |
| `.github/workflows/` | CI/CD pipelines | `sdlc/workflows/06-deployment.md` for security controls |

Do not create these files automatically - flag them as recommended actions for the human to complete.

### Step 9: Provide Onboarding Report

```markdown
## Onboarding Report

### Project Summary
[2-3 sentence description of what the project does and its current state]

### Artifacts Created
- `sdlc_artifacts/context.md`
- `sdlc_artifacts/requirements/existing.md`
- `sdlc_artifacts/fixes/historical-fixes.md` (if historical fixes/remediations exist)
- `sdlc_artifacts/decisions/accepted/ADR-NNNN-*.md` (list each)
- `sdlc_artifacts/STATE.md`

### Current Phase: [Phase Name]

### Gap Analysis
| Phase | Gate Status | Notes |
|-------|------------|-------|
| Requirements | [OK] / Partial / [X] | [brief note] |
| Design | [OK] / Partial / [X] | [brief note] |
| Implementation | [OK] / N/A | |
| Testing | [OK] / Partial / [X] | [brief note] |
| Security Review | [OK] / [X] | [brief note] |
| Deployment | [OK] / Partial / [X] | [brief note] |

### Recommended Next Steps
1. [Most important immediate action]
2. [Following action]
3. [Following action]

### Questions for Project Owner
- [Anything that could not be inferred from the codebase]
```

### Step 10: Hand Off to Appropriate Agent

Once the report is delivered and the human confirms direction, invoke the agent for the current phase:

**Testing phase** -> `Read agents/tester.md and create a test plan for the existing implementation.`

**Security Review phase** -> `Read agents/security-reviewer.md and review the existing codebase against OWASP guidelines.`

**Iterate phase** -> `Read agents/orchestrator.md. We are starting a new iteration. Ask me what the next feature or change is.`

**Implementation phase** -> `Read agents/developer.md. Review the existing code and create a change proposal for the next planned feature.`

---

## Quick Start Command

Copy and paste this to your AI assistant:

```
Read sdlc/prompts/onboard.md and begin. Explore the existing codebase, reconstruct the framework artifacts, and give me an onboarding report with your recommended next step.
```

> **Note**: Run this from the **project root** (not inside the `sdlc/` folder), so the agent can read both the framework and the existing source code.
