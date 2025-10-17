from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - import optional dependency lazily
    import requests
except ModuleNotFoundError:  # pragma: no cover - handled in execute
    requests = None  # type: ignore


@dataclass(slots=True)
class ResearchTool:
    """Research helper with optional live DuckDuckGo integration."""

    docs_root: Path
    offline: bool = True
    name: str = "research_tool"
    _session: Optional["requests.Session"] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.offline:
            return

        if requests is None:
            return

        try:
            self._session = requests.Session()
        except Exception:  # pragma: no cover - defensive fallback
            self._session = None

    def execute(self, query: str) -> Dict[str, Any]:
        """Return research hits from local docs and, when allowed, the web."""

        local_matches = self._search_local_docs(query)
        if self.offline or self._session is None:
            return {
                "query": query,
                "matches": local_matches,
                "mode": "offline",
            }

        live_matches = self._search_live(query)
        combined = live_matches or local_matches
        payload: Dict[str, Any] = {
            "query": query,
            "matches": combined,
            "mode": "online",
        }
        if local_matches:
            payload["local_support"] = local_matches
        return payload

    def _search_local_docs(self, query: str) -> List[str]:
        matches: List[str] = []
        for path in self.docs_root.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            if query.lower() in text.lower():
                matches.append(f"{path.name}: {query}")
        return matches

    def _search_live(self, query: str) -> List[str]:
        assert self._session is not None

        try:
            response = self._session.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": "1",
                    "no_redirect": "1",
                },
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:  # pragma: no cover - network only
            return []

        matches: List[str] = []
        for topic in payload.get("RelatedTopics", []):
            if isinstance(topic, dict):
                text = topic.get("Text") or topic.get("FirstURL")
                if text:
                    matches.append(str(text))
            elif isinstance(topic, list):
                for item in topic:
                    if isinstance(item, dict):
                        text = item.get("Text") or item.get("FirstURL")
                        if text:
                            matches.append(str(text))
        abstract = payload.get("AbstractText")
        if abstract:
            matches.insert(0, str(abstract))
        return matches


__all__ = ["ResearchTool"]
