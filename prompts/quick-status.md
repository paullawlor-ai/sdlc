# Quick Status Prompt

Use this prompt for a fast project status check. No work is started and no agents are invoked - report only.

---

## Instructions for AI Agent

Read the project state and report concisely. **Do not start any work. Do not invoke any agents. Do not create or modify any documents.**

### Step 1: Find and Read sdlc_artifacts/STATE.md

sdlc_artifacts/STATE.md is typically at the project root (one level above `sdlc/` if the framework is in a subfolder, or at the repo root if the framework is the root).

If sdlc_artifacts/STATE.md does not exist, do a minimal fallback scan:
- Count files in `sdlc_artifacts/changes/` by status (grep for `**Status**:`)
- Count ADRs in `sdlc_artifacts/decisions/proposed/` and `accepted/`
- Note that sdlc_artifacts/STATE.md is missing

### Step 2: Report

Produce a status report in this exact format - no more, no less:

```markdown
## Status Report - [today's date]

**Phase**: [current phase, or "Unknown - sdlc_artifacts/STATE.md missing"]

**Pending Approvals** ([count]):
- [Document name] - [Change / ADR] - [path]
(or "None")

**In Progress** ([count]):
- [Item] - [owner agent]
(or "None")

**Blocked** ([count]):
- [Item] - blocked by [reason]
(or "None")

**Left off at**: [exact quote from sdlc_artifacts/STATE.md "Left off at" field, or "sdlc_artifacts/STATE.md missing"]

**Recommended next action**: [one sentence - what should happen first in the next session]
```

If sdlc_artifacts/STATE.md is missing or its last session date is more than a week ago, append:

```
[WARN]  sdlc_artifacts/STATE.md [missing / possibly stale - last updated YYYY-MM-DD].
   Run `python scripts/status.py` in root-template mode, or
   `python sdlc/scripts/status.py` in embedded mode, for a plain-text summary.
   Start a full session with `continue.md` to re-orient and update it.
```

### Rules

- Do not begin implementation of any pending item
- Do not create or modify any documents
- Do not invoke specialist agents
- If you are uncertain about a field, write "Unknown" - do not infer or guess
- Keep the total response under 30 lines

---

## Quick Start Command

```
Read sdlc/prompts/quick-status.md and report
```
