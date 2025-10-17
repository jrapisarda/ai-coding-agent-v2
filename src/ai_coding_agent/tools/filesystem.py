"""Filesystem tools exposed to agents."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

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


class RecordEventResult(BaseModel):
    status: str = Field(..., description="Result status of the log operation")
    message: str = Field(..., description="Message that was logged")


class ReadFileResult(BaseModel):
    path: str = Field(..., description="Path of the file that was read")
    content: str = Field(..., description="UTF-8 decoded content of the file (possibly truncated)")
    truncated: bool = Field(default=False, description="Whether the content was truncated due to max_bytes limit")


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
) -> RecordEventResult:
    """Record an event in the shared run log."""

    state = unwrap_context(ctx)
    message = f"[{title}] {body}"
    state.log(message)
    return RecordEventResult(status="recorded", message=message)


def _resolve_workspace_path(workspace: Path, candidate: str) -> Path:
    base = workspace.resolve()
    target = (workspace / candidate).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise ValueError("Requested path escapes the workspace boundary.")
    return target


@function_tool(name_override="read_file", description_override="Read a text file from the workspace")
def read_file_tool(
    ctx: RunContextWrapper[AgentRunState],
    path: str,
    *,
    encoding: str = "utf-8",
    max_bytes: Optional[int] = 16384,
) -> ReadFileResult:
    """Return file contents (optionally truncated) for the requesting agent."""

    state = unwrap_context(ctx)
    target = _resolve_workspace_path(state.workspace, path)
    if not target.exists() or not target.is_file():
        raise FileNotFoundError(f"File not found: {target}")

    data = target.read_bytes()
    truncated = False
    if max_bytes is not None and len(data) > max_bytes:
        data = data[:max_bytes]
        truncated = True

    content = data.decode(encoding, errors="replace")
    relative = str(target.relative_to(state.workspace))
    state.log(f"read_file served {relative} (truncated={truncated})")
    return ReadFileResult(path=relative, content=content, truncated=truncated)


TOOLS = [write_many_tool, record_event_tool, read_file_tool]
