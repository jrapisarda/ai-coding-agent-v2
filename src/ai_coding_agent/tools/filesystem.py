"""Filesystem tools exposed to agents."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.run_context import RunContextWrapper
from agents.tool import function_tool
from pydantic import BaseModel, Field, model_validator

from ..context import AgentRunState, unwrap_context


class FileWriteRequest(BaseModel):
    """Declarative request for writing a single file."""

    path: str = Field(..., description="Path of the file relative to the workspace root")
    content: str = Field(..., description="Contents to write to the file")
    overwrite: bool = Field(
        default=True,
        description="Whether to overwrite the file if it already exists",
    )

    @model_validator(mode="before")
    @classmethod
    def _coerce_overwrite(cls, data: Any) -> Any:
        """Allow string representations of booleans for the overwrite flag."""

        if isinstance(data, dict) and "overwrite" in data:
            overwrite_value = data["overwrite"]
            if isinstance(overwrite_value, str):
                data = dict(data)
                data["overwrite"] = overwrite_value.lower() not in {"false", "0", "no"}
        return data

    def target_path(self, base: Path) -> Path:
        return base / self.path


class WriteManyResult(BaseModel):
    written: int = Field(..., description="Number of files written to disk")


@function_tool(name_override="write_many", description_override="Write multiple files to the workspace")
def write_many_tool(
    ctx: RunContextWrapper[AgentRunState],
    files: list[FileWriteRequest],
    *,
    base_path: str | None = None,
    create_parents: bool = True,
    encoding: str = "utf-8",
) -> WriteManyResult:
    """Write many files atomically within the run workspace."""

    state = unwrap_context(ctx)
    workspace = state.workspace
    if base_path:
        workspace = workspace / base_path

    written = 0
    for raw in files:
        if not isinstance(raw, FileWriteRequest):
            request = FileWriteRequest.model_validate(raw)
        else:
            request = raw
        target = request.target_path(workspace)
        if create_parents:
            target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not request.overwrite:
            continue
        target.write_text(request.content, encoding=encoding)
        written += 1
    state.log(f"write_many wrote {written} files under {workspace}")
    return WriteManyResult(written=written)


@function_tool(name_override="record_event", description_override="Append a structured event to the run log")
def record_event_tool(
    ctx: RunContextWrapper[AgentRunState],
    title: str,
    body: str,
) -> "RecordEventResult":
    """Record an event in the shared run log."""

    state = unwrap_context(ctx)
    message = f"[{title}] {body}"
    state.log(message)
    return RecordEventResult(status="recorded", message=message)


class RecordEventResult(BaseModel):
    status: str = Field(..., description="Result status of the log operation")
    message: str = Field(..., description="Message that was logged")


TOOLS = [write_many_tool, record_event_tool]
