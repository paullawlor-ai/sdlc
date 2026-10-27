# Phase 6: Deployment Workflow

Before release, require passing quality/security CI and a passing Completion
Gate for the tested snapshot. Follow
[security evidence freshness](../docs/framework/quality-and-security.md); expired
or failed scans and unresolved findings block release. Refresh source-bound
review and any required human sign-off after source changes.

## Overview

The Deployment phase prepares and executes the deployment of software to production or target environments.

## Agent

**Primary**: DevOps (`agents/devops.md`)

## Inputs

- Tested and security-reviewed code
- Deployment requirements
- Environment configuration
- Security baselines (especially C0)

## Activities

### 1. Review Deployment Requirements

Check:
- Target environment
- Required secrets and config
- Database migrations needed
- External dependencies
- Rollback requirements

### 2. Create/Update CI/CD Pipeline

Define pipeline stages:
1. Build
2. Test
3. Security scan
4. Deploy
5. Verify

### 3. Create Deployment Runbook

Use `templates/documents/deployment-runbook.md`:

```markdown
# Deployment Runbook - [Service]

## Pre-Deployment
- [ ] Tests passing
- [ ] Security review complete
- [ ] Secrets configured
- [ ] Runbook reviewed

## Deployment Steps
1. [Step with commands]
2. [Step with commands]

## Verification
- [ ] Health checks passing
- [ ] Smoke tests passing

## Rollback
1. [Rollback step]
2. [Rollback step]
```

### 4. Configure Monitoring

Set up:
- Health check endpoints
- Key metrics
- Alerting thresholds
- Dashboards

### 5. Execute Deployment

1. Pre-deployment checks
2. Execute deployment
3. Run verification
4. Monitor for issues

### 6. Report Completion

```markdown
## Deployment Complete

### Service
- Name: [service]
- Version: [version]
- Environment: [env]

### Status
- Health: [OK] Passing
- Smoke tests: [OK] Passing

### Artifacts
- Runbook: sdlc_artifacts/runbooks/[name].md
- CI/CD: [pipeline location]

### Ready for iteration.
```

## Outputs

| Output | Location |
|--------|----------|
| CI/CD config | `.github/workflows/` or similar |
| Deployment runbook | `sdlc_artifacts/runbooks/` |
| Monitoring config | As appropriate |

## Quality Checklist

Before completing this phase:

- [ ] CI/CD pipeline configured
- [ ] All tests passing in pipeline
- [ ] Security scans passing
- [ ] Deployment runbook created
- [ ] Rollback procedure documented
- [ ] Secrets configured securely
- [ ] Monitoring set up
- [ ] Health checks implemented

## GitHub Actions Security

Apply these controls whenever the project uses GitHub Actions (or any CI/CD platform with equivalent concepts).

### Pin action versions to SHAs

Tags are mutable - a compromised third-party action can silently change what a tag points to. Pin to an immutable commit SHA instead:

```yaml
# [X] Vulnerable - tag can be moved
- uses: actions/checkout@v4

# [OK] Safe - SHA is immutable
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

Find the SHA for any action at `https://github.com/<owner>/<action>/tags`.

### Declare minimal permissions per job

Default GitHub Actions permissions are too broad. Declare only what each job needs:

```yaml
permissions:
  contents: read        # default: read only

jobs:
  deploy:
    permissions:
      contents: read
      id-token: write   # only if using OIDC
```

Common scopes: `contents`, `id-token`, `pull-requests`, `packages`, `deployments`. Everything else should be absent (defaults to `none`).

### Use OIDC for cloud credentials - not long-lived secrets

```yaml
# [X] Long-lived secret stored in GitHub
env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}

# [OK] Short-lived credential via OIDC federation
- uses: aws-actions/configure-aws-credentials@...
  with:
    role-to-assume: arn:aws:iam::123456789:role/github-deploy
    aws-region: us-east-1
```

Configure OIDC trust on the cloud side scoped to the specific repo and branch.

