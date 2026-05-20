# Security Profiles

Security profiles are optional, concrete implementations of the portable
baselines in `docs/security/security-baselines.md`.

Use profiles when a team wants stronger defaults for a known stack, domain, or
deployment model. A profile should not replace S0/A0/V0/C0; it should explain
how those baselines are commonly satisfied in a specific context.

## Profile Rules

- Keep baseline documents technology-neutral.
- Put stack-specific controls in profile files.
- Treat profiles as starting points, not mandatory framework policy.
- Link selected profiles from `sdlc_artifacts/context.md`.
- Record deviations in ADRs or change proposals when they affect architecture or security posture.

## Suggested Profiles

Future profile documents may include:

| Profile | Purpose |
|---------|---------|
| `fastapi-postgres-aws.md` | API service with Postgres, AWS secrets, cloud deployment, and optional AI controls. |
| `static-web-app.md` | Static frontend with CDN, forms, analytics, and supply-chain controls. |
| `saas-api.md` | Multi-tenant SaaS API with auth, billing, tenant isolation, and audit needs. |
| `ai-agent.md` | Tool-using AI agent with retrieval, tool permissions, prompt safety, and cost controls. |
| `data-pipeline.md` | Batch/streaming data workloads with lineage, privacy, and recovery controls. |
| `desktop-cli.md` | Local-first CLI or desktop app with update, config, and local secret handling. |
| `kubernetes.md` | Kubernetes deployment with image policy, admission controls, RBAC, and network policy. |

## Current Reference Profile

The current concrete FastAPI/Postgres/AWS-style controls are preserved in the
"Reference Implementation Profile" section of
`docs/security/security-baselines.md`. They can be moved into a dedicated
profile file when the framework adds full profile support.
