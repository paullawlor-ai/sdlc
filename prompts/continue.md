# Continue Prompt

Use this prompt to resume work on an existing project.

---

## Instructions for AI Agent

You are continuing work with the **Agentic SDLC Framework**. Assess the current state and resume from where work left off.

### Step 1: Read Project State

Start with the fast-path files. Only fall back to scanning all artefacts if sdlc_artifacts/STATE.md is absent or clearly stale.

```
Fast path (read in order):
1. sdlc_artifacts/STATE.md                              - current phase, open items, last session summary
2. sdlc_artifacts/context.md              - stack, conventions, constraints
3. sdlc_artifacts/retrospectives/         - most recent file (open action items)

Fallback scan (only if sdlc_artifacts/STATE.md is missing or suspicious):
- sdlc_artifacts/requirements/            - documented requirements
- sdlc_artifacts/decisions/proposed/             - pending ADRs
- sdlc_artifacts/decisions/accepted/             - accepted ADRs (check review-by dates)
- sdlc_artifacts/changes/                             - change proposals (check statuses)
- sdlc_artifacts/reviews/                             - review documents
```

### Step 2: Identify Pending Items

Look for:
1. **Pending approvals**: Documents with status "Proposed" - note what work is blocked vs. independent
2. **In-progress work**: Changes marked "Approved" but not "Implemented"
3. **Unaddressed findings**: Security reviews with must-fix items
4. **Missing artifacts**: Gaps in the SDLC flow
5. **Stale ADRs**: Any accepted ADR with a `review-by` date in the past - flag in sdlc_artifacts/STATE.md
6. **Open retrospective actions**: From the most recent retrospective in `sdlc_artifacts/retrospectives/`

### Step 3: Provide Status Report

```markdown
## Project Status Report

### Current Phase
[Phase name]

### Completed Items
- [x] [Completed item 1]
- [x] [Completed item 2]

### In Progress
- [ ] [In-progress item] - Status: [status]

### Pending Approvals
| Document | Type | Status | Location |
|----------|------|--------|----------|
| [Name] | [Change/ADR] | Proposed | [Path] |

### Blockers
- [Any blockers or issues]

### Recommended Next Action
[What to do next]
```

### Step 4: Handle Pending Approvals

If there are pending approvals:

```markdown
[PAUSE] PENDING APPROVAL

The following items are waiting for approval:

1. **[Document Name]**
   - Type: [Change/ADR]
   - Location: [path]
   - Summary: [brief summary]

To proceed:
- Review the document
- **You** open the file in your editor, update status to "Approved" (or "Accepted" for ADRs), and save
- Tell me to continue

The AI cannot set approval fields. If you say "approved" but the file still shows Proposed, the agent must ask you to save the file first.

Would you like me to summarize any of these documents?
```

### Step 5: Resume Appropriate Phase

Based on state:

**If pending change proposal:**
- Summarize what was proposed
- Wait for approval or proceed if approved

**If implementation in progress:**
- Review what's been built
- Identify remaining work
- Run the Implementation Gate before editing product code
- Continue implementation

**If testing needed:**
- Invoke Tester agent
- Create/update test plan

**If tests passed and the effective class/profile requires a REV:**
- Invoke Security Reviewer agent (Completion Gate requirement is defined by `policy/sdlc-policy.json`)
- Create or update `sdlc_artifacts/reviews/REV-*.md` and fill `## Completion Gate` in the change doc

**If security review needed:**
- Invoke Security Reviewer agent
- Check against baselines; pass Completion Gate before Implemented

**If deployment ready:**
- Invoke DevOps agent
- Create/update runbook

### Step 6: Provide Context

When resuming, provide:
- What was last completed
- What's currently in progress
- What needs to happen next
- Any decisions needed

---

## Quick Start Commands

### Resume Work
```
Read prompts/continue.md and resume. Show me the current project status.
```

### Get Status Only
```
Read prompts/continue.md and give me a status report without taking any action.
```

### Resume Specific Phase
```
Read prompts/continue.md and continue with the [phase name] phase.
```

### Start Next Iteration
```
Read prompts/continue.md and start the next iteration. Review what was completed and plan the next cycle.
```
