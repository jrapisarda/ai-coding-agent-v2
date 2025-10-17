from __future__ import annotations

from typing import Dict, List, Tuple

from agentforge.agents.base import BaseAgent
from agentforge.orchestration.pipeline import PipelineState


class QualityAssuranceAgent(BaseAgent):
    """Perform static analysis and safety checks."""

    def _run(
        self,
        state: PipelineState,
        events: List[str],
    ) -> tuple[Dict[str, str], Dict[str, str], List[str]]:
        ruff = self.get_tool("ruff_checker")
        mypy = self.get_tool("mypy_validator")
        bandit = self.get_tool("bandit_scanner")
        safety = self.get_tool("safety_checker")

        qa_results = {
            "ruff": ruff.execute("src"),
            "mypy": mypy.execute("src"),
            "bandit": bandit.execute("src"),
            "safety": safety.execute("requirements.txt"),
        }
        state.qa_reports = {name: str(report) for name, report in qa_results.items()}

        events.append("qa_checks=4")

        return (
            {"status": "passed"},
            qa_results,
            [],
        )
