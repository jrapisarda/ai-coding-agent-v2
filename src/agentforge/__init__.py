"""
AgentForge package initialization.

This module exposes high-level entrypoints for the agent orchestration pipeline
defined in docs/RFC.md. It keeps the public surface minimal while allowing
internal modules to evolve independently.
"""

from importlib import metadata

try:
    __version__ = metadata.version("agentforge")
except metadata.PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = ["__version__"]
