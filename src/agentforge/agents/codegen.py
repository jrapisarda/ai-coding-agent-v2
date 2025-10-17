from __future__ import annotations

import textwrap
from typing import Dict, List, Tuple

from agentforge.agents.base import BaseAgent
from agentforge.orchestration.pipeline import PipelineState


def _slugify(name: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in name).strip("_") or "artifact"


class CodeGenerationAgent(BaseAgent):
    """Create a lightweight project scaffold derived from requirements."""

    def _run(
        self,
        state: PipelineState,
        events: List[str],
    ) -> tuple[Dict[str, str], Dict[str, str], List[str]]:
        files: Dict[str, str] = {}
        file_writer = self.get_tool("file_writer")
        git_ops = self.get_tool("git_operations")

        for index, requirement in enumerate(state.requirements, start=1):
            filename = f"src/generated/{index:02d}_{_slugify(requirement)}.py"
            content = textwrap.dedent(
                f"""
                \"\"\"Generated artifact for requirement: {requirement}\"\"\"


                def summary() -> str:
                    return "{requirement}"
                """
            ).strip() + "\n"
            file_writer.execute(filename, content, base_dir=state.output_dir)
            files[filename] = content

        if files:
            file_writer.execute("src/generated/__init__.py", "__all__ = []\n", base_dir=state.output_dir)
            files["src/generated/__init__.py"] = "__all__ = []\n"
            manifest_contents = "\n".join(f"- {path}" for path in sorted(files))
            file_writer.execute("src/generated/MANIFEST.md", manifest_contents, base_dir=state.output_dir)
            files["src/generated/MANIFEST.md"] = manifest_contents

        git_ops.execute("add generated artifacts", dry_run=True)

        state.project_files = files
        events.append(f"files_generated={len(files)}")

        return (
            {"files_generated": str(len(files))},
            {"manifest": sorted(files)},
            [],
        )
