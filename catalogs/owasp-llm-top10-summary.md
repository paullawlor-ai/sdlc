# OWASP Top 10 for LLM Applications - Summary

Use this when building AI/LLM features. Map risks in change docs and reviews.

## The Top 10 LLM Risks

| # | Risk | Description |
|---|------|-------------|
| LLM01 | Prompt Injection | Malicious inputs hijacking model behavior |
| LLM02 | Insecure Output Handling | Model output used unsafely as code/commands |
| LLM03 | Training Data Poisoning | Compromised training or fine-tuning data |
| LLM04 | Model Denial of Service | Cost and latency attacks via excessive usage |
| LLM05 | Supply Chain Vulnerabilities | Risks in models, datasets, plugins, dependencies |
| LLM06 | Sensitive Information Disclosure | Context leakage, PII exposure |
| LLM07 | Insecure Plugin Design | Over-permissive tool/plugin integrations |
| LLM08 | Excessive Agency | Model given too-broad permissions |
| LLM09 | Overreliance | Unsafe decisions based on hallucinations |
| LLM10 | Model Theft | Extraction or theft of model weights |

## Required Controls for AI Features

### LLM01 - Prompt Injection Defense
- Separate system prompts from user inputs
- Validate and sanitize user inputs before LLM processing
- Use input/output filtering for known attack patterns
- Implement prompt templates with strict variable escaping

### LLM02 - Output Safety
- Treat all model output as untrusted
- Never execute model output as code without sandboxing
- Validate output against expected schemas
- Apply output encoding before rendering

### LLM04 - Cost/DoS Controls
- Set token limits per request and per user
- Implement rate limiting for LLM endpoints
- Set request timeouts
- Monitor and alert on usage anomalies

### LLM06 - Data Protection
- Implement tenant-scoped retrieval boundaries
- Redact sensitive data before model input
- Apply output policy checks (PII detection, redaction)
- Log AI actions without storing sensitive prompts

### LLM07/LLM08 - Tool Safety
- Use allowlists for permitted tools/actions
- Validate all tool parameters strictly
- Implement least-privilege for tool permissions
- Require human approval for high-risk actions

## How to Use in Change Docs

```markdown
## Security impact
- Risks reduced: LLM01 (adding input sanitization)
- New risks introduced: LLM04 (new LLM endpoint needs rate limiting)
- OWASP LLM mapping: LLM01-Prompt Injection, LLM04-Model DoS
```

## A0 Baseline Checklist

For any AI/LLM feature, ensure:
- [ ] Model output treated as untrusted
- [ ] Prompt/tool injection controls in place
- [ ] Retrieval boundaries enforced (tenant/role scoped)
- [ ] Output controls implemented (redaction, policy checks)
- [ ] Cost/DoS controls configured (token limits, timeouts)

Keep the full OWASP LLM Top 10 reference in `docs/security/owasp/`.

