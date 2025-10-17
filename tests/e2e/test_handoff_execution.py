from __future__ import annotations

import asyncio

from agentforge.orchestration.pipeline import PipelineState, execute_pipeline_with_handoffs


def test_async_handoff_execution(runner, project_root, pipeline_config, tmp_path):
    spec_path = project_root / "tests" / "fixtures" / "min_spec.json"
    state = PipelineState(
        spec_path=spec_path,
        output_dir=tmp_path,
        config=pipeline_config,
    )

    result = asyncio.run(
        execute_pipeline_with_handoffs(
            spec_path=str(spec_path),
            output_dir=str(tmp_path),
            runner=runner,
            state=state,
        )
    )

    assert result.status == "completed"
    assert len(result.agents_executed) == 5
