"""
BA II Plus Financial Calculator — Accessible Web Application
WCAG 2.1 AA + WAI-ARIA 1.1 aligned  |  Dash 4 compatible

Run:  pip install dash dash-bootstrap-components
      python app.py  →  http://localhost:8052
"""

import math
import os
from datetime import date

import dash
from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc

try:
    from calculator import FinancialCalculator
except ImportError:
    from src.calculator import FinancialCalculator

# ── lang="en" on <html> ───────────────────────────────────────────────────────
INDEX_STRING = """<!DOCTYPE html>
<html lang="en">
<head>
  {%metas%}
  <title>{%title%}</title>
  {%favicon%}
  {%css%}
</head>
<body>
  {%app_entry%}
  <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>"""

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="BA II Plus — Accessible Financial Calculator",
    suppress_callback_exceptions=True,
    index_string=INDEX_STRING,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description",
         "content": "WCAG 2.1 AA accessible BA II Plus calculator for the CFA exam."},
    ],
)
server = app.server
calc = FinancialCalculator()

# Colour tokens used for inline style= props only.
# All class-based CSS is in src/assets/custom.css
C = {
    "bg":      "#0a0a0a",
    "surface": "#1a1a1a",
    "border":  "#555555",
    "amber":   "#ffb300",
    "amber_h": "#cc8f00",
    "text":    "#f5f5f5",
    "muted":   "#c0c0c0",
    "ok":      "#00e676",
    "err":     "#ff6d6d",
    "info":    "#40c4ff",
}


# ─────────────────────────────────────────────────────────────────────────────
# Component helpers
# ─────────────────────────────────────────────────────────────────────────────

def ws_input(label_text, input_id, type_="number",
             placeholder="", value=None, help_text="", aria_label=None):
    """Labelled input with optional help text. Label association via htmlFor."""
    hid = f"help-{input_id}"
    children = [
        html.Label(label_text, htmlFor=input_id),
        dcc.Input(
            id=input_id, type=type_,
            placeholder=placeholder, value=value,
            className="ws-input", debounce=False, step="any",
        ),
    ]
    if help_text:
        children.append(html.P(help_text, id=hid, className="help-text"))
    else:
        children.append(html.Span(id=hid))
    return html.Div(children, className="mb-3")


def compute_btn(label, btn_id):
    return html.Button(label, id=btn_id,
                       className="calc-btn btn-primary w-100 mb-2",
                       **{"aria-label": f"Compute: {label}"})


def clear_btn(label, btn_id):
    return html.Button(label, id=btn_id,
                       className="calc-btn btn-danger w-100 mb-2",
                       **{"aria-label": label})


def result_div(div_id, placeholder="Result will appear here."):
    """Live region for screen readers — role=status, aria-live=polite."""
    return html.Div(placeholder, id=div_id, className="result-box",
                    role="status",
                    **{"aria-live": "polite", "aria-atomic": "true",
                       "aria-label": "Computation result"})


def _kv(label, value):
    """Key-value row used in result panels."""
    return html.Div(className="amort-row", children=[
        html.Span(label, className="amort-label"),
        html.Span(value, className="amort-val"),
    ])


def _num_row(nums, ids):
    return dbc.Row([
        dbc.Col(html.Button(str(n), id=ids[i], className="calc-btn",
                            **{"aria-label": str(n)}))
        for i, n in enumerate(nums)
    ], className="g-1 mb-1")


def ok(msg):   return f"✓ {msg}"
def err(msg):  return f"⚠ Error: {msg}"
def info(msg): return f"ℹ {msg}"


# ─────────────────────────────────────────────────────────────────────────────
# Tab builders
# ─────────────────────────────────────────────────────────────────────────────

def build_basic_tab():
    return dcc.Tab(label="Basic Calc", value="basic",
                   className="dash-tab", selected_className="dash-tab--selected",
                   children=[html.Div([
        html.H2("Standard Calculator", className="section-heading mt-3"),

        html.Div(id="basic-display", children="0",
                 className="calc-display mb-2", role="status",
                 **{"aria-live": "polite", "aria-atomic": "true",
                    "aria-label": "Calculator display — current value"}),

        html.Div(id="basic-mode", className="mode-banner",
                 **{"aria-live": "polite", "aria-atomic": "true"},
                 children="Ready — enter a number, then choose an operation"),

        html.Div([
            html.Label("Direct Entry (optional)", htmlFor="basic-manual"),
            dcc.Input(
                id="basic-manual", type="text", value="",
                placeholder="Type a number, then press Enter or Set Display",
                className="ws-input", debounce=False,
            ),
            html.P("For keyboard and screen-reader workflows: type the number directly, "
                   "then press Enter or Set Display.", className="help-text"),
            dbc.Row([
                dbc.Col(html.Button("Set Display", id="basic-set", className="calc-btn",
                                    **{"aria-label": "Set basic calculator display from typed value"}), width=4),
            ], className="g-1 mb-2"),
        ], className="ws-card mb-2"),

        dbc.Row([
            dbc.Col([
                html.H3("Number Entry", className="section-heading"),
                _num_row([7, 8, 9], ["num-7", "num-8", "num-9"]),
                _num_row([4, 5, 6], ["num-4", "num-5", "num-6"]),
                _num_row([1, 2, 3], ["num-1", "num-2", "num-3"]),
                dbc.Row([
                    dbc.Col(html.Button("+/−", id="btn-sign", className="calc-btn",
                                        **{"aria-label": "Toggle positive or negative sign"})),
                    dbc.Col(html.Button("0", id="num-0", className="calc-btn",
                                        **{"aria-label": "Zero"})),
                    dbc.Col(html.Button(".", id="btn-dot", className="calc-btn",
                                        **{"aria-label": "Decimal point"})),
                ], className="g-1 mb-2"),

                html.H3("Operations", className="section-heading"),
                dbc.Row([
                    dbc.Col(html.Button("+",   id="op-add",  className="calc-btn", **{"aria-label": "Add"})),
                    dbc.Col(html.Button("−",   id="op-sub",  className="calc-btn", **{"aria-label": "Subtract"})),
                    dbc.Col(html.Button("×",   id="op-mul",  className="calc-btn", **{"aria-label": "Multiply"})),
                    dbc.Col(html.Button("÷",   id="op-div",  className="calc-btn", **{"aria-label": "Divide"})),
                ], className="g-1 mb-1"),
                dbc.Row([
                    dbc.Col(html.Button("x^y", id="op-pow",   className="calc-btn", **{"aria-label": "x to the power of y"})),
                    dbc.Col(html.Button("√x",  id="op-sqrt",  className="calc-btn", **{"aria-label": "Square root of x"})),
                    dbc.Col(html.Button("1/x", id="op-recip", className="calc-btn", **{"aria-label": "Reciprocal"})),
                    dbc.Col(html.Button("%",   id="op-pct",   className="calc-btn", **{"aria-label": "Percent — divide by 100"})),
                ], className="g-1 mb-1"),
                dbc.Row([
                    dbc.Col(html.Button("ln",  id="op-ln",   className="calc-btn", **{"aria-label": "Natural logarithm"})),
                    dbc.Col(html.Button("e^x", id="op-exp",  className="calc-btn", **{"aria-label": "e to the power of x"})),
                    dbc.Col(html.Button("n!",  id="op-fact", className="calc-btn", **{"aria-label": "Factorial of n"})),
                ], className="g-1 mb-1"),
                dbc.Row([
                    dbc.Col(html.Button("nCr", id="op-ncr", className="calc-btn", **{"aria-label": "Combinations n choose r"})),
                    dbc.Col(html.Button("nPr", id="op-npr", className="calc-btn", **{"aria-label": "Permutations n P r"})),
                ], className="g-1 mb-2"),

                dbc.Row([
                    dbc.Col(html.Button("=",   id="btn-equals", className="calc-btn btn-primary",
                                        **{"aria-label": "Equals — compute result"}), width=4),
                    dbc.Col(html.Button("CE",  id="btn-ce",  className="calc-btn",
                                        **{"aria-label": "Clear current entry"}), width=4),
                    dbc.Col(html.Button("CLR", id="btn-clr", className="calc-btn btn-danger",
                                        **{"aria-label": "Clear all"}), width=4),
                ], className="g-1 mb-3"),

                html.H3("Memory Slots 0 to 9", id="mem-grp-lbl",
                        className="section-heading"),
                html.Div([
                    dbc.Row([dbc.Col([
                        html.Label("Memory slot (0–9)", htmlFor="mem-slot"),
                        dcc.Input(id="mem-slot", type="number", min=0, max=9,
                                  value=0, className="ws-input", step=1),
                        html.P("Which slot to use for the next STO or RCL operation.",
                               id="help-mem-slot", className="help-text"),
                    ])], className="mb-2"),
                    dbc.Row([
                        dbc.Col(html.Button("STO", id="mem-sto",  className="calc-btn",
                                            **{"aria-label": "Store displayed value to memory slot"})),
                        dbc.Col(html.Button("RCL", id="mem-rcl",  className="calc-btn",
                                            **{"aria-label": "Recall value from memory slot"})),
                        dbc.Col(html.Button("M+",  id="mem-madd", className="calc-btn",
                                            **{"aria-label": "Add displayed value to memory slot"})),
                        dbc.Col(html.Button("M−",  id="mem-msub", className="calc-btn",
                                            **{"aria-label": "Subtract displayed value from memory slot"})),
                        dbc.Col(html.Button("MCL", id="mem-mcl",  className="calc-btn btn-danger",
                                            **{"aria-label": "Clear memory slot to zero"})),
                    ], className="g-1"),
                ], role="group", **{"aria-labelledby": "mem-grp-lbl"}),

            ], width=12, lg=6),

            dbc.Col([
                html.H3("How to Use This Calculator", className="section-heading mt-3"),
                html.Div([
                      html.P("You can use on-screen buttons or type directly in Direct Entry. "
                          "Press Tab to move, Enter or Space to activate controls. "
                          "Every result is announced to screen readers."),
                    html.Hr(style={"border-color": C["border"], "margin": "10px 0"}),
                    html.P([html.Strong("DISPLAY — "), "Shows the current number or result."]),
                    html.P([html.Strong("MODE BAR — "), "Describes what the next press will do."]),
                    html.P([html.Strong("CE — "), "Clears only the current entry."]),
                    html.P([html.Strong("CLR — "), "Resets everything to zero."]),
                    html.P([html.Strong("nCr / nPr — "), "Enter n, press button, enter r, press ="]),
                    html.P([html.Strong("STO / RCL — "), "Select slot 0–9, then STO or RCL."]),
                    html.Hr(style={"border-color": C["border"], "margin": "10px 0"}),
                    html.P("All 12 BA II Plus worksheets are in the tabs above.",
                           style={"color": C["info"]}),
                ], className="ws-card"),
            ], width=12, lg=6),
        ]),
    ], className="p-3")])


