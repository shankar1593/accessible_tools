# Formula Verification Matrix

This document maps each worksheet to TI BA II Plus guidebook references and the matching validation cases in the test suite.

- Primary validation files: `tests/test_calculator.py` and `tests/test_app.py`
- Test strategy: compare against manual examples where published; otherwise verify identity/properties and internal consistency
- Output notation: “Pass” means expected value matched within tolerance in the suite

| Worksheet | TI Manual Pages | Formula / Method Verified | Expected Output | Actual Output (Suite) |
|---|---:|---|---|---|
| TVM | p.26–38 | Standard TVM solve functions (`N`, `I/Y`, `PV`, `PMT`, `FV`) using effective period rate from `P/Y` + `C/Y` | Example: PMT for `N=360, I/Y=5.5, PV=75000` is `-425.84` | Pass (within tolerance, backend + app tests) |
| Amortization | p.39–41 | Period-by-period amortization roll-forward using computed `PMT` and periodic rate | Example: `BAL≈118928.63`, `INT≈5490.80` for periods 1–9 (manual mortgage example) | Pass (within tolerance) |
| Cash Flow (NPV/IRR) | p.47–49 | Discounted cash flow summation and numerical IRR root solve | Edited manual case: `NPV≈7266.44` at 20%; `IRR≈52.71%` | Pass (within tolerance) |
| Bond | p.56–57 | Coupon bond pricing + accrued interest under day-count and semiannual options | Core properties: par when coupon=yield, premium/discount monotonic behavior | Pass for property tests; known approximation gap vs exact manual display |
| Depreciation (SL) | p.62 | Straight-line schedule with life, salvage, and first-year month convention (`M01`) | Example: `DEP1≈25132.28`, `RBV1≈974867.72` | Pass (within tolerance) |
| Depreciation (DBX) | p.85 | Declining-balance method with crossover behavior and period updates | Expected schedule behavior per DBX method | Pass (method tests) |
| Statistics (1-Var / 2-Var) | p.95–98 | Mean, standard deviation, linear and exponential regression stats | Example: perfect linear set gives `a=1`, `b=2`, `r≈1` | Pass |
| Interest Conversion | p.104–105 | `NOM ↔ EFF` conversion: `EFF=(1+NOM/CY)^CY-1` and inverse | Example: `NOM=5, CY=12` gives `EFF≈5.1162%` | Pass |
| Percent Change | p.70 | `%Δ`, old/new value transforms, and CAGR/compound rate solve | Example: `658→700 = +6.38%`; `500→750 in 5y = 8.45%` | Pass |
| Profit Margin | p.108–109 | Margin/markup identities and reverse solves for cost/sell | Example: cost `100`, sell `125` => margin `20%`, markup `25%` | Pass |
| Breakeven | p.110–111 | Contribution formulas for quantity, price, fixed cost, and profit | Example: `FC=10000, P=50, VC=30 => Q=500` | Pass |
| Date | p.107 | Date arithmetic: ACT and 30/360 day-count, date add, weekday | Example: Jan 1 to Jul 1 under 30/360 => `180` days | Pass |

## Notes on bond worksheet

The current implementation is intentionally transparent about one known limitation: certain bond outputs are close but not always bit-for-bit identical to BA II Plus display values from manual examples around p.56–57. Existing tests therefore validate financial correctness and directional properties while this parity work remains open.

## Reproducibility

Run full verification suite from project root:

```bash
pytest tests/ -s -q
```

Use `-s` to preserve the printed pass/fail and summary output.
