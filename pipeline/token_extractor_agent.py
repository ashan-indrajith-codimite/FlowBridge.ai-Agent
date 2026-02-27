"""
TokenExtractorAgent — Step 2 of the FlowBridge.ai pipeline.

Calls extract_design_tokens (a deterministic Python function) to walk
normalized_figma and extract every unique color, spacing value, font,
radius, and shadow as a structured token map with exact values and their
Tailwind arbitrary-value equivalents.

Output: state['design_tokens']
"""

from google.adk.agents import LlmAgent

from pipeline._config import GEMINI_MODEL
from tools.figma_tools import extract_design_tokens

TOKEN_EXTRACTOR_INSTRUCTION = """
You are the design token extractor agent.

Your ONLY job is to call the `extract_design_tokens` tool (no arguments).

The tool reads state['normalized_figma'] and extracts all unique design tokens:
- colors: exact hex values + rgb_css + Tailwind arbitrary class
- spacing: exact px values (gaps, widths, paddings) + Tailwind arbitrary class
- fonts: font-family names, sizes, weights + Tailwind arbitrary class
- radii: exact px values + Tailwind arbitrary class
- shadows: exact CSS shadow + Tailwind arbitrary class

After the tool returns successfully, output a confirmation in this format:
Tokens extracted: <N> colors, <N> spacing, <N> fonts, <N> radii, <N> shadows

If the tool returns an error, output:
ERROR: <error message>

Do NOT invent or guess any token values. The tool reads directly from
the normalized Figma data — all values are exact.
"""

token_extractor_agent = LlmAgent(
    name="TokenExtractorAgent",
    model=GEMINI_MODEL,
    instruction=TOKEN_EXTRACTOR_INSTRUCTION,
    tools=[extract_design_tokens],
    output_key="token_extraction_confirmation",
)