def build_tvm_tab():
    return dcc.Tab(label="TVM", value="tvm",
                   className="dash-tab", selected_className="dash-tab--selected",
                   children=[html.Div([
        html.H2("Time Value of Money Worksheet", className="section-heading mt-3"),
        html.P("Enter known values, then click Compute for the unknown. "
               "Outflows (money you pay) are negative; inflows are positive.",
               className="help-text mb-3"),

        html.Div([
            html.H3("Settings"),
            dbc.Row([
                dbc.Col(ws_input("P/Y — Payments per Year", "tvm-py", value=12,
                                 help_text="12=monthly, 4=quarterly, 2=semi-annual, 1=annual"), width=6),
                dbc.Col(ws_input("C/Y — Compounding Periods per Year", "tvm-cy", value=12,
                                 help_text="Usually equals P/Y."), width=6),
            ]),
            html.Div([
                html.Label("Payment Timing", id="bgn-lbl"),
                dcc.RadioItems(id="tvm-bgn",
                    options=[{"label": " END — end of period (most loans)", "value": "END"},
                             {"label": " BGN — start of period (leases, annuities due)", "value": "BGN"}],
                    value="END",
                    inputStyle={"margin-right": "6px"},
                    labelStyle={"color": C["text"], "display": "block", "margin-bottom": "4px"}),
            ], role="group", **{"aria-labelledby": "bgn-lbl"}, className="mb-2"),
        ], className="ws-card"),

        html.Div([
            html.H3("TVM Variables"),
            dbc.Row([
                dbc.Col(ws_input("N — Number of Periods", "tvm-n",
                                 help_text="Total payment periods. Tip: years × P/Y."), width=6),
                dbc.Col(ws_input("I/Y — Annual Interest Rate (%)", "tvm-iy",
                                 help_text="Enter as a percentage, e.g. 5.5 for 5.5%."), width=6),
            ]),
            dbc.Row([
                dbc.Col(ws_input("PV — Present Value ($)", "tvm-pv",
                                 help_text="Loan amount (positive) or deposit (negative)."), width=6),
                dbc.Col(ws_input("PMT — Payment ($)", "tvm-pmt",
                                 help_text="Regular payment. Negative for payments you make."), width=6),
            ]),
            dbc.Row([
                dbc.Col(ws_input("FV — Future Value ($)", "tvm-fv",
                                 help_text="Enter 0 for a fully amortising loan."), width=6),
            ]),
        ], className="ws-card"),

        html.Div([
            html.H3("Compute"),
            html.P("Click the button for the variable you want to solve.",
                   className="help-text mb-2"),
            dbc.Row([
                dbc.Col(compute_btn("Compute N",   "cpt-n")),
                dbc.Col(compute_btn("Compute I/Y", "cpt-iy")),
                dbc.Col(compute_btn("Compute PV",  "cpt-pv")),
                dbc.Col(compute_btn("Compute PMT", "cpt-pmt")),
                dbc.Col(compute_btn("Compute FV",  "cpt-fv")),
            ], className="g-2"),
            dbc.Row([dbc.Col(clear_btn("2nd CLR TVM — Reset All Defaults", "tvm-clr"), width=8)],
                    className="mt-2"),
        ], className="ws-card"),

        result_div("tvm-result", "TVM result will appear here after computing."),
    ], className="p-3")])


def build_amort_tab():
    return dcc.Tab(label="Amort", value="amort",
                   className="dash-tab", selected_className="dash-tab--selected",
                   children=[html.Div([
        html.H2("Amortization Worksheet", className="section-heading mt-3"),
        html.P("First compute PMT in the TVM worksheet, then enter a payment range.",
               className="help-text mb-3"),
        html.Div([
            html.H3("Payment Range"),
            dbc.Row([
                dbc.Col(ws_input("P1 — First Payment", "amort-p1", value=1,
                                 help_text="First payment number in the range."), width=6),
                dbc.Col(ws_input("P2 — Last Payment",  "amort-p2", value=12,
                                 help_text="Last payment number. Must be ≥ P1."), width=6),
            ]),
            compute_btn("Compute Amortization (BAL, PRN, INT)", "cpt-amort"),
        ], className="ws-card"),
        result_div("amort-result", "Amortization results will appear here."),
    ], className="p-3")])


def build_cf_tab():
    return dcc.Tab(label="Cash Flow", value="cashflow",
                   className="dash-tab", selected_className="dash-tab--selected",
                   children=[html.Div([
        html.H2("Cash Flow Worksheet — NPV and IRR", className="section-heading mt-3"),
        html.P("Enter CF0 and up to 24 subsequent cash flows. "
               "Negative = outflows, positive = inflows.",
               className="help-text mb-3"),
        html.Div([
            html.H3("Enter Cash Flows"),
            ws_input("CF0 — Initial Cash Flow ($)", "cf-cf0",
                     help_text="Up-front investment cost. Usually negative."),
            dbc.Row([
                dbc.Col(ws_input("Cash Flow Amount ($)", "cf-amount",
                                 help_text="Amount for C01–C24."), width=6),
                dbc.Col(ws_input("Frequency (1–9999)", "cf-freq", value=1,
                                 help_text="Number of consecutive identical periods."), width=6),
            ]),
            dbc.Row([
                dbc.Col(html.Button("Add Cash Flow", id="cf-add",
                                    className="calc-btn btn-primary",
                                    **{"aria-label": "Add cash flow to list"}), width=6),
                dbc.Col(clear_btn("Clear All Cash Flows", "cf-clr"), width=6),
            ], className="g-2"),
            html.Div(id="cf-list", className="info-box mt-2",
                     role="status",
                     **{"aria-live": "polite", "aria-label": "List of entered cash flows"},
                     children="No cash flows entered yet."),
        ], className="ws-card"),
        html.Div([
            html.H3("Compute NPV and IRR"),
            ws_input("Discount Rate — I (%)", "cf-disc",
                     help_text="Required return per period, e.g. 10 for 10%."),
            dbc.Row([
                dbc.Col(compute_btn("Compute NPV", "cpt-npv")),
                dbc.Col(compute_btn("Compute IRR", "cpt-irr")),
            ], className="g-2"),
        ], className="ws-card"),
        result_div("cf-result", "NPV or IRR result will appear here."),
    ], className="p-3")])


