from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from agentforge.agents.base import Tool


@dataclass(slots=True)
class ResearchTool:
    """
    Offline-friendly research helper.

    It surfaces relevant snippets from local documentation (RFC, implementation
    plan, etc.) to simulate upstream research tooling without network access.
    """

    docs_root: Path
    name: str = "research_tool"

    def execute(self, query: str) -> Dict[str, Any]:
        matches: List[str] = []
        for path in self.docs_root.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            if query.lower() in text.lower():
                matches.append(f"{path.name}: {query}")
        return {
            "query": query,
            "matches": matches,
            "mode": "offline",
        }


__all__ = ["ResearchTool"]
