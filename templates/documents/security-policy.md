# Security Policy

<!-- Copy this file to your project root as SECURITY.md and fill in the placeholders. -->

## Supported Versions

| Version | Supported |
|---------|-----------|
| [x.y.z - latest] | [OK] Yes |
| [x.y.z-1 - previous] | [WARN] Critical fixes only |
| Older | [X] No |

<!-- If you don't version your software, replace the table with a statement like:
"Security fixes are applied to the main branch only. Deploy from main." -->

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report privately using one of the following:

- **GitHub Security Advisories** (preferred): [Submit a draft advisory](https://github.com/[YOUR-ORG]/[YOUR-REPO]/security/advisories/new)
- **Email**: [security@your-domain.com] - use PGP key [KEY-ID] if you require encrypted communication ([public key link])

Please include in your report:
- A clear description of the vulnerability
- Steps to reproduce (proof of concept if available)
- Affected versions
- Potential impact (confidentiality, integrity, availability)
- Any suggested mitigations or patches

## Response Timeline

| Milestone | Target |
|-----------|--------|
| Acknowledgement | Within 48 hours |
| Initial triage and severity rating | Within 5 business days |
| Fix for Critical/High severity | Within 14 days |
| Fix for Medium severity | Within 30 days |
| Fix for Low severity | Next scheduled release |
| Public disclosure | After fix is released, coordinated with reporter |

If a fix will take longer than these targets, we will communicate the delay and reasoning directly to the reporter.

## What to Expect

1. We will acknowledge your report promptly
2. We will keep you informed of progress
3. We will credit you in the release notes and/or CVE unless you prefer anonymity
4. We will coordinate public disclosure timing with you
5. We do not offer a bug bounty program at this time

## Severity Ratings

We use CVSS v3.1 for scoring. Informal guidance:

| Severity | Examples |
|----------|---------|
| **Critical** | Unauthenticated RCE, authentication bypass, mass data exposure |
| **High** | Authenticated RCE, privilege escalation, significant data leakage |
| **Medium** | CSRF, stored XSS, indirect data exposure, broken access control with limited impact |
| **Low** | Reflected XSS (self-only), minor information disclosure, hardening gaps |

## Scope

### In Scope

- All endpoints and services in the production environment (`[your-domain.com]`)
- Authentication and authorisation logic
- Data handling and storage
- Third-party integrations that handle user data
- Infrastructure accessible from the public internet

### Out of Scope

The following will not be accepted as valid vulnerabilities:

- Denial of service attacks (application or infrastructure layer)
- Social engineering or phishing of staff or users
- Physical attacks against infrastructure
- Issues in third-party services outside our control
- Findings from automated scanners without demonstrated exploit potential
- Missing security headers that have no practical exploit in our context
- Rate limiting issues on non-sensitive endpoints
- Clickjacking on pages without sensitive actions
- Self-XSS (requires the victim to execute the payload themselves)
- Issues requiring a compromised user device

## Safe Harbour

We consider security research conducted under this policy to be authorised. We will not pursue legal action against researchers who:

- Report vulnerabilities promptly and in good faith
- Do not access, modify, or exfiltrate data beyond what is necessary to demonstrate the vulnerability
- Do not degrade the service for other users
- Do not publicly disclose before a fix is available

---
*Template: `templates/documents/security-policy.md` - copy to your project root as `SECURITY.md`*
