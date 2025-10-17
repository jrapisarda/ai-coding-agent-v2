from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class AgentRunRecord:
    agent_name: str
    status: str
    payload: Dict[str, Any] = field(default_factory=dict)


__all__ = ["AgentRunRecord"]
