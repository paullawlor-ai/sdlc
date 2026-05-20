# Phase 7: Iterate Workflow

## Overview

The Iterate phase closes the current cycle and prepares for the next iteration based on feedback, metrics, and lessons learned.

## Agent

**Primary**: Orchestrator (`agents/orchestrator.md`)

## Inputs

- Completed deployment
- Feedback and metrics
- Issues or bugs discovered
- New feature requests
- Retrospective notes

## Activities

### 1. Gather Feedback

Collect:
- User feedback
- Bug reports
- Performance metrics
- Security alerts
- Monitoring data

### 2. Conduct Retrospective

Create a structured retrospective document that is saved and readable in future sessions:

```bash
python sdlc/scripts/new_retrospective.py [N] "[optional name]"
# e.g. python sdlc/scripts/new_retrospective.py 2 "Phase 2 Evaluation Orchestrator"
```

Fill out `sdlc_artifacts/retrospectives/YYYY-MM-DD-iter-N.md` using `templates/documents/retrospective.md`. Key sections:
- What went well / what to improve
- **Effort accuracy**: compare estimated vs actual hours from change documents - note any systematic pattern
- **ADR review**: list any accepted ADRs whose context has shifted; flag for Architect to revisit
- **AC coverage**: verify all delivered changes have fully-linked Test IDs in their AC tables
- **Framework feedback**: how did the process itself perform this iteration
- **Action items**: concrete, owned, dated

### 3. Update Backlog

Based on feedback:
- Add new requirements
- Prioritize bug fixes
- Reprioritize existing items
- Close completed items

### 4. Archive Completed Items and Review ADRs

- ADRs remain in `accepted/` - but check `review-by` dates; flag overdue ones in sdlc_artifacts/STATE.md for Architect
- Change docs marked as implemented and effort actuals recorded
- Reviews archived
- Documentation updated

### 5. Plan Next Iteration

Determine scope for next cycle:
- What's the highest priority?
- What dependencies exist?
- What resources are available?
- What's the MVP for next iteration?

### 6. Reset for Next Cycle

Prepare to restart the SDLC:
- Clear work-in-progress
- Update project status
- Identify starting point

## Outputs

| Output | Location |
|--------|----------|
| Retrospective document | `sdlc_artifacts/retrospectives/YYYY-MM-DD-iter-N.md` |
| Updated backlog | `sdlc_artifacts/requirements/` |
| Next iteration plan | `sdlc_artifacts/` |
| Updated sdlc_artifacts/STATE.md | `sdlc_artifacts/STATE.md` |

## Iteration Checklist

- [ ] Feedback collected
- [ ] Retrospective completed
- [ ] Lessons documented
- [ ] Backlog updated
- [ ] Documentation current
- [ ] Next iteration scoped
- [ ] Team aligned on priorities

## Retrospective Questions

### Process
- Did the SDLC phases work well?
- Were approval gates effective?
- Was documentation adequate?

### Quality
- Were there production issues?
- Was testing sufficient?
- Did security review catch issues?

### Velocity
- Was scope realistic?
- Were estimates accurate?
- What slowed us down?

### Team
- Was communication clear?
- Were handoffs smooth?
- What tools helped/hindered?

## Metrics to Review

### Quality
- Bugs found post-deployment
- Security issues discovered
- Test coverage

### Performance
- Response times
- Error rates
- Resource utilization

### Process
- Cycle time (idea to production)
- Approval gate time
- Rework rate

## Continuous Improvement

### Common Actions

**If too many bugs**:
- Increase test coverage
- Add more negative tests
- Improve code review

**If security issues**:
- Enhance security review
- Add security tests earlier
- Improve developer training

**If slow cycles**:
- Reduce scope per iteration
- Streamline approvals
- Automate more

**If scope creep**:
- Better requirements definition
- Stricter change control
- Clearer MVP boundaries

## No Formal Approval Gate

Iteration phase completes when:
- Retrospective done
- Backlog updated
- Next iteration planned

## Phase Transition

**Next Phase**: Requirements (new cycle)

**Transition Trigger**: Ready to start next iteration

**Starting New Cycle**:
```markdown
## Starting New Iteration

### Previous Iteration
- Completed: [summary]
- Lessons: [key lessons]

### Next Iteration
- Focus: [main goal]
- Scope: [key items]
- Timeline: [if known]

### Starting Requirements Phase

Reading requirements for next iteration...
```

## Integration with Framework

The Iterate phase:
1. Reviews how the framework was used
2. Identifies framework improvements
3. Updates templates if needed
4. Improves agent instructions
5. Refines workflows

## Tips

1. **Honest Retrospectives**: Real improvement needs honesty
2. **Action Items**: Don't just discuss, act
3. **Small Batches**: Smaller iterations = faster learning
4. **Measure What Matters**: Focus on actionable metrics
5. **Celebrate Wins**: Acknowledge what went well

## Next Iteration Prompt

To start the next iteration:

```
Read prompts/continue.md and start the next iteration
```

The Orchestrator will:
1. Review project state
2. Read new requirements
3. Begin the next cycle

