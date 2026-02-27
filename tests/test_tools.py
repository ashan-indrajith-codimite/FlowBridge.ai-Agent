"""
Unit tests for tools/figma_tools.py and tools/skills_tools.py.

Run with: pytest tests/test_tools.py -v
"""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tools.figma_tools import normalize_figma_node, extract_design_tokens
from tools.skills_tools import read_skills_file


# ---------------------------------------------------------------------------
# normalize_figma_node
# ---------------------------------------------------------------------------

class TestNormalizeFigmaNode:
    def _make_ctx(self, json_str: str) -> MagicMock:
        ctx = MagicMock()
        ctx.state = {"figma_node_json": json_str}
        return ctx

    def test_normalizes_sample_json(self):
        sample = Path("sample_data/button_node.json").read_text(encoding="utf-8")
        ctx = self._make_ctx(sample)
        result = normalize_figma_node(ctx)

        assert result["status"] == "ok"
        assert "component_name" in result
        assert "root_dimensions" in result

    def test_writes_normalized_figma_to_state(self):
        sample = Path("sample_data/button_node.json").read_text(encoding="utf-8")
        ctx = self._make_ctx(sample)
        normalize_figma_node(ctx)

        assert "normalized_figma" in ctx.state
        assert isinstance(ctx.state["normalized_figma"], dict)

    def test_writes_component_name_to_state(self):
        sample = Path("sample_data/button_node.json").read_text(encoding="utf-8")
        ctx = self._make_ctx(sample)
        normalize_figma_node(ctx)

        assert "component_name" in ctx.state
        # Must be PascalCase (no spaces)
        name = ctx.state["component_name"]
        assert " " not in name
        assert name[0].isupper()

    def test_writes_root_dimensions_to_state(self):
        sample = Path("sample_data/button_node.json").read_text(encoding="utf-8")
        ctx = self._make_ctx(sample)
        normalize_figma_node(ctx)

        dims = ctx.state.get("root_dimensions", {})
        assert "width" in dims
        assert "height" in dims
        assert isinstance(dims["width"], (int, float))
        assert isinstance(dims["height"], (int, float))

    def test_converts_rgb01_to_hex(self):
        """Colors expressed as 0-1 floats must become hex strings."""
        payload = json.dumps({
            "ui_root": {
                "name": "TestCard",
                "style": {
                    "bg": {"r": 0.58, "g": 0.278, "b": 0.69}
                },
                "children": [],
            }
        })
        ctx = self._make_ctx(payload)
        normalize_figma_node(ctx)

        norm = ctx.state["normalized_figma"]["ui_root"]
        bg = norm["style"]["bg"]
        assert "hex" in bg
        assert bg["hex"].startswith("#")
        assert len(bg["hex"]) == 7
        assert "rgb_css" in bg

    def test_pascal_case_component_name(self):
        """Root node name 'login screen container' → 'LoginScreenContainer'."""
        payload = json.dumps({
            "ui_root": {"name": "login screen container", "children": []}
        })
        ctx = self._make_ctx(payload)
        normalize_figma_node(ctx)
        assert ctx.state["component_name"] == "LoginScreenContainer"

    def test_exact_numbers_preserved(self):
        """Numeric spacing/size values must pass through unchanged."""
        payload = json.dumps({
            "ui_root": {
                "name": "Card",
                "layout": {"width": 300, "height": 359, "spacing": 32},
                "children": [],
            }
        })
        ctx = self._make_ctx(payload)
        normalize_figma_node(ctx)

        root = ctx.state["normalized_figma"]["ui_root"]
        assert root["layout"]["width"] == 300
        assert root["layout"]["height"] == 359
        assert root["layout"]["spacing"] == 32

    def test_error_on_empty_state(self):
        ctx = MagicMock()
        ctx.state = {}
        result = normalize_figma_node(ctx)
        assert result["status"] == "error"

    def test_error_on_invalid_json(self):
        ctx = self._make_ctx("{ not valid json }")
        result = normalize_figma_node(ctx)
        assert result["status"] == "error"

    def test_preserves_nested_children(self):
        sample = Path("sample_data/button_node.json").read_text(encoding="utf-8")
        ctx = self._make_ctx(sample)
        normalize_figma_node(ctx)

        root = ctx.state["normalized_figma"].get("ui_root", {})
        assert "children" in root
        assert isinstance(root["children"], list)
        assert len(root["children"]) > 0


# ---------------------------------------------------------------------------
# extract_design_tokens
# ---------------------------------------------------------------------------

