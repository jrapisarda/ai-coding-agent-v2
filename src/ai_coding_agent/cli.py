"""Command line interface for the AI Coding Agent."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import AgentRuntimeSettings, WorkspaceConfig
from .plan import AgentProjectPlan
from .agents.pipeline import MultiAgentPipeline

console = Console()
app = typer.Typer(help="AI Coding Agent CLI using OpenAI Agents SDK")


def _resolve_docs(paths: tuple[Path, ...]) -> list[Path]:
    docs: list[Path] = []
    for path in paths:
        if path.is_dir():
            docs.extend(sorted(path.glob("**/*")))
        elif path.exists():
            docs.append(path)
    return docs


@app.command()
def run(
    target_path: Path = typer.Argument(..., help="Workspace directory for generated code"),
    input_plan: Path = typer.Option(
        ...,
        "--input-plan",
        help="Path to an agent project plan JSON file",
    ),
    prompt: Optional[str] = typer.Option(None, help="Optional override prompt"),
    input_docs: tuple[Path, ...] = typer.Option((), help="Additional documents to load"),
    model: str = typer.Option("gpt-5.0", help="Model identifier to use for agents"),
    max_turns: int = typer.Option(8, help="Maximum turns per agent"),
    temperature: float = typer.Option(0.2, help="Sampling temperature"),
) -> None:
    """Execute the multi-agent coding workflow."""

    target_path.mkdir(parents=True, exist_ok=True)
    plan = AgentProjectPlan.load(input_plan)
    docs = _resolve_docs(input_docs)
    workspace = WorkspaceConfig.from_cli(target_path, docs, prompt)
    settings = AgentRuntimeSettings(model=model, max_turns=max_turns, temperature=temperature)

    pipeline = MultiAgentPipeline(
        workspace=workspace.root,
        plan=plan,
        settings=settings,
    )

    console.rule("AI Coding Agent")
    console.print(f"Workspace: {workspace.root}")
    console.print(f"Model: {settings.model}")
    console.print(f"Prompt override: {workspace.prompt_override!r}")

    initial_prompt = plan.initial_prompt(prompt_override=workspace.prompt_override)

    state = asyncio.run(pipeline.run(initial_prompt))

    table = Table(title="Run Summary")
    table.add_column("Event")
    for event in state.events:
        table.add_row(event)
    console.print(table)

    console.print("Artifacts recorded:")
    for key in state.artifacts:
        console.print(f"- {key}")


if __name__ == "__main__":
    app()
