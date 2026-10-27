# Repository Cleanup - 2026-10-27

## Maintenance Proposal

The owner requested a second review of the 25 October inventory and code before
removing stale content. This is framework maintenance on `release/0.3.0-rc.1`.
The starting commit is `f5b9a6c`; its working tree was clean.

Scope: remove the retired `codex/`, `changes/`, `docs/decisions/`,
`docs/project/`, and root `reviews/` placeholders; remove uncalled internal setup
helpers, retrospective iteration inference, and unused FastAPI models; trim
unused starter dependencies; correct the stale documentation identified in the
review; ignore framework backups, private notes, and temporary write files.

Retain current adapters, compatibility script entry points, historical review
and security evidence, fictional examples, optional security extension guides,
and the chatbot's referenced RAG/safety extension points. Do not change approval
policy, implement new starter features, remove development environments, commit,
or push as part of this cleanup.

## Recheck Evidence

- Compare the original complete inventory with tracked files at the starting
  commit, then inspect all candidate folders before deletion.
- Search every source and test file for callers, imports, and path references.
- Confirm the adapter generator's `codex/AGENTS.md` output is under `adapters/`;
  it does not consume the retired root `codex/` directory.
- Verify removed starter dependencies have no use in the shipped applications.
- Preserve standalone quality configuration and test dependencies; development
  dependency reorganization is a separate packaging change.

## Acceptance and Verification Plan

- Current adapters, scaffolding, installation, lifecycle, and upgrade tests pass.
- Each starter imports and passes its smoke suite after dependency cleanup.
- Ruff, compilation, release consistency, adapter drift, and strict validation
  pass; remaining Markdown links and documented local starter paths exist.
- Verify ignore rules exclude generated/private content while retaining shared
  metadata, templates, and evidence.
- Retain old scan reports as historical snapshots and generate separate security
  evidence for the final cleanup source. Do not edit old evidence to claim that
  it covers the changed tree.

## Results

Rechecked the original 25 October inventory against the starting commit: all
208 file entries matched exactly. No additional tracked files or missing entries
were found before cleanup. The original inventory had 57 directories containing
non-cache files.

Removed 17 tracked files across the five retired locations and the unused
FastAPI models package. Removed six unused helpers (five old installer helpers
and the uncalled retrospective iteration helper). Removed six unused direct
starter dependencies: chatbot OpenAI SDK/tokenizer, CLI configuration/logging
packages, and API multipart support. Current commands, hooks, and starter
features remain in place.

Corrected the security-review scaffold instructions and human-only field sample,
FAQ hotfix/classification/upgrade guidance, starter file trees and API examples,
RAG claims, setup summaries, and catalog context-loading guidance. Replaced the
obsolete external watcher contract with a clearly labeled integration design
note that points to current commands and documents their limits. Added historical
labels to the two 0.2.0 records and retained all original evidence snapshots.
Added migration breadcrumbs and ignore rules for backups, private notes, and
atomic-write leftovers.

### Verification

- Framework unit/integration suite: 116 tests, OK; one opt-in live advisory
  fixture skipped. Expected negative-fixture diagnostics are not test failures.
- Starter smoke tests: FastAPI 14, chatbot 1, CLI 1; all passed in the existing
  development environment. No fresh dependency installation was required.
  The same 16 tests also passed in isolated subprocesses with imports of each
  starter's removed dependencies forced to raise `ModuleNotFoundError`, matching
  absent packages. Optional multipart probing still works without the package.
- Ruff lint and format check: passed; 82 Python files checked for formatting.
- Python compilation, release consistency, generated adapters, and strict
  framework validation: passed. Evidence remains untracked until the owner
  commits this cleanup; strict validation reports that advisory warning.
- Local Markdown link checks and every entry in the three revised starter file
  trees: passed. The FastAPI README's Python calls were checked against the
  actual function signatures.
- Removed symbols have no remaining callers/imports. Surviving references to
  retired paths are migration notes or historical evidence, not runtime users.
