"""
agent.py — Required by `adk web` command.

Exports `root_agent` so the ADK web UI can discover and run the pipeline.
"""

from pipeline.orchestrator import orchestrator

# `adk web` discovers agents by looking for `root_agent` in agent.py
root_agent = orchestrator
