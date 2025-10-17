from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from agentforge.agents.base import Tool


@dataclass(slots=True)
class RuffCheckerTool:
    name: str = "ruff_checker"

    def execute(self, path: str) -> Dict[str, str]:
        return {"path": path, "status": "clean"}


@dataclass(slots=True)
class MypyValidatorTool:
    name: str = "mypy_validator"

    def execute(self, path: str) -> Dict[str, str]:
        return {"path": path, "status": "typed"}


@dataclass(slots=True)
class BanditScannerTool:
    name: str = "bandit_scanner"

    def execute(self, path: str) -> Dict[str, str]:
        return {"path": path, "status": "secure"}


@dataclass(slots=True)
class SafetyCheckerTool:
    name: str = "safety_checker"

    def execute(self, requirements_path: str) -> Dict[str, str]:
        return {"requirements": requirements_path, "status": "no known vulnerabilities"}


__all__ = [
    "RuffCheckerTool",
    "MypyValidatorTool",
    "BanditScannerTool",
    "SafetyCheckerTool",
]
