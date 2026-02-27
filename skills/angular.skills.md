# Angular Skills - FlowBridge.ai

## Framework Identity
- **Name:** Angular
- **Version:** 17+ (Standalone Components, Signal APIs)
- **Language:** TypeScript
- **File extension:** `.component.ts` + `.component.html` (or inline template)
- **Styling:** Tailwind CSS v3 (applied via `[class]` or `[ngClass]`)
- **State management:** Angular Signals (`signal`, `computed`, `effect`)
- **Icon library:** `@ng-icons/core` + `@ng-icons/lucide`
- **Animation:** Angular Animations or Tailwind animate

---

## Component File Structure

```typescript
// button.component.ts
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  input,
  output,
} from "@angular/core";
import { CommonModule } from "@angular/common";
import { NgIconComponent, provideIcons } from "@ng-icons/core";
import { lucideLoader2 } from "@ng-icons/lucide";

export type ButtonVariant = "primary" | "secondary" | "ghost";
export type ButtonSize = "sm" | "md" | "lg";

@Component({
  selector: "app-button",
  standalone: true,                             // ALWAYS standalone: true
  imports: [CommonModule, NgIconComponent],
  providers: [provideIcons({ lucideLoader2 })],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button
      [class]="buttonClasses()"
      [disabled]="isDisabledSignal()"
      [attr.aria-disabled]="isDisabledSignal()"
      [attr.aria-busy]="isLoading()"
      (click)="handleClick($event)"
    >
      @if (isLoading()) {
        <ng-icon name="lucideLoader2" class="h-4 w-4 animate-spin" aria-hidden="true" />
      }
      @if (!isLoading()) {
        <ng-content select="[slot=icon]" />
      }
      <ng-content />
    </button>
  `,
})
export class ButtonComponent {
  // Signal inputs (Angular 17+)
  variant = input<ButtonVariant>("primary");
  size = input<ButtonSize>("md");
  isLoading = input<boolean>(false);
  disabled = input<boolean>(false);

  // Outputs
  clicked = output<MouseEvent>();

  // Derived signals
  isDisabledSignal = computed(() => this.disabled() || this.isLoading());

  buttonClasses = computed(() => {
    const base = [
      "inline-flex items-center justify-center gap-2 rounded-lg",
      "text-sm font-semibold tracking-wide",
      "transition-all duration-200",
      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
    ].join(" ");

    const variantMap: Record<ButtonVariant, string> = {
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

    const sizeMap: Record<ButtonSize, string> = {
      sm: "px-3 py-1.5 text-xs rounded-md",
      md: "px-5 py-2.5 text-sm rounded-lg",
      lg: "px-7 py-3.5 text-base rounded-xl",
    };

    const disabledClasses = this.isDisabledSignal()
      ? "opacity-50 cursor-not-allowed pointer-events-none"
      : "";

    return [base, variantMap[this.variant()], sizeMap[this.size()], disabledClasses]
      .filter(Boolean)
      .join(" ");
  });

  handleClick(event: MouseEvent): void {
    if (!this.isDisabledSignal()) {
      this.clicked.emit(event);
    }
  }
}
```

---

## Import Patterns

```typescript
// Angular core — signals
import {
  Component,
  ChangeDetectionStrategy,
  computed,
  input,
  output,
  signal,
  effect,
} from "@angular/core";

// Template directives
import { CommonModule } from "@angular/common";

// Icons
import { NgIconComponent, provideIcons } from "@ng-icons/core";
import { lucideLoader2, lucideChevronRight } from "@ng-icons/lucide";
```

---

## Styling Approach

- Apply classes via `[class]="computedSignal()"` binding on the host element.
- For conditional classes on internal elements, use `[class.active]="condition"` or `[ngClass]`.
- **State prefixes:** `hover:`, `focus-visible:`, `active:`, `disabled:`.
- **Color tokens:**
  - Primary: `bg-indigo-500` → hover: `bg-indigo-600`
  - Disabled: `opacity-50 cursor-not-allowed pointer-events-none`
  - Focus ring: `focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2`
  - Hover glow: `hover:shadow-[0_8px_20px_rgba(99,102,241,0.5)]`
- Build class strings in a `computed()` signal — never in the template expression.

---

## State and Prop Patterns

### Signal inputs
```typescript
// Required input
label = input.required<string>();

// Optional input with default
variant = input<ButtonVariant>("primary");

// Boolean input
isLoading = input<boolean>(false);
```

### Computed derived state
```typescript
isDisabledSignal = computed(() => this.disabled() || this.isLoading());
```

### Control flow (@if, @for — Angular 17+)
```html
@if (isLoading()) {
  <ng-icon name="lucideLoader2" class="animate-spin" />
} @else {
  <ng-content />
}
```

### Output events
```typescript
clicked = output<MouseEvent>();
// Emit:
this.clicked.emit(event);
```

---

## Naming Conventions

| Construct | Convention | Example |
|-----------|-----------|---------|
| Component class | PascalCase + `Component` | `ButtonComponent` |
| Selector | `app-` prefix + kebab | `app-button` |
| Input signals | camelCase | `isLoading`, `variant` |
| Output signals | past-tense verb | `clicked`, `submitted` |
| Computed signals | camelCase | `buttonClasses`, `isDisabledSignal` |
| Type unions | PascalCase | `ButtonVariant`, `ButtonSize` |
| File names | kebab-case | `button.component.ts` |

---

## Accessibility Requirements

```html
<button
  [disabled]="isDisabledSignal()"
  [attr.aria-disabled]="isDisabledSignal()"
  [attr.aria-busy]="isLoading()"
>
```

- Use `[attr.aria-*]` for dynamic ARIA attributes (not `[aria-*]`).
- `<button>` handles Enter and Space keyboard events natively.
- Focus ring: Add `focus-visible:ring-*` Tailwind classes.
- `aria-hidden="true"` on spinner icons via `aria-hidden` attribute.
- When `isLoading()` is true: `aria-busy="true"` + `disabled="true"`.

---

## Reference Example

```typescript
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  input,
  output,
} from "@angular/core";
import { NgIconComponent, provideIcons } from "@ng-icons/core";
import { lucideLoader2 } from "@ng-icons/lucide";

