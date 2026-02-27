# React Standalone Skills — FlowBridge.ai

## Framework Identity
- **Name:** React
- **Version:** 18+
- **Language:** TypeScript (.tsx)
- **Styling:** Tailwind CSS v3 — arbitrary values for pixel-perfect fidelity
- **State management:** React hooks (useState, useEffect, useRef, useCallback)
- **Icon library:** Inline SVG only — no lucide-react, no heroicons, no external icon packages
- **Dependencies:** ONLY `react` and `react-dom` — nothing else. No icon libraries.

> ⚠️ STANDALONE MODE: No shadcn/ui, no `cn()`, no `cva`, no `@/lib/utils`, no lucide-react,
> no heroicons, no external icon packages. Use inline SVG for all icons.

---

## Component File Structure

```tsx
// 1. React imports — named imports only
import { useState, useEffect, useRef, useCallback } from "react";

// 2. NO external icon imports — use inline SVG inside the component
// Example inline SVG eye icon:
// const EyeIcon = () => (
//   <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
//        fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
//     <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
//     <circle cx="12" cy="12" r="3" />
//   </svg>
// );

// 3. TypeScript props interface
export interface ComponentNameProps {
  onSubmit: (values: FormValues) => void;
  isLoading?: boolean;
}

// 4. Component — React.FC or function declaration
const ComponentName: React.FC<ComponentNameProps> = ({
  onSubmit,
  isLoading = false,
}) => {
  // 5. State hooks
  const [value, setValue] = useState("");

  // 6. Refs
  const inputRef = useRef<HTMLInputElement>(null);

  // 7. Effects
  useEffect(() => { inputRef.current?.focus(); }, []);

  // 8. Handlers
  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    // ...
  }, []);

  // 9. Return JSX
  return (
    <div className="...">
      {/* content */}
    </div>
  );
};

// 10. Default export
export default ComponentName;
```

---

## Tailwind Arbitrary Values — REQUIRED for pixel fidelity

FlowBridge generates pixel-faithful components. ALWAYS use exact values from
the Figma JSON as Tailwind arbitrary values. Never approximate with Tailwind
named classes.

### Colors
```tsx
// ✅ Exact hex from Figma JSON
className="bg-[#9447B0] text-[#FFFFFF]"
className="border-[#DBD9DE]"
className="text-[#474557]"

// ❌ NEVER approximate
className="bg-purple-600 text-white"   // wrong — invented color
className="border-gray-300"            // wrong — wrong value
```

### Spacing (gap, padding, margin, width, height)
```tsx
// ✅ Exact px values
className="gap-[32px] py-[10px] px-[20px]"
className="gap-[7.5px] gap-[4.5px]"
className="w-[300px] max-w-[300px]"

// ❌ NEVER approximate
className="gap-8 py-2.5 px-5"     // wrong — approximation
className="w-72"                   // wrong — not exact
```

### Font size and weight
```tsx
// ✅ Exact values
className="text-[19.5px] font-[500]"
className="text-[9px] font-[400]"
className="text-[24px] font-[600]"

// ❌ NEVER approximate
className="text-xl font-medium"    // wrong
className="text-lg font-semibold"  // wrong
```

### Font family
```tsx
// ✅ Use font-['Font_Name'] with underscores for spaces
className="font-['Public_Sans']"
className="font-['Open_Sans']"

// ❌ NEVER
className="font-sans"             // wrong
```

### Border radius
```tsx
// ✅ Exact px from Figma
className="rounded-[6px]"

// ❌ NEVER
className="rounded-md"            // wrong
```

### Shadows
```tsx
// ✅ Exact CSS shadow
className="shadow-[0_2px_4px_rgba(0,0,0,0.3)]"

// ❌ NEVER
className="shadow-md"             // wrong
```

---

## Conditional Classes — Plain Template Literals

Without `cn()`, use template literals for conditional className logic:

```tsx
// Simple conditional
<input
  className={`w-full rounded-[6px] border py-[7px] px-[14px]
    ${hasError
      ? "border-[#D32F2F] focus:ring-[#D32F2F]/20"
      : "border-[#DBD9DE] hover:border-[#BDBDBD] focus:border-[#9447B0] focus:ring-[#9447B0]/20"
    }
    disabled:cursor-not-allowed disabled:bg-gray-100
    focus:outline-none focus:ring-2 transition-colors duration-200
  `}
/>
```

Multi-line template literals are fine for readability. Always trim whitespace
concerns by keeping each conditional on its own line.

---

## State Patterns

### Form state
```tsx
const [username, setUsername] = useState("");
const [password, setPassword] = useState("");
const [showPassword, setShowPassword] = useState(false);
const [errors, setErrors] = useState<{ username?: string; password?: string }>({});
```

