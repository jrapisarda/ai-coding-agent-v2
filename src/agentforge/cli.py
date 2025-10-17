"""Command line interface for AgentForge."""

from __future__ import annotations

import asyncio
from pathlib import Path

import click

from .agents import agents
from .orchestrator import AgentRunner


@click.group()
def app() -> None:
    """AgentForge orchestration commands."""


@app.command()
@click.argument("spec", type=click.Path(exists=True, path_type=Path))
@click.argument("output", type=click.Path(path_type=Path))
def run(spec: Path, output: Path) -> None:
    """Execute the full multi-agent pipeline."""

    runner = AgentRunner(agents=agents)
    asyncio.run(runner.run(spec_path=spec, output_dir=output))
    click.echo(f"Pipeline completed. Artifacts available in {output}")
