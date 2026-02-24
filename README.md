# Accessible Tools

Open-source tools built for blind and low-vision users — designed to be fully usable with screen readers and keyboard navigation.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](calculators/financial/ba-ii-plus/LICENSE)
[![WCAG 2.1 AA](https://img.shields.io/badge/WCAG-2.1%20AA-6f42c1)](https://www.w3.org/TR/WCAG21/)

## Quick start

All projects in this repository share a single virtual environment at the repository root:

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Always activate `.venv` before running any project or its tests.

## Projects

### [BA II Plus Accessible Calculator](calculators/financial/ba-ii-plus/)

A screen-reader-first, web-based replica of the Texas Instruments BA II Plus financial calculator for CFA, FRM and other competitive finance exam preparation.

- 12 BA II Plus worksheets (TVM, Amortization, Cash Flow, Bond, Depreciation, Statistics and more)
- WCAG 2.1 AA + WAI-ARIA 1.1 compliant
- Built with Dash 4 and pure Python

## Contributing

Contributions are welcome — especially from screen reader users and accessibility advocates. See the [contributing guide](calculators/financial/ba-ii-plus/CONTRIBUTING.md) for details.

## License

[MIT](calculators/financial/ba-ii-plus/LICENSE)
