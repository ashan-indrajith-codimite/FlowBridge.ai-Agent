"""
main.py — FlowBridge.ai entry point.

Hardcoded inputs (figma_node_json, framework, special_notes) will later
be replaced by real Figma plugin data. For now, runs the full pipeline
against the sample button node and prints the generated component code.
"""

import asyncio
import json
import re as _re
from pathlib import Path

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from pipeline.orchestrator import orchestrator
from tools.figma_tools import _normalize_node, _to_pascal_case
from tools.skills_tools import load_skills_content

# ---------------------------------------------------------------------------
# Load environment variables (.env must contain GOOGLE_API_KEY)
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Hardcoded inputs
# ---------------------------------------------------------------------------

# Raw Figma node JSON — loaded from the sample file
FIGMA_NODE_JSON: str = Path("sample_data/button_node.json").read_text(encoding="utf-8")

# Target framework (one of: react, vue, angular, svelte)
FRAMEWORK: str = "react"

# Designer notes — describe interactive states, branding requirements, etc.
SPECIAL_NOTES: str = """

"""

# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

APP_NAME = "flowbridge"
USER_ID = "developer"


async def run_pipeline(
    figma_json_str: str | None = None,
    framework: str | None = None,
    special_notes: str | None = None,
    styling: str = "tailwind",
) -> tuple[str, str, dict]:
    """
    Pre-processes inputs then runs a single CodeGeneratorAgent call.
    Falls back to hardcoded globals when called with no arguments (CLI mode).
    Returns: (generated_code, component_name, root_dimensions)
    """
    figma_json_str = figma_json_str if figma_json_str is not None else FIGMA_NODE_JSON
    framework = framework if framework is not None else FRAMEWORK
    special_notes = special_notes if special_notes is not None else SPECIAL_NOTES

    # --- Pre-processing (pure Python, no LLM) ---
    try:
        data = json.loads(figma_json_str)
        ui_root_raw = data.get("ui_root", data)
        normalized_root = _normalize_node(ui_root_raw)
        normalized_json = json.dumps({"ui_root": normalized_root})
        raw_name = normalized_root.get("name", "Component")
        component_name = _to_pascal_case(raw_name)
        layout = normalized_root.get("layout", {})
        root_dimensions = {"width": layout.get("width", 400), "height": layout.get("height", 600)}
    except Exception:
        normalized_json = figma_json_str
        component_name = "GeneratedComponent"
        root_dimensions = {"width": 400, "height": 600}

    framework_skills = load_skills_content(framework)

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state={
            "figma_node_json": normalized_json,
            "framework": framework,
            "styling": styling,
            "special_notes": special_notes,
            "component_name": component_name,
            "framework_skills": framework_skills,
        },
    )

    runner = Runner(
        agent=orchestrator,
        app_name=APP_NAME,
        session_service=session_service,
    )

    trigger = genai_types.Content(
        role="user",
        parts=[
            genai_types.Part(
                text=(
                    f"Generate a production-ready {framework.capitalize()} "
                    f"component from the Figma design in session state."
                )
            )
        ],
    )

    print(f"\n{'='*60}")
    print(f"FlowBridge.ai — Generating {framework.capitalize()} component")
    print(f"{'='*60}\n")

    final_code = ""

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=trigger,
    ):
        if hasattr(event, "author") and event.author:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        preview = part.text[:120].replace("\n", " ")
                        print(f"[{event.author}] {preview}...")

        if event.is_final_response():
            if event.content and event.content.parts:
                final_code = event.content.parts[0].text
                break

    # Strip markdown fences if the LLM wrapped the code
    final_code = _re.sub(r'^```[\w]*\n?', '', final_code.strip(), flags=_re.MULTILINE)
    final_code = _re.sub(r'^```\s*$', '', final_code, flags=_re.MULTILINE)
    final_code = final_code.strip()

    return final_code, component_name, root_dimensions


def main() -> None:
    code, component_name, _ = asyncio.run(run_pipeline())

    print(f"\n{'='*60}")
    print("FINAL GENERATED COMPONENT CODE")
    print(f"{'='*60}\n")
    print(code)

    ext_map = {"react": "tsx", "vue": "vue", "angular": "ts", "svelte": "svelte", "html": "html"}
    output_path = Path(f"output/{component_name}.{ext_map.get(FRAMEWORK, FRAMEWORK)}")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(code, encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"Saved to: {output_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
