# Vue Skills - FlowBridge.ai

## Framework Identity
- **Name:** Vue
- **Version:** 3.4+ (Composition API)
- **Language:** TypeScript (`<script setup lang="ts">`)
- **File extension:** `.vue` (Single File Component)
- **Styling:** Tailwind CSS v3
- **State management:** `ref`, `computed`, `defineProps`, `defineEmits`
- **Icon library:** `@iconify/vue` or lucide-vue-next
- **Animation:** Tailwind animate + Vue `<Transition>`

---

## Component File Structure

```vue
<script setup lang="ts">
// 1. Vue imports
import { computed } from "vue";

// 2. Third-party imports
import { Loader2 } from "lucide-vue-next";

// 3. Props definition (TypeScript generic syntax — preferred over runtime)
interface Props {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  disabled?: boolean;
  leftIcon?: string; // icon component or name
}

const props = withDefaults(defineProps<Props>(), {
  variant: "primary",
  size: "md",
  isLoading: false,
  disabled: false,
});

// 4. Emits
const emit = defineEmits<{
  click: [event: MouseEvent];
}>();

// 5. Computed state
const isDisabled = computed(() => props.disabled || props.isLoading);

// 6. Class binding (computed, not inline)
const buttonClasses = computed(() => [
  "inline-flex items-center justify-center gap-2 rounded-lg font-semibold",
  "transition-all duration-200",
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
  {
    // variant classes
    "bg-indigo-500 text-white hover:bg-indigo-600 focus-visible:ring-indigo-500":
      props.variant === "primary",
    "bg-white text-indigo-600 border border-indigo-300 hover:bg-indigo-50":
      props.variant === "secondary",
    // size classes
    "px-3 py-1.5 text-xs": props.size === "sm",
    "px-5 py-2.5 text-sm": props.size === "md",
    // state classes
    "opacity-50 cursor-not-allowed pointer-events-none": isDisabled.value,
    "hover:shadow-[0_8px_20px_rgba(99,102,241,0.5)]":
      props.variant === "primary" && !isDisabled.value,
  },
]);

function handleClick(event: MouseEvent) {
  if (!isDisabled.value) emit("click", event);
}
</script>

<template>
  <button
    :class="buttonClasses"
    :disabled="isDisabled"
    :aria-disabled="isDisabled"
    :aria-busy="isLoading"
    @click="handleClick"
  >
    <Loader2 v-if="isLoading" class="h-4 w-4 animate-spin" aria-hidden="true" />
    <span v-if="!isLoading && leftIcon" aria-hidden="true">
      <slot name="icon" />
    </span>
    <span :class="{ 'opacity-0': isLoading }">
      <slot>Button</slot>
    </span>
  </button>
</template>
```

---

## Import Patterns

```vue
<script setup lang="ts">
// Vue core
import { ref, computed, watch } from "vue";

// Icons (lucide)
import { Loader2, ChevronRight } from "lucide-vue-next";

// Utility
import { cn } from "@/lib/utils"; // if using tailwind-merge
</script>
```

---

## Styling Approach

- Use `:class` binding with a **computed array/object** — not inline ternary.
- Object syntax: `{ 'class-name': booleanCondition }`.
- Array syntax: `['static-class', { 'conditional': expr }]`.
- **State prefixes:** `hover:`, `focus-visible:`, `active:`, `disabled:`.
- **Tailwind color tokens:**
  - Primary: `bg-indigo-500` → hover: `bg-indigo-600`
  - Disabled: `opacity-50 cursor-not-allowed pointer-events-none`
  - Focus ring: `focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2`
  - Hover glow: `hover:shadow-[0_8px_20px_rgba(99,102,241,0.5)]`
- Apply `pointer-events-none` in CSS class (not via HTML attribute) for disabled to preserve event capture for overlays.

---

## State and Prop Patterns

### Controlled disabled + loading
```vue
const isDisabled = computed(() => props.disabled || props.isLoading);
```

### Loading state
```vue
<Loader2 v-if="isLoading" class="h-4 w-4 animate-spin" aria-hidden="true" />
<span v-else><slot /></span>
```

### Conditional rendering vs `v-show`
- Use `v-if` for elements that should not exist in the DOM when hidden (spinner, icon).
- Use `v-show` only for elements that toggle frequently and are expensive to mount.

