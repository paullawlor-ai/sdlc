# Implementation Phase Prompt

Focus on coding and change proposals.

---

## Instructions

```
Act as the Developer agent.
Read agents/developer.md.
Read workflows/03-implementation.md.
Read the active change's linked accepted ADRs for design context.

Create a change proposal before implementing any code.
Scaffold as Draft, complete scope/criteria/testing, and run `sdlc.py propose PATH`
before requesting the human's approval. Run lint/format checks with tests. Follow
docs/framework/quality-and-security.md before completion; source changes require
fresh affected tests, scans, review, and any required human digest sign-off.
Before editing product code, run the Implementation Gate from workflows/03-implementation.md.
```

## Quick Commands

### Create Change Proposal
```
Act as Developer. Read agents/developer.md. Create a change proposal for [feature/fix].
```

### Implement Approved Change
```
Act as Developer. Read agents/developer.md and workflows/03-implementation.md. Run the Implementation Gate for sdlc_artifacts/changes/[NNNN]-[name].md. If it passes, implement the approved change. If it fails, stop and report the missing approval or dependency.
```

### Review Implementation
```
Act as Developer. Self-review the implementation against the change proposal and security controls.
```
