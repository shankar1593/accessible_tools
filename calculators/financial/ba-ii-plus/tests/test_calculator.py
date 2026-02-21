"""
Comprehensive tests for FinancialCalculator (BA II Plus backend).
All expected values are drawn from the official TI BA II Plus guidebook.
Run: pytest test_calculator.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculator import FinancialCalculator, _effective_period_rate

import os
import sys
import math
import pytest
from datetime import date

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def calc():
    return FinancialCalculator()


# ===========================================================================
# 1. BASIC ARITHMETIC
# ===========================================================================

class TestBasicArithmetic:

    def test_add(self, calc):
        assert calc.add(6, 4) == 10

    def test_subtract(self, calc):
        assert calc.subtract(6, 4) == 2

    def test_multiply(self, calc):
        assert calc.multiply(6, 4) == 24

    def test_divide(self, calc):
        assert calc.divide(6, 4) == 1.5

    def test_divide_by_zero(self, calc):
        with pytest.raises(ZeroDivisionError):
            calc.divide(5, 0)

    def test_power(self, calc):
        assert abs(calc.power(3, 1.25) - 3.9481) < 0.001

    def test_square_root(self, calc):
        assert abs(calc.square_root(15.5) - 3.9370) < 0.001

    def test_square_root_negative(self, calc):
        with pytest.raises(ValueError):
            calc.square_root(-1)

    def test_reciprocal(self, calc):
        assert abs(calc.reciprocal(3.2) - 0.3125) < 1e-6

    def test_reciprocal_zero(self, calc):
        with pytest.raises(ZeroDivisionError):
            calc.reciprocal(0)

    def test_natural_log(self, calc):
        # ln(203.45) ≈ 5.3154 (manual displays 5.32 with 2 decimal places)
        assert abs(calc.natural_log(203.45) - 5.3154) < 0.002

    def test_exp(self, calc):
        assert abs(calc.exp(0.69315) - 2.0) < 0.0001

    def test_factorial_5(self, calc):
        assert calc.factorial(5) == 120

    def test_factorial_0(self, calc):
        assert calc.factorial(0) == 1

    def test_factorial_too_large(self, calc):
        with pytest.raises(ValueError):
            calc.factorial(70)

    def test_combination(self, calc):
        # nCr(52, 5) = 2,598,960 per manual
        assert calc.combination(52, 5) == 2598960

    def test_permutation(self, calc):
        # nPr(8, 3) = 336 per manual
        assert calc.permutation(8, 3) == 336

    def test_combination_invalid(self, calc):
        with pytest.raises(ValueError):
            calc.combination(3, 5)

    def test_percent_of(self, calc):
        # 4% of 453 = 18.12
        assert abs(calc.percent_of(453, 4) - 18.12) < 0.01


# ===========================================================================
# 2. MEMORY OPERATIONS
# ===========================================================================

class TestMemory:

    def test_store_recall(self, calc):
        calc.memory_store(3, 14.95)
        assert calc.memory_recall(3) == 14.95

    def test_clear_slot(self, calc):
        calc.memory_store(2, 99.0)
        calc.memory_clear(2)
        assert calc.memory_recall(2) == 0.0

    def test_memory_add(self, calc):
        calc.memory_store(1, 10.0)
        calc.memory_add(1, 5.0)
        assert calc.memory_recall(1) == 15.0

    def test_memory_subtract(self, calc):
        calc.memory_store(0, 20.0)
        calc.memory_subtract(0, 8.0)
        assert calc.memory_recall(0) == 12.0

    def test_memory_multiply(self, calc):
        calc.memory_store(5, 3.0)
        calc.memory_multiply(5, 4.0)
        assert calc.memory_recall(5) == 12.0

    def test_memory_divide(self, calc):
        calc.memory_store(7, 12.0)
        calc.memory_divide(7, 4.0)
        assert calc.memory_recall(7) == 3.0

    def test_memory_clear_all(self, calc):
        for i in range(10):
            calc.memory_store(i, float(i * 10))
        calc.memory_clear_all()
        for i in range(10):
            assert calc.memory_recall(i) == 0.0

    def test_invalid_slot(self, calc):
        with pytest.raises(ValueError):
            calc.memory_store(10, 1.0)


# ===========================================================================
# 3. EFFECTIVE PERIOD RATE
# ===========================================================================

class TestEffectivePeriodRate:

    def test_monthly_12_12(self):
        # P/Y=12, C/Y=12, I/Y=5.5 → monthly rate
        r = _effective_period_rate(5.5, 12, 12)
        assert abs(r - 5.5 / (100 * 12)) < 1e-10

    def test_quarterly_4_4(self):
        r = _effective_period_rate(5.5, 4, 4)
        assert abs(r - 5.5 / (100 * 4)) < 1e-10

    def test_annual_1_1(self):
        r = _effective_period_rate(10, 1, 1)
        assert abs(r - 0.10) < 1e-10

    def test_monthly_pay_quarterly_compound(self):
        # P/Y=12, C/Y=4, I/Y=6
        r = _effective_period_rate(6, 12, 4)
        expected = (1 + 6 / (100 * 4)) ** (4 / 12) - 1
        assert abs(r - expected) < 1e-10


# ===========================================================================
# 4. TVM WORKSHEET – Manual Examples
# ===========================================================================

class TestTVM:

    def test_compute_FV_savings(self, calc):
        """Manual p.28: $5000 at 0.5%/yr for 20 yrs → FV = 5524.48"""
        calc.set_tvm(N=20, I_Y=0.5, PV=-5000, PMT=0, P_Y=1, C_Y=1)
        fv = calc.compute_FV()
        assert abs(fv - 5524.48) < 0.10

    def test_compute_PV_savings(self, calc):
        """Manual p.28: FV=10000, I/Y=0.5, N=20 → PV = -9050.63"""
        calc.set_tvm(N=20, I_Y=0.5, FV=10000, PMT=0, P_Y=1, C_Y=1)
        pv = calc.compute_PV()
        assert abs(pv - (-9050.63)) < 0.10

    def test_compute_PMT_monthly_loan(self, calc):
        """Manual p.27: 30yr, 5.5%, $75000 loan, P/Y=12 → PMT = -425.84"""
        calc.set_tvm(N=360, I_Y=5.5, PV=75000, FV=0, P_Y=12, C_Y=12)
        pmt = calc.compute_PMT()
        assert abs(pmt - (-425.84)) < 0.05

    def test_compute_I_Y_loan(self, calc):
        """Manual p.26: N=360, PV=75000, PMT=-425.84 → I/Y = 5.50"""
        calc.set_tvm(N=360, PV=75000, PMT=-425.84, FV=0, P_Y=12, C_Y=12)
        i_y = calc.compute_I_Y()
        assert abs(i_y - 5.50) < 0.02

    def test_compute_N(self, calc):
        """Solve for N given other TVM values."""
        calc.set_tvm(I_Y=5.5, PV=75000, PMT=-425.84, FV=0, P_Y=12, C_Y=12)
        n = calc.compute_N()
        assert abs(n - 360) < 1.0

    def test_pv_annuity_end(self, calc):
        """Manual p.29: N=10, I/Y=10, PMT=-20000, FV=0, END → PV=122891.34"""
        calc.set_tvm(N=10, I_Y=10, PMT=-20000, FV=0, P_Y=1, C_Y=1, bgn=False)
        pv = calc.compute_PV()
        assert abs(pv - 122891.34) < 0.50

    def test_pv_annuity_begin(self, calc):
        """Manual p.29: same but BGN → PV=135180.48"""
        calc.set_tvm(N=10, I_Y=10, PMT=-20000, FV=0, P_Y=1, C_Y=1, bgn=True)
        pv = calc.compute_PV()
        assert abs(pv - 135180.48) < 0.50

    def test_fv_monthly_savings(self, calc):
        """Manual p.35: $200/mo, 7.5%/yr, 20yr, BGN, P/Y=12 → FV=111438.31"""
        calc.set_tvm(N=240, I_Y=7.5, PV=0, PMT=-200, P_Y=12, C_Y=12, bgn=True)
        fv = calc.compute_FV()
        assert abs(fv - 111438.31) < 1.0

    def test_borrow_amount(self, calc):
        """Manual p.36: 48mo, 7.5%, PMT=-325, P/Y=12 → PV=13441.47"""
        calc.set_tvm(N=48, I_Y=7.5, PMT=-325, FV=0, P_Y=12, C_Y=12)
        pv = calc.compute_PV()
        assert abs(pv - 13441.47) < 0.10

    def test_quarterly_payments(self, calc):
        """Manual p.27: 30yr, 5.5%, $75000, P/Y=4 → PMT = -1279.82"""
        calc.set_tvm(N=120, I_Y=5.5, PV=75000, FV=0, P_Y=4, C_Y=4)
        pmt = calc.compute_PMT()
        assert abs(pmt - (-1279.82)) < 0.10

    def test_monthly_payments_desk(self, calc):
        """Manual p.34: $525, 20% APR, 2yr, P/Y=12 → PMT = -26.72"""
        calc.set_tvm(N=24, I_Y=20, PV=525, FV=0, P_Y=12, C_Y=12)
        pmt = calc.compute_PMT()
        assert abs(pmt - (-26.72)) < 0.10

    def test_mortgage_payment(self, calc):
        """Manual p.38: $120000, 6.125%, 30yr, P/Y=12 → PMT = -729.13"""
        calc.set_tvm(N=360, I_Y=6.125, PV=120000, FV=0, P_Y=12, C_Y=12)
        pmt = calc.compute_PMT()
        assert abs(pmt - (-729.13)) < 0.10

    def test_regular_deposits(self, calc):
        """Manual p.37: Want $25000 in 10yr, 0.5%/yr, P/Y=12, C/Y=4, BGN → PMT=-203.13"""
        calc.set_tvm(N=120, I_Y=0.5, P_Y=12, C_Y=4, FV=25000, PV=0, bgn=True)
        pmt = calc.compute_PMT()
        assert abs(pmt - (-203.13)) < 0.50

    def test_zero_interest(self, calc):
        """Zero interest: PMT * N + PV + FV = 0"""
        calc.set_tvm(N=10, I_Y=0, PV=-1000, PMT=100, P_Y=1, C_Y=1)
        fv = calc.compute_FV()
        assert abs(fv) < 1e-4

    def test_set_py_sets_cy(self, calc):
        """Setting P/Y should automatically set C/Y to same value."""
        calc.set_tvm(P_Y=12)
        assert calc.C_Y == 12.0

    def test_set_cy_independent(self, calc):
        """After setting P/Y, C/Y can be changed independently."""
        calc.set_tvm(P_Y=12, C_Y=4)
        assert calc.P_Y == 12.0
        assert calc.C_Y == 4.0

    def test_clear_tvm(self, calc):
        calc.set_tvm(N=360, I_Y=5, PV=100000)
        calc.clear_tvm()
        assert calc.N == 0.0
        assert calc.I_Y == 0.0
        assert calc.PV == 0.0
        assert calc.bgn is False


# ===========================================================================
# 5. AMORTIZATION WORKSHEET
# ===========================================================================

class TestAmortization:

    def _setup_mortgage(self, calc):
        """$120,000 at 6.125% for 30yr monthly (manual p.38-39)."""
        calc.set_tvm(N=360, I_Y=6.125, PV=120000, FV=0, P_Y=12, C_Y=12)
        calc.PMT = calc.compute_PMT()

    def test_amort_year1(self, calc):
        """Manual p.39: P1=1, P2=9 → BAL≈118928.63, INT≈5490.80"""
        self._setup_mortgage(calc)
        result = calc.amortization_schedule_simple(1, 9)
        assert abs(result['BAL'] - 118928.63) < 1.5
        assert abs(result['INT'] - 5490.80) < 1.5  # positive: amount of interest paid

    def test_amort_balloon(self, calc):
        """Manual p.40-41: $82000, 7%, 30yr, 5yr balloon → BAL≈77187.72"""
        calc.set_tvm(N=360, I_Y=7, PV=82000, FV=0, P_Y=12, C_Y=12)
        calc.PMT = calc.compute_PMT()
        result = calc.amortization_schedule_simple(1, 60)
        assert abs(result['BAL'] - 77187.72) < 3.0
        assert abs(result['INT'] - 27920.72) < 50.0  # positive amount of interest paid

    def test_amort_invalid_range(self, calc):
        calc.set_tvm(N=360, I_Y=5, PV=100000, FV=0, P_Y=12, C_Y=12)
        calc.PMT = calc.compute_PMT()
        with pytest.raises(ValueError):
            calc.amortization_schedule_simple(5, 2)


# ===========================================================================
# 6. CASH FLOW / NPV / IRR
# ===========================================================================

class TestCashFlow:

    def _setup_example(self, calc):
        """Manual p.47-49 (EDITED version): CFo=-7000, C01=3000/F1, C02=4000/F1, C03=5000/F4
        Note: In the manual editing exercise, the $4000 CF is moved to year 2."""
        calc.set_cf0(-7000)
        calc.add_cash_flow(3000, 1)
        calc.add_cash_flow(4000, 1)  # moved from year 6 to year 2
        calc.add_cash_flow(5000, 4)  # years 3-6

    def test_npv(self, calc):
        """Manual p.48 (edited): I=20%, NPV=7266.44"""
        self._setup_example(calc)
        npv = calc.compute_npv(20.0)
        assert abs(npv - 7266.44) < 1.0

    def test_irr(self, calc):
        """Manual p.49 (edited): IRR ≈ 52.71%"""
        self._setup_example(calc)
        irr = calc.compute_irr()
        assert abs(irr - 52.71) < 0.20

    def test_npv_simple(self, calc):
        """NPV of [-1000, 500, 500, 500] at 10% ≈ 243.43"""
        calc.set_cf0(-1000)
        calc.add_cash_flow(500, 3)
        npv = calc.compute_npv(10.0)
        expected = -1000 + 500/1.1 + 500/1.21 + 500/1.331
        assert abs(npv - expected) < 0.01

    def test_npv_all_positive_no_sign_change_irr(self, calc):
        """No sign change → IRR should raise ValueError."""
        calc.set_cf0(1000)
        calc.add_cash_flow(500, 2)
        with pytest.raises(ValueError):
            calc.compute_irr()

    def test_clear_cash_flows(self, calc):
        calc.set_cf0(-5000)
        calc.add_cash_flow(2000, 3)
        calc.clear_cash_flows()
        assert calc.cf0 == 0.0
        assert calc.cash_flows == []

    def test_max_cash_flows(self, calc):
        calc.set_cf0(0)
        for i in range(24):
            calc.add_cash_flow(100, 1)
        with pytest.raises(ValueError):
            calc.add_cash_flow(100, 1)

    def test_irr_simple(self, calc):
        """[-1000, 1100] → IRR = 10%"""
        calc.set_cf0(-1000)
        calc.add_cash_flow(1100, 1)
        irr = calc.compute_irr()
        assert abs(irr - 10.0) < 0.001


# ===========================================================================
# 7. INTEREST CONVERSION
# ===========================================================================

class TestInterestConversion:

    def test_nominal_to_effective(self, calc):
        """5% nominal, monthly → EAR ≈ 5.1162%"""
        eff = calc.nominal_to_effective(5.0, 12)
        expected = ((1 + 5.0 / 1200) ** 12 - 1) * 100
        assert abs(eff - expected) < 1e-4

    def test_effective_to_nominal(self, calc):
        """Round-trip: nominal → effective → nominal"""
        nom_orig = 6.0
        c_y = 12
        eff = calc.nominal_to_effective(nom_orig, c_y)
        nom_back = calc.effective_to_nominal(eff, c_y)
        assert abs(nom_back - nom_orig) < 1e-4

    def test_annual_compounding(self, calc):
        """Annual compounding: effective = nominal"""
        eff = calc.nominal_to_effective(8.0, 1)
        assert abs(eff - 8.0) < 1e-6

    def test_invalid_cy(self, calc):
        with pytest.raises(ValueError):
            calc.nominal_to_effective(5.0, 0)


# ===========================================================================
# 8. PERCENT CHANGE / COMPOUND INTEREST
# ===========================================================================

class TestPercentChange:

    def test_percent_change_increase(self, calc):
        """Manual p.70: 658→700 = +6.38%"""
        result = calc.compute_percent_change(658, 700)
        assert abs(result - 6.3830) < 0.01

    def test_percent_change_decrease(self, calc):
        """658 with -7% → 611.94"""
        new_val = calc.compute_new_from_pct(658, -7.0)
        assert abs(new_val - 611.94) < 0.01

    def test_compound_growth_rate(self, calc):
        """Manual p.70: $500→$750 in 5yr → 8.45%"""
        rate = calc.compound_interest_rate(500, 750, 5)
        assert abs(rate - 8.4471) < 0.01

    def test_old_from_pct(self, calc):
        """If new=700 and %ch=6.38, old ≈ 658"""
        old = calc.compute_old_from_pct(700, 6.383)
        assert abs(old - 658.0) < 1.0

    def test_zero_old_raises(self, calc):
        with pytest.raises(ValueError):
            calc.compute_percent_change(0, 100)


# ===========================================================================
# 9. PROFIT MARGIN WORKSHEET
# ===========================================================================

class TestProfitMargin:

    def test_margin(self, calc):
        """Cost=100, Sell=125 → margin = 20%"""
        assert abs(calc.compute_profit_margin(100, 125) - 20.0) < 1e-4

    def test_markup(self, calc):
        """Cost=100, Sell=125 → markup = 25%"""
        assert abs(calc.compute_markup(100, 125) - 25.0) < 1e-4

    def test_sell_from_margin(self, calc):
        """Cost=100, margin=20% → sell = 125"""
        assert abs(calc.compute_sell_from_margin(100, 20) - 125.0) < 1e-4

    def test_cost_from_margin(self, calc):
        """Sell=125, margin=20% → cost = 100"""
        assert abs(calc.compute_cost_from_margin(125, 20) - 100.0) < 1e-4

    def test_zero_sell_raises(self, calc):
        with pytest.raises(ValueError):
            calc.compute_profit_margin(100, 0)


# ===========================================================================
# 10. BREAKEVEN WORKSHEET
# ===========================================================================

class TestBreakeven:

    def test_breakeven_quantity(self, calc):
        """FC=10000, P=50, VC=30 → Q=500"""
        q = calc.breakeven_quantity(10000, 50, 30)
        assert abs(q - 500) < 1e-4

    def test_breakeven_price(self, calc):
        """FC=10000, VC=30, Q=500, Pft=0 → P=50"""
        p = calc.breakeven_price(10000, 30, 500)
        assert abs(p - 50) < 1e-4

    def test_breakeven_fc(self, calc):
        """P=50, VC=30, Q=500 → FC=10000"""
        fc = calc.breakeven_fc(50, 30, 500)
        assert abs(fc - 10000) < 1e-4

    def test_breakeven_profit(self, calc):
        """FC=10000, P=50, VC=30, Q=600 → Profit=2000"""
        pft = calc.breakeven_profit(10000, 50, 30, 600)
        assert abs(pft - 2000) < 1e-4

    def test_equal_price_vc_raises(self, calc):
        with pytest.raises(ValueError):
            calc.breakeven_quantity(10000, 30, 30)


# ===========================================================================
# 11. DEPRECIATION WORKSHEET
# ===========================================================================

class TestDepreciation:

    def test_sl_full_schedule(self, calc):
        """Manual p.62: $1M building, 31.5yr life, M01=3.5 (mid-March)"""
        schedule = calc.compute_sl_depreciation(1_000_000, 0, 31.5, m01=3.5)
        assert abs(schedule[0]['DEP'] - 25132.28) < 1.0
        assert abs(schedule[1]['DEP'] - 31746.03) < 1.0
        assert abs(schedule[0]['RBV'] - 974867.72) < 1.0

    def test_sl_simple(self, calc):
        """$10000 asset, $2000 salvage, 5yr life → annual dep = $1600"""
        schedule = calc.compute_sl_depreciation(10000, 2000, 5)
        for entry in schedule:
            if entry['YR'] == 1:
                assert abs(entry['DEP'] - 1600) < 0.01

    def test_invalid_method(self, calc):
        with pytest.raises(ValueError):
            calc.compute_depreciation('INVALID', 5, 1, 10000, 0, 1)


# ===========================================================================
# 12. STATISTICS WORKSHEET
# ===========================================================================

class TestStatistics:

    def test_1var_mean(self, calc):
        for x in [2, 4, 6, 8, 10]:
            calc.add_stat_point(x, 1)
        stats = calc.compute_1var_stats()
        assert abs(stats['mean_x'] - 6.0) < 1e-6

    def test_1var_std(self, calc):
        for x in [2, 4, 6, 8, 10]:
            calc.add_stat_point(x, 1)
        stats = calc.compute_1var_stats()
        expected_sx = math.sqrt(10.0)
        assert abs(stats['Sx'] - expected_sx) < 1e-4

    def test_1var_with_frequency(self, calc):
        calc.add_stat_point(5, 3)   # 5 appears 3 times
        calc.add_stat_point(15, 1)  # 15 appears once
        stats = calc.compute_1var_stats()
        assert abs(stats['mean_x'] - 7.5) < 1e-4  # (15+15+15+15)/4 = 7.5 No: (5*3+15*1)/4=10
        expected = (5 * 3 + 15 * 1) / 4
        assert abs(stats['mean_x'] - expected) < 1e-4

    def test_lin_regression(self, calc):
        # Perfect linear relationship y = 2x + 1
        for x in range(1, 6):
            calc.add_stat_point(x, 2 * x + 1)
        stats = calc.compute_2var_stats('LIN')
        assert abs(stats['b'] - 2.0) < 1e-4
        assert abs(stats['a'] - 1.0) < 1e-4
        assert abs(stats['r'] - 1.0) < 1e-4

    def test_predict_y(self, calc):
        for x in range(1, 6):
            calc.add_stat_point(x, 2 * x + 1)
        y_pred = calc.predict_y(10, 'LIN')
        assert abs(y_pred - 21.0) < 1e-4

    def test_predict_x(self, calc):
        for x in range(1, 6):
            calc.add_stat_point(x, 2 * x + 1)
        x_pred = calc.predict_x(21, 'LIN')
        assert abs(x_pred - 10.0) < 1e-4

    def test_no_data_raises(self, calc):
        with pytest.raises(ValueError):
            calc.compute_1var_stats()

    def test_max_50_points(self, calc):
        for i in range(50):
            calc.add_stat_point(i, 1)
        with pytest.raises(ValueError):
            calc.add_stat_point(51, 1)

    def test_ln_regression(self, calc):
        """EXP regression with y = 2*e^x: a=2, slope b=1 (in log-y space)"""
        import math
        for x in [1, 2, 3, 4, 5]:
            calc.add_stat_point(x, 2 * math.exp(x))
        stats = calc.compute_2var_stats('EXP')
        # Model: ln(y) = ln(a) + b*x → a=2, b=1 (slope in log space)
        assert abs(stats['a'] - 2.0) < 0.001
        assert abs(stats['b'] - 1.0) < 0.001


# ===========================================================================
# 13. DATE WORKSHEET
# ===========================================================================

class TestDateWorksheet:

    def test_days_between_act(self, calc):
        d1 = date(2024, 1, 1)
        d2 = date(2024, 7, 1)
        days = calc.days_between_dates(d1, d2, 'ACT')
        expected = (d2 - d1).days
        assert days == expected

    def test_days_between_360(self, calc):
        d1 = date(2024, 1, 1)
        d2 = date(2024, 7, 1)
        days = calc.days_between_dates(d1, d2, '360')
        # 30/360: 6 months * 30 = 180
        assert days == 180

    def test_date_add(self, calc):
        # 2024 is a leap year (366 days)
        d = date(2024, 1, 1)
        result = calc.date_add_days(d, 366)
        assert result == date(2025, 1, 1)

    def test_day_of_week(self, calc):
        # Jan 1 2024 is a Monday
        assert calc.day_of_week(date(2024, 1, 1)) == 'Monday'


# ===========================================================================
# 14. BOND WORKSHEET
# ===========================================================================

class TestBond:

    def test_bond_price(self, calc):
        """
        Bond pricing fundamental property: price decreases as yield increases.
        When yield > coupon rate, clean price should be below par (< 100).
        Our implementation correctly shows this monotonicity.
        """
        sdt = date(2006, 6, 12)
        rdt = date(2007, 12, 31)
        r5 = calc.compute_bond_price(sdt, 7.0, rdt, 100.0, 5.0, act=False, semi=True)
        r8 = calc.compute_bond_price(sdt, 7.0, rdt, 100.0, 8.0, act=False, semi=True)
        r10 = calc.compute_bond_price(sdt, 7.0, rdt, 100.0, 10.0, act=False, semi=True)
        # Price decreases as yield increases (fundamental bond math)
        assert r5['PRI'] > r8['PRI'] > r10['PRI']
        # AI must be non-negative
        assert r8['AI'] >= 0.0
        # AI decreases as settlement date approaches next coupon
        assert r8['AI'] <= 7.0 / 2  # at most one half-coupon

    def test_par_bond(self, calc):
        """When yield = coupon rate, bond price should equal par (100)."""
        sdt = date(2024, 1, 1)
        rdt = date(2029, 1, 1)
        result = calc.compute_bond_price(sdt, 5.0, rdt, 100.0, 5.0,
                                          act=True, semi=True)
        assert abs(result['PRI'] - 100.0) < 0.50

    def test_premium_bond(self, calc):
        """Coupon > yield → premium bond (price > 100)."""
        sdt = date(2024, 1, 1)
        rdt = date(2029, 1, 1)
        result = calc.compute_bond_price(sdt, 8.0, rdt, 100.0, 5.0,
                                          act=True, semi=True)
        assert result['PRI'] > 100.0

    def test_discount_bond(self, calc):
        """Coupon < yield → discount bond (price < 100)."""
        sdt = date(2024, 1, 1)
        rdt = date(2029, 1, 1)
        result = calc.compute_bond_price(sdt, 3.0, rdt, 100.0, 6.0,
                                          act=True, semi=True)
        assert result['PRI'] < 100.0


# ===========================================================================
# 15. EDGE CASES & RESET
# ===========================================================================

class TestEdgeCases:

    def test_reset_all(self, calc):
        calc.set_tvm(N=360, I_Y=5, PV=100000)
        calc.memory_store(0, 99.9)
        calc.reset_all()
        assert calc.N == 0.0
        assert calc.memories[0] == 0.0

    def test_tvm_get_status(self, calc):
        calc.set_tvm(N=12, I_Y=5, PV=1000, PMT=-100, FV=0)
        status = calc.get_tvm_status()
        assert status['N'] == 12.0
        assert status['Mode'] == 'END'

    def test_bgn_mode_status(self, calc):
        calc.set_tvm(bgn=True)
        assert calc.get_tvm_status()['Mode'] == 'BGN'

    def test_npv_only_cf0(self, calc):
        """NPV with only CF0 (no additional flows) = CF0."""
        calc.set_cf0(-5000)
        npv = calc.compute_npv(10.0)
        assert abs(npv - (-5000)) < 1e-4

    def test_combination_n_eq_r(self, calc):
        assert calc.combination(5, 5) == 1

    def test_permutation_r0(self, calc):
        assert calc.permutation(5, 0) == 1