"""
Integration tests for the FlowBridge.ai pipeline.

These tests verify agent wiring, configuration, and pipeline structure
WITHOUT making real API calls.

Run with: pytest tests/test_pipeline.py -v
"""

import pytest

from pipeline._config import GEMINI_MODEL
from pipeline.orchestrator import orchestrator
from pipeline.figma_parser_agent import figma_normalizer_agent
from pipeline.token_extractor_agent import token_extractor_agent
from pipeline.design_analyzer_agent import design_analyzer_agent
from pipeline.skills_loader_agent import skills_loader_agent
from pipeline.code_generator_agent import code_generator_agent
from pipeline.code_reviewer_agent import code_reviewer_agent


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class TestConfig:
    def test_gemini_model_is_set(self):
        assert GEMINI_MODEL == "gemini-2.5-pro"

    def test_model_is_not_empty(self):
        assert GEMINI_MODEL.strip() != ""


# ---------------------------------------------------------------------------
# A1 — FigmaNormalizerAgent
# ---------------------------------------------------------------------------

class TestFigmaNormalizerAgent:
    def test_name(self):
        assert figma_normalizer_agent.name == "FigmaNormalizerAgent"

    def test_output_key(self):
        assert figma_normalizer_agent.output_key == "normalization_confirmation"

    def test_has_normalize_tool(self):
        tool_names = [t.__name__ for t in figma_normalizer_agent.tools]
        assert "normalize_figma_node" in tool_names

    def test_model(self):
        assert figma_normalizer_agent.model == GEMINI_MODEL

    def test_instruction_mentions_tool(self):
        assert "normalize_figma_node" in figma_normalizer_agent.instruction

    def test_instruction_mentions_normalized_figma_state_key(self):
        assert "normalized_figma" in figma_normalizer_agent.instruction

    def test_instruction_mentions_component_name(self):
        assert "component_name" in figma_normalizer_agent.instruction


# ---------------------------------------------------------------------------
# A2 — TokenExtractorAgent
# ---------------------------------------------------------------------------

class TestTokenExtractorAgent:
    def test_name(self):
        assert token_extractor_agent.name == "TokenExtractorAgent"

    def test_output_key(self):
        assert token_extractor_agent.output_key == "token_extraction_confirmation"

    def test_has_extract_tool(self):
        tool_names = [t.__name__ for t in token_extractor_agent.tools]
        assert "extract_design_tokens" in tool_names

    def test_model(self):
        assert token_extractor_agent.model == GEMINI_MODEL

    def test_instruction_mentions_tool(self):
        assert "extract_design_tokens" in token_extractor_agent.instruction

    def test_instruction_mentions_design_tokens_state_key(self):
        assert "design_tokens" in token_extractor_agent.instruction


# ---------------------------------------------------------------------------
# A3 — DesignAnalyzerAgent
# ---------------------------------------------------------------------------

class TestDesignAnalyzerAgent:
    def test_name(self):
        assert design_analyzer_agent.name == "DesignAnalyzerAgent"

    def test_output_key(self):
        assert design_analyzer_agent.output_key == "component_blueprint"

    def test_no_tools(self):
        assert not design_analyzer_agent.tools

    def test_model(self):
        assert design_analyzer_agent.model == GEMINI_MODEL

    def test_instruction_mentions_states(self):
        instr = design_analyzer_agent.instruction.lower()
        assert "hover" in instr
        assert "disabled" in instr
        assert "loading" in instr

    def test_instruction_mentions_accessibility(self):
        instr = design_analyzer_agent.instruction.lower()
        assert "aria" in instr or "accessibility" in instr

    def test_instruction_reads_design_tokens(self):
        assert "design_tokens" in design_analyzer_agent.instruction

    def test_instruction_reads_normalized_figma(self):
        assert "normalized_figma" in design_analyzer_agent.instruction

    def test_instruction_enforces_token_id_references(self):
        # Blueprint must reference token IDs, not raw values
        assert "token" in design_analyzer_agent.instruction.lower()


# ---------------------------------------------------------------------------
# A4 — SkillsLoaderAgent
# ---------------------------------------------------------------------------

class TestSkillsLoaderAgent:
    def test_name(self):
        assert skills_loader_agent.name == "SkillsLoaderAgent"

    def test_output_key(self):
        assert skills_loader_agent.output_key == "skills_load_confirmation"

    def test_has_read_skills_tool(self):
        tool_names = [t.__name__ for t in skills_loader_agent.tools]
        assert "read_skills_file" in tool_names

    def test_model(self):
        assert skills_loader_agent.model == GEMINI_MODEL

    def test_instruction_mentions_framework_skills(self):
        assert "framework_skills" in skills_loader_agent.instruction


