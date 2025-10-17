"""Configuration helpers for AgentForge."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Literal


@dataclass(slots=True)
class Settings:
    """Application settings sourced from environment variables."""

    database_path: str = os.getenv("AGENTFORGE_DB", ".agentforge.sqlite")
    offline: bool = os.getenv("AGENTFORGE_OFFLINE", "1") == "1"
    seed: int = int(os.getenv("AGENTFORGE_SEED", "1337"))
    debug: bool = os.getenv("AGENTFORGE_DEBUG", "0") == "1"
    model: str = os.getenv("AGENTFORGE_MODEL", "gpt-5-mini")
    reasoning_effort: Literal["minimal", "low", "medium", "high"] = (
        os.getenv("AGENTFORGE_REASONING_EFFORT", "medium")  # type: ignore[assignment]
    )
    verbosity: Literal["low", "medium", "high"] = (
        os.getenv("AGENTFORGE_VERBOSITY", "medium")  # type: ignore[assignment]
    )
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")


settings = Settings()
