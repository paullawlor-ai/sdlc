"""Shared path helpers for framework scripts.

The framework has two important roots:

1. The framework root (`sdlc/`), which contains reusable templates, prompts,
   workflows, and scripts.
2. The artifact root (`sdlc_artifacts/` by default), which belongs to the host
   project and stores generated requirements, ADRs, change proposals, reviews,
   and STATE.md.

Keeping this path logic in one small module prevents every script from making
slightly different assumptions about where project evidence should live.
"""
import os
from pathlib import Path


# `__file__` is <framework>/scripts/_paths.py, so parents[1] is the framework
# directory itself. This works whether the framework is cloned directly or
# copied into a host project as `sdlc/`.
FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]


def _is_relative_to(path: Path, parent: Path) -> bool:
    """Return True when path is inside parent.

    `Path.is_relative_to` is only available on newer Python versions. Keeping a
    tiny helper here lets the framework scripts stay friendly to older 3.x
    environments that teams may already have installed.
    """
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def project_root() -> Path:
    """Return the project that is using the framework.

    In normal use the framework sits in `<project>/sdlc`, so the host project
    root is the parent directory. If somebody opens the framework repository
    directly, the framework root is also the project root.
    """
    configured = os.environ.get("SDLC_PROJECT_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()

    cwd = Path.cwd().resolve()

    # When invoked as `python sdlc/scripts/...` from a host project root, use
    # the caller's project directory. This is the normal embedded-framework path.
    if (cwd / "sdlc").resolve() == FRAMEWORK_ROOT:
        return cwd

    if FRAMEWORK_ROOT.name == "sdlc":
        # A standalone framework checkout such as C:\dev\sdlc has its own git
        # metadata and should write artifacts inside the framework repo.
        if (FRAMEWORK_ROOT / ".git").exists():
            return FRAMEWORK_ROOT

        # If running from inside the embedded framework folder, the host project
        # is still the parent directory.
        if _is_relative_to(cwd, FRAMEWORK_ROOT):
            return FRAMEWORK_ROOT.parent

        return FRAMEWORK_ROOT.parent

    return FRAMEWORK_ROOT


def artifacts_root() -> Path:
    """Return the SDLC artifact root for the current project.

    Defaults to <project>/sdlc_artifacts. Set SDLC_ARTIFACTS_DIR to override.
    Relative overrides are resolved from the host project root.
    """
    # The environment override is useful for tests, experiments, or teams that
    # want a different evidence directory name without editing the framework.
    configured = os.environ.get("SDLC_ARTIFACTS_DIR", "sdlc_artifacts")
    configured_path = Path(configured)

    # Absolute paths are respected as-is; relative paths are intentionally
    # anchored to the host project rather than to the caller's current shell
    # directory. That makes script behavior predictable from any working dir.
    if configured_path.is_absolute():
        return configured_path
    return project_root() / configured_path
