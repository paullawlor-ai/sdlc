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
- Work classified as standard or high-risk under the project policy

**Rule of thumb**: if you are deciding *what kind of thing to build*, write an ADR. If you are deciding *what to build next*, write a change proposal. A single piece of work often produces both: an ADR for the key decision, and a change proposal for the implementation.

If a change depends on an ADR, list that ADR in the change proposal's Dependencies section. Implementation must not begin until the change is approved and every blocking ADR is accepted.

---

## What counts as a "significant" change requiring a proposal?

Use the change classes and selected profile in
[`policy-profiles.md`](policy-profiles.md), backed by `policy/sdlc-policy.json`.
Classification depends on impact, not estimated duration or line count.

- Standard behavior, configuration, and dependency changes require a proposal.
- High-risk work also requires accepted blocking ADRs.
- Trivial documentation, comment, formatting, or isolated low-risk corrections
  do not require a proposal by default. A test or logging change is not trivial
  if it changes security posture, shared contracts, or production behavior.

When uncertain, use the more restrictive class and explain why.

---

## Can I skip phases?

Use the selected profile/class to determine required evidence and approvals.
Design work can be brief when there is no new architectural decision, and
trivial documentation changes do not need a full delivery cycle. A skipped
activity does not waive a gate that policy requires.

Record applicable skips and their justification in `sdlc_artifacts/STATE.md`.
Security, dependency, infrastructure, and hotfix work still use their actual
risk class rather than automatically taking a lighter path.

---

## How do I handle a hotfix?

1. Classify the fix under the existing policy. Urgency does not waive approval,
   required review, or accepted blocking ADRs.
2. Create a Draft with `sdlc.py new change`, complete the required scope,
   dependencies, acceptance criteria, testing, and rollback information, then
   run `sdlc.py propose PATH`.
3. Have a human set the canonical `Approval / Status` to exactly `Approved` and
   fill the separate approval identity/date fields. Do not combine initials or
   dates into the status value, and do not have an agent edit human-only fields.
4. Run the Implementation Gate, implement, and collect the required test and
   fresh scan/review evidence. Use `sdlc.py check --ready-to-finalize` before the
   human completion transition, and follow deployment/rollback procedures.
5. Record the outcome and resume point in `sdlc_artifacts/STATE.md`.

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

Follow [`upgrading.md`](upgrading.md). Back up the host project, replace only
the framework runtime, preview and apply managed adapter upgrades, and verify
the installation. Preserve the host project's `sdlc_artifacts/`, owner
instructions, install manifest, and rollback snapshots.

Do not copy the framework repository's development environments or release scan
records into a host project. Metadata adoption is a separate explicit operation;
it must preserve Markdown and human approval history.

---

## What is the right level of detail for acceptance criteria?

Use the Given / When / Then format:

```
Given [precondition or context],
when [action or event],
then [observable outcome].
```

Each criterion should be testable by the Tester agent without ambiguity. If you cannot write a test for it, the criterion is probably too vague. Aim for 3-6 criteria per change proposal.