def build_bond_tab():
    return dcc.Tab(label="Bond", value="bond",
                   className="dash-tab", selected_className="dash-tab--selected",
                   children=[html.Div([
        html.H2("Bond Worksheet", className="section-heading mt-3"),
        html.P("Computes price (PRI), yield (YLD), and accrued interest (AI). "
               "Dates as YYYY-MM-DD.", className="help-text mb-3"),
        html.Div([
            html.H3("Bond Data"),
            dbc.Row([
                dbc.Col(ws_input("Settlement Date (SDT)", "bond-sdt", type_="text",
                                 placeholder="YYYY-MM-DD",
                                 help_text="Date bond changes hands."), width=6),
                dbc.Col(ws_input("Redemption Date (RDT)", "bond-rdt", type_="text",
                                 placeholder="YYYY-MM-DD",
                                 help_text="Maturity or call date."), width=6),
            ]),
            dbc.Row([
                dbc.Col(ws_input("Annual Coupon Rate — CPN (%)", "bond-cpn",
                                 help_text="Annual coupon as % of par, e.g. 7 for 7%."), width=6),
                dbc.Col(ws_input("Redemption Value — RV (% of par)", "bond-rv", value=100,
                                 help_text="100 for maturity; call price for callable bonds."), width=6),
            ]),
            dbc.Row([
                dbc.Col(html.Div([
                    html.Label("Day-Count Method", id="bond-dc-lbl"),
                    dcc.RadioItems(id="bond-daycount",
                        options=[{"label": " ACT/ACT", "value": "ACT"},
                                 {"label": " 30/360",  "value": "360"}],
                        value="ACT",
                        inputStyle={"margin-right": "6px"},
                        labelStyle={"color": C["text"], "display": "block",
                                    "margin-bottom": "4px"}),
                ], role="group", **{"aria-labelledby": "bond-dc-lbl"}), width=6),
                dbc.Col(html.Div([
                    html.Label("Coupon Frequency", id="bond-freq-lbl"),
                    dcc.RadioItems(id="bond-freq",
                        options=[{"label": " Semiannual (2/Y)", "value": "SEMI"},
                                 {"label": " Annual (1/Y)",     "value": "ANN"}],
                        value="SEMI",
                        inputStyle={"margin-right": "6px"},
                        labelStyle={"color": C["text"], "display": "block",
                                    "margin-bottom": "4px"}),
                ], role="group", **{"aria-labelledby": "bond-freq-lbl"}), width=6),
            ], className="mb-2"),
        ], className="ws-card"),
        html.Div([
            html.H3("Compute"),
            dbc.Row([
                dbc.Col(ws_input("YLD — Yield (%) to compute PRI", "bond-yld",
                                 help_text="Enter known yield to compute price."), width=6),
                dbc.Col(ws_input("PRI — Price to compute YLD (per $100)", "bond-pri",
                                 help_text="Enter known price to compute yield."), width=6),
            ]),
            dbc.Row([
                dbc.Col(compute_btn("Compute PRI given YLD", "cpt-bond-pri")),
                dbc.Col(compute_btn("Compute YLD given PRI", "cpt-bond-yld")),
            ], className="g-2"),
        ], className="ws-card"),
        result_div("bond-result", "Bond price or yield will appear here."),
    ], className="p-3")])


def build_dep_tab():
    return dcc.Tab(label="Depreciation", value="dep",
                   className="dash-tab", selected_className="dash-tab--selected",
                   children=[html.Div([
        html.H2("Depreciation Worksheet", className="section-heading mt-3"),
        html.Div([
            html.H3("Setup"),
            dbc.Row([
                dbc.Col([
                    html.Label("Depreciation Method", htmlFor="dep-method"),
                    dcc.Dropdown(id="dep-method",
                        options=[
                            {"label": "Straight-Line (SL)",         "value": "SL"},
                            {"label": "Sum-of-Years-Digits (SYD)",   "value": "SYD"},
                            {"label": "Declining Balance (DB)",      "value": "DB"},
                            {"label": "DB with Crossover to SL (DBX)","value": "DBX"},
                        ],
                        value="SL", clearable=False,
                        style={"background": "#111", "color": "#fff"}),
                    html.P("DB and DBX require a rate. Default is 200.",
                           id="help-dep-method", className="help-text"),
                ], width=6),
                dbc.Col(ws_input("DB Rate (%) — for DB/DBX only", "dep-dbrate", value=200,
                                 help_text="200 = double-declining balance."), width=6),
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(ws_input("LIF — Asset Life (years)", "dep-lif",
                                 help_text="e.g. 5 or 31.5"), width=6),
                dbc.Col(ws_input("M01 — Starting Month", "dep-m01", value=1,
                                 help_text="1–12. Add decimal for mid-month, e.g. 3.5 = mid-March."), width=6),
            ]),
            dbc.Row([
                dbc.Col(ws_input("CST — Cost of Asset ($)", "dep-cst"), width=6),
                dbc.Col(ws_input("SAL — Salvage Value ($)", "dep-sal", value=0), width=6),
            ]),
            ws_input("YR — Year to Compute", "dep-yr", value=1,
                     help_text="Enter 1 for first year. Use 'Next Year' to advance."),
            compute_btn("Compute DEP, RBV, and RDV for This Year", "cpt-dep"),
            html.Button("Compute Next Year (YR + 1)", id="cpt-dep-next",
                        className="calc-btn w-100 mb-2",
                        **{"aria-label": "Compute depreciation for the next year"}),
            clear_btn("Clear Depreciation Worksheet", "dep-clr"),
        ], className="ws-card"),
        result_div("dep-result", "Depreciation results will appear here."),
    ], className="p-3")])


def build_stats_tab():
    return dcc.Tab(label="Statistics", value="stats",
                   className="dash-tab", selected_className="dash-tab--selected",
                   children=[html.Div([
        html.H2("Statistics Worksheet", className="section-heading mt-3"),
        html.Div([
            html.H3("Data Entry"),
            html.P("1-Variable: X = value, Y = frequency. 2-Variable: X and Y paired.",
                   className="help-text mb-2"),
            dbc.Row([
                dbc.Col(ws_input("X Value", "stat-x",
                                 help_text="The X data value."), width=6),
                dbc.Col(ws_input("Y Value or Frequency", "stat-y", value=1,
                                 help_text="Y value for 2-variable, or frequency for 1-variable."), width=6),
            ]),
            dbc.Row([
                dbc.Col(html.Button("Add Data Point", id="stat-add",
                                    className="calc-btn btn-primary",
                                    **{"aria-label": "Add data point"}), width=6),
                dbc.Col(clear_btn("Clear All Data", "stat-clr"), width=6),
            ], className="g-2 mb-2"),
            html.Div(id="stat-count", className="info-box",
                     role="status",
                     **{"aria-live": "polite", "aria-label": "Data point count"},
                     children="0 data points entered."),
        ], className="ws-card"),
        html.Div([
            html.H3("Compute"),
            dbc.Row([
                dbc.Col(html.Div([
                    html.Label("Analysis Method", id="stat-meth-lbl"),
                    dcc.RadioItems(id="stat-method",
                        options=[
                            {"label": " 1-Variable statistics",    "value": "1-V"},
                            {"label": " Linear regression (LIN)",  "value": "LIN"},
                            {"label": " Logarithmic regression (Ln)", "value": "Ln"},
                            {"label": " Exponential regression (EXP)", "value": "EXP"},
                            {"label": " Power regression (PWR)",   "value": "PWR"},
                        ],
                        value="1-V",
                        inputStyle={"margin-right": "6px"},
                        labelStyle={"color": C["text"], "display": "block",
                                    "margin-bottom": "4px"}),
                ], role="group", **{"aria-labelledby": "stat-meth-lbl"}), width=6),
                dbc.Col([
                    html.H3("Regression Prediction (optional)"),
                    ws_input("X′ — enter X to predict Y′", "stat-xprime"),
                    ws_input("Y′ — enter Y to predict X′", "stat-yprime"),
                ], width=6),
            ], className="mb-2"),
            compute_btn("Compute Statistical Results", "cpt-stats"),
        ], className="ws-card"),
        result_div("stats-result", "Statistical results will appear here."),
    ], className="p-3")])