class TestExtractDesignTokens:
    def _make_ctx_with_normalized(self) -> MagicMock:
        """Run normalize first, return context ready for extract_design_tokens."""
        sample = Path("sample_data/button_node.json").read_text(encoding="utf-8")
        ctx = MagicMock()
        ctx.state = {"figma_node_json": sample}
        normalize_figma_node(ctx)
        return ctx

    def test_extract_succeeds_after_normalize(self):
        ctx = self._make_ctx_with_normalized()
        result = extract_design_tokens(ctx)
        assert result["status"] == "ok"

    def test_writes_design_tokens_to_state(self):
        ctx = self._make_ctx_with_normalized()
        extract_design_tokens(ctx)
        assert "design_tokens" in ctx.state
        assert isinstance(ctx.state["design_tokens"], dict)

    def test_design_tokens_has_required_sections(self):
        ctx = self._make_ctx_with_normalized()
        extract_design_tokens(ctx)
        tokens = ctx.state["design_tokens"]
        # All expected sections must be present
        for section in ("colors", "spacing", "fonts", "radii", "shadows"):
            assert section in tokens, f"Missing section: {section}"

    def test_colors_contain_hex_and_tailwind(self):
        ctx = self._make_ctx_with_normalized()
        extract_design_tokens(ctx)
        colors = ctx.state["design_tokens"].get("colors", {})
        assert len(colors) > 0
        for token_id, token in colors.items():
            assert "hex" in token, f"{token_id} missing hex"
            assert "tailwind_arbitrary" in token, f"{token_id} missing tailwind_arbitrary"
            assert token["hex"].startswith("#")

    def test_spacing_contains_px_and_tailwind(self):
        ctx = self._make_ctx_with_normalized()
        extract_design_tokens(ctx)
        spacing = ctx.state["design_tokens"].get("spacing", {})
        assert len(spacing) > 0
        for token_id, token in spacing.items():
            assert "px" in token, f"{token_id} missing px"
            assert "tailwind_arbitrary" in token, f"{token_id} missing tailwind_arbitrary"

    def test_token_summary_in_return(self):
        ctx = self._make_ctx_with_normalized()
        result = extract_design_tokens(ctx)
        assert "token_summary" in result
        summary = result["token_summary"]
        for key in ("colors", "spacing_values", "font_families", "radii", "shadows"):
            assert key in summary

    def test_error_without_normalized_figma(self):
        ctx = MagicMock()
        ctx.state = {}  # no normalized_figma
        result = extract_design_tokens(ctx)
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# read_skills_file
# ---------------------------------------------------------------------------

class TestReadSkillsFile:
    def _make_tool_context(self) -> MagicMock:
        ctx = MagicMock()
        ctx.state = {}
        return ctx

    def test_loads_react_skills(self):
        ctx = self._make_tool_context()
        result = read_skills_file("react", ctx)

        assert result["status"] == "ok"
        assert "framework_skills" in ctx.state
        assert len(ctx.state["framework_skills"]) > 100

    def test_react_loads_standalone_file(self):
        """react framework must load react-standalone.skills.md (pure Tailwind, no shadcn)."""
        ctx = self._make_tool_context()
        read_skills_file("react", ctx)
        content = ctx.state["framework_skills"]
        # react-standalone.skills.md should explicitly PROHIBIT cn() from @/lib/utils
        # (the file mentions it as a DON'T DO, not as an import)
        assert "standalone" in content.lower() or "STANDALONE" in content

    def test_loads_vue_skills(self):
        ctx = self._make_tool_context()
        result = read_skills_file("vue", ctx)
        assert result["status"] == "ok"
        assert "Vue" in ctx.state["framework_skills"]

    def test_loads_angular_skills(self):
        ctx = self._make_tool_context()
        result = read_skills_file("angular", ctx)
        assert result["status"] == "ok"
        assert "Angular" in ctx.state["framework_skills"]

    def test_loads_svelte_skills(self):
        ctx = self._make_tool_context()
        result = read_skills_file("svelte", ctx)
        assert result["status"] == "ok"
        assert "Svelte" in ctx.state["framework_skills"]

    def test_case_insensitive_framework(self):
        ctx = self._make_tool_context()
        result = read_skills_file("REACT", ctx)
        assert result["status"] == "ok"

    def test_unsupported_framework(self):
        ctx = self._make_tool_context()
        result = read_skills_file("flutter", ctx)
        assert result["status"] == "error"
        assert "flutter" in result["message"].lower() or "Unsupported" in result["message"]

    def test_writes_to_state(self):
        """Confirms the tool writes directly to state, bypassing output_key."""
        ctx = self._make_tool_context()
        read_skills_file("react", ctx)
        assert ctx.state.get("framework_skills") is not None
        assert isinstance(ctx.state["framework_skills"], str)


# ---------------------------------------------------------------------------
# Sample JSON file validity
# ---------------------------------------------------------------------------

class TestSampleData:
    def test_sample_json_is_valid(self):
        content = Path("sample_data/button_node.json").read_text(encoding="utf-8")
        data = json.loads(content)  # raises if invalid
        assert "ui_root" in data

    def test_sample_json_has_children(self):
        content = Path("sample_data/button_node.json").read_text(encoding="utf-8")
        data = json.loads(content)
        assert "children" in data["ui_root"]
        assert len(data["ui_root"]["children"]) > 0

    def test_sample_json_normalizes_cleanly(self):
        """Full round-trip: sample JSON → normalize → extract tokens."""
        ctx = MagicMock()
        ctx.state = {
            "figma_node_json": Path("sample_data/button_node.json").read_text(encoding="utf-8")
        }
        norm_result = normalize_figma_node(ctx)
        assert norm_result["status"] == "ok"

        token_result = extract_design_tokens(ctx)
        assert token_result["status"] == "ok"
        assert token_result["token_summary"]["colors"] >= 0
