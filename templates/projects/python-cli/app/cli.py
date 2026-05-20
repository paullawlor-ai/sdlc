"""CLI entry point."""

import click
from rich.console import Console

from app.commands.example import example

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """CLI tool description."""
    pass


cli.add_command(example)


if __name__ == "__main__":
    cli()

