"""
The main entrypoint for the volsegtools application.

It is aggregating all other relevant commands (sub-applications).
"""

import typer

from .version import app as version_subapp

app = typer.Typer()

app.add_typer(version_subapp)

if __name__ == "__main__":
    app()
