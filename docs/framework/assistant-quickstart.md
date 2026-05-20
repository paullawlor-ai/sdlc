# Assistant Quickstart

Use this page after choosing an installation mode. The goal is to make the
assistant load the right always-on guidance, then enter the right SDLC prompt.

## Codex

If the framework is the repository root, Codex reads `AGENTS.md` automatically.

If the framework is embedded as `sdlc/` and `sdlc/` is committed, Codex can read
the root `AGENTS.md` copied from:

```text
sdlc/adapters/codex/AGENTS.md
```

If `sdlc/` is gitignored, copy or adapt that file into the host project root:

```text
AGENTS.md
```

Validation prompt:

```text
Summarize the AGENTS.md instructions you loaded and list the SDLC entry point you would use to resume work.
```

## Cursor

Source templates:

```text
sdlc/adapters/cursor/rules/
```

Install into the host project (creates `.cursor/rules/` if needed):

```bash
python sdlc/scripts/setup_project.py
python sdlc/scripts/verify_setup.py
```

`verify_setup.py` checks Cursor rules, Copilot files, Claude hooks, and `sdlc_artifacts/STATE.md`. Run it after every setup.

See `adapters/cursor/rules/README.md` for Implementation Gate and Completion Gate behaviour.

First prompt for an existing project:

```text
Read sdlc/prompts/onboard.md and begin
```

First prompt for a new root-template project:

```text
Read prompts/bootstrap.md and begin
```

## Claude Code

Claude Code uses **hooks only** — no framework instruction file. Install from the project root:

```bash
python sdlc/scripts/setup_project.py
```

This merges four hooks into `.claude/settings.json`:
- **implementation_gate** — blocks Write/Edit/MultiEdit to product code without an approved change; enforces Active Change when multiple approved; checks blocking ADRs
- **approval_field_guard** — blocks the model from writing human-only approval fields (`Approved`, `Implemented`, etc.) in artifacts
- **bash_gate** — blocks `sed -i`, output redirects, `tee`, `patch` to product code files
- **session_end_reminder** — reminds Claude to update `STATE.md` at session end

Hooks do **not** enforce STATE.md pending/blocked, acceptance criteria, test expectations, or Completion Gate — those are instruction-only. Humans must set `Status: Approved` in the editor; the model cannot self-approve.

Hooks only:

```bash
python sdlc/scripts/install_hooks.py
```

Safe to re-run. Merges into an existing `settings.json` without clobbering other settings.

### Validation prompt

```text
Summarize how this repository distinguishes framework maintenance from product work, and confirm which hooks are active.
```

## GitHub Copilot

Use:

```text
sdlc/adapters/copilot/copilot-instructions.md
sdlc/adapters/copilot/instructions/sdlc.instructions.md
```

For a host project, copy them to:

```text
.github/copilot-instructions.md
.github/instructions/sdlc.instructions.md
```

Validation prompt:

```text
Using repository instructions, summarize how significant changes should flow through the SDLC framework.
```

## First Prompt Selector

| Situation | Root-template prompt | Embedded-framework prompt |
|-----------|----------------------|---------------------------|
| New project | `Read prompts/bootstrap.md and begin` | `Read sdlc/prompts/bootstrap.md and begin` |
| Existing project adoption | N/A unless repo root is already the product | `Read sdlc/prompts/onboard.md and begin` |
| Resume work | `Read prompts/continue.md and resume` | `Read sdlc/prompts/continue.md and resume` |
| Quick status only | `Read prompts/quick-status.md and report` | `Read sdlc/prompts/quick-status.md and report` |
| Documentation | `Read prompts/phase-specific/docs.md and begin` | `Read sdlc/prompts/phase-specific/docs.md and begin` |
| Browser UI | `Read prompts/phase-specific/web-design.md and begin` | `Read sdlc/prompts/phase-specific/web-design.md and begin` |

## Good First Check

Ask the assistant:

```text
Before changing files, tell me which installation mode this project appears to use and which SDLC entry point you will follow.
```
