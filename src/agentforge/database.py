"""SQLite persistence for AgentForge runs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import aiosqlite

from .config import settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT UNIQUE NOT NULL,
    spec_path TEXT NOT NULL,
    output_dir TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSON
);

CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL,
    input JSON,
    output JSON,
    error TEXT,
    retries INTEGER DEFAULT 0,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    step_id INTEGER,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    path TEXT NOT NULL,
    checksum TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

CREATE TABLE IF NOT EXISTS assumptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    assumption TEXT NOT NULL,
    rationale TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);
"""


async def init_db() -> None:
    """Initialize the SQLite database with required tables."""

    path = Path(settings.database_path)
    async with aiosqlite.connect(path) as db:
        await db.executescript(_SCHEMA)
        await db.commit()


async def record_run(
    *,
    run_id: str,
    spec_path: Path,
    output_dir: Path,
    status: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute(
            """
            INSERT INTO runs(run_id, spec_path, output_dir, status, metadata)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET status=excluded.status, metadata=excluded.metadata
            """,
            (run_id, str(spec_path), str(output_dir), status, json.dumps(metadata or {})),
        )
        await db.commit()


async def record_step(
    *,
    run_id: str,
    agent_name: str,
    status: str,
    input_payload: dict[str, Any] | None = None,
    output_payload: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute(
            """
            INSERT INTO steps(run_id, agent_name, status, input, output, error)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                agent_name,
                status,
                json.dumps(_serialize(input_payload or {})),
                json.dumps(_serialize(output_payload or {})),
                error,
            ),
        )
        await db.commit()


async def record_artifact(
    *, run_id: str, artifact_type: str, path: Path, checksum: str | None = None
) -> None:
    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute(
            """
            INSERT INTO artifacts(run_id, artifact_type, path, checksum)
            VALUES (?, ?, ?, ?)
            """,
            (run_id, artifact_type, str(path), checksum),
        )
        await db.commit()


async def rollback_run(run_id: str) -> None:
    """Delete recorded artifacts and mark a run as rolled back."""

    async with aiosqlite.connect(settings.database_path) as db:
        async with db.execute(
            "SELECT path FROM artifacts WHERE run_id = ?", (run_id,)
        ) as cursor:
            artifact_paths = [Path(row[0]) for row in await cursor.fetchall()]

    for path in artifact_paths:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute(
            "UPDATE runs SET status = 'rolled_back' WHERE run_id = ?",
            (run_id,),
        )
        await db.commit()


def _serialize(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "model_dump"):
        return _serialize(value.model_dump())
    if isinstance(value, dict):
        return {key: _serialize(val) for key, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize(item) for item in value]
    return value
