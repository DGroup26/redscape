#!/usr/bin/env python3
import click
import os
from pathlib import Path

REDSCAPE_DIR = Path.home() / ".redscape"
REDSCAPE_DIR.mkdir(exist_ok=True)

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Redscape - Full Spectrum OSINT Platform"""
    pass

# Load commands
from redscape.commands import scrape
cli.add_command(scrape.scrape)

if __name__ == '__main__':
    cli()
