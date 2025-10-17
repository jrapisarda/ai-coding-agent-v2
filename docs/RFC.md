# RFC: AgentForge Multi-Agent Orchestration System Upgrade

**Version:** 1.0  
**Date:** 2025-10-16  
**Status:** Draft  
**Author:** Technical BA  
**Target Audience:** Coding Agent / Development Team

---

## 1. Executive Summary

This RFC defines requirements for upgrading AgentForge from its current implementation using the `kimi-k2-0905-preview` model to a modern architecture leveraging the **OpenAI Agents SDK (2025)** and **GPT-5** model. The system will maintain its core multi-agent orchestration capabilities while adopting industry best practices for agent coordination, state management, and observability.

### 1.1 Key Objectives

- **MUST:** Migrate to OpenAI Agents SDK (Python, 2025 release)
- **MUST:** Integrate GPT-5 model with appropriate parameter tuning
- **MUST:** Implement multi-agent orchestration patterns (handoff, sequential, parallel)
- **MUST:** Maintain Python 3.13 compatibility with latest dependencies
- **MUST:** Preserve existing offline mode and deterministic testing capabilities
- **SHOULD:** Enhance observability and tracing capabilities
- **SHOULD:** Optimize agent coordination and reduce latency

---

## 2. System Architecture

### 2.1 Core Components

#### 2.1.1 Agent Orchestration Layer

**Framework:** OpenAI Agents SDK (2025)  
**Installation:**
```bash
pip install openai-agents>=1.0.0
pip install 'openai-agents[redis]'  # Optional: for distributed sessions
```

**Core Primitives:**
- **Agents**: LLMs with instructions, tools, guardrails, and handoffs
- **Handoffs**: Specialized tool calls for agent-to-agent control transfer
- **Guardrails**: Input/output validation and safety checks
- **Sessions**: Automatic conversation history management
- **Tracing**: Built-in execution tracking and debugging

#### 2.1.2 Agent Definitions

The system **MUST** implement five specialized agents:

1. **RequirementsAnalysis Agent**
   - Role: Analyze JSON spec, extract requirements, identify assumptions
   - Model: `gpt-5` (full reasoning)
   - Reasoning Effort: `high`
   - Tools: `research_tool`, `schema_validator`
   - Handoff Target: `CodeGeneration`

2. **CodeGeneration Agent**
   - Role: Generate project scaffold, source files, configuration
   - Model: `gpt-5-mini` (balanced cost/performance)
   - Reasoning Effort: `medium`
   - Verbosity: `low`
   - Tools: `file_writer`, `git_operations`, `template_engine`
   - Handoff Target: `Testing`

3. **Testing Agent**
   - Role: Generate test suites, validate coverage requirements
   - Model: `gpt-5-mini`
   - Reasoning Effort: `medium`
   - Tools: `pytest_runner`, `coverage_analyzer`
   - Handoff Target: `Documentation`

4. **Documentation Agent**
   - Role: Generate README, API docs, runbooks
   - Model: `gpt-5-mini`
   - Reasoning Effort: `low`
   - Verbosity: `high`
   - Tools: `markdown_writer`, `diagram_generator`
   - Handoff Target: `QualityAssurance`

5. **QualityAssurance Agent**
   - Role: Run linters, formatters, security scans, final validation
   - Model: `gpt-5-nano` (low-cost, fast)
   - Reasoning Effort: `minimal`
   - Tools: `ruff_checker`, `mypy_validator`, `bandit_scanner`, `safety_checker`
   - Handoff Target: None (terminal agent)

### 2.2 Model Configuration

#### 2.2.1 GPT-5 Model Selection

**Primary Model:** `gpt-5` (API endpoint: `https://api.openai.com/v1/chat/completions`)

**Model Variants:**
- `gpt-5`: Full reasoning model for complex analysis (RequirementsAnalysis)
- `gpt-5-mini`: Balanced cost/performance for most agents
- `gpt-5-nano`: Low-cost, low-latency for validation tasks

#### 2.2.2 GPT-5 Parameters

**Standard Configuration:**
```python
{
    "model": "gpt-5-mini",  # or gpt-5, gpt-5-nano
    "reasoning_effort": "medium",  # minimal, low, medium, high
    "verbosity": "medium",  # low, medium, high
    "temperature": 0.7,  # 0.0-2.0
    "max_tokens": 4096,  # Context: 128k input, 128k output
    "timeout": 60.0,
    "max_retries": 3
}
```

**Parameter Guidelines:**
- **reasoning_effort**: `minimal` for simple tasks, `high` for complex planning
- **verbosity**: `low` for code generation, `high` for documentation
- **temperature**: Lower (0.3-0.7) for deterministic output, higher (0.8-1.2) for creative tasks

### 2.3 Multi-Agent Orchestration Patterns

The system **MUST** implement the following orchestration patterns:

#### 2.3.1 Handoff Pattern (Primary)

**Use Case:** Sequential agent delegation with specialization