### Slot pattern for icon
```vue
<!-- Named slot for icon -->
<slot name="icon" />

<!-- Consumer usage -->
<Button>
  <template #icon><ChevronRight class="h-4 w-4" /></template>
  Click me
</Button>
```

---

## Naming Conventions

| Construct | Convention | Example |
|-----------|-----------|---------|
| Component file | PascalCase | `Button.vue`, `IconButton.vue` |
| Props interface | `Props` (local) | `interface Props { ... }` |
| Emits | `defineEmits<{...}>()` | `emit('click', event)` |
| Computed | camelCase | `isDisabled`, `buttonClasses` |
| Template ref | camelCase + `Ref` | `buttonRef` |
| Boolean props | `is` / `has` prefix | `isLoading`, `hasIcon` |
| Slots | kebab-case | `#icon`, `#default` |

---

## Accessibility Requirements

```vue
<button
  :disabled="isDisabled"
  :aria-disabled="String(isDisabled)"
  :aria-busy="String(isLoading)"
>
```

- `<button>` is natively keyboard accessible — no `@keydown` needed.
- `aria-disabled` uses string `"true"/"false"` in Vue template bindings, or use `:aria-disabled="isDisabled"` (Vue handles boolean → string).
- `aria-busy="true"` on the button while loading.
- `aria-hidden="true"` on decorative spinner icons.
- Focus ring: Use `focus-visible:ring-*` Tailwind classes.

---

## Reference Example

```vue
<script setup lang="ts">
import { computed } from "vue";
import { Loader2 } from "lucide-vue-next";

interface Props {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: "primary",
  size: "md",
  isLoading: false,
  disabled: false,
});

const emit = defineEmits<{ click: [event: MouseEvent] }>();

const isDisabled = computed(() => props.disabled || props.isLoading);

const buttonClasses = computed(() => [
  "inline-flex items-center justify-center gap-2 rounded-lg",
  "text-sm font-semibold tracking-wide",
  "transition-all duration-200",
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
  {
    "bg-indigo-500 text-white hover:bg-indigo-600 focus-visible:ring-indigo-500 hover:shadow-[0_8px_20px_rgba(99,102,241,0.5)]":
      props.variant === "primary",
    "bg-white text-indigo-600 border border-indigo-300 hover:bg-indigo-50 focus-visible:ring-indigo-400":
      props.variant === "secondary",
    "text-indigo-600 hover:bg-indigo-50 focus-visible:ring-indigo-400":
      props.variant === "ghost",
    "px-3 py-1.5 text-xs rounded-md": props.size === "sm",
    "px-5 py-2.5 text-sm rounded-lg": props.size === "md",
    "px-7 py-3.5 text-base rounded-xl": props.size === "lg",
    "opacity-50 cursor-not-allowed pointer-events-none": isDisabled.value,
  },
]);
</script>

<template>
  <button
    :class="buttonClasses"
    :disabled="isDisabled"
    :aria-disabled="isDisabled"
    :aria-busy="isLoading"
    @click="(e) => { if (!isDisabled) emit('click', e) }"
  >
    <Loader2 v-if="isLoading" class="h-4 w-4 animate-spin" aria-hidden="true" />
    <template v-if="!isLoading">
      <span v-if="$slots.icon" aria-hidden="true"><slot name="icon" /></span>
      <slot>Button</slot>
    </template>
    <span v-if="isLoading" class="sr-only">Loading</span>
  </button>
</template>
```

---

## Do / Don't Rules

**Do:**
- Use `<script setup lang="ts">` — always, no Options API.
- Use `defineProps<Props>()` generic syntax for type-safe props.
- Use `withDefaults()` to set default prop values.
- Use computed properties for class bindings — keep template readable.
- Use named slots for icon/action areas.
- Emit typed events with `defineEmits<{...}>()`.
- Guard clicks in handler when `isDisabled` (belt-and-suspenders with CSS).

**Don't:**
- Don't use `defineComponent({})` wrapper — `<script setup>` is preferred.
- Don't use Options API (`data()`, `methods:`, `computed:`).
- Don't concatenate class strings with template literals.
- Don't use `:class="condition ? 'a' : 'b'"` for more than one condition.
- Don't forget `aria-busy` and `aria-disabled` on loading/disabled states.
- Don't use scoped styles — use Tailwind utilities instead.
