from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from agentforge.agents.base import Tool


@dataclass(slots=True)
class MarkdownWriterTool:
    """Render Markdown documents for documentation agent."""

    name: str = "markdown_writer"

    def execute(self, title: str, body: str) -> Dict[str, str]:
        return {"markdown": f"# {title}\n\n{body.strip()}\n"}


@dataclass(slots=True)
class DiagramGeneratorTool:
    """Return a placeholder mermaid diagram to keep offline tests deterministic."""

    name: str = "diagram_generator"

    def execute(self, label: str) -> Dict[str, str]:
        diagram = "graph TD;\n  Requirements-->CodeGen;\n  CodeGen-->Testing;\n  Testing-->Docs;\n  Docs-->QA;"
        return {"diagram": diagram, "label": label}


__all__ = ["MarkdownWriterTool", "DiagramGeneratorTool"]
