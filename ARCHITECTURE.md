# FlowBridge.ai Architecture

## 🎯 Overview

**FlowBridge.ai** is a streamlined AI system that converts Figma design JSON into pixel-perfect, production-ready UI components. Built with [Google ADK](https://github.com/google/adk-python) and powered by Gemini 2.5 Pro, it uses a **single-agent architecture** for fast, direct code generation from raw Figma JSON.

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
                    │  - Derive component_name    │
                    │  - Initialize ADK Runner    │
                    │  - Create Session + State   │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   CodeGeneratorAgent        │
                    │   (Single LLM Call)         │
                    │   Gemini 2.5 Pro            │
                    └──────────────┬──────────────┘
                                   │
                         ┌─────────▼─────────┐
                         │  generated_code   │
                         │  (Final Output)   │
                         └───────────────────┘
```

---

## 🔄 Pipeline Flow

### Input Processing (Pure Python - No LLM)

```python
# main.py / server.py
def run_pipeline(figma_json_str, framework, special_notes, styling):
    # 1. Parse JSON and derive component name
    data = json.loads(figma_json_str)
    root = data.get("ui_root", data)
    component_name = "".join(w.capitalize() for w in re.split(r"[\s_\-]+", root.get("name", "Component")) if w)
    
    # 2. Put everything into session state
    state = {
        "figma_node_json": figma_json_str,  # Raw JSON string
        "framework": framework,             # 'react', 'vue', 'angular', 'svelte', 'html'
        "styling": styling,                 # 'tailwind' or 'inline_css'
        "special_notes": special_notes,     # Designer requirements
        "component_name": component_name,   # PascalCase name
    }
    
    # 3. Run single agent
    session = await session_service.create_session(state=state)
    runner = Runner(agent=orchestrator)
    async for event in runner.run_async(...):
        # Agent executes, writes to state['generated_code']
        pass
    
    return state['generated_code']
```

### Single LLM Call (CodeGeneratorAgent)

The `CodeGeneratorAgent` receives **all 5 inputs injected into its system prompt** via ADK's `inject_session_state` mechanism:

```
SYSTEM PROMPT (after ADK substitution):
═══════════════════════════════════════════════════════
INPUTS (injected from session state)
═══════════════════════════════════════════════════════

FIGMA NODE JSON (the design to implement exactly):
{ "ui_root": { "name": "Login Screen Container", ... } }

TARGET FRAMEWORK: react
STYLING APPROACH: tailwind
COMPONENT NAME: LoginScreenContainer

SPECIAL NOTES FROM DESIGNER:
Make it pixel perfect with the exact colors from the design.

═══════════════════════════════════════════════════════
FIGMA NODE TREE INTERPRETATION REFERENCE
═══════════════════════════════════════════════════════
[... Figma JSON structure documentation ...]

═══════════════════════════════════════════════════════
PIXEL FIDELITY — NON-NEGOTIABLE
═══════════════════════════════════════════════════════
Read every color, spacing, font size, border radius, and shadow directly from
the FIGMA NODE JSON above and use the EXACT values in the output code.
[... detailed styling rules ...]
```

**Key Technical Detail**: The instruction uses `{figma_node_json}`, `{framework}`, `{styling}`, `{component_name}`, `{special_notes}` placeholder syntax, which ADK's `inject_session_state` function replaces with actual session state values at runtime before sending to the LLM.

---

## 📁 Project Structure

```
C:\Users\Admin\Desktop\FlowBridge.ai-Agent\
├── agent.py                    # Root agent export (orchestrator)
├── main.py                     # CLI entry point
├── server.py                   # FastAPI API server
├── pipeline/
│   ├── _config.py              # Model selection (GEMINI_MODEL = "gemini-2.5-pro")
│   ├── orchestrator.py         # Wraps CodeGeneratorAgent in SequentialAgent
│   ├── code_generator_agent.py # Single LLM agent (LlmAgent)
│   └── figma-tree-interpretation.md  # Figma JSON structure reference
├── tools/
│   ├── figma_tools.py          # (Legacy - not used)
│   └── skills_tools.py         # (Legacy - not used)
└── tests/
    └── test_pipeline.py        # 27 unit tests (all passing)
```

---

## 🔧 How It Works

### 1. No Preprocessing

**Old architecture** (removed):
- `FigmaNormalizerAgent` — normalized JSON structure
- `TokenExtractorAgent` — extracted design tokens
- `DesignAnalyzerAgent` — analyzed component hierarchy
- `SkillsLoaderAgent` — loaded framework-specific patterns
- `StylingAgent` — generated styling conventions

**New architecture** (current):
- **None** — raw Figma JSON goes directly to the LLM

### 2. Single LLM Call

The `CodeGeneratorAgent`:
- Receives raw Figma JSON + framework + styling + notes in the system prompt
- Uses a comprehensive instruction with:
  - Figma JSON interpretation guide (1000+ lines of structural documentation)
  - Pixel-fidelity rules (exact colors, spacing, shadows)
  - Framework-specific patterns (React/Vue/Angular/Svelte/HTML)
  - Styling rules (Tailwind arbitrary values or inline CSS)
  - Completeness requirements (all states, validation, accessibility)
- Outputs complete component code in a single response

### 3. State Injection Mechanism

**Critical implementation detail**: ADK's `LlmAgent` uses `inject_session_state()` to substitute `{placeholder}` patterns in the instruction string with session state values.

```python
# In code_generator_agent.py
_CODE_GENERATOR_BASE_INSTRUCTION = """
You are an expert UI component code generator.

FIGMA NODE JSON (the design to implement exactly):
{figma_node_json}  # ← ADK replaces this with state["figma_node_json"]

TARGET FRAMEWORK: {framework}  # ← ADK replaces with state["framework"]
STYLING APPROACH: {styling}    # ← ADK replaces with state["styling"]
...
"""
```

**Without these placeholders**, the LLM would receive an empty instruction — the bug we fixed in commit `9f8fa5f`.

### 4. Brace Escaping for Static Content

The Figma interpretation guide (loaded from `figma-tree-interpretation.md`) contains JSON code examples with `{r}`, `{g}`, `{b}`, `{x}`, `{y}` etc. To prevent ADK from treating these as session state keys, we escape them:

```python
_FIGMA_INTERPRETATION_GUIDE = _INTERPRETATION_GUIDE_PATH.read_text(encoding="utf-8")
_FIGMA_INTERPRETATION_GUIDE_ESCAPED = _FIGMA_INTERPRETATION_GUIDE.replace("{", "{{").replace("}", "}}")
```

This ensures `{r}` becomes `{{r}}`, which ADK leaves as-is (literal `{r}` in the final prompt).

---

## 🚀 Performance

**Old 7-agent architecture**:
- 7 sequential LLM calls
- ~30-60 seconds per component
- Complex state management across agents

**New single-agent architecture**:
- 1 LLM call
- ~5-10 seconds per component
- Minimal state management (5 keys in, 1 key out)

**Speed improvement**: **6-12x faster** ⚡

---

## 🎨 Supported Frameworks & Styling

### Frameworks
- **React** (`framework: "react"`) — TypeScript, functional components
- **Vue** (`framework: "vue"`) — TypeScript, Composition API
- **Angular** (`framework: "angular"`) — TypeScript, standalone components
- **Svelte** (`framework: "svelte"`) — TypeScript
- **HTML** (`framework: "html"`) — Vanilla JS, self-contained `.html` file

### Styling
- **Tailwind CSS** (`styling: "tailwind"`)
  - Uses arbitrary values: `className="bg-[#9447B0] text-[19.5px] rounded-[6px]"`
  - No inline styles
- **Inline CSS** (`styling: "inline_css"`)
  - React/Vue/Angular: `style={{backgroundColor: '#9447B0', fontSize: '19.5px'}}`
  - HTML: `style="background-color: #9447B0; font-size: 19.5px;"`
  - No Tailwind classes

---

## 📝 Example Usage

### CLI Mode

```bash
python main.py --json sample_data/login.json --framework react --styling tailwind
```

### API Mode

```bash
# Start server
python server.py

# POST request
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "figma_node_json": { "ui_root": { "name": "Login Screen", ... } },
    "framework": "react",
    "styling": "tailwind",
    "special_note": "Make it pixel perfect"
  }'
