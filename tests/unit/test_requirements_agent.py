from __future__ import annotations

from pathlib import Path

from agentforge.agents.requirements import RequirementsAnalysisAgent
from agentforge.config import PipelineConfig
from agentforge.tools.research import ResearchTool
from agentforge.tools.validators import SchemaValidatorTool
from agentforge.orchestration.pipeline import PipelineState


def build_agent(config: PipelineConfig, project_root: Path) -> RequirementsAnalysisAgent:
    schema_path = project_root / "src" / "agentforge" / "schema" / "spec_schema.json"
    return RequirementsAnalysisAgent(
        name="RequirementsAnalysis",
        config=config.agents["RequirementsAnalysis"],
        tools=[
            SchemaValidatorTool(schema_path=schema_path),
            ResearchTool(docs_root=project_root / "docs"),
        ],
    )


def test_requirements_agent_extracts_requirements(pipeline_config: PipelineConfig, project_root: Path, tmp_path):
    agent = build_agent(pipeline_config, project_root)
    spec_path = project_root / "tests" / "fixtures" / "min_spec.json"
    state = PipelineState(
        spec_path=spec_path,
        output_dir=tmp_path,
        config=pipeline_config,
    )

    result = agent.run(state)

    assert int(result.output["requirements_count"]) == 2
    assert state.requirements
    assert state.metadata["project"]["name"]
    assert "items" in state.metadata.get("requirements", {})
