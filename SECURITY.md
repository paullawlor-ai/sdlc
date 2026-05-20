# Security Policy

> **Host projects:** This file is for the framework GitHub repository only. Do not copy it into host projects. Use `templates/documents/security-policy.md` to create a `SECURITY.md` for **your** product at the project root.

## Scope

This policy covers the **Agentic SDLC Framework** repository - its Python scripts, agent definitions, workflow documents, and templates. It does not cover projects that have adopted this framework; those projects maintain their own security policies (see `templates/documents/security-policy.md` for a template).

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest commit on `main` | [OK] Yes |
| Older commits | [X] No - update to latest |

This is a living framework, not a versioned library. Security improvements are applied to `main` and are not backported.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities privately via GitHub's [Security Advisories](https://github.com/inabubblewithyou/sdlc/security/advisories/new) feature, or by emailing the maintainer directly (see the GitHub profile for contact details).

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested mitigations

## What to Expect

| Timeline | Action |
|----------|--------|
| Within 48 hours | Acknowledgement of your report |
| Within 7 days | Initial assessment and severity rating |
| Within 30 days | Fix released (critical/high) or scheduled (medium/low) |

You will be credited in the fix commit unless you prefer to remain anonymous.

## What Counts as a Vulnerability Here

Given that this repo is documentation and scripts, relevant vulnerabilities include:

- **Python scripts** (`scripts/`): path traversal, command injection, or unsafe file operations
- **Security guidance** in agents, workflows, or catalogs that is demonstrably incorrect and would lead adopters to build insecure systems
- **Template documents** that contain insecure defaults or advice

## Out of Scope

- Theoretical issues with no practical exploit path
- Issues in projects that have adopted this framework (report those to the relevant project)
- GitHub Actions supply-chain risks in upstream framework CI (not shipped in host `sdlc/` copies)
