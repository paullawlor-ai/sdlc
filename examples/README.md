# Examples

Filled-in reference documents showing the expected level of detail for each document type. Based on a fictional project called **Bloom** - a plant care reminder API.

Use these to calibrate your own documents, not as copy-paste templates.

The Bloom records are historical fictional examples, not executable 0.3.0
completion evidence. Their statuses and names do not confer approval on a real
project. For the current command sequence, use
[`docs/framework/lifecycle-example.md`](../docs/framework/lifecycle-example.md)
and the executable `tests/test_end_to_end.py` fixture. A real completion needs
the current profile's metadata, scan report, source digest, and human sign-off
where required; do not copy a fictional approval or invent a passing scan.

---

## Documents

### ADR - `examples/adr/ADR-0004-notification-delivery.md`

An Architecture Decision Record for choosing a notification delivery strategy. Key things to notice:

- **Status metadata**: `review-by date` is set so the orchestrator flags it when stale. Use 6 months for technology choices, 12 months for architectural patterns.
- **Decision Drivers**: five named constraints that made this a real decision. Without these, a future reader cannot judge whether the decision still holds if circumstances change.
- **Options Considered**: four explicit options - including one (Option D) that is quickly disqualifying. Showing why bad options were rejected is as important as explaining why the chosen one wins.
- **Justification**: one paragraph that explicitly references the decision drivers by name, not just "this was the best option."
- **Security Notes**: specific threat model, mitigations, and control numbers - not a generic checklist.
- **Rollback / Reversal Plan**: describes how to undo the *decision* (disable the feature flag, fall back to in-app), not just the implementation.
- **Follow-up Work**: three concrete items that become change proposals or backlog entries. ADRs create downstream work - capture it here.

### Change Proposal - `examples/changes/0005-plant-health-log.md`

A completed change proposal for a new feature (plant health log). Key things to notice:

- **Acceptance Criteria table**: six criteria in Given/When/Then format, defined *before* implementation. The Tester fills in the Test ID column after writing tests. This is the most important section - if you only fill in one thing before coding, make it this.
- **AC-04 and AC-06**: both test security requirements (access control and MIME type spoofing), not just happy-path behaviour. Security criteria belong in the AC table alongside functional ones.
- **Effort section**: estimated hours recorded before starting, actual hours on completion. One data point is not useful; accumulated across many changes it reveals estimation bias.
- **Security Impact**: maps to specific OWASP categories and control numbers. The "new risks introduced" field is not left blank - it documents the enumerable ID decision and its mitigation.
- **Failure modes**: the Reliability section calls out the S3/DB consistency edge case and explicitly accepts it for v1 rather than silently ignoring it.
- **Operational Notes**: specific env var names and a concrete alert threshold - ops-ready, not just dev-ready.
- **Rollback**: exact commands, expected data loss, and a statement about acceptability. Someone under incident pressure needs to execute this without thinking.

---

## What these examples are not

- The project ("Bloom") is fictional. Paths, env var names, and file references are illustrative - yours will differ.
- These represent a mature use of the framework. Early change proposals on a new project may be shorter; that is fine.
- Do not copy the content - copy the *structure and level of detail*.
