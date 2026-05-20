# Python CLI Tool Template

A template for building command-line tools with security best practices.

## Features

- Click-based CLI interface
- Structured logging
- Configuration management
- Security baseline (S0)
- Testing setup

## Quick Start

1. Initialize from this template:
   ```bash
   python sdlc/scripts/init_project.py python-cli
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the CLI:
   ```bash
   python -m app.cli --help
   ```

## Project Structure

```
+-- app/
|   +-- __init__.py
|   +-- cli.py               # CLI entry point
|   +-- config.py            # Configuration
|   +-- commands/            # CLI commands
|   |   +-- __init__.py
|   |   +-- example.py
|   +-- utils/
|       +-- __init__.py
|       +-- logging.py
+-- tests/
+-- requirements.txt
+-- README.md
```

## Security Baseline

This template implements S0 baseline:
- Input validation
- Secure logging (no secrets)
- Safe file operations

## Next Steps

1. Add your requirements to `sdlc_artifacts/requirements/`
2. Run the bootstrap prompt in Cursor
3. Follow the SDLC phases to build your CLI tool

