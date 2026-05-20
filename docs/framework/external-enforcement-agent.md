# External Enforcement Agent — Interface Specification

> **Audience**: Developers building a runtime agent or filesystem watcher that enforces SDLC discipline at the OS level, independently of the AI coding tool being used.

---

## Why this exists

Claude Code hooks (`PreToolUse` on Write/Edit/Bash) enforce the implementation gate for the most common code-editing paths. One gap remains: a Bash command that invokes a Python or Node script which internally writes files cannot be intercepted by a hook, because the hook only sees the command string, not the runtime I/O.

An external agent running a filesystem watcher closes this gap. It operates independently of the AI tool — it watches the project directory at the OS level and reacts to any file write, regardless of what caused it.

---

## What the agent needs to do

1. **Watch** the project directory for file-write events (create, modify, rename-to).
2. **Classify** each written file as product code or framework/artifact (see below).
3. **Check** whether an approved change proposal exists for the current session.
4. **Enforce**: if a product code file was written without an approved change, revert it and alert.

---

## Artefact contract

All artefacts the agent reads are plain Markdown files. The framework guarantees their location and format across versions.

### Project root detection

The project root is the directory that contains **either**:
- `sdlc/` — the framework directory, **or**
- `sdlc_artifacts/` — the generated evidence directory

(Claude Code hooks accept either marker when walking up from the working directory. External agents may require both for stricter detection.)

The agent should walk up from its working directory to find the root, or accept it as a configuration parameter.

Environment override: `SDLC_PROJECT_ROOT` — if set, use this path directly.

---

### Approved change detection

**Location**: `<project_root>/sdlc_artifacts/changes/*.md`

**Format**: Each file is a Markdown change proposal. The agent must find at least one file whose `Status` field value is `Approved`.

**Status field pattern** (regex, case-insensitive, multiline):
```
^\s*[-*]?\s*[*_]*status[*_]*\s*[:\|]\s*Approved
```

This matches all variants the template can produce:
| Template line | Matches? |
|---|---|
| `- **Status**: Approved` | Yes |
| `**Status**: Approved` | Yes |
| `Status: Approved` | Yes |
| `Status \| Approved` | Yes |
| `- **Status**: Proposed` | No |
| `- **Status**: Proposed \| Approved \| Rejected` | No |

**Recommendation**: cache the approved-change result and invalidate it whenever any file in `sdlc_artifacts/changes/` is written, so the agent picks up approvals in real time without polling.

---

### Current phase

**Location**: `<project_root>/sdlc_artifacts/STATE.md`

**Format**: The file contains a `## Current Phase` section with a `**Phase**:` line:
```markdown
## Current Phase

**Phase**: Implementation
```

**Phases where the gate applies**: `Implementation`, `Testing`

**Phases where the gate should not fire**: `Requirements`, `Design`, `Security Review`, `Deployment`, `Iterate`

> **Note:** Claude Code hooks in this framework do **not** currently check phase — they block product-code writes whenever no approved change exists, regardless of phase. Phase gating is a recommended behaviour for external enforcement agents and instruction-based tools (Cursor, Copilot, Codex).

If `STATE.md` does not exist, the framework has not been bootstrapped — treat as gate inactive (Claude Code hooks fail-closed and block until `sdlc_artifacts/` exists).

---

### Blocked items

**Location**: `<project_root>/sdlc_artifacts/STATE.md` — `### Blocked` table

The agent may optionally check whether the specific file being written belongs to a blocked work item. In practice this correlation is hard to automate; it is sufficient to check that at least one approved change exists (above).

---

## Product code classification

A file is **product code** (gate applies) if its path relative to the project root does **not** start with any of these prefixes:

```
sdlc/
sdlc_artifacts/
.claude/
.cursor/
.github/
.git/
```

Apply the same logic on Windows by normalising separators to `/` before checking, or check both `/` and `os.sep` variants.

Files that are always product code (examples):
- `azure_documenter/main.py`
- `src/index.ts`
- `app/models/user.py`
- `requirements.txt`, `package.json`, `pyproject.toml` (dependency manifests count)

Files that are never product code (examples):
- `sdlc_artifacts/STATE.md`
- `sdlc/agents/developer.md`
- `.claude/settings.json`
- `.github/copilot-instructions.md`

---

## Enforcement actions

When a product code write is detected without an approved change, the agent should:

1. **Revert** the file immediately:
   ```bash
   git checkout HEAD -- <file>
   ```
   If the file is new (untracked), delete it:
   ```bash
   git clean -f <file>
   ```
   If the project is not a git repo, the agent cannot revert — log and alert only.

2. **Log** the event with: timestamp, file path, command or process that wrote it (if determinable from OS APIs), and the absence of an approved change.

3. **Alert** via the agent's configured channel (webhook, desktop notification, etc.). Suggested payload:

```json
{
  "event": "gate_violation",
  "file": "azure_documenter/main.py",
  "project_root": "/path/to/project",
  "approved_changes": [],
  "current_phase": "Implementation",
  "timestamp": "2026-05-06T14:32:00Z"
}
```

---

## Exclusion rules

The agent must not fire on:

- Writes to any excluded prefix path (see above).
- Writes caused by `git` itself (e.g. `git checkout`, `git merge`) — these are framework-managed operations, not AI-initiated edits.
- Writes to temp files (paths containing `.tmp`, `.swp`, `~`).
- Writes to compiled output directories (`__pycache__/`, `node_modules/`, `dist/`, `build/`, `.venv/`).

Suggested compiled/cache exclusion prefixes (add to the excluded list):
```
__pycache__/
.venv/
node_modules/
dist/
build/
*.egg-info/
.mypy_cache/
.pytest_cache/
```

---

## Filesystem watcher recommendations

| Platform | Recommended API |
|----------|----------------|
| Linux | `inotify` via `watchdog` (Python) or `inotifywait` |
| macOS | `FSEvents` via `watchdog` (Python) |
| Windows | `ReadDirectoryChangesW` via `watchdog` (Python) |
| Cross-platform Python | [`watchdog`](https://pypi.org/project/watchdog/) — single API for all three |
| Cross-platform Node | [`chokidar`](https://github.com/paulmillr/chokidar) |

Watch for events: `created`, `modified`, `moved` (destination path). Ignore `deleted`.

---

## Co-existence with Claude Code hooks

The hooks (`implementation_gate.py`, `bash_gate.py`) and the external agent cover overlapping but not identical surface areas:

| Scenario | Hook catches | Agent catches |
|----------|-------------|---------------|
| Claude writes via Write/Edit tool | Yes | Yes (redundant, harmless) |
| Claude runs `sed -i` via Bash | Yes | Yes (redundant, harmless) |
| Claude runs `python build_script.py` that writes files | No | Yes |
| Human edits file directly in editor | No | Yes |
| Another process writes files | No | Yes |

When both are active, a write blocked by the hook never reaches the agent. The agent is the backstop, not the primary gate.

To avoid double-alerting on files the hook already blocked (which never get written): this is not an issue in practice because the hook exits 2 before the write occurs, so no filesystem event is generated.

---

## Versioning

This specification is versioned by the framework. Breaking changes to artefact paths or formats will be accompanied by a framework ADR. The agent should treat missing artefacts gracefully (gate inactive) rather than failing hard.

**Current spec version**: 1.0  
**Compatible framework versions**: any version containing `sdlc/docs/framework/external-enforcement-agent.md`

---

*Maintained by the framework team. File issues or questions in the project that owns this `sdlc/` copy.*
