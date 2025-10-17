from __future__ import annotations

from agentforge.orchestration.pipeline import PipelineState


def test_pipeline_runs_sequentially(runner, project_root, pipeline_config, tmp_path):
    spec_path = project_root / "tests" / "fixtures" / "min_spec.json"
    state = PipelineState(
        spec_path=spec_path,
        output_dir=tmp_path,
        config=pipeline_config,
    )

    result = runner.run("RequirementsAnalysis", state)

    assert result.status == "completed"
    assert state.requirements
    assert state.project_files
    assert result.agents_executed == [
        "RequirementsAnalysis",
        "CodeGeneration",
        "Testing",
        "Documentation",
        "QualityAssurance",
    ]
