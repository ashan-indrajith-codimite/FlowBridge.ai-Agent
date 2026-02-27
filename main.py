"""
main.py — FlowBridge.ai entry point.

Usage:
  # Use defaults (sample_data/button_node.json, react, built-in special notes):
  python main.py

  # Custom JSON file:
  python main.py --json path/to/my_component.json

  # Custom JSON + framework:
  python main.py --json path/to/my_component.json --framework vue

  # Custom JSON + special notes:
  python main.py --json path/to/my_component.json --notes "Make it dark mode"

  # Custom JSON + notes from a file:
  python main.py --json path/to/my_component.json --notes-file path/to/notes.txt

  # All options:
  python main.py --json path/to/my_component.json --framework react --notes "notes here"
"""

import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from pipeline.orchestrator import orchestrator

# ---------------------------------------------------------------------------
# Load environment variables (.env must contain GOOGLE_API_KEY)
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Default inputs (used when no CLI args are passed)
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
# CLI argument parser
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="FlowBridge.ai — generate a pixel-faithful component from Figma JSON.",
    )
    parser.add_argument(
        "--json",
        metavar="PATH",
        default=DEFAULT_JSON_PATH,
        help=f"Path to Figma node JSON file (default: {DEFAULT_JSON_PATH})",
    )
    parser.add_argument(
        "--framework",
        metavar="NAME",
        default=DEFAULT_FRAMEWORK,
        choices=["react", "vue", "angular", "svelte"],
        help="Target framework (default: react)",
    )
    parser.add_argument(
        "--notes",
        metavar="TEXT",
        default=None,
        help="Special design notes as a plain string",
    )
    parser.add_argument(
        "--notes-file",
        metavar="PATH",
        default=None,
        help="Path to a .txt file containing special design notes",
    )
    return parser.parse_args()


APP_NAME = "flowbridge"
USER_ID = "developer"


async def run_pipeline(figma_node_json: str, framework: str, special_notes: str) -> tuple[str, str, dict]:
    """
    Creates a session with the given inputs, runs the FlowBridge orchestrator
    pipeline, and returns: (final_code, component_name, root_dimensions)
    """
    session_service = InMemorySessionService()

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state={
            "figma_node_json": figma_node_json,
            "framework": framework,
            "special_notes": special_notes,
        },
    )

    runner = Runner(
        agent=orchestrator,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # Trigger message — the pipeline reads everything from state,
    # so the content of this message is just a start signal.
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

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=trigger,
    ):
        # Print agent activity to console for visibility
        if hasattr(event, "author") and event.author:
            agent_name = event.author
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        preview = part.text[:120].replace("\n", " ")
                        print(f"[{agent_name}] {preview}...")

    # Read state after pipeline completes
    updated_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session.id,
    )
    state = updated_session.state

    final_code = state.get("final_code", "")

    if not final_code:
        # Fallback: try generated_code (in case fidelity gate didn't run)
        final_code = state.get("generated_code", "")

    if not final_code:
        final_code = "ERROR: Pipeline did not produce any code. Check agent logs above."

    # Strip markdown fences if the LLM wrapped the code in ```tsx ... ```
    import re as _re
    final_code = _re.sub(r'^```[\w]*\n?', '', final_code.strip(), flags=_re.MULTILINE)
    final_code = _re.sub(r'^```\s*$', '', final_code, flags=_re.MULTILINE)
    final_code = final_code.strip()

    component_name: str = state.get("component_name", "GeneratedComponent")
    root_dimensions: dict = state.get("root_dimensions", {"width": 400, "height": 600})

    return final_code, component_name, root_dimensions


def main() -> None:
    args = parse_args()

    # Resolve JSON input
    json_path = Path(args.json)
    if not json_path.exists():
        print(f"[error] JSON file not found: {json_path}")
        sys.exit(1)
    figma_node_json = json_path.read_text(encoding="utf-8")

    framework = args.framework

    # Resolve special notes (CLI string > notes file > default)
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

    print(f"[config] JSON   : {json_path}")
    print(f"[config] Framework: {framework}")
    print(f"[config] Notes  : {'(from --notes)' if args.notes else '(from --notes-file)' if args.notes_file else '(default)'}")

    final_code, component_name, root_dims = asyncio.run(
        run_pipeline(figma_node_json, framework, special_notes)
    )

    print(f"\n{'='*60}")
    print("FINAL GENERATED COMPONENT CODE")
    print(f"{'='*60}\n")
    print(final_code)

    # Derive file extension from framework
    ext = "tsx" if framework == "react" else framework
    output_path = Path(f"output/{component_name}.{ext}")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(final_code, encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Saved to: {output_path}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