def build_iconv_tab():
    return dcc.Tab(label="Int. Conv.", value="iconv",
                   className="dash-tab", selected_className="dash-tab--selected",
                   children=[html.Div([
        html.H2("Interest Conversion Worksheet", className="section-heading mt-3"),
        html.P("Converts between Nominal (APR) and Effective annual rate (APY).",
               className="help-text mb-3"),
        html.Div([
            html.H3("Rates"),
            dbc.Row([
                dbc.Col(ws_input("NOM — Nominal Rate / APR (%)", "iconv-nom",
                                 help_text="Annual rate before compounding."), width=6),
                dbc.Col(ws_input("EFF — Effective Rate / APY (%)", "iconv-eff",
                                 help_text="True annual return with compounding."), width=6),
            ]),
            ws_input("C/Y — Compounding Periods per Year", "iconv-cy", value=12,
                     help_text="12=monthly, 4=quarterly, 2=semi-annual, 1=annual."),
            dbc.Row([
                dbc.Col(compute_btn("Compute EFF given NOM", "cpt-eff")),
                dbc.Col(compute_btn("Compute NOM given EFF", "cpt-nom")),
            ], className="g-2"),
        ], className="ws-card"),
        result_div("iconv-result", "Conversion result will appear here."),
    ], className="p-3")])


def build_pct_tab():
    return dcc.Tab(label="% Change", value="pctchange",
                   className="dash-tab", selected_className="dash-tab--selected",
                   children=[html.Div([
        html.H2("Percent Change and Compound Interest Worksheet",
                className="section-heading mt-3"),
        html.P("Enter values for known variables and compute the unknown.",
               className="help-text mb-3"),
        html.Div([
            html.H3("Variables"),
            dbc.Row([
                dbc.Col(ws_input("OLD — Old Value or Cost", "pct-old",
                                 help_text="Starting value or cost."), width=6),
                dbc.Col(ws_input("NEW — New Value or Selling Price", "pct-new",
                                 help_text="Ending value or selling price."), width=6),
            ]),
            dbc.Row([
                dbc.Col(ws_input("%CH — Percent Change (%)", "pct-ch",
                                 help_text="Leave blank to compute."), width=6),
                dbc.Col(ws_input("#PD — Number of Periods", "pct-npd", value=1,
                                 help_text="1 for percent change. >1 for CAGR."), width=6),
            ]),
            dbc.Row([
                dbc.Col(compute_btn("Compute %CH",  "cpt-pctch"),  width=4),
                dbc.Col(compute_btn("Compute NEW",  "cpt-pctnew"), width=4),
                dbc.Col(compute_btn("Compute OLD",  "cpt-pctold"), width=4),
            ], className="g-2"),
        ], className="ws-card"),
        result_div("pct-result", "Percent change result will appear here."),
    ], className="p-3")])


def build_profit_tab():
    return dcc.Tab(label="Profit Margin", value="profit",
                   className="dash-tab", selected_className="dash-tab--selected",
                   children=[html.Div([
        html.H2("Profit Margin Worksheet", className="section-heading mt-3"),
        html.Div([
            html.H3("Gross Profit Margin"),
            dbc.Row([
                dbc.Col(ws_input("Cost ($)",           "pm-cost"), width=6),
                dbc.Col(ws_input("Selling Price ($)",  "pm-sell"), width=6),
            ]),
            ws_input("Profit Margin (%)", "pm-margin",
                     help_text="Gross margin = (Sell − Cost) ÷ Sell × 100"),
            dbc.Row([
                dbc.Col(compute_btn("Compute Margin", "cpt-margin"), width=4),
                dbc.Col(compute_btn("Compute Sell",   "cpt-sell"),   width=4),
                dbc.Col(compute_btn("Compute Cost",   "cpt-cost"),   width=4),
            ], className="g-2"),
            html.Hr(style={"border-color": C["border"], "margin": "14px 0"}),
            html.H3("Markup"),
            dbc.Row([
                dbc.Col(ws_input("Cost ($)",          "mu-cost"), width=6),
                dbc.Col(ws_input("Selling Price ($)", "mu-sell"), width=6),
            ]),
            compute_btn("Compute Markup Percentage", "cpt-markup"),
        ], className="ws-card"),
        result_div("profit-result", "Profit margin or markup result will appear here."),
    ], className="p-3")])


def build_be_tab():
    return dcc.Tab(label="Breakeven", value="breakeven",
                   className="dash-tab", selected_className="dash-tab--selected",
                   children=[html.Div([
        html.H2("Breakeven Worksheet", className="section-heading mt-3"),
        html.P("Enter any four of the five variables and compute the fifth.",
               className="help-text mb-3"),
        html.Div([
            html.H3("Variables"),
            dbc.Row([
                dbc.Col(ws_input("FC — Fixed Cost ($)",             "be-fc"), width=6),
                dbc.Col(ws_input("VC — Variable Cost per Unit ($)", "be-vc"), width=6),
            ]),
            dbc.Row([
                dbc.Col(ws_input("P — Price per Unit ($)",         "be-p"),         width=6),
                dbc.Col(ws_input("PFT — Target Profit ($)",        "be-pft", value=0), width=6),
            ]),
            ws_input("Q — Quantity (units)", "be-q"),
            dbc.Row([
                dbc.Col(compute_btn("Compute Q",   "cpt-be-q"),   width=3),
                dbc.Col(compute_btn("Compute P",   "cpt-be-p"),   width=3),
                dbc.Col(compute_btn("Compute FC",  "cpt-be-fc"),  width=3),
                dbc.Col(compute_btn("Compute PFT", "cpt-be-pft"), width=3),
            ], className="g-2"),
        ], className="ws-card"),
        result_div("be-result", "Breakeven result will appear here."),
    ], className="p-3")])


def build_date_tab():
    return dcc.Tab(label="Date", value="date",
                   className="dash-tab", selected_className="dash-tab--selected",
                   children=[html.Div([
        html.H2("Date Worksheet", className="section-heading mt-3"),
        html.P("Computes days between two dates, or a date a given number of days from a start.",
               className="help-text mb-3"),
        html.Div([
            html.H3("Date Inputs"),
            dbc.Row([
                dbc.Col(ws_input("DT1 — Start Date", "date-dt1", type_="text",
                                 placeholder="YYYY-MM-DD",
                                 help_text="Start date, e.g. 2024-06-15."), width=6),
                dbc.Col(ws_input("DT2 — End Date",   "date-dt2", type_="text",
                                 placeholder="YYYY-MM-DD",
                                 help_text="End date."), width=6),
            ]),
            dbc.Row([
                dbc.Col(html.Div([
                    html.Label("Day-Count Method", id="date-meth-lbl"),
                    dcc.RadioItems(id="date-method",
                        options=[{"label": " ACT — actual calendar days", "value": "ACT"},
                                 {"label": " 360 — 30/360 convention",    "value": "360"}],
                        value="ACT",
                        inputStyle={"margin-right": "6px"},
                        labelStyle={"color": C["text"], "display": "block",
                                    "margin-bottom": "4px"}),
                ], role="group", **{"aria-labelledby": "date-meth-lbl"}), width=6),
                dbc.Col(ws_input("DBD — Days to Add from DT1", "date-dbd",
                                 help_text="Days to add to DT1 to find DT2."), width=6),
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(compute_btn("Compute DBD (days between)", "cpt-dbd"), width=6),
                dbc.Col(compute_btn("Compute DT2 (DT1 + DBD days)", "cpt-dt2"), width=6),
            ], className="g-2"),
        ], className="ws-card"),
        result_div("date-result", "Date result will appear here."),
    ], className="p-3")])


# ─────────────────────────────────────────────────────────────────────────────
# Main layout
# ─────────────────────────────────────────────────────────────────────────────

