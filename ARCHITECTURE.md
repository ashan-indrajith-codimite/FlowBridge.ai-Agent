# FlowBridge.ai Architecture & Agent Flow

## 🎯 Overview

**FlowBridge.ai** is a multi-agent AI system that converts Figma design JSON into pixel-perfect, production-ready UI components. Built with [Google ADK](https://github.com/google/adk-python) and powered by Gemini 2.5 Pro, it orchestrates 7 specialized agents in a sequential pipeline to ensure design fidelity and code quality.


## 🎯 Overview

**FlowBridge.ai** is a multi-agent AI system that converts Figma design JSON into pixel-perfect, production-ready UI components. Built with [Google ADK](https://github.com/google/adk-python) and powered by Gemini 2.5 Pro, it orchestrates 7 specialized agents in a sequential pipeline to ensure design fidelity and code quality.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FlowBridge.ai System                        │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
            ┌───────▼────────┐           ┌────────▼─────────┐
            │   CLI Mode     │           │    API Mode      │
            │   (main.py)    │           │   (server.py)    │
            └───────┬────────┘           └────────┬─────────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   run_pipeline() Function   │
                    │  - Initialize ADK Runner    │
                    │  - Create Session           │
                    │  - Set Initial State        │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   Orchestrator Agent        │
                    │   (SequentialAgent)         │
                    │   7-Stage Pipeline          │

                    └──────────────┬──────────────┘
                                   │
        ┌──────────────────────────┴──────────────────────────┐
        │                                                      │
        ▼                                                      ▼
┌───────────────┐                                   ┌────────────────┐
│  Session      │                                   │  Agent Tools   │
│  State        │◄──────────────────────────────────┤  (Python       │
│  (Scratchpad) │   Reads/Writes on Each Step      │   Functions)   │
└───────────────┘                                   └────────────────┘
        │
        │  State Variables:
        │  - figma_node_json (input)
        │  - framework (input)
        │  - styling (input)
        │  - special_notes (input)
        │  - normalized_figma (step 1)
        │  - component_name (step 1)
        │  - root_dimensions (step 1)
        │  - design_tokens (step 2)
        │  - component_blueprint (step 3)
        │  - framework_skills (step 4)
        │  - styling_conventions (step 5)
        │  - generated_code (step 6)
        │  - final_code (step 7 - output)
        │
        └─► Flows through all 7 agents sequentially

        │  - special_notes (input)
        │  - normalized_figma (step 1)
        │  - component_name (step 1)
        │  - root_dimensions (step 1)
        │  - design_tokens (step 2)
        │  - component_blueprint (step 3)
        │  - framework_skills (step 4)
        │  - styling_conventions (step 5)
        │  - generated_code (step 6)
        │  - final_code (step 7 - output)
        │
        └─► Flows through all 7 agents sequentially
```

---

## 🔄 7-Agent Sequential Pipeline


Each agent reads from and writes to **session state** (the shared scratchpad). Agents execute in strict order, with each building on the previous agent's output.

### 📊 Pipeline Flow Diagram

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                                                                                │
│  INPUT:  figma_node_json (raw Figma JSON)                                     │
│          framework (react | vue | angular | svelte | html)                   │
│          styling (tailwind | inline_css)                                     │
│          special_notes (designer requirements)                                │
│                                                                                │

│          framework (react | vue | angular | svelte)                           │
│          special_notes (designer requirements)                                │
│                                                                                │
└────────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃  AGENT 1: FigmaNormalizerAgent                       ┃
        ┃  ─────────────────────────────────────────           ┃
        ┃  Tool: normalize_figma_node (deterministic)          ┃
        ┃                                                       ┃
        ┃  INPUT:  state['figma_node_json']                    ┃
        ┃  OUTPUT: state['normalized_figma']                   ┃
        ┃          state['component_name']                     ┃
        ┃          state['root_dimensions']                    ┃
        ┃                                                       ┃
        ┃  TASK:                                               ┃
        ┃  • Validate Figma JSON structure                     ┃
        ┃  • Convert 0-1 RGB to hex (#9447B0) & rgb_css        ┃
        ┃  • Preserve exact px values (no rounding)            ┃
        ┃  • Extract component name from root node             ┃
        ┃  • Store dimensions (width x height)                 ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                 │
                                 ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃  AGENT 2: TokenExtractorAgent                        ┃
        ┃  ────────────────────────────────────────            ┃
        ┃  Tool: extract_design_tokens (deterministic)         ┃
        ┃                                                       ┃
        ┃  INPUT:  state['normalized_figma']                   ┃
        ┃  OUTPUT: state['design_tokens']                      ┃
        ┃                                                       ┃
        ┃  TASK:                                               ┃
        ┃  • Walk entire Figma tree                            ┃
        ┃  • Extract unique design tokens:                     ┃
        ┃    - colors (hex, rgb_css, Tailwind arbitrary)       ┃
        ┃    - spacing (px, Tailwind arbitrary)                ┃
        ┃    - fonts (family, size, weight, Tailwind)          ┃
        ┃    - radii (px, Tailwind arbitrary)                  ┃
        ┃    - shadows (CSS value, Tailwind arbitrary)         ┃
        ┃  • No approximations — exact values only             ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                 │
                                 ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃  AGENT 3: DesignAnalyzerAgent (LLM)                  ┃
        ┃  ──────────────────────────────────────              ┃
        ┃  Model: Gemini 2.5 Pro                               ┃
        ┃                                                       ┃
        ┃  INPUT:  state['normalized_figma']                   ┃
        ┃          state['design_tokens']                      ┃
        ┃          state['special_notes']                      ┃
        ┃  OUTPUT: state['component_blueprint']                ┃
        ┃                                                       ┃
        ┃  TASK:                                               ┃
        ┃  • Analyze design structure & hierarchy              ┃
        ┃  • Create component blueprint with sections:         ┃
        ┃    - Component Identity (name, type, purpose)        ┃
        ┃    - Sections & Layout Tree (hierarchy, gaps)        ┃
        ┃    - Props Interface (TypeScript types)              ┃
        ┃    - Interactive Elements (states, validation)       ┃
        ┃    - Style Token Map (token ID references)           ┃
        ┃    - Accessibility Requirements (ARIA, labels)       ┃
        ┃  • Reference token IDs only — NO raw values          ┃
        ┃  • Blueprint = single source of truth for Step 5     ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                 │
                                 ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃  AGENT 4: SkillsLoaderAgent                          ┃
        ┃  ──────────────────────────────────                  ┃
        ┃  Tool: read_skills_file                              ┃
        ┃                                                       ┃
        ┃  INPUT:  state['framework']                          ┃
        ┃  OUTPUT: state['framework_skills']                   ┃
        ┃                                                       ┃
        ┃  TASK:                                               ┃
        ┃  • Read framework-specific .skills.md file           ┃
        ┃  • Load code conventions & patterns                  ┃
        ┃    - react-standalone.skills.md (Tailwind only)      ┃
        ┃    - vue.skills.md                                   ┃
        ┃    - angular.skills.md                               ┃
        ┃    - svelte.skills.md                                ┃
        ┃  • Skills define:                                    ┃
        ┃    - File structure                                  ┃
        ┃    - Import conventions                              ┃
        ┃    - TypeScript patterns                             ┃
        ┃    - State management                                ┃
        ┃    - Styling approach (Tailwind arbitrary values)    ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                 │
                                 ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃  AGENT 5: StylingAgent (LLM)                         ┃
        ┃  ──────────────────────────────────────              ┃
        ┃  Model: Gemini 2.5 Pro                               ┃
        ┃                                                       ┃
        ┃  INPUT:  state['styling']                            ┃
        ┃  OUTPUT: state['styling_conventions']                ┃
        ┃                                                       ┃
        ┃  TASK:                                               ┃
        ┃  • Read the styling mode (tailwind | inline_css)     ┃
        ┃  • Generate detailed styling convention rules        ┃
        ┃  • Define how tokens map to CSS/Tailwind classes     ┃
        ┃  • Ensure consistency for downstream CodeGenerator   ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                 │
                                 ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃  AGENT 6: CodeGeneratorAgent (LLM)                   ┃
        ┃  ─────────────────────────────────────               ┃
        ┃  Model: Gemini 2.5 Pro                               ┃
        ┃  Context: figma-tree-interpretation.md (821 lines)   ┃
        ┃                                                       ┃
        ┃  INPUT:  state['component_blueprint']                ┃
        ┃          state['design_tokens']                      ┃
        ┃          state['normalized_figma']                   ┃
        ┃          state['framework_skills']                   ┃
        ┃          state['styling_conventions']                ┃
        ┃          state['special_notes']                      ┃
        ┃          state['component_name']                     ┃
        ┃  OUTPUT: state['generated_code']                     ┃
        ┃                                                       ┃
        ┃  TASK:                                               ┃
        ┃  • Generate complete, runnable component code        ┃
        ┃  • PIXEL FIDELITY RULES (NON-NEGOTIABLE):            ┃
        ┃    1. Colors: EXACT hex as Tailwind/CSS arbitrary    ┃
        ┃       ✅ bg-[#9447B0]  ❌ bg-purple-600              ┃
        ┃    2. Spacing: EXACT px as Tailwind/CSS arbitrary    ┃
        ┃       ✅ gap-[32px]  ❌ gap-8                        ┃
        ┃    3. Font size: EXACT px                            ┃
        ┃       ✅ text-[19.5px]  ❌ text-xl                   ┃
        ┃    4. Font family: Exact name with underscores       ┃
        ┃       ✅ font-['Public_Sans']  ❌ font-sans          ┃
        ┃    5. Border radius: EXACT px                        ┃
        ┃       ✅ rounded-[6px]  ❌ rounded-md                ┃
        ┃    6. Shadows: EXACT CSS value                       ┃
        ┃       ✅ shadow-[0_2px_4px_rgba(0,0,0,0.3)]          ┃
        ┃  • Follow framework_skills conventions exactly       ┃
        ┃  • Fully standalone (React/Vue/HTML + Styling)       ┃
        ┃  • All states: default, hover, focus, disabled, etc. ┃
        ┃  • Complete accessibility (ARIA, labels, roles)      ┃
        ┃  • Output raw code (no markdown fences)              ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                 │
                                 ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃  AGENT 7: FidelityGateAgent (LLM)                    ┃
        ┃  ────────────────────────────────────                ┃
        ┃  Model: Gemini 2.5 Pro                               ┃
        ┃                                                       ┃
        ┃  INPUT:  state['generated_code']                     ┃
        ┃          state['design_tokens']                      ┃
        ┃          state['normalized_figma']                   ┃
        ┃          state['component_blueprint']                ┃
        ┃          state['special_notes']                      ┃
        ┃  OUTPUT: state['final_code']                         ┃
        ┃                                                       ┃
        ┃  TASK:                                               ┃
        ┃  • Diff generated_code vs design_tokens              ┃
        ┃  • FIDELITY CHECKLIST:                               ┃
        ┃    ✓ Every color hex present correctly               ┃
        ┃    ✓ Every spacing px present correctly              ┃
        ┃    ✓ Every font family/size/weight exact             ┃
        ┃    ✓ Every radius px present                         ┃
        ┃    ✓ Every shadow CSS value present                  ┃
        ┃  • COMPLETENESS CHECKLIST:                           ┃
        ┃    ✓ All sections from blueprint implemented         ┃
        ┃    ✓ All interactive states implemented              ┃
        ┃    ✓ All validation rules from special_notes         ┃
        ┃    ✓ All accessibility requirements                  ┃
        ┃  • If violations found: FIX inline and output        ┃
        ┃  • Replace semantic classes with exact values        ┃
        ┃    (bg-purple-600 → bg-[#9447B0])                    ┃
        ┃  • Output final_code (corrected or unchanged)        ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                                 │
                                 ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃  AGENT 5: CodeGeneratorAgent (LLM)                   ┃
        ┃  ─────────────────────────────────────               ┃
        ┃  Model: Gemini 2.5 Pro                               ┃
        ┃  Context: figma-tree-interpretation.md (821 lines)   ┃
        ┃                                                       ┃
        ┃  INPUT:  state['component_blueprint']                ┃
        ┃          state['design_tokens']                      ┃
        ┃          state['normalized_figma']                   ┃
        ┃          state['framework_skills']                   ┃
        ┃          state['special_notes']                      ┃
        ┃          state['component_name']                     ┃
        ┃  OUTPUT: state['generated_code']                     ┃
        ┃                                                       ┃
        ┃  TASK:                                               ┃
        ┃  • Generate complete, runnable component code        ┃
        ┃  • PIXEL FIDELITY RULES (NON-NEGOTIABLE):            ┃
        ┃    1. Colors: EXACT hex as Tailwind arbitrary        ┃
        ┃       ✅ bg-[#9447B0]  ❌ bg-purple-600              ┃
        ┃    2. Spacing: EXACT px as Tailwind arbitrary        ┃
        ┃       ✅ gap-[32px]  ❌ gap-8                        ┃
        ┃    3. Font size: EXACT px                            ┃
        ┃       ✅ text-[19.5px]  ❌ text-xl                   ┃
        ┃    4. Font family: Exact name with underscores       ┃
        ┃       ✅ font-['Public_Sans']  ❌ font-sans          ┃
        ┃    5. Border radius: EXACT px                        ┃
        ┃       ✅ rounded-[6px]  ❌ rounded-md                ┃
        ┃    6. Shadows: EXACT CSS value                       ┃
        ┃       ✅ shadow-[0_2px_4px_rgba(0,0,0,0.3)]          ┃
        ┃  • Follow framework_skills conventions exactly       ┃
        ┃  • Fully standalone (React + Tailwind only)          ┃
        ┃  • All states: default, hover, focus, disabled, etc. ┃
        ┃  • Complete accessibility (ARIA, labels, roles)      ┃
        ┃  • Output raw .tsx code (no markdown fences)         ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                 │
                                 ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃  AGENT 6: FidelityGateAgent (LLM)                    ┃
        ┃  ────────────────────────────────────                ┃
        ┃  Model: Gemini 2.5 Pro                               ┃
        ┃                                                       ┃
        ┃  INPUT:  state['generated_code']                     ┃
        ┃          state['design_tokens']                      ┃
        ┃          state['normalized_figma']                   ┃
        ┃          state['component_blueprint']                ┃
        ┃          state['special_notes']                      ┃
        ┃  OUTPUT: state['final_code']                         ┃
        ┃                                                       ┃
        ┃  TASK:                                               ┃
        ┃  • Diff generated_code vs design_tokens              ┃
        ┃  • FIDELITY CHECKLIST:                               ┃
        ┃    ✓ Every color hex present as Tailwind arbitrary   ┃
        ┃    ✓ Every spacing px present as Tailwind arbitrary  ┃
        ┃    ✓ Every font family/size/weight exact             ┃
        ┃    ✓ Every radius px present                         ┃
        ┃    ✓ Every shadow CSS value present                  ┃
        ┃  • COMPLETENESS CHECKLIST:                           ┃
        ┃    ✓ All sections from blueprint implemented         ┃
        ┃    ✓ All interactive states implemented              ┃
        ┃    ✓ All validation rules from special_notes         ┃
        ┃    ✓ All accessibility requirements                  ┃
        ┃  • If violations found: FIX inline and output        ┃
        ┃  • Replace semantic classes with exact values        ┃
        ┃    (bg-purple-600 → bg-[#9447B0])                    ┃
        ┃  • Output final_code (corrected or unchanged)        ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                                                                                │
│  OUTPUT:  final_code (pixel-perfect component)                                │
│           component_name (PascalCase)                                          │
│           root_dimensions (width x height dict)                                │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Agent Details

### 1. **FigmaNormalizerAgent** (Deterministic Tool)
- **Type**: LlmAgent with deterministic tool
- **Tool**: `normalize_figma_node()`
- **Input**: Raw Figma JSON string
- **Output**: Normalized JSON with hex colors, exact px values
- **Key Operations**:
  - Validates Figma JSON structure
  - Converts RGB 0-1 values to hex and `rgb(r,g,b)` strings
  - Preserves all numeric values exactly (no rounding)
  - Extracts component name from root node
  - Stores root dimensions
- **State Updates**:
  - `normalized_figma`: Clean JSON tree
  - `component_name`: PascalCase name (e.g., "LoginScreenContainer")
  - `root_dimensions`: `{width: 300, height: 359}`

---

### 2. **TokenExtractorAgent** (Deterministic Tool)
- **Type**: LlmAgent with deterministic tool
- **Tool**: `extract_design_tokens()`
- **Input**: `normalized_figma`
- **Output**: Structured token map
- **Key Operations**:
  - Walks entire Figma tree
  - Extracts unique values for:
    - **Colors**: `{id: "color-9447B0", hex: "#9447B0", rgb_css: "rgb(148,71,176)", tailwind: "bg-[#9447B0]"}`
    - **Spacing**: `{id: "spacing-32", px: 32, tailwind: "gap-[32px]"}`
    - **Fonts**: `{id: "font-PublicSans-19.5-500", family: "Public Sans", size: 19.5, weight: 500, tailwind: "font-['Public_Sans'] text-[19.5px] font-[500]"}`
    - **Radii**: `{id: "radius-6", px: 6, tailwind: "rounded-[6px]"}`
    - **Shadows**: `{id: "shadow-0_2_4_0.3", css: "0 2px 4px rgba(0,0,0,0.3)", tailwind: "shadow-[0_2px_4px_rgba(0,0,0,0.3)]"}`
- **State Updates**:
  - `design_tokens`: Complete token map (single source of truth for all values)

---

### 3. **DesignAnalyzerAgent** (LLM)
- **Type**: LlmAgent (Gemini 2.5 Pro)
- **Input**: `normalized_figma`, `design_tokens`, `special_notes`
- **Output**: Structural blueprint
- **Key Operations**:
  - Analyzes design hierarchy
  - Creates structured blueprint with sections:
    - Component Identity (name, type, purpose)
    - Sections & Layout Tree (hierarchy, gaps, alignment)
    - Props Interface (TypeScript types)
    - Interactive Elements (states, validation)
    - Style Token Map (which tokens apply to which elements)
    - Accessibility Requirements (ARIA, labels, roles)
  - **Critical Rule**: Only references token IDs from `design_tokens` — NEVER re-expresses raw values
- **State Updates**:
  - `component_blueprint`: Markdown-formatted structural spec

---

### 4. **SkillsLoaderAgent** (Tool)
- **Type**: LlmAgent with tool
- **Tool**: `read_skills_file(framework: str)`
- **Input**: `framework` (react | vue | angular | svelte | html)
- **Output**: Framework-specific coding conventions
- **Key Operations**:
  - Reads `.skills.md` file from `skills/` directory
  - For React: loads `react-standalone.skills.md`
  - For HTML: loads `html.skills.md`
  - Skills include:
    - File structure conventions
    - Import order
    - TypeScript patterns
    - State management approach
    - Styling methodology
    - Forbidden dependencies (no lucide-react, no shadcn/ui, etc.)
- **State Updates**:
  - `framework_skills`: Full skills file content

---

### 5. **StylingAgent** (LLM)
- **Type**: LlmAgent (Gemini 2.5 Pro)
- **File**: `pipeline/styling_agent.py`
- **Input**: `state["styling"]` ('tailwind' | 'inline_css')
- **Output**: `state["styling_conventions"]`
- **Purpose**: Reads the styling mode and generates detailed styling convention rules for the downstream CodeGeneratorAgent.
- **Key Operations**:
  - Analyzes the requested styling mode
  - Generates rules for mapping design tokens to CSS or Tailwind classes
  - Defines how hover/active/focus states should be handled in the selected mode
  - Ensures consistency in class naming or style object structure
- **State Updates**:
  - `styling_conventions`: Markdown-formatted styling spec

---

### 6. **CodeGeneratorAgent** (LLM)
- **Type**: LlmAgent (Gemini 2.5 Pro)
- **Special Context**: `figma-tree-interpretation.md` (821-line Figma JSON format guide) prepended to instruction
- **Input**: `component_blueprint`, `design_tokens`, `normalized_figma`, `framework_skills`, `styling_conventions`, `special_notes`, `component_name`
- **Output**: Complete component source code
- **Key Operations**:
  - Generates pixel-perfect component following blueprint
  - **Pixel Fidelity Rules** (non-negotiable):
    1. Colors: EXACT hex as Tailwind/CSS arbitrary
    2. Spacing: EXACT px as Tailwind/CSS arbitrary
    3. Font size: EXACT px
    4. Font family: Exact name with underscores
    5. Border radius: EXACT px
    6. Shadows: EXACT CSS value
  - Implements all states: default, hover, focus, active, disabled, loading, error
  - Full accessibility (ARIA, labels, roles)
  - Fully standalone (no external UI libraries)
  - Outputs raw code (no markdown fences)
- **State Updates**:
  - `generated_code`: Complete component code

---

### 7. **FidelityGateAgent** (LLM - Quality Control)

- **Input**: `framework` (react | vue | angular | svelte)
- **Output**: Framework-specific coding conventions
- **Key Operations**:
  - Reads `.skills.md` file from `skills/` directory
  - For React: loads `react-standalone.skills.md` (Tailwind arbitrary values only)
  - Skills include:
    - File structure conventions
    - Import order
    - TypeScript patterns
    - State management approach
    - Styling methodology (Tailwind with exact values)
    - Forbidden dependencies (no lucide-react, no shadcn/ui, etc.)
- **State Updates**:
  - `framework_skills`: Full skills file content

---

### 5. **CodeGeneratorAgent** (LLM)
- **Type**: LlmAgent (Gemini 2.5 Pro)
- **Special Context**: `figma-tree-interpretation.md` (821-line Figma JSON format guide) prepended to instruction
- **Input**: `component_blueprint`, `design_tokens`, `normalized_figma`, `framework_skills`, `special_notes`, `component_name`
- **Output**: Complete component source code
- **Key Operations**:
  - Generates pixel-perfect component following blueprint
  - **Pixel Fidelity Rules** (non-negotiable):
    1. Colors: EXACT hex as Tailwind arbitrary (`bg-[#9447B0]`)
    2. Spacing: EXACT px as Tailwind arbitrary (`gap-[32px]`)
    3. Font size: EXACT px (`text-[19.5px]`)
    4. Font family: Exact name with underscores (`font-['Public_Sans']`)
    5. Border radius: EXACT px (`rounded-[6px]`)
    6. Shadows: EXACT CSS value (`shadow-[0_2px_4px_rgba(0,0,0,0.3)]`)
  - Implements all states: default, hover, focus, active, disabled, loading, error
  - Full accessibility (ARIA, labels, roles)
  - Fully standalone (React + Tailwind only — no external UI libraries)
  - Outputs raw `.tsx` code (no markdown fences)
- **State Updates**:
  - `generated_code`: Complete component code

---

### 6. **FidelityGateAgent** (LLM - Quality Control)
- **Type**: LlmAgent (Gemini 2.5 Pro)
- **Input**: `generated_code`, `design_tokens`, `normalized_figma`, `component_blueprint`, `special_notes`
- **Output**: Final verified code
- **Key Operations**:
  - **Fidelity Diff**: Checks if every token from `design_tokens` appears in code
    - Every color hex present as Tailwind arbitrary class
    - Every spacing px present
    - Every font family/size/weight exact
    - Every radius px present
    - Every shadow CSS value present
  - **Completeness Check**:
    - All sections from blueprint implemented
    - All interactive states implemented
    - All validation rules from special_notes
    - All accessibility requirements
  - **Automatic Fixes**: If violations found, corrects inline
    - Replaces semantic classes with exact values (e.g., `bg-purple-600` → `bg-[#9447B0]`)
    - Adds missing states or validation
  - Outputs final code (corrected or unchanged)
- **State Updates**:
  - `final_code`: Production-ready component (final output)

---

## 🔧 Key Components

### Session State (Scratchpad)
Google ADK's session state acts as a shared scratchpad. All agents read from and write to it. Key state variables:

| Variable | Set By | Used By | Description |
|----------|--------|---------|-------------|
| `figma_node_json` | Input | Agent 1 | Raw Figma JSON string |
| `framework` | Input | Agent 4 | Target framework (react/vue/angular/svelte/html) |
| `styling` | Input | Agent 5 | Styling mode (tailwind | inline_css) |
| `special_notes` | Input | Agent 3, 6, 7 | Designer requirements |
| `normalized_figma` | Agent 1 | Agent 2, 3, 6, 7 | Clean Figma tree with hex colors |
| `component_name` | Agent 1 | Agent 6, 7 | PascalCase component name |
| `root_dimensions` | Agent 1 | Output | Root node width x height |
| `design_tokens` | Agent 2 | Agent 3, 6, 7 | Extracted token map (single source of truth) |
| `component_blueprint` | Agent 3 | Agent 6, 7 | Structural spec with token references |
| `framework_skills` | Agent 4 | Agent 6 | Framework coding conventions |
| `styling_conventions` | Agent 5 | Agent 6 | Styling convention rules |
| `generated_code` | Agent 6 | Agent 7 | Initial generated code |
| `final_code` | Agent 7 | Output | Final verified code |

| `figma_node_json` | Input | Agent 1 | Raw Figma JSON string |
| `framework` | Input | Agent 4 | Target framework (react/vue/angular/svelte) |
| `special_notes` | Input | Agent 3, 5, 6 | Designer requirements |
| `normalized_figma` | Agent 1 | Agent 2, 3, 5, 6 | Clean Figma tree with hex colors |
| `component_name` | Agent 1 | Agent 5, 6 | PascalCase component name |
| `root_dimensions` | Agent 1 | Output | Root node width x height |
| `design_tokens` | Agent 2 | Agent 3, 5, 6 | Extracted token map (single source of truth) |
| `component_blueprint` | Agent 3 | Agent 5, 6 | Structural spec with token references |
| `framework_skills` | Agent 4 | Agent 5 | Framework coding conventions |
| `generated_code` | Agent 5 | Agent 6 | Initial generated code |
| `final_code` | Agent 6 | Output | Final verified code |

---

### Tools (Deterministic Python Functions)

#### `normalize_figma_node()` (Agent 1)
```python
def normalize_figma_node() -> dict:
    """
    Reads state['figma_node_json'] and:
    - Validates JSON structure
    - Converts RGB 0-1 to hex (#9447B0) and rgb_css (rgb(148,71,176))
    - Preserves exact px values (no rounding)
    - Extracts component name from root node
    - Writes to state['normalized_figma'], state['component_name'], state['root_dimensions']
    """
```

#### `extract_design_tokens()` (Agent 2)
```python
def extract_design_tokens() -> dict:
    """
    Reads state['normalized_figma'] and:
    - Walks entire tree
    - Extracts unique colors, spacing, fonts, radii, shadows
    - Generates Tailwind arbitrary value syntax for each token
    - Writes to state['design_tokens']
    """
```

#### `read_skills_file(framework: str)` (Agent 4)
```python
def read_skills_file(framework: str) -> dict:
    """
    Reads skills/{framework}.skills.md and:
    - For React: reads react-standalone.skills.md
    - Loads coding conventions, patterns, constraints
    - Writes to state['framework_skills']
    """
```

---

### Configuration

**File**: `pipeline/_config.py`
```python
GEMINI_MODEL = "gemini-2.5-pro"  # Shared model for all LLM agents
```

---

## 🚀 Usage Modes

### 1. CLI Mode (`main.py`)
```bash
# Default (uses sample_data/button_node.json + react)
python main.py

# Custom JSON file
python main.py --json path/to/design.json

# Custom framework
python main.py --json design.json --framework html

# With styling (tailwind | inline_css)
python main.py --json design.json --styling inline_css


# With special notes
python main.py --json design.json --notes "Add dark mode support"

# Notes from file
python main.py --json design.json --notes-file requirements.txt
```

**Output**: Writes generated code to `output/{ComponentName}.tsx`

---

### 2. API Mode (`server.py`)

#### Start Server
```bash
# Default (http://127.0.0.1:8000)
python server.py

# Custom host/port
python server.py --host 0.0.0.0 --port 3000

# Via uvicorn with auto-reload
uvicorn server:app --reload
```

#### API Endpoints

**POST /generate**
- **Request**:
  ```json
  {
    "figma_node_json": { /* Figma JSON object or string */ },
    "framework": "react",  // react | vue | angular | svelte | html
    "styling": "tailwind", // tailwind | inline_css (default: tailwind)
    "special_note": "Make it pixel perfect with exact colors. Use Tailwind CSS."
  }

    "figma_node_json": { /* Figma JSON object or string */ },
    "framework": "react",  // react | vue | angular | svelte
    "special_note": "Make it pixel perfect with exact colors. Use Tailwind CSS."
  }
  ```
- **Response**:
  ```json
  {
    "code": "import React from 'react';\n\nexport const LoginScreenContainer = ...",
    "component_name": "LoginScreenContainer",
    "framework": "react"
  }
  ```

**GET /health**
- **Response**: `{"status": "ok"}`

---

## 📁 Project Structure

```
FlowBridge.ai-Agent/
├── main.py                          # CLI entry point
├── server.py                        # FastAPI server
├── agent.py                         # ADK web UI root agent export
├── requirements.txt                 # Python dependencies
├── .env                             # GOOGLE_API_KEY
├── pipeline/
│   ├── orchestrator.py              # SequentialAgent wiring all 7 agents
│   ├── _config.py                   # GEMINI_MODEL config
│   ├── figma_parser_agent.py        # Agent 1: FigmaNormalizerAgent
│   ├── token_extractor_agent.py     # Agent 2: TokenExtractorAgent
│   ├── design_analyzer_agent.py     # Agent 3: DesignAnalyzerAgent
│   ├── skills_loader_agent.py       # Agent 4: SkillsLoaderAgent
│   ├── styling_agent.py             # Agent 5: StylingAgent
│   ├── code_generator_agent.py      # Agent 6: CodeGeneratorAgent
│   ├── code_reviewer_agent.py       # Agent 7: FidelityGateAgent
│   └── figma-tree-interpretation.md # Figma JSON format guide (821 lines)

│   ├── _config.py                   # GEMINI_MODEL config
│   ├── figma_parser_agent.py        # Agent 1: FigmaNormalizerAgent
│   ├── token_extractor_agent.py     # Agent 2: TokenExtractorAgent
│   ├── design_analyzer_agent.py     # Agent 3: DesignAnalyzerAgent
│   ├── skills_loader_agent.py       # Agent 4: SkillsLoaderAgent
│   ├── code_generator_agent.py      # Agent 5: CodeGeneratorAgent
│   ├── code_reviewer_agent.py       # Agent 6: FidelityGateAgent
│   └── figma-tree-interpretation.md # Figma JSON format guide (821 lines)
├── tools/
│   ├── figma_tools.py               # normalize_figma_node, extract_design_tokens
│   └── skills_tools.py              # read_skills_file
├── skills/
│   ├── react-standalone.skills.md   # React conventions (Tailwind only)
│   ├── react.skills.md              # React with shadcn/ui (not used)
│   ├── html.skills.md               # HTML conventions
│   ├── vue.skills.md                # Vue conventions
│   ├── angular.skills.md            # Angular conventions
│   └── svelte.skills.md             # Svelte conventions

│   ├── react-standalone.skills.md   # React conventions (Tailwind only)
│   ├── react.skills.md              # React with shadcn/ui (not used)
│   ├── vue.skills.md                # Vue conventions
│   ├── angular.skills.md            # Angular conventions
│   └── svelte.skills.md             # Svelte conventions
├── sample_data/
│   ├── button_node.json             # Sample Figma button
│   └── figma_article_node.json      # Sample Figma article layout
├── output/                          # Generated component files (CLI mode)
└── tests/
    ├── test_pipeline.py             # Pipeline integration tests
    └── test_tools.py                # Tool unit tests
```

---

## 🔑 Key Design Decisions

### 1. **Token-First Architecture**
- **Agent 2** extracts ALL design values into `design_tokens` (single source of truth)
- **Agent 3** references token IDs only (never raw values)
- **Agent 5** uses exact token values from the map
- **Agent 6** verifies every token appears in code
- **Why**: Prevents approximations, ensures pixel-perfect fidelity

### 2. **Deterministic Tools + LLM Reasoning**
- **Agents 1, 2, 4**: Deterministic Python tools (no LLM hallucination risk)
- **Agents 3, 5, 6**: LLM reasoning for structure, generation, verification
- **Why**: Combine reliability of code with reasoning power of LLM

### 3. **Figma Interpretation Guide as Context**
- **Agent 5** has 821-line `figma-tree-interpretation.md` prepended to instruction
- Explains Figma JSON format, color encoding, layout modes, etc.
- **Why**: Ensures LLM correctly interprets nested Figma structures

### 4. **Framework Skills as Code Conventions**
- **Agent 4** loads framework-specific `.skills.md` files
- React uses `react-standalone.skills.md` (Tailwind only, no UI libraries)
- **Why**: Ensures generated code follows framework best practices

### 5. **Fidelity Gate as Final Verification**
- **Agent 6** diffs code vs tokens and fixes violations inline
- Catches semantic class approximations (e.g., `bg-purple-600`)
- **Why**: Guarantees pixel-perfect output even if Agent 5 deviates

### 6. **No Template Variable Conflicts**
- **Issue**: ADK's instruction template engine treats `{variable}` as session state lookups
- **Solution**: Replaced `${r}`, `${g}`, `${b}` in JavaScript examples with string concatenation
- **Why**: Prevents runtime errors from curly braces in code examples

---

## 🧪 Example Flow

### Input
```json
{
  "figma_node_json": {
    "ui_root": {
      "id": "2995:10957",
      "type": "FRAME",
      "name": "Login Screen Container",
      "layout": {"mode": "VERTICAL", "spacing": 32, "width": 300, "height": 359},
      "children": [
        /* ... logo, header, form fields, button ... */
      ]
    }
  },
  "framework": "react",
  "special_note": "Make it pixel perfect with exact colors. Use Tailwind CSS."
}
```

### Agent 1 Output
```python
state['normalized_figma'] = {
  "ui_root": {
    "id": "2995:10957",
    "name": "Login Screen Container",
    "w": 300,
    "h": 359,
    "fills": [{"type": "SOLID", "color": "#FFFFFF", "rgb_css": "rgb(255,255,255)"}],
    # ... all colors converted to hex ...
  }
}
state['component_name'] = "LoginScreenContainer"
state['root_dimensions'] = {"width": 300, "height": 359}
```

### Agent 2 Output
```python
state['design_tokens'] = {
  "colors": [
    {"id": "color-9447B0", "hex": "#9447B0", "rgb_css": "rgb(148,71,176)", "tailwind": "bg-[#9447B0]"},
    {"id": "color-FFFFFF", "hex": "#FFFFFF", "rgb_css": "rgb(255,255,255)", "tailwind": "bg-[#FFFFFF]"}
  ],
  "spacing": [
    {"id": "spacing-32", "px": 32, "tailwind": "gap-[32px]"},
    {"id": "spacing-10", "px": 10, "tailwind": "py-[10px]"}
  ],
  # ... fonts, radii, shadows ...
}
```

### Agent 3 Output
```markdown
state['component_blueprint'] = """
## Component Identity
- **Component name:** LoginScreenContainer
- **Component type:** Screen / Form
- **Brief description:** Full-page login card with username/password fields

## Sections & Layout Tree
1. Logo_Section (HORIZONTAL, gap: spacing-7.5, align: CENTER)
2. Header_Text_Section (VERTICAL, gap: spacing-4.5)
3. Login_Form (VERTICAL, gap: spacing-12)
   - Username input (border: color-DBDADE, radius: radius-6)
   - Password input (border: color-DBDADE, radius: radius-6)
   - Submit button (bg: color-9447B0, text: color-FFFFFF, radius: radius-6)

## Props Interface
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| onSubmit | (data: {username: string, password: string}) => void | Yes | - | Form submit handler |
| isLoading | boolean | No | false | Loading state |

## Interactive Elements
- **Submit Button**
  - default: bg color-9447B0, text color-FFFFFF
  - hover: darken bg by 10%
  - disabled: opacity 50%, cursor-not-allowed

## Style Token Map
- Root container: spacing-32 (gap), color-FFFFFF (bg)
- Submit button: color-9447B0 (bg), radius-6 (rounded)
"""
```

### Agent 4 Output
```python
state['framework_skills'] = """
# React Standalone Skills

## Component Structure
1. Single .tsx file
2. Import order: React, types, utils
3. Named export only

## Styling
- Tailwind CSS with EXACT arbitrary values
- ✅ bg-[#9447B0]  ❌ bg-purple-600
- ✅ gap-[32px]  ❌ gap-8

## Dependencies
- ONLY: react, react-dom
- NO: lucide-react, shadcn/ui, icon libraries

## TypeScript
- All props typed
- Explicit return types
"""
```

### Agent 5 Output
```tsx
state['generated_code'] = `
import React, { useState } from 'react';

type LoginScreenContainerProps = {
  onSubmit: (data: { username: string; password: string }) => void;
  isLoading?: boolean;
};

export const LoginScreenContainer = ({ onSubmit, isLoading = false }: LoginScreenContainerProps) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ username, password });
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-[32px] w-[300px] h-[359px] bg-[#FFFFFF] p-[24px] rounded-[16px]">
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="border border-[#DBDADE] rounded-[6px] px-[14px] py-[7px]"
        placeholder="Enter your username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="border border-[#DBDADE] rounded-[6px] px-[14px] py-[7px]"
        placeholder="Enter your password"
      />
      <button
        type="submit"
        disabled={isLoading}
        className="bg-[#9447B0] text-[#FFFFFF] rounded-[6px] px-[20px] py-[10px] hover:bg-[#7A3990] disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Loading...' : 'Login'}
      </button>
    </form>
  );
};
`
```

### Agent 6 Output
```python
# Verifies:
# ✅ color-9447B0 (#9447B0) present as bg-[#9447B0]
# ✅ color-FFFFFF (#FFFFFF) present as bg-[#FFFFFF]
# ✅ spacing-32 (32px) present as gap-[32px]
# ✅ radius-6 (6px) present as rounded-[6px]
# ✅ All interactive states implemented

state['final_code'] = state['generated_code']  # No corrections needed
```

### Final Output
```json
{
  "code": "import React, { useState } from 'react';\n\ntype LoginScreenContainerProps = ...",
  "component_name": "LoginScreenContainer",
  "framework": "react"
}
```

---

## 🔍 Debugging & Monitoring

### Agent Progress Logging (CLI Mode)
```
============================================================
FlowBridge.ai — Generating React component
============================================================

[FigmaNormalizerAgent] Normalized: LoginScreenContainer | root 300x359px | all values preserved exactly...
[TokenExtractorAgent] Tokens extracted: 3 colors, 9 spacing, 2 fonts, 1 radii, 1 shadows...
[DesignAnalyzerAgent] ## Component Identity - **Component name:** LoginScreenContainer...
[SkillsLoaderAgent] Loaded: react.skills.md Key conventions: 1. Component Structure...
[StylingAgent] Selected styling: tailwind. Rules generated for class mappings.
[CodeGeneratorAgent] import React, { useState } from 'react';...
[FidelityGateAgent] ✅ All tokens verified. Final code complete.

[TokenExtractorAgent] Tokens extracted: 3 colors, 9 spacing, 2 fonts, 1 radii, 1 shadows...
[DesignAnalyzerAgent] ## Component Identity - **Component name:** LoginScreenContainer...
[SkillsLoaderAgent] Loaded: react.skills.md Key conventions: 1. Component Structure...
[CodeGeneratorAgent] import React, { useState } from 'react';...
[FidelityGateAgent] ✅ All tokens verified. Final code complete.

Component generated: output/LoginScreenContainer.tsx
```

### Session State Inspection
```python
# During development, inspect state at any point:
from google.adk.sessions import Session

session = runner.run(orchestrator, inputs={...})
print(session.state['design_tokens'])  # View extracted tokens
print(session.state['component_blueprint'])  # View blueprint
```

---

## 🚧 Known Limitations

1. **Figma JSON Format**: Requires pre-cleaned Figma JSON (from Figma plugin or API)
2. **Tailwind Only**: Currently only supports Tailwind CSS (no CSS-in-JS, styled-components)
3. **No Image Assets**: Doesn't download/embed images (uses placeholders)
4. **Single Component**: Generates one component per call (no multi-file outputs)
5. **No Backend Logic**: UI only (no API calls, auth, state management libraries)

---

## 🔮 Future Enhancements

- [ ] Direct Figma API integration (no plugin needed)
- [ ] Support for styled-components, Emotion, CSS Modules
- [ ] Image asset download and embedding
- [ ] Multi-component generation (design systems)
- [ ] Component library integration (Material-UI, Ant Design)
- [ ] Animation and interaction code generation
- [ ] Responsive breakpoint handling
- [ ] Theme and dark mode support
- [ ] Storybook story generation
- [ ] Unit test generation

---

## 📚 References

- **Google ADK**: https://github.com/google/adk-python
- **Gemini 2.5 Pro**: https://ai.google.dev/gemini-api/docs
- **Tailwind CSS**: https://tailwindcss.com/docs/adding-custom-styles#arbitrary-values
- **Figma REST API**: https://www.figma.com/developers/api

---

## 📝 License

MIT License - See LICENSE file for details.

---

**Built with ❤️ using Google ADK and Gemini 2.5 Pro**
