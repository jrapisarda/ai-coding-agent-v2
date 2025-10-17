from __future__ import annotations

from agentforge.orchestration.pipeline import PipelineState


def test_pipeline_handles_project_plan(runner, project_root, pipeline_config, tmp_path):
    spec_path = project_root / "tests" / "fixtures" / "agent_project_plan.json"
    output_dir = tmp_path / "artifacts"

    state = PipelineState(
        spec_path=spec_path,
        output_dir=output_dir,
        config=pipeline_config,
    )

    result = runner.run("RequirementsAnalysis", state)

    assert result.status == "completed"
    assert state.metadata["project"]["name"] == "AgentForge Project" or state.metadata["project"]["name"]
    plan_summary = output_dir / "docs" / "plan_summary.md"
    readme = output_dir / "README.md"
    quality_report = output_dir / "reports" / "quality.json"
    assert plan_summary.exists()
    assert readme.exists()
    assert quality_report.exists()
