# BA II Plus Accessible Calculator — Project Guide

## 1. Project Overview

This project is a **web-based, accessible replica of the Texas Instruments BA II Plus financial calculator**, built specifically for **blind and low-vision users** preparing for or sitting **CFA, FRM and other competitive finance exams**. The CFA Institute and other exam bodies permit the BA II Plus as an approved exam calculator. This app must be functionally equivalent to the physical device so that blind and low-vision candidates can practise with a tool that works seamlessly with screen readers.

### Primary Goals

1. **Full BA II Plus feature parity** — every worksheet and formula from the official TI manual must be implemented and produce results matching the manual's worked examples.
2. **Accessibility-first design** — WCAG 2.1 AA and WAI-ARIA 1.1 compliant. Every element must be usable with a keyboard and screen reader alone.
3. **Professional quality** — the app must look and feel credible enough to present to the CFA Institute. High-contrast amber-on-black design, monospace calculator display, clean typography.
4. **Comprehensive test coverage** — every calculation must be tested against the official TI manual with printed output showing inputs, expected values, and actual results.

---

## 2. Directory Structure

```
accessible_tools/
└── calculators/financial/ba-ii-plus/
    ├── src/
    │   ├── __init__.py
    │   ├── app.py              ← Dash web application (UI + callbacks)
    │   ├── calculator.py       ← Pure Python backend (all calculations)
    │   └── assets/
    │       └── custom.css      ← All styling (Dash auto-loads from assets/)
    └── tests/
        ├── __init__.py         ← Empty — must stay empty
        ├── test_calculator.py  ← Backend calculation tests
        └── test_app.py         ← Integration / logic tests
```

**Critical path rules:**
- `app.py` imports `calculator.py` with `from calculator import FinancialCalculator`
- Tests import with `sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))` at the top of each test file — this is the only path fix needed, no `conftest.py` or `pytest.ini` required
- **Never** use `html.Style()` in `app.py` — it does not exist in Dash 4. All CSS must live in `src/assets/custom.css`
- Run tests from the `ba-ii-plus/` directory: `pytest tests/ -s -q`

---

## 3. Technology Stack

| Component | Technology | Version constraint |
|-----------|-----------|-------------------|
| Web framework | Dash | 4.x |
| Component library | dash-bootstrap-components (dbc) | 2.x |
| Styling | Custom CSS in `assets/custom.css` | — |
| Backend | Pure Python | 3.10+ |
| Testing | pytest | Any modern |
| Date handling | Python `datetime.date` | stdlib |

### Dash 4 Compatibility Rules (Critical)

Dash 4 is stricter than earlier versions. These things **do not work** and will raise `TypeError`:

| Component | Forbidden kwargs |
|-----------|-----------------|
| `dcc.Input` | `aria-*` attributes |
| `dcc.Tabs` | `aria-label` |
| `dbc.Col` | `role`, `aria-labelledby`, `aria-label` |
| `dbc.Row` | `role`, `aria-*` |

**Solution pattern:** Wrap content in `html.Div` when you need ARIA attributes. `html.Div`, `html.Button`, `html.Label`, `html.Header`, `html.Main`, `html.Footer`, `html.H1`–`html.H3`, `html.A`, `html.P`, `html.Span`, `html.Hr` all accept arbitrary HTML attributes including `role` and `aria-*`.

```python
# WRONG — dbc.Col does not accept role in Dash 4
dbc.Col([...], role="group", **{"aria-labelledby": "my-label"})

# RIGHT — wrap content in html.Div
dbc.Col(html.Div([...], role="group", **{"aria-labelledby": "my-label"}))
```

---

## 4. calculator.py — Backend Specification

### 4.1 Module-level function

```python
_effective_period_rate(i_y, p_y, c_y) -> float
```
Converts annual nominal rate to effective rate per payment period using the exact BA II Plus formula:
`r = (1 + I/Y / (100 × C/Y))^(C/Y / P/Y) − 1`

This is **not** the simplified `I/Y / (100 × P/Y)`. The distinction matters when `P/Y ≠ C/Y`.

### 4.2 FinancialCalculator class — state variables

