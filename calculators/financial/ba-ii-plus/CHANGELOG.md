# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows semantic versioning intent.

## [0.1.0] - 2026-02-19

### Added

- Initial accessible BA II Plus web application built with Python + Dash 4
- 12 worksheet implementations:
  - TVM
  - Amortization
  - Cash Flow (NPV/IRR)
  - Bond
  - Depreciation
  - Statistics
  - Interest Conversion
  - Percent Change
  - Profit Margin
  - Breakeven
  - Date
  - Memory
- WCAG 2.1 AA-aligned accessibility implementation
- WAI-ARIA 1.1 semantics and live-region behavior
- Full test suite totaling **231 tests**:
  - 103 backend tests (`tests/test_calculator.py`)
  - 128 app/integration tests (`tests/test_app.py`)

### Fixed

- Accessibility/ARIA audit fixes (8-item set):
  - `lang="en"` set via Dash `index_string`
  - Display switched to `role="status"` (from textbox-like behavior)
  - Semantic heading hierarchy standardized (`h1`/`h2`/`h3`)
  - Result messages made polite live status updates
  - Success/error text prefixes added (`✓`, `⚠`) so state is not color-only
  - Button border contrast increased (`#555555`) for non-text contrast support
  - Skip navigation link added at top of DOM flow
  - Radio groups wrapped with `role="group"` and `aria-labelledby`

### Known Issues

- Bond worksheet can differ slightly from exact TI manual display values in some scenarios (approximation currently documented).
- Dash 4 `dcc.Input` has a known limitation around direct `aria-describedby` support.
