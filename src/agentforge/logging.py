"""Structured logging configuration for AgentForge."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, MutableMapping


def configure_logging(level: int | None = None) -> None:
    """Configure structured JSON logging for the application."""

    level = level or logging.INFO
    logger = logging.getLogger("agentforge")
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(_StructuredFormatter())
        logger.addHandler(handler)


class _StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload: MutableMapping[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "logger": record.name,
        }

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        for key, value in record.__dict__.items():
            if key.startswith("_structured_"):
                payload[key.removeprefix("_structured_")] = value

        return json.dumps(payload, sort_keys=True)
