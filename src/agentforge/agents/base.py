"""
Base classes and utilities shared by all agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Protocol, TYPE_CHECKING

from agentforge.config import AgentConfig

if TYPE_CHECKING:
    from agentforge.orchestration.pipeline import PipelineState


class AgentExecutionError(RuntimeError):
    """Raised when an agent fails to complete its task."""


@dataclass(slots=True)
class AgentRunResult:
    """Standardized agent response that the orchestration layer consumes."""

    agent_name: str
    output: Dict[str, Any]
    handoff_target: Optional[str]
    artifacts: Dict[str, Any] = field(default_factory=dict)
    events: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class Tool(Protocol):
    """Simple protocol describing an agent tool."""

    name: str

    def execute(self, **kwargs: Any) -> Any:
        ...


class BaseAgent:
    """
    Base class for all specialized agents.

    Concrete agents override `_run` to populate the shared pipeline state.
    """

    def __init__(self, name: Optional[str], config: AgentConfig, tools: Iterable[Tool]) -> None:
        self.name = name or config.role
        self.config = config
        self._tools: Dict[str, Tool] = {tool.name: tool for tool in tools}

    @property
    def handoff_target(self) -> Optional[str]:
        return self.config.handoff_target

    def get_tool(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise AgentExecutionError(f"Tool '{name}' not registered for {self.name}") from exc

    def run(self, state: "PipelineState") -> AgentRunResult:
        events: List[str] = [
            f"{self.name}:model={self.config.model.name}",
            f"{self.name}:reasoning={self.config.model.reasoning_effort}",
        ]

        output, artifacts, warnings = self._run(state, events)
        return AgentRunResult(
            agent_name=self.name,
            output=output,
            handoff_target=self.handoff_target,
            artifacts=artifacts,
            events=events,
            warnings=warnings,
        )

    def _run(
        self,
        state: "PipelineState",
        events: List[str],
    ) -> tuple[Dict[str, Any], Dict[str, Any], List[str]]:
        """Override in subclasses to implement agent-specific logic."""
        raise NotImplementedError


__all__ = ["BaseAgent", "AgentRunResult", "AgentExecutionError", "Tool"]
