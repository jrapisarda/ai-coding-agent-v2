from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from agentforge.persistence.models import AgentRunRecord


def init_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                status TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def record_agent_runs(path: Path, records: Iterable[AgentRunRecord]) -> None:
    with sqlite3.connect(path) as conn:
        conn.executemany(
            """
            INSERT INTO agent_runs (agent_name, status, payload)
            VALUES (?, ?, ?)
            """,
            (
                (record.agent_name, record.status, json.dumps(record.payload, default=str))
                for record in records
            ),
        )
        conn.commit()


__all__ = ["init_db", "record_agent_runs"]