- Ignore probes exclude backup/private/temporary paths while shared install
  manifests, metadata sidecars, evidence, and templates remain trackable.
- `git diff --check`: passed.
- Initial restricted security scan: Bandit and detect-secrets passed; dependency
  audit failed to complete. The network-enabled rerun passed all three scanners
  with zero findings; the incomplete result was not treated as clean evidence.

The starter suites still emit existing Pydantic configuration and
Starlette/HTTPX deprecation warnings. Their migration is outside removal of the
confirmed dead content. This run does not establish hosted CI or manual
assistant acceptance.

### Security Snapshot

The fresh report is `security-0.3.0-cleanup.json`. Bandit, detect-secrets, and
pip-audit all passed with zero findings. The runner independently audited seven
requirements files, including all starter runtime and development manifests.

- Recorded at: `2026-10-27T21:30:50.648168+00:00`.
- Base Git revision: `f5b9a6c98afe3ed3f582587c4fff1d5d0b4f1aaf` (the cleanup is uncommitted).
- Reviewed source digest: `cbfaab25dd8dbad1dbdc9a3c85bb79ccd866bd335c929ce4b83411978fbbfc8c`.
- Source manifest: 189 inputs; exact equality with the final working tree
  was verified after scanning, and `inputs_stable` is true.

The previous `security.json` and `security-0.3.0.json` remain historical evidence;
neither was rewritten or used to claim that the cleanup source was scanned.

### Delivery State

Cleanup is left as working-tree changes on `release/0.3.0-rc.1`. Nothing was
committed, pushed, tagged, or released during this task. The owner's backup and
starting commit retain the pre-cleanup source.


## Follow-up Commit Request

After reviewing the cleanup results, the owner requested a commit on a new
branch, `cleanup/repository-content`. The cleanup history above describes its
original uncommitted delivery state. The follow-up commit includes this record
and the fresh scan report; pushing remains outside this request.

## Post-cleanup Folder Inventory

193 non-cache files across 44 directories containing files, including
this record and the separate cleanup security report.

