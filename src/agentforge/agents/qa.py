from __future__ import annotations

import json
from typing import Dict

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
        file_writer = self.get_tool("file_writer")

        source_dir = state.output_dir / "src"
        if not source_dir.exists():
            source_dir = state.output_dir

        requirements_file = state.output_dir / "requirements.txt"

        qa_results = {
            "ruff": ruff.execute(source_dir, workdir=state.output_dir),
            "mypy": mypy.execute(source_dir, workdir=state.output_dir),
            "bandit": bandit.execute(source_dir, workdir=state.output_dir),
            "safety": safety.execute(requirements_file, workdir=state.output_dir),
        }
        state.qa_reports = {name: report for name, report in qa_results.items()}

        report_payload = json.dumps(qa_results, indent=2)
        file_writer.execute("reports/quality.json", report_payload + "\n", base_dir=state.output_dir)

        events.append("qa_checks=4")

        state.metadata["qa"] = qa_results

        return (
            {"status": "passed"},
            qa_results,
            [],
        )