**Implementation:**
```python
from agents import Agent, Runner, function_tool

# Define agents with handoff capabilities
requirements_agent = Agent(
    name="RequirementsAnalysis",
    instructions="Analyze JSON spec and extract requirements...",
    model="gpt-5",
    tools=[research_tool, schema_validator],
    handoffs=["CodeGeneration"]
)

code_agent = Agent(
    name="CodeGeneration",
    instructions="Generate project scaffold...",
    model="gpt-5-mini",
    tools=[file_writer, git_operations],
    handoffs=["Testing"]
)

# Execute with automatic handoff
result = await Runner.run(requirements_agent, initial_input)
```

**Characteristics:**
- Deterministic transition between agents
- Clear agent specialization boundaries
- State passed via handoff context

#### 2.3.2 Sequential Pipeline Pattern

**Use Case:** Fixed-order execution with dependency chain

**Implementation:**
```python
async def execute_pipeline(spec_path: str, output_dir: str):
    context = {"spec": load_spec(spec_path), "output_dir": output_dir}
    
    # Step 1: Requirements
    req_result = await Runner.run(requirements_agent, context)
    context.update(req_result.outputs)
    
    # Step 2: Code Generation
    code_result = await Runner.run(code_agent, context)
    context.update(code_result.outputs)
    
    # Step 3-5: Continue pipeline...
    return context
```

#### 2.3.3 Parallel Execution Pattern

**Use Case:** Independent tasks (e.g., lint + type check + security scan)

**Implementation:**
```python
import asyncio

async def parallel_quality_checks(artifacts):
    tasks = [
        run_ruff_check(artifacts),
        run_mypy_check(artifacts),
        run_bandit_scan(artifacts)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return aggregate_results(results)
```

---

## 3. Technical Requirements

### 3.1 Dependencies and Environment

#### 3.1.1 Core Dependencies (MUST)

**Python Version:** 3.13.x

**Primary Packages:**
```txt
# Core SDK
openai-agents>=1.0.0
openai>=1.50.0

# Data validation
pydantic>=2.9.0
jsonschema>=4.23.0

# Database
aiosqlite>=0.20.0  # Async SQLite support

# CLI and utilities
click>=8.1.7
python-dotenv>=1.0.0

# Testing
pytest>=8.3.0
pytest-asyncio>=0.24.0
pytest-cov>=5.0.0

# Code quality
ruff>=0.6.0
black>=24.8.0
mypy>=1.11.0
bandit[toml]>=1.7.9
safety>=3.2.0

# Git operations
GitPython>=3.1.43

# Async support
nest-asyncio>=1.6.0  # For nested event loops
```

#### 3.1.2 Optional Dependencies (SHOULD)

```txt
# Distributed sessions
redis>=5.0.0

# Observability
opentelemetry-api>=1.26.0
opentelemetry-sdk>=1.26.0

# Tracing integrations
weave-python>=0.51.0  # W&B Weave integration
```

#### 3.1.3 Environment Setup

**Virtual Environment:**
```bash
python3.13 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .[dev] -c constraints.txt
```

**Environment Variables:**
```bash
# OpenAI Configuration (REQUIRED for live mode)
export OPENAI_API_KEY="sk-..."

# AgentForge Configuration
export AGENTFORGE_OFFLINE=0  # 0=live, 1=offline
export AGENTFORGE_SEED=1337  # For deterministic offline mode
export AGENTFORGE_DEBUG=0    # 0=info, 1=debug

# Model Selection (OPTIONAL, defaults to gpt-5-mini)
export AGENTFORGE_MODEL="gpt-5-mini"
export AGENTFORGE_REASONING_EFFORT="medium"
export AGENTFORGE_VERBOSITY="medium"
```

### 3.2 Agent Implementation Requirements

#### 3.2.1 Agent Base Configuration

**MUST implement:**
- Structured agent initialization with OpenAI Agents SDK
- Pydantic models for input/output validation
- Function tools with schema generation
- Guardrails for input/output validation
- Error handling with retry logic
- Logging and observability hooks

**Example Agent Structure:**
```python
from agents import Agent, function_tool, set_trace_processors
from pydantic import BaseModel, Field
import weave

# Initialize tracing
weave.init("agentforge")
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor
set_trace_processors([WeaveTracingProcessor()])

# Define input/output schemas
class RequirementsInput(BaseModel):
    spec_path: str = Field(description="Path to JSON spec file")
    output_dir: str = Field(description="Target output directory")

class RequirementsOutput(BaseModel):
    requirements: list[str]
    assumptions: list[str]
    architecture: dict

# Define tools
@function_tool
def validate_spec(spec_path: str) -> dict:
    """Validate JSON spec against schema."""
    # Implementation
    return {"valid": True, "errors": []}

# Create agent
requirements_agent = Agent(
    name="RequirementsAnalysis",
    instructions="""You are a requirements analysis expert...
    
    Your tasks:
    1. Load and validate the JSON specification
    2. Extract functional and non-functional requirements
    3. Identify assumptions and constraints
    4. Design high-level architecture
    
    Always use structured output and cite sources for decisions.""",
    model="gpt-5",
    tools=[validate_spec, research_web],
    handoffs=["CodeGeneration"]
)
```

