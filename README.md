# Agentic SDLC Framework

**Structured software delivery for AI-assisted development.**

AI coding assistants are fast — but without guardrails they drift, skip review, and lose context between sessions. This framework gives you a repeatable process: specialised agent roles, written artifacts, human approval gates, and tool adapters so Cursor, Copilot, Claude Code, and Codex all follow the same rules.

Copy the `sdlc/` folder into any project. Run one setup script. Start with a prompt.

---

## What problem does this solve?

Most teams using AI assistants hit the same walls:

- **No memory** — each session starts cold; the model re-reads the codebase or guesses.
- **No change control** — code gets edited before anyone agrees on scope or approach.
- **No traceability** — requirements, decisions, tests, and reviews live in chat logs instead of the repo.
- **No security rhythm** — reviews happen late, or not at all.

The Agentic SDLC Framework addresses this with **artifacts in git**, **phase-based agent roles**, and **gates** that block implementation until a human approves the plan.

---

## How it works

```
Requirements  →  Design (ADRs)  →  Change proposal  →  Human approval
       →  Implementation  →  Testing  →  Security review  →  Deployment  →  Iterate
```

1. **You copy `sdlc/`** into your project — it holds agents, prompts, workflows, templates, and scripts. It is framework infrastructure, not product code.

2. **Setup installs adapters** — Cursor rules, Copilot instructions, Codex `AGENTS.md`, and Claude Code hooks land at your project root. Your existing config is never overwritten.

3. **Work produces `sdlc_artifacts/`** — requirements, ADRs, change proposals, reviews, and `STATE.md` (current phase and open items). Agents read these every session.

4. **Gates enforce discipline** — nothing ships to product code without an approved change proposal. Approval fields (`Status: Approved`, `Implemented`, etc.) are human-only. Claude Code hooks enforce this at the tool level; other assistants follow the same rules via instructions.

5. **You drive with prompts** — tell your assistant `Read sdlc/prompts/continue.md and resume` and it picks up where you left off.

---

## Quick start

