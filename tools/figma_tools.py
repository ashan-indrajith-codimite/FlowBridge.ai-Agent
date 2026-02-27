"""
Figma Tools — deterministic JSON normalization for the FlowBridge.ai pipeline.

Two public tools:
  - normalize_figma_node : validate + normalize raw JSON; write normalized_figma to state.
  - extract_design_tokens: walk normalized_figma and extract exact design tokens to state.
"""

import json
import math
import re
from typing import Any

from google.adk.tools import ToolContext

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _rgb01_to_255(r: float, g: float, b: float) -> tuple[int, int, int]:
    """Convert 0-1 floats to 0-255 ints."""
    return (round(r * 255), round(g * 255), round(b * 255))


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def _normalize_color(color: dict) -> dict:
    """
    Accepts either:
      - { "r": 0.58, "g": 0.28, "b": 0.69 }          (0-1 floats)
      - "#RRGGBB" strings (passed through)
    Returns: { "r255": int, "g255": int, "b255": int, "hex": "#RRGGBB", "rgb_css": "rgb(R,G,B)" }
    """
    r255, g255, b255 = _rgb01_to_255(color["r"], color["g"], color["b"])
    a = color.get("a", 1.0)
    hex_val = _rgb_to_hex(r255, g255, b255)
    return {
        "r255": r255,
        "g255": g255,
        "b255": b255,
        "a": round(a, 3),
        "hex": hex_val,
        "rgb_css": f"rgb({r255},{g255},{b255})",
    }


def _normalize_node(node: dict) -> dict:
    """Recursively normalize a Figma node dict."""
    out: dict[str, Any] = {}

    for key, val in node.items():
        if key == "style" and isinstance(val, dict):
            style_out: dict[str, Any] = {}
            for sk, sv in val.items():
                if sk in ("bg", "text_color", "border", "color") and isinstance(sv, dict) and "r" in sv:
                    style_out[sk] = _normalize_color(sv)
                elif sk in ("bg", "text_color", "border", "color") and isinstance(sv, str) and sv.startswith("#"):
                    # Any color key can be a plain hex string from Figma
                    sv_clean = sv.lstrip("#")
                    r = int(sv_clean[0:2], 16)
                    g = int(sv_clean[2:4], 16)
                    b = int(sv_clean[4:6], 16)
                    style_out[sk] = {
                        "r255": r, "g255": g, "b255": b, "a": 1.0,
                        "hex": f"#{sv_clean.upper()}",
                        "rgb_css": f"rgb({r},{g},{b})",
                    }
                elif sk == "shadow" and isinstance(sv, dict):
                    style_out[sk] = {
                        "offset_x": sv.get("offset", [0, 0])[0],
                        "offset_y": sv.get("offset", [0, 0])[1],
                        "blur": sv.get("blur", 0),
                        "opacity": sv.get("opacity", 0),
                    }
                elif sk == "padding" and isinstance(sv, list):
                    # [vertical, horizontal] → explicit fields
                    v = sv[0] if len(sv) > 0 else 0
                    h = sv[1] if len(sv) > 1 else v
                    style_out[sk] = {"vertical": v, "horizontal": h}
                elif sk == "radius":
                    style_out[sk] = sv  # keep as number
                else:
                    style_out[sk] = sv
            out["style"] = style_out

        elif key == "text_elements" and isinstance(val, list):
            out["text_elements"] = [_normalize_node(te) for te in val]

        elif key == "children" and isinstance(val, list):
            out["children"] = [_normalize_node(child) for child in val]

        elif key == "layout" and isinstance(val, dict):
            out["layout"] = val  # keep all layout values verbatim

        elif key in ("color",) and isinstance(val, dict) and "r" in val:
            out[key] = _normalize_color(val)

        else:
            # Pass through: strings, numbers, booleans, ids
            out[key] = val

    return out


def _to_pascal_case(name: str) -> str:
    """'Login Screen Container' → 'LoginScreenContainer'"""
    words = re.split(r"[\s_\-]+", name)
    return "".join(w.capitalize() for w in words if w)


