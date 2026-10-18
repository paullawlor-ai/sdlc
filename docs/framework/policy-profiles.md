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

The Implementation Gate and human-only approval rules apply according to the
effective class and profile. Run `python sdlc/scripts/sdlc.py check` to validate
configuration and generated adapters.