app.layout = html.Div([
    # Skip navigation — first DOM element (WCAG 2.4.1)
    html.A("Skip to calculator", href="#main-content", className="skip-nav"),

    # Screen-reader live region
    html.Div(id="sr-announce", role="status",
             **{"aria-live": "polite", "aria-atomic": "true"},
             style={"position": "absolute", "left": "-9999px",
                    "width": "1px", "height": "1px", "overflow": "hidden"}),

    # State stores
    dcc.Store(id="basic-input", data=""),
    dcc.Store(id="basic-prev",  data=None),
    dcc.Store(id="basic-op",    data=None),
    dcc.Store(id="cf-flows-store", data=[]),

    # Header (banner landmark)
    html.Header([
        html.Div([
            html.H1("BA II PLUS",
                    **{"aria-label": "BA II Plus Financial Calculator"},
                    style={"font-family": "'Courier New', monospace",
                           "color": C["amber"], "font-size": "1.3rem",
                           "font-weight": "700", "letter-spacing": "2px", "margin": "0"}),
            html.Span("Accessible Financial Calculator",
                      className="app-subtitle", style={"margin-left": "12px"}),
        ], style={"display": "flex", "align-items": "center", "flex-wrap": "wrap"}),
    ], className="app-header", **{"aria-label": "Application header"}),

    # Main content (main landmark)
    html.Main([
        html.Span(id="main-content", **{"aria-hidden": "true"},
                  style={"position": "absolute", "top": "-4px"}),

        dcc.Tabs(id="main-tabs", value="basic",
                 children=[
                     build_basic_tab(), build_tvm_tab(),    build_amort_tab(),
                     build_cf_tab(),    build_bond_tab(),   build_dep_tab(),
                     build_stats_tab(), build_iconv_tab(),  build_pct_tab(),
                     build_profit_tab(),build_be_tab(),     build_date_tab(),
                 ],
                 colors={"border": C["border"], "primary": C["amber"],
                         "background": C["surface"]}),
    ], style={"max-width": "1200px", "margin": "0 auto", "padding": "0 12px 40px"},
       **{"aria-label": "Calculator main content"}),

    # Footer (contentinfo landmark)
    html.Footer(
        html.P("BA II Plus Accessible Calculator  |  WCAG 2.1 AA + WAI-ARIA 1.1 aligned ",
               style={"color": C["muted"], "text-align": "center",
                      "font-size": ".78rem", "padding": "12px"}),
        style={"border-top": f"1px solid {C['border']}", "margin-top": "40px"},
        **{"aria-label": "Application footer"}),

], style={"min-height": "100vh"})


# =============================================================================
# CALLBACKS — Basic Calculator
# =============================================================================

NUMERIC_INPUTS = [Input(f"num-{n}", "n_clicks") for n in range(10)]


@app.callback(
    [Output("basic-display", "children"), Output("basic-mode", "children"),
     Output("basic-input", "data"),       Output("basic-prev", "data"),
     Output("basic-op", "data"),          Output("sr-announce", "children")],
    NUMERIC_INPUTS + [
        Input("btn-sign", "n_clicks"),  Input("btn-dot",  "n_clicks"),
        Input("btn-equals","n_clicks"), Input("btn-ce",   "n_clicks"),
        Input("btn-clr",  "n_clicks"),
        Input("basic-set", "n_clicks"), Input("basic-manual", "n_submit"),
        Input("op-add",   "n_clicks"),  Input("op-sub",   "n_clicks"),
        Input("op-mul",   "n_clicks"),  Input("op-div",   "n_clicks"),
        Input("op-pow",   "n_clicks"),
        Input("op-sqrt",  "n_clicks"),  Input("op-recip", "n_clicks"),
        Input("op-pct",   "n_clicks"),  Input("op-ln",    "n_clicks"),
        Input("op-exp",   "n_clicks"),  Input("op-fact",  "n_clicks"),
        Input("op-ncr",   "n_clicks"),  Input("op-npr",   "n_clicks"),
        Input("mem-sto",  "n_clicks"),  Input("mem-rcl",  "n_clicks"),
        Input("mem-madd", "n_clicks"),  Input("mem-msub", "n_clicks"),
        Input("mem-mcl",  "n_clicks"),
    ],
    [State("basic-input",   "data"),
     State("basic-prev",    "data"),
     State("basic-op",      "data"),
     State("basic-display", "children"),
     State("basic-manual",  "value"),
     State("mem-slot",      "value")],
    prevent_initial_call=True,
)
def basic_calculator(
    n0, n1, n2, n3, n4, n5, n6, n7, n8, n9,
    ns, nd, neq, nce, nclr, nset, nmanual_submit,
    nadd, nsub, nmul, ndiv, npow,
    nsqrt, nrecip, npct, nln, nexp, nfact, nncr, nnpr,
    nmsto, nmrcl, nmmadd, nmmsub, nmmcl,
    cur_input, prev_val, cur_op, display_val, manual_val, mem_slot,
):
    tid = ctx.triggered_id
    if not tid:
        return dash.no_update

    cur_input   = cur_input  or ""
    display_num = display_val or "0"

    def _cur():
        return float(cur_input) if cur_input else float(display_num)

    def _fmt(v):
        if isinstance(v, int):      return str(v)
        if abs(v) > 1e12 or (abs(v) < 1e-8 and v != 0): return f"{v:.6e}"
        if v == int(v):             return f"{int(v)}"
        return f"{v:.8g}"

    for d in range(10):
        if tid == f"num-{d}":
            ni = cur_input + str(d)
            return ni, f"Entering: {ni}", ni, prev_val, cur_op, f"Digit {d}"

    if tid == "btn-dot":
        if "." not in cur_input:
            ni = (cur_input + ".") if cur_input else "0."
            return ni, f"Entering: {ni}", ni, prev_val, cur_op, "Decimal point"
        return dash.no_update

    if tid == "btn-sign":
        try:
            v = -_cur(); s = _fmt(v)
            return s, f"Value: {s}", s, prev_val, cur_op, ok(f"Sign toggled: {s}")
        except Exception as e:
            m = err(str(e)); return display_num, m, "", prev_val, None, m

    if tid in {"basic-set", "basic-manual"}:
        txt = (manual_val or "").strip()
        if not txt:
            m = err("Type a number first, then press Enter or Set Display.")
            return display_num, m, cur_input, prev_val, cur_op, m
        txt = txt.replace(",", "")
        if txt.startswith("(") and txt.endswith(")") and len(txt) > 2:
            txt = f"-{txt[1:-1]}"
        try:
            v = float(txt); s = _fmt(v)
            return s, f"Typed entry: {s}", s, prev_val, cur_op, ok(f"Typed entry set: {s}")
        except Exception:
            m = err("Invalid typed number. Example formats: 75000, -425.84, 1.5e3")
            return display_num, m, cur_input, prev_val, cur_op, m

    if tid == "btn-ce":  return "0", "Entry cleared",      "", prev_val, cur_op, "Entry cleared"
    if tid == "btn-clr": return "0", "Calculator cleared", "", None,     None,   "Calculator cleared"

    op_map = {"op-add": "+", "op-sub": "−", "op-mul": "×", "op-div": "÷",
              "op-pow": "^", "op-ncr": "nCr", "op-npr": "nPr"}
    if tid in op_map:
        try:
            v = _cur(); o = op_map[tid]
            return _fmt(v), f"[{_fmt(v)}] {o}", "", v, o, f"Stored {_fmt(v)} {o}"
        except Exception as e:
            m = err(str(e)); return display_num, m, "", prev_val, None, m

    unary = {
        "op-sqrt":  ("√",    lambda v: calc.square_root(v)),
        "op-recip": ("1/x",  lambda v: calc.reciprocal(v)),
        "op-pct":   ("%",    lambda v: v / 100),
        "op-ln":    ("ln",   lambda v: calc.natural_log(v)),
        "op-exp":   ("e^x",  lambda v: calc.exp(v)),
        "op-fact":  ("n!",   lambda v: calc.factorial(int(v))),
    }
    if tid in unary:
        lbl, fn = unary[tid]
        try:
            v = _cur(); r = fn(v); s = _fmt(r)
            return s, f"{lbl}({_fmt(v)}) = {s}", s, prev_val, cur_op, ok(f"{lbl} = {s}")
        except Exception as e:
            m = err(str(e)); return display_num, m, "", prev_val, None, m

    if tid == "btn-equals":
        if cur_op is None or prev_val is None:
            return dash.no_update
        try:
            L, R = float(prev_val), _cur()
            ops = {"+": calc.add, "−": calc.subtract, "×": calc.multiply,
                   "÷": calc.divide, "^": calc.power}
            if cur_op in ops:
                r = ops[cur_op](L, R)
            elif cur_op == "nCr": r = calc.combination(int(L), int(R))
            elif cur_op == "nPr": r = calc.permutation(int(L), int(R))
            else: return dash.no_update
            s = _fmt(r); calc.last_answer = r
            return s, f"Result: {s}", s, None, None, ok(f"Result: {s}")
        except Exception as e:
            m = err(str(e)); return display_num, m, "", None, None, m

    slot = int(mem_slot) if mem_slot is not None else 0
    if tid == "mem-sto":
        try:
            v = _cur(); calc.memory_store(slot, v)
            a = ok(f"Stored {_fmt(v)} in M{slot}")
            return display_num, a, cur_input, prev_val, cur_op, a
        except Exception as e:
            m = err(str(e)); return display_num, m, cur_input, prev_val, cur_op, m
    if tid == "mem-rcl":
        try:
            v = calc.memory_recall(slot); s = _fmt(v)
            a = ok(f"Recalled M{slot}: {s}")
            return s, f"Recalled M{slot} = {s}", s, prev_val, cur_op, a
        except Exception as e:
            m = err(str(e)); return display_num, m, cur_input, prev_val, cur_op, m
    if tid == "mem-madd":
        try:
            v = _cur(); calc.memory_add(slot, v)
            a = ok(f"Added {_fmt(v)} to M{slot}")
            return display_num, a, cur_input, prev_val, cur_op, a
        except Exception as e:
            m = err(str(e)); return display_num, m, cur_input, prev_val, cur_op, m
    if tid == "mem-msub":
        try:
            v = _cur(); calc.memory_subtract(slot, v)
            a = ok(f"Subtracted {_fmt(v)} from M{slot}")
            return display_num, a, cur_input, prev_val, cur_op, a
        except Exception as e:
            m = err(str(e)); return display_num, m, cur_input, prev_val, cur_op, m
    if tid == "mem-mcl":
        calc.memory_clear(slot)
        a = ok(f"M{slot} cleared")
        return display_num, f"M{slot} cleared", cur_input, prev_val, cur_op, a

    return dash.no_update


