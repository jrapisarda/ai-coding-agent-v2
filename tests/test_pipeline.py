from __future__ import annotations

import asyncio
from pathlib import Path

import aiosqlite
import pytest

from agentforge.agents import agents
from agentforge.orchestrator import AgentRunner


def _run_async(async_fn, /, *args, **kwargs):
    return asyncio.run(async_fn(*args, **kwargs))


def test_pipeline_execution(tmp_path: Path) -> None:
    spec = Path(__file__).parent / "tests_data" / "sample_spec.json"
    runner = AgentRunner(agents=agents)
    context = _run_async(runner.run, spec_path=spec, output_dir=tmp_path)

    assert "generated_files" in context
    assert any(tmp_path.glob("requirement_*.md"))
    summary = tmp_path / "docs" / "SUMMARY.md"
    assert summary.exists()


def test_pipeline_records_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    spec = Path(__file__).parent / "tests_data" / "sample_spec.json"
    db_path = tmp_path / "test.sqlite"
    monkeypatch.setenv("AGENTFORGE_DB", str(db_path))
    monkeypatch.setenv("AGENTFORGE_OFFLINE", "1")

    from importlib import reload

    import agentforge.config as config_module
    import agentforge.database as database_module

    reload(config_module)
    reload(database_module)
    from agentforge.orchestrator import AgentRunner as ReloadedRunner

    _run_async(ReloadedRunner(agents=agents).run, spec_path=spec, output_dir=tmp_path)

    async def fetch_count() -> int:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM runs") as cursor:
                (count,) = await cursor.fetchone()
                return count

    count = _run_async(fetch_count)
    assert count == 1
