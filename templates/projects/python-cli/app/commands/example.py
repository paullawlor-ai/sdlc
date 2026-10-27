"""Example command."""

import click
from rich.console import Console

console = Console()


@click.command()
@click.argument("name")
def example(name: str):
    """Example command that greets someone."""
    console.print(f"Hello, [bold blue]{name}[/bold blue]!")