### Loading pattern (spinner + text swap)
```tsx
<button
  type="submit"
  disabled={isLoading || isFormInvalid}
  aria-busy={isLoading}
  className={`w-full flex items-center justify-center gap-[8px]
    rounded-[6px] py-[10px] px-[20px]
    bg-[#9447B0] text-[#FFFFFF] text-[14px] font-[600]
    shadow-[0_2px_4px_rgba(0,0,0,0.3)]
    hover:bg-[#7D3A99]
    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#9447B0] focus-visible:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
    transition-all duration-200
  `}
>
  {isLoading ? (
    <>
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
           fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
           className="animate-spin" aria-hidden="true">
        <path d="M21 12a9 9 0 1 1-6.219-8.56" />
      </svg>
      <span>Logging in...</span>
    </>
  ) : (
    <span>Login</span>
  )}
</button>
```

### Password visibility toggle
```tsx
const [showPassword, setShowPassword] = useState(false);

// Input
<input type={showPassword ? "text" : "password"} ... />

// Toggle button (inside relative container)
<button
  type="button"
  onClick={() => setShowPassword(prev => !prev)}
  aria-label={showPassword ? "Hide password" : "Show password"}
  className="absolute inset-y-0 right-0 flex items-center pr-3
    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#9447B0]/50"
>
  {showPassword ? (
    // Eye icon (password visible)
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
         fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
         className="text-[#706B7D]" aria-hidden="true">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" />
    </svg>
  ) : (
    // Eye-off icon (password hidden)
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
         fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
         className="text-[#706B7D]" aria-hidden="true">
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  }
</button>
```

### Validation on blur
```tsx
const validateField = useCallback((field: "username" | "password", value: string) => {
  const newErrors = { ...errors };
  if (field === "username" && !value.trim()) {
    newErrors.username = "Username is required";
  } else if (field === "username") {
    delete newErrors.username;
  }
  if (field === "password" && value.length < 6) {
    newErrors.password = "Password must be at least 6 characters";
  } else if (field === "password" && value.length >= 6) {
    delete newErrors.password;
  }
  setErrors(newErrors);
}, [errors]);
```

---

## Accessibility Patterns

```tsx
// Form
<form onSubmit={handleSubmit} noValidate>

// Label + input pair (htmlFor ↔ id)
<label htmlFor="username">Username</label>
<input
  id="username"
  name="username"
  aria-invalid={!!errors.username}
  aria-describedby={errors.username ? "username-error" : undefined}
/>

// Inline error (aria-live for screen readers)
{errors.username && (
  <p id="username-error" role="alert" aria-live="polite">
    {errors.username}
  </p>
)}

// Auto-focus on mount
const usernameRef = useRef<HTMLInputElement>(null);
useEffect(() => { usernameRef.current?.focus(); }, []);

// Focus ring — always use focus-visible: not focus:
className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#9447B0] focus-visible:ring-offset-2"
```

---

## Naming Conventions

| Construct | Convention | Example |
|-----------|------------|---------|
| Component | PascalCase | `LoginScreenContainer` |
| Props interface | `{Component}Props` | `LoginScreenContainerProps` |
| State booleans | `is` / `has` / `show` | `isLoading`, `showPassword` |
| Event handlers | `handle` prefix | `handleSubmit`, `handleBlur` |
| Refs | `{field}Ref` | `usernameRef` |

---

## Full Screen Layout Wrapper

For full-screen centered layouts (not atomic components), use:

```tsx
// Outer: center on full screen
<div className="min-h-screen flex items-center justify-center bg-[#F5F5F5] p-4">
  {/* Inner: constrained width card, exact dimensions from Figma */}
  <div className="w-full max-w-[300px] flex flex-col gap-[32px]">
    {/* Sections go here */}
  </div>
</div>
```

---

## Do / Don't Rules

**Do:**
- Use exact px values from the Figma JSON as Tailwind arbitrary values.
- Use `font-['Font_Name']` for non-standard fonts.
- Use `focus-visible:` prefix, not bare `focus:`.
- Use `disabled:pointer-events-none disabled:opacity-50` pattern.
- Use `transition-all duration-200` on all interactive elements.
- Auto-focus the first input field on mount.
- Use `type="submit"` on the submit button inside a `<form>`.
- Use `noValidate` on forms to prevent browser validation UI.

**Don't:**
- Don't use semantic Tailwind color names (bg-purple-600, text-gray-700) — use exact hex.
- Don't use cn() or cva from external packages.
- Don't import from "@/lib/utils" — no such file exists in standalone mode.
- Don't use inline `style={{}}` props — use Tailwind classes only.
- Don't use role="button" on a `<button>` element.
- Don't leave TODO comments.
- Don't use template literals for static classes — direct string is fine.
- Don't approximate spacing with named Tailwind classes (gap-8, p-4, etc.).
- Don't import lucide-react, heroicons, or ANY external icon package — use inline SVG instead.
