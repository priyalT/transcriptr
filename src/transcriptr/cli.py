from pathlib import Path

import rich_click as click

from transcriptr.config import ConfigManager


@click.group()
def cli():
    """Transcriptr CLI."""


@cli.group()
def config():
    """Configuration commands."""


@config.command()
@click.argument("output", type=click.Path(path_type=Path))
def init(output: Path):
    """Create a template configuration file."""
    ConfigManager.init(output)
    click.echo(f"YAML file saved to {output}")


@config.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def check(path: Path):
    """Validate a configuration file."""
    ConfigManager.check(path)


if __name__ == "__main__":
    cli()
