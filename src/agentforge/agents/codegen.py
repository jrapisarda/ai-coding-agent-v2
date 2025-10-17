from __future__ import annotations

import textwrap
from typing import Any, Dict, List, Tuple

from agentforge.agents.base import BaseAgent
from agentforge.orchestration.pipeline import PipelineState


def _slugify(name: str, max_len: int = 60) -> str:
    slug = "".join(char.lower() if char.isalnum() else "_" for char in name)
    slug = "_".join(filter(None, slug.split("_")))
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("_")
    return slug or "artifact"


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
        code_tool = self.get_tool("code_synthesis")

        model_files = self._synthesize_with_model(code_tool, state, events)
        if model_files:
            for entry in model_files:
                path = entry.get("path") or entry.get("file") or entry.get("name")
                contents = entry.get("contents") or entry.get("content")
                if not path or contents is None:
                    continue
                path = str(path).strip()
                file_writer.execute(path, contents, base_dir=state.output_dir)
                files[path] = contents
        else:
            files.update(self._fallback_synthetic_files(state, file_writer))

        plan_summary = self._render_plan_summary(state.metadata.get("requirements"))
        if plan_summary:
            plan_summary_path = "docs/plan_summary.md"
            file_writer.execute(plan_summary_path, plan_summary, base_dir=state.output_dir)
            files[plan_summary_path] = plan_summary

        if files:
            manifest_contents = "\n".join(f"- {path}" for path in sorted(files))
            file_writer.execute("MANIFEST.md", manifest_contents, base_dir=state.output_dir)
            files["MANIFEST.md"] = manifest_contents

            generated_paths = sorted(path for path in files if path.startswith("src/generated/"))
            if generated_paths:
                generated_manifest = "\n".join(f"- {path}" for path in generated_paths)
                file_writer.execute("src/generated/MANIFEST.md", generated_manifest, base_dir=state.output_dir)
                files["src/generated/MANIFEST.md"] = generated_manifest

        git_ops.execute("add generated artifacts", dry_run=True)

        state.project_files = files
        events.append(f"files_generated={len(files)}")

        return (
            {"files_generated": str(len(files))},
            {"manifest": sorted(files)},
            [],
        )

    def _render_plan_summary(self, requirements_meta: Any) -> str:
        if not isinstance(requirements_meta, dict):
            return ""

        lines: List[str] = ["# Plan Summary", ""]
        overview = requirements_meta.get("overview")
        if overview:
            lines.extend(["## Overview", overview.strip(), ""])

        for section_name, key in (
            ("Goals", "goals"),
            ("Assumptions", "assumptions"),
        ):
            items = requirements_meta.get(key) or []
            if items:
                lines.append(f"## {section_name}")
                lines.extend(f"- {item}" for item in items)
                lines.append("")

        scope = requirements_meta.get("scope")
        if isinstance(scope, dict):
            lines.append("## Scope")
            for label, entries in scope.items():
                lines.append(f"### {label.capitalize()}")
                lines.extend(f"- {entry}" for entry in entries)
            lines.append("")

        user_stories = requirements_meta.get("user_stories") or []
        if user_stories:
            lines.append("## User Stories")
            lines.extend(f"- {story}" for story in user_stories)
            lines.append("")

        return "\n".join(line.rstrip() for line in lines if line is not None)

    def _synthesize_with_model(self, code_tool, state: PipelineState, events: List[str]) -> List[Dict[str, Any]]:
        prompt = self._build_generation_prompt(state)
        response = code_tool.execute(
            prompt,
            instructions=(
                "You are the CodeGeneration agent for AgentForge. "
                "Respond with JSON containing a `files` array. Each file needs `path` and `contents` keys. "
                "Prefer Python scaffolding when the requirements are ambiguous. "
                "Do not include explanations outside the JSON response."
            ),
            response_format={"type": "json_object"},
            model=self.config.model.name,
        )

        status = response.get("status")
        if status == "ok" and response.get("files"):
            events.append("codegen:model=online")
            return list(response["files"])

        events.append(f"codegen:model_status={status}")
        return []

    def _build_generation_prompt(self, state: PipelineState) -> str:
        metadata = state.metadata.get("requirements") or {}
        overview = metadata.get("overview", "")
        goals = "\n".join(f"- {item}" for item in metadata.get("goals", []))
        assumptions = "\n".join(f"- {item}" for item in metadata.get("assumptions", []))
        scope = metadata.get("scope", {})
        scope_lines = []
        if isinstance(scope, dict):
            for label, entries in scope.items():
                scope_lines.append(f"{label.capitalize()}:\n" + "\n".join(f"  - {entry}" for entry in entries))
        scope_text = "\n".join(scope_lines)
        requirements_text = "\n".join(f"- {req}" for req in state.requirements)

        prompt = textwrap.dedent(
            f"""
            Project: {state.metadata.get("project", {}).get("name", "AgentForge Project")}
            Overview:
            {overview}

            Goals:
            {goals}

            Assumptions:
            {assumptions}

            Scope:
            {scope_text}

            Normalized Requirements:
            {requirements_text}

            Generate code artifacts that satisfy the scope. Ensure the primary entrypoint is a CLI that can orchestrate the agents.
            Include README guidance and minimal tests mirroring the generated modules.
            """
        ).strip()
        return prompt

    def _fallback_synthetic_files(self, state: PipelineState, file_writer) -> Dict[str, str]:
        files: Dict[str, str] = {}
        for index, requirement in enumerate(state.requirements, start=1):
            filename = f"src/generated/{index:02d}_{_slugify(requirement)}.py"
            content = textwrap.dedent(
                f"""
                \"\"\"Generated artifact for requirement: {requirement}\"\"\"


                def summary() -> str:
                    return \"{requirement}\"
                """
            ).strip() + "\n"
            file_writer.execute(filename, content, base_dir=state.output_dir)
            files[filename] = content

        if files:
            file_writer.execute("src/generated/__init__.py", "__all__ = []\n", base_dir=state.output_dir)
            files["src/generated/__init__.py"] = "__all__ = []\n"

        return files
