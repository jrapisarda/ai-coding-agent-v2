from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import replace
from pathlib import Path

from agentforge.agents import build_agents
from agentforge.config import load_config
from agentforge.observability.logging import configure_logging
from agentforge.observability.tracing import Tracer
from agentforge.orchestration.pipeline import PipelineRunner, PipelineState, execute_pipeline_with_handoffs


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AgentForge multi-agent pipeline CLI.")
    parser.add_argument("--spec", required=True, help="Path to the JSON specification file.")
    parser.add_argument("--output", default="_output", help="Directory to emit generated artifacts.")
    parser.add_argument("--offline", action="store_true", help="Force offline mode.")
    return parser


async def main_async(args: argparse.Namespace) -> int:
    base_dir = Path.cwd()
    config = load_config(base_dir=base_dir)
    if args.offline:
        config = replace(config, offline_mode=True)

    configure_logging(config.observability.logging_level)

    tracer = Tracer()
    docs_root = base_dir / "docs"
    schema_path = base_dir / "src" / "agentforge" / "schema" / "spec_schema.json"
    output_dir = base_dir / args.output
    agents = build_agents(config, docs_root=docs_root, output_dir=output_dir, schema_path=schema_path)
    runner = PipelineRunner(agents=agents, config=config, tracer=tracer)

    state = PipelineState(
        spec_path=Path(args.spec),
        output_dir=output_dir,
        config=config,
    )
    result = await execute_pipeline_with_handoffs(args.spec, str(output_dir), runner, state=state)

    print(json.dumps(
        {
            "status": result.status,
            "agents_executed": result.agents_executed,
            "duration_ms": result.duration_ms,
        },
        indent=2,
    ))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = create_arg_parser()
    args = parser.parse_args(argv)
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