# =============================================================================
# CALLBACKS — TVM
# =============================================================================

@app.callback(
    [Output("tvm-result", "children"),  Output("tvm-result", "className"),
     Output("tvm-n", "value"),          Output("tvm-iy", "value"),
     Output("tvm-pv", "value"),         Output("tvm-pmt", "value"),
     Output("tvm-fv", "value"),
     Output("sr-announce", "children", allow_duplicate=True)],
    [Input("cpt-n",   "n_clicks"), Input("cpt-iy",  "n_clicks"),
     Input("cpt-pv",  "n_clicks"), Input("cpt-pmt", "n_clicks"),
     Input("cpt-fv",  "n_clicks"), Input("tvm-clr", "n_clicks")],
    [State("tvm-n",   "value"), State("tvm-iy",  "value"),
     State("tvm-pv",  "value"), State("tvm-pmt", "value"),
     State("tvm-fv",  "value"), State("tvm-py",  "value"),
     State("tvm-cy",  "value"), State("tvm-bgn", "value")],
    prevent_initial_call=True,
)
def handle_tvm(cn, ciy, cpv, cpmt, cfv, clr, n, iy, pv, pmt, fv, py, cy, bgn_val):
    tid = ctx.triggered_id
    if tid == "tvm-clr":
        calc.clear_tvm()
        m = info("TVM cleared. Defaults: N=0, I/Y=0, PV=0, PMT=0, FV=0, P/Y=1, C/Y=1, END.")
        return m, "info-box", 0, 0, 0, 0, 0, m
    try:
        calc.set_tvm(
            N=float(n)   if n   is not None else calc.N,
            I_Y=float(iy) if iy is not None else calc.I_Y,
            PV=float(pv)  if pv is not None else calc.PV,
            PMT=float(pmt) if pmt is not None else calc.PMT,
            FV=float(fv)  if fv is not None else calc.FV,
            P_Y=float(py) if py else 1.0,
            C_Y=float(cy) if cy else 1.0,
            bgn=(bgn_val == "BGN"),
        )
    except Exception as e:
        m = err(str(e)); return m, "error-box", n, iy, pv, pmt, fv, m
    cmap = {
        "cpt-n":   ("N",   calc.compute_N),
        "cpt-iy":  ("I/Y", calc.compute_I_Y),
        "cpt-pv":  ("PV",  calc.compute_PV),
        "cpt-pmt": ("PMT", calc.compute_PMT),
        "cpt-fv":  ("FV",  calc.compute_FV),
    }
    vl, fn = cmap[tid]
    try:
        r = fn(); r2 = round(r, 2); mode = "BGN" if calc.bgn else "END"
        detail = (f"{ok(f'Computed {vl} = {r2:,.4f}')}\n"
                  f"  N={calc.N} | I/Y={calc.I_Y}% | PV={calc.PV:,.2f} | "
                  f"PMT={calc.PMT:,.2f} | FV={calc.FV:,.2f} | P/Y={calc.P_Y} | {mode}")
        return (detail, "result-box",
                round(calc.N, 6), round(calc.I_Y, 6),
                round(calc.PV, 2), round(calc.PMT, 2), round(calc.FV, 2),
                ok(f"{vl} = {r2:,.4f}"))
    except Exception as e:
        m = err(f"Cannot compute {vl}: {e}")
        return m, "error-box", n, iy, pv, pmt, fv, m


# =============================================================================
# CALLBACKS — Amortization
# =============================================================================

@app.callback(
    [Output("amort-result", "children"),  Output("amort-result", "className"),
     Output("sr-announce", "children", allow_duplicate=True)],
    Input("cpt-amort", "n_clicks"),
    [State("amort-p1", "value"), State("amort-p2", "value")],
    prevent_initial_call=True,
)
def handle_amort(_, p1, p2):
    if p1 is None or p2 is None:
        m = err("Enter both P1 and P2 before computing.")
        return m, "error-box", m
    try:
        r = calc.amortization_schedule_simple(int(p1), int(p2))
        ann = ok(f"Payments {p1}–{p2}: BAL={r['BAL']:,.2f}, "
                 f"PRN={r['PRN']:,.2f}, INT={r['INT']:,.2f}")
        detail = html.Div([
            html.P(ok(f"Payments {p1} through {p2}"),
                   style={"color": C["ok"], "margin-bottom": "8px"}),
            _kv("BAL — Remaining Balance", f"${r['BAL']:>14,.2f}"),
            _kv("PRN — Principal Paid",    f"${r['PRN']:>14,.2f}"),
            _kv("INT — Interest Paid",     f"${r['INT']:>14,.2f}"),
            html.P(f"Next: P1={int(p2)+1}, P2={int(p2)+(int(p2)-int(p1)+1)}.",
                   className="help-text mt-2"),
        ])
        return detail, "result-box", ann
    except Exception as e:
        m = err(str(e)); return m, "error-box", m


# =============================================================================
# CALLBACKS — Cash Flow / NPV / IRR
# =============================================================================

@app.callback(
    [Output("cf-flows-store", "data"),  Output("cf-list",   "children"),
     Output("cf-result",  "children"), Output("cf-result",  "className"),
     Output("sr-announce", "children", allow_duplicate=True)],
    [Input("cf-add",  "n_clicks"), Input("cf-clr",  "n_clicks"),
     Input("cpt-npv", "n_clicks"), Input("cpt-irr", "n_clicks")],
    [State("cf-cf0",  "value"), State("cf-amount", "value"),
     State("cf-freq", "value"), State("cf-disc",   "value"),
     State("cf-flows-store", "data")],
    prevent_initial_call=True,
)
def handle_cf(nadd, nclr, nnpv, nirr, cf0, amount, freq, disc, stored):
    tid = ctx.triggered_id; stored = stored or []
    if tid == "cf-clr":
        calc.clear_cash_flows()
        m = info("All cash flows cleared.")
        return [], "No cash flows entered.", m, "info-box", m
    if tid == "cf-add":
        if cf0 is None and amount is None:
            m = err("Enter CF0 or a cash flow amount first.")
            return stored, _cf_list(stored), m, "error-box", m
        if cf0 is not None: calc.set_cf0(float(cf0))
        if amount is not None:
            f = int(freq) if freq else 1
            calc.add_cash_flow(float(amount), f)
            stored.append({"amount": float(amount), "freq": f})
        m = ok(f"Added. CF0={calc.cf0:.2f}, {len(calc.cash_flows)} additional flow(s).")
        return stored, _cf_list(stored), m, "info-box", m
    if tid == "cpt-npv":
        if disc is None:
            m = err("Enter a discount rate first.")
            return stored, _cf_list(stored), m, "error-box", m
        try:
            _sync_cf(cf0, stored); npv = calc.compute_npv(float(disc))
            d = ("Positive NPV — exceeds required return." if npv > 0
                 else "Negative NPV — falls short of required return.")
            m = ok(f"NPV at {disc}% = ${npv:,.4f}  ({d})")
            return stored, _cf_list(stored), m, "result-box", ok(f"NPV = ${npv:,.4f}")
        except Exception as e:
            m = err(str(e)); return stored, _cf_list(stored), m, "error-box", m
    if tid == "cpt-irr":
        try:
            _sync_cf(cf0, stored); irr = calc.compute_irr()
            m = ok(f"IRR = {irr:.4f}%")
            return stored, _cf_list(stored), m, "result-box", m
        except Exception as e:
            m = err(str(e)); return stored, _cf_list(stored), m, "error-box", m
    return stored, _cf_list(stored), info("Enter cash flows above."), "info-box", ""