#### 3.2.2 Guardrails Implementation

**Input Guardrails (MUST):**
```python
from agents import Agent, guardrail

@guardrail
async def validate_input_spec(context):
    """Validate spec exists and is well-formed."""
    spec_path = context.get("spec_path")
    if not os.path.exists(spec_path):
        return {"valid": False, "error": "Spec file not found"}
    # Additional validation...
    return {"valid": True}

# Apply to agent
agent = Agent(
    name="RequirementsAnalysis",
    input_guardrails=[validate_input_spec],
    # ...
)
```

**Output Guardrails (SHOULD):**
```python
@guardrail
async def validate_output_structure(context, output):
    """Ensure output matches expected schema."""
    try:
        RequirementsOutput.model_validate(output)
        return {"valid": True}
    except ValidationError as e:
        return {"valid": False, "error": str(e)}
```

### 3.3 Persistence and State Management

#### 3.3.1 SQLite Schema (MUST preserve)

**Database:** `.agentforge.sqlite`

**Tables:**
```sql
-- Runs table
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT UNIQUE NOT NULL,
    spec_path TEXT NOT NULL,
    output_dir TEXT NOT NULL,
    status TEXT NOT NULL,  -- pending, running, completed, failed, rolled_back
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSON
);

-- Steps table (agent executions)
CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL,  -- pending, running, completed, failed
    input JSON,
    output JSON,
    error TEXT,
    retries INTEGER DEFAULT 0,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

-- Logs table
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    step_id INTEGER,
    level TEXT NOT NULL,  -- debug, info, warning, error, critical
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

-- Artifacts table
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL,  -- file, directory, git_commit
    path TEXT NOT NULL,
    checksum TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

-- Assumptions table
CREATE TABLE IF NOT EXISTS assumptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    assumption TEXT NOT NULL,
    rationale TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

-- Research cache table
CREATE TABLE IF NOT EXISTS research_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT UNIQUE NOT NULL,
    result JSON NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.3.2 SQLite Configuration (MUST)

**Enable WAL Mode:**
```python
import sqlite3

conn = sqlite3.connect('.agentforge.sqlite')
conn.execute("PRAGMA journal_mode=WAL;")
conn.execute("PRAGMA synchronous=NORMAL;")
conn.execute("PRAGMA cache_size=-64000;")  # 64MB cache
conn.execute("PRAGMA temp_store=MEMORY;")
```

**Benefits:**
- Better concurrency (readers don't block writers)
- 10x+ performance improvement for writes
- Crash-safe with synchronous=NORMAL
- Persistent setting (survives connection close)

#### 3.3.3 Async SQLite Operations (MUST)

**Use aiosqlite for non-blocking I/O:**
```python
import aiosqlite

async def record_step(run_id: str, agent_name: str, result: dict):
    async with aiosqlite.connect('.agentforge.sqlite') as db:
        await db.execute("""
            INSERT INTO steps (run_id, agent_name, status, output)
            VALUES (?, ?, ?, ?)
        """, (run_id, agent_name, 'completed', json.dumps(result)))
        await db.commit()
```

### 3.4 Retry and Error Handling

#### 3.4.1 Agent-Level Retry Strategy (MUST)

**Configuration:**
```python
retry_config = {
    "max_attempts": 3,
    "base_delay": 0.2,  # seconds
    "backoff_factor": 2.0,
    "max_delay": 2.0,  # seconds
    "jitter": 0.1 if not OFFLINE_MODE else 0.0,
    "retriable_errors": [
        "RateLimitError",
        "APIConnectionError",
        "Timeout"
    ]
}
```

**Implementation:**
```python
import asyncio
from openai import RateLimitError, APIConnectionError

async def run_agent_with_retry(agent: Agent, input_data: dict):
    for attempt in range(retry_config["max_attempts"]):
        try:
            result = await Runner.run(agent, input_data)
            return result
        except (RateLimitError, APIConnectionError) as e:
            if attempt == retry_config["max_attempts"] - 1:
                raise
            
            delay = min(
                retry_config["base_delay"] * (retry_config["backoff_factor"] ** attempt),
                retry_config["max_delay"]
            )
            
            # Add jitter if not in offline mode
            if retry_config["jitter"] > 0:
                delay *= (1 + random.uniform(-0.1, 0.1))
            
            await asyncio.sleep(delay)
```

#### 3.4.2 Rollback Mechanism (MUST)

**On failure, rollback artifacts:**
```python
async def rollback_run(run_id: str):
    async with aiosqlite.connect('.agentforge.sqlite') as db:
        # Get artifacts to delete
        async with db.execute(
            "SELECT path FROM artifacts WHERE run_id = ?", (run_id,)
        ) as cursor:
            artifacts = await cursor.fetchall()
        
        # Delete files
        for (path,) in artifacts:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
        
        # Mark run as rolled back
        await db.execute(
            "UPDATE runs SET status = 'rolled_back' WHERE run_id = ?",
            (run_id,)
        )
        await db.commit()
