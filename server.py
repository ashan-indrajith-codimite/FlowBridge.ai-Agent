"""
server.py — FlowBridge.ai FastAPI server.

Exposes a single endpoint that accepts a Figma node JSON tree,
target framework, and optional special notes — then runs the
multi-agent code generation pipeline and returns the result as JSON.

Usage:
  # Start the server (default port 8000):
  python server.py

  # Custom host/port:
  python server.py --host 0.0.0.0 --port 3000

  # Or via uvicorn directly:
  uvicorn server:app --reload
"""

import argparse
import json
from enum import Enum
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from main import run_pipeline

# ---------------------------------------------------------------------------
# Load environment variables (.env must contain GOOGLE_API_KEY)
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="FlowBridge.ai",
    description="Generate pixel-faithful UI components from Figma design JSON.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS middleware - allow requests from Chrome Extension
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Chrome extensions use chrome-extension://)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class Framework(str, Enum):
    react = "react"
    vue = "vue"
    angular = "angular"
    svelte = "svelte"
    html = "html"

class Styling(str, Enum):
    inline_css = "inline_css"
    tailwind = "tailwind"

class GenerateRequest(BaseModel):
    figma_node_json: Any = Field(
        ...,
        description=(
            "The cleaned Figma node JSON tree. "
            "Can be a JSON object (dict) or a pre-serialized JSON string."
        ),
    )
    framework: Framework = Field(
        default=Framework.react,
        description="Target UI framework for code generation.",
    )
    styling: Styling = Field(
        default=Styling.tailwind,
        description="Styling approach: 'tailwind' for Tailwind CSS utility classes, 'inline_css' for inline style attributes.",
    )
    special_note: str = Field(
        default="",
        description="Optional designer notes or extra requirements for the LLM.",
    )


class GenerateResponse(BaseModel):
    code: str = Field(..., description="The generated component source code.")
    component_name: str = Field(..., description="PascalCase component name derived from the Figma root node.")
    framework: str = Field(..., description="The target framework that was used.")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post(
    "/generate",
    response_model=GenerateResponse,
    summary="Generate a UI component from Figma JSON",
)
async def generate(req: GenerateRequest) -> GenerateResponse:
    """
    Accepts a cleaned Figma node JSON tree, a target framework, and an
    optional special note.  Runs the full FlowBridge.ai multi-agent
    pipeline and returns the generated component code as JSON.
    """
    # Normalise figma_node_json to a JSON string (the pipeline expects a string)
    if isinstance(req.figma_node_json, (dict, list)):
        figma_json_str = json.dumps(req.figma_node_json)
    elif isinstance(req.figma_node_json, str):
        # Validate it's actually valid JSON
        try:
            json.loads(req.figma_node_json)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"figma_node_json is not valid JSON: {exc}",
            )
        figma_json_str = req.figma_node_json
    else:
        raise HTTPException(
            status_code=422,
            detail="figma_node_json must be a JSON object or a JSON string.",
        )

    framework_str = req.framework.value
    styling_str = req.styling.value
    special_notes = req.special_note or ""

    try:
        final_code, component_name, _root_dims = await run_pipeline(
            figma_json_str, framework_str, special_notes, styling_str
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline error: {exc}",
        )

    # Guard against pipeline producing no usable code
    if not final_code or final_code.startswith("ERROR:"):
        raise HTTPException(
            status_code=500,
            detail=final_code or "Pipeline did not produce any code.",
        )

    return GenerateResponse(
        code=final_code,
        component_name=component_name,
        framework=framework_str,
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="FlowBridge.ai API server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    uvicorn.run(
        "server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
