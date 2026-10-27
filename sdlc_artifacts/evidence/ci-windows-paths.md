# Windows CI Path Normalization Fix

## Failure and Scope

PR #1's initial hosted run failed all four Windows Python test jobs with the
same 12 errors. Linux, quality, security, and starter jobs passed. See
https://github.com/paullawlor-ai/sdlc/actions/runs/40592328825.

The runner's temporary project root used `C:\Users\RUNNER~1`, while resolved
artifact paths used `C:\Users\runneradmin`. These refer to the same directory,
but lexical `Path.relative_to` comparisons rejected the two spellings.
`propose_artifact` and completion diagnostics mixed resolved artifacts with an
unresolved root. No CI matrix, gate policy, or approval requirement is relaxed.

## Change and Regression Evidence

- Canonicalize the root when proposing changes/ADRs, retaining the existing
  containment check beneath `sdlc_artifacts`.
- Canonicalize both the root and selected change before completion diagnostics.
- Add five portable regressions using an existing directory followed by `..`
  to reproduce mixed root spellings without requiring Windows symlink privileges.
  Four tests failed before the fix (including both change/ADR subcases), and the
  out-of-artifact-root rejection test passed before and after.
- After the fix, all five regressions pass. Incomplete Drafts still produce
  diagnostics without mutation, out-of-scope files are rejected, and open
  must-fix findings still block completion with a project-relative path.

## Local Verification

- Full framework suite: 121 tests, OK, one opt-in advisory fixture skipped.
- Ruff lint and formatting: passed, 82 Python files already formatted.
- Compilation, generated adapters, release consistency, and strict validation:
  passed.
- Fresh security report: `security-0.3.0-ci-fix.json`; Bandit, detect-secrets,
  and pip-audit all passed with zero findings. Source inputs were stable during
  the scan, and exact equality with the final source manifest was verified.
  Source digest: `5ae99f33e527688975789a0b3aa6cfc9e07c290d55f0fea713c23d8e3f4c5504`.
  Base revision: `473726449135264390c8d8733cbc14afc9919196`.

Prior cleanup/release security reports remain historical source snapshots.
Hosted verification of the new commit is pending the branch update.
