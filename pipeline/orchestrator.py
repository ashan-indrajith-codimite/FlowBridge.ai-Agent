"""
OrchestratorAgent — root agent for the FlowBridge.ai pipeline.

Single-agent pipeline:
  1. Pre-processing (Python, no LLM):
       - normalize_figma_node  → state['normalized_figma'], state['component_name']
       - extract_design_tokens → state['design_tokens']
       - read_skills_file      → state['framework_skills']
       - styling conventions   → state['styling_conventions'] (inline string, no LLM)
  2. CodeGeneratorAgent — single LLM call that reads all state and produces the component.
"""

from google.adk.agents import SequentialAgent

from pipeline.code_generator_agent import code_generator_agent

orchestrator = SequentialAgent(
    name="FlowBridgeOrchestrator",
    description=(
        "Single-agent pipeline that converts a Figma node JSON + target framework "
        "+ designer notes into a pixel-faithful, production-ready UI component."
    ),
    sub_agents=[
        code_generator_agent,
    ],
)
