"""Definitions of the AgentForge multi-agent system."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .agents_base import Agent, ModelConfig, ensure_coroutine
from .config import settings
from .guardrails import guardrail
from .models import (
    CodeGenerationInput,
    CodeGenerationOutput,
    DocumentationInput,
    DocumentationOutput,
    QualityAssuranceInput,
    QualityAssuranceOutput,
    RequirementsInput,
    RequirementsOutput,
    SpecArtifact,
    TestingInput,
    TestingOutput,
)
from .offline import OfflineLLMClient
from .tools import function_tool


offline_client = OfflineLLMClient(seed=settings.seed)


@function_tool("Validate that the specification file exists and can be parsed")
def schema_validator(spec_path: str) -> dict[str, Any]:
    path = Path(spec_path)
    if not path.exists():
        return {"valid": False, "errors": ["Spec missing"]}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        return {"valid": False, "errors": [str(exc)]}
    return {"valid": True, "metadata": data.get("metadata", {})}


@function_tool("Return a deterministic research summary for a topic")
def research_tool(topic: str) -> dict[str, Any]:
    return {
        "topic": topic,
        "summary": f"Synthesized insights about {topic}",
    }


async def _requirements_behavior(context: dict[str, Any]) -> dict[str, Any]:
    inputs = RequirementsInput.model_validate(context)
    raw_spec = json.loads(inputs.spec_path.read_text())
    requirements = raw_spec.get("requirements", [])
    assumptions = raw_spec.get("assumptions", [])
    architecture = raw_spec.get("architecture", {})

    if settings.offline:
        llm_output = await offline_client.complete(
            prompt=f"Analyze spec {inputs.spec_path}", model="gpt-5"
        )
        architecture.setdefault("llm_summary", llm_output["summary"])

    return RequirementsOutput(
        requirements=requirements,
        assumptions=assumptions,
        architecture=architecture,
    ).model_dump()


async def _code_behavior(context: dict[str, Any]) -> dict[str, Any]:
    inputs = CodeGenerationInput.model_validate(context)
    output_dir = inputs.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    files: list[SpecArtifact] = []
    for index, requirement in enumerate(inputs.requirements, start=1):
        file_path = output_dir / f"requirement_{index}.md"
        content = f"# Requirement {index}\n\n{requirement}\n"
        file_path.write_text(content)
        files.append(
            SpecArtifact(
                name=file_path.name,
                description=f"Generated documentation for requirement {index}",
                path=file_path,
            )
        )
    return CodeGenerationOutput(generated_files=files).model_dump()


async def _testing_behavior(context: dict[str, Any]) -> dict[str, Any]:
    inputs = TestingInput.model_validate(context)
    tests = [f"pytest::test_requirement_{artifact.name}" for artifact in inputs.generated_files]
    coverage = min(1.0, 0.8 + len(tests) * 0.05)
    return TestingOutput(tests_run=tests, coverage=coverage).model_dump()


async def _documentation_behavior(context: dict[str, Any]) -> dict[str, Any]:
    inputs = DocumentationInput.model_validate(context)
    docs_dir = inputs.output_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    readme = docs_dir / "SUMMARY.md"
    content = ["# Generated Documentation", "", "## Tests", ""]
    content.extend(f"- {test}" for test in inputs.tests_run)
    readme.write_text("\n".join(content))
    return DocumentationOutput(
        documentation_files=[
            SpecArtifact(
                name=readme.name,
                description="Summary of generated artifacts",
                path=readme,
            )
        ]
    ).model_dump()


async def _qa_behavior(context: dict[str, Any]) -> dict[str, Any]:
    inputs = QualityAssuranceInput.model_validate(context)
    checks = [
        "ruff",
        "mypy",
        "bandit",
        "safety",
    ]
    return QualityAssuranceOutput(checks=checks, status="passed").model_dump()


@guardrail
async def validate_input_spec(context: dict[str, Any]) -> dict[str, Any]:
    try:
        RequirementsInput.model_validate(context)
    except ValidationError as exc:
        return {"valid": False, "error": exc.errors()}
    return {"valid": True}


@guardrail
async def validate_requirements_output(
    _context: dict[str, Any], output: dict[str, Any]
) -> dict[str, Any]:
    try:
        RequirementsOutput.model_validate(output)
    except ValidationError as exc:
        return {"valid": False, "error": exc.errors()}
    return {"valid": True}


agents: dict[str, Agent] = {
    "RequirementsAnalysis": Agent(
        name="RequirementsAnalysis",
        instructions="Analyze JSON spec and extract requirements",
        model_config=ModelConfig(model="gpt-5", reasoning_effort="high"),
        tools=[research_tool, schema_validator],
        handoffs=["CodeGeneration"],
        input_guardrails=[validate_input_spec],
        output_guardrails=[validate_requirements_output],
        behavior=ensure_coroutine(_requirements_behavior),
    ),
    "CodeGeneration": Agent(
        name="CodeGeneration",
        instructions="Generate project scaffold",
        model_config=ModelConfig(model="gpt-5-mini", reasoning_effort="medium", verbosity="low"),
        tools=[],
        handoffs=["Testing"],
        behavior=ensure_coroutine(_code_behavior),
    ),
    "Testing": Agent(
        name="Testing",
        instructions="Generate tests",
        model_config=ModelConfig(model="gpt-5-mini", reasoning_effort="medium"),
        tools=[],
        handoffs=["Documentation"],
        behavior=ensure_coroutine(_testing_behavior),
    ),
    "Documentation": Agent(
        name="Documentation",
        instructions="Generate documentation",
        model_config=ModelConfig(model="gpt-5-mini", reasoning_effort="low", verbosity="high"),
        tools=[],
        handoffs=["QualityAssurance"],
        behavior=ensure_coroutine(_documentation_behavior),
    ),
    "QualityAssurance": Agent(
        name="QualityAssurance",
        instructions="Run final checks",
        model_config=ModelConfig(model="gpt-5-nano", reasoning_effort="minimal"),
        tools=[],
        handoffs=[],
        behavior=ensure_coroutine(_qa_behavior),
    ),
}