export type ButtonVariant = "primary" | "secondary" | "ghost";
export type ButtonSize = "sm" | "md" | "lg";

@Component({
  selector: "app-button",
  standalone: true,
  imports: [NgIconComponent],
  providers: [provideIcons({ lucideLoader2 })],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button
      [class]="buttonClasses()"
      [disabled]="isDisabledSignal()"
      [attr.aria-disabled]="isDisabledSignal()"
      [attr.aria-busy]="isLoading()"
      (click)="handleClick($event)"
    >
      @if (isLoading()) {
        <ng-icon
          name="lucideLoader2"
          class="h-4 w-4 animate-spin"
          aria-hidden="true"
        />
        <span class="sr-only">Loading</span>
      }
      @if (!isLoading()) {
        <ng-content select="[slot=icon]" />
        <ng-content />
      }
    </button>
  `,
})
export class ButtonComponent {
  variant = input<ButtonVariant>("primary");
  size = input<ButtonSize>("md");
  isLoading = input<boolean>(false);
  disabled = input<boolean>(false);

  clicked = output<MouseEvent>();

  isDisabledSignal = computed(() => this.disabled() || this.isLoading());

  buttonClasses = computed(() => {
    const base =
      "inline-flex items-center justify-center gap-2 rounded-lg text-sm font-semibold tracking-wide transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2";

    const variants: Record<ButtonVariant, string> = {
      primary:
        "bg-indigo-500 text-white hover:bg-indigo-600 hover:shadow-[0_8px_20px_rgba(99,102,241,0.5)] focus-visible:ring-indigo-500 active:scale-[0.98]",
      secondary:
        "bg-white text-indigo-600 border border-indigo-300 hover:bg-indigo-50 focus-visible:ring-indigo-400",
      ghost:
        "text-indigo-600 hover:bg-indigo-50 focus-visible:ring-indigo-400",
    };

    const sizes: Record<ButtonSize, string> = {
      sm: "px-3 py-1.5 text-xs rounded-md",
      md: "px-5 py-2.5 rounded-lg",
      lg: "px-7 py-3.5 text-base rounded-xl",
    };

    const disabled = this.isDisabledSignal()
      ? "opacity-50 cursor-not-allowed pointer-events-none"
      : "";

    return [base, variants[this.variant()], sizes[this.size()], disabled]
      .filter(Boolean)
      .join(" ");
  });

  handleClick(event: MouseEvent): void {
    if (!this.isDisabledSignal()) {
      this.clicked.emit(event);
    }
  }
}
```

---

## Do / Don't Rules

**Do:**
- Always use `standalone: true` — no NgModule required.
- Use Signal inputs (`input()`) and outputs (`output()`) — not `@Input()` / `@Output()`.
- Use `computed()` for derived state — not getters.
- Use `ChangeDetectionStrategy.OnPush` always.
- Use Angular 17+ control flow (`@if`, `@for`, `@switch`) — not `*ngIf` / `*ngFor`.
- Use `[attr.aria-*]` for ARIA attribute bindings.
- Build class strings in `computed()` signals, not in the template.

**Don't:**
- Don't use `@Input()` / `@Output()` decorators — use signal APIs.
- Don't use `*ngIf` or `*ngFor` — use `@if` / `@for`.
- Don't use `NgModule` — keep components standalone.
- Don't use `ngClass` with complex objects in the template — build in `computed()`.
- Don't add `role="button"` to a native `<button>`.
- Don't skip `ChangeDetectionStrategy.OnPush`.