### Never print secrets to logs

```yaml
# [X] Leaks the secret into the log
- run: echo "Token is ${{ secrets.API_TOKEN }}"

# [OK] GitHub masks registered secrets, but don't rely on it
- run: curl -H "Authorization: Bearer $TOKEN" https://api.example.com
  env:
    TOKEN: ${{ secrets.API_TOKEN }}
```

Register any derived secret values as step outputs using `::add-mask::` if they must be computed at runtime.

### Restrict which events can trigger sensitive jobs

```yaml
on:
  push:
    branches: [main]        # only main, not all branches
  pull_request:
    branches: [main]

# For PRs from forks, use pull_request (not pull_request_target)
# pull_request_target runs in the context of the base repo and has
# access to secrets - never use it with untrusted PR code.
```

### Add dependency and code scanning

```yaml
# In a separate security-scan job:
- name: Dependency review (blocks PRs with known-vulnerable deps)
  uses: actions/dependency-review-action@...   # pin to SHA

- name: CodeQL analysis
  uses: github/codeql-action/analyze@...       # pin to SHA
```

Enable these in GitHub Settings -> Code security -> Code scanning.

### Quality Checklist - GitHub Actions

- [ ] All `uses:` references pinned to commit SHAs
- [ ] `permissions:` block on every job (not just top-level)
- [ ] No long-lived cloud credentials stored as secrets (use OIDC)
- [ ] No secrets echoed to run steps or debug output
- [ ] `pull_request_target` not used for untrusted PRs
- [ ] Dependency review action enabled for PRs
- [ ] Branch protection requires CI to pass before merge

---

## Cloud Security (C0 Baseline)

For cloud deployments:

### IAM
- [ ] Least privilege service accounts
- [ ] No long-lived credentials
- [ ] Role-based access

### Secrets
- [ ] In KMS/secrets manager
- [ ] Not in environment variables directly
- [ ] Rotation strategy defined

### Network
- [ ] Private subnets
- [ ] No public admin ports
- [ ] Security groups configured

### Logging
- [ ] Central logging enabled
- [ ] Security alerts configured
- [ ] Audit trail for admin actions

## Deployment Checklist

```markdown
## Pre-Deployment
- [ ] CI passing
- [ ] Security review approved
- [ ] Change proposal approved
- [ ] Runbook ready
- [ ] Secrets configured
- [ ] Backup taken (if applicable)

## Deployment
- [ ] Deployment initiated
- [ ] No errors
- [ ] Health checks passing
- [ ] Smoke tests passing
- [ ] Logs normal

## Post-Deployment
- [ ] Stakeholders notified
- [ ] Monitoring verified
- [ ] Change status updated
```

## Rollback Procedures

### Stateless Services
1. Identify previous version
2. Deploy previous version
3. Verify health
4. Investigate

### With Database Changes
1. Reverse migration
2. Deploy previous app version
3. Verify data integrity

### Feature Flags
1. Disable flag
2. Verify reversion
3. Investigate
4. Re-enable when ready

## No Formal Approval Gate

Deployment proceeds after:
- All prior gates passed
- Runbook created
- Verification successful

If deployment fails:
```markdown
## Deployment Failed

### Issue
[Description]

### Rollback Status
[Rolled back / In progress / N/A]

### Next Steps
[Investigation needed]
```

## Phase Transition

**Next Phase**: Iterate

**Transition Trigger**: Successful deployment

**Handoff**:
```markdown
## Handoff: Deployment -> Iterate

### Deployment Summary
- Service: [name]
- Version: [version]
- Status: [OK] Successful

### Artifacts
- Runbook: [location]
- Dashboard: [link]

### Ready for iteration/feedback.
```

## Tips

1. **Automate Everything**: Manual = errors
2. **Test Rollback**: Untested rollback isn't reliable
3. **Monitor First**: Set up before needed
4. **Document Decisions**: Why this config?
5. **Keep Runbooks Current**: Update when things change

