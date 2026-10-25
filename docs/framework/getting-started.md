# Getting Started with the Agentic SDLC Framework

This guide walks you through using the framework to build your first project.
For the framework-repo layout (without a separate `sdlc/` subfolder), see
`sdlc/docs/framework/installation-modes.md`.

## Onboarding an Existing Project

If you have an existing codebase that hasn't used this framework before, use the onboarding prompt instead of the steps below:

```
Read sdlc/prompts/onboard.md and begin.
```

The agent will explore the codebase, reconstruct requirements and ADRs from what already exists, and position `sdlc_artifacts/STATE.md` at the correct phase so you can continue with `sdlc/prompts/continue.md` from that point on. See `sdlc/prompts/onboard.md` for details.

---

## Prerequisites

- **Python 3.10+** — required for all framework scripts (`setup_project.py`, scaffolding, hooks). Standard library only; no pip packages needed for setup. See [Prerequisites](../../README.md#python) in the main README for install links (Windows, macOS, Linux) and version checks.
- An AI coding assistant (Cursor, GitHub Copilot, Claude Code, Codex, etc.)
- Basic understanding of your target technology stack
- A project idea or requirements document

## Step 1: Set Up Your Project

> **Before you begin:** install **Python 3.10+** and confirm with `python --version`. See [Prerequisites](../../README.md#python) in the main README.

Copy the **`sdlc/`** folder into your project root, then run setup from the project root.

### Existing project (recommended workflow)

1. Download the framework release from GitHub and extract the zip
2. Copy the `sdlc/` folder into your existing project root
3. Run:
   ```bash
   python sdlc/scripts/setup_project.py
   python sdlc/scripts/verify_setup.py
   ```
   This installs Cursor rules, Copilot instructions, Codex `AGENTS.md`, and Claude Code hooks without overwriting anything you already have. It also creates `sdlc_artifacts/STATE.md` when missing. Use `--dry-run` to preview changes without writing files.

   To install only the tools in use, pass `--assistant` one or more times. Setup
   also creates `sdlc_artifacts/config.json`, where `standard` can be changed to
   the `lite` or `regulated` policy profile.
4. Open the project and run:
   ```
   Read sdlc/prompts/onboard.md and begin
   ```

### New project

1. Create your project folder and copy the **`sdlc/`** folder into it (from the framework release zip or GitHub)
2. Run:
   ```bash
   python sdlc/scripts/setup_project.py
   python sdlc/scripts/verify_setup.py
   ```
3. (Optional) If using a Python project template:
   ```bash
   python sdlc/scripts/init_project.py python-fastapi-ai
   ```
   Then create a venv and `pip install -r requirements.txt` as described in the template README.
4. Open the project and run:
   ```
   Read sdlc/prompts/bootstrap.md and begin
   ```

## Step 2: Add Your Requirements

Create your initial requirements in `sdlc_artifacts/requirements/`:

```markdown
# My Application Requirements

## Overview
A brief description of what you're building.

## User Stories
- As a [user type], I want [feature] so that [benefit]

## Constraints
- Technology preferences
- Performance requirements
- Security requirements
```

## Step 3: Bootstrap the Project

Open the project in your AI coding assistant and give this prompt:

```
Read sdlc/prompts/bootstrap.md and begin
```

The orchestrator agent will:
1. Read your requirements
2. Analyze the project scope
3. Create a phased implementation plan
4. Begin the requirements analysis phase

## Step 4: Follow the SDLC Phases

The orchestrator guides you through each phase:

### Phase 1: Requirements
- Clarifies ambiguous requirements
- Creates detailed user stories
- Defines acceptance criteria

### Phase 2: Design
- Proposes system architecture
- Creates ADRs for key decisions
- Defines API contracts

### Phase 3: Implementation
- Creates change proposals before coding
- Lists blocking ADRs and dependencies
- Runs the Implementation Gate before product-code edits
- Implements in small, reviewable increments
- Writes unit tests alongside code

### Phase 4: Testing
- Creates test plans
- Runs integration tests
- Reports coverage

### Phase 5: Security Review
- Reviews against OWASP guidelines
- Maps risks to controls
- Suggests mitigations

### Phase 6: Deployment
- Creates CI/CD configuration
- Writes deployment runbooks
- Documents rollback procedures

## Step 5: Approve at Gates

The framework pauses at key decision points:
- **Change Proposals**: Review and approve before implementation
- **ADRs**: Accept architectural decisions
- **Implementation Gate**: Confirm the change is approved, blocking ADRs are accepted, and (for instruction-based tools) STATE.md is clear, acceptance criteria and test expectations are present
- **Completion Gate**: After tests pass, security review (REV) must pass before Status becomes `Implemented`
- **Security Findings**: Address must-fix items

Change proposals and ADRs are created as Drafts so an assistant can safely fill
them in without implying they are ready for review. Once the Draft is complete,
promote it from the project root:

```bash
python sdlc/scripts/sdlc.py propose sdlc_artifacts/changes/0001-example.md
python sdlc/scripts/sdlc.py propose sdlc_artifacts/decisions/proposed/ADR-0001-example.md
```

The command checks required sections and substantive fields, then atomically
changes `Draft` to `Proposed`. If validation fails, the file remains Draft and
the reported diagnostic codes identify the missing content. Drafts are not
shown as pending human approvals and cannot satisfy implementation gates.

Before the human changes an approved change to `Implemented`, run
`python sdlc/scripts/sdlc.py check --ready-to-finalize`. Standard work requires
the agent recommendation and clean review evidence. Regulated and high-risk
work additionally requires one approving human verdict, reviewer name, and ISO
date in the REV document. The command reports missing actions but never edits
human-owned fields.

### Structured Metadata

For a 0.2.0 project, follow the complete sequence in
[upgrading.md](upgrading.md) before strict validation. Release contributors should
also use the [release checklist](releasing.md).

New projects use required structured metadata from setup. Existing projects stay
in compatibility mode after replacing or upgrading the framework. Preview and
adopt required mode explicitly:

```bash
python sdlc/scripts/sdlc.py metadata sync
python sdlc/scripts/sdlc.py metadata sync --apply
python sdlc/scripts/sdlc.py check
```

Apply writes derived sidecars and `index.json`, changes only `metadata_mode` in
project configuration, and creates a rollback snapshot. It does not rewrite
Markdown or approval fields. Run
`python sdlc/scripts/sdlc.py migrate --rollback` to restore the previous
metadata, index, and configuration snapshot.

**Human-only approval fields.** You must edit approval status yourself in your editor — the AI cannot set `Status: Approved`, `Status: Implemented`, `Current status: Accepted`, or sign-off fields, even if you tell it to verbally. Claude Code blocks these writes via `approval_field_guard.py`; other tools rely on instruction rules.

Before completion, follow [quality and security evidence](quality-and-security.md).
Required reviews link successful scan JSON and its reviewed source digest;
regulated/high-risk human sign-off also records the approved source digest.
After human edits, synchronize metadata, then run `sdlc.py check
--ready-to-finalize` and `sdlc.py gate completion` before marking Implemented.

When **more than one** change proposal is Approved, set exactly one in `sdlc_artifacts/STATE.md` under `## Active Change` → **Change document** before implementing.

Update the status in the relevant document (you edit, not the AI):
```markdown
## Approval
- Status: Approved
- Approved by: You
- Date: 2024-01-15
```

Then save the file and tell the agent to continue. If the file still shows `Proposed`, the gate will block until you save the change.

## Step 6: Iterate

To continue work on an existing project:

```
Read sdlc/prompts/continue.md and resume
```

The orchestrator will:
1. Review current project state
2. Check for pending items
3. Continue from where you left off

## Tips for Success

1. **Start with clear requirements**: The better your initial requirements, the better the output
2. **Review change proposals carefully**: This is your first quality gate
3. **Check the Implementation Gate result**: Claude Code hooks enforce approved change, Active Change scoping, and blocking ADRs. Instruction-based tools (Cursor, Copilot, Codex) also expect STATE.md to be clear and AC/test expectations to be present — verify these during review even though hooks do not check them automatically.
4. **Don't skip security reviews**: They catch issues early
5. **Use the decision templates**: ADRs help you make better choices
6. **Keep the backlog updated**: Track what's done and what's next

## Troubleshooting

### Check the local execution environment

Run `python sdlc/scripts/sdlc.py doctor` from the project root. It reports the
interpreter and virtual environment actually in use, write access, the operating
system temporary directory, and Git evidence readiness. Use the printed quoted
Python command when an assistant resolves a different interpreter than your
shell.

Let pytest create its normal unique temporary directories through `tmp_path` or
`tmp_path_factory`. Do not configure a fixed project-local `--basetemp` for
interactive or concurrent assistant runs. When a custom base is unavoidable,
generate a unique path per run and clean it up after the run. Environment or
temporary-directory failures should be reported separately from product test
failures.

### Agent seems confused about project state
Run: `Read sdlc/prompts/continue.md and give me a status report`

### Too many changes at once
Ask: `Break this into smaller increments, one change proposal per feature`

### Security findings overwhelming
Ask: `Prioritize the must-fix security findings for the current increment`

## Next Steps

- Read [Agent System](agent-system.md) to understand how agents coordinate
- Read [SDLC Phases](sdlc-phases.md) for detailed phase information
- Read [Installation Modes](installation-modes.md) if path conventions are unclear
- Read [Assistant Quickstart](assistant-quickstart.md) for Codex, Cursor, Claude Code, and Copilot setup
- Read [Lifecycle Example](lifecycle-example.md) for a small traceability walkthrough
- Read [FAQ](faq.md) for common questions (ADR vs change proposal, skipping phases, etc.)
- Explore [templates/projects/](../../templates/projects/) for starter templates (paths under `sdlc/templates/projects/` in a host project)
- See [examples/](../../examples/) for filled-in reference documents (paths under `sdlc/examples/` in a host project)