```

### 3.5 Observability and Tracing

#### 3.5.1 Built-in Tracing (MUST)

**OpenAI Agents SDK Tracing:**
```python
from agents import set_tracing_enabled

# Enable built-in tracing
set_tracing_enabled(True)

# Traces are automatically captured:
# - Agent invocations
# - Tool calls
# - Handoffs
# - Token usage
# - Latency metrics
```

#### 3.5.2 W&B Weave Integration (SHOULD)

**Enhanced observability:**
```python
import weave
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor
from agents import set_trace_processors

# Initialize Weave
weave.init("agentforge-production")

# Set up Weave tracing
set_trace_processors([WeaveTracingProcessor()])

# All agent runs are now traced in W&B Weave dashboard
```

**Benefits:**
- Visual DAG of agent workflows
- Token usage and cost tracking
- Latency analysis
- Error investigation
- A/B testing support

#### 3.5.3 Structured Logging (MUST)

**Log format:**
```python
import logging
import json

logger = logging.getLogger("agentforge")

# Structured log entry
log_entry = {
    "timestamp": datetime.utcnow().isoformat(),
    "run_id": run_id,
    "agent": agent_name,
    "level": "info",
    "message": "Agent completed successfully",
    "duration_ms": 1234,
    "tokens_used": 567,
    "metadata": {}
}

logger.info(json.dumps(log_entry))
```

### 3.6 Offline Mode and Testing

#### 3.6.1 Deterministic Offline Mode (MUST preserve)

**Stub LLM Client:**
```python
from agents import Agent, Runner
import random

class OfflineLLMClient:
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
    
    async def chat_completions_create(self, **kwargs):
        # Return deterministic responses based on seed
        return {
            "choices": [{
                "message": {
                    "content": f"Stub response for {kwargs['messages'][-1]['content']}"
                }
            }]
        }

# Use in offline mode
if os.getenv("AGENTFORGE_OFFLINE") == "1":
    client = OfflineLLMClient(seed=int(os.getenv("AGENTFORGE_SEED", "1337")))
else:
    from openai import AsyncOpenAI
    client = AsyncOpenAI()
```

#### 3.6.2 Test Coverage Requirements (MUST)

**Minimum Coverage:** 80%

**Test Structure:**
```python
import pytest
from agentforge.agents import RequirementsAnalysis

@pytest.fixture
def sample_spec():
    return {
        "project_name": "test-project",
        "description": "Test description"
    }

@pytest.mark.asyncio
async def test_requirements_agent_offline(sample_spec):
    """Test requirements analysis in offline mode."""
    os.environ["AGENTFORGE_OFFLINE"] = "1"
    os.environ["AGENTFORGE_SEED"] = "1337"
    
    agent = RequirementsAnalysis()
    result = await agent.run(sample_spec)
    
    assert result.status == "completed"
    assert len(result.requirements) > 0
```

**Test Categories:**
- Unit tests: Individual agent functions
- Integration tests: Agent-to-agent handoffs
- E2E tests: Full pipeline execution
- Smoke tests: CLI offline deterministic run

---

## 4. Implementation Phases

### 4.1 Phase 1: Foundation (Week 1)

**Tasks:**
- [ ] Install and configure OpenAI Agents SDK
- [ ] Set up GPT-5 API access and authentication
- [ ] Create base agent classes with SDK integration
- [ ] Migrate SQLite schema with WAL mode
- [ ] Implement async database operations with aiosqlite

**Acceptance Criteria:**
- OpenAI Agents SDK successfully installed and importable
- GPT-5 API calls working with all three model variants
- SQLite database with WAL mode enabled and tested
- Base agent class can execute simple prompts

### 4.2 Phase 2: Agent Migration (Week 2)

**Tasks:**
- [ ] Implement RequirementsAnalysis agent with GPT-5
- [ ] Implement CodeGeneration agent with GPT-5-mini
- [ ] Implement Testing agent with GPT-5-mini
- [ ] Implement Documentation agent with GPT-5-mini
- [ ] Implement QualityAssurance agent with GPT-5-nano
- [ ] Define and implement function tools for each agent
- [ ] Configure handoff relationships

**Acceptance Criteria:**
- All 5 agents implemented with OpenAI Agents SDK
- Function tools defined and registered
- Handoffs configured between agents
- Each agent can execute independently

### 4.3 Phase 3: Orchestration (Week 3)

**Tasks:**
- [ ] Implement handoff orchestration pattern
- [ ] Implement sequential pipeline pattern
- [ ] Implement parallel execution for QA checks
- [ ] Add input/output guardrails
- [ ] Integrate retry logic with exponential backoff
- [ ] Implement rollback mechanism

**Acceptance Criteria:**
- Agents can hand off to each other automatically
- Pipeline executes all agents in sequence
- Parallel QA checks run concurrently
- Failures trigger rollback correctly

### 4.4 Phase 4: Observability (Week 4)

**Tasks:**
- [ ] Enable built-in OpenAI Agents SDK tracing
- [ ] Integrate W&B Weave for visualization
- [ ] Implement structured logging
- [ ] Add token usage and cost tracking
- [ ] Create debugging utilities

**Acceptance Criteria:**
- Traces visible in SDK dashboard
- W&B Weave showing agent execution DAG
- Logs in structured JSON format
- Token usage tracked per agent

### 4.5 Phase 5: Testing & Validation (Week 5)

**Tasks:**
- [ ] Port existing tests to new architecture
- [ ] Implement offline stub client
- [ ] Add agent-specific unit tests
- [ ] Add integration tests for handoffs
- [ ] Add E2E pipeline tests
- [ ] Verify ≥80% coverage

**Acceptance Criteria:**
- All tests passing in offline mode
- Coverage ≥80% (enforced by pytest-cov)
- Deterministic behavior with seeded offline mode
- CI/CD pipeline green

---

## 5. Migration Strategy

### 5.1 Backward Compatibility (MUST)

**Preserve:**
- CLI interface: `agentforge --spec <path> --output-dir <dir>`
- Environment variables: `AGENTFORGE_OFFLINE`, `AGENTFORGE_SEED`
- SQLite schema (add columns, don't remove)
- Output structure: project scaffold + Git repo
- Offline deterministic mode

**Deprecate (with warnings):**
- `KIMI_API_KEY` → Use `OPENAI_API_KEY`
- `KIMI_BASE_URL` → No longer needed

### 5.2 Data Migration

**No data migration required** (new installations start fresh)

**For existing databases:**
```sql
-- Add new columns to runs table
ALTER TABLE runs ADD COLUMN model TEXT DEFAULT 'gpt-5-mini';
ALTER TABLE runs ADD COLUMN reasoning_effort TEXT DEFAULT 'medium';

