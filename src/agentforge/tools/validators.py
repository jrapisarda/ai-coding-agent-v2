from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentforge.agents.base import Tool

try:
    import jsonschema
except ModuleNotFoundError:  # pragma: no cover - fallback for offline usage
    jsonschema = None


@dataclass(slots=True)
class SchemaValidatorTool:
    """Validate a JSON document against the project schema."""

    schema_path: Path
    name: str = "schema_validator"
    _compiled_schema: Optional[Any] = None

    def _load_schema(self) -> Dict[str, Any]:
        return json.loads(self.schema_path.read_text(encoding="utf-8"))

    def _ensure_compiled(self) -> None:
        if self._compiled_schema is not None or jsonschema is None:
            return
        schema = self._load_schema()
        self._compiled_schema = jsonschema.Draft202012Validator(schema)

    def execute(self, document: Dict[str, Any]) -> List[str]:
        """
        Validate and return warnings. Raises on fatal errors.
        """
        if jsonschema is None:
            # Minimal structural check to ensure required keys exist.
            required = {"project", "requirements"}
            missing = sorted(required - document.keys())
            return [f"jsonschema unavailable; skipped validation. Missing keys: {missing}"]

        self._ensure_compiled()
        assert self._compiled_schema is not None
        errors = sorted(self._compiled_schema.iter_errors(document), key=lambda e: e.path)
        return [f"{'/'.join([str(s) for s in err.path])}: {err.message}" for err in errors]


__all__ = ["SchemaValidatorTool"]
