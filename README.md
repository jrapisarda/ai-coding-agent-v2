# AgentForge Multi-Agent Pipeline

AgentForge implements the orchestration model defined in `docs/RFC.md`. It upgrades the platform to the 2025 OpenAI Agents SDK architecture, delivering a deterministic multi-agent workflow that still supports offline execution.

## Features
- RequirementsAnalysis -> CodeGeneration -> Testing -> Documentation -> QualityAssurance agents with explicit handoffs.
- CodeGeneration agent can call GPT-5 through the OpenAI Responses API when online, while retaining deterministic offline fallbacks.
- Offline-friendly tooling, SQLite persistence, and lightweight tracing for observability.
- Configurable GPT-5 family model parameters per agent.
- Deterministic unit, integration, and async end-to-end tests covering the full pipeline.

## Getting Started
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # optional: tooling and test stack
agentforge --spec tests/fixtures/min_spec.json --output _output
```

Run the full pipeline against the richer project plan specification:

```bash
agentforge --spec tests/fixtures/agent_project_plan.json --output _output/plan_run
```

### Configuration
Runtime configuration lives in `src/agentforge/config.py` and can be overridden via environment variables:

- `REQUIREMENTS_AGENT_MODEL` (and similarly for other agents) to adjust model names.
- `OPENAI_API_KEY` enables live code synthesis; unset or offline mode forces deterministic fallbacks.
- `AGENTFORGE_OFFLINE=1` to force offline execution.
- `AGENTFORGE_DB` to point to a different SQLite persistence file.

## Project Layout
- `src/agentforge/agents/`: concrete agent implementations and base classes.
- `src/agentforge/orchestration/`: pipeline runner, handoff coordination, parallel utilities.
- `src/agentforge/tools/`: deterministic tool adapters (schema validation, research, docs, QA).
- `src/agentforge/persistence/`: SQLite models and helpers.
- `tests/`: unit, integration, and e2e coverage using the sample spec.

## Testing
```bash
pytest
```

Generated artifacts are emitted into the chosen `--output` directory. All tests use local resources only, ensuring deterministic execution in CI and offline environments.

## Observability
- Structured logging controlled by `AGENTFORGE_LOG_LEVEL`.
- Tracing spans captured per agent via `PipelineRunner.tracer`.
- Agent execution metadata persisted in `.agentforge.sqlite`.

## Dependency Validation
- Runtime dependencies: `openai-agents>=1.0.0`, `jsonschema>=4.18.0`, `openai>=1.16.0`.
- Optional developer tools: `pytest`, `coverage`, `ruff`, `mypy`, `bandit`, `safety`.
- See `constraints.txt` for pinned versions when reproducibility is required.
