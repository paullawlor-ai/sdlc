from click.testing import CliRunner

from app.cli import cli


def test_cli_help_starts() -> None:
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Commands" in result.output
