# OWASP Top 10 (Web Applications) - Summary

Use this as a *risk vocabulary* when writing change docs and doing reviews.

## The Top 10 Categories

| # | Category | Description |
|---|----------|-------------|
| A01 | Broken Access Control | Failures to enforce proper access restrictions |
| A02 | Cryptographic Failures | Weak or missing encryption for sensitive data |
| A03 | Injection | SQL, NoSQL, OS command, LDAP injection attacks |
| A04 | Insecure Design | Missing security controls in architecture |
| A05 | Security Misconfiguration | Insecure default configs, incomplete setups |
| A06 | Vulnerable Components | Using components with known vulnerabilities |
| A07 | Auth Failures | Identification and authentication weaknesses |
| A08 | Integrity Failures | Software and data integrity compromises |
| A09 | Logging Failures | Insufficient logging and monitoring |
| A10 | SSRF | Server-Side Request Forgery attacks |

## How to Use in Change Docs

When proposing a change, map risks to these categories:
```markdown
## Security impact
- Risks reduced: A01 (adding object-level authorization)
- New risks introduced: None
- OWASP mapping: A01-Broken Access Control
```

## How to Use in Reviews

During security review, check the change against each applicable category:
- [ ] A01: Are access controls enforced on every affected endpoint?
- [ ] A02: Is sensitive data encrypted in transit and at rest?
- [ ] A03: Are inputs validated and outputs encoded?
- [ ] A04: Is the design secure by default?
- [ ] A05: Are configurations secure and complete?
- [ ] A06: Are dependencies up to date and scanned?
- [ ] A07: Is authentication robust?
- [ ] A08: Are integrity checks in place?
- [ ] A09: Are security events logged?
- [ ] A10: Are outbound requests validated?

Keep the full OWASP Top 10 reference in `docs/security/owasp/`.

