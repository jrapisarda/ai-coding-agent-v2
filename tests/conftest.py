from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

import pytest

from agentforge.config import load_config
from agentforge.agents import build_agents
from agentforge.observability.tracing import Tracer
from agentforge.orchestration.pipeline import PipelineRunner


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def _extend_sys_path(project_root: Path) -> None:
    src = project_root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


@pytest.fixture(scope="session")
def pipeline_config(project_root: Path):
    return load_config(base_dir=project_root)


@pytest.fixture()
def runner(project_root: Path, pipeline_config):
    tracer = Tracer()
    agents = build_agents(
        pipeline_config,
        docs_root=project_root / "docs",
        output_dir=project_root / "_output",
        schema_path=project_root / "src" / "agentforge" / "schema" / "spec_schema.json",
    )
    return PipelineRunner(agents=agents, config=pipeline_config, tracer=tracer)
