"""Offline deterministic client used for testing."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class OfflineLLMClient:
    """Produce deterministic canned responses for tests."""

    seed: int = 1337

    def __post_init__(self) -> None:
        random.seed(self.seed)

    async def complete(self, *, prompt: str, model: str) -> dict[str, Any]:
        """Return a deterministic structured response."""

        checksum = abs(hash((prompt, model, self.seed))) % 10000
        random_value = random.randint(0, 9999)
        return {
            "summary": f"Offline response for {model}",
            "details": {
                "checksum": checksum,
                "random": random_value,
            },
        }
