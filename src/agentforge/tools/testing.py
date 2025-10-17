from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from agentforge.agents.base import Tool


@dataclass(slots=True)
class PytestRunnerTool:
    """Simulate pytest execution."""

    name: str = "pytest_runner"

    def execute(self, test_directory: str) -> Dict[str, Any]:
        return {
            "tests": test_directory,
            "status": "simulated",
        }


@dataclass(slots=True)
class CoverageAnalyzerTool:
    """Return pseudo coverage details used for offline validation."""

    name: str = "coverage_analyzer"

    def execute(self, coverage_target: float) -> Dict[str, Any]:
        return {
            "target": coverage_target,
            "observed": max(coverage_target - 5.0, 0.0),
            "status": "estimated",
        }


__all__ = ["PytestRunnerTool", "CoverageAnalyzerTool"]
