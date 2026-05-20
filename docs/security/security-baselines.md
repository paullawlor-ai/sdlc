# Security Baselines

The framework enforces four portable security baselines. Apply the relevant
baselines based on the project's characteristics, then record the concrete
technology choices in `sdlc_artifacts/context.md`, ADRs, and change proposals.

These baselines are intentionally technology-neutral. The reference profile
near the end preserves a more opinionated implementation example for teams that
want stronger defaults.

## S0 - Baseline for Any Project (Minimum)

Every project must address these controls:

### Authentication & Authorization
- [ ] Authentication strategy documented, or explicitly marked N/A for local-only tools.
- [ ] Authorization enforced for protected operations and data access.
- [ ] Least privilege access model documented for users, services, and maintainers.

### Input & Output
- [ ] Server-side input validation applied at trust boundaries.
- [ ] Output encoding or sanitization applied where data crosses presentation boundaries.
- [ ] Injection controls used for database, shell, template, and interpreter boundaries.

### Secrets Management
- [ ] No secrets committed to the repository.
- [ ] Secrets excluded or redacted from logs, traces, prompts, and evidence.
- [ ] Secrets loaded from an approved local, hosted, or cloud secret store.

### Communication
- [ ] HTTPS or equivalent secure transport used for production network traffic.
- [ ] TLS certificate and external connection assumptions documented.

### Error Handling
- [ ] Client-facing errors avoid leaking sensitive implementation detail.
- [ ] Diagnostic detail is logged only where access is controlled and redaction is applied.

### Dependencies
- [ ] Dependency versions are pinned or locked where the ecosystem supports it.
- [ ] Dependency vulnerability review is defined for CI, release, or maintenance cadence.

### Operations
- [ ] Structured logging includes request or correlation identifiers where useful.
- [ ] Outbound calls and long-running tasks have timeouts.
- [ ] Abuse controls are defined for public or shared interfaces.

## A0 - Baseline for AI/LLM Features

Projects with AI/LLM features must also address:

### Input Safety
- [ ] Model inputs are validated, normalized, and scoped before use.
- [ ] Prompt injection and instruction-conflict risks are considered and mitigated.
- [ ] Retrieved or user-supplied content is treated as untrusted.

### Tool/Plugin Safety
- [ ] Tool access is allowlisted by capability and context.
- [ ] Tool parameters are validated strictly before execution.
- [ ] Tool permissions follow least privilege and are auditable.

### Data Boundaries
- [ ] Retrieval and memory are scoped to the authorized user, tenant, or data domain.
- [ ] Sensitive data handling rules are documented.
- [ ] PII or regulated data paths have detection, redaction, or exclusion controls.

### Output Controls
- [ ] Model output is treated as untrusted until validated or reviewed.
- [ ] Output policy checks are defined for harmful, sensitive, or non-compliant content.
- [ ] Human review is required for high-risk or irreversible actions.

### Cost/DoS Controls
- [ ] Token, request, or compute limits are defined.
- [ ] Timeouts and concurrency limits are set for model calls and tools.
- [ ] Failure modes avoid runaway retries or unbounded spend.

### Audit
- [ ] AI-assisted actions are logged with enough metadata for review.
- [ ] Sensitive prompts and outputs are not stored verbatim unless approved.
- [ ] Model/provider/version assumptions are tracked where they affect behavior.

## V0 - Evidence/Audit Baseline

Projects requiring auditability must also address:

### Event Logging
- [ ] Audit events include who, what, when, and where relevant why.
- [ ] Events include request, trace, or correlation IDs.
- [ ] Events include policy, ruleset, or configuration version where decisions depend on them.

### Integrity
- [ ] Audit records are protected against casual alteration or deletion.
- [ ] Tamper-evidence or independent retention is used for high-assurance workflows.

### Retention
- [ ] Retention period and deletion policy are documented.
- [ ] Access controls for audit data are documented.
- [ ] Export, review, and incident access paths are defined.

### Traceability
- [ ] Requirements, acceptance criteria, tests, reviews, and deployment evidence are linked.
- [ ] Cross-service or cross-tool actions can be correlated.

## C0 - Cloud Deployment Baseline

Projects deployed to cloud environments must also address:

### Identity & Access
- [ ] Cloud identities follow least privilege.
- [ ] Service accounts have minimal permissions and clear ownership.
- [ ] Long-lived credentials are avoided where managed identities or federation are available.

### Key Management
- [ ] Keys and production secrets are stored in managed or otherwise approved secure storage.
- [ ] Rotation and revocation expectations are documented.
- [ ] Backup, restore, and break-glass access are documented where needed.

### Network
- [ ] Public exposure is intentional and documented.
- [ ] Administrative access is restricted.
- [ ] Network boundaries and trust zones are documented.

### Logging & Monitoring
- [ ] Operational logs are centralized or otherwise accessible for incident response.
- [ ] Security-relevant events have alerting or review cadence.
- [ ] Administrative actions are logged.

### Asset Management
- [ ] Asset inventory is maintained.
- [ ] Resource ownership and tagging conventions are defined.
- [ ] Access documentation is kept current.

