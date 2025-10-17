from __future__ import annotations

import json
from typing import Dict, List, Tuple

from agentforge.agents.base import BaseAgent
from agentforge.orchestration.pipeline import PipelineState


class RequirementsAnalysisAgent(BaseAgent):
    """Load the spec, validate structure, and extract actionable requirements."""

    def _run(
        self,
        state: PipelineState,
        events: List[str],
    ) -> tuple[Dict[str, str], Dict[str, str], List[str]]:
        spec_data = state.spec or json.loads(state.spec_path.read_text(encoding="utf-8"))
        state.spec = spec_data

        validator = self.get_tool("schema_validator")
        warnings = validator.execute(spec_data)
        events.append(f"requirements:validators={len(warnings)}")

        requirements = []
        for item in spec_data.get("requirements", []):
            if isinstance(item, dict):
                summary = f"{item.get('id', 'R?')}: {item.get('description', '').strip()}"
            else:
                summary = str(item)
            requirements.append(summary)

        if not requirements:
            requirements.append("No explicit requirements; proceed with defaults.")

        state.requirements = requirements

        research_tool = self.get_tool("research_tool")
        research_hits = research_tool.execute(spec_data.get("project", {}).get("name", ""))
        events.append(f"research:matches={len(research_hits['matches'])}")

        return (
            {
                "summary": spec_data.get("project", {}).get("summary", ""),
                "requirements_count": str(len(requirements)),
            },
            {"research": research_hits},
            warnings,
        )
