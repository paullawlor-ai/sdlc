# Contributing

Use Python 3.10 or newer and run all checks before submitting a change:

```bash
python -m unittest discover -s tests -v
python scripts/generate_adapters.py --check
python scripts/sdlc.py check
python -m compileall -q scripts tests templates/projects
```

Core policy changes belong in `policy/sdlc-policy.json`; regenerate adapters
with `python scripts/generate_adapters.py`. Do not edit generated adapters by hand.

Add regression tests for behavioural fixes. Major changes to policy, artifact
schema, or installation require an ADR. Keep setup dependencies in the Python
standard library. A redistribution licence must be selected by the repository
owner before publishing a public package or release archive.