def _sync_cf(cf0, stored):
    calc.clear_cash_flows()
    if cf0 is not None: calc.set_cf0(float(cf0))
    for s in stored: calc.add_cash_flow(s["amount"], s["freq"])


def _cf_list(stored):
    if not stored: return "No additional cash flows entered yet."
    lines = [f"CF0 = {calc.cf0:.2f}"] + [
        f"C{i+1:02d} = {s['amount']:.2f}  (F={s['freq']})"
        for i, s in enumerate(stored)]
    return html.Div([html.P(l, style={"margin": "2px 0",
                                       "font-family": "monospace"}) for l in lines])


# =============================================================================
# CALLBACKS — Bond
# =============================================================================

@app.callback(
    [Output("bond-result", "children"),  Output("bond-result", "className"),
     Output("sr-announce", "children", allow_duplicate=True)],
    [Input("cpt-bond-pri", "n_clicks"), Input("cpt-bond-yld", "n_clicks")],
    [State("bond-sdt", "value"),  State("bond-rdt",      "value"),
     State("bond-cpn", "value"),  State("bond-rv",       "value"),
     State("bond-yld", "value"),  State("bond-pri",      "value"),
     State("bond-daycount","value"), State("bond-freq",  "value")],
    prevent_initial_call=True,
)
def handle_bond(npri, nyld, sdt_s, rdt_s, cpn, rv, yld, pri, daycount, freq_val):
    tid = ctx.triggered_id
    try:
        sdt = date.fromisoformat(sdt_s); rdt = date.fromisoformat(rdt_s)
        cpn = float(cpn); rv = float(rv) if rv else 100.0
        act = (daycount == "ACT"); semi = (freq_val == "SEMI")
        if tid == "cpt-bond-pri":
            r = calc.compute_bond_price(sdt, cpn, rdt, rv, float(yld), act, semi)
            ann = ok(f"PRI = {r['PRI']:.4f} per $100 par")
            detail = html.Div([
                html.P(ann, style={"color": C["ok"], "margin-bottom": "8px"}),
                _kv("PRI — Clean Price",      f"${r['PRI']:.4f} per $100"),
                _kv("AI  — Accrued Interest", f"${r['AI']:.4f} per $100"),
                _kv("Full Price (Dirty)",      f"${r['PRI']+r['AI']:.4f} per $100"),
            ])
            return detail, "result-box", ann
        if tid == "cpt-bond-yld":
            y = calc.compute_bond_yield(sdt, cpn, rdt, rv, float(pri), act, semi)
            m = ok(f"YLD = {y:.4f}%"); return m, "result-box", m
    except Exception as e:
        m = err(str(e)); return m, "error-box", m
    return dash.no_update


# =============================================================================
# CALLBACKS — Depreciation
# =============================================================================

@app.callback(
    [Output("dep-result", "children"),  Output("dep-result", "className"),
     Output("dep-yr", "value"),
     Output("sr-announce", "children", allow_duplicate=True)],
    [Input("cpt-dep", "n_clicks"), Input("cpt-dep-next", "n_clicks"),
     Input("dep-clr", "n_clicks")],
    [State("dep-method", "value"), State("dep-lif",    "value"),
     State("dep-m01",    "value"), State("dep-cst",    "value"),
     State("dep-sal",    "value"), State("dep-yr",     "value"),
     State("dep-dbrate", "value")],
    prevent_initial_call=True,
)
def handle_dep(ncpt, nnext, nclr, method, lif, m01, cst, sal, yr, dbrate):
    tid = ctx.triggered_id
    if tid == "dep-clr":
        m = info("Depreciation worksheet cleared.")
        return m, "info-box", 1, m
    if lif is None or cst is None:
        m = err("Enter LIF (life) and CST (cost) before computing.")
        return m, "error-box", yr, m
    yr_use = int(yr) if yr else 1
    if tid == "cpt-dep-next": yr_use += 1
    try:
        if method == "SL":
            sch = calc.compute_sl_depreciation(
                float(cst), float(sal or 0), float(lif), float(m01 or 1))
            r = next((s for s in sch if s["YR"] == yr_use), None)
            if r is None:
                m = err(f"Year {yr_use} is beyond the asset's useful life.")
                return m, "error-box", yr_use, m
        else:
            r = calc.compute_depreciation(
                method, float(lif), float(m01 or 1),
                float(cst), float(sal or 0), yr_use, float(dbrate or 200))
        ann = ok(f"Year {yr_use}: DEP={r['DEP']:,.2f}, "
                 f"RBV={r['RBV']:,.2f}, RDV={r['RDV']:,.2f}")
        detail = html.Div([
            html.P(ok(f"Year {yr_use} — {method}"),
                   style={"color": C["ok"], "margin-bottom": "8px"}),
            _kv("DEP — Depreciation Expense",       f"${r['DEP']:,.2f}"),
            _kv("RBV — Remaining Book Value",        f"${r['RBV']:,.2f}"),
            _kv("RDV — Remaining Depreciable Value", f"${r['RDV']:,.2f}"),
        ])
        return detail, "result-box", yr_use, ann
    except Exception as e:
        m = err(str(e)); return m, "error-box", yr_use, m


# =============================================================================
# CALLBACKS — Statistics
# =============================================================================

@app.callback(
    [Output("stats-result", "children"),  Output("stats-result", "className"),
     Output("stat-count",   "children"),
     Output("sr-announce",  "children", allow_duplicate=True)],
    [Input("stat-add",  "n_clicks"), Input("stat-clr",  "n_clicks"),
     Input("cpt-stats", "n_clicks")],
    [State("stat-x",      "value"), State("stat-y",      "value"),
     State("stat-method", "value"),
     State("stat-xprime", "value"), State("stat-yprime", "value")],
    prevent_initial_call=True,
)
def handle_stats(nadd, nclr, ncpt, x_val, y_val, method, x_prime, y_prime):
    tid = ctx.triggered_id; count = len(calc.stat_data)
    if tid == "stat-clr":
        calc.clear_stat_data()
        m = info("Statistics worksheet cleared.")
        return m, "info-box", "0 data points entered.", m
    if tid == "stat-add":
        if x_val is None:
            m = err("Enter an X value first.")
            return m, "error-box", f"{count} data points.", m
        try:
            calc.add_stat_point(float(x_val),
                                float(y_val) if y_val is not None else 1.0)
            count = len(calc.stat_data)
            a = ok(f"Added ({x_val}, {y_val or 1}). Total: {count}.")
            return a, "info-box", f"{count} data points entered.", a
        except Exception as e:
            m = err(str(e)); return m, "error-box", f"{count} data points.", m
    if tid == "cpt-stats":
        try:
            if method == "1-V":
                s = calc.compute_1var_stats()
                rows = [_kv("n",  str(int(s["n"]))),
                        _kv("x̄",  f"{s['mean_x']:,.6f}"),
                        _kv("Sx", f"{s['Sx']:,.6f}"),
                        _kv("σx", f"{s['sx']:,.6f}"),
                        _kv("Σx", f"{s['sum_x']:,.6f}"),
                        _kv("Σx²",f"{s['sum_x2']:,.6f}")]
                ann = ok(f"1-V: n={int(s['n'])}, mean={s['mean_x']:.4f}, Sx={s['Sx']:.4f}")
            else:
                s = calc.compute_2var_stats(method)
                rows = [_kv("n", str(s["n"])),
                        _kv("a (intercept)", f"{s['a']:,.6f}"),
                        _kv("b (slope)",     f"{s['b']:,.6f}"),
                        _kv("r",             f"{s['r']:,.6f}"),
                        _kv("x̄",            f"{s['mean_x']:,.6f}"),
                        _kv("ȳ",            f"{s['mean_y']:,.6f}"),
                        _kv("Sx",            f"{s['Sx']:,.6f}"),
                        _kv("Sy",            f"{s['Sy']:,.6f}")]
                if x_prime is not None:
                    rows.append(_kv(f"Y′(X′={x_prime})",
                                    f"{calc.predict_y(float(x_prime), method):,.6f}"))
                if y_prime is not None:
                    rows.append(_kv(f"X′(Y′={y_prime})",
                                    f"{calc.predict_x(float(y_prime), method):,.6f}"))
                ann = ok(f"{method}: a={s['a']:.4f}, b={s['b']:.4f}, r={s['r']:.4f}")
            detail = html.Div([html.P(ann, style={"color": C["ok"],
                                                   "margin-bottom": "8px"})] + rows)
            return detail, "result-box", f"{count} data points.", ann
        except Exception as e:
            m = err(str(e)); return m, "error-box", f"{count} data points.", m
    return dash.no_update


