"""
Configuration management for AgentForge.

The configuration layer reads environment variables and provides sensible
defaults so the pipeline can run in both online and offline modes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_MODEL_CONFIG = {
    "requirements": "gpt-5",
    "codegen": "gpt-5-mini",
    "testing": "gpt-5-mini",
    "documentation": "gpt-5-mini",
    "qa": "gpt-5-nano",
}


@dataclass(frozen=True)
class ModelConfig:
    """Model and parameter configuration for an agent."""

    name: str
    reasoning_effort: str = "medium"
    verbosity: str = "medium"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: float = 60.0
    max_retries: int = 3


@dataclass(frozen=True)
class AgentConfig:
    """Configuration bundle for a single agent."""

    role: str
    model: ModelConfig
    tools: tuple[str, ...]
    handoff_target: Optional[str]


@dataclass(frozen=True)
class DatabaseConfig:
    """Persistence layer configuration."""

    path: Path


@dataclass(frozen=True)
class ObservabilityConfig:
    """Tracing and logging configuration."""

    tracing_enabled: bool = True
    logging_level: str = "INFO"


@dataclass(frozen=True)
class PipelineConfig:
    """Root configuration used by the orchestration layer."""

    agents: Dict[str, AgentConfig]
    database: DatabaseConfig
    observability: ObservabilityConfig
    offline_mode: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        payload = {
            "agents": {
                name: {
                    "role": cfg.role,
                    "model": vars(cfg.model),
                    "tools": cfg.tools,
                    "handoff_target": cfg.handoff_target,
                }
                for name, cfg in self.agents.items()
            },
            "database": {"path": str(self.database.path)},
            "observability": vars(self.observability),
            "offline_mode": self.offline_mode,
            "extra": self.extra,
        }
        return json.dumps(payload, indent=2, sort_keys=True)


def _bool_env(var: str, default: bool = False) -> bool:
    raw = os.getenv(var)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _float_env(var: str, default: float) -> float:
    raw = os.getenv(var)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _int_env(var: str, default: int) -> int:
    raw = os.getenv(var)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _model_config(prefix: str, default_name: str) -> ModelConfig:
    return ModelConfig(
        name=os.getenv(f"{prefix}_MODEL", default_name),
        reasoning_effort=os.getenv(f"{prefix}_REASONING", "medium"),
        verbosity=os.getenv(f"{prefix}_VERBOSITY", "medium"),
        temperature=_float_env(f"{prefix}_TEMPERATURE", 0.7),
        max_tokens=_int_env(f"{prefix}_MAX_TOKENS", 4096),
        timeout=_float_env(f"{prefix}_TIMEOUT", 60.0),
        max_retries=_int_env(f"{prefix}_MAX_RETRIES", 3),
    )


def load_config(base_dir: Optional[Path] = None) -> PipelineConfig:
    """
    Load configuration from environment variables.

    Args:
        base_dir: Optional override for the project base directory.
    """
    root = base_dir or Path(os.getenv("AGENTFORGE_HOME", Path.cwd()))
    db_path = Path(os.getenv("AGENTFORGE_DB", root / ".agentforge.sqlite"))

    agents: Dict[str, AgentConfig] = {
        "RequirementsAnalysis": AgentConfig(
            role="analysis",
            model=_model_config("REQUIREMENTS_AGENT", DEFAULT_MODEL_CONFIG["requirements"]),
            tools=("research_tool", "schema_validator"),
            handoff_target="CodeGeneration",
        ),
        "CodeGeneration": AgentConfig(
            role="codegen",
            model=_model_config("CODEGEN_AGENT", DEFAULT_MODEL_CONFIG["codegen"]),
            tools=("file_writer", "git_operations", "template_engine"),
            handoff_target="Testing",
        ),
        "Testing": AgentConfig(
            role="testing",
            model=_model_config("TESTING_AGENT", DEFAULT_MODEL_CONFIG["testing"]),
            tools=("pytest_runner", "coverage_analyzer"),
            handoff_target="Documentation",
        ),
        "Documentation": AgentConfig(
            role="documentation",
            model=_model_config("DOCUMENTATION_AGENT", DEFAULT_MODEL_CONFIG["documentation"]),
            tools=("markdown_writer", "diagram_generator"),
            handoff_target="QualityAssurance",
        ),
        "QualityAssurance": AgentConfig(
            role="qa",
            model=_model_config("QA_AGENT", DEFAULT_MODEL_CONFIG["qa"]),
            tools=("ruff_checker", "mypy_validator", "bandit_scanner", "safety_checker"),
            handoff_target=None,
        ),
    }

    observability = ObservabilityConfig(
        tracing_enabled=_bool_env("AGENTFORGE_TRACING", True),
        logging_level=os.getenv("AGENTFORGE_LOG_LEVEL", "INFO"),
    )

    offline = _bool_env("AGENTFORGE_OFFLINE", False)

    extra: Dict[str, Any] = {}
    extra_path = os.getenv("AGENTFORGE_EXTRA_CONFIG")
    if extra_path:
        try:
            extra = json.loads(Path(extra_path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            extra = {}

    return PipelineConfig(
        agents=agents,
        database=DatabaseConfig(path=db_path),
        observability=observability,
        offline_mode=offline,
        extra=extra,
    )


__all__ = [
    "AgentConfig",
    "DatabaseConfig",
    "ModelConfig",
    "ObservabilityConfig",
    "PipelineConfig",
    "load_config",
]
