"""Tooling primitives similar to the OpenAI Agents SDK."""

from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Awaitable, Callable, Protocol


class ToolFunction(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover - Protocol
        ...


@dataclass(slots=True)
class Tool:
    name: str
    description: str
    handler: Callable[..., Awaitable[Any]] | Callable[..., Any]

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        result = self.handler(*args, **kwargs)
        if callable(getattr(result, "__await__", None)):
            return await result  # type: ignore[return-value]
        return result


def function_tool(description: str) -> Callable[[ToolFunction], Tool]:
    """Decorator that registers a synchronous or async function as a tool."""

    def decorator(func: ToolFunction) -> Tool:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return Tool(name=func.__name__, description=description, handler=wrapper)

    return decorator
