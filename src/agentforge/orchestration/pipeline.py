from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentforge.agents.base import AgentExecutionError, AgentRunResult, BaseAgent
from agentforge.config import PipelineConfig
from agentforge.observability.tracing import Tracer
from agentforge.persistence.database import init_db, record_agent_runs
from agentforge.persistence.models import AgentRunRecord
from agentforge.orchestration.handoffs import determine_next_agent


@dataclass
class PipelineState:
    spec_path: Path
    output_dir: Path
    config: PipelineConfig
    spec: Optional[Dict] = None
    requirements: List[str] = field(default_factory=list)
    project_files: Dict[str, str] = field(default_factory=dict)
    test_suite: Dict[str, str] = field(default_factory=dict)
    documentation: Dict[str, str] = field(default_factory=dict)
    qa_reports: Dict[str, str] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def record_history(self, message: str) -> None:
        self.history.append(message)


@dataclass
class PipelineResult:
    status: str
    final_output: Dict[str, Any]
    agents_executed: List[str]
    total_tokens: int
    duration_ms: float
    trace: Dict


class PipelineRunner:
    """
    Orchestrate agent execution with deterministic offline behaviour.
    """

    def __init__(self, agents: Dict[str, BaseAgent], config: PipelineConfig, tracer: Optional[Tracer] = None) -> None:
        self._agents = agents
        self._config = config
        self._tracer = tracer or Tracer()
        init_db(config.database.path)

    @property
    def tracer(self) -> Tracer:
        return self._tracer

    def _execute_agent(self, agent_name: str, state: PipelineState) -> AgentRunResult:
        agent = self._agents.get(agent_name)
        if agent is None:
            raise AgentExecutionError(f"Agent '{agent_name}' not registered.")

        with self._tracer.span(f"agent.{agent_name}", reasoning=agent.config.model.reasoning_effort):
            state.record_history(f"Start {agent_name}")
            result = agent.run(state)
            state.record_history(f"End {agent_name}")
            return result

    def run(self, start_agent: str, state: PipelineState) -> PipelineResult:
        state.output_dir.mkdir(parents=True, exist_ok=True)

        executed: List[str] = []
        records: List[AgentRunRecord] = []
        current = start_agent
        while current:
            result = self._execute_agent(current, state)
            executed.append(current)
            records.append(
                AgentRunRecord(
                    agent_name=current,
                    status="completed",
                    payload={
                        "output": result.output,
                        "events": result.events,
                        "warnings": result.warnings,
                    },
                )
            )
            current = determine_next_agent(result)

        record_agent_runs(self._config.database.path, records)

        return PipelineResult(
            status="completed",
            final_output={
                "requirements": state.requirements,
                "project_files": state.project_files,
                "test_suite": state.test_suite,
                "documentation": state.documentation,
                "qa_reports": state.qa_reports,
                "metadata": state.metadata,
            },
            agents_executed=executed,
            total_tokens=0,
            duration_ms=sum(span.duration_ms for span in self.tracer.spans),
            trace=self.tracer.to_dict(),
        )


async def execute_pipeline_with_handoffs(spec_path: str, output_dir: str, runner: PipelineRunner, state: Optional[PipelineState] = None) -> PipelineResult:
    """
    Async-friendly wrapper for the RFC handoff sequence.
    """

    if state is None:
        state = PipelineState(
            spec_path=Path(spec_path),
            output_dir=Path(output_dir),
            config=runner._config,
        )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, runner.run, "RequirementsAnalysis", state)


__all__ = ["PipelineRunner", "PipelineState", "PipelineResult", "execute_pipeline_with_handoffs"]