# ---------------------------------------------------------------------------
# A5 — CodeGeneratorAgent
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

    def test_instruction_requires_all_states(self):
        instr = code_generator_agent.instruction.lower()
        for state in ["hover", "focus", "active", "disabled", "loading"]:
            assert state in instr, f"State '{state}' not mentioned in CodeGeneratorAgent instruction"

    def test_instruction_prohibits_markdown_fences(self):
        assert "markdown" in code_generator_agent.instruction.lower() or \
               "```" in code_generator_agent.instruction

    def test_instruction_enforces_pixel_fidelity(self):
        # Must call out exact hex and px usage
        instr = code_generator_agent.instruction
        assert "[#" in instr or "arbitrary" in instr.lower()

    def test_instruction_reads_design_tokens(self):
        assert "design_tokens" in code_generator_agent.instruction

    def test_instruction_reads_component_name(self):
        assert "component_name" in code_generator_agent.instruction

    def test_instruction_prohibits_cn_cva(self):
        instr = code_generator_agent.instruction.lower()
        assert "cn(" in instr or "cva" in instr  # mentioned as forbidden


# ---------------------------------------------------------------------------
# A6 — FidelityGateAgent (code_reviewer_agent)
# ---------------------------------------------------------------------------

class TestFidelityGateAgent:
    def test_name(self):
        assert code_reviewer_agent.name == "FidelityGateAgent"

    def test_output_key(self):
        assert code_reviewer_agent.output_key == "final_code"

    def test_no_tools(self):
        assert not code_reviewer_agent.tools

    def test_model(self):
        assert code_reviewer_agent.model == GEMINI_MODEL

    def test_instruction_has_fidelity_checklist(self):
        instr = code_reviewer_agent.instruction.lower()
        assert "fidelity" in instr or "checklist" in instr

    def test_instruction_mentions_aria(self):
        assert "aria" in code_reviewer_agent.instruction.lower()

    def test_instruction_reads_design_tokens(self):
        assert "design_tokens" in code_reviewer_agent.instruction

    def test_instruction_reads_generated_code(self):
        assert "generated_code" in code_reviewer_agent.instruction

    def test_instruction_enforces_hex_colors(self):
        assert "#" in code_reviewer_agent.instruction


# ---------------------------------------------------------------------------
# Orchestrator (SequentialAgent wiring)
# ---------------------------------------------------------------------------

class TestOrchestrator:
    def test_name(self):
        assert orchestrator.name == "FlowBridgeOrchestrator"

    def test_has_six_sub_agents(self):
        assert len(orchestrator.sub_agents) == 6

    def test_sub_agent_order(self):
        names = [a.name for a in orchestrator.sub_agents]
        assert names == [
            "FigmaNormalizerAgent",
            "TokenExtractorAgent",
            "DesignAnalyzerAgent",
            "SkillsLoaderAgent",
            "CodeGeneratorAgent",
            "FidelityGateAgent",
        ]

    def test_all_sub_agents_have_output_keys(self):
        for agent in orchestrator.sub_agents:
            assert agent.output_key, f"{agent.name} is missing output_key"

    def test_sub_agents_use_gemini_model(self):
        for agent in orchestrator.sub_agents:
            assert agent.model == GEMINI_MODEL, (
                f"{agent.name} uses model '{agent.model}', expected '{GEMINI_MODEL}'"
            )

    def test_data_flow_keys(self):
        """
        Verify that output keys form a valid data flow:
        each agent's output_key should exist as a readable key
        in subsequent agents' instructions.
        """
        # A1 FigmaNormalizerAgent → normalized_figma (written directly to state by tool)
        assert "normalized_figma" in token_extractor_agent.instruction
        assert "normalized_figma" in design_analyzer_agent.instruction

        # A2 TokenExtractorAgent → design_tokens (written directly to state by tool)
        assert "design_tokens" in design_analyzer_agent.instruction
        assert "design_tokens" in code_generator_agent.instruction
        assert "design_tokens" in code_reviewer_agent.instruction

        # A3 DesignAnalyzerAgent → component_blueprint
        assert "component_blueprint" in code_generator_agent.instruction
        assert "component_blueprint" in code_reviewer_agent.instruction

        # A4 SkillsLoaderAgent → framework_skills (written directly to state by tool)
        assert "framework_skills" in code_generator_agent.instruction

        # A5 CodeGeneratorAgent → generated_code
        assert "generated_code" in code_reviewer_agent.instruction


# ---------------------------------------------------------------------------
# Import smoke tests
# ---------------------------------------------------------------------------

class TestImports:
    def test_tools_importable(self):
        from tools.figma_tools import normalize_figma_node, extract_design_tokens
        from tools.skills_tools import read_skills_file
        assert callable(normalize_figma_node)
        assert callable(extract_design_tokens)
        assert callable(read_skills_file)

    def test_pipeline_importable(self):
        from pipeline import orchestrator as orch
        assert orch is not None

    def test_agent_module_exports_root_agent(self):
        import agent as agent_module
        assert hasattr(agent_module, "root_agent")
        assert agent_module.root_agent is orchestrator
