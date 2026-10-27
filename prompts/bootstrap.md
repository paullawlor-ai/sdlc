# Bootstrap Prompt

Use this prompt to start a new project with the Agentic SDLC Framework.

---

## Instructions for AI Agent

You are working with the **Agentic SDLC Framework**. This framework coordinates specialized agents to build software through structured SDLC phases.

### Step 0: Confirm Project Setup

Before doing any framework work, confirm adapters are installed at the **host project root** (not inside `sdlc/`):

```bash
python scripts/verify_setup.py
# or, in embedded mode:
python sdlc/scripts/verify_setup.py
```

If verification fails, the human must run once from the project root:

```bash
python scripts/setup_project.py
# or, in embedded mode:
python sdlc/scripts/setup_project.py
```

Do not proceed with implementation until setup passes or the human confirms they have run it.

### Step 1: Read Framework Context and Initialise Project Files

Setup initializes required metadata for new projects. Keep it synchronized after
human edits with `python sdlc/scripts/sdlc.py metadata sync --apply`. New changes
and ADRs start as Draft: complete them and run `sdlc.py propose PATH` before
requesting human approval. Load the relevant role/workflow as needed; do not load
every role or security catalogue into ordinary session context.

Start with existing `sdlc_artifacts/STATE.md` and `context.md`, or use
`python sdlc/scripts/sdlc.py context --budget 2000`. Read `agents/orchestrator.md`
when coordinating phases. Consult `README.md`, `docs/framework/getting-started.md`,
and relevant security baselines only as needed to resolve the current task.
Prefix framework paths with `sdlc/` in embedded projects; omit that prefix when
the framework itself is the project root.

Then initialise project-specific files if they don't already exist. Use
`python scripts/...` when this framework is the project root, or
`python sdlc/scripts/...` when it is embedded in a host project.

```bash
# Initialise sdlc_artifacts/STATE.md (project phase tracker)
python scripts/new_state.py
# or, in embedded mode:
python sdlc/scripts/new_state.py
```

If `sdlc_artifacts/context.md` does not exist, create it from
`templates/documents/project-context.md`. Fill in anything you can infer from
the requirements, repository files, or user prompt. Mark unknown fields as
`[UNKNOWN - ask owner]`, then ask only the smallest set of questions needed to
avoid blocking the next phase. This file is essential - all agents read it.

### Step 2: Read Project Requirements

Check for existing requirements:
- `sdlc_artifacts/requirements/` - Look for requirement documents
- Any design documents in `sdlc_artifacts/design/`
- Any accepted ADRs in `sdlc_artifacts/decisions/accepted/`

### Step 3: Assess Project State

Determine the current state:
1. Are there documented requirements? (If not, start with requirements gathering)
2. Are there accepted ADRs? (If not, design phase needed after requirements)
3. Are there approved change proposals? (If yes, implementation may be in progress)
4. Are there pending approvals? (If yes, wait for approval)

### Step 4: Provide Status Report

Report your findings:

```markdown
## Project Bootstrap Report

### Project State
- Requirements: [Found/Not found]
- Design (ADRs): [Found/Not found]
- Changes: [Count pending/approved/implemented]
- Reviews: [Count if any]

### Current Phase
[Requirements/Design/Implementation/Testing/Security Review/Deployment/New Project]

### Recommended Next Steps
1. [First action]
2. [Second action]

### Questions (if any)
- [Question about unclear requirements]
```

### Step 5: Begin Appropriate Phase

Based on state assessment:

**If new project (no requirements):**
- Ask for project description
- Begin requirements gathering
- Invoke Requirements Analyst agent

**If requirements exist but no design:**
- Review requirements
- Begin design phase
- Invoke Architect agent

**If design exists but no implementation:**
- Review approved ADRs
- Create first change proposal
- Invoke Developer agent

**If implementation in progress:**
- Check for pending approvals
- Continue with current phase
- Invoke appropriate agent

### Step 6: Follow SDLC Workflow

Reference the appropriate workflow (prefix with `sdlc/` when embedded):
- `workflows/01-requirements.md` or `sdlc/workflows/01-requirements.md`
- `workflows/02-design.md` or `sdlc/workflows/02-design.md`
- `workflows/03-implementation.md` or `sdlc/workflows/03-implementation.md`
- `workflows/04-testing.md` or `sdlc/workflows/04-testing.md`
- `workflows/05-security-review.md` or `sdlc/workflows/05-security-review.md`
- `workflows/06-deployment.md` or `sdlc/workflows/06-deployment.md`
- `workflows/07-iterate.md` or `sdlc/workflows/07-iterate.md`

### Key Rules

1. **Document significant work before coding**: Create change proposals before implementation for significant changes
2. **Wait for human approvals**: Pause at approval gates; humans edit Status fields in the editor — the model must not self-approve
3. **Run the Implementation Gate before product-code edits**: approved change (human-set), blocking ADRs accepted, Active Change set when multiple approved; also verify STATE.md, AC, and test expectations per workflow docs
4. **Follow security baselines**: Apply S0 always, A0 for AI features
5. **Work incrementally**: Small, reviewable changes
6. **Maintain traceability**: Link requirements -> design -> code -> tests
7. **Active Change**: When more than one change is Approved, set exactly one in `sdlc_artifacts/STATE.md` before implementing
8. **Completion Gate**: After tests pass, apply the active class/profile policy;
   when a REV is required, pass it before the human sets Status: Implemented

---

## Quick Start Command

Copy and paste this to your AI assistant:

```
Read prompts/bootstrap.md and begin. Assess the current project state and guide me through the next steps.
```
