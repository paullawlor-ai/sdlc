# Contributing

Use Python 3.10 or newer and run all checks before submitting a change:

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check scripts tests templates/projects
python -m ruff format --check scripts tests templates/projects
python -m unittest discover -s tests -v
python scripts/release_check.py
python scripts/generate_adapters.py --check
python scripts/sdlc.py check --strict
python -m compileall -q scripts tests templates/projects
python scripts/security_scan.py
```

The security scan needs network access for dependency advisories. Run each
starter's smoke suite from its project directory. See
`docs/framework/quality-and-security.md` for scope and failure handling and
`docs/framework/releasing.md` for release/assistant acceptance evidence.

Core policy changes belong in `policy/sdlc-policy.json`; regenerate adapters
with `python scripts/generate_adapters.py`. Do not edit generated adapters by hand.

Add regression tests for behavioural fixes. Major changes to policy, artifact
schema, or installation require an ADR. Keep setup dependencies in the Python
standard library. A redistribution licence must be selected by the repository
owner before publishing a public package or release archive.
