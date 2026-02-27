"""
OrchestratorAgent — root agent for the FlowBridge.ai pipeline.

Pre-processing is done in run_pipeline() (main.py) before this agent runs:
  - Figma JSON normalized via _normalize_node  → state['figma_node_json'] (hex colors, clean structure)
  - component_name derived via _to_pascal_case → state['component_name']
  - Framework skills loaded via load_skills_content → state['framework_skills']

Then a single LLM call:
  - CodeGeneratorAgent — reads all state and produces the final component code.
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
