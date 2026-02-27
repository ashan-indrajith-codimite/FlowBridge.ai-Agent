# React Skills - FlowBridge.ai

## Framework Identity
- **Name:** React
- **Version:** 18+
- **Language:** TypeScript (.tsx)
- **Styling:** Tailwind CSS v3 + `class-variance-authority` (cva)
- **State management:** React hooks (useState, useCallback)
- **Icon library:** lucide-react
- **Animation:** Tailwind animate utilities + `tailwind-merge`

---

## Component File Structure

```tsx
// 1. React imports
import { type ButtonHTMLAttributes, forwardRef } from "react";

// 2. Third-party utilities
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";          // shadcn/ui merge helper
import { Loader2 } from "lucide-react";   // icon example

// 3. Variant definitions (cva)
const buttonVariants = cva(
  // base classes
  "...",
  {
    variants: {
      variant: { primary: "...", secondary: "...", ghost: "..." },
      size:    { sm: "...", md: "...", lg: "..." },
    },
    defaultVariants: { variant: "primary", size: "md" },
  }
);

// 4. Props interface (extend native HTML element attrs)
export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
}

// 5. Component (forwardRef for ref forwarding)
const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, isLoading, leftIcon, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size }), className)}
        disabled={disabled || isLoading}
        aria-disabled={disabled || isLoading}
        aria-busy={isLoading}
        {...props}
      >
        {/* content */}
      </button>
    );
  }
);
Button.displayName = "Button";

// 6. Named export
export { Button, buttonVariants };
```

---

## Import Patterns

```tsx
// cn utility (shadcn/ui pattern)
import { cn } from "@/lib/utils";

// Class variance authority
import { cva, type VariantProps } from "class-variance-authority";

// Icons
import { Loader2, ChevronRight } from "lucide-react";

// React
import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from "react";
```

---

## Styling Approach

- **Base classes** go in the first argument of `cva()`.
- **Variants** are defined inside `cva({ variants: {} })`.
- **Conditional classes** use `cn()` — never string template literals.
- **State prefixes:** `hover:`, `focus-visible:`, `active:`, `disabled:`, `aria-busy:`.
- **Color tokens (Tailwind):**
  - Primary: `bg-indigo-500` / hover: `bg-indigo-600`
  - Disabled: `opacity-50 cursor-not-allowed`
  - Focus ring: `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2`
  - Hover glow: `hover:shadow-[0_8px_20px_rgba(99,102,241,0.5)]`
- **Transition:** Always add `transition-all duration-200` to interactive elements.

---

## State and Prop Patterns

### Disabled pattern
```tsx
// Spread disabled to the native button + aria-disabled for CSS
<button disabled={disabled || isLoading} aria-disabled={disabled || isLoading}>
```

### Loading pattern
```tsx
// Show spinner, hide or dim label, prevent interaction
{isLoading && (
  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
)}
<span className={cn(isLoading && "opacity-0 absolute")}>{children}</span>
```

Or simpler (spinner + label side by side):
```tsx
{isLoading ? (
  <>
    <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
    <span>Loading...</span>
  </>
) : (
  <>
    {leftIcon}
    {children}
  </>
)}
```

### Optional icon slot
```tsx
// leftIcon?: React.ReactNode — consumer passes <IconComponent className="h-4 w-4" />
{leftIcon && <span aria-hidden="true">{leftIcon}</span>}
```

---

## Naming Conventions

| Construct | Convention | Example |
|-----------|-----------|---------|
| Component | PascalCase | `Button`, `IconButton` |
| Props interface | `{Component}Props` | `ButtonProps` |
| cva variants object | `{component}Variants` | `buttonVariants` |
| File name | kebab-case or PascalCase | `button.tsx` / `Button.tsx` |
| Boolean props | `is` / `has` prefix | `isLoading`, `hasIcon` |
| Event handlers | `on` prefix | `onClick`, `onFocus` |
| CSS class helpers | `cn()` | `cn(base, conditional)` |

---

## Accessibility Requirements

```tsx
// Button role is implicit on <button> — no role needed
<button
  disabled={disabled || isLoading}
  aria-disabled={disabled || isLoading}   // for CSS :disabled-like styling on wrappers
  aria-busy={isLoading}                   // announces loading state to screen readers
  aria-label={ariaLabel}                  // when no visible text
>
```

- **Keyboard:** Native `<button>` handles Enter and Space automatically.
- **Focus ring:** Use `focus-visible:ring-*` (not `focus:ring-*`) to avoid rings on click.
- **Spinner:** Add `aria-hidden="true"` to the spinner icon; the `aria-busy` on the button is enough.
- **Tab order:** Never set `tabIndex={-1}` on a visible button.

---

## Reference Example

```tsx
import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

const buttonVariants = cva(
  [
    "inline-flex items-center justify-center gap-2",
    "rounded-lg px-5 py-2.5",
    "text-sm font-semibold tracking-wide",
    "transition-all duration-200",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
    "disabled:pointer-events-none disabled:opacity-50",
  ].join(" "),
  {
    variants: {
      variant: {
        primary: [
          "bg-indigo-500 text-white",
          "hover:bg-indigo-600",
          "hover:shadow-[0_8px_20px_rgba(99,102,241,0.5)]",
          "focus-visible:ring-indigo-500",
          "active:scale-[0.98]",
        ].join(" "),
        secondary: [
          "bg-white text-indigo-600 border border-indigo-300",
          "hover:bg-indigo-50",
          "focus-visible:ring-indigo-400",
        ].join(" "),
        ghost: [
          "text-indigo-600",
          "hover:bg-indigo-50",
          "focus-visible:ring-indigo-400",
        ].join(" "),
      },
      size: {
        sm: "px-3 py-1.5 text-xs rounded-md",
        md: "px-5 py-2.5 text-sm rounded-lg",
        lg: "px-7 py-3.5 text-base rounded-xl",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  }
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
  leftIcon?: ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      isLoading = false,
      leftIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || isLoading;

    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size }), className)}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        aria-busy={isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            <span>Loading...</span>
          </>
        ) : (
          <>
            {leftIcon && <span aria-hidden="true">{leftIcon}</span>}
            {children}
          </>
        )}
      </button>
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
```

---

## Do / Don't Rules

**Do:**
- Use `forwardRef` for all components that wrap native HTML elements.
- Use `cva` for multi-variant styling — keeps variants co-located and type-safe.
- Use `cn()` (tailwind-merge + clsx) for all conditional class concatenation.
- Export both the component AND the `buttonVariants` function for composability.
- Set `displayName` when using `forwardRef`.
- Use `focus-visible:` prefix, not bare `focus:`.
- Use `disabled:pointer-events-none` to block hover effects on disabled state.

**Don't:**
- Don't use template literals for conditional Tailwind classes.
- Don't use `className={condition ? "a" : "b"}` — use `cn()` instead.
- Don't import from `react/jsx-runtime` directly.
- Don't add `role="button"` to a `<button>` element.
- Don't use `outline-none` without a visible focus replacement.
- Don't leave `TODO` comments in generated code.
- Don't use inline styles — use Tailwind classes only.
