# Quality and Security Evidence

The framework runtime uses only the Python standard library. Install quality
tools in a separate development environment (Python 3.10 or newer):

```bash
python -m venv .venv
# Activate .venv using your shell's activation command, then:
python -m pip install -r requirements-dev.txt
python -m ruff check scripts tests templates/projects
python -m ruff format --check scripts tests templates/projects
python -m unittest discover -s tests -v
python scripts/security_scan.py
```

These are the same scopes and commands used by CI. Ruff checks errors, unused
imports, and common bugs. Use `python -m ruff format scripts tests templates/projects`
to apply formatting. Formatting and lint fixes do not need a human approval step.
An optional local pre-commit hook can invoke the two check commands; CI remains
the authoritative automated enforcement point.

## Security Scans

From a host project's root, use its development interpreter:

```bash
python sdlc/scripts/security_scan.py --root . --output sdlc_artifacts/evidence/security.json
```

Install the tools from `sdlc/requirements-dev.txt` first. Do not install these
tools into production images. Python starter projects include their own copy of
the Ruff configuration and development requirements for standalone use.

The runner performs:

- Bandit: production Python files at medium-or-higher severity and confidence.
  Test directories are excluded from this check. Inline `nosec` suppressions
  cannot bypass the runner. Low-severity hardening remains part of manual review.
- detect-secrets: all snapshot files, including tests and documentation. Network
  credential verification is disabled so secret material is never sent to a
  provider by the scanner. Reports retain rule, file, and line, not plaintext.
- pip-audit: each `requirements.txt` and `requirements-dev.txt` independently,
  including transitive dependencies. Resolution and vulnerability lookups need
  network access; offline failures, unsupported dependencies, and malformed
  output fail the scan. Requirements ranges are resolved at scan time; pin or
  lock the deployed environment separately when reproducibility is required.

This runner supports Python requirements-based projects. Additional languages,
dependency formats, infrastructure, and deployed artifacts need appropriate
additional checks and linked evidence; these three tools do not establish
complete coverage of those technologies. It scans the current working tree,
including untracked files, rather than historical Git revisions. Repository
history scanning remains a separate release/incident procedure.

## Review and Completion

For every review required by the selected profile/class:

1. Complete implementation, linting, formatting, and testing.
2. Run the scanner. Every tool must succeed with no findings at its configured
   threshold; a tool error never means a clean result.
3. Review the report scope, tool versions, and findings. Fill the REV's
   `Reviewed source digest` from `source_digest` and `Reviewed revision` from
   `revision` when Git is used. Link the project-relative JSON path in
   `Evidence References / Security evidence` (plain path, not a Markdown link).
4. Record applicable S0/A0/V0/C0 controls and assess authorization, data
   boundaries, business logic, and AI tool access beyond scanner coverage.
5. Run `python sdlc/scripts/sdlc.py check --ready-to-finalize` and the Completion
   Gate. When human review is required, the human also copies the reviewed digest
   into `Approval / Approved source digest`; agents cannot change that field.
   The human performs the final transition after required sign-off.

The gate verifies full source hashes, scan scope, tool versions, successful
results, the review's digest, and revision ancestry. Any source edit, new file,
deletion, dependency change, or scan-configuration change requires fresh scans
and review. Reports expire after seven days to require updated advisory checks.
Non-Git projects use the same hash checks. Lifecycle artifacts and virtual
environments/caches are excluded from the snapshot so saving a review or
committing evidence alone does not invalidate it. Evidence commits may follow
the tested commit when it remains in history and the source snapshot matches.

Canonical policy currently permits **no risk exceptions**, in any profile.
Resolve Must-Fix findings and automated findings before completion. An exception
entry (even one claiming approval or a future expiry) is rejected. Introducing
waivers would require a separately reviewed policy change with human-owned
owner, rationale, approval, expiry, and evidence binding; agents cannot invent
or approve a waiver. Suspected scanner false positives must be investigated
and corrected through reviewed code or configuration, never labelled passed
after a failed run.

Existing reviews without scan evidence need a report and digest before their
next completion check. Required implemented reviews are audited for internal
evidence consistency, not compared to later source changes or expired after
completion. Use a separate report path for each completed review; overwriting a
shared report invalidates its historical review binding. No
approval, reviewer name, or date is rewritten during this upgrade. JSON evidence
is a verifiable record of inputs and results, not an independent attestation of
who ran a tool; repository permissions and human review remain necessary.

CI retains the JSON report even when scanning fails. Hosted Windows/Linux
execution still needs to be verified after pushing the branch.

## Starter Dependency Remediation

The first audit found that old test-tool upper bounds retained vulnerable
versions. Starters now use pytest 9.0.3 or newer and compatible async/coverage
plugins. Unused ChromaDB, sentence-transformers, and python-jose requirements
were removed; RAG remains an explicit implementation placeholder and no starter
implements JWT authentication. Add and review the dependencies required by the
chosen implementation when building those features. Development linters/scanners
are kept in `requirements-dev.txt`; Ruff replaces the unused Black dependency.

Tool references: [Ruff configuration](https://docs.astral.sh/ruff/configuration/),
[Bandit](https://bandit.readthedocs.io/),
[pip-audit](https://github.com/pypa/pip-audit), and
[detect-secrets](https://github.com/Yelp/detect-secrets).
