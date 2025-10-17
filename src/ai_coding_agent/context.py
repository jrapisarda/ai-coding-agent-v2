"""Shared context used across agent runs."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agents.run_context import RunContextWrapper

from .plan import AgentProjectPlan


@dataclass
class AgentRunState:
    """Mutable state stored on the run context."""

    workspace: Path
    plan: AgentProjectPlan
    events: list[str] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)

    def log(self, message: str) -> None:
        self.events.append(message)

    def add_artifact(self, name: str, payload: Any) -> None:
        self.artifacts[name] = payload


def unwrap_context(wrapper: RunContextWrapper[AgentRunState]) -> AgentRunState:
    """Convenience helper to access the underlying dataclass."""

    return wrapper.context
