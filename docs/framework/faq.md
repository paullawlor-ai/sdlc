# Framework FAQ

Common questions about when and how to use the framework.

---

## ADR vs Change Proposal - which do I use?

**ADR** (Architecture Decision Record): for *irreversible or hard-to-reverse* decisions that shape the system - choices that, once made, constrain everything else.
- Choosing a framework, database, auth protocol, or messaging system
- Adopting a new architectural pattern (event sourcing, CQRS, plugin architecture)
- Accepting a significant trade-off (eventual consistency for scalability, etc.)
- Retiring a technology or major dependency

**Change Proposal**: for *planned implementation work* - a specific change to code, config, or infrastructure that needs review before it is built.
- Adding a new feature or API endpoint
- Refactoring a module or component
- Updating a dependency with breaking changes
- Any change that would take more than an hour to implement

**Rule of thumb**: if you are deciding *what kind of thing to build*, write an ADR. If you are deciding *what to build next*, write a change proposal. A single piece of work often produces both: an ADR for the key decision, and a change proposal for the implementation.

If a change depends on an ADR, list that ADR in the change proposal's Dependencies section. Implementation must not begin until the change is approved and every blocking ADR is accepted.

---

## What counts as a "significant" change requiring a proposal?

Create a change proposal for any change that is:
- Security-relevant (auth, DB access, middleware, secrets, config defaults, dependencies)
- Modifying a public API or contract
- Touching multiple components
- Expected to take more than ~1 hour
- Introducing or removing a dependency
- Changing deployment or infrastructure configuration

**Skip the proposal for**: typos, comment fixes, test-only changes, minor log-level tweaks, README updates, and other changes that do not affect product behavior, security posture, deployment, shared contracts, or architecture.

When in doubt, write a short proposal. A one-paragraph proposal is better than none.

---

## Can I skip phases?

Yes, with documented justification. The framework includes skip conditions in `docs/framework/sdlc-phases.md`. General guidance:

| Situation | What to skip | What to keep |
|-----------|-------------|-------------|
| Small bug fix | Design phase, formal change proposal | Self-review checklist, unit test |
| Hotfix to production | Design, formal testing | Security check, rollback plan, brief proposal |
| Exploratory spike | All formal process | Document outcome as ADR if a decision was reached |
| Config-only change | Design, testing | Change proposal (1 paragraph), approval |
| Documentation update | Everything | Nothing required |

Always note skips in sdlc_artifacts/STATE.md with a brief justification so future sessions understand why artefacts are missing.

---

## How do I handle a hotfix?

1. Create a minimal change proposal - Summary and Rollback Plan are the most important sections; the rest can be brief
2. Get inline approval: write `Approved - [initials] [date]` in the document and proceed
3. Implement and deploy
4. Run a mental security checklist (no formal review needed for trivial fixes)
5. Update sdlc_artifacts/STATE.md: note what was fixed and that the normal process was abbreviated

---

## How big should a change proposal be?

As short as it can be while covering: what changes, why, how to test it, and how to roll it back. A small change might fit in 10 lines; a complex one might be 60. If you are writing more than ~100 lines, split the change into smaller increments.

The Acceptance Criteria table is the most important part - define it before implementation begins, not after.

Also fill in Dependencies. If there are no blocking ADRs or upstream changes, write `None`. An empty dependency section is treated as incomplete at the Implementation Gate.

---

## What is the Implementation Gate?

The Implementation Gate is the final check immediately before an AI coding assistant edits product code.

It applies to any agentic coding tool using the framework: Cursor, GitHub Copilot, Codex, Claude Code, and others.

The agent must verify:

- The active change exists and its Approval status is `Approved`.
- Every blocking ADR listed by the change, `STATE.md`, or design context is accepted.
- The item is not listed under Pending Approvals or Blocked in `sdlc_artifacts/STATE.md`.
- Acceptance criteria are present and testable.
- Testing expectations are present.

If any item fails, the agent must stop and ask for approval or missing documentation instead of editing product code.

---

## How long should an ADR be?

Long enough that a reader 12 months from now can understand why you chose what you chose, without having to ask anyone. Typically 1-2 pages. The key sections are:
- **Decision Drivers** - the constraints that made this decision non-trivial
- **Options Considered** - what else was evaluated and why it lost
- **Justification** - why the chosen option wins given the drivers

---

## How do I update or supersede an ADR?

Do not edit accepted ADRs. Instead:

1. Create a new ADR with the updated decision
2. In the new ADR header: `Supersedes: ADR-XXXX`
3. In the old ADR: change Status to `Superseded`, add `Superseded by: ADR-YYYY`
4. Move the old ADR from `sdlc_artifacts/decisions/accepted/` to `sdlc_artifacts/decisions/superseded/`

This preserves the history of *why* decisions changed over time.

---

## What if I disagree with the agent's recommendation?

You are the decision-maker - override it. Tell the agent what you want and why. If the reason is a constraint the agent did not know about, add it to `sdlc_artifacts/context.md` so future sessions have that context. If the agent made a design choice you want to revisit, create a new ADR that supersedes the existing one.

---

## How often should sdlc_artifacts/STATE.md be updated?

At the end of every AI session. The orchestrator is responsible for this - prompt it if it forgets: `Update sdlc_artifacts/STATE.md before we finish.`

A stale sdlc_artifacts/STATE.md means the next session wastes time re-reading everything to re-orient. The "Left off at" sentence is the most important field: make it specific enough that the next session can resume without re-reading all artefacts.

---

## What if the agent seems confused about project state?

Run the quick-status check first for a clean orientation:

```
Read sdlc/prompts/quick-status.md and report
```

If still confused, run `python scripts/status.py` in root-template mode or `python sdlc/scripts/status.py` in embedded mode to get a plain-text summary without AI and compare it to what sdlc_artifacts/STATE.md claims. The most common cause is a stale sdlc_artifacts/STATE.md - the orchestrator's `continue.md` path will rebuild it from artefacts.

---

## When should I use phase-specific prompts vs. the orchestrator?

| Prompt | When to use |
|--------|-------------|
| `continue.md` | Starting a session with no specific goal - let the orchestrator figure out what is next |
| `phase-specific/<phase>.md` | You know exactly which phase you want and do not need orientation overhead |
| Direct agent invocation | Quick targeted task within an already-running session |
| `quick-status.md` | You just want to know the current state without starting any work |

---

## How do I handle changes to external dependencies (APIs, third-party services)?

Include them in a change proposal like any other change. In the Testing section, be explicit about what can be tested in CI vs. what requires a staging environment or manual verification. Add pre-deployment validation steps to the deployment runbook for anything that cannot be automatically verified.

---

## How do I get framework updates into a project that already has `sdlc/` copied in?

The simplest approach: copy the updated framework files over the existing `sdlc/` folder and review the diff. Only framework files (`.md`, `.py`, templates) should change - your project artefacts (`sdlc_artifacts/changes/`, `sdlc_artifacts/`, `sdlc_artifacts/reviews/`, `sdlc_artifacts/STATE.md`) are unaffected because they do not exist in the framework repo.

If you have customised any framework files locally, reconcile those changes after the copy.

---

## What is the right level of detail for acceptance criteria?

Use the Given / When / Then format:

```
Given [precondition or context],
when [action or event],
then [observable outcome].
```

Each criterion should be testable by the Tester agent without ambiguity. If you cannot write a test for it, the criterion is probably too vague. Aim for 3-6 criteria per change proposal.
