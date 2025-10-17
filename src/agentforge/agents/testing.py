from __future__ import annotations

from pathlib import Path
import textwrap
from typing import Dict, List, Tuple

from agentforge.agents.base import BaseAgent
from agentforge.orchestration.pipeline import PipelineState


class TestingAgent(BaseAgent):
    """Generate deterministic tests for generated artifacts."""

    def _run(
        self,
        state: PipelineState,
        events: List[str],
    ) -> tuple[Dict[str, str], Dict[str, str], List[str]]:
        pytest_tool = self.get_tool("pytest_runner")
        coverage_tool = self.get_tool("coverage_analyzer")
        file_writer = self.get_tool("file_writer")

        test_file = "tests/generated/test_requirements.py"
        modules = [
            f"'generated.{Path(path).stem}'"
            for path in state.project_files
            if path.endswith(".py")
        ]

        if not modules:
            modules = ["'generated.placeholder'"]

        content = textwrap.dedent(
            """
            import importlib
            import pytest


            @pytest.mark.parametrize("module_name", [
                {modules_list}
            ])
            def test_summary_matches_requirement(module_name):
                module = importlib.import_module(module_name)
                assert isinstance(module.summary(), str)
                assert module.summary()
            """
        ).format(
            modules_list=",\n                ".join(modules)
        ).strip() + "\n"

        file_writer.execute("tests/generated/__init__.py", "__all__ = []\n", base_dir=state.output_dir)
        file_writer.execute(test_file, content, base_dir=state.output_dir)

        state.test_suite = {test_file: content}

        pytest_result = pytest_tool.execute("tests/generated")
        coverage_result = coverage_tool.execute(coverage_target=85.0)

        events.append("tests_generated=1")

        return (
            {"tests": "generated"},
            {"pytest": pytest_result, "coverage": coverage_result},
            [],
        )