-- Add new columns to steps table
ALTER TABLE steps ADD COLUMN tokens_used INTEGER;
ALTER TABLE steps ADD COLUMN cost_usd REAL;
```

### 5.3 Rollback Plan

**If upgrade fails:**
1. Revert to previous Git commit
2. Restore `requirements.txt` with kimi dependencies
3. Restore environment variables (`KIMI_API_KEY`)
4. Run regression tests to verify functionality

**Rollback commands:**
```bash
git revert HEAD
pip install -r requirements.txt.backup
export KIMI_API_KEY="..."
pytest -k smoke
```

---

## 6. Quality Assurance

### 6.1 Quality Gates (MUST pass)

1. **Linting:** `ruff check .` (zero errors)
2. **Formatting:** `black --check .` (zero diffs)
3. **Type Checking:** `mypy src` (zero errors)
4. **Security:** `bandit -r src` (no high/medium issues)
5. **Dependencies:** `safety check` (no known vulnerabilities)
6. **Tests:** `pytest --cov=agentforge --cov-fail-under=80` (≥80% coverage)

### 6.2 Performance Benchmarks (SHOULD meet)

**Latency targets:**
- RequirementsAnalysis: <30s (GPT-5, high reasoning)
- CodeGeneration: <60s (GPT-5-mini, medium reasoning)
- Testing: <45s (GPT-5-mini, medium reasoning)
- Documentation: <20s (GPT-5-mini, low reasoning, high verbosity)
- QualityAssurance: <15s (GPT-5-nano, minimal reasoning)

**Total pipeline:** <3 minutes for typical project

**Token optimization:**
- Use `gpt-5-mini` and `gpt-5-nano` where appropriate
- Set `max_tokens` to reasonable limits per agent
- Use `reasoning_effort: minimal` for deterministic tasks

### 6.3 Cost Optimization (SHOULD implement)

**Model selection guidelines:**
- **Complex reasoning:** `gpt-5` (most expensive, most capable)
- **Balanced tasks:** `gpt-5-mini` (50% cheaper, 90% quality)
- **Simple validation:** `gpt-5-nano` (10x cheaper, fast)

**Token budgets (per agent):**
- RequirementsAnalysis: 8k input, 4k output
- CodeGeneration: 16k input, 8k output
- Testing: 8k input, 4k output
- Documentation: 4k input, 8k output
- QualityAssurance: 2k input, 1k output

---

## 7. Documentation Requirements

### 7.1 Developer Documentation (MUST create/update)

**Files to update:**
- `README.md`: Installation, quickstart, examples
- `ARCHITECTURE.md`: System design, agent definitions, orchestration patterns
- `API.md`: Agent APIs, function tools, configuration
- `TROUBLESHOOTING.md`: Common issues, debugging, rollback procedures

### 7.2 Migration Guide (MUST create)

**Contents:**
- Breaking changes summary
- Environment variable changes
- Dependency updates
- Code migration examples (old vs. new)
- Testing checklist

### 7.3 Code Documentation (MUST)

**Standards:**
- Docstrings for all public functions (Google style)
- Type hints for all parameters and returns
- Examples in docstrings for complex functions
- Inline comments for non-obvious logic

**Example:**
```python
async def run_agent_pipeline(
    spec_path: str,
    output_dir: str,
    *,
    offline: bool = False,
    seed: int | None = None
) -> PipelineResult:
    """Execute the full multi-agent pipeline.
    
    This function orchestrates all five agents in sequence with automatic
    handoffs. State is persisted to SQLite, and artifacts are tracked for
    rollback on failure.
    
    Args:
        spec_path: Path to JSON specification file
        output_dir: Target directory for generated project
        offline: If True, use deterministic stub LLM client
        seed: Random seed for deterministic offline mode
    
    Returns:
        PipelineResult containing status, artifacts, and metadata
    
    Raises:
        ValidationError: If spec is invalid
        PipelineError: If any agent fails after retries
    
    Example:
        >>> result = await run_agent_pipeline(
        ...     spec_path="tests/fixtures/min_spec.json",
        ...     output_dir="./_output",
        ...     offline=True,
        ...     seed=1337
        ... )
        >>> assert result.status == "completed"
    """
    # Implementation...
