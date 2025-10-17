from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from agentforge.agents.base import Tool


@dataclass(slots=True)
class GitOperationsTool:
    """Record git operations to keep deterministic tests."""

    name: str = "git_operations"

    def execute(self, command: str, dry_run: bool = True) -> Dict[str, Any]:
        return {"command": command, "dry_run": dry_run}


__all__ = ["GitOperationsTool"]
