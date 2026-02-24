"""
Automated Accessibility Tests — BA II Plus Web Calculator
==========================================================
Uses Playwright + axe-core to run WCAG 2.1 AA checks against
every worksheet tab in the live app.

Requirements:
    pip install playwright axe-playwright-python pytest
    playwright install chromium

Usage:
    # Start the app first in a separate terminal:
    #   python app.py
    #
    # Then run:
    #   pytest test_accessibility.py -v

Environment:
    APP_URL  — override base URL (default: http://localhost:8052)
"""

import os
import time
import pytest
from playwright.sync_api import sync_playwright, Page
from axe_playwright_python.sync_playwright import Axe

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = os.environ.get("APP_URL", "http://localhost:8052")

# All 12 worksheet tabs — labels must match the tab text in app.py
WORKSHEETS = [
    "TVM",
    "Amortization",
    "Cash Flow",
    "Bond",
    "Depreciation",
    "Statistics",
    "Interest Conversion",
    "Percent Change",
    "Profit Margin",
    "Breakeven",
    "Date",
    "Memory",
]

# axe rules to enforce — maps to WCAG 2.1 AA
AXE_OPTIONS = {
    "runOnly": {
        "type": "tag",
        "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"],
    }
}

# Known acceptable violations to exclude (add any false positives here)
EXCLUDE_RULES = set()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def wait_for_app(page: Page, timeout: int = 10) -> None:
    """Wait until the Dash app has fully loaded."""
    page.wait_for_selector(".tab-content", timeout=timeout * 1000)
    # Small extra buffer for Dash callbacks to settle
    time.sleep(0.5)


def navigate_to_worksheet(page: Page, worksheet: str) -> None:
    """Click the tab for the given worksheet and wait for content to load."""
    tab = page.get_by_role("tab", name=worksheet)
    tab.click()
    # Wait for the selected tab panel to become visible
    page.wait_for_selector("[role='tabpanel']:not([hidden])", timeout=5000)
    time.sleep(0.3)


def run_axe(page: Page) -> list:
    """Run axe-core on the current page state and return violations list."""
    axe = Axe()
    results = axe.run(page, options=AXE_OPTIONS)
    return results.response.get("violations", [])


def format_violations(violations: list) -> str:
    """Format axe violations into a readable string for pytest output."""
    if not violations:
        return "No violations"
    lines = []
    for v in violations:
        lines.append(f"\n  [{v['impact'].upper()}] {v['id']}: {v['description']}")
        for node in v.get("nodes", [])[:2]:  # show first 2 affected nodes
            lines.append(f"    → {node.get('html', '')[:120]}")
            for failure in node.get("failureSummary", "").split("\n")[:2]:
                if failure.strip():
                    lines.append(f"      {failure.strip()}")
    return "\n".join(lines)


