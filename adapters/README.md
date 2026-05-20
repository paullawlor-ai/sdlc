# Assistant Adapters

This directory contains steering-file templates for AI coding assistants.

The framework lives in an `sdlc/` folder inside your project. Adapter files must be installed at the **project root** so each assistant can find them.

## Recommended: use the setup script

From your project root (after copying `sdlc/` into the project):

```bash
python sdlc/scripts/setup_project.py
```

The script installs adapters **additively** — it never overwrites existing Cursor rules, Copilot instructions, or `AGENTS.md` at the project root. Claude Code hooks are merged into `.claude/settings.json`.

## Codex

Source:

```text
sdlc/adapters/codex/AGENTS.md -> AGENTS.md (project root)
```

Optional nested service overrides can use `AGENTS.md` or `AGENTS.override.md` in subdirectories.

## GitHub Copilot

Source files (there is no `.github/` folder inside adapters — setup creates it at the project root):

```text
sdlc/adapters/copilot/copilot-instructions.md -> .github/copilot-instructions.md
sdlc/adapters/copilot/instructions/sdlc.instructions.md -> .github/instructions/sdlc.instructions.md
```

Copilot also understands `AGENTS.md` for agent instructions, so the Codex adapter can be useful for Copilot agent mode too.

## Cursor

Source:

```text
sdlc/adapters/cursor/rules/*.mdc -> .cursor/rules/
```

See `cursor/rules/README.md` for details on `implementation-gate.mdc` and the other rules.

## Claude Code

Hooks only — no separate instruction file. Setup merges hooks into `.claude/settings.json`:

```bash
python sdlc/scripts/install_hooks.py
```

Or use the full setup script above.

Four hooks are installed:

- **`implementation_gate.py`** — `PreToolUse` on Write/Edit/MultiEdit. Blocks product code edits until an approved change proposal exists.
- **`approval_field_guard.py`** — `PreToolUse` on Write/Edit/MultiEdit. Blocks the model from setting human-only approval fields in `sdlc_artifacts/`.
- **`bash_gate.py`** — `PreToolUse` on Bash. Blocks common Bash write patterns to product code without an approved change.
- **`session_end_reminder.py`** — `Stop`. Reminds Claude to update `STATE.md`.

See `claude/README.md`. The `settings.json` file in `claude/` is a reference snapshot only — `setup_project.py` generates hook commands with the correct paths for your install layout.

Keep assistant-specific files small. Put durable framework behavior in `agents/`, `prompts/`, and `workflows/`, then have adapters point assistants to those files.

**Instruction vs hook enforcement:**
- **Claude Code hooks** hard-enforce: approved change proposal, Active Change when multiple approved, blocking ADRs accepted, and human-only approval fields.
- **Cursor, Copilot, Codex** instruction files describe the full gate checklist (STATE.md, AC, test expectations, Completion Gate) — the model must follow them; there is no tool-level block.
