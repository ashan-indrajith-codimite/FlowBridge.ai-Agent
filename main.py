"""
main.py — FlowBridge.ai entry point.

Hardcoded inputs (figma_node_json, framework, special_notes) will later
be replaced by real Figma plugin data. For now, runs the full pipeline
against the sample button node and prints the generated component code.
"""

import asyncio
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


async def run_pipeline() -> str:
    """
    Creates a session with the hardcoded initial state, runs the
    FlowBridge orchestrator pipeline, and returns the final component code.
    """
    session_service = InMemorySessionService()

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state={
            "figma_node_json": FIGMA_NODE_JSON,
            "framework": FRAMEWORK,
            "special_notes": SPECIAL_NOTES,
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
                    f"Generate a production-ready {FRAMEWORK.capitalize()} "
                    f"component from the Figma design in session state."
                )
            )
        ],
    )

    print(f"\n{'='*60}")
    print(f"FlowBridge.ai — Generating {FRAMEWORK.capitalize()} component")
    print(f"{'='*60}\n")

    final_code = ""

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

        if event.is_final_response():
            if event.content and event.content.parts:
                final_code = event.content.parts[0].text
                break

    return final_code


def main() -> None:
    code = asyncio.run(run_pipeline())

    print(f"\n{'='*60}")
    print("FINAL GENERATED COMPONENT CODE")
    print(f"{'='*60}\n")
    print(code)

    # Optionally save to file
    output_path = Path(f"output/LoginScreen.{'tsx' if FRAMEWORK == 'react' else FRAMEWORK}")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(code, encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"Saved to: {output_path}")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
