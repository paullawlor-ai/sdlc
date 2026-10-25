#!/usr/bin/env python3
"""Initialize a new project from a template.

Usage:
  python sdlc/scripts/init_project.py <template-name> [target-directory]

Available templates:
  - python-fastapi-ai    FastAPI service with LLM integration
  - python-chatbot       Conversational AI with RAG support
  - python-cli           Command-line tool

Examples:
  python sdlc/scripts/init_project.py python-fastapi-ai
  python sdlc/scripts/init_project.py python-chatbot ./my-chatbot
"""

import os
import shutil
import sys

# This script operates on the framework repository itself because project
# templates are framework assets. It copies a starter application into a target
# directory; the generated project's SDLC evidence will later live in
# `sdlc_artifacts/`.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(ROOT, "templates", "projects")

# Keep the allowlist explicit so a typo cannot accidentally copy an unexpected
# directory. Public users can run `--list` to discover these names.
AVAILABLE_TEMPLATES = [
    "python-fastapi-ai",
    "python-chatbot",
    "python-cli",
]


def list_templates():
    """Print the built-in starter templates and their short descriptions.

    Descriptions are taken from each template README's first markdown heading.
    This keeps the CLI output in sync with the template documentation.
    """
    print("Available templates:")
    for t in AVAILABLE_TEMPLATES:
        template_path = os.path.join(TEMPLATES_DIR, t)
        readme = os.path.join(template_path, "README.md")
        desc = "(no description)"
        if os.path.exists(readme):
            with open(readme, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line.startswith("#"):
                    desc = first_line.lstrip("# ")
        print(f"  - {t}: {desc}")


def copy_template(template_name: str, target_dir: str):
    """Copy one starter template into the requested target directory.

    The copy is intentionally shallow at the top level but recursive for
    directories. `dirs_exist_ok=True` allows users to initialise into an
    existing folder without deleting unrelated files.
    """
    template_path = os.path.join(TEMPLATES_DIR, template_name)

    # Fail fast with a friendly message rather than letting shutil raise a
    # lower-level file error.
    if not os.path.exists(template_path):
        print(f"Error: Template '{template_name}' not found.")
        print(f"Available templates: {', '.join(AVAILABLE_TEMPLATES)}")
        sys.exit(1)

    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)

    # Copy template files
    for item in os.listdir(template_path):
        src = os.path.join(template_path, item)
        dst = os.path.join(target_dir, item)

        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)

    print(f"Initialized project from template: {template_name}")
    print(f"Target directory: {target_dir}")
    print()
    print("Next steps:")
    print("  1. From the project root, run: python sdlc/scripts/setup_project.py")
    print("  2. Run: python sdlc/scripts/verify_setup.py")
    print("  3. Add your requirements to sdlc_artifacts/requirements/")
    print("  4. Open in Cursor (or your AI assistant)")
    print("  5. Run: Read sdlc/prompts/bootstrap.md and begin")


def main():
    # No arguments means "show help and available templates"; this makes the
    # script discoverable for people exploring the public repository.
    if len(sys.argv) < 2:
        print(__doc__)
        print()
        list_templates()
        sys.exit(0)

    template_name = sys.argv[1]

    if template_name in ["--list", "-l"]:
        list_templates()
        sys.exit(0)

    # Only allow known templates. This prevents surprising copies from arbitrary
    # sibling directories under templates/projects.
    if template_name not in AVAILABLE_TEMPLATES:
        print(f"Error: Unknown template '{template_name}'")
        list_templates()
        sys.exit(1)

    # Determine target directory
    if len(sys.argv) >= 3:
        target_dir = sys.argv[2]
    else:
        # Default to the framework root for convenience when someone is using
        # this repository as a starting point rather than as an embedded tool.
        target_dir = ROOT  # Initialize in framework root

    target_dir = os.path.abspath(target_dir)

    copy_template(template_name, target_dir)


if __name__ == "__main__":
    main()
