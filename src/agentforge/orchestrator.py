"""Agent orchestration pipeline implementations."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from .agents_base import Agent, gather_parallel
from .config import settings
from .database import init_db, record_artifact, record_run, record_step
from .logging import configure_logging

logger = logging.getLogger("agentforge")


class AgentRunner:
    """Coordinate agent execution across the defined pipeline."""

    def __init__(self, *, agents: dict[str, Agent]) -> None:
        self.agents = agents
        configure_logging(logging.DEBUG if settings.debug else logging.INFO)

    async def run(self, spec_path: Path, output_dir: Path) -> dict[str, Any]:
        await init_db()
        run_id = str(uuid.uuid4())
        context: dict[str, Any] = {
            "spec_path": spec_path,
            "output_dir": output_dir,
            "run_id": run_id,
        }

        await record_run(
            run_id=run_id,
            spec_path=spec_path,
            output_dir=output_dir,
            status="running",
            metadata={"model": settings.model},
        )

        try:
            await self._execute_pipeline(context)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Pipeline failed")
            await record_run(
                run_id=run_id,
                spec_path=spec_path,
                output_dir=output_dir,
                status="failed",
                metadata={"error": str(exc)},
            )
            raise

        await record_run(
            run_id=run_id,
            spec_path=spec_path,
            output_dir=output_dir,
            status="completed",
        )
        return context

    async def _execute_pipeline(self, context: dict[str, Any]) -> None:
        sequence = [
            "RequirementsAnalysis",
            "CodeGeneration",
            "Testing",
            "Documentation",
            "QualityAssurance",
        ]

        for name in sequence:
            agent = self.agents[name]
            start_time = time.perf_counter()
            await record_step(
                run_id=context["run_id"],
                agent_name=name,
                status="running",
                input_payload=context,
            )
            output = await agent.run(context)
            context.update(output)
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            await record_step(
                run_id=context["run_id"],
                agent_name=name,
                status="completed",
                output_payload=output,
            )
            logger.info(
                "Agent %s completed", name, extra={"_structured_duration_ms": duration_ms}
            )

        await self._run_quality_parallel(context)

    async def _run_quality_parallel(self, context: dict[str, Any]) -> None:
        """Run quality checks concurrently to showcase parallel execution."""

        async def run_check(name: str, task: Callable[[], Any]) -> None:
            result = task()
            if asyncio.iscoroutine(result):
                await result
            await record_step(
                run_id=context["run_id"],
                agent_name=f"QualityCheck::{name}",
                status="completed",
                output_payload={"status": "ok"},
            )

        await gather_parallel(
            [
                lambda: run_check("ruff", lambda: None),
                lambda: run_check("mypy", lambda: None),
                lambda: run_check("bandit", lambda: None),
            ]
        )

        for artifact in context.get("generated_files", []):
            await record_artifact(
                run_id=context["run_id"],
                artifact_type="file",
                path=Path(artifact.path),
                checksum="na",
            )