```

**Response:**
```json
{
  "code": "import React, { useState } from 'react';\n\nexport function LoginScreen() { ... }",
  "component_name": "LoginScreen",
  "framework": "react"
}
```

---

## 🧪 Testing

```bash
# Run all tests (27 unit tests)
pytest tests/test_pipeline.py -v

# Test coverage
- Config validation (2 tests)
- CodeGeneratorAgent structure (11 tests)
- Orchestrator structure (5 tests)
- Component name derivation (4 tests)
- Import validation (2 tests)
- End-to-end pipeline (3 tests)
```

**All tests passing** ✅

---

## 🔍 State Flow

```
INPUT (main.py / server.py)
  ↓
  figma_json_str: str
  framework: str
  special_notes: str
  styling: str
  ↓
SESSION STATE (created)
  {
    "figma_node_json": figma_json_str,
    "framework": framework,
    "styling": styling,
    "special_notes": special_notes,
    "component_name": component_name  # derived from JSON
  }
  ↓
CodeGeneratorAgent (LLM reads state via {placeholders})
  ↓
SESSION STATE (updated)
  {
    ...existing keys...,
    "generated_code": "<complete component code>"
  }
  ↓
OUTPUT (main.py / server.py)
  final_code: str
  component_name: str
  root_dimensions: dict
