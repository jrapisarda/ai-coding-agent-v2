"""Multi-agent orchestration pipeline."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from agents import Agent, set_default_openai_key
from agents.model_settings import ModelSettings
from agents.run import Runner
from openai import AsyncOpenAI

from ..config import AgentRuntimeSettings
from ..context import AgentRunState
from ..plan import AgentProjectPlan
from ..tools.filesystem import TOOLS as FILESYSTEM_TOOLS


@dataclass(slots=True)
class AgentSpec:
    """Declarative specification for an agent participating in the workflow."""

    name: str
    instructions: str


class MultiAgentPipeline:
    """Coordinates Requirements → Coding → Testing → Documentation agents."""

    def __init__(
        self,
        *,
        workspace: Path,
        plan: AgentProjectPlan,
        settings: AgentRuntimeSettings | None = None,
        openai_client: AsyncOpenAI | None = None,
    ) -> None:
        self.workspace = workspace
        self.plan = plan
        self.settings = settings or AgentRuntimeSettings()
        self._client = openai_client or AsyncOpenAI()
        self.runner = Runner()
        self.agents = self._build_agents()

    def _build_agents(self) -> list[AgentSpec]:
        prompt_block = self.plan.to_prompt_block()

        def base_instructions(role: str, focus: str) -> str:
            return (
                f"You are the {role} agent in a coordinated GPT-5 workflow. "
                f"Focus on {focus}. Always use tools for filesystem or logging operations. "
                "You share a workspace with other agents; prefer incremental updates via write_many."
            )

        requirements = AgentSpec(
            name="requirements",
            instructions=base_instructions(
                "Requirements",
                "extracting structured requirements, clarifying ambiguities, and preparing downstream context",
            ),
        )
        coding = AgentSpec(
            name="coding",
            instructions=base_instructions(
                "Coding",
                "producing code scaffolds, dependency manifests, and automation scripts based on requirements context",
            ),
        )
        testing = AgentSpec(
            name="testing",
            instructions=base_instructions(
                "Testing",
                "designing and executing automated tests, recording outcomes, and suggesting fixes",
            ),
        )
        documentation = AgentSpec(
            name="documentation",
            instructions=base_instructions(
                "Documentation",
                "writing concise READMEs, runbooks, and provenance logs",
            ),
        )
        return [requirements, coding, testing, documentation]

    def _instantiate_agent(self, spec: AgentSpec) -> Agent[AgentRunState]:
        agent_kwargs = {
            "name": spec.name,
            "instructions": spec.instructions,
            "tools": FILESYSTEM_TOOLS,
            "model": self.settings.model,
        }
        if self.settings.temperature is not None:
            agent_kwargs["model_settings"] = ModelSettings(temperature=self.settings.temperature)

        return Agent(**agent_kwargs)

    @staticmethod
    def _summarize_markdown(text: str, limit: int = 400) -> str:
        segments = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            segments.append(stripped)
            snippet = " ".join(segments)
            if len(snippet) >= limit:
                break
        summary = " ".join(segments)
        if len(summary) > limit:
            summary = summary[:limit].rstrip() + "..."
        return summary or "_No content available._"

    def _emit_requirements_summary(self, state: AgentRunState) -> str | None:
        requirements_dir = self.workspace / "requirements"
        if not requirements_dir.exists():
            state.log("No requirements directory found; skipping requirements summary.")
            return None

        md_files = sorted(requirements_dir.glob("*.md"))
        if not md_files:
            state.log("No markdown requirements files detected; skipping summary.")
            return None

        artifacts_dir = self.workspace / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        summary_path = artifacts_dir / "requirements_summary.md"

        lines = [
            "# Requirements Summary",
            "",
            f"Generated from {len(md_files)} markdown file(s) in `requirements/`.",
            "",
        ]

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
            except OSError as exc:
                state.log(f"Failed to read {md_file}: {exc}")
                continue

            relative = md_file.relative_to(self.workspace)
            lines.append(f"## {relative}")
            lines.append("")
            lines.append(self._summarize_markdown(content))
            lines.append("")

        summary_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        state.add_artifact("requirements_summary_path", str(summary_path))
        state.log(f"Requirements summary written to {summary_path}")
        try:
            return summary_path.read_text(encoding="utf-8")
        except OSError as exc:
            state.log(f"Failed to read generated summary {summary_path}: {exc}")
            return None

    async def _run_agent(
        self,
        spec: AgentSpec,
        state: AgentRunState,
        input_text: str,
    ) -> None:
        agent = self._instantiate_agent(spec)
        await self.runner.run(
            agent,
            input_text,
            context=state,
            max_turns=self.settings.max_turns,
        )

    async def run(self, prompt: str) -> AgentRunState:
        """Run the end-to-end pipeline and return the final run state."""

        state = AgentRunState(workspace=self.workspace, plan=self.plan)
        state.log("Pipeline start")
        plan_summary = self.plan.to_prompt_block()
        state.add_artifact("requirements_summary", plan_summary)

        # Sequence through each agent, feeding forward summaries.
        plan_prompt_block = self.plan.to_prompt_block()
        await self._run_agent(
            self.agents[0],
            state,
            f"{prompt}\n\n{plan_prompt_block}",
        )
        summary_text = self._emit_requirements_summary(state)
        if summary_text:
            state.add_artifact("requirements_summary", summary_text)
        state.add_artifact(
            "coding_summary",
            "Coding agent must transform requirements into code plans using write_many and record_event.",
        )
        await self._run_agent(
            self.agents[1],
            state,
            "Leverage the requirements_summary artifact to scaffold the repository.",
        )
        state.add_artifact(
            "testing_summary",
            "Ensure tests exist for generated components and capture results to the log via record_event.",
        )
        await self._run_agent(
            self.agents[2],
            state,
            "Review code artifacts and contribute pytest or smoke test coverage.",
        )
        await self._run_agent(
            self.agents[3],
            state,
            "Summarize the run, produce README content, and reference recorded events.",
        )
        state.log("Pipeline complete")
        return state


def run_pipeline(
    *,
    workspace: Path,
    plan: AgentProjectPlan,
    settings: AgentRuntimeSettings | None = None,
    openai_key: str | None = None,
    prompt: str,
) -> AgentRunState:
    """Convenience synchronous wrapper around :class:`MultiAgentPipeline`."""

    if openai_key:
        set_default_openai_key(openai_key)
    pipeline = MultiAgentPipeline(workspace=workspace, plan=plan, settings=settings)
    return asyncio.run(pipeline.run(prompt))
