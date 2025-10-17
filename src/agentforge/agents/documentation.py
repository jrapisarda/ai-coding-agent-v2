from __future__ import annotations

from typing import Dict, List, Tuple

from agentforge.agents.base import BaseAgent
from agentforge.orchestration.pipeline import PipelineState


class DocumentationAgent(BaseAgent):
    """Produce documentation artifacts such as README excerpts and diagrams."""

    def _run(
        self,
        state: PipelineState,
        events: List[str],
    ) -> tuple[Dict[str, str], Dict[str, str], List[str]]:
        markdown_tool = self.get_tool("markdown_writer")
        diagram_tool = self.get_tool("diagram_generator")

        spec = state.spec or {}
        project_name = spec.get("project", {}).get("name", "Generated Project")
        requirements_section = "\n".join(f"- {req}" for req in state.requirements)
        markdown = markdown_tool.execute(
            title=project_name,
            body=f"## Requirements\n\n{requirements_section}",
        )
        diagram = diagram_tool.execute(label="agent-flow")

        state.documentation = {
            "README.md": markdown["markdown"],
            "docs/flow.mmd": diagram["diagram"],
        }

        events.append("documentation_pages=2")

        return (
            {"documents": "README.md, docs/flow.mmd"},
            {"markdown": markdown, "diagram": diagram},
            [],
        )
