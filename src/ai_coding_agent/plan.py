"""Utilities for parsing agent project plans."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class AgentProjectPlan:
    """Typed view over the agent project plan JSON payload."""

    requirements: dict[str, Any]
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "AgentProjectPlan":
        data = json.loads(path.read_text())
        requirements = data.get("requirements", {})
        raw = data.get("raw", {})
        return cls(requirements=requirements, raw=raw)

    def _format_value(self, value: Any, indent: int = 0) -> list[str]:
        """Render a nested value into Markdown-friendly bullet points."""

        pad = " " * indent
        if value is None:
            return []
        if isinstance(value, str):
            stripped = value.strip()
            return [pad + stripped] if stripped else []
        if isinstance(value, (int, float)):
            return [pad + str(value)]
        if isinstance(value, bool):
            return [pad + ("yes" if value else "no")]
        if isinstance(value, list):
            if not value:
                return []
            lines: list[str] = []
            for item in value:
                if isinstance(item, (str, int, float, bool)) or item is None:
                    rendered = "" if item is None else str(item).strip()
                    lines.append(f"{pad}- {rendered}" if rendered else f"{pad}-")
                else:
                    lines.append(f"{pad}-")
                    lines.extend(self._format_value(item, indent + 2))
            return lines
        if isinstance(value, dict):
            if not value:
                return []
            lines = []
            for key, inner in value.items():
                key_line = f"{pad}- **{key}**:"
                if isinstance(inner, (dict, list)):
                    lines.append(key_line)
                    nested = self._format_value(inner, indent + 2)
                    if nested:
                        lines.extend(nested)
                    else:
                        lines.append(" " * (indent + 2) + "_None provided._")
                else:
                    rendered = "" if inner is None else str(inner).strip()
                    if not rendered:
                        rendered = "_None provided._"
                    lines.append(f"{key_line} {rendered}")
            return lines
        return [pad + str(value)]

    def _format_section(self, title: str, value: Any) -> list[str]:
        heading_level = "##"
        lines = [f"{heading_level} {title}"]
        rendered = self._format_value(value)
        if not rendered:
            lines.append("_None provided._")
        else:
            lines.extend(rendered)
        lines.append("")
        return lines

    def to_prompt_block(self) -> str:
        """Return a formatted text summary for agent hand-offs."""

        lines = ["# Project Requirements", ""]
        overview = self.requirements.get("overview")
        if overview:
            lines.extend(["## Overview", overview.strip(), ""])
        else:
            lines.extend(["## Overview", "_None provided._", ""])

        ordered_sections = [
            ("Goals", self.requirements.get("goals")),
            ("Assumptions", self.requirements.get("assumptions")),
            ("Scope", self.requirements.get("scope")),
            ("User Stories", self.requirements.get("user_stories")),
            ("Flows", self.requirements.get("flows")),
            ("Risks", self.requirements.get("risks")),
            ("Open Questions", self.requirements.get("open_questions")),
            ("Project Details", self.requirements.get("project")),
            ("Specifications", self.requirements.get("specifications")),
            ("File Structure", self.requirements.get("file_structure")),
            ("Dependencies", self.requirements.get("dependencies")),
            ("Configuration", self.requirements.get("configuration")),
            ("Execution Flow", self.requirements.get("execution_flow")),
            ("Output Examples", self.requirements.get("output_example")),
        ]

        for title, value in ordered_sections:
            lines.extend(self._format_section(title, value))

        lines.append("## Full Requirements JSON")
        lines.append("```json")
        lines.append(json.dumps(self.requirements, indent=2))
        lines.append("```")
        lines.append("")

        return "\n".join(lines).strip() + "\n"

    def initial_prompt(self, prompt_override: str | None = None) -> str:
        prompt = prompt_override or self.raw.get("prompt") or ""
        appendix = self.raw.get("input_docs_text")
        if appendix:
            prompt = f"{prompt}\n\n# Provided Documents\n{appendix}" if prompt else appendix
        return prompt
