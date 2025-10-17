Implementation Plan
Environment & Tooling Setup

Establish Python 3.13 virtualenv, install dev extras under pinned constraints, and configure pre-commit to align with the documented workflow.

Capture optional bootstrap path (fresh git init) to support clean-room runs when generating new scaffolds.

CLI Entrypoint & Configuration Surface

Implement agentforge CLI (and python -m agentforge.cli) that accepts JSON spec + output directory, validates inputs against the bundled schema, and wires configuration such as offline mode, deterministic seed, and optional environment overrides.

Agent Orchestration Pipeline

Define composable agents (RequirementsAnalysis, CodeGeneration, Testing, Documentation, QualityAssurance) executed as discrete, logged steps with configurable retries/backoff and artifact management, matching the summarized multi-agent architecture.

Deterministic Offline Mode & Live Extensibility

Honor AGENTFORGE_OFFLINE and AGENTFORGE_SEED to toggle deterministic stubs for LLM/research, while permitting live integrations via configurable OpenAI-compatible endpoints (default kimi-k2-0905-preview) and DuckDuckGo scraping with caching when online.

Persistence, Observability & Rollback

Back pipeline state with SQLite (.agentforge.sqlite) capturing runs/steps/logs/artifacts/assumptions, provide inspection helpers, ensure WAL compatibility, and guarantee artifact rollback semantics on failure.

Output Generation & Git Automation

Materialize project scaffold in requested output dir, initialize git repo, and structure commits by phase to reflect pipeline progress, aligning with documented expectations.

Quality Gates & Testing Strategy

Integrate lint/format/type (Ruff, Black, MyPy) and security gates (Bandit, Safety) alongside pytest coverage ≥80%, plus targeted smoke suites (offline CLI).

Operational Playbooks & Troubleshooting

Document runbooks for deterministic runs, schema validation, logging escalation, CI parity checks, optional Docker usage, and known limitations (e.g., concurrency, research rate limits).