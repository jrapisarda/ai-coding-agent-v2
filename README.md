# AI Coding Agent

This repository contains a proof-of-concept multi-agent coding orchestrator that uses the OpenAI Agents SDK (``openai_agents``) and the GPT-5 family of models to execute project plans encoded as JSON. The CLI accepts an ``agent_project_plan.json`` input and coordinates Requirements, Coding, Testing, and Documentation agents with shared workspace tooling such as ``write_many`` for batched filesystem writes.

> **Note**
> The workflow expects an ``OPENAI_API_KEY`` environment variable and internet access for model/tool usage. Without credentials the agents will build context but skip remote calls.

## Quick start

```bash
pip install -e .
ai-coding-agent run ./workspace --input-plan docs/agent_project_plan.json --prompt "Build a coding agent using OpenAI SDK"
```

Refer to [docs/README.md](docs/README.md) for background documents.