```python
# Basic
self.display, self.last_answer

# Memory — 10 independent slots
self.memories = [0.0] * 10  # M0 through M9

# TVM
self.N, self.I_Y, self.PV, self.PMT, self.FV
self.P_Y = 1.0, self.C_Y = 1.0  # Setting P_Y auto-sets C_Y (per manual)
self.bgn = False  # False=END, True=BGN

# Amortization
self.amort_p1, self.amort_p2

# Cash Flow
self.cf0                    # Initial cash flow (CF0)
self.cash_flows             # list of (amount, frequency) tuples, max 24

# Bond, Depreciation, Statistics, Percent Change, Interest Conversion,
# Profit Margin, Breakeven, Date — all have corresponding state vars
```

### 4.3 Method inventory by worksheet

**Basic Arithmetic**
- `add`, `subtract`, `multiply`, `divide`, `power`, `square_root`, `reciprocal`
- `natural_log`, `exp`, `factorial` (0–69 only), `combination`, `permutation`, `percent_of`, `round_to`

**Memory (M0–M9)**
- `memory_store(slot, value)`, `memory_recall(slot)`, `memory_clear(slot)`, `memory_clear_all()`
- `memory_add(slot, value)`, `memory_subtract(slot, value)`, `memory_multiply(slot, value)`, `memory_divide(slot, value)`

**TVM Worksheet**
- `set_tvm(**kwargs)` — accepts: `N, I_Y, PV, PMT, FV, P_Y, C_Y, bgn`. Setting `P_Y` automatically sets `C_Y` to the same value (matches physical calculator behaviour). Use `C_Y` separately to override.
- `clear_tvm()` — resets to defaults (0s, P/Y=1, C/Y=1, END)
- `compute_FV()`, `compute_PV()`, `compute_PMT()`, `compute_N()`, `compute_I_Y()` — all solve and store result back into the instance
- `get_tvm_status()` → dict with N, I/Y, PV, PMT, FV, P/Y, C/Y, Mode

**Amortization Worksheet**
- `amortization_schedule_simple(p1, p2)` → `{'BAL': float, 'PRN': float, 'INT': float}`
  - Uses rounded PMT (2dp) per BA II Plus convention
  - P1 must be ≥ 1, P2 must be ≥ P1 — raises `ValueError` otherwise
  - PRN and INT are returned as **positive** amounts (magnitude of money flow)

**Cash Flow Worksheet**
- `set_cf0(amount)`, `clear_cash_flows()`
- `add_cash_flow(amount, frequency=1)` — max 24 additional flows, freq 1–9999
- `compute_npv(discount_rate)` — discount_rate is a percentage (e.g. `10.0` means 10%)
- `compute_irr()` — raises `ValueError` if no sign change in cash flows

**Bond Worksheet**
- `compute_bond_price(sdt, cpn, rdt, rv, yld, act, semi)` → `{'PRI': float, 'AI': float}`
- `compute_bond_yield(sdt, cpn, rdt, rv, price, act, semi)` → `float`
- `sdt`/`rdt` are Python `date` objects. `act=True` = ACT/ACT, `False` = 30/360. `semi=True` = 2/Y.

**Depreciation Worksheet**
- `compute_sl_depreciation(cst, sal, lif, m01=1.0)` → list of `{'YR', 'DEP', 'RBV', 'RDV'}`
- `compute_depreciation(method, lif, m01, cst, sal, yr, db_rate=200.0)` → `{'DEP', 'RBV', 'RDV'}`
- Methods: `'SL'`, `'SYD'`, `'DB'`, `'DBX'`

**Statistics Worksheet**
- `add_stat_point(x, y=1.0)` — max 50 points. For 1-var: y is frequency. For 2-var: y is the paired value.
- `clear_stat_data()`
- `compute_1var_stats()` → `{'n', 'mean_x', 'Sx', 'sx', 'sum_x', 'sum_x2'}`
- `compute_2var_stats(method)` → `{'n', 'a', 'b', 'r', 'mean_x', 'mean_y', 'Sx', 'Sy', 'sum_x', 'sum_x2', 'sum_y', 'sum_y2', 'sum_xy'}`
- `predict_y(x_val, method)`, `predict_x(y_val, method)` — regression methods: `'LIN'`, `'Ln'`, `'EXP'`, `'PWR'`

**Interest Conversion Worksheet**
- `nominal_to_effective(nom, c_y)` — NOM% with C/Y compoundings → EFF%
- `effective_to_nominal(eff, c_y)` — EFF% → NOM%

