from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(slots=True)
class GitOperationsTool:
    """Execute git commands against the generated project when online."""

    offline: bool = True
    name: str = "git_operations"

    def execute(self, command: str, *, workdir: Path, dry_run: bool = True) -> Dict[str, Any]:
        if self.offline or dry_run:
            return {"command": command, "dry_run": True}

        try:
            completed = subprocess.run(
                ["git"] + shlex.split(command),
                cwd=workdir,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:  # pragma: no cover - depends on environment
            return {"command": command, "status": "error", "error": str(exc)}

        status = "success" if completed.returncode == 0 else "failed"
        return {
            "command": command,
            "status": status,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }


__all__ = ["GitOperationsTool"]
