"""
OrchestratorAgent — root SequentialAgent for the FlowBridge.ai pipeline.

Wires the 6 agents in order:
  1. FigmaNormalizerAgent  — normalize_figma_node tool (deterministic)
  2. TokenExtractorAgent   — extract_design_tokens tool (deterministic)
  3. DesignAnalyzerAgent   — structural blueprint (references token IDs)
  4. SkillsLoaderAgent     — loads react-standalone.skills.md
  5. CodeGeneratorAgent    — pixel-faithful component (exact Tailwind arbitrary values)
  6. FidelityGateAgent     — diffs output vs tokens; fixes any mismatches
"""

from google.adk.agents import SequentialAgent

from pipeline.figma_parser_agent import figma_normalizer_agent
from pipeline.token_extractor_agent import token_extractor_agent
from pipeline.design_analyzer_agent import design_analyzer_agent
from pipeline.skills_loader_agent import skills_loader_agent
from pipeline.code_generator_agent import code_generator_agent
from pipeline.code_reviewer_agent import code_reviewer_agent

orchestrator = SequentialAgent(
    name="FlowBridgeOrchestrator",
    description=(
        "Multi-agent pipeline that converts a Figma node JSON + target framework "
        "+ designer notes into a pixel-faithful, production-ready UI component."
    ),
    sub_agents=[
        figma_normalizer_agent,
        token_extractor_agent,
        design_analyzer_agent,
        skills_loader_agent,
        code_generator_agent,
        code_reviewer_agent,
    ],
)
