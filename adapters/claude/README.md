# Claude Code adapter

Claude Code is configured through **hooks in `.claude/settings.json` only**. The framework does not ship a `CLAUDE.md` instruction file.

Do **not** copy `settings.json` from this directory manually.

Run from the project root:

```bash
python sdlc/scripts/setup_project.py
```

That merges four SDLC hooks with correct paths for your install layout:

| Hook | Purpose |
|------|---------|
| `implementation_gate.py` | Blocks product code edits without an approved change; Active Change when multiple approved; blocking ADRs accepted |
| `approval_field_guard.py` | Blocks the model from writing human-only approval fields (`Approved`, `Implemented`, etc.) |
| `bash_gate.py` | Applies the gate to common Bash write patterns (best-effort defence in depth) |
| `session_end_reminder.py` | Reminds Claude to update STATE.md at session end |

**Human approval is required.** The model cannot set `Status: Approved` or `Status: Implemented` — a human must open the change file in an editor, edit the status, and save. Hooks block the model from writing those fields even if the user says "approved" verbally.

**Not hook-enforced** (instruction-only): STATE.md pending/blocked, acceptance criteria, test expectations, Completion Gate, SDLC phase. See `workflows/03-implementation.md`.

Hooks only (no Cursor/Copilot adapters):

```bash
python sdlc/scripts/install_hooks.py
```

The `settings.json` file in this directory is a **reference snapshot** only. `setup_project.py` generates hook commands dynamically (embedded `sdlc/scripts/...` vs root-template `scripts/...`).
