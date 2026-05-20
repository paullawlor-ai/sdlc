# Security Review Phase Prompt

Focus on security analysis and verification.

---

## Instructions

```
Act as the Security Reviewer agent.
Read agents/security-reviewer.md.
Read workflows/05-security-review.md.
Read catalogs/owasp-secure-coding-100.md.
Read docs/security/security-baselines.md.

Review the implementation against OWASP guidelines and security baselines.
```

## Quick Commands

### Full Security Review
```
Act as Security Reviewer. Read agents/security-reviewer.md. Perform a security review of sdlc_artifacts/changes/[NNNN]-[name].md against OWASP guidelines.
```

### Baseline Verification
```
Act as Security Reviewer. Verify the implementation meets the S0 (and A0 if applicable) security baselines.
```

### Quick Security Check
```
Act as Security Reviewer. Do a quick security check on [file or feature]. Focus on input validation, auth, and injection risks.
```

