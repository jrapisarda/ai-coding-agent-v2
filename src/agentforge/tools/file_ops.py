from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(slots=True)
class FileWriterTool:
    """Persist structured artifacts to disk."""

    output_dir: Path
    name: str = "file_writer"

    def execute(self, relative_path: str, contents: str, base_dir: Optional[Path] = None) -> Dict[str, Any]:
        target_root = base_dir or self.output_dir
        target = target_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents, encoding="utf-8")
        return {"path": str(target)}


__all__ = ["FileWriterTool"]
