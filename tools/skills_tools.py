"""
Skills Tools — reads framework .skills.md files into session state.

read_skills_file is the only public tool exposed to the ADK agent.
It writes directly to state["framework_skills"], bypassing output_key.
"""

from pathlib import Path

from google.adk.tools import ToolContext

# Resolve skills/ directory relative to this file's location
_SKILLS_DIR = Path(__file__).parent.parent / "skills"

SUPPORTED_FRAMEWORKS = {"react", "vue", "angular", "svelte"}

# Map framework name → skills file stem (without .skills.md extension)
# "react" maps to react-standalone.skills.md (pure Tailwind, no shadcn/cn/cva)
_FRAMEWORK_TO_FILE: dict[str, str] = {
    "react": "react-standalone",
    "vue": "vue",
    "angular": "angular",
    "svelte": "svelte",
}


def read_skills_file(framework: str, tool_context: ToolContext) -> dict:
    """
    Opens skills/{framework}.skills.md and writes its content directly
    to state["framework_skills"].

    Args:
        framework: One of 'react', 'vue', 'angular', 'svelte'.
        tool_context: ADK ToolContext providing state access.

    Returns:
        {"status": "ok", "message": "..."} on success.
        {"status": "error", "message": "..."} on failure.
    """
    framework = framework.lower().strip()

    if framework not in SUPPORTED_FRAMEWORKS:
        msg = (
            f"Unsupported framework '{framework}'. "
            f"Supported: {sorted(SUPPORTED_FRAMEWORKS)}"
        )
        return {"status": "error", "message": msg}

    skills_path = _SKILLS_DIR / f"{_FRAMEWORK_TO_FILE[framework]}.skills.md"

    if not skills_path.exists():
        msg = f"Skills file not found: {skills_path}"
        return {"status": "error", "message": msg}

    content = skills_path.read_text(encoding="utf-8")

    # Write directly to session state — this bypasses output_key
    tool_context.state["framework_skills"] = content

    return {
        "status": "ok",
        "message": (
            f"Loaded {_FRAMEWORK_TO_FILE[framework]}.skills.md ({len(content)} chars) "
            f"into state['framework_skills']."
        ),
    }
