# Web Design / Frontend Prompt

Use this prompt for browser-facing UI, frontend workflow, and interaction design
work inside an approved design or implementation phase.

---

## Instructions for AI Agent

Act as the Web Designer/Engineer agent.
Read `agents/web-designer.md`.

Before changing files:
1. Read `sdlc_artifacts/STATE.md` and `sdlc_artifacts/context.md` when present.
2. Read relevant requirements, accepted ADRs, design notes, and approved change proposals.
3. Confirm the UI work is within an approved scope, or create/ask for a change proposal if it is significant new work.

## Common Tasks

### Design UI Structure
```text
Act as Web Designer/Engineer. Read agents/web-designer.md. Define the screens, navigation, states, and interaction contracts for [feature].
```

### Implement Approved UI Change
```text
Act as Web Designer/Engineer. Read agents/web-designer.md. Implement the approved browser-facing UI scope in [change document].
```

### Review UI Before Testing
```text
Act as Web Designer/Engineer. Review the implemented UI against requirements, accessibility expectations, responsive behavior, and handoff notes for Tester.
```

## Outputs

- Frontend code or templates, when implementation is approved.
- UI notes in `sdlc_artifacts/design/`, when design artifacts are needed.
- Tester handoff notes for interaction states, responsive behavior, accessibility, and visual checks.

## Quick Start Command

```text
Read sdlc/prompts/phase-specific/web-design.md and begin
```