def filter_violations(violations: list) -> list:
    """Remove any violations in the EXCLUDE_RULES set."""
    return [v for v in violations if v["id"] not in EXCLUDE_RULES]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser_page():
    """Session-scoped Playwright browser and page."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            has_touch=False,
        )
        page = context.new_page()
        page.goto(BASE_URL)
        wait_for_app(page)
        yield page
        browser.close()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHomePage:
    """Accessibility checks on the initial page load."""

    def test_page_has_no_critical_violations(self, browser_page):
        """No critical or serious axe violations on first load."""
        violations = filter_violations(run_axe(browser_page))
        critical = [v for v in violations if v["impact"] in ("critical", "serious")]
        assert not critical, (
            f"Critical/serious accessibility violations on home page:\n"
            f"{format_violations(critical)}"
        )

    def test_page_language_set(self, browser_page):
        """html[lang] must be set — required for screen readers."""
        lang = browser_page.evaluate("document.documentElement.lang")
        assert lang and lang.strip(), (
            "html element is missing a lang attribute. "
            "Screen readers need this to use the correct language engine."
        )

    def test_skip_navigation_link_exists(self, browser_page):
        """A skip nav link must be the first focusable element."""
        skip_link = browser_page.query_selector("a[href='#main-content'], a.skip-link")
        assert skip_link is not None, (
            "No skip navigation link found. "
            "Keyboard users need this to bypass repeated navigation."
        )

    def test_page_title_is_meaningful(self, browser_page):
        """Page title must be descriptive, not generic."""
        title = browser_page.title()
        assert title and len(title) > 5, f"Page title is too short or missing: '{title}'"
        generic = {"untitled", "home", "index", "page"}
        assert title.lower() not in generic, f"Page title is too generic: '{title}'"


class TestWorksheetAccessibility:
    """Per-worksheet axe scans across all 12 worksheets."""

    @pytest.mark.parametrize("worksheet", WORKSHEETS)
    def test_worksheet_no_critical_violations(self, browser_page, worksheet):
        """Each worksheet must have zero critical or serious axe violations."""
        navigate_to_worksheet(browser_page, worksheet)
        violations = filter_violations(run_axe(browser_page))
        critical = [v for v in violations if v["impact"] in ("critical", "serious")]
        assert not critical, (
            f"Critical/serious violations on '{worksheet}' worksheet:\n"
            f"{format_violations(critical)}"
        )

    @pytest.mark.parametrize("worksheet", WORKSHEETS)
    def test_worksheet_no_violations_at_all(self, browser_page, worksheet):
        """Strict mode: zero axe violations of any severity per worksheet."""
        navigate_to_worksheet(browser_page, worksheet)
        violations = filter_violations(run_axe(browser_page))
        assert not violations, (
            f"Accessibility violations on '{worksheet}' worksheet:\n"
            f"{format_violations(violations)}"
        )

    @pytest.mark.parametrize("worksheet", WORKSHEETS)
    def test_worksheet_tab_is_keyboard_accessible(self, browser_page, worksheet):
        """Each worksheet tab must be reachable and activatable via keyboard."""
        browser_page.goto(BASE_URL)
        wait_for_app(browser_page)

        browser_page.keyboard.press("Tab")
        found = False
        for _ in range(30):  # max 30 tab presses
            focused = browser_page.evaluate(
                "document.activeElement ? document.activeElement.textContent.trim() : ''"
            )
            if worksheet in focused:
                browser_page.keyboard.press("Enter")
                found = True
                break
            browser_page.keyboard.press("Tab")

        assert found, (
            f"Could not reach the '{worksheet}' tab via keyboard navigation. "
            "This blocks blind users from accessing this worksheet."
        )


class TestAriaAndSemantics:
    """Structural ARIA and semantic HTML checks."""

    def test_buttons_have_accessible_names(self, browser_page):
        """All buttons must have a non-empty accessible name."""
        browser_page.goto(BASE_URL)
        wait_for_app(browser_page)
        buttons = browser_page.query_selector_all("button")
        unnamed = []
        for btn in buttons:
            name = btn.get_attribute("aria-label") or btn.inner_text().strip()
            if not name:
                unnamed.append(btn.evaluate("el => el.outerHTML")[:100])
        assert not unnamed, (
            f"Buttons with no accessible name (screen readers will announce these as 'button'):\n"
            + "\n".join(f"  {b}" for b in unnamed[:5])
        )

    def test_inputs_have_labels(self, browser_page):
        """All visible inputs must be associated with a label."""
        all_violations = run_axe(browser_page)
        label_violations = [
            v for v in all_violations
            if v["id"] in ("label", "label-content-name-mismatch")
        ]
        assert not label_violations, (
            f"Input labelling violations:\n{format_violations(label_violations)}"
        )

    def test_colour_contrast(self, browser_page):
        """Text must meet WCAG AA contrast ratio (4.5:1 normal, 3:1 large text)."""
        all_violations = run_axe(browser_page)
        contrast_violations = [
            v for v in all_violations if v["id"] == "color-contrast"
        ]
        assert not contrast_violations, (
            f"Colour contrast violations:\n{format_violations(contrast_violations)}"
        )

    def test_heading_hierarchy(self, browser_page):
        """Headings must not skip levels (e.g. h1 → h3 with no h2)."""
        all_violations = run_axe(browser_page)
        heading_violations = [
            v for v in all_violations if v["id"] == "heading-order"
        ]
        assert not heading_violations, (
            f"Heading hierarchy violations:\n{format_violations(heading_violations)}"
        )

    def test_live_regions_present(self, browser_page):
        """Result areas must use aria-live so screen readers announce updates."""
        live_regions = browser_page.query_selector_all("[aria-live]")
        assert len(live_regions) > 0, (
            "No aria-live regions found. Screen readers won't announce "
            "calculation results when they update dynamically."
        )

    def test_tab_panels_have_correct_roles(self, browser_page):
        """Worksheet tabs must use role='tab' and role='tabpanel'."""
        tabs = browser_page.query_selector_all("[role='tab']")
        panels = browser_page.query_selector_all("[role='tabpanel']")
        assert len(tabs) >= len(WORKSHEETS), (
            f"Expected at least {len(WORKSHEETS)} tab elements, found {len(tabs)}"
        )
        assert len(panels) > 0, "No tabpanel elements found"