# =============================================================================
# CALLBACKS — Interest Conversion
# =============================================================================

@app.callback(
    [Output("iconv-result", "children"), Output("iconv-result", "className"),
     Output("sr-announce",  "children", allow_duplicate=True)],
    [Input("cpt-eff", "n_clicks"), Input("cpt-nom", "n_clicks")],
    [State("iconv-nom", "value"), State("iconv-eff", "value"),
     State("iconv-cy",  "value")],
    prevent_initial_call=True,
)
def handle_iconv(neff, nnom, nom, eff, cy):
    tid = ctx.triggered_id
    try:
        cy = float(cy) if cy else 12.0
        if tid == "cpt-eff":
            r = calc.nominal_to_effective(float(nom), cy)
            m = ok(f"EFF (APY) = {r:.6f}%  (NOM={nom}%, C/Y={cy})")
        else:
            r = calc.effective_to_nominal(float(eff), cy)
            m = ok(f"NOM (APR) = {r:.6f}%  (EFF={eff}%, C/Y={cy})")
        return m, "result-box", m
    except Exception as e:
        m = err(str(e)); return m, "error-box", m


# =============================================================================
# CALLBACKS — Percent Change
# =============================================================================

@app.callback(
    [Output("pct-result", "children"), Output("pct-result", "className"),
     Output("pct-ch",  "value"),       Output("pct-new",  "value"),
     Output("pct-old", "value"),
     Output("sr-announce", "children", allow_duplicate=True)],
    [Input("cpt-pctch",  "n_clicks"), Input("cpt-pctnew", "n_clicks"),
     Input("cpt-pctold", "n_clicks")],
    [State("pct-old", "value"), State("pct-new", "value"),
     State("pct-ch",  "value"), State("pct-npd", "value")],
    prevent_initial_call=True,
)
def handle_pct(nc, nn, no, old, new, ch, npd):
    tid = ctx.triggered_id
    try:
        npd = float(npd) if npd else 1.0
        if tid == "cpt-pctch":
            r = (calc.compute_percent_change(float(old), float(new)) if npd == 1
                 else calc.compound_interest_rate(float(old), float(new), npd))
            m = ok(f"%CH = {r:.6f}%")
            return m, "result-box", round(r, 6), new, old, m
        elif tid == "cpt-pctnew":
            r = (calc.compute_new_from_pct(float(old), float(ch)) if npd == 1
                 else calc.compound_interest_new(float(old), float(ch), npd))
            m = ok(f"NEW = {r:.4f}")
            return m, "result-box", ch, round(r, 4), old, m
        elif tid == "cpt-pctold":
            r = calc.compute_old_from_pct(float(new), float(ch))
            m = ok(f"OLD = {r:.4f}")
            return m, "result-box", ch, new, round(r, 4), m
    except Exception as e:
        m = err(str(e)); return m, "error-box", ch, new, old, m
    return dash.no_update


# =============================================================================
# CALLBACKS — Profit Margin
# =============================================================================

@app.callback(
    [Output("profit-result", "children"), Output("profit-result", "className"),
     Output("sr-announce",   "children", allow_duplicate=True)],
    [Input("cpt-margin", "n_clicks"), Input("cpt-sell",   "n_clicks"),
     Input("cpt-cost",   "n_clicks"), Input("cpt-markup", "n_clicks")],
    [State("pm-cost",   "value"), State("pm-sell",  "value"),
     State("pm-margin", "value"), State("mu-cost",  "value"),
     State("mu-sell",   "value")],
    prevent_initial_call=True,
)
def handle_profit(nm, ns, nc, nmu, cost, sell, margin, mu_cost, mu_sell):
    tid = ctx.triggered_id
    try:
        if   tid == "cpt-margin":
            m = ok(f"Profit Margin = {calc.compute_profit_margin(float(cost), float(sell)):.4f}%")
        elif tid == "cpt-sell":
            m = ok(f"Selling Price = ${calc.compute_sell_from_margin(float(cost), float(margin)):,.4f}")
        elif tid == "cpt-cost":
            m = ok(f"Cost = ${calc.compute_cost_from_margin(float(sell), float(margin)):,.4f}")
        elif tid == "cpt-markup":
            m = ok(f"Markup = {calc.compute_markup(float(mu_cost), float(mu_sell)):.4f}%")
        else:
            return dash.no_update
        return m, "result-box", m
    except Exception as e:
        m = err(str(e)); return m, "error-box", m


# =============================================================================
# CALLBACKS — Breakeven
# =============================================================================

@app.callback(
    [Output("be-result",  "children"),  Output("be-result",  "className"),
     Output("sr-announce","children",  allow_duplicate=True)],
    [Input("cpt-be-q",   "n_clicks"), Input("cpt-be-p",   "n_clicks"),
     Input("cpt-be-fc",  "n_clicks"), Input("cpt-be-pft", "n_clicks")],
    [State("be-fc",  "value"), State("be-vc",  "value"),
     State("be-p",   "value"), State("be-pft", "value"),
     State("be-q",   "value")],
    prevent_initial_call=True,
)
def handle_be(nq, np_, nfc, npft, fc, vc, p, pft, q):
    tid = ctx.triggered_id
    try:
        fc  = float(fc)  if fc  is not None else 0.0
        vc  = float(vc)  if vc  is not None else 0.0
        p   = float(p)   if p   is not None else 0.0
        pft = float(pft) if pft is not None else 0.0
        q   = float(q)   if q   is not None else 0.0
        if   tid == "cpt-be-q":   m = ok(f"Q = {calc.breakeven_quantity(fc, p, vc):,.4f} units")
        elif tid == "cpt-be-p":   m = ok(f"P = ${calc.breakeven_price(fc, vc, q, pft):,.4f}")
        elif tid == "cpt-be-fc":  m = ok(f"FC = ${calc.breakeven_fc(p, vc, q, pft):,.4f}")
        elif tid == "cpt-be-pft": m = ok(f"PFT = ${calc.breakeven_profit(fc, p, vc, q):,.4f}")
        else: return dash.no_update
        return m, "result-box", m
    except Exception as e:
        m = err(str(e)); return m, "error-box", m


# =============================================================================
# CALLBACKS — Date
# =============================================================================

@app.callback(
    [Output("date-result", "children"),  Output("date-result", "className"),
     Output("sr-announce", "children",  allow_duplicate=True)],
    [Input("cpt-dbd", "n_clicks"), Input("cpt-dt2", "n_clicks")],
    [State("date-dt1",    "value"), State("date-dt2",    "value"),
     State("date-dbd",    "value"), State("date-method", "value")],
    prevent_initial_call=True,
)
def handle_date(ndbd, ndt2, dt1_s, dt2_s, dbd, method):
    tid = ctx.triggered_id
    try:
        if tid == "cpt-dbd":
            dt1 = date.fromisoformat(dt1_s); dt2 = date.fromisoformat(dt2_s)
            days = calc.days_between_dates(dt1, dt2, method)
            dow1 = calc.day_of_week(dt1); dow2 = calc.day_of_week(dt2)
            ann = ok(f"DBD = {days} days  ({method})")
            detail = html.Div([
                html.P(ann, style={"color": C["ok"], "margin-bottom": "8px"}),
                _kv("Days Between (DBD)", f"{days} days"),
                _kv(f"DT1 — {dt1_s}", dow1),
                _kv(f"DT2 — {dt2_s}", dow2),
                _kv("Method", method),
            ])
            return detail, "result-box", ann
        if tid == "cpt-dt2":
            dt1 = date.fromisoformat(dt1_s)
            r = calc.date_add_days(dt1, float(dbd)); dow = calc.day_of_week(r)
            m = ok(f"DT2 = {r.isoformat()} ({dow})"); return m, "result-box", m
    except Exception as e:
        m = err(str(e)); return m, "error-box", m
    return dash.no_update


# =============================================================================
# Entrypoint
# =============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8052))
    app.run(debug=True, host="0.0.0.0", port=port)