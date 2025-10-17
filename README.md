# AgentForge Multi-Agent Orchestration

AgentForge is a reference implementation of the orchestration strategy defined in [`docs/RFC.md`](docs/RFC.md). The project demonstrates a five-agent workflow built on top of Python async primitives, Pydantic validation, and SQLite persistence. It is intentionally designed to run entirely offline while providing hooks that mirror the OpenAI Agents SDK patterns described in the RFC.

## Features

- Five coordinated agents (RequirementsAnalysis → CodeGeneration → Testing → Documentation → QualityAssurance)
- Structured Pydantic models and guardrails for inputs and outputs
- SQLite persistence layer recording runs, steps, and artifacts
- Deterministic offline LLM client seeded via environment variables
- Sequential and parallel orchestration patterns
- Click-powered CLI to execute the pipeline end-to-end

## Installation

```bash
python3.13 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .[dev]
```

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | _unset_ | Used for live mode (not required for offline tests). |
| `AGENTFORGE_OFFLINE` | `1` | When `1`, uses the deterministic offline client. |
| `AGENTFORGE_DB` | `.agentforge.sqlite` | SQLite database path. |
| `AGENTFORGE_SEED` | `1337` | Seed applied to the offline LLM client. |
| `AGENTFORGE_MODEL` | `gpt-5-mini` | Default model label recorded for telemetry. |
| `AGENTFORGE_REASONING_EFFORT` | `medium` | Recorded reasoning effort hint. |
| `AGENTFORGE_VERBOSITY` | `medium` | Recorded verbosity hint. |

## Usage

1. Prepare a JSON specification file. A sample is provided at `tests/tests_data/sample_spec.json`.
2. Run the pipeline:
   ```bash
   agentforge run tests/tests_data/sample_spec.json build/artifacts
   ```
3. Generated requirement markdown files will be placed in the output directory along with a documentation summary.
4. Inspect `.agentforge.sqlite` (or your configured path) for run telemetry.

## Testing

```bash
pytest
```

## Project Structure

- `src/agentforge/agents.py` – definitions for all five agents and supporting tools
- `src/agentforge/orchestrator.py` – pipeline orchestrator implementing sequential and parallel patterns
- `src/agentforge/database.py` – SQLite persistence and rollback utilities
- `src/agentforge/cli.py` – command line interface entry points
- `tests/` – asynchronous tests verifying pipeline execution and persistence

## Extensibility

The codebase mirrors the RFC requirements and can be extended to integrate the official OpenAI Agents SDK by replacing the offline client with the real SDK calls, implementing tracing processors, and enriching the tool implementations.
