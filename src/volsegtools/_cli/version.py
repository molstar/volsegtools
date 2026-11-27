"""
Informs the user about the current version of used volsegtools.
"""

import typer

import volsegtools as vst

app = typer.Typer()


@app.command()
def version():
    print(f"Version: {vst.__version__}")
