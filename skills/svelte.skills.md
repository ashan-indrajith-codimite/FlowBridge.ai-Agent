# Svelte Skills - FlowBridge.ai

## Framework Identity
- **Name:** Svelte
- **Version:** 5 (Runes API)
- **Language:** TypeScript
- **File extension:** `.svelte`
- **Styling:** Tailwind CSS v3
- **State management:** `$state()`, `$derived()`, `$effect()` runes
- **Icon library:** `lucide-svelte`
- **Animation:** Tailwind animate + Svelte transitions

---

## Component File Structure

```svelte
<script lang="ts">
  // 1. Svelte runes + imports
  import { Loader2 } from "lucide-svelte";

  // 2. Props via $props() rune (Svelte 5)
  interface Props {
    variant?: "primary" | "secondary" | "ghost";
    size?: "sm" | "md" | "lg";
    isLoading?: boolean;
    disabled?: boolean;
    onclick?: (event: MouseEvent) => void;
    children?: import("svelte").Snippet;
    icon?: import("svelte").Snippet;
  }

  let {
    variant = "primary",
    size = "md",
    isLoading = false,
    disabled = false,
    onclick,
    children,
    icon,
  }: Props = $props();

  // 3. Derived state via $derived()
  const isDisabled = $derived(disabled || isLoading);

  // 4. Derived class string
  const buttonClasses = $derived(() => {
    const base = [
      "inline-flex items-center justify-center gap-2 rounded-lg",
      "text-sm font-semibold tracking-wide",
      "transition-all duration-200",
      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
    ].join(" ");

    const variants = {
      primary: [
        "bg-indigo-500 text-white",
        "hover:bg-indigo-600",
        "hover:shadow-[0_8px_20px_rgba(99,102,241,0.5)]",
        "focus-visible:ring-indigo-500",
        "active:scale-[0.98]",
      ].join(" "),
      secondary:
        "bg-white text-indigo-600 border border-indigo-300 hover:bg-indigo-50 focus-visible:ring-indigo-400",
      ghost:
        "text-indigo-600 hover:bg-indigo-50 focus-visible:ring-indigo-400",
    };

    const sizes = {
      sm: "px-3 py-1.5 text-xs rounded-md",
      md: "px-5 py-2.5 text-sm rounded-lg",
      lg: "px-7 py-3.5 text-base rounded-xl",
    };

    return [
      base,
      variants[variant],
      sizes[size],
      isDisabled ? "opacity-50 cursor-not-allowed pointer-events-none" : "",
    ]
      .filter(Boolean)
      .join(" ");
  });

  function handleClick(event: MouseEvent) {
    if (!isDisabled) onclick?.(event);
  }
</script>

<button
  class={buttonClasses()}
  disabled={isDisabled}
  aria-disabled={isDisabled}
  aria-busy={isLoading}
  onclick={handleClick}
>
  {#if isLoading}
    <Loader2 class="h-4 w-4 animate-spin" aria-hidden="true" />
    <span class="sr-only">Loading</span>
  {:else}
    {#if icon}
      <span aria-hidden="true">{@render icon()}</span>
    {/if}
    {@render children?.()}
  {/if}
</button>
```

---

## Import Patterns

```svelte
<script lang="ts">
  // Icons
  import { Loader2, ChevronRight } from "lucide-svelte";

  // Svelte snippets type (for typing)
  import type { Snippet } from "svelte";
</script>
```

---

## Styling Approach

- Use `class={derivedExpression()}` binding — **not** `class:name={condition}` for complex scenarios.
- Use `class:active={condition}` directive for single boolean class toggles.
- Build full class strings in `$derived()` — keep template clean.
- **State prefixes:** `hover:`, `focus-visible:`, `active:`, `disabled:`.
- **Color tokens:**
  - Primary: `bg-indigo-500` → hover: `bg-indigo-600`
  - Disabled: `opacity-50 cursor-not-allowed pointer-events-none`
  - Focus ring: `focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2`
  - Hover glow: `hover:shadow-[0_8px_20px_rgba(99,102,241,0.5)]`

---

## State and Prop Patterns

### Props (Svelte 5 runes)
```svelte
<script lang="ts">
  interface Props { label?: string; isLoading?: boolean; }
  let { label = "Button", isLoading = false }: Props = $props();
</script>
```

### Reactive state
```svelte
let count = $state(0);
const doubled = $derived(count * 2);
```

### Side effects
```svelte
$effect(() => {
  console.log("isLoading changed:", isLoading);
});
```

### Snippets (Svelte 5 replacement for slots)
```svelte
<!-- Consumer -->
<Button>
  {#snippet icon()}<ChevronRight class="h-4 w-4" />{/snippet}
  Click me
</Button>

<!-- Component -->
{@render icon?.()}
{@render children?.()}
```

