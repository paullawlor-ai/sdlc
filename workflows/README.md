# Workflows

SDLC phase workflow documents.

## Phases

| # | Phase | File | Description |
|---|-------|------|-------------|
| 1 | Requirements | `01-requirements.md` | Gather and document requirements |
| 2 | Design | `02-design.md` | Create architecture and ADRs |
| 3 | Implementation | `03-implementation.md` | Build the software |
| 4 | Testing | `04-testing.md` | Verify the implementation |
| 5 | Security Review | `05-security-review.md` | Check security compliance |
| 6 | Deployment | `06-deployment.md` | Deploy to production |
| 7 | Iterate | `07-iterate.md` | Learn and plan next cycle |

## Flow

```
Requirements -> Design -> Implementation -> Testing
                                            v
        Iterate <- Deployment <- Security Review
```

## Usage

Each workflow document contains:
- Phase overview
- Primary agent
- Activities and steps
- Outputs
- Quality checklist
- Approval gates
- Phase transitions

Reference the appropriate workflow when working in that phase.

## Supporting Specialists

Some agents support multiple phases rather than owning a phase:

| Agent | File | Typical Phase |
|-------|------|---------------|
| Docs Writer | `agents/docs-writer.md` | Implementation, Testing, Deployment, Iterate |
| Web Designer/Engineer | `agents/web-designer.md` | Design, Implementation, Testing |

Use `prompts/phase-specific/docs.md` for documentation-focused work and
`prompts/phase-specific/web-design.md` for browser UI work.
