"""
Lightweight tracing to capture agent execution metadata.
"""

from __future__ import annotations

import contextlib
import time
from dataclasses import dataclass, field
from typing import Dict, Generator, List


@dataclass(slots=True)
class Span:
    name: str
    start: float
    end: float | None = None
    tags: Dict[str, str] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        if self.end is None:
            return 0.0
        return (self.end - self.start) * 1000


@dataclass
class Tracer:
    spans: List[Span] = field(default_factory=list)

    @contextlib.contextmanager
    def span(self, name: str, **tags: str) -> Generator[Span, None, None]:
        span = Span(name=name, start=time.perf_counter(), tags=tags)
        self.spans.append(span)
        try:
            yield span
        finally:
            span.end = time.perf_counter()

    def to_dict(self) -> Dict[str, List[Dict[str, float | str]]]:
        return {
            "spans": [
                {"name": span.name, "duration_ms": span.duration_ms, **span.tags}
                for span in self.spans
            ]
        }


__all__ = ["Tracer", "Span"]
