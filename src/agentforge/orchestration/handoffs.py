"""
Utilities for agent handoffs.
"""

from __future__ import annotations

from typing import Dict, Optional

from agentforge.agents.base import AgentRunResult


def determine_next_agent(result: AgentRunResult, overrides: Optional[Dict[str, str]] = None) -> Optional[str]:
    """
    Determine which agent should execute next based on the current result.
    """
    overrides = overrides or {}
    if result.agent_name in overrides:
        return overrides[result.agent_name]
    return result.handoff_target


__all__ = ["determine_next_agent"]
