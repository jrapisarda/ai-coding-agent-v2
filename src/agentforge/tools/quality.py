from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


def _command_result(cmd: list[str], workdir: Path) -> Dict[str, str]:
    try:
        completed = subprocess.run(
            cmd,
            cwd=workdir,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:  # pragma: no cover - depends on environment
        return {
            "command": " ".join(cmd),
            "status": "error",
            "error": str(exc),
        }

    status = "passed" if completed.returncode == 0 else "failed"
    return {
        "command": " ".join(cmd),
        "status": status,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


@dataclass(slots=True)
class RuffCheckerTool:
    offline: bool = True
    name: str = "ruff_checker"

    def execute(self, path: Path, *, workdir: Path) -> Dict[str, str]:
        if self.offline:
            return {"path": str(path), "status": "skipped"}
        return _command_result(["ruff", "check", str(path)], workdir)


@dataclass(slots=True)
class MypyValidatorTool:
    offline: bool = True
    name: str = "mypy_validator"

    def execute(self, path: Path, *, workdir: Path) -> Dict[str, str]:
        if self.offline:
            return {"path": str(path), "status": "skipped"}
        return _command_result(["mypy", str(path)], workdir)


@dataclass(slots=True)
class BanditScannerTool:
    offline: bool = True
    name: str = "bandit_scanner"

    def execute(self, path: Path, *, workdir: Path) -> Dict[str, str]:
        if self.offline:
            return {"path": str(path), "status": "skipped"}
        return _command_result(["bandit", "-q", "-r", str(path)], workdir)


@dataclass(slots=True)
class SafetyCheckerTool:
    offline: bool = True
    name: str = "safety_checker"

    def execute(self, requirements_path: Path, *, workdir: Path) -> Dict[str, str]:
        if self.offline:
            return {"requirements": str(requirements_path), "status": "skipped"}
        if not requirements_path.exists():
            return {"requirements": str(requirements_path), "status": "missing"}
        return _command_result(["safety", "check", "-r", str(requirements_path)], workdir)


__all__ = [
    "RuffCheckerTool",
    "MypyValidatorTool",
    "BanditScannerTool",
    "SafetyCheckerTool",
]
