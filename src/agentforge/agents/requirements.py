from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

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

        requirements_raw = spec_data.get("requirements", [])
        requirements, metadata = self._normalize_requirements(requirements_raw)
        if not requirements:
            requirements = ["No explicit requirements; proceed with defaults."]

        state.requirements = requirements
        normalized_metadata = metadata if metadata else {"items": requirements}
        state.metadata["requirements"] = normalized_metadata
        state.metadata["requirements_raw"] = requirements_raw

        project_info = dict(spec_data.get("project") or {})
        project_name = project_info.get("name") or spec_data.get("name") or "AgentForge Project"
        overview = metadata.get("overview") if isinstance(metadata, dict) else None
        if overview and not project_info.get("summary"):
            project_info["summary"] = overview
        project_info.setdefault("name", project_name)
        spec_data["project"] = project_info
        state.metadata["project"] = project_info

        research_tool = self.get_tool("research_tool")
        research_query = project_info.get("name") or overview or "AgentForge Project"
        research_hits = research_tool.execute(research_query)
        events.append(f"research:matches={len(research_hits['matches'])}")

        return (
            {
                "summary": project_info.get("summary", ""),
                "requirements_count": str(len(requirements)),
            },
            {"research": research_hits},
            warnings,
        )

    def _normalize_requirements(self, requirements_raw: Any) -> Tuple[List[str], Dict[str, Any]]:
        metadata: Dict[str, Any] = {}
        normalized: List[str] = []

        def _extend(prefix: str, values: List[str]) -> None:
            for value in values:
                normalized.append(f"{prefix}: {value.strip()}")

        if isinstance(requirements_raw, dict):
            overview = requirements_raw.get("overview")
            if overview:
                metadata["overview"] = overview
                normalized.append(f"Overview: {overview.strip()}")

            goals = [str(goal).strip() for goal in requirements_raw.get("goals", [])]
            if goals:
                metadata["goals"] = goals
                _extend("Goal", goals)

            assumptions = [str(item).strip() for item in requirements_raw.get("assumptions", [])]
            if assumptions:
                metadata["assumptions"] = assumptions
                _extend("Assumption", assumptions)

            scope = requirements_raw.get("scope", {})
            if isinstance(scope, dict):
                normalized_scope: Dict[str, List[str]] = {}
                for key, items in scope.items():
                    stringified = [str(item).strip() for item in (items or [])]
                    normalized_scope[key] = stringified
                    label = f"Scope-{key}"
                    _extend(label, stringified)
                metadata["scope"] = normalized_scope

            user_stories = []
            for story in requirements_raw.get("user_stories", []):
                if isinstance(story, dict):
                    role = story.get("role", "User")
                    goal = story.get("goal", "").strip()
                    reason = story.get("reason", "").strip()
                    summary = f"{role}: {goal}"
                    if reason:
                        summary += f" (so that {reason})"
                    user_stories.append(summary)
                else:
                    user_stories.append(str(story))
            if user_stories:
                metadata["user_stories"] = user_stories
                _extend("UserStory", user_stories)

            handled_keys = {"overview", "goals", "assumptions", "scope", "user_stories"}
            for key, value in requirements_raw.items():
                if key in handled_keys:
                    continue
                if isinstance(value, list):
                    entries = [str(item).strip() for item in value if str(item).strip()]
                    if entries:
                        metadata[key] = entries
                        _extend(key.capitalize(), entries)
                elif isinstance(value, dict):
                    metadata[key] = value
                elif value:
                    metadata[key] = str(value)
                    normalized.append(f"{key.capitalize()}: {value}")

        elif isinstance(requirements_raw, list):
            for item in requirements_raw:
                if isinstance(item, dict):
                    summary = f"{item.get('id', 'R?')}: {item.get('description', '').strip()}"
                else:
                    summary = str(item)
                normalized.append(summary)
        elif requirements_raw:
            normalized.append(str(requirements_raw))

        return normalized, metadata