### class: directive (for single toggles)
```svelte
<button
  class="base-classes"
  class:opacity-50={isDisabled}
  class:cursor-not-allowed={isDisabled}
>
```

---

## Naming Conventions

| Construct | Convention | Example |
|-----------|-----------|---------|
| Component file | PascalCase | `Button.svelte` |
| Props destructuring | camelCase | `isLoading`, `variant` |
| Derived state | camelCase | `isDisabled`, `buttonClasses` |
| Snippets | camelCase | `icon`, `children` |
| Event handlers | `handle` prefix | `handleClick`, `handleKeydown` |
| Type/Interface | PascalCase | `ButtonVariant`, `Props` |

---

## Accessibility Requirements

```svelte
<button
  disabled={isDisabled}
  aria-disabled={isDisabled}
  aria-busy={isLoading}
>
```

- `<button>` natively handles Enter and Space.
- `aria-busy={isLoading}` announces loading state.
- `aria-disabled={isDisabled}` — in Svelte, boolean values are rendered as the attribute being present/absent (correct behavior).
- Add `aria-hidden="true"` to decorative spinner icons.
- Use `class="sr-only"` for screen-reader-only loading text.
- Focus ring: `focus-visible:ring-*` Tailwind classes.

---

## Reference Example

```svelte
<script lang="ts">
  import { Loader2 } from "lucide-svelte";
  import type { Snippet } from "svelte";

  type ButtonVariant = "primary" | "secondary" | "ghost";
  type ButtonSize = "sm" | "md" | "lg";

  interface Props {
    variant?: ButtonVariant;
    size?: ButtonSize;
    isLoading?: boolean;
    disabled?: boolean;
    onclick?: (event: MouseEvent) => void;
    children?: Snippet;
    icon?: Snippet;
  }

  let {
    variant = "primary",
    size = "md",
    isLoading = false,
    disabled = false,
    onclick,
    children,
    icon,
  }: Props = $props();

  const isDisabled = $derived(disabled || isLoading);

  const buttonClasses = $derived(() => {
    const variants: Record<ButtonVariant, string> = {
      primary:
        "bg-indigo-500 text-white hover:bg-indigo-600 hover:shadow-[0_8px_20px_rgba(99,102,241,0.5)] focus-visible:ring-indigo-500 active:scale-[0.98]",
      secondary:
        "bg-white text-indigo-600 border border-indigo-300 hover:bg-indigo-50 focus-visible:ring-indigo-400",
      ghost: "text-indigo-600 hover:bg-indigo-50 focus-visible:ring-indigo-400",
    };

    const sizes: Record<ButtonSize, string> = {
      sm: "px-3 py-1.5 text-xs rounded-md",
      md: "px-5 py-2.5 text-sm rounded-lg",
      lg: "px-7 py-3.5 text-base rounded-xl",
    };

    return [
      "inline-flex items-center justify-center gap-2 rounded-lg text-sm font-semibold tracking-wide",
      "transition-all duration-200",
      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
      variants[variant],
      sizes[size],
      isDisabled ? "opacity-50 cursor-not-allowed pointer-events-none" : "",
    ]
      .filter(Boolean)
      .join(" ");
  });

  function handleClick(event: MouseEvent) {
    if (!isDisabled) onclick?.(event);
  }
</script>

<button
  class={buttonClasses()}
  disabled={isDisabled}
  aria-disabled={isDisabled}
  aria-busy={isLoading}
  onclick={handleClick}
>
  {#if isLoading}
    <Loader2 class="h-4 w-4 animate-spin" aria-hidden="true" />
    <span class="sr-only">Loading</span>
  {:else}
    {#if icon}
      <span aria-hidden="true">{@render icon()}</span>
    {/if}
    {@render children?.()}
  {/if}
</button>
```

---

## Do / Don't Rules

**Do:**
- Use `$props()` rune — not `export let` (Svelte 4 pattern).
- Use `$state()` for mutable reactive state.
- Use `$derived()` for computed values.
- Use `$effect()` for side effects (replaces `$: effect`).
- Use Snippets (`Snippet` type + `{@render}`) — not slots (Svelte 4).
- Type your Props interface explicitly.
- Use `onclick` (lowercase, no `on:click`) — Svelte 5 event syntax.

**Don't:**
- Don't use `export let` for props — that's Svelte 4.
- Don't use `<slot>` — use Snippets in Svelte 5.
- Don't use `on:click={handler}` — use `onclick={handler}` in Svelte 5.
- Don't use `$:` reactive declarations — use `$derived()` and `$effect()`.
- Don't build class strings in the template — build in `$derived()`.
- Don't skip `lang="ts"` on the script tag.
