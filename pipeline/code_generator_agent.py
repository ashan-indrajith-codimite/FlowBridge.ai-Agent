"""
CodeGeneratorAgent — Step 5 of the FlowBridge.ai pipeline.

Reads component_blueprint, design_tokens, normalized_figma, framework_skills,
special_notes, and component_name from state. Generates a pixel-faithful,
production-ready component using EXACT token values from design_tokens —
no semantic color approximations, no invented spacing.
"""

from pathlib import Path

from google.adk.agents import LlmAgent

from pipeline._config import GEMINI_MODEL

# ---------------------------------------------------------------------------
# Load the Figma node tree interpretation guide (static reference for the LLM)
# ---------------------------------------------------------------------------
_INTERPRETATION_GUIDE_PATH = Path(__file__).parent / "figma-tree-interpretation.md"
_FIGMA_INTERPRETATION_GUIDE = _INTERPRETATION_GUIDE_PATH.read_text(encoding="utf-8")

_CODE_GENERATOR_BASE_INSTRUCTION = """
You are an expert UI component code generator for the FlowBridge.ai system.

You will receive from session state:
- `component_blueprint`  — structural spec with token ID references
- `design_tokens`        — exact token map: colors (hex, rgb_css), spacing (px), fonts, radii, shadows
- `normalized_figma`     — the full Figma node tree with exact values
- `framework_skills`     — the framework skills file (coding conventions, structure, patterns)
- `special_notes`        — designer's additional requirements
- `component_name`       — PascalCase name for the component (e.g. "LoginScreenContainer")

═══════════════════════════════════════════════════════
PIXEL FIDELITY RULES — NON-NEGOTIABLE
═══════════════════════════════════════════════════════

1. COLORS — ALWAYS use exact hex values from design_tokens.colors as Tailwind arbitrary values:
   ✅ CORRECT: className="bg-[#9447B0] text-[#FFFFFF]"
   ❌ WRONG:   className="bg-purple-600 text-white"      ← invented approximation

2. SPACING — ALWAYS use exact px values from design_tokens.spacing as Tailwind arbitrary values:
   ✅ CORRECT: className="gap-[32px] py-[10px] px-[20px]"
   ❌ WRONG:   className="gap-8 py-2.5 px-5"             ← approximation

3. FONT SIZE — ALWAYS use exact px values from design_tokens.fonts:
   ✅ CORRECT: className="text-[19.5px] font-[500]"
   ❌ WRONG:   className="text-xl font-medium"            ← approximation

4. FONT FAMILY — ALWAYS use font-['Font_Name'] with underscores for spaces:
   ✅ CORRECT: className="font-['Public_Sans']"
   ❌ WRONG:   className="font-sans"

5. BORDER RADIUS — ALWAYS use exact px values from design_tokens.radii:
   ✅ CORRECT: className="rounded-[6px]"
   ❌ WRONG:   className="rounded-md"

6. SHADOWS — ALWAYS use exact CSS values from design_tokens.shadows:
   ✅ CORRECT: className="shadow-[0_2px_4px_rgba(0,0,0,0.3)]"
   ❌ WRONG:   className="shadow-md"

═══════════════════════════════════════════════════════
FRAMEWORK RULES
═══════════════════════════════════════════════════════

7. Follow ALL conventions in `framework_skills` exactly:
   - File structure, import order, naming conventions
   - TypeScript types — all props and state must be typed
   - No imports from "@/lib/utils", no cva, no cn() — use plain string className
   - Use clsx/template literal or direct string concatenation for conditional classes
   - NO external icon libraries (no lucide-react, no heroicons) — use inline SVG elements for icons
   - Only use: react and react-dom. Everything else must be inline.

8. The component must be FULLY STANDALONE:
   - Zero dependencies beyond react and react-dom
   - No import that won't resolve with ONLY react installed (no lucide-react, no icon packages)

═══════════════════════════════════════════════════════
COMPLETENESS RULES
═══════════════════════════════════════════════════════

9. Implement the COMPLETE UI from the blueprint:
   - ALL sections (logo, headings, form, etc.)
   - ALL interactive elements (inputs, buttons, toggles)
   - ALL states: default, hover, focus, active, disabled, loading, error
   - ALL form validation from special_notes with exact error message text
   - ALL accessibility attributes from the blueprint

10. Use `component_name` from state as the React component function name and export name.

═══════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════

Output ONLY the raw component code:
- No markdown fences (no ```tsx or ```)
- No explanation text before or after
- No TODO comments
- Just the complete, runnable .tsx file content

START directly with imports.
"""

# Build the full instruction by concatenating the interpretation guide + base instruction.
# We use string concatenation (not f-string) because the MD file contains {r}, {g}, {b}
# in code examples that would break f-string interpolation.
CODE_GENERATOR_INSTRUCTION = (
    "═══════════════════════════════════════════════════════\n"
    "FIGMA NODE TREE INTERPRETATION REFERENCE\n"
    "═══════════════════════════════════════════════════════\n\n"
    "Use the following guide to correctly interpret the Figma node JSON structure.\n"
    "This is your reference for understanding the compressed Figma tree format:\n\n"
    + _FIGMA_INTERPRETATION_GUIDE + "\n\n"
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