**Percent Change / Compound Interest Worksheet**
- `compute_percent_change(old, new)`, `compute_new_from_pct(old, pct_ch)`, `compute_old_from_pct(new, pct_ch)`
- `compound_interest_new(old, rate, periods)`, `compound_interest_rate(old, new, periods)` — CAGR

**Profit Margin Worksheet**
- `compute_profit_margin(cost, sell)` — gross margin %
- `compute_sell_from_margin(cost, margin)`, `compute_cost_from_margin(sell, margin)`
- `compute_markup(cost, sell)` — markup % (different from margin)

**Breakeven Worksheet**
- `breakeven_quantity(fc, p, vc)` — P=VC raises ValueError
- `breakeven_price(fc, vc, q, pft=0.0)` — Q=0 raises ValueError
- `breakeven_fc(p, vc, q, pft=0.0)`, `breakeven_profit(fc, p, vc, q)`

**Date Worksheet**
- `days_between_dates(dt1, dt2, method='ACT')` — method: `'ACT'` or `'360'`
- `date_add_days(dt, days, method='ACT')` → `date`
- `day_of_week(dt)` → string e.g. `'Monday'`

**Utility**
- `reset_all()` — factory reset, equivalent to "2nd Reset Enter" on physical calculator

---

## 5. app.py — UI Specification

### 5.1 Architecture

- **Framework:** Dash 4 with `dash-bootstrap-components`
- **State management:** `dcc.Store` components (not server-side session state) — `basic-input`, `basic-prev`, `basic-op`, `cf-flows-store`
- **Single global `calc` instance** — `calc = FinancialCalculator()` at module level. This is intentional: the calculator is stateful like the physical device.
- **CSS:** 100% in `src/assets/custom.css`. Dash serves this automatically. Never inject CSS via `html.Style()` (does not exist in Dash 4) or inline `style=` strings for anything that can be a class.

### 5.2 Colour palette (C dict in app.py)

```python
C = {
    "bg":      "#0a0a0a",   # near-black background
    "surface": "#1a1a1a",   # card/panel backgrounds
    "border":  "#555555",   # button borders and dividers (≥3:1 contrast — WCAG 1.4.11)
    "amber":   "#ffb300",   # primary accent — all interactive highlights
    "amber_h": "#cc8f00",   # amber hover state
    "text":    "#f5f5f5",   # primary text (≥18:1 on bg)
    "muted":   "#c0c0c0",   # labels, secondary text (≥7:1 on bg — WCAG AAA)
    "ok":      "#00e676",   # success / result colour
    "err":     "#ff6d6d",   # error colour
    "info":    "#40c4ff",   # informational colour
}
```

**Do not change these values without updating `custom.css` to match.** The palette was chosen to pass WCAG 2.1 AA contrast ratios at every level.

### 5.3 Tab layout (12 worksheets)

| Tab label | `value` | Build function | Callback function |
|-----------|---------|----------------|-------------------|
| Basic Calc | `basic` | `build_basic_tab()` | `basic_calculator()` |
| TVM | `tvm` | `build_tvm_tab()` | `handle_tvm()` |
| Amort | `amort` | `build_amort_tab()` | `handle_amort()` |
| Cash Flow | `cashflow` | `build_cf_tab()` | `handle_cf()` |
| Bond | `bond` | `build_bond_tab()` | `handle_bond()` |
| Depreciation | `dep` | `build_dep_tab()` | `handle_dep()` |
| Statistics | `stats` | `build_stats_tab()` | `handle_stats()` |
| Int. Conv. | `iconv` | `build_iconv_tab()` | `handle_iconv()` |
| % Change | `pctchange` | `build_pct_tab()` | `handle_pct()` |
| Profit Margin | `profit` | `build_profit_tab()` | `handle_profit()` |
| Breakeven | `breakeven` | `build_be_tab()` | `handle_be()` |
| Date | `date` | `build_date_tab()` | `handle_date()` |

### 5.4 Component helpers

