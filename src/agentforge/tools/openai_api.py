from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(slots=True)
class OpenAICodeGenerationTool:
    """Leverage the OpenAI Responses API to synthesize source files."""

    model: str
    reasoning_effort: str = "medium"
    name: str = "code_synthesis"
    offline: bool = True
    _client: Any = None

    def __post_init__(self) -> None:
        if self.offline:
            return

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return

        try:
            from openai import OpenAI  # type: ignore

            self._client = OpenAI(api_key=api_key)
        except Exception:
            self._client = None

    @property
    def is_online(self) -> bool:
        return self._client is not None and not self.offline

    def execute(
        self,
        prompt: str,
        *,
        instructions: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.is_online:
            return {
                "status": "offline",
                "files": [],
            }

        try:
            payload = {
                "model": model or self.model,
                "reasoning": {"effort": self.reasoning_effort},
                "input": [
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": instructions
                                or "Respond with JSON containing a `files` array where each entry has `path` and `contents`.",
                            }
                        ],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            }
                        ],
                    },
                ],
            }
            if response_format:
                payload["response_format"] = response_format

            response = self._client.responses.create(**payload)  # type: ignore[call-arg,attr-defined]
            text_output = _extract_text(response)
            data = json.loads(text_output)
            files = data.get("files") or []
            return {
                "status": "ok",
                "files": files,
                "raw": data,
            }
        except Exception as exc:  # pragma: no cover - exercised only with live API
            return {
                "status": "error",
                "error": str(exc),
                "files": [],
            }


def _extract_text(response: Any) -> str:
    """Best-effort extraction of text from an OpenAI Responses API payload."""
    if hasattr(response, "output_text"):
        return response.output_text  # type: ignore[return-value]

    # Fall back to traversing structured output.
    output = getattr(response, "output", None)
    if output:
        for item in output:
            content = item.get("content") if isinstance(item, dict) else getattr(item, "content", None)
            if not content:
                continue
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    value = part.get("text")
                    if isinstance(value, dict):
                        value = value.get("value")
                    if isinstance(value, str):
                        return value
                value = getattr(part, "text", None)
                if isinstance(value, str):
                    return value

    raise ValueError("Unable to extract text from OpenAI response")


__all__ = ["OpenAICodeGenerationTool"]
