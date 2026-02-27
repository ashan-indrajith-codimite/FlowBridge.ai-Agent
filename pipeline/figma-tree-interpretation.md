# Figma Node Tree Interpretation Guide (for AI Agents)

**Format version:** `flowbridge-cleaned-figma-tree-v2` (compact) / `flowbridge-cleaned-figma-tree-v1` (aggressive)
**Cleaning version:** `2.0.0`
**Last updated:** 2026-02-27

---

## Purpose

This document explains how to interpret the **heavily compressed** Figma node tree JSON format produced by FlowBridge.ai Designer Chrome Extension.

The JSON has been aggressively cleaned to minimize token usage while retaining all information necessary to accurately reconstruct the UI component in code (HTML, CSS, React, Vue, etc.).

There are two format versions:
- **v2 (compact)** — default, highest compression. See [Compact Format (v2)](#compact-format-v2) below.
- **v1 (aggressive)** — less compression, more verbose property names.

Check `_aiContext.format` to determine which version you are reading.

**Key optimizations applied (both versions):**
- Top-level metadata removed (`componentSets`, `components`, `editorType`, `linkAccess`)
- Empty arrays removed entirely (`effects: []`, `strokes: []`)
- Default property values removed (you must apply defaults when missing)
- Nested objects (Paint, Effect, TypeStyle) cleaned to remove redundant/metadata fields
- Design token bindings (`boundVariables`) removed

**Additional optimizations in v2 (compact):**
- Invisible nodes (`visible: false`) removed entirely (not present in tree)
- `absoluteBoundingBox` replaced with `w` / `h` (width/height as integers)
- Colors use array format: `[r, g, b]` or `[r, g, b, a]` (0-1 range)
- Layout properties compacted into a single `layout` object
- `constraints`, `blendMode`, `styles` (Figma ref IDs) dropped
- Text fill color merged into `style.color`; empty overrides removed
- Numbers rounded (dimensions: integer, spacing/fonts: 1 decimal, colors: 2 decimals)

---

## JSON Structure

```json
{
  "meta": {
    "fileName": "V1-Website",
    "lastModified": "2026-02-26T04:57:48Z",
    "cleanedAt": 1772183010058,
    "cleaningVersion": "1.0.0"
  },
  "nodes": {
    "<nodeId>": {
      "document": { ... }
    }
  },
  "_aiContext": {
    "format": "flowbridge-cleaned-figma-tree-v1",
    "defaults": { ... },
    "promptFile": "ai-prompts/figma-tree-interpretation.md"
  }
}
```

The actual node tree is at `.nodes["<nodeId>"].document`.

---

## CRITICAL: Default Values

**If a property is missing, you MUST use the default value from `_aiContext.defaults`.**

### Node-level defaults (apply if property is absent)

| Property | Default Value | Meaning |
|---|---|---|
| `visible` | `true` | Node is visible (not `display: none`) |
| `opacity` | `1` | Fully opaque |
| `locked` | `false` | Unlocked (not relevant for code gen) |
| `clipsContent` | `false` | Content is not clipped (`overflow: visible`) |
| `blendMode` | `"PASS_THROUGH"` (containers) or `"NORMAL"` (shapes) | Rendering blend mode |
| `layoutWrap` | `"NO_WRAP"` | Auto-layout does not wrap (`flex-wrap: nowrap`) |
| `layoutAlign` | `"INHERIT"` | Inherits alignment from parent |
| `layoutGrow` | `0` | Does not grow (`flex-grow: 0`) |
| `strokeAlign` | `"INSIDE"` | Border is inside the box |
| `itemReverseZIndex` | `false` | Normal stacking order |
| `strokesIncludedInLayout` | `false` | Strokes do not affect layout size (`box-sizing: content-box`) |

**Blend mode defaults by node type:**
- **Containers** (FRAME, GROUP, COMPONENT, COMPONENT_SET, INSTANCE, SECTION): `"PASS_THROUGH"`
- **Shapes** (RECTANGLE, TEXT, VECTOR, ELLIPSE, etc.): `"NORMAL"`

### Paint-level defaults (for items in `fills` or `strokes` arrays)

| Property | Default Value |
|---|---|
| `blendMode` | `"NORMAL"` |
| `opacity` | `1` |
| `visible` | `true` |

### Effect-level defaults (for items in `effects` array)

| Property | Default Value |
|---|---|
| `visible` | `true` |
| `blendMode` | `"NORMAL"` |

### Missing arrays (treat as empty)

If these properties are **completely absent** (not present as a key):
- Missing `fills` → `[]` (transparent background)
- Missing `strokes` → `[]` (no border)
- Missing `effects` → `[]` (no shadows/blurs)
- Missing `children` → `[]` (leaf node, no children)

---

## Node Types

| Type | Description | Typical HTML |
|---|---|---|
| `FRAME` | Container with layout (flexbox or grid) | `<div>` |
| `GROUP` | Simple grouping container | `<div>` |
| `TEXT` | Text content | `<p>`, `<span>`, `<h*>` |
| `RECTANGLE` | Box shape | `<div>` |
| `VECTOR` | SVG icon or shape | `<svg>` |
| `ELLIPSE` | Circle or ellipse | `<div>` with `border-radius: 50%` |
| `LINE` | Line shape | `<hr>` or `<div>` with border |
| `STAR`, `REGULAR_POLYGON` | Geometric shapes | `<svg>` |
| `BOOLEAN_OPERATION` | Combined shapes (union, subtract, etc.) | `<svg>` |
| `INSTANCE` | Instance of a reusable component | Render children or reference component |
| `COMPONENT` | Component definition | Template (usually not rendered directly) |
| `COMPONENT_SET` | Component variant set | Container of components |

---

## Layout System

### Positioning Mode

Determined by `layoutMode`:

| Value | Meaning | CSS Equivalent |
|---|---|---|
| `"NONE"` | Absolute positioning | `position: absolute` + use `absoluteBoundingBox` |
| `"HORIZONTAL"` | Flexbox row | `display: flex; flex-direction: row;` |
| `"VERTICAL"` | Flexbox column | `display: flex; flex-direction: column;` |
| `"GRID"` | CSS Grid | `display: grid;` |

### Auto-layout (Flexbox) Properties

| Figma Property | CSS Equivalent |
|---|---|
| `primaryAxisAlignItems` | `justify-content` (for primary axis) |
| `counterAxisAlignItems` | `align-items` (for cross axis) |
| `counterAxisAlignContent` | `align-content` (for wrapped tracks) |
| `itemSpacing` | `gap` |
| `paddingLeft`, `paddingRight`, `paddingTop`, `paddingBottom` | `padding-*` |
| `layoutSizingHorizontal: "FILL"` | Child: `flex-grow: 1; width: 100%` |
| `layoutSizingHorizontal: "HUG"` | Child: `width: fit-content` |
| `layoutSizingHorizontal: "FIXED"` | Child: `width: <absoluteBoundingBox.width>px` |
| `layoutSizingVertical: "FILL"` | Child: `flex-grow: 1; height: 100%` |
| `layoutSizingVertical: "HUG"` | Child: `height: fit-content` |
| `layoutSizingVertical: "FIXED"` | Child: `height: <absoluteBoundingBox.height>px` |

**Alignment values mapping:**

| Figma Value | CSS `justify-content` / `align-items` |
|---|---|
| `"MIN"` | `flex-start` |
| `"CENTER"` | `center` |
| `"MAX"` | `flex-end` |
| `"SPACE_BETWEEN"` | `space-between` |
| `"BASELINE"` | `baseline` (for `counterAxisAlignItems` only) |

### Grid Layout Properties

If `layoutMode === "GRID"`:

| Figma Property | CSS Equivalent |
|---|---|
| `gridColumnCount` | Number of columns |
| `gridRowCount` | Number of rows |
| `gridColumnGap` | `column-gap` |
| `gridRowGap` | `row-gap` |
| `gridColumnsSizing` | `grid-template-columns` (CSS string, use as-is) |
| `gridRowsSizing` | `grid-template-rows` (CSS string, use as-is) |

Grid child properties:
- `gridRowSpan`, `gridColumnSpan` → `grid-row: span N` / `grid-column: span N`
- `gridRowAnchorIndex`, `gridColumnAnchorIndex` → `grid-row-start`, `grid-column-start`
- `gridChildHorizontalAlign`, `gridChildVerticalAlign` → `justify-self`, `align-self`

### Constraints (for absolute positioning)

`constraints` defines how a node resizes when its parent resizes.

| Property | Value | Behavior |
|---|---|---|
| `horizontal` | `"LEFT"` | Pin to left edge |
|  | `"RIGHT"` | Pin to right edge |
|  | `"CENTER"` | Center horizontally |
|  | `"SCALE"` | Stretch proportionally |
|  | `"LEFT_RIGHT"` | Pin to both edges (stretch width) |
| `vertical` | `"TOP"` | Pin to top |
|  | `"BOTTOM"` | Pin to bottom |
|  | `"CENTER"` | Center vertically |
|  | `"SCALE"` | Stretch proportionally |
|  | `"TOP_BOTTOM"` | Pin to both edges (stretch height) |

---

## Visual Properties

### absoluteBoundingBox

Defines the node's position and size in absolute canvas coordinates:

```json
{
  "x": 100,
  "y": 50,
  "width": 200,
  "height": 100
}
```

Use for:
- Absolute positioning (`left: 100px; top: 50px`)
- Fixed sizing (`width: 200px; height: 100px`)

### fills (backgrounds)

Array of Paint objects. **If missing entirely, background is transparent.**

#### Paint types:

**SOLID:**
```json
{ "type": "SOLID", "color": { "r": 0.2, "g": 0.4, "b": 0.8, "a": 1 } }
```
→ CSS: `background: rgba(51, 102, 204, 1)`  
(multiply `r`, `g`, `b` by 255)

**GRADIENT_LINEAR:**
```json
{
  "type": "GRADIENT_LINEAR",
  "gradientHandlePositions": [
    { "x": 0.5, "y": 0 },
    { "x": 0.5, "y": 1 }
  ],
  "gradientStops": [
    { "color": { "r": 1, "g": 0, "b": 0, "a": 1 }, "position": 0 },
    { "color": { "r": 0, "g": 0, "b": 1, "a": 1 }, "position": 1 }
  ]
}
```
→ CSS: `background: linear-gradient(180deg, rgb(255,0,0) 0%, rgb(0,0,255) 100%)`  
(Use `gradientHandlePositions` to compute angle; `gradientStops` for color stops)

**IMAGE:**
```json
{
  "type": "IMAGE",
  "imageRef": "48f0559bbf8c24ee987f70a971f1221ec1f8f4cf",
  "scaleMode": "FILL"
}
```
→ Fetch image URL from Figma: `GET /v1/images/:fileKey?ids=<imageRef>`, then use as `background-image: url(...)`

**scaleMode values:**
- `"FILL"` → `background-size: cover`
- `"FIT"` → `background-size: contain`
- `"STRETCH"` → `background-size: 100% 100%`
- `"TILE"` → `background-repeat: repeat`

### strokes (borders)

Same structure as fills. Additional properties on the node:

| Property | CSS Equivalent |
|---|---|
| `strokeWeight` | `border-width` |
| `strokeAlign` | Border position: `"INSIDE"` (use `box-sizing: border-box`), `"CENTER"` (default), `"OUTSIDE"` (use box-shadow workaround) |
| `strokeDashes` | Array like `[5, 3]` → `border-style: dashed` |

### effects (shadows, blurs)

Array of Effect objects. **If missing entirely, no effects.**

**DROP_SHADOW:**
```json
{
  "type": "DROP_SHADOW",
  "radius": 10,
  "color": { "r": 0, "g": 0, "b": 0, "a": 0.25 },
  "offset": { "x": 0, "y": 4 },
  "spread": 0
}
```
→ CSS: `box-shadow: 0px 4px 10px 0px rgba(0,0,0,0.25)`

**INNER_SHADOW:**
Same as DROP_SHADOW but add `inset`:  
→ CSS: `box-shadow: inset 0px 4px 10px rgba(0,0,0,0.25)`

**LAYER_BLUR:**
```json
{ "type": "LAYER_BLUR", "radius": 5 }
```
→ CSS: `filter: blur(5px)`

**BACKGROUND_BLUR:**
```json
{ "type": "BACKGROUND_BLUR", "radius": 10 }
```
→ CSS: `backdrop-filter: blur(10px)`

### Corner Radius

| Property | CSS Equivalent |
|---|---|
| `cornerRadius` | `border-radius: 8px` (single value for all corners) |
| `rectangleCornerRadii` | Array `[TL, TR, BR, BL]` → `border-radius: 8px 4px 12px 0` |
| `cornerSmoothing` | iOS-style "squircle" (0 = circle, 0.6 = iOS icon). No direct CSS equivalent — approximate or ignore for web. |

### opacity

- Map directly to CSS `opacity` property
- Range: 0 (fully transparent) to 1 (fully opaque)

---

## Text Nodes

TEXT nodes contain:

| Property | Purpose |
|---|---|
| `characters` | The actual text content |
| `style` | Typography object (font, size, weight, line-height, etc.) |
| `characterStyleOverrides` | Array mapping character index → style override ID |
| `styleOverrideTable` | Map of override ID → TypeStyle (for per-character styling) |

### TypeStyle Object

```json
{
  "fontFamily": "Inter",
  "fontSize": 16,
  "fontWeight": 500,
  "lineHeightPx": 24,
  "lineHeightUnit": "PIXELS",
  "letterSpacing": 0,
  "textAlignHorizontal": "LEFT",
  "textAlignVertical": "TOP",
  "textCase": "ORIGINAL",
  "textAutoResize": "HEIGHT"
}
```

**CSS mapping:**

| Figma Property | CSS Equivalent |
|---|---|
| `fontFamily` | `font-family` |
| `fontSize` | `font-size: <value>px` |
| `fontWeight` | `font-weight` |
| `fontStyle` | `font-style: italic` (if "Italic") |
| `lineHeightPx` | `line-height: <value>px` |
| `letterSpacing` | `letter-spacing: <value>px` |
| `textAlignHorizontal` | `text-align: left` / `center` / `right` / `justified` |
| `textAlignVertical` | `vertical-align` or Flexbox `align-items` |
| `textCase` | `text-transform: uppercase` / `lowercase` / `capitalize` / `none` |
| `textDecoration` | `text-decoration: underline` / `line-through` |

**textCase values:**
- `"ORIGINAL"` → `text-transform: none`
- `"UPPER"` → `text-transform: uppercase`
- `"LOWER"` → `text-transform: lowercase`
- `"TITLE"` → `text-transform: capitalize`

### Character Style Overrides

If `characterStyleOverrides` is present, some characters have different styles.

Example:
```json
{
  "characters": "Hello World",
  "characterStyleOverrides": [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
  "styleOverrideTable": {
    "1": { "fontWeight": 700 }
  }
}
```

→ Characters 0-5 ("Hello ") use the base `style`, characters 6-10 ("World") use the override (bold).

Render as:
```html
Hello <strong>World</strong>
```

---

## Component Instances

`INSTANCE` nodes are instances of reusable components.

| Property | Meaning |
|---|---|
| `componentId` | ID of the component definition (e.g. `"2811:8702"`) |
| `componentProperties` | Property overrides (variant, exposed text, etc.) |
| `children` | Fully-resolved instance children (use these for rendering) |

**For code generation:**

You can either:
1. **Flatten:** Render the instance's `children` directly as if it were a regular container
2. **Component reference:** Generate `<Button variant="primary" text="Click me" />` if you have a component library

**ComponentProperties structure:**

```json
{
  "Variant": {
    "type": "VARIANT",
    "value": "Primary"
  },
  "Label": {
    "type": "TEXT",
    "value": "Click me"
  }
}
```

Use these values to parameterize the component if generating component references.

---

## Hierarchy and Recursion

The tree is **recursive**. Every node can have `children` (an array of nodes).

**Traversal pattern:**

```js
function renderNode(node) {
  // 1. Check visibility
  if (node.visible === false) {
    return null; // or render with display: none
  }

  // 2. Create element based on type
  const element = createElementForType(node.type, node.name);

  // 3. Apply styles (fills, strokes, effects, layout, etc.)
  applyStyles(element, node);

  // 4. Recurse into children
  if (node.children) {
    for (const child of node.children) {
      const childEl = renderNode(child);
      if (childEl) element.appendChild(childEl);
    }
  }

  return element;
}
```

---

## Color Format

**v1 (aggressive):** Colors are RGBA objects with components in the range `[0, 1]`:

```js
function figmaColorToCss(color) {
  const r = Math.round(color.r * 255);
  const g = Math.round(color.g * 255);
  const b = Math.round(color.b * 255);
  return "rgba(" + r + ", " + g + ", " + b + ", " + color.a + ")";
}
```

**v2 (compact):** Colors are arrays: `[r, g, b]` (alpha=1) or `[r, g, b, a]` (alpha≠1):

```js
function compactColorToCss(color) {
  const r = Math.round(color[0] * 255);
  const g = Math.round(color[1] * 255);
  const b = Math.round(color[2] * 255);
  const a = color[3] !== undefined ? color[3] : 1;
  return "rgba(" + r + ", " + g + ", " + b + ", " + a + ")";
}
```

---

## Code Generation Guidelines

1. **Use semantic HTML** where possible (infer from `node.name` — e.g. "Button" → `<button>`, "Heading" → `<h1>`)
2. **Generate reusable CSS classes** — don't inline everything
3. **Map auto-layout to Flexbox/Grid** — use `layoutMode`, alignment, spacing properties
4. **Handle absolute positioning** when `layoutMode === "NONE"` — use `absoluteBoundingBox` for `top`, `left`, `width`, `height`
5. **Apply defaults rigorously** — missing properties are intentionally removed, not errors
6. **Respect visibility** — skip or add `display: none` for `visible === false`
7. **Handle text overrides** — use `characterStyleOverrides` to wrap styled segments in `<span>`
8. **Extract colors to CSS variables** for maintainability

---

## Example Interpretation (v1)

### Input (v1 cleaned JSON)

```json
{
  "id": "123:456",
  "name": "Primary Button",
  "type": "FRAME",
  "absoluteBoundingBox": { "x": 100, "y": 50, "width": 120, "height": 40 },
  "fills": [{ "type": "SOLID", "color": { "r": 0.29, "g": 0.56, "b": 1, "a": 1 } }],
  "cornerRadius": 8,
  "layoutMode": "HORIZONTAL",
  "primaryAxisAlignItems": "CENTER",
  "counterAxisAlignItems": "CENTER",
  "paddingLeft": 16,
  "paddingRight": 16,
  "children": [
    {
      "id": "123:457",
      "name": "Label",
      "type": "TEXT",
      "characters": "Click me",
      "fills": [{ "type": "SOLID", "color": { "r": 1, "g": 1, "b": 1, "a": 1 } }],
      "style": {
        "fontFamily": "Inter",
        "fontSize": 14,
        "fontWeight": 600,
        "textAlignHorizontal": "CENTER"
      }
    }
  ]
}
```

### Output (React + CSS)

```jsx
function PrimaryButton() {
  return (
    <div className="primary-button">
      <span className="label">Click me</span>
    </div>
  );
}
```

```css
.primary-button {
  /* Layout */
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 0; /* itemSpacing not present, assume 0 */
  
  /* Sizing */
  width: 120px;
  height: 40px;
  
  /* Spacing */
  padding-left: 16px;
  padding-right: 16px;
  padding-top: 0; /* not specified, assume 0 */
  padding-bottom: 0;
  
  /* Visual */
  background: rgba(74, 143, 255, 1);
  border-radius: 8px;
  
  /* Defaults (not in JSON, apply from _aiContext.defaults): */
  opacity: 1;
  /* visible: true → rendered, not display: none */
  /* blendMode: PASS_THROUGH → normal rendering */
  /* clipsContent: false → overflow: visible */
}

.label {
  font-family: Inter;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
  color: rgba(255, 255, 255, 1); /* from fills */
  
  /* Defaults: */
  /* opacity: 1 */
  /* visible: true */
}
```

---

## Compact Format (v2)

When `_aiContext.format` is `flowbridge-cleaned-figma-tree-v2`, the following differences apply. All v1 rules still apply unless overridden below.

### Invisible Nodes

Nodes with `visible: false` are **completely removed** from the tree (including all their children). You do not need to check for `visible === false` — every node in the tree is visible.

### Dimensions: `w` and `h`

Instead of `absoluteBoundingBox`, compact nodes have:

```json
{ "w": 320, "h": 48 }
```

- `w` = width in pixels (rounded to nearest integer)
- `h` = height in pixels (rounded to nearest integer)
- Canvas-relative `x`/`y` coordinates are dropped (not useful for code gen)

Use `w`/`h` for `width`/`height` in CSS when sizing is `"FIXED"`.

### Color Format

Colors are arrays instead of objects:

```json
[0.29, 0.56, 1]         // RGB, alpha = 1 (implicit)
[0, 0, 0, 0.25]         // RGBA, alpha ≠ 1
```

Values are in the range `[0, 1]`. Multiply by 255 for CSS `rgb()`/`rgba()`.

This format is used in: `fills[].color`, `effects[].color`, `style.color`, `gradientStops[].color`.

### Layout Object

Auto-layout properties are compacted into a single `layout` object:

```json
{
  "layout": {
    "mode": "HORIZONTAL",
    "gap": 12,
    "sizing": ["FILL", "HUG"],
    "primary": "CENTER",
    "counter": "CENTER",
    "padding": [10, 20, 10, 20],
    "wrap": true
  }
}
```

**Property mapping:**

| `layout` key | Original property | Notes |
|---|---|---|
| `mode` | `layoutMode` | `"HORIZONTAL"`, `"VERTICAL"`, or `"GRID"` |
| `sizing` | `[layoutSizingHorizontal, layoutSizingVertical]` | Array: `["FILL", "HUG"]` |
| `gap` | `itemSpacing` | Primary axis gap |
| `counterGap` | `counterAxisSpacing` | Cross axis gap (only if present) |
| `primary` | `primaryAxisAlignItems` | e.g. `"CENTER"`, `"SPACE_BETWEEN"` |
| `counter` | `counterAxisAlignItems` | e.g. `"CENTER"`, `"MIN"` |
| `counterContent` | `counterAxisAlignContent` | Wrapped track alignment |
| `padding` | `[top, right, bottom, left]` | Only if any non-zero |
| `wrap` | `true` if `layoutWrap === "WRAP"` | Omitted if `NO_WRAP` |
| `grid` | Grid sub-object | Only for `mode: "GRID"` |

**Grid sub-object** (when `mode: "GRID"`):

| Key | Original property |
|---|---|
| `cols` | `gridColumnCount` |
| `rows` | `gridRowCount` |
| `colGap` | `gridColumnGap` |
| `rowGap` | `gridRowGap` |
| `colSizing` | `gridColumnsSizing` |
| `rowSizing` | `gridRowsSizing` |

**Child-in-parent properties** remain top-level on child nodes:
- `layoutAlign` — only present when not `"INHERIT"`
- `layoutGrow` — only present when not `0`

If no `layout` key exists, the node uses absolute positioning (like `layoutMode: "NONE"` in v1).

### Text Nodes (v2 differences)

- **Fill color merged into `style`**: If a TEXT node had a single SOLID fill, the color is at `style.color` (array format) and `fills` is removed.
- **Empty overrides removed**: `characterStyleOverrides: []`, `styleOverrideTable: {}`, `lineTypes: ["NONE"]`, `lineIndentations: [0]` are all removed when empty/default.
- **Trimmed style properties**: `fontStyle` dropped when redundant with `fontWeight` (e.g., "Regular"=400, "Medium"=500, "Bold"=700). `lineHeightUnit`, `textAutoResize`, and `letterSpacing: 0` are dropped.

### Dropped Properties (v2)

These properties are **not present** in compact mode:
- `constraints` — overridden by auto-layout; not useful for code gen
- `blendMode` — rarely maps to meaningful CSS
- `styles` — internal Figma style reference IDs (e.g., `{ "fill": "2810:44798" }`)
- `locked` — not relevant for code gen
- `strokeWeight` when no strokes exist on the node
- `cornerSmoothing` when `0`

### Compact v2 Defaults

Fewer defaults since many properties are structurally removed:

| Property | Default Value |
|---|---|
| `opacity` | `1` |
| `clipsContent` | `false` |
| `layoutAlign` | `"INHERIT"` |
| `layoutGrow` | `0` |
| `strokeAlign` | `"INSIDE"` |
| `paint.opacity` | `1` |
| `paint.visible` | `true` |
| `effect.visible` | `true` |

### Example (v2 Compact)

```json
{
  "id": "123:456",
  "name": "Primary Button",
  "type": "FRAME",
  "w": 120,
  "h": 40,
  "fills": [{ "type": "SOLID", "color": [0.29, 0.56, 1] }],
  "cornerRadius": 8,
  "layout": {
    "mode": "HORIZONTAL",
    "sizing": ["HUG", "HUG"],
    "primary": "CENTER",
    "counter": "CENTER",
    "padding": [0, 16, 0, 16]
  },
  "children": [
    {
      "id": "123:457",
      "name": "Label",
      "type": "TEXT",
      "w": 88,
      "h": 24,
      "characters": "Click me",
      "style": {
        "fontFamily": "Inter",
        "fontSize": 14,
        "fontWeight": 600,
        "textAlignHorizontal": "CENTER",
        "color": [1, 1, 1]
      }
    }
  ]
}
```

---

## Special Cases

### Invisible Nodes

**v2 (compact):** Invisible nodes are removed from the tree entirely. You never need to check visibility.

**v1 (aggressive):** If `visible === false` (explicitly present in JSON), either:
- Skip rendering entirely, OR
- Render with `display: none` (if you need to preserve DOM structure)

### Transparent Backgrounds

If `fills` is **missing entirely** (not just an empty array), the background is transparent:
→ CSS: no `background` property or `background: transparent`

### Multiple Fills/Strokes

`fills` and `strokes` are **arrays** and can have multiple entries (layered backgrounds/borders).

Render in order:
- `fills[0]` is the bottom layer
- `fills[fills.length - 1]` is the top layer

CSS supports multiple backgrounds:
```css
background: 
  linear-gradient(...),  /* top fill */
  url(...),              /* middle fill */
  rgb(255, 0, 0);        /* bottom fill */
```

### Empty Text

If `characters === ""`, the TEXT node has no visible content. Still render the element for layout purposes (may have width/height from `absoluteBoundingBox`).

---

## Constraints and Responsiveness

For responsive design:

- `horizontal: "SCALE"` / `vertical: "SCALE"` → use percentages or viewport units (`vw`, `vh`)
- `horizontal: "LEFT_RIGHT"` → `width: 100%` (stretch to fill parent width)
- `vertical: "TOP_BOTTOM"` → `height: 100%` (stretch to fill parent height)

**Note:** Constraints are mostly ignored if the parent uses auto-layout (`layoutMode !== "NONE"`). Auto-layout takes precedence.

---

## Questions?

If you encounter a property or structure not documented here:
- Refer to the [Figma REST API documentation](https://www.figma.com/developers/api)
- Check `_aiContext.defaults` for default values
- Assume missing arrays are empty (`[]`)

**Remember:** This is a **compressed format**. Missing properties indicate defaults should be applied, not that the data is incomplete.

---

**End of guide.**
