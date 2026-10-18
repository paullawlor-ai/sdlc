#!/usr/bin/env python3
"""Generate compact assistant adapters from the canonical SDLC policy."""
from __future__ import annotations

import argparse
from pathlib import Path

from _paths import FRAMEWORK_ROOT
from _policy import load_policy

GENERATED_MARKER = "<!-- Generated from policy/sdlc-policy.json; do not edit directly. -->"


def common_body(policy: dict) -> str:
    rules = "\n".join(f"- **{key}** {value}" for key, value in policy["rules"].items())
    classes = "\n".join(
        f"- **{name}**: {item['description']}"
        for name, item in policy["change_classes"].items()
    )
    return f"""{GENERATED_MARKER}
# Agentic SDLC {policy['framework_version']}

Read `sdlc_artifacts/STATE.md` and `sdlc_artifacts/context.md` when present.
For resumed work, prefer `python sdlc/scripts/sdlc.py context` over scanning all
framework documents. Do not edit `sdlc/` unless maintaining the framework.

## Change Classification

{classes}

Use the project profile from `sdlc_artifacts/config.json`, or
`{policy['default_profile']}` when absent. Run
`python sdlc/scripts/sdlc.py gate implementation` before product-code edits.

## Rules

{rules}

Human approval must be present in the artifact; verbal approval is insufficient.
When a role is requested, read only its matching file under `sdlc/agents/`.
Use `python sdlc/scripts/sdlc.py next` for the next permitted action.
"""


def outputs(policy: dict) -> dict[Path, str]:
    common = common_body(policy)
    cursor_core = f"""---
alwaysApply: true
---
{common}
"""
    cursor_gate = f"""---
alwaysApply: true
---
{GENERATED_MARKER}
# SDLC Gates

Before product-code edits run:

```text
python sdlc/scripts/sdlc.py gate implementation
```

Exit code 0 permits the edit. Exit code 2 means stop and report the command's
blocker. Assistants must not alter human-only approval fields. Completion uses:

```text
python sdlc/scripts/sdlc.py gate completion
```

The canonical policy is `sdlc/policy/sdlc-policy.json`. Detailed implementation
and completion procedures are loaded from `sdlc/workflows/03-implementation.md`
only when a gate reports that they are needed.
"""
    cursor_agents = f"""---
description: Portable SDLC role selection
globs: ["**/*"]
alwaysApply: false
---
{GENERATED_MARKER}
# Roles

Role definitions are under `sdlc/agents/`. Read only the role needed for the
current action. "Invoke" means spawn a specialist when supported, otherwise
adopt that role in the current session. Record handoffs in `STATE.md`.
"""
    cursor_security = f"""---
description: Contextual SDLC security baselines
globs: ["**/*"]
alwaysApply: false
---
{GENERATED_MARKER}
# Security Baselines

- S0 applies to all software.
- A0 applies to AI or LLM features.
- V0 applies to audit or compliance evidence.
- C0 applies to cloud deployment.

Load `sdlc/docs/security/security-baselines.md` and relevant catalogs only when
the active change needs those baselines.
"""
    copilot_scoped = f"""---
applyTo: "**"
---
{common}
"""
    return {
        Path("codex/AGENTS.md"): common,
        Path("copilot/copilot-instructions.md"): common,
        Path("copilot/instructions/sdlc.instructions.md"): copilot_scoped,
        Path("cursor/rules/core.mdc"): cursor_core,
        Path("cursor/rules/implementation-gate.mdc"): cursor_gate,
        Path("cursor/rules/agents.mdc"): cursor_agents,
        Path("cursor/rules/security.mdc"): cursor_security,
    }


def generate(check: bool = False) -> list[str]:
    policy = load_policy()
    adapters = FRAMEWORK_ROOT / "adapters"
    messages: list[str] = []
    stale: list[str] = []
    for relative, content in outputs(policy).items():
        destination = adapters / relative
        rendered = content.rstrip() + "\n"
        current = destination.read_text(encoding="utf-8") if destination.exists() else None
        if current == rendered:
            messages.append(f"OK: {destination.relative_to(FRAMEWORK_ROOT)}")
            continue
        if check:
            stale.append(str(destination.relative_to(FRAMEWORK_ROOT)))
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
        messages.append(f"Generated: {destination.relative_to(FRAMEWORK_ROOT)}")
    if stale:
        raise SystemExit("Generated adapters are stale: " + ", ".join(stale))
    return messages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    print("\n".join(generate(check=args.check)))


if __name__ == "__main__":
    main()
