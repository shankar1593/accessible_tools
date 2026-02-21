"""
BA II Plus Financial Calculator - Backend Engine
Implements all worksheets: TVM, Amortization, Cash Flow (NPV/IRR),
Bond, Depreciation, Statistics, Interest Conversion, Percent Change,
Profit Margin, Breakeven, Date, and Memory worksheets.

Formulas verified against TI BA II Plus official manual.
"""

import math
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Helper: TVM effective period rate (correct formula per BA II Plus manual)
# ---------------------------------------------------------------------------

def _effective_period_rate(i_y: float, p_y: float, c_y: float) -> float:
    """
    Convert annual nominal rate (I/Y) to effective rate per payment period.
    The BA II Plus uses:
        r = (1 + I/Y / (100 * C/Y))^(C/Y / P/Y) - 1
    """
    if p_y <= 0 or c_y <= 0:
        raise ValueError("P/Y and C/Y must be positive")
    nominal_per_compound = i_y / (100.0 * c_y)
    return (1.0 + nominal_per_compound) ** (c_y / p_y) - 1.0


# ---------------------------------------------------------------------------
# Main calculator class
# ---------------------------------------------------------------------------

class FinancialCalculator:
    """
    Comprehensive BA II Plus Financial Calculator.
    Implements all worksheets and standard arithmetic operations.
    """

    def __init__(self):
        # ---- Basic calculator state ----
        self.display = 0.0
        self.last_answer = 0.0

        # ---- Memory bank (10 slots M0-M9) ----
        self.memories = [0.0] * 10

        # ---- TVM variables ----
        self.N = 0.0
        self.I_Y = 0.0
        self.PV = 0.0
        self.PMT = 0.0
        self.FV = 0.0
        self.P_Y = 1.0
        self.C_Y = 1.0
        self.bgn = False           # False = END, True = BEGIN

        # ---- Amortization variables ----
        self.amort_p1 = 1.0
        self.amort_p2 = 1.0

        # ---- Cash Flow worksheet ----
        self.cf0 = 0.0
        self.cash_flows = []        # list of (amount, frequency)
        self.cf_discount_rate = 0.0

        # ---- Bond worksheet ----
        self.bond_sdt = None        # settlement date (date object)
        self.bond_cpn = 0.0         # annual coupon rate %
        self.bond_rdt = None        # redemption date (date object)
        self.bond_rv = 100.0        # redemption value (% of par)
        self.bond_act = True        # True=ACT/ACT, False=30/360
        self.bond_semi = True       # True=2/Y, False=1/Y
        self.bond_yld = 0.0
        self.bond_pri = 0.0

        # ---- Depreciation worksheet ----
        self.dep_method = 'SL'      # SL, SYD, DB, DBX
        self.dep_db_rate = 200.0    # declining balance %
        self.dep_lif = 5.0
        self.dep_m01 = 1.0
        self.dep_cst = 0.0
        self.dep_sal = 0.0
        self.dep_yr = 1.0

        # ---- Statistics worksheet ----
        # Each entry: (x, y) where y is frequency for 1-var or y-value for 2-var
        self.stat_data = []         # list of (x, y)
        self.stat_method = 'LIN'    # LIN, Ln, EXP, PWR, 1-V

        # ---- Percent Change / Compound Interest worksheet ----
        self.pct_old = 0.0
        self.pct_new = 0.0
        self.pct_ch = 0.0
        self.pct_npd = 1.0

        # ---- Interest Conversion worksheet ----
        self.iconv_nom = 0.0        # Nominal (APR)
        self.iconv_eff = 0.0        # Effective (APY)
        self.iconv_c_y = 1.0       # Compounding periods

        # ---- Profit Margin worksheet ----
        self.pm_cost = 0.0
        self.pm_sell = 0.0
        self.pm_margin = 0.0

        # ---- Breakeven worksheet ----
        self.be_fc = 0.0            # Fixed cost
        self.be_vc = 0.0            # Variable cost per unit
        self.be_p = 0.0             # Price per unit
        self.be_pft = 0.0           # Profit
        self.be_q = 0.0             # Quantity

        # ---- Date worksheet ----
        self.date_dt1 = None
        self.date_dt2 = None
        self.date_dbm = 'ACT'       # ACT or 360

    # =======================================================================
    # BASIC ARITHMETIC
    # =======================================================================

    def add(self, a: float, b: float) -> float:
        return a + b

    def subtract(self, a: float, b: float) -> float:
        return a - b

    def multiply(self, a: float, b: float) -> float:
        return a * b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b

    def power(self, base: float, exp: float) -> float:
        return base ** exp

    def square_root(self, x: float) -> float:
        if x < 0:
            raise ValueError("Cannot take square root of negative number")
        return math.sqrt(x)

    def reciprocal(self, x: float) -> float:
        if x == 0:
            raise ZeroDivisionError("Cannot take reciprocal of zero")
        return 1.0 / x

    def natural_log(self, x: float) -> float:
        if x <= 0:
            raise ValueError("ln requires a positive number")
        return math.log(x)

    def exp(self, x: float) -> float:
        return math.exp(x)

    def factorial(self, n: int) -> int:
        if n < 0 or n > 69:
            raise ValueError("Factorial requires 0 ≤ n ≤ 69")
        if not isinstance(n, int):
            n = int(n)
        return math.factorial(n)

    def combination(self, n: int, r: int) -> int:
        """nCr - number of combinations"""
        if n < 0 or r < 0 or r > n:
            raise ValueError("Invalid combination arguments")
        return math.comb(n, r)

    def permutation(self, n: int, r: int) -> int:
        """nPr - number of permutations"""
        if n < 0 or r < 0 or r > n:
            raise ValueError("Invalid permutation arguments")
        return math.perm(n, r)

    def percent_of(self, base: float, pct: float) -> float:
        """base * pct / 100"""
        return base * pct / 100.0

    def round_to(self, value: float, decimals: int) -> float:
        return round(value, decimals)

    # =======================================================================
    # MEMORY OPERATIONS (10 slots: M0 - M9)
    # =======================================================================

    def memory_store(self, slot: int, value: float):
        self._check_slot(slot)
        self.memories[slot] = value

    def memory_recall(self, slot: int) -> float:
        self._check_slot(slot)
        return self.memories[slot]

    def memory_clear(self, slot: int):
        self._check_slot(slot)
        self.memories[slot] = 0.0

    def memory_clear_all(self):
        self.memories = [0.0] * 10

    def memory_add(self, slot: int, value: float):
        self._check_slot(slot)
        self.memories[slot] += value

    def memory_subtract(self, slot: int, value: float):
        self._check_slot(slot)
        self.memories[slot] -= value

    def memory_multiply(self, slot: int, value: float):
        self._check_slot(slot)
        self.memories[slot] *= value

    def memory_divide(self, slot: int, value: float):
        self._check_slot(slot)
        if value == 0:
            raise ZeroDivisionError("Cannot divide memory by zero")
        self.memories[slot] /= value

    def _check_slot(self, slot: int):
        if slot < 0 or slot > 9:
            raise ValueError("Memory slot must be 0-9")

    # =======================================================================
    # TVM WORKSHEET
    # =======================================================================

    def set_tvm(self, **kwargs):
        """Set one or more TVM variables. Keys: N, I_Y, PV, PMT, FV, P_Y, C_Y, bgn"""
        for k, v in kwargs.items():
            if k == 'N':
                self.N = float(v)
            elif k == 'I_Y':
                self.I_Y = float(v)
            elif k == 'PV':
                self.PV = float(v)
            elif k == 'PMT':
                self.PMT = float(v)
            elif k == 'FV':
                self.FV = float(v)
            elif k == 'P_Y':
                self.P_Y = float(v)
                # Setting P_Y automatically sets C_Y to same value (per manual)
                self.C_Y = float(v)
            elif k == 'C_Y':
                self.C_Y = float(v)
            elif k == 'bgn':
                self.bgn = bool(v)

    def clear_tvm(self):
        """Reset TVM variables to defaults"""
        self.N = 0.0
        self.I_Y = 0.0
        self.PV = 0.0
        self.PMT = 0.0
        self.FV = 0.0
        self.P_Y = 1.0
        self.C_Y = 1.0
        self.bgn = False

    def _r(self) -> float:
        """Effective rate per payment period."""
        return _effective_period_rate(self.I_Y, self.P_Y, self.C_Y)

    # Internal TVM core solver (returns value, not stored)
    @staticmethod
    def _tvm_npv(n, r, pv, pmt, fv, bgn):
        """
        TVM fundamental equation:
        PV*(1+r)^n + PMT*(1+r*bgn)*((1+r)^n - 1)/r + FV = 0
        (zero-rate version: PV + PMT*n + FV = 0)
        Returns equation residual (should be 0 at solution).
        """
        if r == 0:
            return pv + pmt * n + fv
        factor = (1.0 + r) ** n
        bgn_mult = (1.0 + r) if bgn else 1.0
        return pv * factor + pmt * bgn_mult * (factor - 1.0) / r + fv

    def compute_FV(self) -> float:
        """Solve for Future Value."""
        n, r = self.N, self._r()
        pv, pmt, bgn = self.PV, self.PMT, self.bgn
        if r == 0:
            fv = -(pv + pmt * n)
        else:
            bgn_mult = (1.0 + r) if bgn else 1.0
            factor = (1.0 + r) ** n
            fv = -(pv * factor + pmt * bgn_mult * (factor - 1.0) / r)
        self.FV = round(fv, 6)
        return self.FV

    def compute_PV(self) -> float:
        """Solve for Present Value."""
        n, r = self.N, self._r()
        pmt, fv, bgn = self.PMT, self.FV, self.bgn
        if r == 0:
            pv = -(pmt * n + fv)
        else:
            bgn_mult = (1.0 + r) if bgn else 1.0
            factor = (1.0 + r) ** n
            pv = -(pmt * bgn_mult * (factor - 1.0) / r + fv) / factor
        self.PV = round(pv, 6)
        return self.PV

    def compute_PMT(self) -> float:
        """Solve for Payment."""
        n, r = self.N, self._r()
        pv, fv, bgn = self.PV, self.FV, self.bgn
        if r == 0:
            if n == 0:
                raise ValueError("Cannot compute PMT when N=0 and I/Y=0")
            pmt = -(pv + fv) / n
        else:
            bgn_mult = (1.0 + r) if bgn else 1.0
            factor = (1.0 + r) ** n
            pmt = -(pv * factor + fv) / (bgn_mult * (factor - 1.0) / r)
        self.PMT = round(pmt, 6)
        return self.PMT

    def compute_N(self) -> float:
        """Solve for Number of Periods."""
        r = self._r()
        pv, pmt, fv, bgn = self.PV, self.PMT, self.FV, self.bgn
        if r == 0:
            if pmt == 0:
                raise ValueError("Cannot compute N when I/Y=0 and PMT=0")
            n = -(pv + fv) / pmt
        else:
            bgn_mult = (1.0 + r) if bgn else 1.0
            # Rearrange: PV*(1+r)^n + PMT*bgn_mult*((1+r)^n-1)/r + FV = 0
            # Let x = (1+r)^n
            # PV*x + PMT*bgn_mult*(x-1)/r + FV = 0
            # x*(PV + PMT*bgn_mult/r) = PMT*bgn_mult/r - FV
            adj_pmt = pmt * bgn_mult / r
            denom = pv + adj_pmt
            if abs(denom) < 1e-12:
                raise ValueError("Cannot compute N: invalid combination of values")
            num = adj_pmt - fv
            if num / denom <= 0:
                raise ValueError("Cannot compute N: no valid solution")
            n = math.log(num / denom) / math.log(1.0 + r)
        self.N = round(n, 6)
        return self.N

    def compute_I_Y(self) -> float:
        """Solve for Annual Interest Rate using Newton-Raphson."""
        n, pv, pmt, fv, bgn = self.N, self.PV, self.PMT, self.FV, self.bgn
        p_y, c_y = self.P_Y, self.C_Y

        # Objective: find r (period rate) such that TVM equation = 0
        # Then convert back to I/Y

        # Initial guess from simple case
        if pv != 0 and pmt == 0:
            try:
                r_guess = (abs(fv / pv)) ** (1.0 / n) - 1.0
                if pv * fv > 0:
                    r_guess = -abs(r_guess)
            except Exception:
                r_guess = 0.1
        else:
            r_guess = 0.1

        r = self._newton_raphson_irr(r_guess, n, pv, pmt, fv, bgn)

        # Convert period rate back to annual I/Y
        # r = (1 + I/Y/(100*C/Y))^(C/Y/P/Y) - 1
        # 1 + r = (1 + I/Y/(100*C/Y))^(C/Y/P/Y)
        # (1+r)^(P/Y/C/Y) = 1 + I/Y/(100*C/Y)
        # I/Y = ((1+r)^(P/Y/C/Y) - 1) * C/Y * 100
        i_y = ((1.0 + r) ** (p_y / c_y) - 1.0) * c_y * 100.0
        self.I_Y = round(i_y, 6)
        return self.I_Y

    def _newton_raphson_irr(self, r_guess, n, pv, pmt, fv, bgn,
                             max_iter=200, tol=1e-10):
        """Newton-Raphson solver for period interest rate."""
        r = r_guess
        for _ in range(max_iter):
            if r <= -1.0:
                r = -0.9999
            if abs(r) < 1e-10:
                # Near-zero: use limit
                f = pv + pmt * n + fv
                df = -pv * n - pmt * n * (n - 1) / 2.0
            else:
                bgn_mult = (1.0 + r) if bgn else 1.0
                factor = (1.0 + r) ** n
                f = pv * factor + pmt * bgn_mult * (factor - 1.0) / r + fv
                # Derivative df/dr
                d_factor = n * (1.0 + r) ** (n - 1.0)
                if bgn:
                    d_bgn_pmt = (pmt / r) * (d_factor * (1.0 + r) + (factor - 1.0) +
                                              (factor - 1.0) * 0) - pmt * bgn_mult * (factor - 1.0) / r**2
                    # Simplify:
                    d_bgn_pmt = pmt * (d_factor * (1.0 + r) / r +
                                       (factor - 1.0) / r -
                                       bgn_mult * (factor - 1.0) / r**2)
                else:
                    d_bgn_pmt = pmt * (d_factor / r - (factor - 1.0) / r**2)
                df = pv * d_factor + d_bgn_pmt

            if abs(df) < 1e-14:
                break
            r_new = r - f / df
            if abs(r_new - r) < tol:
                return r_new
            r = r_new
        return r

    # =======================================================================
    # AMORTIZATION WORKSHEET
    # =======================================================================

    def amortization_schedule(self, p1: int, p2: int) -> dict:
        """
        Generate amortization schedule for payments p1 through p2.
        Uses rounded PMT (2 decimal places) per BA II Plus convention.
        Returns dict with BAL, PRN, INT.
        """
        if p1 < 1 or p2 < p1:
            raise ValueError("Invalid payment range: p1 >= 1 and p2 >= p1")

        r = self._r()
        pv = self.PV
        pmt_rounded = round(self.PMT, 2)
        bgn = self.bgn

        # Walk from payment 1 to p2
        balance = pv
        total_prn = 0.0
        total_int = 0.0

        for period in range(1, p2 + 1):
            if bgn:
                # Beginning of period: payment first, then interest
                balance += pmt_rounded
                interest = balance * r
            else:
                # End of period: interest first, then payment
                interest = balance * r
                balance = balance + interest + pmt_rounded

            if period >= p1:
                principal = pmt_rounded - interest if not bgn else -interest
                if bgn:
                    principal = pmt_rounded
                    total_int += interest
                    total_prn += principal
                else:
                    total_int += interest
                    total_prn += (pmt_rounded - interest)

        # Recalculate cleanly
        balance = self.PV
        for period in range(1, p2 + 1):
            interest = balance * r
            principal_paid = pmt_rounded - interest  # pmt is negative for outflow
            if not bgn:
                balance = balance - principal_paid
            else:
                balance = balance + pmt_rounded
                interest = balance * r

        # Clean approach - walk step by step
        balance = self.PV
        total_principal = 0.0
        total_interest = 0.0

        for period in range(1, p2 + 1):
            if bgn:
                bal_after_pmt = balance + pmt_rounded
                interest_charged = bal_after_pmt * r
                if period >= p1:
                    total_interest += interest_charged
                    total_principal += pmt_rounded
                balance = bal_after_pmt + interest_charged
            else:
                interest_charged = balance * r
                principal_paid = -(pmt_rounded + interest_charged)
                if period >= p1:
                    total_interest += interest_charged
                    total_principal += principal_paid
                balance = balance + interest_charged + pmt_rounded

        return {
            'BAL': round(balance, 2),
            'PRN': round(total_principal, 2),
            'INT': round(total_interest, 2),
        }

    def amortization_schedule_simple(self, p1: int, p2: int) -> dict:
        """
        Simplified amortization (END mode) matching BA II Plus output.
        Loan convention: PV > 0, PMT < 0.
        """
        if p1 < 1:
            raise ValueError("P1 must be >= 1")
        if p2 < p1:
            raise ValueError("P2 must be >= P1")
        r = self._r()
        pmt = round(self.PMT, 2)
        balance = self.PV

        total_principal = 0.0
        total_interest = 0.0

        for period in range(1, p2 + 1):
            interest = round(balance * r, 10)
            principal = -(pmt + interest)   # how much balance reduces
            if period >= p1:
                total_principal += principal
                total_interest += interest
            balance = balance - principal

        return {
            'BAL': round(balance, 2),
            'PRN': round(total_principal, 2),
            'INT': round(total_interest, 2),
        }

    # =======================================================================
    # CASH FLOW WORKSHEET (NPV / IRR)
    # =======================================================================

    def set_cf0(self, amount: float):
        """Set initial cash flow CF0."""
        self.cf0 = amount

    def clear_cash_flows(self):
        """Clear all cash flows."""
        self.cf0 = 0.0
        self.cash_flows = []

    def add_cash_flow(self, amount: float, frequency: int = 1):
        """Add a cash flow C01..C24 with frequency."""
        if len(self.cash_flows) >= 24:
            raise ValueError("Maximum 24 additional cash flows (C01-C24)")
        if frequency < 1 or frequency > 9999:
            raise ValueError("Frequency must be 1-9999")
        self.cash_flows.append((float(amount), int(frequency)))

    def _expand_cash_flows(self):
        """Expand (amount, freq) pairs into period-by-period list starting with CF0."""
        expanded = [self.cf0]
        for amount, freq in self.cash_flows:
            for _ in range(freq):
                expanded.append(amount)
        return expanded

    def compute_npv(self, discount_rate: float) -> float:
        """
        Compute Net Present Value.
        discount_rate is the periodic rate as a percentage.
        CF0 is at period 0, subsequent CFs at periods 1, 2, ...
        """
        expanded = self._expand_cash_flows()
        if not expanded:
            raise ValueError("No cash flows entered")
        r = discount_rate / 100.0
        npv = 0.0
        for t, cf in enumerate(expanded):
            npv += cf / (1.0 + r) ** t
        return round(npv, 6)

    def compute_irr(self, max_iterations: int = 500, tolerance: float = 1e-8) -> float:
        """
        Compute Internal Rate of Return (periodic, as percentage).
        Uses Newton-Raphson with multiple starting points.
        """
        expanded = self._expand_cash_flows()
        if not expanded:
            raise ValueError("No cash flows entered")
        if len(expanded) < 2:
            raise ValueError("Need at least one cash flow beyond CF0")

        # Check for sign changes (required for IRR to exist)
        signs = [1 if cf >= 0 else -1 for cf in expanded]
        sign_changes = sum(1 for i in range(1, len(signs)) if signs[i] != signs[i-1])
        if sign_changes == 0:
            raise ValueError("No sign change in cash flows – no IRR solution")

        def npv_at(r):
            return sum(cf / (1.0 + r) ** t for t, cf in enumerate(expanded))

        def dnpv_at(r):
            return sum(-t * cf / (1.0 + r) ** (t + 1) for t, cf in enumerate(expanded))

        # Try multiple starting points
        best_r = None
        for r0 in [0.1, 0.01, 0.5, -0.01, 0.001]:
            r = r0
            for _ in range(max_iterations):
                if r <= -1.0:
                    r = -0.9999
                f = npv_at(r)
                df = dnpv_at(r)
                if abs(df) < 1e-15:
                    break
                r_new = r - f / df
                if abs(r_new - r) < tolerance:
                    r = r_new
                    break
                r = r_new
            if abs(npv_at(r)) < 1e-4:
                best_r = r
                break

        if best_r is None:
            raise ValueError("IRR did not converge – try different cash flows")

        return round(best_r * 100.0, 6)

    # =======================================================================
    # BOND WORKSHEET
    # =======================================================================

    @staticmethod
    def _days_between(d1: date, d2: date, method: str = 'ACT') -> float:
        """Days between two dates using ACT or 30/360 convention."""
        if method == 'ACT':
            return (d2 - d1).days
        else:  # 30/360
            y1, m1, day1 = d1.year, d1.month, min(d1.day, 30)
            y2, m2, day2 = d2.year, d2.month, d2.day
            if day2 == 31 and day1 >= 30:
                day2 = 30
            elif day2 == 31:
                day2 = 31
            day1 = min(day1, 30)
            return (y2 - y1) * 360 + (m2 - m1) * 30 + (day2 - day1)

    def compute_bond_price(self, sdt: date, cpn: float, rdt: date, rv: float,
                           yld: float, act: bool = True, semi: bool = True) -> dict:
        """
        Compute bond price and accrued interest.
        Returns dict with PRI (price per $100) and AI (accrued interest per $100).

        sdt: settlement date
        cpn: annual coupon rate (%)
        rdt: redemption date
        rv:  redemption value (% of par, typically 100)
        yld: yield to redemption (annual %)
        act: True = ACT/ACT day count, False = 30/360
        semi: True = semiannual coupons, False = annual
        """
        freq = 2 if semi else 1
        coupon_payment = cpn / freq  # coupon per period (% of par)
        y_per_period = yld / (100.0 * freq)  # yield per coupon period
        day_method = 'ACT' if act else '360'

        # Find coupon dates surrounding settlement
        # Walk back from redemption date to find coupon dates
        coupon_dates = []
        d = rdt
        while d > sdt:
            coupon_dates.append(d)
            months_back = 12 // freq
            m = d.month - months_back
            y = d.year
            while m <= 0:
                m += 12
                y -= 1
            try:
                d = date(y, m, d.day)
            except ValueError:
                import calendar
                d = date(y, m, calendar.monthrange(y, m)[1])
        coupon_dates.append(d)  # last date before or on settlement
        coupon_dates.reverse()

        # Previous coupon date (on or before settlement)
        prev_cpn = coupon_dates[0]
        # Next coupon date (after settlement)
        if len(coupon_dates) < 2:
            raise ValueError("Cannot determine coupon dates")
        next_cpn = coupon_dates[1]
        remaining_coupons = len(coupon_dates) - 1  # coupons from next to redemption

        # Fraction of coupon period elapsed since last coupon
        if act:
            days_in_period = (next_cpn - prev_cpn).days
            days_since_last = (sdt - prev_cpn).days
        else:
            days_in_period = self._days_between(prev_cpn, next_cpn, '360')
            days_since_last = self._days_between(prev_cpn, sdt, '360')

        if days_in_period == 0:
            raise ValueError("Invalid coupon dates")

        w = days_since_last / days_in_period   # fraction elapsed
        e = 1.0 - w                            # fraction remaining to next coupon

        if remaining_coupons == 1:
            # Odd (last) period
            price = (coupon_payment + rv) / (1.0 + y_per_period * e) - coupon_payment * w
        else:
            # Price = sum of PV of coupons + PV of redemption
            # Discount factor for first partial period
            df_first = (1.0 + y_per_period) ** e
            price = 0.0
            for k in range(1, remaining_coupons + 1):
                price += coupon_payment / ((1.0 + y_per_period) ** (k - 1) * df_first)
            price += rv / ((1.0 + y_per_period) ** (remaining_coupons - 1) * df_first)

        # Accrued interest
        ai = coupon_payment * w

        return {'PRI': round(price, 6), 'AI': round(ai, 6)}

    def compute_bond_yield(self, sdt: date, cpn: float, rdt: date, rv: float,
                           price: float, act: bool = True, semi: bool = True,
                           max_iter: int = 200, tol: float = 1e-8) -> float:
        """
        Compute bond yield given price using Newton-Raphson.
        Returns yield as annual percentage.
        """
        # Use bisection to bracket, then Newton-Raphson
        def price_at_yld(y):
            try:
                return self.compute_bond_price(sdt, cpn, rdt, rv, y, act, semi)['PRI']
            except Exception:
                return float('nan')

        # Bracket
        ylo, yhi = 0.001, 50.0
        plowest = price_at_yld(ylo)
        phighest = price_at_yld(yhi)

        target = price
        if plowest < target < phighest or phighest < target < plowest:
            pass  # bracketed
        else:
            ylo, yhi = 0.0001, 100.0

        y = (ylo + yhi) / 2.0
        for _ in range(max_iter):
            p = price_at_yld(y)
            if math.isnan(p):
                break
            diff = p - target
            if abs(diff) < tol:
                break
            # Numerical derivative
            dy = y * 0.0001 + 1e-6
            dp = price_at_yld(y + dy) - p
            if abs(dp) < 1e-12:
                break
            y = y - diff / (dp / dy)
            y = max(0.0001, min(y, 100.0))

        return round(y, 6)

    # =======================================================================
    # DEPRECIATION WORKSHEET
    # =======================================================================

    def compute_depreciation(self, method: str, lif: float, m01: float,
                              cst: float, sal: float, yr: int,
                              db_rate: float = 200.0) -> dict:
        """
        Compute depreciation for a given year.
        Returns dict with DEP, RBV (remaining book value), RDV (remaining depreciable value).

        method: 'SL', 'SYD', 'DB', 'DBX'
        lif:    asset life in years
        m01:    starting month (integer part) + fractional start of month
        cst:    cost of asset
        sal:    salvage value
        yr:     year to compute (1-based)
        db_rate: declining balance rate (e.g., 200 for double-declining)
        """
        depreciable = cst - sal

        # First-year fraction based on m01
        # m01 integer = starting month, decimal = fraction into month
        month_start = int(m01)
        month_frac = m01 - month_start
        # Fraction of year remaining after start
        months_used_first_yr = 12 - (month_start - 1) - month_frac
        first_yr_frac = months_used_first_yr / 12.0

        if method == 'SL':
            annual_dep = depreciable / lif
            if yr == 1:
                dep = annual_dep * first_yr_frac
            elif yr <= math.ceil(lif + (1 - first_yr_frac)):
                # Last partial year
                dep = min(annual_dep * (1 - first_yr_frac)
                          if yr == math.ceil(lif) + 1 else annual_dep,
                          depreciable)
                # Simpler: compute accumulated and cap
            else:
                dep = 0.0

            # Compute accumulated depreciation up to end of year yr
            total_dep = 0.0
            for y in range(1, yr + 1):
                if y == 1:
                    d = annual_dep * first_yr_frac
                else:
                    d = annual_dep
                total_dep += d
            total_dep = min(total_dep, depreciable)
            dep = total_dep - min(sum(annual_dep * first_yr_frac if y == 1
                                      else annual_dep for y in range(1, yr)), depreciable)
            dep = max(0.0, dep)

        elif method == 'SYD':
            lif_int = int(lif)
            syd_sum = lif_int * (lif_int + 1) / 2

            def syd_frac(y):
                return (lif_int - y + 1) / syd_sum

            # SYD with partial first year
            if yr == 1:
                dep = depreciable * syd_frac(1) * first_yr_frac
            else:
                dep = (depreciable * syd_frac(yr - 1) * (1 - first_yr_frac) +
                       depreciable * syd_frac(yr) * first_yr_frac)

        elif method in ('DB', 'DBX'):
            db_pct = db_rate / (lif * 100.0)
            rbv = cst
            for y in range(1, yr):
                if method == 'DBX':
                    sl_dep = rbv / (lif - y + 1) if (lif - y + 1) > 0 else 0
                    db_dep = rbv * db_pct
                    d = max(db_dep, sl_dep)
                else:
                    d = rbv * db_pct
                if y == 1:
                    d *= first_yr_frac
                rbv = max(rbv - d, sal)

            if method == 'DBX':
                sl_dep = rbv / (lif - yr + 1) if (lif - yr + 1) > 0 else 0
                db_dep = rbv * db_pct
                d = max(db_dep, sl_dep)
            else:
                d = rbv * db_pct
            if yr == 1:
                d *= first_yr_frac
            dep = min(d, rbv - sal)
            dep = max(dep, 0.0)

        else:
            raise ValueError(f"Unknown depreciation method: {method}")

        # Compute RBV and RDV by summing all years up to yr
        total_accumulated = 0.0
        for y in range(1, yr + 1):
            result_y = self.compute_depreciation(method, lif, m01, cst, sal, y, db_rate)
            total_accumulated += result_y['DEP']
            if y == yr:
                break

        # Direct computation for this year (avoid infinite recursion)
        rbv_final = cst - total_accumulated
        rdv_final = rbv_final - sal

        return {
            'DEP': round(dep, 2),
            'RBV': round(max(rbv_final, sal), 2),
            'RDV': round(max(rdv_final, 0), 2),
        }

    def compute_sl_depreciation(self, cst: float, sal: float, lif: float,
                                  m01: float = 1.0) -> list:
        """Return full straight-line depreciation schedule as list of dicts."""
        schedule = []
        total_years = math.ceil(lif) + (1 if m01 > 1 else 0)
        annual = (cst - sal) / lif
        rbv = cst

        month_start = int(m01)
        frac = m01 - month_start
        first_frac = (12 - (month_start - 1) - frac) / 12.0

        for yr in range(1, total_years + 1):
            if yr == 1:
                dep = annual * first_frac
            else:
                dep = annual
            dep = min(dep, rbv - sal)
            dep = max(dep, 0.0)
            rbv -= dep
            rdv = max(rbv - sal, 0.0)
            schedule.append({'YR': yr, 'DEP': round(dep, 2),
                              'RBV': round(rbv, 2), 'RDV': round(rdv, 2)})
            if rdv == 0:
                break
        return schedule

    # =======================================================================
    # STATISTICS WORKSHEET
    # =======================================================================

    def clear_stat_data(self):
        self.stat_data = []

    def add_stat_point(self, x: float, y: float = 1.0):
        """
        Add data point. For 1-variable stats: x=value, y=frequency.
        For 2-variable stats: x and y are the paired values.
        Up to 50 data points.
        """
        if len(self.stat_data) >= 50:
            raise ValueError("Maximum 50 data points")
        self.stat_data.append((float(x), float(y)))

    def compute_1var_stats(self) -> dict:
        """Compute 1-variable statistics. y is treated as frequency."""
        if not self.stat_data:
            raise ValueError("No data points")
        n = 0.0
        sum_x = 0.0
        sum_x2 = 0.0
        for x, freq in self.stat_data:
            n += freq
            sum_x += x * freq
            sum_x2 += x ** 2 * freq
        if n == 0:
            raise ValueError("Total frequency is zero")
        mean_x = sum_x / n
        # Sample std dev
        sx = math.sqrt((sum_x2 - n * mean_x ** 2) / (n - 1)) if n > 1 else 0.0
        # Population std dev
        ox = math.sqrt((sum_x2 - n * mean_x ** 2) / n)
        return {
            'n': n,
            'mean_x': round(mean_x, 6),
            'Sx': round(sx, 6),
            'sx': round(ox, 6),
            'sum_x': round(sum_x, 6),
            'sum_x2': round(sum_x2, 6),
        }

    def compute_2var_stats(self, method: str = 'LIN') -> dict:
        """Compute 2-variable regression statistics."""
        if len(self.stat_data) < 2:
            raise ValueError("Need at least 2 data points")

        xs = [p[0] for p in self.stat_data]
        ys = [p[1] for p in self.stat_data]

        # Transform data for regression
        if method == 'LIN':
            tx, ty = xs, ys
        elif method == 'Ln':
            if any(x <= 0 for x in xs):
                raise ValueError("Ln regression requires all X > 0")
            tx = [math.log(x) for x in xs]
            ty = ys
        elif method == 'EXP':
            if any(y <= 0 for y in ys):
                raise ValueError("EXP regression requires all Y > 0")
            tx = xs
            ty = [math.log(y) for y in ys]
        elif method == 'PWR':
            if any(x <= 0 for x in xs) or any(y <= 0 for y in ys):
                raise ValueError("PWR regression requires all X, Y > 0")
            tx = [math.log(x) for x in xs]
            ty = [math.log(y) for y in ys]
        else:
            raise ValueError(f"Unknown regression method: {method}")

        n = len(tx)
        sx = sum(tx)
        sy = sum(ty)
        sxy = sum(tx[i] * ty[i] for i in range(n))
        sx2 = sum(x ** 2 for x in tx)
        sy2 = sum(y ** 2 for y in ty)

        denom = n * sx2 - sx ** 2
        if abs(denom) < 1e-12:
            raise ValueError("Cannot compute regression (no variance in X)")

        b = (n * sxy - sx * sy) / denom  # slope
        a = (sy - b * sx) / n            # intercept

        # Transform back
        if method in ('EXP', 'PWR'):
            a = math.exp(a)

        # Correlation coefficient
        denom_r = math.sqrt((n * sx2 - sx ** 2) * (n * sy2 - sy ** 2))
        r_corr = (n * sxy - sx * sy) / denom_r if abs(denom_r) > 1e-12 else 0.0

        # 1-var stats on original data
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        sx_sample = math.sqrt(sum((x - mean_x) ** 2 for x in xs) / (n - 1)) if n > 1 else 0
        sy_sample = math.sqrt(sum((y - mean_y) ** 2 for y in ys) / (n - 1)) if n > 1 else 0

        return {
            'n': n,
            'a': round(a, 6),
            'b': round(b, 6),
            'r': round(r_corr, 6),
            'mean_x': round(mean_x, 6),
            'mean_y': round(mean_y, 6),
            'Sx': round(sx_sample, 6),
            'Sy': round(sy_sample, 6),
            'sum_x': round(sum(xs), 6),
            'sum_x2': round(sum(x ** 2 for x in xs), 6),
            'sum_y': round(sum(ys), 6),
            'sum_y2': round(sum(y ** 2 for y in ys), 6),
            'sum_xy': round(sum(xs[i] * ys[i] for i in range(n)), 6),
        }

    def predict_y(self, x_val: float, method: str = 'LIN') -> float:
        """Predict Y given X using regression."""
        stats = self.compute_2var_stats(method)
        a, b = stats['a'], stats['b']
        if method == 'LIN':
            return round(a + b * x_val, 6)
        elif method == 'Ln':
            return round(a + b * math.log(x_val), 6)
        elif method == 'EXP':
            return round(a * b ** x_val, 6)
        elif method == 'PWR':
            return round(a * x_val ** b, 6)
        raise ValueError(f"Unknown method: {method}")

    def predict_x(self, y_val: float, method: str = 'LIN') -> float:
        """Predict X given Y using regression."""
        stats = self.compute_2var_stats(method)
        a, b = stats['a'], stats['b']
        if method == 'LIN':
            if abs(b) < 1e-12:
                raise ValueError("Slope is zero")
            return round((y_val - a) / b, 6)
        elif method == 'Ln':
            return round(math.exp((y_val - a) / b), 6)
        elif method == 'EXP':
            return round(math.log(y_val / a) / math.log(b), 6)
        elif method == 'PWR':
            return round((y_val / a) ** (1.0 / b), 6)
        raise ValueError(f"Unknown method: {method}")

    # =======================================================================
    # PERCENT CHANGE / COMPOUND INTEREST WORKSHEET
    # =======================================================================

    def compute_percent_change(self, old: float, new: float) -> float:
        """Percent change from old to new."""
        if old == 0:
            raise ValueError("Old value cannot be zero")
        return round((new - old) / abs(old) * 100.0, 6)

    def compute_new_from_pct(self, old: float, pct_ch: float) -> float:
        """New value given old and percent change."""
        return round(old * (1 + pct_ch / 100.0), 6)

    def compute_old_from_pct(self, new: float, pct_ch: float) -> float:
        """Old value given new and percent change."""
        if pct_ch == -100:
            raise ValueError("Percent change of -100% gives undefined old value")
        return round(new / (1 + pct_ch / 100.0), 6)

    def compound_interest_new(self, old: float, rate: float, periods: float) -> float:
        """FV = PV * (1 + rate/100)^periods"""
        return round(old * (1 + rate / 100.0) ** periods, 6)

    def compound_interest_rate(self, old: float, new: float, periods: float) -> float:
        """Rate per period for compound growth."""
        if old <= 0:
            raise ValueError("Old value must be positive")
        if periods <= 0:
            raise ValueError("Periods must be positive")
        return round(((new / old) ** (1.0 / periods) - 1.0) * 100.0, 6)

    # =======================================================================
    # INTEREST CONVERSION WORKSHEET
    # =======================================================================

    def nominal_to_effective(self, nom: float, c_y: float) -> float:
        """Convert nominal rate (APR %) to effective annual rate (APY %)."""
        if c_y <= 0:
            raise ValueError("Compounding periods must be positive")
        eff = ((1.0 + nom / (100.0 * c_y)) ** c_y - 1.0) * 100.0
        return round(eff, 6)

    def effective_to_nominal(self, eff: float, c_y: float) -> float:
        """Convert effective annual rate (APY %) to nominal rate (APR %)."""
        if c_y <= 0:
            raise ValueError("Compounding periods must be positive")
        nom = ((1.0 + eff / 100.0) ** (1.0 / c_y) - 1.0) * c_y * 100.0
        return round(nom, 6)

    # =======================================================================
    # DATE WORKSHEET
    # =======================================================================

    def days_between_dates(self, dt1: date, dt2: date, method: str = 'ACT') -> float:
        """
        Compute days between two dates.
        method: 'ACT' (actual) or '360' (30/360).
        """
        if method == 'ACT':
            return abs((dt2 - dt1).days)
        else:
            return abs(self._days_between(dt1, dt2, '360'))

    def date_add_days(self, dt: date, days: float, method: str = 'ACT') -> date:
        """Compute date that is 'days' days from dt."""
        if method == 'ACT':
            return dt + timedelta(days=int(round(days)))
        else:
            # 30/360: approximate
            return dt + timedelta(days=int(round(days * 365.0 / 360.0)))

    def day_of_week(self, dt: date) -> str:
        """Return day of week name."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                'Friday', 'Saturday', 'Sunday']
        return days[dt.weekday()]

    # =======================================================================
    # PROFIT MARGIN WORKSHEET
    # =======================================================================

    def compute_profit_margin(self, cost: float, sell: float) -> float:
        """Gross profit margin = (sell - cost) / sell * 100"""
        if sell == 0:
            raise ValueError("Selling price cannot be zero")
        return round((sell - cost) / sell * 100.0, 6)

    def compute_sell_from_margin(self, cost: float, margin: float) -> float:
        """Selling price given cost and margin %."""
        if margin >= 100:
            raise ValueError("Margin must be less than 100%")
        return round(cost / (1.0 - margin / 100.0), 6)

    def compute_cost_from_margin(self, sell: float, margin: float) -> float:
        """Cost given selling price and margin %."""
        return round(sell * (1.0 - margin / 100.0), 6)

    def compute_markup(self, cost: float, sell: float) -> float:
        """Markup percentage = (sell - cost) / cost * 100"""
        if cost == 0:
            raise ValueError("Cost cannot be zero")
        return round((sell - cost) / cost * 100.0, 6)

    # =======================================================================
    # BREAKEVEN WORKSHEET
    # =======================================================================

    def breakeven_quantity(self, fc: float, p: float, vc: float) -> float:
        """Breakeven quantity = FC / (P - VC)"""
        if p == vc:
            raise ValueError("Price equals variable cost – no breakeven")
        return round(fc / (p - vc), 6)

    def breakeven_price(self, fc: float, vc: float, q: float, pft: float = 0.0) -> float:
        """Price = (FC + Profit) / Q + VC"""
        if q == 0:
            raise ValueError("Quantity cannot be zero")
        return round((fc + pft) / q + vc, 6)

    def breakeven_fc(self, p: float, vc: float, q: float, pft: float = 0.0) -> float:
        """Fixed cost = (P - VC) * Q - Profit"""
        return round((p - vc) * q - pft, 6)

    def breakeven_profit(self, fc: float, p: float, vc: float, q: float) -> float:
        """Profit = (P - VC) * Q - FC"""
        return round((p - vc) * q - fc, 6)

    # =======================================================================
    # UTILITY
    # =======================================================================

    def reset_all(self):
        """Reset all worksheets to defaults (like 2nd Reset Enter on the real calculator)."""
        self.__init__()

    def get_tvm_status(self) -> dict:
        return {
            'N': self.N, 'I/Y': self.I_Y, 'PV': self.PV,
            'PMT': self.PMT, 'FV': self.FV,
            'P/Y': self.P_Y, 'C/Y': self.C_Y,
            'Mode': 'BGN' if self.bgn else 'END',
        }