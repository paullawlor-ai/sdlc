# Preparing a Framework Release

The prepared source version is **0.3.0**. `CHANGELOG.md` remains Unreleased until
the release owner completes acceptance and publication. A version bump is not
evidence that a release has been published.

## Local Verification

From the framework repository root, use an isolated development environment:

```bash
python -m pip install -r requirements-dev.txt
python scripts/release_check.py
python -m ruff check scripts tests templates/projects
python -m ruff format --check scripts tests templates/projects
python -m unittest discover -s tests -v
python scripts/generate_adapters.py --check
python scripts/sdlc.py check --strict --json
python -m compileall -q scripts tests templates/projects
python scripts/security_scan.py --output sdlc_artifacts/evidence/security-0.3.0.json
```

Run each starter's pytest suite from its directory after installing its
requirements in a development environment. The security CI job additionally
sets `SDLC_LIVE_AUDIT=1` for `tests.test_security` to prove that the live dependency
auditor detects a controlled vulnerable dependency. This opt-in fixture only
queries advisories; it does not install or execute the vulnerable package.

`release_check.py` verifies version/policy/changelog agreement, generated adapter
content, adapter token budgets, and required release guidance. It does not
replace functional tests, scans, hosted CI, or human approval. The end-to-end
suite copies an embedded framework into unique temporary host projects with
spaces in their paths. It tests all profiles, draft/proposal/approval gates,
requirements and ADR links, required metadata, implemented code/tests, review,
simulated human sign-off, finalization, and upgrade/rollback preservation.
Synthetic scan records are clearly identified as test fixtures; actual release
security evidence comes from `security_scan.py`.

Finalize source and documentation before scanning. A source edit after scanning
invalidates the snapshot and requires affected checks to be refreshed. Retain
separate per-review reports rather than overwriting historical evidence.

## Hosted CI Acceptance

After the owner pushes the prepared branch, retain links to successful runs of:

| Job | Expected coverage |
| --- | --- |
| `quality` | Ruff lint and formatting across framework and starters |
| `security` | Real scanner fixtures, security report, independent dependency audits |
| `test` | Framework and embedded lifecycle/upgrade fixtures on Windows and Linux, Python 3.10-3.13 |
| `starter-smoke` | All three installed starters on Windows and Linux |

Record the run URL, tested commit, result, and security artifact in release
evidence. Failed or unrun jobs do not count as acceptance. Local execution
cannot establish hosted Windows/Linux success.

## Manual Assistant Acceptance

Use a disposable host project per assistant actually used. Install only that
adapter and run the same acceptance sequence. Role instructions are portable;
only Claude hooks provide the documented tool-level write interception.

| Assistant | Install | Evidence to record |
| --- | --- | --- |
| Codex | `sdlc.py setup --assistant codex --verify` | Root managed AGENTS instructions loaded; gate and approval behavior |
| Claude Code | `sdlc.py setup --assistant claude --verify` | Hook commands resolve; protected approval edit blocked; permitted draft edit succeeds |
| Cursor | `sdlc.py setup --assistant cursor --verify` | Compact rules loaded; correct role selected; gate behavior |
| GitHub Copilot | `sdlc.py setup --assistant copilot --verify` | Managed/scoped instructions loaded; gate behavior |

Run these through the assistant, not just the CLI: create an incomplete Draft;
confirm it cannot be implemented or promoted untouched; complete and propose
it; have a human save approval and select the Active Change; implement and
test; produce required scan/review evidence; confirm changed source invalidates
completion; have a human supply required digest sign-off; pass finalization.
Resume with a bounded context packet and check that acceptance criteria remain
present. Verify upgrade preview and rollback preserve owner instructions and
approval fields. Record assistant/app version, OS, date, result, and evidence
link; mark unused assistants as not tested, never as passed.

## Owner Release Checklist

- [ ] Local release checks, tests, starter smoke suites, and security report pass.
- [ ] Hosted CI run URLs and tested commit are recorded and successful.
- [ ] Manual acceptance is recorded for each assistant actually supported/used.
- [ ] A redistribution licence is selected and included before publication.
- [ ] Distribution/support policy is documented. The implemented installation
      path is copying `sdlc/`; packaged distribution requires a separate decision.
- [ ] Migration notes, compatibility limitations, and rollback steps are reviewed.
- [ ] Changes are committed and reviewed under the repository's process.
- [ ] `CHANGELOG.md` is dated for publication; checks are refreshed for final source.
- [ ] The reviewed commit is tagged `v0.3.0` and release notes cite its evidence.

Keep these boxes unchecked until there is actual evidence. This preparation does
not choose a licence, push, merge, tag, or publish on the owner's behalf.
