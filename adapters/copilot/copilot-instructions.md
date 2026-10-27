<!-- Generated from policy/sdlc-policy.json; do not edit directly. -->
# Agentic SDLC 0.3.0

Read `sdlc_artifacts/STATE.md` and `sdlc_artifacts/context.md` when present.
For resumed work, prefer `python sdlc/scripts/sdlc.py context` over scanning all
framework documents. Do not edit `sdlc/` unless maintaining the framework.

## Change Classification

- **trivial**: Documentation, comments, formatting, or an isolated low-risk correction.
- **standard**: A normal feature, behaviour, configuration, or dependency change.
- **high-risk**: Authentication, authorization, secrets, sensitive data, migrations, architecture, production infrastructure, or AI safety.

Use the project profile from `sdlc_artifacts/config.json`, or
`standard` when absent. Run
`python sdlc/scripts/sdlc.py gate implementation` before product-code edits.

## Rules

- **R1** Read STATE.md and context.md before significant or resumed work.
- **R2** Classify the requested change before deciding which gates apply.
- **R3** Standard and high-risk implementation requires a human-approved change proposal.
- **R4** High-risk implementation requires accepted blocking ADRs.
- **R5** When multiple changes are approved, STATE.md must name one Active Change.
- **R6** Assistants never modify human-only approval fields.
- **R7** Required reviews need fresh scan evidence. Human sign-off binds the source digest; completion follows profile/class policy.
- **R8** Detailed role, workflow, and security references are loaded only when applicable.

Human approval must be present in the artifact; verbal approval is insufficient.
When a role is requested, read only its matching file under `sdlc/agents/`.
Use `python sdlc/scripts/sdlc.py next` for the next permitted action.
