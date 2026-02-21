# Architecture Overview

## Core design principle

The project intentionally separates:

- `src/calculator.py` — formula engine, pure Python, no UI dependencies
- `src/app.py` — Dash UI layout, callback orchestration, ARIA semantics

This split is deliberate so formula correctness can be validated independently from rendering and browser behavior.

## Why separation matters

1. **Testability:** backend formulas are deterministic and easy to unit test.
2. **Reliability:** UI regressions do not require rewriting financial logic.
3. **Reusability:** `calculator.py` can be imported by CLI tools, notebooks, or alternate front ends.
4. **Auditability:** formula source can be reviewed against TI manual examples without UI noise.

## Dash 4 compatibility constraints and workarounds

### Constraint: avoid inline style blocks

- Pattern: do not use `html.Style()` for runtime CSS injection.
- Workaround: all style rules live in `src/assets/custom.css` (auto-loaded by Dash).

### Constraint: ARIA on `dbc.*` wrappers

- Pattern: some `dash-bootstrap-components` primitives are not ideal ARIA hosts.
- Workaround: apply ARIA attributes on `html.*` wrapper elements where semantics are explicit.

### Constraint: `dcc.Input` helper text linkage

- Pattern: `aria-describedby` support is limited for `dcc.Input` in Dash 4 contexts.
- Workaround: keep visible helper text adjacent and preserve explicit labels.

## ARIA implementation decisions

- **Display as status region:** calculator display uses `role="status"` so updates are announced naturally and not treated as editable input.
- **Result live regions:** compute outputs are `role="status"` with `aria-live="polite"` and atomic updates.
- **Grouped controls:** radio groups wrapped with `role="group"` + `aria-labelledby`.
- **Skip link:** top-of-DOM bypass mechanism for repeated content.
- **Semantic headings:** worksheet structure is discoverable by heading navigation in screen readers.

## Color system and contrast

Palette is defined to preserve dark-theme readability and non-text contrast:

| Token | Value | Usage | Contrast notes |
|---|---|---|---|
| Background | `#0a0a0a` | app background | supports high-contrast text |
| Surface | `#1a1a1a` | cards/panels | separates containers on dark theme |
| Text | `#f5f5f5` | primary body text | high contrast on dark surfaces |
| Muted | `#c0c0c0` | labels/help text | readable secondary text |
| Accent | `#ffb300` | headings/focus/highlights | strong contrast on dark backgrounds |
| Border | `#555555` | button and panel outlines | ~3.6:1 non-text contrast target |
| Success | `#00e676` | success status | paired with ✓ text indicator |
| Error | `#ff6d6d` | error status | paired with ⚠ text indicator |
| Info | `#40c4ff` | informational messages | distinct from success/error hues |

## Financial sign convention

The app uses BA II Plus-compatible cash-flow sign convention:

- **Outflows** (money paid) are negative.
- **Inflows** (money received) are positive.

This convention is maintained consistently across TVM, cash-flow, amortization, and related worksheets.

## Single global calculator instance

`app.py` uses a single global `calc` instance intentionally.

Why this is acceptable for this project:

- Dash callbacks need shared worksheet state similar to physical calculator memory behavior.
- Memory slots and mode state are easier to model with a persistent object.
- The deterministic backend and test coverage reduce risk of hidden state regressions.

If future multi-user isolation is required, state can be moved to per-session storage with minimal changes to `calculator.py`.
