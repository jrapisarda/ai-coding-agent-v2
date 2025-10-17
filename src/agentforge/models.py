"""Pydantic models shared across agents."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl


class SpecArtifact(BaseModel):
    name: str
    description: str
    path: Path


class RequirementsInput(BaseModel):
    spec_path: Path = Field(description="Path to JSON spec file")
    output_dir: Path = Field(description="Target output directory")


class RequirementsOutput(BaseModel):
    requirements: list[str]
    assumptions: list[str]
    architecture: dict[str, Any]


class CodeGenerationInput(BaseModel):
    requirements: list[str]
    assumptions: list[str]
    output_dir: Path


class CodeGenerationOutput(BaseModel):
    generated_files: list[SpecArtifact]
    repositories: list[HttpUrl] | None = None


class TestingInput(BaseModel):
    output_dir: Path
    generated_files: list[SpecArtifact]


class TestingOutput(BaseModel):
    tests_run: list[str]
    coverage: float


class DocumentationInput(BaseModel):
    output_dir: Path
    generated_files: list[SpecArtifact]
    tests_run: list[str]


class DocumentationOutput(BaseModel):
    documentation_files: list[SpecArtifact]


class QualityAssuranceInput(BaseModel):
    output_dir: Path
    generated_files: list[SpecArtifact]
    documentation_files: list[SpecArtifact]


class QualityAssuranceOutput(BaseModel):
    checks: list[str]
    status: Literal["passed", "failed"]
