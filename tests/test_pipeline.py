"""
Tests for the FlowBridge.ai pipeline.

Run with: pytest tests/test_pipeline.py -v
"""

import json

from pipeline._config import GEMINI_MODEL
from pipeline.orchestrator import orchestrator
from pipeline.code_generator_agent import code_generator_agent


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class TestConfig:
    def test_gemini_model_is_set(self):
        assert GEMINI_MODEL == "gemini-2.5-pro"

    def test_model_is_not_empty(self):
        assert GEMINI_MODEL.strip() != ""


# ---------------------------------------------------------------------------
# CodeGeneratorAgent
# ---------------------------------------------------------------------------

class TestCodeGeneratorAgent:
    def test_name(self):
        assert code_generator_agent.name == "CodeGeneratorAgent"

    def test_output_key(self):
        assert code_generator_agent.output_key == "generated_code"

    def test_no_tools(self):
        assert not code_generator_agent.tools

    def test_model(self):
        assert code_generator_agent.model == GEMINI_MODEL

    def test_instruction_reads_figma_node_json(self):
        assert "figma_node_json" in code_generator_agent.instruction

    def test_instruction_reads_framework(self):
        assert "framework" in code_generator_agent.instruction

    def test_instruction_reads_styling(self):
        assert "styling" in code_generator_agent.instruction

    def test_instruction_reads_special_notes(self):
        assert "special_notes" in code_generator_agent.instruction

    def test_instruction_reads_component_name(self):
        assert "component_name" in code_generator_agent.instruction

    def test_instruction_enforces_pixel_fidelity(self):
        instr = code_generator_agent.instruction
        assert "[#" in instr or "arbitrary" in instr.lower()

    def test_instruction_requires_interactive_states(self):
        instr = code_generator_agent.instruction.lower()
        for state in ["hover", "focus", "active", "disabled", "loading"]:
            assert state in instr, f"'{state}' not in instruction"

    def test_instruction_mentions_accessibility(self):
        assert "aria" in code_generator_agent.instruction.lower()

    def test_instruction_prohibits_markdown_fences(self):
        assert "```" in code_generator_agent.instruction or \
               "markdown" in code_generator_agent.instruction.lower()

    def test_instruction_covers_tailwind_and_inline_css(self):
        instr = code_generator_agent.instruction.lower()
        assert "tailwind" in instr
        assert "inline" in instr


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class TestOrchestrator:
    def test_name(self):
        assert orchestrator.name == "FlowBridgeOrchestrator"

    def test_has_one_sub_agent(self):
        assert len(orchestrator.sub_agents) == 1

    def test_sub_agent_is_code_generator(self):
        assert orchestrator.sub_agents[0].name == "CodeGeneratorAgent"

    def test_sub_agent_has_output_key(self):
        assert orchestrator.sub_agents[0].output_key == "generated_code"

    def test_sub_agent_uses_gemini_model(self):
        assert orchestrator.sub_agents[0].model == GEMINI_MODEL


# ---------------------------------------------------------------------------
# component_name derivation (pure Python in run_pipeline)
# ---------------------------------------------------------------------------

class TestComponentNameDerivation:
    def _derive(self, name: str) -> str:
        import re
        return "".join(w.capitalize() for w in re.split(r"[\s_\-]+", name) if w)

    def test_simple_name(self):
        assert self._derive("Button") == "Button"

    def test_spaced_name(self):
        assert self._derive("Login Screen") == "LoginScreen"

    def test_multi_word(self):
        assert self._derive("login screen container") == "LoginScreenContainer"

    def test_hyphen_underscore(self):
        assert self._derive("my-cool_component") == "MyCoolComponent"


# ---------------------------------------------------------------------------
# Import smoke tests
# ---------------------------------------------------------------------------

class TestImports:
    def test_pipeline_importable(self):
        from pipeline import orchestrator as orch
        assert orch is not None

    def test_agent_module_exports_root_agent(self):
        import agent as agent_module
        assert hasattr(agent_module, "root_agent")
        assert agent_module.root_agent is orchestrator
