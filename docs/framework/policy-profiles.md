# Policy Profiles and Change Classes

The canonical policy is `policy/sdlc-policy.json`. Assistant adapters are
generated from it; do not maintain independent gate rules in adapter files.

## Change Classes

- **Trivial** covers documentation, comments, formatting, and isolated low-risk
  corrections. It does not require a proposal by default.
- **Standard** covers normal product behaviour, features, configuration, and
  dependencies. It requires a human-approved change proposal.
- **High-risk** covers architecture, authentication, authorization, secrets,
  sensitive data, migrations, production infrastructure, and AI safety. It
  requires a proposal and accepted blocking ADRs.

Classification is based on impact, not line count. When uncertain, use the more
restrictive class and record the reason in the change proposal.

## Profiles

Projects select a profile in `sdlc_artifacts/config.json`:

- `lite` requires completion security reviews only for high-risk changes.
- `standard` requires them for standard and high-risk changes.
- `regulated` requires them for every change class.

Review sign-off also follows policy:

- `lite` uses the agent recommendation when a review is required.
- `standard` uses the agent recommendation and the human-owned transition of the
  change status to `Implemented`; REV human verdict fields are optional.
- `regulated`, and every `high-risk` change under any profile, requires exactly
  one approving human Summary Verdict plus a named reviewer, ISO review date,
  and human-owned approved source digest matching the reviewed snapshot.

Every required review links a successful, fresh scan report and records its
reviewed source digest/revision. Scanner errors, unresolved findings, incomplete
scope, stale source, and active reports older than seven days block completion.
No profile permits risk waivers. See `quality-and-security.md` for coverage and
`upgrading.md` for handling existing reviews without altering human fields.

Repository evidence is checked independently from artifact content. Lite and
standard projects receive advisory warnings when a Git repository has no
baseline commit or SDLC evidence is untracked or modified. Regulated projects
must have a baseline and committed SDLC evidence before finalisation. A project
that intentionally does not use Git can declare `"repository_mode": "non-git"`
in `sdlc_artifacts/config.json`; `"git"` explicitly expects a repository and
`"auto"` is the default.

Before changing a status to `Implemented`, run:

```bash
python sdlc/scripts/sdlc.py check --ready-to-finalize
```

This reports missing evidence and human actions without editing protected
fields. A normal `sdlc check` also audits already-Implemented changes when a review
is required, checking their historical evidence and required human trail without
invalidating completed snapshots just because subsequent code or time changed.

The Implementation Gate and human-only approval rules apply according to the
effective class and profile. Run `python sdlc/scripts/sdlc.py check` to validate
configuration and generated adapters.
