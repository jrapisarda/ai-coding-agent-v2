"""Filesystem tools exposed to agents."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agents.run_context import RunContextWrapper
from agents.tool import function_tool

from ..context import AgentRunState, unwrap_context


@dataclass
class FileWriteRequest:
    """Declarative request for writing a single file."""

    path: str
    content: str
    overwrite: bool = True

    def target_path(self, base: Path) -> Path:
        return base / self.path


def _normalize_request(data: dict[str, Any]) -> FileWriteRequest:
    overwrite_value = data.get("overwrite", True)
    if isinstance(overwrite_value, str):
        overwrite_value = overwrite_value.lower() not in {"false", "0", "no"}
    return FileWriteRequest(
        path=data.get("path", ""),
        content=data.get("content", ""),
        overwrite=bool(overwrite_value),
    )


@function_tool(name_override="write_many", description_override="Write multiple files to the workspace")
def write_many_tool(
    ctx: RunContextWrapper[AgentRunState],
    files: list[dict[str, Any]],
    *,
    base_path: str | None = None,
    create_parents: bool = True,
    encoding: str = "utf-8",
) -> dict[str, int]:
    """Write many files atomically within the run workspace."""

    state = unwrap_context(ctx)
    workspace = state.workspace
    if base_path:
        workspace = workspace / base_path

    written = 0
    for raw in files:
        request = _normalize_request(raw)
        target = request.target_path(workspace)
        if create_parents:
            target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not request.overwrite:
            continue
        target.write_text(request.content, encoding=encoding)
        written += 1
    state.log(f"write_many wrote {written} files under {workspace}")
    return {"written": written}


@function_tool(name_override="record_event", description_override="Append a structured event to the run log")
def record_event_tool(
    ctx: RunContextWrapper[AgentRunState],
    title: str,
    body: str,
) -> dict[str, str]:
    """Record an event in the shared run log."""

    state = unwrap_context(ctx)
    message = f"[{title}] {body}"
    state.log(message)
    return {"status": "recorded", "message": message}


TOOLS = [write_many_tool, record_event_tool]