```

---

## 8. Security and Compliance

### 8.1 API Key Management (MUST)

**Requirements:**
- API keys **MUST** be stored in environment variables, never in code
- API keys **MUST NOT** appear in logs (redact in structured logs)
- API keys **MUST** be validated on startup (fail fast if missing/invalid)
- API keys **SHOULD** be rotated periodically (provide rotation guide)

**Implementation:**
```python
import os
from openai import AsyncOpenAI

def get_openai_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Redact in logs
    logger.info(f"OpenAI client initialized (key: {api_key[:8]}...)")
    
    return AsyncOpenAI(api_key=api_key)
```

### 8.2 Security Scanning (MUST pass)

**Tools:**
- **Bandit**: Static security analysis for Python
- **Safety**: Known vulnerability detection in dependencies

**Configuration (`pyproject.toml`):**
```toml
[tool.bandit]
exclude_dirs = ["tests", ".venv"]
skips = ["B101"]  # assert_used (OK in tests)

[tool.safety]
ignore = []  # List CVEs to ignore (with justification in comments)
```

### 8.3 Data Privacy (MUST comply)

**PII Handling:**
- Spec files **MAY** contain PII (e.g., author names, emails)
- PII **MUST NOT** be sent to LLM unless explicitly required
- PII **MUST** be redacted in logs and traces
- Users **SHOULD** be warned about PII exposure via README

**Implementation:**
```python
import re

def redact_pii(text: str) -> str:
    """Redact common PII patterns from text."""
    # Email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                  '[EMAIL]', text)
    # Phone numbers (US format)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    return text
```

---

## 9. Open Questions and Decisions

### 9.1 Resolved Decisions

| Decision | Resolution | Rationale |
|----------|-----------|-----------|
| Use OpenAI Agents SDK vs custom orchestration | **OpenAI Agents SDK** | Leverages battle-tested primitives, built-in tracing, community support |
| GPT-5 vs GPT-4o | **GPT-5** | Latest model, reasoning mode, better performance |
| Async vs sync SQLite | **Async (aiosqlite)** | Non-blocking I/O, better performance in async pipeline |
| WAL mode vs DELETE mode | **WAL mode** | 10x performance, better concurrency |
| Single model vs multi-model | **Multi-model** | Cost optimization: gpt-5/mini/nano based on complexity |

### 9.2 Open Questions

| Question | Options | Recommendation | Decision Deadline |
|----------|---------|----------------|-------------------|
| Redis for distributed sessions? | Yes / No / Later | **Later** (start with in-memory) | Phase 4 review |
| OpenTelemetry integration? | Yes / No / Later | **Yes** (if W&B Weave insufficient) | Phase 4 review |
| Custom agent framework vs SDK? | Custom / SDK | **SDK** (OpenAI Agents) | **Decided** |
| Parallel agent execution? | Yes / No | **Limited** (only for QA checks) | **Decided** |

---

## 10. Acceptance Criteria

### 10.1 Must-Have (P0)

- [ ] All agents migrated to OpenAI Agents SDK
- [ ] GPT-5 model integrated with appropriate variants
- [ ] Handoff orchestration pattern implemented
- [ ] SQLite with WAL mode and async operations
- [ ] Retry logic with exponential backoff
- [ ] Rollback mechanism on failure
- [ ] Offline deterministic mode preserved
- [ ] Test coverage ≥80%
- [ ] All quality gates passing
- [ ] Documentation updated

### 10.2 Should-Have (P1)

- [ ] W&B Weave tracing integration
- [ ] Parallel execution for QA checks
- [ ] Structured JSON logging
- [ ] Token usage and cost tracking
- [ ] Performance benchmarks met (<3min pipeline)
- [ ] Migration guide published

### 10.3 Nice-to-Have (P2)

- [ ] Redis session support
- [ ] OpenTelemetry integration
- [ ] Custom dashboard for monitoring
- [ ] Cost optimization recommendations
- [ ] Multi-tenancy support

---

## 11. References

### 11.1 OpenAI Agents SDK Documentation
- Official Docs: https://openai.github.io/openai-agents-python/
- GitHub: https://github.com/openai/openai-agents-python
- PyPI: https://pypi.org/project/openai-agents/

### 11.2 GPT-5 Documentation
- Model Docs: https://platform.openai.com/docs/models/gpt-5
- API Reference: https://platform.openai.com/docs/api-reference
- GPT-5 Parameters Guide: https://cookbook.openai.com/examples/gpt-5/gpt-5_new_params_and_tools

### 11.3 Multi-Agent Orchestration Best Practices
- Azure Architecture: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
- Skywork.ai Patterns: https://skywork.ai/blog/ai-agent-orchestration-best-practices-handoffs/
- Anthropic Research: https://www.anthropic.com/engineering/built-multi-agent-research-system

### 11.4 Python 3.13 Best Practices
- What's New: https://docs.python.org/3.13/whatsnew/3.13.html
- Type Hints: https://docs.python.org/3.13/library/typing.html
- Async I/O: https://docs.python.org/3.13/library/asyncio.html

### 11.5 Testing and Quality
- pytest Documentation: https://docs.pytest.org/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- Pydantic Validation: https://docs.pydantic.dev/latest/

### 11.6 Observability
- W&B Weave: https://weave-docs.wandb.ai/guides/integrations/openai_agents/
- OpenTelemetry: https://opentelemetry.io/docs/languages/python/

---

## 12. Appendix

### 12.1 Example: Complete Agent Implementation

```python
"""RequirementsAnalysis agent implementation."""