# ──────────────────────────────────────────────────────────────────────────────
# Token extraction helpers
# ──────────────────────────────────────────────────────────────────────────────

def _collect_tokens(node: dict, tokens: dict) -> None:
    """Walk normalized node tree, collecting unique design tokens."""
    colors = tokens.setdefault("colors", {})
    spacing = tokens.setdefault("spacing", {})
    fonts = tokens.setdefault("fonts", {})
    radii = tokens.setdefault("radii", {})
    shadows = tokens.setdefault("shadows", {})
    borders = tokens.setdefault("borders", {})

    style = node.get("style", {})

    # Colors from style.bg / style.text_color / style.border
    for color_key in ("bg", "text_color", "border"):
        c = style.get(color_key)
        if isinstance(c, dict) and "hex" in c:
            token_id = f"color-{c['hex'].lstrip('#')}"
            colors[token_id] = {
                "hex": c["hex"],
                "rgb_css": c.get("rgb_css", ""),
                "tailwind_arbitrary": f"[{c['hex']}]",
            }

    # Colors from text elements
    for te in node.get("text_elements", []):
        c = te.get("color") or (te.get("style") or {}).get("color")
        if isinstance(c, dict) and "hex" in c:
            token_id = f"color-{c['hex'].lstrip('#')}"
            colors[token_id] = {
                "hex": c["hex"],
                "rgb_css": c.get("rgb_css", ""),
                "tailwind_arbitrary": f"[{c['hex']}]",
            }

    # Direct text node color (normalized from 0-1)
    node_color = node.get("color")
    if isinstance(node_color, dict) and "hex" in node_color:
        token_id = f"color-{node_color['hex'].lstrip('#')}"
        colors[token_id] = {
            "hex": node_color["hex"],
            "rgb_css": node_color.get("rgb_css", ""),
            "tailwind_arbitrary": f"[{node_color['hex']}]",
        }

    # Spacing from layout
    layout = node.get("layout", {})
    sp = layout.get("spacing")
    if sp is not None:
        token_id = f"spacing-{sp}".replace(".", "_")
        spacing[token_id] = {"px": sp, "tailwind_arbitrary": f"[{sp}px]"}

    w = layout.get("width")
    if w is not None:
        token_id = f"width-{w}"
        spacing[token_id] = {"px": w, "tailwind_arbitrary": f"[{w}px]"}

    # Spacing from style.padding
    pad = style.get("padding")
    if isinstance(pad, dict):
        for axis, val in pad.items():
            token_id = f"padding-{axis}-{val}".replace(".", "_")
            spacing[token_id] = {"px": val, "tailwind_arbitrary": f"[{val}px]"}

    # Radius
    r = style.get("radius")
    if r is not None:
        token_id = f"radius-{r}".replace(".", "_")
        radii[token_id] = {"px": r, "tailwind_arbitrary": f"[{r}px]"}

    # Shadow
    shadow = style.get("shadow")
    if isinstance(shadow, dict):
        ox = shadow["offset_x"]
        oy = shadow["offset_y"]
        bl = shadow["blur"]
        op = shadow["opacity"]
        token_id = f"shadow-{ox}-{oy}-{bl}"
        shadows[token_id] = {
            "css": f"{ox}px {oy}px {bl}px rgba(0,0,0,{op})",
            "tailwind_arbitrary": f"[{ox}px_{oy}px_{bl}px_rgba(0,0,0,{op})]",
        }

    # Fonts from text_elements
    for te in node.get("text_elements", []):
        font = te.get("font")
        size = te.get("size")
        weight = te.get("weight")
        if font:
            if font not in fonts:
                fonts[font] = []
            entry = {}
            if size is not None:
                entry["size_px"] = size
                entry["tailwind_size"] = f"[{size}px]"
            if weight is not None:
                entry["weight"] = weight
                entry["tailwind_weight"] = f"[{weight}]"
            if entry:
                fonts[font].append(entry)

    # Fonts from direct style (header text nodes)
    node_style = node.get("style", {})
    font = node_style.get("font")
    size = node_style.get("size")
    weight = node_style.get("weight")
    if font:
        if font not in fonts:
            fonts[font] = []
        entry = {}
        if size is not None:
            entry["size_px"] = size
            entry["tailwind_size"] = f"[{size}px]"
        if weight is not None:
            entry["weight"] = weight
            entry["tailwind_weight"] = f"[{weight}]"
        if entry:
            fonts[font].append(entry)

    # Recurse into children
    for child in node.get("children", []):
        _collect_tokens(child, tokens)