```

---

## 🛠️ Configuration

### Model Selection

```python
# pipeline/_config.py
GEMINI_MODEL = "gemini-2.5-pro"  # High-quality model for code generation
```

### Environment Variables

```bash
# .env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## 📚 Dependencies

```txt
# Core
google-genai-adk>=0.2.0  # ADK framework
fastapi>=0.115.0         # API server
uvicorn>=0.34.0          # ASGI server
python-dotenv>=1.0.0     # Environment variables

# Testing
pytest>=8.3.0
pytest-asyncio>=0.24.0
```

---

## 🚨 Critical Bug Fixed (Commit 9f8fa5f)

**Problem**: LLM was generating wrong output (profile UI instead of login UI) because `figma_node_json` was never actually sent to the LLM.

**Root Cause**: ADK's `inject_session_state()` requires `{placeholder}` syntax in the instruction string to substitute session state values. The original instruction just mentioned the variable names in prose, without the `{braces}`.

**Fix**: Added `{figma_node_json}`, `{framework}`, `{styling}`, `{component_name}`, `{special_notes}` placeholders to the instruction, and brace-escaped the Figma interpretation guide to prevent ADK from treating JSON examples like `{r}`, `{g}`, `{b}` as session state keys.

**Verification**: End-to-end test with Login Screen JSON now correctly outputs a login form component with all expected elements (username, password, welcome text, admin studio branding).

---

## 📖 Further Reading

- **Google ADK Documentation**: https://github.com/google/adk-python
- **Gemini API**: https://ai.google.dev/gemini-api/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **Figma Plugin API**: https://www.figma.com/plugin-docs/api/api-overview/

---

## 🎯 Design Principles

1. **Zero Preprocessing** — Raw Figma JSON → LLM → Code
2. **Single Responsibility** — One agent, one job
3. **Pixel Fidelity** — Exact colors, spacing, shadows from JSON
4. **Framework Agnostic** — Same pipeline works for React/Vue/Angular/Svelte/HTML
5. **Stateless** — Each request is independent, no persistent state
6. **Fast** — 5-10 seconds per component (6-12x faster than old architecture)

---

## 📄 License

MIT License - See LICENSE file for details.
