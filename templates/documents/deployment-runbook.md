# Deployment Runbook - <service/application name>

## Overview
Brief description of what is being deployed.

## Pre-Deployment Checklist

### Code Ready
- [ ] All tests passing
- [ ] Security review completed
- [ ] Change proposal approved
- [ ] Code merged to deploy branch

### Environment Ready
- [ ] Target environment available
- [ ] Required secrets/configs in place
- [ ] Database migrations prepared (if applicable)
- [ ] Dependencies available

### Team Ready
- [ ] Deployment owner identified: 
- [ ] Rollback owner identified: 
- [ ] On-call notified (if applicable)

## Deployment Steps

### Step 1: Pre-Deployment Verification
```bash
# Verify current state
# Example commands
```

- [ ] Current version noted: 
- [ ] Health checks passing

### Step 2: Database Migration (if applicable)
```bash
# Migration commands
```

- [ ] Migration completed
- [ ] Migration verified

### Step 3: Deploy Application
```bash
# Deployment commands
```

- [ ] Deployment initiated
- [ ] Deployment completed

### Step 4: Post-Deployment Verification
```bash
# Verification commands
```

- [ ] Health checks passing
- [ ] Smoke tests passing
- [ ] Logs showing normal activity

### Step 5: Monitoring Check
- [ ] No error spikes in logs
- [ ] Latency within expected range
- [ ] No alerts triggered

## Rollback Procedure

### Rollback Triggers
Initiate rollback if:
- Health checks fail after deployment
- Error rate exceeds [threshold]
- Critical functionality broken
- Security issue discovered

### Rollback Steps

#### Step R1: Initiate Rollback
```bash
# Rollback commands
```

- [ ] Previous version: 
- [ ] Rollback initiated

#### Step R2: Database Rollback (if applicable)
```bash
# Rollback migration commands
```

- [ ] Database rolled back

#### Step R3: Verify Rollback
```bash
# Verification commands
```

- [ ] Previous version running
- [ ] Health checks passing
- [ ] Functionality restored

### Rollback Side Effects
Document any side effects of rollback:
- 
- 

## Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| | | |

### Feature Flags
| Flag | Description | Default |
|------|-------------|---------|
| | | |

### Secrets
| Secret | Location | Purpose |
|--------|----------|---------|
| | | |

## Monitoring & Alerts

### Key Metrics
- Metric 1:
- Metric 2:

### Alerts to Watch
- Alert 1:
- Alert 2:

### Dashboards
- Link to dashboard:

## Troubleshooting

### Common Issues

#### Issue 1: <description>
**Symptoms**: 
**Cause**: 
**Resolution**: 

#### Issue 2: <description>
**Symptoms**: 
**Cause**: 
**Resolution**: 

## Contact Information
- **Deployment Owner**: 
- **On-Call**: 
- **Escalation**: 

## Change History
| Date | Version | Change | Author |
|------|---------|--------|--------|
| | | | |

---
*Template: `templates/documents/deployment-runbook.md`*

