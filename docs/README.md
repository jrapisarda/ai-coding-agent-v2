# Generated README

## Summary
- AgentForge is a single-CLI, multi-agent pipeline that generates full project scaffolding from a JSON spec. Agents include RequirementsAnalysis, CodeGeneration, Testing, Documentation, and QualityAssurance.

## Quickstart
Prerequisites
- Python 3.13
- Git
- sqlite3 CLI (for quick inspection)
- Optional: Docker, Make
- Create and activate a virtualenv:
- python3.13 -m venv .venv
- source .venv/bin/activate
- pip install -U pip
- pip install -e .[dev] -c constraints.txt
- pre-commit install
First run (deterministic offline smoke)
- export AGENTFORGE_OFFLINE=1
- export AGENTFORGE_SEED=1337
- agentforge --spec tests/fixtures/min_spec.json --output-dir ./_output
- Equivalent invocation:
- python -m agentforge.cli --spec tests/fixtures/min_spec.json --output-dir ./_output
Bootstrap (optional, new empty directory)
- mkdir -p agentforge && cd agentforge
- git init
- python3.13 -m venv .venv
- source .venv/bin/activate
- python -m pip install -U pip
- Then create or clone the project and install as above.
- Lint & Type
- Test
- Steps include:
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
- pip install -e .[dev] -c constraints.txt
- ruff, black, mypy, pytest with coverage
Reproducibility and Determinism
Offline mode (default)
- Set AGENTFORGE_OFFLINE=1 to disable networked I/O and use seeded LLM/research stubs.
- Set AGENTFORGE_SEED to a fixed value for deterministic outputs.
- Jitter is forced to 0 in offline/tests; time.sleep may be patched to a no-op in unit tests to keep them fast.
- Toolchain is pinned via constraints.txt for consistent environments.
Retry and backoff
- Step-level capped exponential backoff:
- attempts: 3 (configurable per step)
- base delay: 0.2s
- factor: 2.0 → delays: 0.2s, 0.4s, 0.8s
- cap: 2.0s
- jitter: 0.0 in offline/tests; ±10% decorrelated jitter in live mode
- On failure after retries: emit a structured error, mark the step failed, roll back artifacts.
SQLite persistence and observability
Database
- Default path: .agentforge.sqlite
- Tables: runs, steps, logs, artifacts, assumptions, research_cache
- WAL mode may be enabled for performance.
Inspect state (examples)
- sqlite3 .agentforge.sqlite ".tables"
- sqlite3 .agentforge.sqlite "SELECT * FROM runs ORDER BY id DESC LIMIT 3;"
- sqlite3 .agentforge.sqlite "SELECT * FROM steps WHERE run_id=<id> ORDER BY id;"
- sqlite3 .agentforge.sqlite "SELECT level, message FROM logs WHERE run_id=<id> ORDER BY id LIMIT 50;"
- sqlite3 .agentforge.sqlite "SELECT * FROM artifacts WHERE run_id=<id>;"
- sqlite3 .agentforge.sqlite "SELECT * FROM assumptions WHERE run_id=<id>;"
Rollback verification
- Confirm artifact files referenced in artifacts were deleted.
- The run is marked rolled_back and no temp directories remain.
Inputs and Outputs
Inputs
- Spec JSON validated against src/agentforge/schema/spec_schema.json.
- Research tool may scrape DuckDuckGo in live mode and caches results; offline runs use the cached or stubbed results.
Outputs
- Generated project scaffold into the specified output directory.
- Initialized Git repository with commits grouped by pipeline phases.
- SQLite persistence of state/logs/assumptions/artifacts.
- README assumptions section may be appended or updated with summarized assumptions per run.
Research and LLM
LLM client
- OpenAI-compatible API targeting model kimi-k2-0905-preview by default.
- Configurable via KIMI_API_KEY and optional KIMI_BASE_URL.
- In offline mode, a deterministic stub client produces seeded responses.
Research tool
- Live mode: DuckDuckGo scraping with caching to research_cache.
- Offline mode: returns cached or stubbed results without network access.
- Be mindful of provider TOS and rate limits when enabling live research.
Docker (optional)
- If Dockerfile is present:
- docker build -t agentforge .
- docker run --rm -it \
-e AGENTFORGE_OFFLINE=1 -e AGENTFORGE_SEED=1337 \
-v "$PWD":/work -w /work \
agentforge agentforge --spec tests/fixtures/min_spec.json --output-dir ./_output
Troubleshooting Checklist
Determinism and environment
- export AGENTFORGE_OFFLINE=1
- export AGENTFORGE_SEED=1337
- Ensure KIMI_API_KEY is unset when offline; secrets must not appear in logs.
- Confirm pinned versions from constraints.txt are used.
Validate inputs and schema
- Verify the spec file path is correct and readable.
- Confirm src/agentforge/schema/spec_schema.json exists and has expected keys.
Increase logging
- export AGENTFORGE_DEBUG=1 (if supported)
- Re-run the failing step or CLI smoke to capture more logs.
Investigate SQLite
- Use the sqlite3 commands above to inspect runs/steps/logs/artifacts and verify rollback behavior.
CI-only failures
- Compare Python version and OS between local and CI.
- Download and inspect CI artifacts (coverage.xml, pytest logs, and persisted SQLite DB if uploaded).
Known Limitations
- Offline-first design:
- Default operation uses deterministic stubs; results may differ from live LLM/research behavior.
- Live LLM variance:
- Real model responses are nondeterministic; expect differences vs offline.
- Research constraints:
- DuckDuckGo scraping can be rate-limited or blocked; cache mitigates but cannot guarantee freshness.
- Concurrency:
- Multiple concurrent runs against the same SQLite file may require WAL mode and careful process coordination; high parallelism is not yet optimized.
- Rollback scope:
- File artifacts recorded during the run are deleted on rollback, but external/manual modifications and untracked files aren’t reverted. Git history outside generated commits is not rolled back.
- Platform coverage:
- Primarily tested on Python 3.13; other versions/OSes may require adjustments (e.g., Windows path nuances).
- Security scanning:
- Bandit and Safety are configured but may be conservative; allowlists may be required for some environments.
- Dockerfile optionality:
- Docker support depends on whether the scaffold included a Dockerfile in your spec selection.
- Schema evolution:
- Specs are validated against a versioned schema; older specs may need migration if the schema changes.
Key Commands Summary
- python3.13 -m venv .venv
- source .venv/bin/activate
- pip install -U pip
- pip install -e .[dev] -c constraints.txt
- pre-commit install
Run CLI (offline deterministic)
- export AGENTFORGE_OFFLINE=1
- export AGENTFORGE_SEED=1337
- agentforge --spec tests/fixtures/min_spec.json --output-dir ./_output
Quality gates
- ruff check .
- black --check .
- mypy src
Tests
- pytest -q --maxfail=1
- export AGENTFORGE_COVERAGE_MIN=${AGENTFORGE_COVERAGE_MIN:-80}
- pytest --cov=agentforge --cov-report=term-missing --cov-fail-under=${AGENTFORGE_COVERAGE_MIN}
- pytest -q -k "cli_offline_smoke or invalid_spec_path or wal_is_enabled"
- pytest -vv -k "<failing_test_name>" -s
SQLite inspection
- sqlite3 .agentforge.sqlite ".tables"
- sqlite3 .agentforge.sqlite "SELECT * FROM runs ORDER BY id DESC LIMIT 3;"
- sqlite3 .agentforge.sqlite "SELECT * FROM steps WHERE run_id=<id> ORDER BY id;"
- sqlite3 .agentforge.sqlite "SELECT level, message FROM logs WHERE run_id=<id> ORDER BY id LIMIT 50;"
- sqlite3 .agentforge.sqlite "SELECT * FROM artifacts WHERE run_id=<id>;"