```python
ws_input(label_text, input_id, type_="number", placeholder="", value=None, help_text="")
# → html.Div([Label, dcc.Input, help P/Span]) — label association via htmlFor

compute_btn(label, btn_id)   # → amber html.Button with aria-label="Compute: {label}"
clear_btn(label, btn_id)     # → red html.Button
result_div(div_id, placeholder)  # → role="status" aria-live="polite" div

ok(msg)    # → "✓ {msg}"   — prefix for success (colour not sole indicator)
err(msg)   # → "⚠ Error: {msg}"  — prefix for errors
info(msg)  # → "ℹ {msg}"   — prefix for informational messages
_kv(label, value)  # → amort-row div with amort-label / amort-val spans
```

### 5.5 Heading hierarchy (WCAG 2.4.6)

```
h1  — "BA II PLUS" in the page header (one per page)
h2  — Worksheet name at top of each tab, className="section-heading"
h3  — Subsection within a worksheet (e.g. "Settings", "TVM Variables", "Compute")
```

Never use styled `<div>` elements as headings. Always use `html.H2`, `html.H3`.

### 5.6 Live regions

- **`sr-announce`** (`id`): `role="status"`, `aria-live="polite"`, `aria-atomic="true"`. Positioned off-screen via CSS. Updated by every callback to announce results to screen readers.
- **`result_div`** components: also `role="status"`, `aria-live="polite"` — a second announcement channel for the visual result box.
- **Error boxes**: styled with `.error-box` CSS class (red border with extra `border-left: 4px solid` as a non-colour indicator). The `err()` prefix adds `⚠ Error:` text so colour is never the sole indicator of error state.

### 5.7 Skip navigation (WCAG 2.4.1)

```python
html.A("Skip to calculator", href="#main-content", className="skip-nav")
```
This must be the **first element in the DOM** (before the header). It is off-screen by default and becomes visible on focus. The target is `html.Span(id="main-content")` at the top of `html.Main`.

### 5.8 lang attribute (WCAG 3.1.1)

Set via `index_string`:
```python
INDEX_STRING = """<!DOCTYPE html>
<html lang="en">
<head>...</head>
<body>...</body>
</html>"""
```
Pass to `dash.Dash(..., index_string=INDEX_STRING)`.

---

## 6. custom.css — Styling Specification

All CSS lives in `src/assets/custom.css`. Dash loads it automatically — no import needed in Python.

### Key CSS classes

| Class | Purpose |
|-------|---------|
| `.skip-nav` | Off-screen skip link, visible on focus |
| `.calc-display` | Calculator output display — monospace, amber on black |
| `.mode-banner` | Context/mode description below display |
| `.calc-btn` | All calculator buttons — min 48px height (WCAG 2.5.5) |
| `.btn-primary` | Amber compute buttons |
| `.btn-danger` | Red clear/destructive buttons |
| `.ws-card` | Worksheet section container |
| `.result-box` | Green success result area |
| `.error-box` | Red error area (has extra left border for non-colour cue) |
| `.info-box` | Blue informational area |
| `.dash-tab` / `.dash-tab--selected` | Tab strip styling |
| `.amort-row` | Key-value row in result panels |
| `.amort-label` / `.amort-val` | Label and value within amort-row |
| `.app-header` | Page header bar |
| `.section-heading` | h2/h3 within worksheets |
| `.help-text` | Small hint text below inputs |

### Focus indicators (WCAG 2.4.7, Fix 4)

Uses `:focus-visible` instead of `:focus` so keyboard users get a visible 3px amber outline, but mouse users do not see it on every click.

```css
.calc-btn:focus-visible { outline: 3px solid #ffb300; outline-offset: 2px; }
```

---

## 7. Test Suite Specification

### 7.1 Running tests

```bash
# From ba-ii-plus/ directory:
pytest tests/test_calculator.py -s -q   # calculator backend
pytest tests/test_app.py -s -q          # integration/logic

# The -s flag is REQUIRED — it disables output capture so print() calls appear
# Without -s you will see no output from the custom print helpers
```


### 7.2 Test sections

**test_calculator.py** (103 calculator tests + 1 summary):
1. Basic Arithmetic — 19 tests
2. Memory Operations — 8 tests
3. Effective Period Rate — 6 tests
4. TVM Worksheet — 21 tests (manual examples pp.26–38)
5. Amortization Worksheet — 5 tests
6. Cash Flow NPV/IRR — 8 tests
7. Interest Conversion — 5 tests
8. Percent Change — 6 tests
9. Profit Margin — 7 tests
10. Breakeven — 6 tests
11. Depreciation Worksheet — 8 tests
12. Statistics Worksheet — 12 tests
13. Date Worksheet — 4 tests
14. Bond Worksheet — 5 tests
15. Edge Cases & Reset — 8 tests

