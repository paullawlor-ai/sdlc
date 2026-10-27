# Python CLI Tool Template

A minimal Click command group with Rich terminal output and a smoke test.
The example command greets a supplied name. Configuration management, structured
logging, authentication, and file operations are left to the host application.

## Quick Start

From the host project root:

```bash
python sdlc/scripts/init_project.py python-cli
python -m pip install -r requirements.txt
python -m app.cli --help
python -m app.cli example World
```

## Project Structure

```text
app/
  __init__.py
  cli.py
  commands/
    __init__.py
    example.py
tests/
  __init__.py
  test_smoke.py
requirements.txt
requirements-dev.txt
ruff.toml
README.md
```

## Quality Checks and Next Steps

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check app tests
python -m ruff format --check app tests
python -m pytest -q
```

Add requirements to `sdlc_artifacts/requirements/` and start with
`Read sdlc/prompts/bootstrap.md and begin`. Implement applicable S0 controls for
the actual commands and data handled by your application. From the host root,
run `python sdlc/scripts/security_scan.py` and link its report in required
reviews; see `sdlc/docs/framework/quality-and-security.md` for scope and freshness.
