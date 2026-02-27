# HTML Skills — FlowBridge.ai

## Framework Identity
- **Name:** HTML (Plain / Vanilla)
- **Version:** HTML5
- **Language:** HTML (.html)
- **Styling:** Determined by `styling_conventions` in state (Tailwind CSS OR inline CSS)
- **Interactivity:** Vanilla JavaScript (no frameworks, no build tools)
- **Dependencies:** NONE — single self-contained .html file

> This is a ZERO-DEPENDENCY output. The generated file must open directly in any browser with no build step, no npm, no bundler.

---

## File Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ComponentName</title>
  <!-- If using Tailwind: include CDN script -->
  <!-- <script src="https://cdn.tailwindcss.com"></script> -->
  <style>
    /* If using inline_css: global resets and font imports go here */
    /* If using tailwind: minimal resets only */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  </style>
</head>
<body>
  <!-- Component markup here -->

  <script>
    // Vanilla JS for interactivity
  </script>
</body>
</html>
```

---

## Tailwind CSS Mode (when styling == "tailwind")

When the styling approach is Tailwind CSS:

1. Include `<script src="https://cdn.tailwindcss.com"></script>` in the `<head>`.
2. Use Tailwind utility classes with EXACT arbitrary values from design tokens.
3. Follow the same arbitrary value rules as React Tailwind mode:
   - Colors: `class="bg-[#9447B0] text-[#FFFFFF]"`
   - Spacing: `class="gap-[32px] py-[10px] px-[20px]"`
   - Font size: `class="text-[19.5px] font-[500]"`
   - Font family: `class="font-['Public_Sans']"`
   - Border radius: `class="rounded-[6px]"`
   - Shadows: `class="shadow-[0_2px_4px_rgba(0,0,0,0.3)]"`
4. Use `class` attribute (NOT `className` — this is HTML, not JSX).
5. No approximation with named Tailwind classes.

```html
<!-- ✅ Correct -->
<button class="bg-[#9447B0] text-[#FFFFFF] rounded-[6px] py-[10px] px-[20px] text-[14px] font-[600]">
  Login
</button>

<!-- ❌ Wrong -->
<button class="bg-purple-600 text-white rounded-md py-2.5 px-5 text-sm font-semibold">
  Login
</button>
```

---

## Inline CSS Mode (when styling == "inline_css")

When the styling approach is inline CSS:

1. Do NOT include Tailwind CDN.
2. Use `style="..."` attributes with exact values from design tokens.
3. Use standard CSS property names (hyphenated, not camelCase).
4. All visual styling goes in `style` attributes.
5. Use `<style>` block in `<head>` ONLY for:
   - CSS reset
   - Font imports (@import or @font-face)
   - Pseudo-class styles (:hover, :focus, :disabled) that cannot be inline
   - Animations (@keyframes)

```html
<!-- ✅ Correct -->
<button style="background-color: #9447B0; color: #FFFFFF; border-radius: 6px; padding: 10px 20px; font-size: 14px; font-weight: 600; border: none; cursor: pointer;">
  Login
</button>

<!-- For hover/focus states, use a <style> block -->
<style>
  .login-btn:hover { background-color: #7D3A99; }
  .login-btn:focus-visible { outline: 2px solid #9447B0; outline-offset: 2px; }
  .login-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
<button class="login-btn" style="background-color: #9447B0; color: #FFFFFF; ...">
  Login
</button>
```

---

## Interactivity — Vanilla JavaScript

```html
<script>
  // DOM ready
  document.addEventListener("DOMContentLoaded", () => {
    // Query elements
    const form = document.getElementById("login-form");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const submitBtn = document.getElementById("submit-btn");

    // Form validation
    function validateField(input, errorEl) {
      if (!input.value.trim()) {
        errorEl.textContent = input.name.charAt(0).toUpperCase() + input.name.slice(1) + " is required";
        errorEl.setAttribute("aria-live", "polite");
        input.setAttribute("aria-invalid", "true");
        return false;
      }
      errorEl.textContent = "";
      input.removeAttribute("aria-invalid");
      return true;
    }

    // Blur validation
    usernameInput.addEventListener("blur", () => {
      validateField(usernameInput, document.getElementById("username-error"));
    });

    // Password show/hide toggle
    const toggleBtn = document.getElementById("toggle-password");
    toggleBtn.addEventListener("click", () => {
      const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
      passwordInput.setAttribute("type", type);
      toggleBtn.setAttribute("aria-label", type === "password" ? "Show password" : "Hide password");
    });

    // Form submit
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      // Validate all fields
      // If valid, handle submission
    });

    // Auto-focus first input
    usernameInput.focus();
  });
</script>
```

---

## Accessibility Patterns

```html
<!-- Form -->
<form id="login-form" novalidate>

<!-- Label + input pair -->
<label for="username">Username</label>
<input
  type="text"
  id="username"
  name="username"
  aria-invalid="false"
  aria-describedby="username-error"
/>
<p id="username-error" role="alert" aria-live="polite"></p>

<!-- Submit button -->
<button type="submit" id="submit-btn" aria-busy="false">
  Login
</button>
</form>
```

---

## Icons — Inline SVG Only

No icon libraries. Use inline SVG for all icons:

```html
<!-- Eye icon (show password) -->
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
  <circle cx="12" cy="12" r="3"></circle>
</svg>

<!-- Eye-off icon (hide password) -->
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
  <line x1="1" y1="1" x2="23" y2="23"></line>
</svg>

<!-- Spinner -->
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2" class="spinner" aria-hidden="true">
  <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
</svg>
<style>
  @keyframes spin { to { transform: rotate(360deg); } }
  .spinner { animation: spin 1s linear infinite; }
</style>
```

---

## Loading State Pattern

```html
<!-- Normal state -->
<button type="submit" id="submit-btn">Login</button>

<!-- Loading state (swap via JS) -->
<button type="submit" id="submit-btn" disabled aria-busy="true">
  <svg class="spinner" ...></svg>
  <span>Logging in...</span>
</button>
```

---

## Naming Conventions

| Construct | Convention | Example |
|-----------|------------|---------|
| IDs | kebab-case | `id="login-form"` |
| Classes | kebab-case | `class="login-btn"` |
| JS variables | camelCase | `const submitBtn` |
| Functions | camelCase | `function validateField()` |

---

## Full Screen Layout

```html
<body style="margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; background-color: #F5F5F5; padding: 16px;">
  <div style="width: 100%; max-width: 300px;">
    <!-- Component content -->
  </div>
</body>
```

---

## Do / Don't Rules

**Do:**
- Output a single, complete, self-contained .html file.
- Use exact values from Figma JSON / design tokens — no approximation.
- Use semantic HTML elements (form, label, button, input).
- Include all accessibility attributes (aria-invalid, aria-describedby, aria-live, aria-busy).
- Auto-focus the first input field on page load.
- Use `novalidate` on forms to prevent browser validation UI.
- Use inline SVG for all icons.
- For Tailwind mode: include the CDN script tag.

**Don't:**
- Don't use any npm packages or build tools.
- Don't use React, Vue, Angular, or any framework.
- Don't use `className` — this is HTML, use `class`.
- Don't use JSX syntax like `style={{}}` — use `style="..."`.
- Don't approximate values with named Tailwind classes.
- Don't use external icon libraries.
- Don't leave TODO comments.
- Don't use ES modules or import statements in the script.