**test_app.py** (128 integration tests + 1 summary):
Same 15 sections but tests the logic as accessed through the UI layer, with additional tests for state isolation, independence between worksheets, and edge cases from the app perspective.

### 7.3 Key test patterns

```python
# Every test file starts with the sys.path fix:
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Helper functions (defined at top of each test file):
_section(name)           # prints section header, initialises results dict
_check(label, actual, expected, tol=None, detail="")  # asserts and prints
_check_raises(label, exc_type, fn, *args)              # asserts exception
_record(label, passed, detail="")                      # manual pass/fail record
_print_summary()         # prints the final summary table
```

---

## 8. Accessibility Compliance Summary

This project targets **WCAG 2.1 AA** and **WAI-ARIA 1.1**. The following specific fixes have been implemented and must be preserved:

| Fix | Standard | What was done |
|-----|----------|---------------|
| Fix 1 | WCAG 3.1.1 (A) | `lang="en"` on `<html>` via `index_string` |
| Fix 2 | WAI-ARIA Rule 2 | Display div uses `role="status"` not `role="textbox"` |
| Fix 3 | WCAG 2.4.6 (AA) | Semantic `h1/h2/h3` heading hierarchy throughout |
| Fix 4 | WAI-ARIA 1.1 | `role="status"` + `aria-live="polite"` for results (not "assertive") |
| Fix 5 | WCAG 1.4.1 (A) | `✓`/`⚠ Error:` text prefixes — colour is never the sole indicator |
| Fix 6 | WCAG 1.4.11 (AA) | Button borders `#555555` (~3.6:1), muted text `#c0c0c0` (~7:1) |
| Fix 7 | WCAG 2.4.1 (A) | Skip-nav link as first DOM element → `#main-content` |
| Fix 8 | WAI-ARIA Rule 5 | Help text via `htmlFor`; `role="group"` on radio groups in `html.Div` |

**Remaining known limitation:** `dcc.Input` in Dash 4 does not accept `aria-describedby`. The workaround is `htmlFor` on `<label>` for the accessible name, and the help text paragraph has an `id` that is available for future upgrade when Dash supports it. The label association via `htmlFor` is sufficient for WCAG A conformance.

---

## 9. Known Issues and Decisions

### Decisions already made — do not revisit without user instruction

1. **Single global `calc` instance** — intentional. Reflects physical calculator behaviour. Do not refactor to per-session state.

2. **`dcc.Input` for all worksheet inputs** — Dash 4 does not allow ARIA kwargs on `dcc.Input`. Do not replace with `html.Input` (does not exist in Dash 4).

3. **Bond pricing implementation** — the `compute_bond_price` function computes correctly for the fundamental bond pricing relationships (premium/discount direction, monotonicity) but may differ slightly from the physical calculator's exact 30/360 coupon date walk in edge cases. Tests verify fundamental properties rather than exact values.

4. **`amortization_schedule_simple`** — PRN and INT are returned as positive values (magnitudes). The physical calculator displays them as negative outflows. The app formats them with `$` prefix. Do not change the sign convention in `calculator.py`.

5. **EXP regression coefficient `b`** — in our implementation, `b` is the slope in log-y space (= 1 for `y = 2·eˣ`), not the base `e`. This matches the standard linear regression in log space and is mathematically correct.

6. **`2024-01-01 + 365 days ≠ 2025-01-01`** — 2024 is a leap year (366 days). Tests reflect this.

7. **CSS in `assets/` not `html.Style()`** — `html.Style` does not exist in Dash 4. All styling is in `src/assets/custom.css`.

8. **Tab CSS classes** — `dcc.Tab` uses `className="dash-tab"` and `selected_className="dash-tab--selected"`. These are overridden in `custom.css`.

### Open items / future work

