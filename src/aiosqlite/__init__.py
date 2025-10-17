"""Lightweight async wrapper around sqlite3 for offline tests."""

from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path
from typing import Any, Iterable


class Cursor:
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        self._cursor = cursor

    async def fetchall(self) -> list[tuple[Any, ...]]:
        return self._cursor.fetchall()

    async def fetchone(self) -> tuple[Any, ...] | None:
        return self._cursor.fetchone()

    async def __aenter__(self) -> "Cursor":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self._cursor.close()


class _ExecuteContext:
    def __init__(self, connection: sqlite3.Connection, sql: str, parameters: Iterable[Any]) -> None:
        self._connection = connection
        self._sql = sql
        self._parameters = tuple(parameters)
        self._cursor: Cursor | None = None

    async def _get_cursor(self) -> Cursor:
        if self._cursor is None:
            cursor = self._connection.execute(self._sql, self._parameters)
            self._cursor = Cursor(cursor)
        return self._cursor

    def __await__(self):  # pragma: no cover
        return self._get_cursor().__await__()

    async def __aenter__(self) -> Cursor:
        return await self._get_cursor()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._cursor is not None:
            await self._cursor.__aexit__(exc_type, exc, tb)


class Connection:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    async def executescript(self, script: str) -> None:
        self._connection.executescript(script)

    def execute(self, sql: str, parameters: Iterable[Any] | None = None) -> _ExecuteContext:
        if parameters is None:
            parameters = []
        return _ExecuteContext(self._connection, sql, parameters)

    async def commit(self) -> None:
        self._connection.commit()

    async def close(self) -> None:
        self._connection.close()

    async def __aenter__(self) -> "Connection":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()


class _ConnectionFactory:
    def __init__(self, path: str | Path) -> None:
        self._path = path
        self._connection: Connection | None = None

    async def _get(self) -> Connection:
        if self._connection is None:
            raw = sqlite3.connect(str(self._path))
            raw.row_factory = sqlite3.Row
            self._connection = Connection(raw)
        return self._connection

    def __await__(self):  # pragma: no cover - convenience
        return self._get().__await__()

    async def __aenter__(self) -> Connection:
        return await self._get()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None


def connect(path: str | Path) -> _ConnectionFactory:
    return _ConnectionFactory(path)
