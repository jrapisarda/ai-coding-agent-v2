"""Core agent abstractions inspired by the OpenAI Agents SDK."""

from __future__ import annotations

import asyncio
import inspect
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Iterable

from .guardrails import Guardrail
from .tools import Tool

logger = logging.getLogger("agentforge")


@dataclass(slots=True)
class ModelConfig:
    model: str
    reasoning_effort: str = "medium"
    verbosity: str = "medium"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: float = 60.0
    max_retries: int = 3


@dataclass(slots=True)
class Agent:
    """Represents a single agent execution unit."""

    name: str
    instructions: str
    model_config: ModelConfig
    behavior: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]
    tools: list[Tool] = field(default_factory=list)
    handoffs: list[str] = field(default_factory=list)
    input_guardrails: list[Guardrail] = field(default_factory=list)
    output_guardrails: list[Guardrail] = field(default_factory=list)

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        logger.debug("Running agent", extra={"_structured_agent": self.name})
        for guardrail in self.input_guardrails:
            result = await guardrail(context)
            if not result.get("valid", False):
                raise ValueError(f"Input guardrail failed: {result.get('error')}")

        output = await self.behavior(context)

        for guardrail in self.output_guardrails:
            result = await guardrail(context, output)
            if not result.get("valid", False):
                raise ValueError(f"Output guardrail failed: {result.get('error')}")

        return output


async def gather_parallel(tasks: Iterable[Callable[[], Awaitable[Any]]]) -> list[Any]:
    """Execute tasks in parallel with graceful error handling."""

    coroutines = [task() for task in tasks]
    return await asyncio.gather(*coroutines, return_exceptions=False)


def ensure_coroutine(func: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    """Wrap a synchronous function into an async function."""

    if inspect.iscoroutinefunction(func):
        return func  # type: ignore[return-value]

    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper
