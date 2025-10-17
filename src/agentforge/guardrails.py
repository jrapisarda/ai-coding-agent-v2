"""Guardrail primitives for agent execution."""

from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Awaitable, Callable


@dataclass(slots=True)
class Guardrail:
    name: str
    handler: Callable[..., Awaitable[dict[str, Any]]]

    async def __call__(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return await self.handler(*args, **kwargs)


def guardrail(func: Callable[..., Awaitable[dict[str, Any]]]) -> Guardrail:
    """Decorator for declaring guardrail functions."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return await func(*args, **kwargs)

    return Guardrail(name=func.__name__, handler=wrapper)
