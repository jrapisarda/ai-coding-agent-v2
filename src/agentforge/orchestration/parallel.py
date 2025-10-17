"""
Parallel execution helpers.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, List, TypeVar

T = TypeVar("T")


def run_in_parallel(callables: Iterable[Callable[[], T]], max_workers: int = 4) -> List[T]:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(func) for func in callables]
        return [future.result() for future in as_completed(futures)]


__all__ = ["run_in_parallel"]
