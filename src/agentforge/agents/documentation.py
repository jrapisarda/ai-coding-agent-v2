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

        testing_meta = state.metadata.get("testing")
        if isinstance(testing_meta, dict):
            pytest_status = testing_meta.get("pytest", {}).get("status")
            coverage_status = testing_meta.get("coverage", {}).get("status")
            coverage_observed = testing_meta.get("coverage", {}).get("observed")
            testing_lines: List[str] = ["## Test Results"]
            if pytest_status:
                testing_lines.append(f"- Pytest: {pytest_status}")
            if coverage_status or coverage_observed:
                coverage_line = "- Coverage"
                details = []
                if coverage_status:
                    details.append(f"status={coverage_status}")
                if coverage_observed:
                    details.append(f"observed={coverage_observed}")
                if details:
                    coverage_line += " (" + ", ".join(details) + ")"
                testing_lines.append(coverage_line)
            if len(testing_lines) > 1:
                body_parts.append("\n".join(testing_lines))

        qa_meta = state.metadata.get("qa")
        if isinstance(qa_meta, dict):
            qa_lines: List[str] = ["## Quality Checks"]
            for name, result in qa_meta.items():
                status = result.get("status") or result.get("dry_run")
                if status is None and "command" in result:
                    status = "executed"
                if status is None:
                    continue
                qa_lines.append(f"- {name}: {status}")
            if len(qa_lines) > 1:
                body_parts.append("\n".join(qa_lines))

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
