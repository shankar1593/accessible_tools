# Accessibility Statement

This project targets **WCAG 2.1 AA** conformance and **WAI-ARIA 1.1** patterns for all implemented user flows in the BA II Plus web interface. The application is designed screen-reader-first, with semantic structure, keyboard operation, and live announcements for computed results.

## WCAG 2.1 criteria addressed

The following success criteria are explicitly addressed in current implementation:

### Perceivable

- **1.1.1 Non-text Content (A):** Controls and interactive elements expose accessible names via labels/ARIA labels.
- **1.3.1 Info and Relationships (A):** Semantic heading hierarchy (`h1`/`h2`/`h3`), grouped controls, and explicit label association.
- **1.3.2 Meaningful Sequence (A):** Logical DOM order, including skip navigation as first actionable element.
- **1.3.3 Sensory Characteristics (A):** Instructions do not rely only on visual position, shape, or color.
- **1.4.1 Use of Color (A):** State is not conveyed by color alone; text prefixes/symbols are used (✓, ⚠).
- **1.4.3 Contrast (Minimum) (AA):** Text colors selected to meet or exceed minimum contrast ratios.
- **1.4.11 Non-text Contrast (AA):** Interactive boundaries (e.g., button borders `#555555`) maintain non-text contrast.

### Operable

- **2.1.1 Keyboard (A):** All controls are reachable and operable via keyboard.
- **2.1.2 No Keyboard Trap (A):** Focus can move in and out of all controls.
- **2.4.1 Bypass Blocks (A):** Skip link provided at top of DOM.
- **2.4.3 Focus Order (A):** Focus follows interface reading and workflow order.
- **2.4.6 Headings and Labels (AA):** Headings and labels describe purpose clearly.
- **2.4.7 Focus Visible (AA):** Visible focus styles for interactive controls.
- **2.5.5 Target Size (AAA advisory but implemented):** Controls use touch-friendly minimum heights.

### Understandable

- **3.2.2 On Input (A):** Input does not trigger unexpected context changes.
- **3.3.2 Labels or Instructions (A):** Worksheet fields include clear labels and helper text.

### Robust

- **4.1.2 Name, Role, Value (A):** Roles/states are set for status regions and grouped controls.
- **4.1.3 Status Messages (AA):** Result and display announcements use polite live regions.

## 8 specific fixes implemented

1. Set `lang="en"` at document root using Dash `index_string`.
2. Calculator display uses `role="status"` (not `role="textbox"`).
3. Enforced semantic heading hierarchy with real `h1`/`h2`/`h3` elements.
4. Result areas use `role="status"` with `aria-live="polite"` and atomic announcements.
5. Added text prefixes (`✓` success, `⚠` error) so color is not the sole indicator.
6. Standardized button borders (`#555555`) to satisfy non-text contrast expectations.
7. Added skip navigation link as the first focusable DOM element.
8. Wrapped radio groups with `role="group"` + `aria-labelledby`.

## Known remaining accessibility gap

- **Dash 4 limitation:** `dcc.Input` does not currently expose `aria-describedby` as expected for direct helper-text linking in all cases.

## Screen reader testing status

Manual testing has been performed with:

- NVDA (Windows)
- JAWS (Windows)
- VoiceOver (macOS)

Additional community verification across versions and browsers is strongly encouraged.

## Reporting accessibility bugs

Please open a GitHub issue and include:

- Screen reader name and version
- Browser and version
- OS version
- Worksheet/page and exact control
- Steps to reproduce
- Expected spoken output vs actual spoken output

Use the bug template and mark the issue as accessibility-specific.