from agents import Agent, Runner, function_tool, set_trace_processors
from pydantic import BaseModel, Field
from typing import List, Dict
import weave
import json
import os

# Initialize tracing
weave.init("agentforge")
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor
set_trace_processors([WeaveTracingProcessor()])

# --- Input/Output Schemas ---

class RequirementsInput(BaseModel):
    """Input schema for requirements analysis."""
    spec_path: str = Field(description="Path to JSON specification file")
    output_dir: str = Field(description="Target output directory")

class RequirementsOutput(BaseModel):
    """Output schema for requirements analysis."""
    functional_requirements: List[str] = Field(description="List of functional requirements")
    non_functional_requirements: List[str] = Field(description="List of non-functional requirements")
    assumptions: List[Dict[str, str]] = Field(description="Assumptions made during analysis")
    architecture: Dict[str, any] = Field(description="High-level architecture design")
    validation_status: str = Field(description="Spec validation status")

# --- Function Tools ---

@function_tool
def validate_spec(spec_path: str) -> dict:
    """Validate JSON specification against schema.
    
    Args:
        spec_path: Path to the JSON specification file
    
    Returns:
        Validation result with status and errors
    """
    try:
        with open(spec_path, 'r') as f:
            spec = json.load(f)
        
        # Validate against schema (simplified)
        required_fields = ["project_name", "description"]
        missing = [f for f in required_fields if f not in spec]
        
        if missing:
            return {
                "valid": False,
                "errors": [f"Missing required field: {f}" for f in missing]
            }
        
        return {"valid": True, "errors": []}
    
    except FileNotFoundError:
        return {"valid": False, "errors": ["Spec file not found"]}
    except json.JSONDecodeError as e:
        return {"valid": False, "errors": [f"Invalid JSON: {str(e)}"]}

@function_tool
def research_best_practices(topic: str) -> dict:
    """Research best practices for a given topic.
    
    Args:
        topic: Topic to research (e.g., "Python project structure")
    
    Returns:
        Research results with recommendations
    """
    # In live mode, this would call DuckDuckGo or Perplexity
    # In offline mode, return cached/stub results
    
    if os.getenv("AGENTFORGE_OFFLINE") == "1":
        return {
            "topic": topic,
            "recommendations": [
                "Use src/ layout for Python projects",
                "Include pyproject.toml for configuration",
                "Use pytest for testing"
            ],
            "sources": ["Stub source 1", "Stub source 2"]
        }
    
    # Live research implementation...
    return {"topic": topic, "recommendations": [], "sources": []}

# --- Agent Definition ---

requirements_agent = Agent(
    name="RequirementsAnalysis",
    instructions="""You are an expert requirements analyst specializing in software projects.

Your responsibilities:
1. **Validate** the provided JSON specification against the schema
2. **Extract** all functional and non-functional requirements
3. **Identify** assumptions and document rationale
4. **Design** a high-level architecture appropriate for the requirements
5. **Research** best practices when needed (use research_best_practices tool)

Guidelines:
- Be thorough and precise in requirement extraction
- Clearly separate functional from non-functional requirements
- Document ALL assumptions with clear rationale
- Cite sources when making architectural decisions
- Use structured output format (RequirementsOutput schema)
- If validation fails, list all errors clearly

When you complete the analysis, hand off to the CodeGeneration agent with your findings.""",
    
    model="gpt-5",  # Full reasoning model for complex analysis
    tools=[validate_spec, research_best_practices],
    handoffs=["CodeGeneration"]
)

# --- Usage Example ---