# ──────────────────────────────────────────────────────────────────────────────
# Public ADK tools
# ──────────────────────────────────────────────────────────────────────────────

def normalize_figma_node(tool_context: ToolContext) -> dict:
    """
    Reads figma_node_json from session state.
    Normalizes it deterministically — preserving EXACT numeric values, converting
    all 0-1 RGB colors to hex + rgb_css, expanding padding arrays, normalizing
    shadows — then writes the result to state['normalized_figma'].

    Also derives component_name and output_file_name from the root node name.

    Returns: {"status": "ok", "component_name": str, "root_dimensions": {...}}
             or {"status": "error", "message": str}
    """
    raw_json: str = tool_context.state.get("figma_node_json", "")

    if not raw_json:
        return {"status": "error", "message": "figma_node_json not found in session state"}

    try:
        data: dict = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return {"status": "error", "message": f"Invalid JSON: {exc}"}

    # Normalize the full tree — operate on ui_root directly so all node
    # keys (style.bg, style.border, etc.) are recursed correctly.
    ui_root_raw = data.get("ui_root", data)  # support both {ui_root:{...}} and bare node
    normalized_root = _normalize_node(ui_root_raw)
    # Re-wrap to preserve the {"ui_root": ...} envelope that downstream reads
    normalized = {"ui_root": normalized_root}
    # Copy any top-level keys other than ui_root (if present)
    for k, v in data.items():
        if k != "ui_root":
            normalized[k] = v
    tool_context.state["normalized_figma"] = normalized

    # Derive component name from root node
    root = normalized.get("ui_root", {})
    raw_name = root.get("name", "Component")
    component_name = _to_pascal_case(raw_name)
    tool_context.state["component_name"] = component_name

    # Root dimensions for preview viewport sizing
    root_layout = root.get("layout", {})
    root_dimensions = {
        "width": root_layout.get("width", 400),
        "height": root_layout.get("height", 600),
    }
    tool_context.state["root_dimensions"] = root_dimensions

    return {
        "status": "ok",
        "component_name": component_name,
        "root_dimensions": root_dimensions,
        "message": (
            f"Normalized Figma JSON for component '{component_name}'. "
            f"Root dimensions: {root_dimensions['width']}×{root_dimensions['height']}px. "
            f"All RGB colors converted to hex. All numeric values preserved exactly."
        ),
    }


def extract_design_tokens(tool_context: ToolContext) -> dict:
    """
    Reads normalized_figma from session state, walks the entire node tree,
    and extracts every unique design token (colors, spacing, fonts, radii,
    shadows) with their exact pixel/hex values and Tailwind arbitrary-value
    equivalents.

    Writes result to state['design_tokens'].

    Returns: {"status": "ok", "token_summary": {...}} or {"status": "error", ...}
    """
    normalized = tool_context.state.get("normalized_figma")

    if not normalized:
        return {
            "status": "error",
            "message": "normalized_figma not found in state. Run normalize_figma_node first.",
        }

    tokens: dict = {}
    root = normalized.get("ui_root", normalized)
    _collect_tokens(root, tokens)

    tool_context.state["design_tokens"] = tokens

    summary = {
        "colors": len(tokens.get("colors", {})),
        "spacing_values": len(tokens.get("spacing", {})),
        "font_families": len(tokens.get("fonts", {})),
        "radii": len(tokens.get("radii", {})),
        "shadows": len(tokens.get("shadows", {})),
    }

    return {
        "status": "ok",
        "token_summary": summary,
        "message": (
            f"Extracted {summary['colors']} colors, "
            f"{summary['spacing_values']} spacing values, "
            f"{summary['font_families']} font families, "
            f"{summary['radii']} radii, "
            f"{summary['shadows']} shadows."
        ),
    }
