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
        file_writer = self.get_tool("file_writer")

        spec = state.spec or {}
        project = spec.get("project", {}) if isinstance(spec, dict) else {}
        project_name = project.get("name", "Generated Project")

        requirements_meta = state.metadata.get("requirements", {}) or {}
        if not isinstance(requirements_meta, dict):
            requirements_meta = {"items": state.requirements}
        overview = requirements_meta.get("overview", "")
        goals = requirements_meta.get("goals", [])
        assumptions = requirements_meta.get("assumptions", [])
        scope = requirements_meta.get("scope", {})

        body_parts: List[str] = []
        if overview:
            body_parts.append("## Overview")
            body_parts.append(overview.strip())
        if goals:
            body_parts.append("## Goals")
            body_parts.extend(f"- {goal}" for goal in goals)
        if assumptions:
            body_parts.append("## Assumptions")
            body_parts.extend(f"- {assumption}" for assumption in assumptions)
        if scope:
            body_parts.append("## Scope")
            for label, entries in scope.items():
                body_parts.append(f"### {label.capitalize()}")
                body_parts.extend(f"- {entry}" for entry in entries)

        if not body_parts:
            items = requirements_meta.get("items", state.requirements)
            requirements_section = "\n".join(f"- {req}" for req in items)
            body = f"## Requirements\n\n{requirements_section}"
        else:
            body = "\n\n".join(body_parts)

        markdown = markdown_tool.execute(
            title=project_name,
            body=body,
        )
        diagram = diagram_tool.execute(label="agent-flow")

        file_writer.execute("README.md", markdown["markdown"], base_dir=state.output_dir)
        file_writer.execute("docs/flow.mmd", diagram["diagram"], base_dir=state.output_dir)

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
