"""
main.py — FlowBridge.ai entry point.

Usage:
  python main.py
  python main.py --json path/to/my_component.json --framework vue --styling inline_css
  python main.py --json path/to/my_component.json --notes "Make it dark mode"
  python main.py --json path/to/my_component.json --notes-file path/to/notes.txt
"""

import argparse
import asyncio
import json
import re as _re
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from pipeline.orchestrator import orchestrator
from tools.figma_tools import _normalize_node, _to_pascal_case
from tools.skills_tools import load_skills_content

load_dotenv()

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_JSON_PATH = "sample_data/button_node.json"
DEFAULT_FRAMEWORK = "react"
DEFAULT_SPECIAL_NOTES = """
This is a Login Page component.
The root frame is the full login card, centered on the page.

1. OVERALL LAYOUT:
   - Render a full-viewport centered wrapper (min-h-screen, flex, items-center,
     justify-center, bg-gray-50).
   - The card itself matches the root frame width/height from the JSON.
   - Add 32px padding inside the card and a subtle white background with a
     light box shadow so it reads as a card on the grey page.

2. FORM FIELDS:
   - Render all fields from the JSON with their exact labels and placeholders.
   - Use React useState to track all field values.
   - Password field with eye icon for show/hide toggle.

3. SUBMIT BUTTON:
   - Full-width, exact colors from the JSON.
   - Hover: darken background slightly.
   - Disabled state: 50% opacity, cursor-not-allowed.
   - Loading state: replace text with 'Logging in...' + spinner, aria-busy=true.

4. FORM VALIDATION:
   - All fields required — show inline error on blur.
   - Disable submit button until all fields pass validation.

5. ACCESSIBILITY:
   - All inputs have associated <label> elements.
   - Error messages use aria-live='polite'.
   - Auto-focus first input field on mount.
   - Submit button is type='submit' inside a <form>.
"""

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="FlowBridge.ai — generate a UI component from Figma JSON.",
    )
    parser.add_argument("--json", metavar="PATH", default=DEFAULT_JSON_PATH)
    parser.add_argument("--framework", metavar="NAME", default=DEFAULT_FRAMEWORK,
                        choices=["react", "vue", "angular", "svelte", "html"])
    parser.add_argument("--notes", metavar="TEXT", default=None)
    parser.add_argument("--notes-file", metavar="PATH", default=None)
    parser.add_argument("--styling", metavar="MODE", default="tailwind",
                        choices=["tailwind", "inline_css"])
    return parser.parse_args()


APP_NAME = "flowbridge"
USER_ID = "developer"

# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

async def run_pipeline(
    figma_json_str: str,
    framework: str,
    special_notes: str,
    styling: str = "tailwind",
) -> tuple[str, str, dict]:
    """
    Pre-processes inputs (normalize Figma JSON, load skills) then runs a
    single CodeGeneratorAgent call.
    Returns: (generated_code, component_name, root_dimensions)
    """
    # --- Pre-processing (pure Python, no LLM) ---
    try:
        data = json.loads(figma_json_str)
        ui_root_raw = data.get("ui_root", data)

        # Normalize: converts 0-1 RGB floats → hex, expands padding arrays, etc.
        normalized_root = _normalize_node(ui_root_raw)
        normalized_json = json.dumps({"ui_root": normalized_root})

        # Derive component name and root dimensions from the normalized tree
        raw_name = normalized_root.get("name", "Component")
        component_name = _to_pascal_case(raw_name)
        layout = normalized_root.get("layout", {})
        root_dimensions = {"width": layout.get("width", 400), "height": layout.get("height", 600)}
    except Exception:
        normalized_json = figma_json_str
        component_name = "GeneratedComponent"
        root_dimensions = {"width": 400, "height": 600}

    # Load framework-specific coding standards (skills file)
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

    runner = Runner(agent=orchestrator, app_name=APP_NAME, session_service=session_service)

    trigger = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=(
            f"Generate a production-ready {framework.capitalize()} "
            f"component from the Figma design in session state."
        ))],
    )

    print(f"\n{'='*60}")
    print(f"FlowBridge.ai — Generating {framework.capitalize()} component")
    print(f"{'='*60}\n")

    async for event in runner.run_async(user_id=USER_ID, session_id=session.id, new_message=trigger):
        if hasattr(event, "author") and event.author:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(f"[{event.author}] {part.text[:120].replace(chr(10), ' ')}...")

    updated_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session.id
    )
    state = updated_session.state

    final_code = state.get("generated_code", "") or "ERROR: Pipeline did not produce any code."

    # Strip markdown fences if the LLM wrapped the code
    final_code = _re.sub(r'^```[\w]*\n?', '', final_code.strip(), flags=_re.MULTILINE)
    final_code = _re.sub(r'^```\s*$', '', final_code, flags=_re.MULTILINE)
    final_code = final_code.strip()

    return final_code, component_name, root_dimensions


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    json_path = Path(args.json)
    if not json_path.exists():
        print(f"[error] JSON file not found: {json_path}")
        sys.exit(1)
    figma_node_json = json_path.read_text(encoding="utf-8")

    framework = args.framework
    styling = args.styling

    if args.notes:
        special_notes = args.notes
    elif args.notes_file:
        notes_path = Path(args.notes_file)
        if not notes_path.exists():
            print(f"[error] Notes file not found: {notes_path}")
            sys.exit(1)
        special_notes = notes_path.read_text(encoding="utf-8")
    else:
        special_notes = DEFAULT_SPECIAL_NOTES

    print(f"[config] JSON     : {json_path}")
    print(f"[config] Framework: {framework}")
    print(f"[config] Styling  : {styling}")

    final_code, component_name, root_dims = asyncio.run(
        run_pipeline(figma_node_json, framework, special_notes, styling)
    )

    print(f"\n{'='*60}")
    print("FINAL GENERATED COMPONENT CODE")
    print(f"{'='*60}\n")
    print(final_code)

    ext_map = {"react": "tsx", "vue": "vue", "angular": "ts", "svelte": "svelte", "html": "html"}
    output_path = Path(f"output/{component_name}.{ext_map.get(framework, framework)}")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(final_code, encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Saved to: {output_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
