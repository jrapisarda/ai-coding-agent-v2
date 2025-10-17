"""Agent factory helpers."""

from pathlib import Path

from agentforge.config import PipelineConfig
from agentforge.tools.documentation import DiagramGeneratorTool, MarkdownWriterTool
from agentforge.tools.file_ops import FileWriterTool
from agentforge.tools.git_ops import GitOperationsTool
from agentforge.tools.quality import BanditScannerTool, MypyValidatorTool, RuffCheckerTool, SafetyCheckerTool
from agentforge.tools.research import ResearchTool
from agentforge.tools.testing import CoverageAnalyzerTool, PytestRunnerTool
from agentforge.tools.validators import SchemaValidatorTool

from .base import BaseAgent
from .codegen import CodeGenerationAgent
from .documentation import DocumentationAgent
from .qa import QualityAssuranceAgent
from .requirements import RequirementsAnalysisAgent
from .testing import TestingAgent


def build_agents(config: PipelineConfig, docs_root: Path, output_dir: Path, schema_path: Path) -> dict[str, BaseAgent]:
    schema_tool = SchemaValidatorTool(schema_path=schema_path)
    research_tool = ResearchTool(docs_root=docs_root)
    file_writer = FileWriterTool(output_dir=output_dir)
    git_ops = GitOperationsTool()
    pytest_tool = PytestRunnerTool()
    coverage_tool = CoverageAnalyzerTool()
    markdown_tool = MarkdownWriterTool()
    diagram_tool = DiagramGeneratorTool()
    ruff_tool = RuffCheckerTool()
    mypy_tool = MypyValidatorTool()
    bandit_tool = BanditScannerTool()
    safety_tool = SafetyCheckerTool()

    return {
        "RequirementsAnalysis": RequirementsAnalysisAgent(
            name="RequirementsAnalysis",
            config=config.agents["RequirementsAnalysis"],
            tools=[schema_tool, research_tool],
        ),
        "CodeGeneration": CodeGenerationAgent(
            name="CodeGeneration",
            config=config.agents["CodeGeneration"],
            tools=[file_writer, git_ops],
        ),
        "Testing": TestingAgent(
            name="Testing",
            config=config.agents["Testing"],
            tools=[pytest_tool, coverage_tool],
        ),
        "Documentation": DocumentationAgent(
            name="Documentation",
            config=config.agents["Documentation"],
            tools=[markdown_tool, diagram_tool],
        ),
        "QualityAssurance": QualityAssuranceAgent(
            name="QualityAssurance",
            config=config.agents["QualityAssurance"],
            tools=[ruff_tool, mypy_tool, bandit_tool, safety_tool],
        ),
    }


__all__ = ["build_agents"]