## Reference Implementation Profile

The following profile preserves a stronger, concrete baseline that can be copied
or adapted for projects using a FastAPI/Postgres/AWS-style stack with AI,
multi-tenant data, and audit needs. Treat it as an example profile, not the
framework-wide default.

### S0 Reference Controls
- Authentication strategy: OIDC/SSO plus API keys.
- Authorization: granular RBAC on every endpoint.
- Input validation: Pydantic/FastAPI models at API boundaries.
- Output encoding: template autoescape where server-rendered views are used.
- Database access: parameterized queries or ORM-only query construction.
- Secrets: AWS Secrets Manager, local secret file for development, and CI secret scanning.
- Logging: structured logs with correlation IDs and redaction.
- Abuse controls: middleware rate limiting for public interfaces.

### A0 Reference Controls
- Model output validated by a policy engine before trusted use.
- Prompt injection controls include pattern checks, classifier/evaluator support, and prompt isolation.
- Tool access is mapped through static route or capability allowlists.
- Tenant-scoped retrieval uses row-level security or equivalent data boundaries.
- PII handling uses detection and redaction before evidence storage.
- Human-in-the-loop review is required for high-risk outputs.
- Token, request, timeout, and concurrency quotas are enforced per route, user, or tenant.

### V0 Reference Controls
- Append-only event log using JSONL and/or Postgres.
- Events include actor, action, timestamp, trace ID, policy version, and redaction notes.
- Tamper evidence uses a SHA-256 hash chain or equivalent integrity mechanism.
- Retention uses object lifecycle policy or WORM-capable storage where required.
- Cross-service tracing uses correlation IDs or OpenTelemetry.

### C0 Reference Controls
- IAM roles are least privilege and documented.
- Keys are stored in AWS KMS or equivalent managed KMS/HSM.
- Secrets are managed through AWS Secrets Manager or equivalent.
- Production runs inside private networking where possible.
- Central logging uses a stack such as Loki/Tempo or equivalent.
- Security event alerting uses Prometheus alerts or equivalent.

## Expansion Backlog

Use these as future framework side quests:

- Add an M0 mobile/client baseline for offline storage, secure update, and device permissions.
- Add a D0 data protection baseline for GDPR/PII, data classification, and deletion workflows.
- Add an R0 resilience baseline for backups, restore tests, disaster recovery, and SLOs.
- Add an O0 open-source baseline for license scanning, contribution flow, and disclosure policy.
- Add a K0 Kubernetes baseline for cluster RBAC, admission controls, image policy, and network policy.
- Add profile documents under `docs/security/profiles/` for common stacks such as static sites, SaaS APIs, data pipelines, AI agents, and desktop apps.

## Applying Baselines

### In Requirements Phase

Identify which baselines apply:
- S0: Always.
- A0: If building AI/LLM features.
- V0: If auditability, compliance evidence, or high-assurance traceability is required.
- C0: If deploying to cloud infrastructure.

### In Design Phase

Map baseline requirements to architectural decisions:

```markdown
## Security Notes (in ADR)
- S0 controls: Auth strategy, input validation layer, secret handling.
- A0 controls: Tool allowlist, output policy checks.
- V0 controls: Append-only audit log.
```

### In Implementation Phase

Reference specific controls in change proposals:

```markdown
## Security Impact
- Implements: S0 input validation, A0 prompt sanitization.
- Controls from catalog: #1, #6, #82, #83.
```

### In Security Review Phase

Verify baseline compliance:

```markdown
## Baseline Verification
- S0: Complete.
- A0: Complete for AI features.
- V0: Partial; audit log pending.
- C0: N/A; not deployed to cloud.
```

## Baseline Checklist Template

Copy this to project documentation:

```markdown
# Security Baseline Compliance

## Project: [Name]
## Date: [Date]
## Reviewer: [Name]

### S0 - Base Security
- [ ] Authentication documented or N/A justified.
- [ ] Authorization enforced.
- [ ] Input validation centralized or consistently applied.
- [ ] Output encoding applied.
- [ ] Secrets secure.
- [ ] Secure transport documented.
- [ ] Errors handled safely.
- [ ] Dependencies scanned or reviewed.
- [ ] Logging structured.
- [ ] Abuse controls defined.

### A0 - AI Security (if applicable)
- [ ] Inputs scoped and validated.
- [ ] Prompt injection risks mitigated.
- [ ] Tool safety controls defined.
- [ ] Data boundaries enforced.
- [ ] Output controls defined.
- [ ] Cost controls implemented.
- [ ] AI audit logging defined.

### V0 - Audit (if applicable)
- [ ] Event logging defined.
- [ ] Integrity controls defined.
- [ ] Retention policy documented.
- [ ] Traceability links maintained.

### C0 - Cloud (if applicable)
- [ ] IAM least privilege.
- [ ] Keys and secrets managed securely.
- [ ] Network exposure documented.
- [ ] Central logging and alerting defined.
- [ ] Asset inventory maintained.
```