- Bond worksheet: exact match to TI manual p.56 example (settle 6/12/2006, redeem 12/31/2007, 30/360, 8% yield → PRI=98.56). Current implementation has a ~3 point discrepancy due to coupon date reconstruction in 30/360 convention.
- No `conftest.py` or `pytest.ini` currently — just the sys.path line in each test file.
- No end-to-end browser tests (would require selenium/chromedriver).
- `dcc.Input` `aria-describedby` — when Dash 4 adds support, add to `ws_input()` helper.

---

## 10. Manual Reference — Key Worked Examples

These are the canonical expected values from the official TI BA II Plus guidebook. Tests are written against these.

| Worksheet | Example | Inputs | Expected output |
|-----------|---------|--------|----------------|
| TVM | Monthly PMT [p.27] | N=360, I/Y=5.5, PV=75000, FV=0, P/Y=12 | PMT = −425.84 |
| TVM | Annual FV [p.28] | N=20, I/Y=0.5, PV=−5000, PMT=0, P/Y=1 | FV = 5524.48 |
| TVM | Annuity END [p.29] | N=10, I/Y=10, PMT=−20000, FV=0, END | PV = 122891.34 |
| TVM | Annuity BGN [p.29] | Same but BGN | PV = 135180.48 |
| TVM | Monthly savings [p.35] | N=240, I/Y=7.5, PMT=−200, BGN, P/Y=12 | FV = 111438.31 |
| TVM | Mortgage [p.38] | N=360, I/Y=6.125, PV=120000, P/Y=12 | PMT = −729.13 |
| Amort | Year 1 [p.39] | Above mortgage, P1=1, P2=9 | BAL=118928.63, INT=5490.80 |
| Amort | Balloon [p.40] | $82000, 7%, 30yr, P1=1, P2=60 | BAL=77187.72 |
| Cash Flow | NPV [p.48] | CF0=−7000, C01=3000, C02=4000, C03=5000×4, I=20% | NPV=7266.44 |
| Cash Flow | IRR [p.49] | Same cash flows | IRR≈52.71% |
| Depreciation | SL [p.62] | $1M, 31.5yr, M01=3.5 | Yr1 DEP=25132.28, RBV=974867.72 |
| Depreciation | SL [p.62] | Same | Yr2 DEP=31746.03, RBV=943121.69 |
| % Change | Increase [p.70] | OLD=658, NEW=700 | %CH=+6.38% |
| % Change | CAGR [p.70] | OLD=500, NEW=750, #PD=5 | %CH=8.45% |

**Note on Cash Flow example:** The manual shows an editing exercise where $4000 is moved from year 6 to year 2. The test uses the *edited* version: CF0=−7000, C01=3000, C02=4000 (F=1), C03=5000 (F=4). This produces NPV=7266.44 at 20%.

---

## 11. How to Work on This Project

### When adding a new feature

1. Add the calculation method to `calculator.py` with full type hints and a docstring stating the formula source.
2. Add tests in `test_calculator.py` using `_section()` / `_check()` / `_check_raises()` helpers. Reference the manual page if applicable.
3. If it requires UI, add or update the relevant tab in `app.py` following the existing patterns. Keep CSS in `custom.css`.
4. Add corresponding integration tests in `test_app.py`.
5. Run `pytest tests/ -s -q` and confirm 100% pass rate with visible output.

### When fixing a bug

1. Write a failing test first that reproduces the bug.
2. Fix in `calculator.py` (backend bugs) or `app.py` (UI/callback bugs).
3. Confirm the test now passes.
4. Confirm no other tests broke.

### When changing styling

1. Only edit `src/assets/custom.css`.
2. Never add `style=` inline props unless absolutely necessary (one-off layout values like `margin-left: 12px`).
3. Do not change the colour hex values in `custom.css` without also updating the `C` dict in `app.py` (used for inline style props that cannot be done via class).
4. Verify contrast ratios if changing any text or border colour: text must be ≥4.5:1, UI components ≥3:1.

---

## 12. Quick Reference — File Locations

| File | Destination in project | Purpose |
|------|----------------------|---------|
| `app.py` | `src/app.py` | Dash web application |
| `calculator.py` | `src/calculator.py` | All financial calculations |
| `custom.css` | `src/assets/custom.css` | All styling |
| `test_calculator.py` | `tests/test_calculator.py` | Backend tests |
| `test_app.py` | `tests/test_app.py` | Integration tests |
| `PROJECTGUIDE.md` | `.github/PROJECTGUIDE.md` | Detailed project guide |
