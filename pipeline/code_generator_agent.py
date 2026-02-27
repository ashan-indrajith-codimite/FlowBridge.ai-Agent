"""
CodeGeneratorAgent — sole LLM agent in the FlowBridge.ai pipeline.

Reads from session state:
  - figma_node_json  — raw Figma node JSON as provided
  - framework        — target framework
  - styling          — 'tailwind' or 'inline_css'
  - special_notes    — designer's additional requirements
  - component_name   — PascalCase component name (derived from root node name)

Outputs: state['generated_code']
"""

from pathlib import Path

from google.adk.agents import LlmAgent

from pipeline._config import GEMINI_MODEL

# ---------------------------------------------------------------------------
# Load the Figma node tree interpretation guide (static reference for the LLM)
# ---------------------------------------------------------------------------
_INTERPRETATION_GUIDE_PATH = Path(__file__).parent / "figma-tree-interpretation.md"
_FIGMA_INTERPRETATION_GUIDE = _INTERPRETATION_GUIDE_PATH.read_text(encoding="utf-8")
# Escape all curly braces in the guide so ADK's inject_session_state won't try
# to substitute {r}, {g}, {b}, {x}, {y} etc. found in the JSON code examples.
_FIGMA_INTERPRETATION_GUIDE_ESCAPED = _FIGMA_INTERPRETATION_GUIDE.replace("{", "{{").replace("}", "}}")
_CODE_GENERATOR_BASE_INSTRUCTION = """
You are an expert UI component code generator.

═══════════════════════════════════════════════════════
INPUTS (injected from session state)
═══════════════════════════════════════════════════════

FIGMA NODE JSON (the design to implement exactly):
{figma_node_json}

TARGET FRAMEWORK: {framework}
STYLING APPROACH: {styling}
COMPONENT NAME: {component_name}

SPECIAL NOTES FROM DESIGNER:
{special_notes}

═══════════════════════════════════════════════════════
PIXEL FIDELITY — NON-NEGOTIABLE
═══════════════════════════════════════════════════════

Read every color, spacing, font size, border radius, and shadow directly from
the FIGMA NODE JSON above and use the EXACT values in the output code. Never approximate.

If styling == 'tailwind':
  - Use Tailwind arbitrary values for all exact values.
  - Colors:       className="bg-[#9447B0] text-[#FFFFFF]"
  - Spacing:      className="gap-[32px] py-[10px] px-[20px]"
  - Font size:    className="text-[19.5px] font-[500]"
  - Border radius: className="rounded-[6px]"
  - Shadows:      className="shadow-[0_2px_4px_rgba(0,0,0,0.3)]"
  - Font family:  className="font-['Public_Sans']"
  - NO inline style={{}} — Tailwind classes ONLY.

If styling == 'inline_css':
  - Use inline style attributes for all styling.
  - Colors:       style={{backgroundColor: '#9447B0', color: '#FFFFFF'}}
  - Spacing:      style={{gap: '32px', padding: '10px 20px'}}
  - Font:         style={{fontSize: '19.5px', fontWeight: 500}}
  - Border radius: style={{borderRadius: '6px'}}
  - Shadows:      style={{boxShadow: '0 2px 4px rgba(0,0,0,0.3)'}}
  - NO Tailwind classes — inline styles ONLY.
  - For HTML: use style="..." attribute syntax.

═══════════════════════════════════════════════════════
FRAMEWORK RULES
═══════════════════════════════════════════════════════

- For React/Vue/Angular/Svelte: use TypeScript, proper component patterns.
- For HTML: output a single self-contained .html file with vanilla JS.
- NO external icon libraries — use inline SVG for any icons.
- For React: zero dependencies beyond react and react-dom.
- For HTML+Tailwind: include the Tailwind CDN script tag in <head>.

═══════════════════════════════════════════════════════
COMPLETENESS
═══════════════════════════════════════════════════════

- Implement ALL sections and elements visible in the FIGMA NODE JSON.
- ALL interactive states: default, hover, focus, active, disabled, loading, error.
- ALL form validation from SPECIAL NOTES with exact error message text.
- ALL accessibility attributes: aria-live, aria-busy, aria-invalid, aria-describedby, htmlFor.
- Use the COMPONENT NAME as the component function name and export name.
  For HTML: use it as the page <title>.

═══════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════

Output ONLY the raw component code:
- No markdown fences (no ```tsx or ```html)
- No explanation before or after
- No TODO comments
- For React: start with imports.
- For HTML: start with <!DOCTYPE html>.
"""

# Append the Figma tree interpretation guide to the instruction.
# The guide is brace-escaped so ADK's inject_session_state won't mistake
# JSON examples like {r}, {g}, {b} as session state placeholders.
CODE_GENERATOR_INSTRUCTION = (
    "═══════════════════════════════════════════════════════\n"
    "FIGMA NODE TREE INTERPRETATION REFERENCE\n"
    "═══════════════════════════════════════════════════════\n\n"
    "Use the following guide to correctly interpret the Figma node JSON structure:\n\n"
    + _FIGMA_INTERPRETATION_GUIDE_ESCAPED + "\n\n"
    "═══════════════════════════════════════════════════════\n"
    "END OF FIGMA INTERPRETATION REFERENCE\n"
    "═══════════════════════════════════════════════════════\n"
    + _CODE_GENERATOR_BASE_INSTRUCTION
)

code_generator_agent = LlmAgent(
    name="CodeGeneratorAgent",
    model=GEMINI_MODEL,
    instruction=CODE_GENERATOR_INSTRUCTION,
    output_key="generated_code",
)
