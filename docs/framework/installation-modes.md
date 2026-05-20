# Installation Modes

The framework supports several installation styles. Pick one mode per project
and use its paths consistently.

## Mode Summary

| Mode | Layout | Best for | Prompt paths | Script paths |
|------|--------|----------|--------------|--------------|
| Root template | `project/` contains `agents/`, `prompts/`, `scripts/` | New projects started from this repo | `prompts/bootstrap.md` | `python scripts/status.py` |
| Embedded framework | `project/sdlc/` contains the framework | Existing projects adopting the framework | `sdlc/prompts/onboard.md` | `python sdlc/scripts/status.py` |
| Git submodule | `project/sdlc/` is a submodule | Teams that want controlled framework updates | `sdlc/prompts/...` | `python sdlc/scripts/...` |
| Local ignored framework | `project/sdlc/` is gitignored | Teams that commit artifacts but not framework runtime | `sdlc/prompts/...` | `python sdlc/scripts/...` |

## Root Template Mode

Use this when the framework repository is the project starting point.

```text
project/
  agents/
  prompts/
  scripts/
  templates/
  workflows/
  sdlc_artifacts/
```

Start a new project:

```text
Read prompts/bootstrap.md and begin
```

Run scripts:

```bash
python scripts/status.py
python scripts/new_state.py
python scripts/new_change.py "description"
```

## Embedded Framework Mode

Use this when an existing project adopts the framework under `sdlc/`.

```text
project/
  app/
  tests/
  package.json
  sdlc/
    agents/
    prompts/
    scripts/
  sdlc_artifacts/
```

Adopt the project:

```text
Read sdlc/prompts/onboard.md and begin
```

Run scripts from the host project root:

```bash
python sdlc/scripts/status.py
python sdlc/scripts/new_state.py
python sdlc/scripts/new_change.py "description"
```

## What To Commit

In most team projects, commit:

```text
sdlc_artifacts/
AGENTS.md or assistant-specific adapter files
```

Choose whether to commit `sdlc/`:

- Commit it when you want the framework version pinned in the repository.
- Ignore it when each developer or automation environment provides the framework runtime separately.
- Use a submodule when you want explicit framework versioning without copying files.

## Artifact Location

Generated project evidence belongs in `sdlc_artifacts/` at the host project
root, not inside the framework runtime.

The scripts resolve this automatically in normal layouts. Set
`SDLC_ARTIFACTS_DIR` only when a project intentionally stores artifacts
elsewhere.

## Assistant Rule Of Thumb

If you see `sdlc/prompts/...`, work from the host project root.
If you see `prompts/...`, the framework is the project root.
