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

    def to_prompt_block(self) -> str:
        """Return a formatted text summary for agent hand-offs."""

        overview = self.requirements.get("overview", "")
        goals = "\n".join(f"- {goal}" for goal in self.requirements.get("goals", []))
        scope = self.requirements.get("scope", {})
        scope_must = "\n".join(f"* {item}" for item in scope.get("must", []))
        user_stories = "\n".join(
            f"- {story['role']}: {story['goal']} ({story['reason']})"
            for story in self.requirements.get("user_stories", [])
        )
        return (
            "# Project Overview\n"
            f"{overview}\n\n"
            "## Goals\n"
            f"{goals}\n\n"
            "## Scope (Must)\n"
            f"{scope_must}\n\n"
            "## User Stories\n"
            f"{user_stories}\n"
        )

    def initial_prompt(self, prompt_override: str | None = None) -> str:
        prompt = prompt_override or self.raw.get("prompt") or ""
        appendix = self.raw.get("input_docs_text")
        if appendix:
            prompt = f"{prompt}\n\n# Provided Documents\n{appendix}" if prompt else appendix
        return prompt
