# Assistant Adapters

The Agentic SDLC Framework is intended to work across AI coding assistants. Each assistant has different automatic instruction-file conventions, so the framework provides small adapter files that point the assistant back to the canonical framework prompts, agents, workflows, and templates.

For first-run prompts and validation checks, see
`docs/framework/assistant-quickstart.md`. For path differences between root and
embedded installs, see `docs/framework/installation-modes.md`.

## Adapter Strategy

Keep platform adapters thin:

- Always-on behavior belongs in assistant steering files.
- Detailed phase behavior belongs in `prompts/`, `agents/`, and `workflows/`.
- Document templates stay in `templates/`.
- Security and SDLC references stay in `docs/security/` and `catalogs/`.

This keeps the framework portable and avoids maintaining different versions of the same process for every assistant.

## Codex

Codex reads `AGENTS.md` and `AGENTS.override.md` files when it starts a session. It can also read global instructions from the Codex home directory.

Use:

```text
sdlc/adapters/codex/AGENTS.md
```

For a host project where `sdlc/` is gitignored, copy that file to:

```text
AGENTS.md
```

If a subproject needs stricter or different guidance, add a nested `AGENTS.md` or `AGENTS.override.md` near that subproject.

The framework root also includes `AGENTS.md` at the repo root (root-template) or `sdlc/AGENTS.md` (framework-maintenance context when opening the `sdlc/` folder directly). Host projects receive `AGENTS.md` from `adapters/codex/AGENTS.md` via the setup script.

## GitHub Copilot

GitHub Copilot supports repository-wide instructions and path-specific instructions.

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

Copilot agent mode can also use `AGENTS.md`, so the Codex adapter can be copied to the host project root when you want shared agent guidance.

## Cursor

Cursor rules are source templates in:

```text
sdlc/adapters/cursor/rules/
```

Install them into the host project with:

```bash
python sdlc/scripts/setup_project.py
```

Cursor loads rules from `.cursor/rules/` at the project root — not from inside `sdlc/`. See `adapters/cursor/rules/README.md` for the Implementation Gate and Completion Gate details.

## Claude Code

Claude Code is configured through **PreToolUse and Stop hooks** in `.claude/settings.json`. There is no separate framework instruction file — enforcement and session-end reminders come from the hooks. See `adapters/claude/README.md`.

The framework ships four hooks that enforce SDLC discipline automatically:

| Hook file | Event | Effect |
|-----------|-------|--------|
| `sdlc/scripts/hooks/implementation_gate.py` | PreToolUse Write/Edit/MultiEdit | Blocks product code edits without an approved change proposal |
| `sdlc/scripts/hooks/approval_field_guard.py` | PreToolUse Write/Edit/MultiEdit | Blocks the model from writing human-only approval fields |
| `sdlc/scripts/hooks/bash_gate.py` | PreToolUse Bash | Blocks `sed -i`, redirects, `tee`, `patch` to product code files |
| `sdlc/scripts/hooks/session_end_reminder.py` | Stop | Reminds Claude to update STATE.md |

Install via:

```bash
python sdlc/scripts/setup_project.py
```

Or hooks only:

```bash
python sdlc/scripts/install_hooks.py
```

See `adapters/claude/README.md` — do not copy `settings.json` verbatim (hook paths are layout-specific).

For host projects that commit adapter files, also commit `.claude/settings.json` so teammates get the hooks automatically.

## Enforcement scope

| Check | Claude Code hooks | Cursor / Copilot / Codex instructions |
|-------|-------------------|----------------------------------------|
| Approved change exists | Yes | Yes |
| Active Change when multiple approved | Yes | Yes |
| Blocking ADRs accepted | Yes | Yes |
| Human-only approval fields | Yes (`approval_field_guard`) | Yes (instruction + model discipline) |
| STATE.md pending/blocked | No | Yes (instruction only) |
| Acceptance criteria / test expectations | No | Yes (instruction only) |
| Completion Gate before Implemented | No | Yes (instruction only) |
| SDLC phase gating | No | Partial (instruction only) |

See `workflows/03-implementation.md` for the full Implementation Gate checklist.

## Recommended Host Project Layout

When adopting a project while keeping `sdlc/` ignored, commit only the host project artifacts and assistant adapters you actually want the team to share:

```text
AGENTS.md
.github/copilot-instructions.md
.github/instructions/sdlc.instructions.md
.claude/settings.json
sdlc_artifacts/STATE.md
sdlc_artifacts/context.md
sdlc_artifacts/requirements/
sdlc_artifacts/decisions/
sdlc_artifacts/changes/
sdlc_artifacts/reviews/
```

The ignored `sdlc/` folder remains the local framework source.

## Versioning Guidance

In most projects, commit `sdlc_artifacts/`.

Git and GitHub already provide the version history: each committed change to `sdlc_artifacts/requirements/`, `sdlc_artifacts/decisions/`, `sdlc_artifacts/changes/`, `sdlc_artifacts/reviews/`, and `sdlc_artifacts/STATE.md` is tracked in normal commit history and pull requests.

Keep explicit status fields inside artifacts anyway. Git tells you what changed and when; artifact statuses tell agents and humans what the change means in the SDLC process.

Recommended default `.gitignore`:

```gitignore
# Framework runtime
/sdlc/

# Optional local-only notes or generated scratch output
/sdlc_artifacts/tmp/
/sdlc_artifacts/private/
```

For experiments or solo scratch work, a project may ignore all of `sdlc_artifacts/`, but that should be an explicit local-mode choice because it loses the shared audit trail.

## Validation Prompts

After installing an adapter, ask the assistant to summarize its active instructions.

For Codex:

```text
Summarize the AGENTS.md instructions you loaded and list the SDLC entry point you would use to resume work.
```

For GitHub Copilot:

```text
Using repository instructions, summarize how significant changes should flow through the SDLC framework.
```
