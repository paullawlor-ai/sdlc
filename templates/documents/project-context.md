# Project Context

> **Owner**: Architect Agent  
> **Purpose**: Project-specific context that all agents read at startup to specialise their behaviour. Created at bootstrap; updated whenever stack decisions change.

---

## Project Identity

**Name**: [Project name]  
**One-line description**: [What does this software do?]  
**Primary users**: [Who will use it?]  
**Current status**: [e.g. Greenfield / Active development / Maintenance]

---

## Technology Stack

### Languages
- **Primary**: [e.g. Python 3.11 / TypeScript / Go / Java / Swift]
- **Secondary**: [e.g. TypeScript for frontend, SQL, Bash for scripts]

### Frameworks & Libraries
- **Web / API**: [e.g. FastAPI, Django, Express, Rails, ASP.NET, none]
- **Frontend / UI**: [e.g. React, Vue, Svelte, native mobile, CLI, none]
- **Data / ORM**: [e.g. SQLAlchemy 2.0 async, Prisma, Entity Framework, none]
- **Testing**: [e.g. pytest + pytest-asyncio, Jest, JUnit, Playwright]
- **Validation**: [e.g. Pydantic v2, Zod, JSON Schema, framework validators]
- **Other key libraries**: [list]

### Infrastructure
- **Database**: [e.g. PostgreSQL 16 / SQLite for dev]
- **Object storage**: [e.g. AWS S3 / MinIO]
- **Cache / Queue**: [e.g. Redis / DB-backed polling]
- **Container runtime**: [e.g. Podman / Docker]
- **Orchestration**: [e.g. Kubernetes / systemd Quadlets / none]
- **CI/CD**: [e.g. GitHub Actions]
- **Cloud provider**: [e.g. AWS / Azure / GCP / Self-hosted]
- **Client platforms**: [e.g. Web, iOS, Android, desktop, CLI, library]

---

## Security Profile

Applicable baselines (tick all that apply):

- [x] **S0** - Base security (always)
- [ ] **A0** - AI/LLM features present
- [ ] **V0** - Audit / evidence / compliance required
- [ ] **C0** - Cloud deployment with IAM / KMS

Additional constraints:
- [e.g. "EU AI Act compliance required for evaluation outputs"]
- [e.g. "No PII may be stored unencrypted"]

---

## Coding Conventions

### Style
- [e.g. "ruff for linting and formatting, line length 100"]
- [e.g. "Strict type hints on all functions (mypy)"]
- [e.g. "No comments unless the WHY is non-obvious"]

### Patterns
- [e.g. "Pydantic BaseSettings for all config; MYAPP_ env var prefix"]
- [e.g. "FastAPI dependency injection for auth and DB sessions"]
- [e.g. "Async throughout - no blocking I/O on the main thread"]
- [e.g. "Structured logging with correlation IDs on every log line"]

### Python Environment (Python projects only)
- All packages installed into `.venv/` at the project root — never the global Python environment
- Create if absent: `python -m venv .venv`
- Activate before any install:
  - bash/zsh: `source .venv/Scripts/activate` (Windows) or `source .venv/bin/activate` (Unix)
  - PowerShell: `.venv\Scripts\Activate.ps1`
- `.venv/` is gitignored — never committed

### Testing
- [e.g. "pytest with asyncio_mode=auto"]
- [e.g. "Integration tests marked @pytest.mark.integration - require Docker"]
- [e.g. "Test files mirror source structure in tests/"]
- [e.g. "Run single test: pytest tests/test_foo.py::test_bar"]
- [e.g. "Activate .venv before running pytest: source .venv/Scripts/activate && pytest"]

### File / Module Organisation
- [e.g. "One module per domain concept; no circular imports"]
- [e.g. "Config always loaded via get_settings() - never instantiate Settings directly"]

---

## Key Constraints

Things all agents must remember when proposing solutions:

- [e.g. "No synchronous database calls - everything is async SQLAlchemy"]
- [e.g. "Python 3.11+ only - f-strings and match statements are fine"]
- [e.g. "The evidence hash chain requires sequential writes - do not parallelise evidence writes"]
- [e.g. "Safety evaluators (Presidio, Detoxify) are optional heavy deps - never import unconditionally"]

---

## Glossary

Key terms that have specific meanings in this project:

| Term | Meaning |
|------|---------|
| [Term] | [Definition] |
| [Term] | [Definition] |

---

## Agent-Specific Notes

### For Developer Agent
- [Stack-specific guidance, e.g. "Always use asyncpg driver for PostgreSQL, never psycopg2 in async context"]

### For Tester Agent
- [e.g. "Use respx for mocking httpx calls; testcontainers for integration DB"]

### For Security Reviewer Agent
- [e.g. "Also check against OWASP LLM Top 10 - A0 baseline applies"]

### For Architect Agent
- [e.g. "All new persistence requires a new Alembic revision - no schema changes in code"]

---

*Last updated by Architect Agent on [YYYY-MM-DD]*
