"""
SkillsLoaderAgent — Step 4 of the FlowBridge.ai pipeline.

Reads the target `framework` from state, calls read_skills_file tool
which writes the .skills.md content directly to state["framework_skills"].

For the "react" framework, reads react-standalone.skills.md which uses
pure Tailwind CSS with arbitrary values — no cn(), no cva, no shadcn/ui
dependencies that require a separate project setup.
"""

from google.adk.agents import LlmAgent

from pipeline._config import GEMINI_MODEL
from tools.skills_tools import read_skills_file

SKILLS_LOADER_INSTRUCTION = """
You are the framework skills loader agent for the FlowBridge.ai pipeline.

Steps:
1. Read the `framework` value from session state (e.g. "react", "vue").
2. Call `read_skills_file` with that framework name as the `framework` argument.
   The tool will write the .skills.md content into state["framework_skills"].
3. After the tool returns successfully, output a brief confirmation in this format:

Loaded: <framework>.skills.md
Key conventions:
1. <first key convention from the skills file>
2. <second key convention>
3. <third key convention>

If the tool returns an error, output:
ERROR: <error message from tool>
"""

skills_loader_agent = LlmAgent(
    name="SkillsLoaderAgent",
    model=GEMINI_MODEL,
    instruction=SKILLS_LOADER_INSTRUCTION,
    tools=[read_skills_file],
    output_key="skills_load_confirmation",
)