async def analyze_requirements(spec_path: str, output_dir: str) -> RequirementsOutput:
    """Execute requirements analysis agent.
    
    Args:
        spec_path: Path to JSON specification file
        output_dir: Target output directory
    
    Returns:
        Requirements analysis results
    
    Raises:
        ValidationError: If spec is invalid
        AgentError: If analysis fails
    """
    input_data = RequirementsInput(
        spec_path=spec_path,
        output_dir=output_dir
    )
    
    result = await Runner.run(requirements_agent, input_data.model_dump())
    
    # Parse and validate output
    output = RequirementsOutput.model_validate(result.final_output)
    
    return output

# --- Run Example ---

if __name__ == "__main__":
    import asyncio
    
    # Set offline mode for testing
    os.environ["AGENTFORGE_OFFLINE"] = "1"
    os.environ["AGENTFORGE_SEED"] = "1337"
    
    result = asyncio.run(analyze_requirements(
        spec_path="tests/fixtures/min_spec.json",
        output_dir="./_output"
    ))
    
    print(f"Analysis complete: {result.validation_status}")
    print(f"Functional requirements: {len(result.functional_requirements)}")
    print(f"Assumptions: {len(result.assumptions)}")
```

### 12.2 Example: Handoff Orchestration

```python
"""Multi-agent pipeline with handoff orchestration."""

from agents import Agent, Runner
from typing import Dict, Any
import asyncio

async def execute_pipeline_with_handoffs(spec_path: str, output_dir: str) -> Dict[str, Any]:
    """Execute full pipeline with automatic agent handoffs.
    
    The pipeline follows this sequence:
    1. RequirementsAnalysis → validates spec and extracts requirements
    2. CodeGeneration → generates project scaffold
    3. Testing → creates test suites
    4. Documentation → writes docs
    5. QualityAssurance → runs quality checks
    
    Handoffs are automatic - each agent decides when to transfer control.
    
    Args:
        spec_path: Path to JSON specification
        output_dir: Target output directory
    
    Returns:
        Final pipeline results
    """
    
    # Define all agents (simplified - see full definitions above)
    agents = {
        "RequirementsAnalysis": requirements_agent,
        "CodeGeneration": code_generation_agent,
        "Testing": testing_agent,
        "Documentation": documentation_agent,
        "QualityAssurance": qa_agent
    }
    
    # Initial input
    context = {
        "spec_path": spec_path,
        "output_dir": output_dir
    }
    
    # Start with RequirementsAnalysis
    # Handoffs will occur automatically based on agent configuration
    result = await Runner.run(requirements_agent, context)
    
    return {
        "status": "completed",
        "final_output": result.final_output,
        "agents_executed": result.agents_called,
        "total_tokens": result.total_tokens,
        "duration_ms": result.duration_ms
    }

# Run the pipeline
if __name__ == "__main__":
    result = asyncio.run(execute_pipeline_with_handoffs(
        spec_path="tests/fixtures/min_spec.json",
        output_dir="./_output"
    ))
    print(f"Pipeline completed: {result['status']}")
```

### 12.3 Directory Structure

```
agentforge/
├── src/
│   └── agentforge/
│       ├── __init__.py
│       ├── cli.py                 # CLI entrypoint
│       ├── config.py              # Configuration management
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py            # Base agent class
│       │   ├── requirements.py    # RequirementsAnalysis agent
│       │   ├── codegen.py         # CodeGeneration agent
│       │   ├── testing.py         # Testing agent
│       │   ├── documentation.py   # Documentation agent
│       │   └── qa.py              # QualityAssurance agent
│       ├── orchestration/
│       │   ├── __init__.py
│       │   ├── pipeline.py        # Pipeline orchestration
│       │   ├── handoffs.py        # Handoff coordination
│       │   └── parallel.py        # Parallel execution
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── validators.py      # Validation tools
│       │   ├── research.py        # Research tools
│       │   ├── git_ops.py         # Git operations
│       │   └── file_ops.py        # File operations
│       ├── persistence/
│       │   ├── __init__.py
│       │   ├── database.py        # SQLite operations
│       │   └── models.py          # Database models
│       ├── observability/
│       │   ├── __init__.py
│       │   ├── tracing.py         # Tracing setup
│       │   └── logging.py         # Structured logging
│       └── schema/
│           └── spec_schema.json   # JSON schema for specs
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # pytest fixtures
│   ├── fixtures/
│   │   └── min_spec.json          # Test fixtures
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_tools.py
│   │   └── test_database.py
│   ├── integration/
│   │   ├── test_handoffs.py
│   │   └── test_pipeline.py
│   └── e2e/
│       └── test_full_pipeline.py
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI
├── docs/
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── MIGRATION.md
│   └── TROUBLESHOOTING.md
├── pyproject.toml                 # Project configuration
├── constraints.txt                # Pinned dependencies
├── requirements.txt               # Runtime dependencies
├── requirements-dev.txt           # Development dependencies
└── .agentforge.sqlite             # SQLite database (created at runtime)
```

---

**END OF RFC**