**Requires [Python 3.10+](#python).** No pip packages needed for setup.

### 1. Install the framework

Copy the `sdlc/` folder into your project root, then run:

```bash
python sdlc/scripts/setup_project.py
python sdlc/scripts/verify_setup.py
```

Setup is safe to re-run. It skips files you already have — compare with `sdlc/adapters/` when upgrading the framework.

### 2. Start your first session

Open the project in your AI assistant and paste **one** of these:

| Situation | Prompt |
|-----------|--------|
| **New project** | `Read sdlc/prompts/bootstrap.md and begin` |
| **Existing codebase** | `Read sdlc/prompts/onboard.md and begin` |
| **Resume work** | `Read sdlc/prompts/continue.md and resume` |
| **Status only** | `Read sdlc/prompts/quick-status.md and report` |
| **Specific phase** | `Read sdlc/prompts/phase-specific/[phase].md and begin` |

The orchestrator agent reads `sdlc_artifacts/STATE.md`, assesses where you are, and delegates to the right role (Developer, Architect, Tester, etc.).

### 3. Approve before code changes

For any significant change:

```bash
python sdlc/scripts/new_change.py "short description of the change"
```

Fill in the proposal, then **you** open the file and set `Status: Approved`. The AI cannot approve its own work — that is enforced by design.

---

## Project layout

After setup, your project looks like this:

```
your-project/
├── sdlc/                    ← Framework (agents, prompts, scripts, templates)
├── sdlc_artifacts/          ← Your project's SDLC evidence (commit this)
│   ├── STATE.md             ← Current phase, open items, active change
│   ├── context.md           ← Stack, conventions, constraints
│   ├── requirements/
│   ├── decisions/           ← ADRs (proposed/ and accepted/)
│   ├── changes/             ← Change proposals
│   └── reviews/             ← Security and quality reviews
├── .cursor/rules/           ← Installed by setup (Cursor)
├── .github/                 ← Installed by setup (Copilot)
├── .claude/settings.json    ← Installed by setup (Claude Code hooks)
├── AGENTS.md                ← Installed by setup (Codex)
└── src/ …                   ← Your product code
```

**Rule of thumb:** `sdlc/` is read-only framework. Everything the project learns and decides goes in `sdlc_artifacts/`.

---

## Gates

Three gates keep AI-assisted work under control:

| Gate | When | What it checks |
|------|------|----------------|
| **Approval** | Before implementation | Change proposal reviewed; **you** set `Status: Approved` in the file |
| **Implementation** | Before every product-code edit | Approved change exists; blocking ADRs accepted; Active Change set when multiple approved |
| **Completion** | Before marking done | Tests pass; security review (REV) written; **you** set `Status: Implemented` |

**Human-only fields** — the model must never write approval statuses, sign-offs, or REV verdict checkboxes. In Claude Code, `approval_field_guard.py` blocks these at the tool level. In Cursor and Copilot, the rules instruct the model to stop and ask you to edit the file yourself.

**Enforcement by tool:**

| Check | Claude Code (hooks) | Cursor / Copilot / Codex (rules) |
|-------|---------------------|----------------------------------|
| Approved change exists | Hard block | Instruction |
| Active Change scoping | Hard block | Instruction |
| Blocking ADRs accepted | Hard block | Instruction |
| AI cannot self-approve | Hard block | Instruction |
| Acceptance criteria present | — | Instruction |
| Completion Gate before Implemented | — | Instruction |

Details: [Implementation workflow](workflows/03-implementation.md) · [Cursor gate rules](adapters/cursor/rules/README.md) · [Claude hooks](adapters/claude/README.md)

---

## AI assistant support

Setup installs the right adapter for each tool:

| Tool | Config location | Enforcement |
|------|-----------------|-------------|
| **Cursor** | `.cursor/rules/*.mdc` | Instruction rules (always-on) |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Instruction rules |
| **Codex** | `AGENTS.md` | Instruction rules |
| **Claude Code** | `.claude/settings.json` hooks | Hard enforcement via PreToolUse hooks |

Per-tool setup notes: [Assistant adapters](docs/framework/assistant-adapters.md) · [Assistant quickstart](docs/framework/assistant-quickstart.md)

---

## Python

Framework scripts (`setup_project.py`, `new_change.py`, hooks, scaffolding) need **Python 3.10+** and use only the standard library — no `pip install` for setup.

```bash
python --version    # expect 3.10 or higher
# Windows alternative:
py --version
```

<details>
<summary>Installing Python (click to expand)</summary>

**Windows** — Download from [python.org/downloads](https://www.python.org/downloads/) and check **“Add python.exe to PATH”**, or install from the Microsoft Store.

**macOS** — [python.org](https://www.python.org/downloads/) or `brew install python`. Use `python3` if `python` points to an older system version.

**Linux** — e.g. `sudo apt install python3 python3-venv` (Debian/Ubuntu) or `sudo dnf install python3` (Fedora).

Use `python3` instead of `python` wherever that is your system default.

</details>

Python project templates under `templates/projects/` have their own `requirements.txt` — use a venv for those. See [Getting started](docs/framework/getting-started.md).

---

## Scripts

Run from your **project root**:

```bash
python sdlc/scripts/setup_project.py              # install adapters + hooks
python sdlc/scripts/setup_project.py --dry-run    # preview changes
python sdlc/scripts/verify_setup.py               # verify installation
python sdlc/scripts/status.py                     # summarise project state

python sdlc/scripts/new_requirement.py "title"
python sdlc/scripts/new_change.py "description"
python sdlc/scripts/new_adr.py "decision title"
python sdlc/scripts/new_state.py
python sdlc/scripts/init_project.py python-fastapi-ai   # optional template
```

---

## SDLC phases

| Phase | Lead agent | Key outputs |
|-------|------------|-------------|
| Requirements | Requirements Analyst | User stories, acceptance criteria |
| Design | Architect | ADRs, `context.md` |
| Implementation | Developer | Code, change proposals |
| Testing | Tester | Tests linked to acceptance criteria |
| Security Review | Security Reviewer | REV documents, OWASP findings |
| Deployment | DevOps | CI/CD, runbooks |
| Iterate | Orchestrator | Retrospective, updated `STATE.md` |

Supporting roles: **Docs Writer**, **Web Designer/Engineer**. Full phase guide: [SDLC phases](docs/framework/sdlc-phases.md).

Large changes are split into **implementation phases** sized for one AI session (~2–3 files, ~200 lines). See [Change proposal template](templates/documents/change-proposal.md).

---

## Security

Four baselines apply by context:

| Baseline | When | Covers |
|----------|------|--------|
| **S0** | Always | Auth, input validation, secrets, logging |
| **A0** | AI/LLM features | Prompt safety, output controls, cost limits |
| **V0** | Compliance | Audit logs, tamper evidence |
| **C0** | Cloud deployment | IAM, KMS, network boundaries |

Reference: [Security baselines](docs/security/security-baselines.md)

---

## Learn more

| Topic | Document |
|-------|----------|
| Step-by-step first project | [Getting started](docs/framework/getting-started.md) |
| End-to-end traceability example | [Lifecycle example](docs/framework/lifecycle-example.md) |
| Agent roles and coordination | [Agent system](docs/framework/agent-system.md) |
| Document templates | [templates/documents/](templates/documents/) |
| Starter project templates | [templates/projects/](templates/projects/) |
| Filled-in examples | [examples/](examples/) |
| FAQ | [faq.md](docs/framework/faq.md) |
| External filesystem enforcement | [External enforcement agent](docs/framework/external-enforcement-agent.md) |

---

## Contributing

This repository is the framework source. To use it in a project, copy the `sdlc/` folder — you do not fork the framework into your product repo unless you are actively developing the framework itself.

When maintaining the framework repo directly (without a separate `sdlc/` subfolder), see [Installation modes](docs/framework/installation-modes.md) for path differences.
