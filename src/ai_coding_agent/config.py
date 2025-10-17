"""Configuration helpers for the AI Coding Agent CLI."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from pydantic import BaseModel, Field


@dataclass(slots=True)
class WorkspaceConfig:
    """Configuration for a target workspace run."""

    root: Path
    input_docs: list[Path]
    prompt_override: Optional[str] = None

    @classmethod
    def from_cli(
        cls,
        target_path: Path,
        input_docs: Iterable[Path] | None = None,
        prompt: str | None = None,
    ) -> "WorkspaceConfig":
        docs = sorted(path for path in (input_docs or []) if path.exists())
        return cls(root=target_path, input_docs=list(docs), prompt_override=prompt)


class AgentRuntimeSettings(BaseModel):
    """Runtime knobs that can be serialized and stored in SQLite later."""

    model: str = Field(default="gpt-5.0")
    max_turns: int = Field(default=8, ge=1, le=32)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    enable_web_search: bool = Field(default=False)

    class Config:
        extra = "allow"
