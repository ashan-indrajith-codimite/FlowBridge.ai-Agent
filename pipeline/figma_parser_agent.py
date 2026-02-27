"""
FigmaNormalizerAgent — Step 1 of the FlowBridge.ai pipeline.

Calls normalize_figma_node (a deterministic Python function — no LLM
summarization) to validate the raw Figma JSON and write the normalized
tree with exact hex colors, exact pixel values, and derived component name
into session state. No information is lost or re-interpreted.
"""

from google.adk.agents import LlmAgent

from pipeline._config import GEMINI_MODEL
from tools.figma_tools import normalize_figma_node

FIGMA_NORMALIZER_INSTRUCTION = """
You are the Figma normalizer agent.

Your ONLY job is to call the `normalize_figma_node` tool (no arguments).

The tool does all the work:
- Validates the raw Figma JSON from session state
- Normalizes all 0–1 RGB colors to hex and rgb_css (e.g., rgb(148,71,176))
- Preserves ALL numeric values exactly as-is (spacing, size, padding, radius)
- Derives the component name from the root node name
- Writes results to state['normalized_figma'], state['component_name'], state['root_dimensions']

After the tool returns, output a one-line confirmation in this exact format:
Normalized: <component_name> | root <width>x<height>px | all values preserved exactly

If the tool returns an error, output:
ERROR: <error message>

Do NOT describe, interpret, or summarize the design. The downstream agents
will read state directly.
"""

figma_normalizer_agent = LlmAgent(
    name="FigmaNormalizerAgent",
    model=GEMINI_MODEL,
    instruction=FIGMA_NORMALIZER_INSTRUCTION,
    tools=[normalize_figma_node],
    output_key="normalization_confirmation",
)