| Folder | Immediate files |
| --- | --- |
| `.` | `.gitignore`, `AGENTS.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `README.md`, `SECURITY.md`, `VERSION`, `requirements-dev.txt`, `ruff.toml` |
| `.github/workflows` | `framework-ci.yml` |
| `adapters` | `README.md` |
| `adapters/claude` | `README.md`, `settings.json` |
| `adapters/codex` | `AGENTS.md` |
| `adapters/copilot` | `copilot-instructions.md` |
| `adapters/copilot/instructions` | `sdlc.instructions.md` |
| `adapters/cursor/rules` | `README.md`, `agents.mdc`, `core.mdc`, `implementation-gate.mdc`, `security.mdc` |
| `agents` | `README.md`, `architect.md`, `developer.md`, `devops.md`, `docs-writer.md`, `orchestrator.md`, `requirements-analyst.md`, `security-reviewer.md`, `tester.md`, `web-designer.md` |
| `catalogs` | `README.md`, `owasp-llm-top10-summary.md`, `owasp-secure-coding-100.md`, `owasp-top10-web-summary.md`, `sdlc-checklist.md` |
| `codex-review` | `further-remediation-plan.md`, `implementation-report.md`, `remediation-plan.md` |
| `docs/framework` | `agent-system.md`, `assistant-adapters.md`, `assistant-quickstart.md`, `external-enforcement-agent.md`, `faq.md`, `getting-started.md`, `installation-modes.md`, `lifecycle-example.md`, `policy-profiles.md`, `quality-and-security.md`, `releasing.md`, `sdlc-phases.md`, `starter-templates.md`, `structured-artifacts.md`, `upgrading.md` |
| `docs/security` | `security-baselines.md` |
| `docs/security/owasp` | `README.md` |
| `docs/security/profiles` | `README.md` |
| `examples` | `README.md` |
| `examples/adr` | `ADR-0004-notification-delivery.md` |
| `examples/changes` | `0005-plant-health-log.md` |
| `policy` | `sdlc-policy.json`, `token-baseline.json` |
| `prompts` | `bootstrap.md`, `continue.md`, `onboard.md`, `quick-status.md` |
| `prompts/phase-specific` | `deployment.md`, `design.md`, `docs.md`, `implementation.md`, `requirements.md`, `security-review.md`, `testing.md`, `web-design.md` |
| `scripts` | `_artifacts.py`, `_fields.py`, `_paths.py`, `_policy.py`, `_readiness.py`, `_security.py`, `_setup.py`, `generate_adapters.py`, `init_project.py`, `install_hooks.py`, `new_adr.py`, `new_change.py`, `new_requirement.py`, `new_retrospective.py`, `new_review.py`, `new_state.py`, `release_check.py`, `sdlc.py`, `security_scan.py`, `setup_project.py`, `status.py`, `token_report.py`, `verify_setup.py` |
| `scripts/hooks` | `_gate_common.py`, `approval_field_guard.py`, `bash_gate.py`, `implementation_gate.py`, `session_end_reminder.py` |
| `sdlc_artifacts/evidence` | `repository-cleanup.md`, `security-0.3.0-cleanup.json`, `security-0.3.0.json`, `security.json` |
| `templates/documents` | `adr.md`, `change-proposal.md`, `config.json`, `deployment-runbook.md`, `project-context.md`, `requirement.md`, `retrospective.md`, `review.md`, `security-policy.md`, `state.md`, `test-plan.md`, `user-story.md` |
| `templates/projects/python-chatbot` | `README.md`, `requirements-dev.txt`, `requirements.txt`, `ruff.toml` |
| `templates/projects/python-chatbot/app` | `__init__.py`, `config.py`, `main.py` |
| `templates/projects/python-chatbot/app/chat` | `__init__.py`, `engine.py`, `memory.py`, `prompts.py` |
| `templates/projects/python-chatbot/app/rag` | `__init__.py`, `retriever.py` |
| `templates/projects/python-chatbot/app/safety` | `__init__.py`, `input.py`, `output.py` |
| `templates/projects/python-chatbot/app/utils` | `__init__.py`, `logging.py` |
| `templates/projects/python-chatbot/tests` | `__init__.py`, `test_smoke.py` |
| `templates/projects/python-cli` | `README.md`, `requirements-dev.txt`, `requirements.txt`, `ruff.toml` |
| `templates/projects/python-cli/app` | `__init__.py`, `cli.py` |
| `templates/projects/python-cli/app/commands` | `__init__.py`, `example.py` |
| `templates/projects/python-cli/tests` | `__init__.py`, `test_smoke.py` |
| `templates/projects/python-fastapi-ai` | `Dockerfile`, `README.md`, `requirements-dev.txt`, `requirements.txt`, `ruff.toml` |
| `templates/projects/python-fastapi-ai/app` | `__init__.py`, `config.py`, `main.py` |
| `templates/projects/python-fastapi-ai/app/api` | `__init__.py`, `dependencies.py`, `routes.py` |
| `templates/projects/python-fastapi-ai/app/core` | `__init__.py`, `logging.py`, `rate_limit.py` |
| `templates/projects/python-fastapi-ai/app/llm` | `__init__.py`, `client.py`, `safety.py` |
| `templates/projects/python-fastapi-ai/tests` | `__init__.py`, `conftest.py`, `test_api.py`, `test_safety.py` |
| `tests` | `__init__.py`, `security_fixtures.py`, `test_approval_field_guard.py`, `test_artifacts.py`, `test_cli.py`, `test_end_to_end.py`, `test_fields.py`, `test_gate_common.py`, `test_lifecycle.py`, `test_policy.py`, `test_readiness.py`, `test_release.py`, `test_security.py`, `test_setup.py`, `test_status.py`, `test_templates.py` |
| `workflows` | `01-requirements.md`, `02-design.md`, `03-implementation.md`, `04-testing.md`, `05-security-review.md`, `06-deployment.md`, `07-iterate.md`, `README.md` |