## Commands
- Pytest coverage gate.
- pytest -q --maxfail=1
- pytest --cov=agentforge --cov-report=term-missing --cov-fail-under=${AGENTFORGE_COVERAGE_MIN}
- Run only smoke tests:
- pytest -q -k "cli_offline_smoke or invalid_spec_path or wal_is_enabled"
- pytest -vv -k "<failing_test_name>" -s

## Known Limitations
- AgentForge is a single-CLI, multi-agent pipeline that generates full project scaffolding from a JSON spec. Agents include RequirementsAnalysis, CodeGeneration, Testing, Documentation, and QualityAssurance.
- Shared state is persisted in a local SQLite database, including runs, steps, logs, artifacts, assumptions, and a research cache.
- LLM integration supports an OpenAI-compatible API (default model: kimi-k2-0905-preview). The system defaults to an offline deterministic stub for local reproducibility and tests.
- The pipeline validates inputs against a versioned JSON Schema and commits generated artifacts to a new Git repo in phase-organized commits.
- Quality gates include Black, Ruff, MyPy, Bandit, Safety, and pytest with a default coverage threshold of 80%.
- Python 3.13
- Git
- sqlite3 CLI (for quick inspection)
- Optional: Docker, Make
- Create and activate a virtualenv:
- python3.13 -m venv .venv
- source .venv/bin/activate
- Install with dev extras and pinned constraints:
- pip install -U pip
- pip install -e .[dev] -c constraints.txt
- Install pre-commit hooks:
- pre-commit install
- export AGENTFORGE_OFFLINE=1
- export AGENTFORGE_SEED=1337
- agentforge --spec tests/fixtures/min_spec.json --output-dir ./_output
- Equivalent invocation:
- python -m agentforge.cli --spec tests/fixtures/min_spec.json --output-dir ./_output
- mkdir -p agentforge && cd agentforge
- git init
- python3.13 -m venv .venv
- source .venv/bin/activate
- python -m pip install -U pip
- Then create or clone the project and install as above.
- agentforge --spec <path/to/spec.json> --output-dir <path/to/output>
- Also available via: python -m agentforge.cli ...
- Validates the spec against src/agentforge/schema/spec_schema.json (versioned).
- Orchestrates multi-agent steps; persists runs/steps/logs/artifacts/assumptions to .agentforge.sqlite.
- Generates a project scaffold in the output directory, initializes a Git repository, and organizes commits by phases.
- On persistent failure, emits a structured error report, rolls back recorded file artifacts, and marks the run as rolled_back.
- AGENTFORGE_OFFLINE=1
- Default local/test mode. Disables networked LLM and research. Uses deterministic stub outputs.
- AGENTFORGE_SEED=1337
- Seeds RNG for LLM stubs, backoff, and any randomized operations.
- AGENTFORGE_COVERAGE_MIN=80
- Pytest coverage gate.
- AGENTFORGE_DEBUG=1
- Increase log detail (if supported).
- Live LLM configuration (OpenAI-compatible):
- KIMI_API_KEY
- KIMI_BASE_URL (optional; falls back to provider defaults)
- Note: Do not set KIMI_API_KEY when running offline; secrets must not appear in logs.
- ruff check .
- black --check .
- mypy src
- bandit -q -r src
- safety check -r requirements.txt or via extras if configured
- pytest -q --maxfail=1
- With coverage (default gate 80%):
- export AGENTFORGE_COVERAGE_MIN=${AGENTFORGE_COVERAGE_MIN:-80}
- pytest --cov=agentforge --cov-report=term-missing --cov-fail-under=${AGENTFORGE_COVERAGE_MIN}
- Run only smoke tests:
- pytest -q -k "cli_offline_smoke or invalid_spec_path or wal_is_enabled"
- Re-run a failing test verbosely:
- pytest -vv -k "<failing_test_name>" -s
- Jobs:
- Install
- Lint & Type
- Test
- Steps include:
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
- pip install -e .[dev] -c constraints.txt
- ruff, black, mypy, pytest with coverage
- Set AGENTFORGE_OFFLINE=1 to disable networked I/O and use seeded LLM/research stubs.
- Set AGENTFORGE_SEED to a fixed value for deterministic outputs.
- Jitter is forced to 0 in offline/tests; time.sleep may be patched to a no-op in unit tests to keep them fast.
- Toolchain is pinned via constraints.txt for consistent environments.
- Step-level capped exponential backoff:
- attempts: 3 (configurable per step)
- base delay: 0.2s
- factor: 2.0 → delays: 0.2s, 0.4s, 0.8s
- cap: 2.0s
- jitter: 0.0 in offline/tests; ±10% decorrelated jitter in live mode
- On failure after retries: emit a structured error, mark the step failed, roll back artifacts.
- Default path: .agentforge.sqlite
- Tables: runs, steps, logs, artifacts, assumptions, research_cache
- WAL mode may be enabled for performance.
- sqlite3 .agentforge.sqlite ".tables"
- sqlite3 .agentforge.sqlite "SELECT * FROM runs ORDER BY id DESC LIMIT 3;"
- sqlite3 .agentforge.sqlite "SELECT * FROM steps WHERE run_id=<id> ORDER BY id;"
- sqlite3 .agentforge.sqlite "SELECT level, message FROM logs WHERE run_id=<id> ORDER BY id LIMIT 50;"
- sqlite3 .agentforge.sqlite "SELECT * FROM artifacts WHERE run_id=<id>;"
- sqlite3 .agentforge.sqlite "SELECT * FROM assumptions WHERE run_id=<id>;"
- Confirm artifact files referenced in artifacts were deleted.
- The run is marked rolled_back and no temp directories remain.
- Spec JSON validated against src/agentforge/schema/spec_schema.json.
- Research tool may scrape DuckDuckGo in live mode and caches results; offline runs use the cached or stubbed results.
- Generated project scaffold into the specified output directory.
- Initialized Git repository with commits grouped by pipeline phases.
- SQLite persistence of state/logs/assumptions/artifacts.
- README assumptions section may be appended or updated with summarized assumptions per run.
- OpenAI-compatible API targeting model kimi-k2-0905-preview by default.
- Configurable via KIMI_API_KEY and optional KIMI_BASE_URL.
- In offline mode, a deterministic stub client produces seeded responses.
- Live mode: DuckDuckGo scraping with caching to research_cache.
- Offline mode: returns cached or stubbed results without network access.
- Be mindful of provider TOS and rate limits when enabling live research.
- If Dockerfile is present:
- docker build -t agentforge .
- docker run --rm -it \
- export AGENTFORGE_OFFLINE=1
- export AGENTFORGE_SEED=1337
- Ensure KIMI_API_KEY is unset when offline; secrets must not appear in logs.
- Confirm pinned versions from constraints.txt are used.
- Verify the spec file path is correct and readable.
- Confirm src/agentforge/schema/spec_schema.json exists and has expected keys.
- export AGENTFORGE_DEBUG=1 (if supported)
- Re-run the failing step or CLI smoke to capture more logs.
- Use the sqlite3 commands above to inspect runs/steps/logs/artifacts and verify rollback behavior.
- Compare Python version and OS between local and CI.
- Download and inspect CI artifacts (coverage.xml, pytest logs, and persisted SQLite DB if uploaded).
- Offline-first design:
- Default operation uses deterministic stubs; results may differ from live LLM/research behavior.
- Live LLM variance:
- Real model responses are nondeterministic; expect differences vs offline.
- Research constraints:
- DuckDuckGo scraping can be rate-limited or blocked; cache mitigates but cannot guarantee freshness.
- Concurrency:
- Multiple concurrent runs against the same SQLite file may require WAL mode and careful process coordination; high parallelism is not yet optimized.
- Rollback scope:
- File artifacts recorded during the run are deleted on rollback, but external/manual modifications and untracked files aren’t reverted. Git history outside generated commits is not rolled back.
- Platform coverage:
- Primarily tested on Python 3.13; other versions/OSes may require adjustments (e.g., Windows path nuances).
- Security scanning:
- Bandit and Safety are configured but may be conservative; allowlists may be required for some environments.
- Dockerfile optionality:
- Docker support depends on whether the scaffold included a Dockerfile in your spec selection.
- Schema evolution:
- Specs are validated against a versioned schema; older specs may need migration if the schema changes.
- python3.13 -m venv .venv
- source .venv/bin/activate
- pip install -U pip
- pip install -e .[dev] -c constraints.txt
- pre-commit install
- export AGENTFORGE_OFFLINE=1
- export AGENTFORGE_SEED=1337
- agentforge --spec tests/fixtures/min_spec.json --output-dir ./_output
- ruff check .
- black --check .
- mypy src
- pytest -q --maxfail=1
- export AGENTFORGE_COVERAGE_MIN=${AGENTFORGE_COVERAGE_MIN:-80}
- pytest --cov=agentforge --cov-report=term-missing --cov-fail-under=${AGENTFORGE_COVERAGE_MIN}
- pytest -q -k "cli_offline_smoke or invalid_spec_path or wal_is_enabled"
- pytest -vv -k "<failing_test_name>" -s
- sqlite3 .agentforge.sqlite ".tables"
- sqlite3 .agentforge.sqlite "SELECT * FROM runs ORDER BY id DESC LIMIT 3;"
- sqlite3 .agentforge.sqlite "SELECT * FROM steps WHERE run_id=<id> ORDER BY id;"
- sqlite3 .agentforge.sqlite "SELECT level, message FROM logs WHERE run_id=<id> ORDER BY id LIMIT 50;"
- sqlite3 .agentforge.sqlite "SELECT * FROM artifacts WHERE run_id=<id>;"
