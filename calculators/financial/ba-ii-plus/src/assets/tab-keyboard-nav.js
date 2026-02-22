/**
 * Keyboard navigation for Dash dcc.Tabs — WAI-ARIA Tabs pattern
 *
 * Dash renders tab headers as plain <div> elements without arrow-key
 * navigation.  This script retrofits the standard ARIA tab pattern:
 *
 *   • Left / Right arrow  — move focus between tab headers
 *   • Home / End           — jump to first / last tab header
 *   • Enter / Space        — activate the focused tab
 *   • Alt + T              — jump focus to the currently-selected tab header
 *
 * It also sets role="tablist" on the tab-parent container and role="tab"
 * on each tab header so screen readers announce them correctly.
 */
(function () {
  "use strict";

  /* ── helpers ──────────────────────────────────────────────────────── */

  /** Return an ordered array of all tab header elements. */
  function getTabs() {
    var parent = document.querySelector(".tab-parent");
    if (!parent) return [];
    return Array.prototype.slice.call(
      parent.querySelectorAll(".tab, .tab--selected")
    );
  }

  /** Set ARIA attributes on the tab strip once Dash has rendered it. */
  function applyAriaRoles() {
    var parent = document.querySelector(".tab-parent");
    if (!parent || parent.getAttribute("role") === "tablist") return;

    parent.setAttribute("role", "tablist");
    parent.setAttribute("aria-label", "Calculator worksheets");

    var tabs = getTabs();
    tabs.forEach(function (tab, i) {
      tab.setAttribute("role", "tab");
      var isSelected =
        tab.classList.contains("tab--selected") ||
        tab.classList.contains("dash-tab--selected");
      tab.setAttribute("aria-selected", isSelected ? "true" : "false");
      tab.setAttribute("tabindex", isSelected ? "0" : "-1");
    });
  }

  /** Update aria-selected + tabindex after a tab change. */
  function refreshAriaState() {
    var tabs = getTabs();
    tabs.forEach(function (tab) {
      var isSelected =
        tab.classList.contains("tab--selected") ||
        tab.classList.contains("dash-tab--selected");
      tab.setAttribute("aria-selected", isSelected ? "true" : "false");
      tab.setAttribute("tabindex", isSelected ? "0" : "-1");
    });
  }

  /* ── arrow-key handler on the tablist ─────────────────────────────── */

  function handleTabKeydown(e) {
    var tabs = getTabs();
    if (tabs.length === 0) return;

    var current = tabs.indexOf(document.activeElement);
    if (current === -1) return; // focus is not on a tab header

    var next = -1;

    switch (e.key) {
      case "ArrowRight":
      case "Right":
        next = (current + 1) % tabs.length;
        break;
      case "ArrowLeft":
      case "Left":
        next = (current - 1 + tabs.length) % tabs.length;
        break;
      case "Home":
        next = 0;
        break;
      case "End":
        next = tabs.length - 1;
        break;
      case "Enter":
      case " ":
        e.preventDefault();
        tabs[current].click();
        return;
      default:
        return; // let other keys pass through
    }

    e.preventDefault();
    tabs[next].focus();
    // Activate the tab immediately so users see the switch
    tabs[next].click();
  }

  /* ── Alt+T global shortcut to jump to tab strip ──────────────────── */

  function handleGlobalKeydown(e) {
    if (e.altKey && (e.key === "t" || e.key === "T")) {
      var tabs = getTabs();
      if (tabs.length === 0) return;

      e.preventDefault();
      // Focus the currently-selected tab, or the first one
      var selected = document.querySelector(
        ".tab--selected, .dash-tab--selected"
      );
      (selected || tabs[0]).focus();
    }
  }

  /* ── bootstrap ─────────────────────────────────────────────────────── */

  function init() {
    applyAriaRoles();

    // Attach the arrow-key handler to the tab parent
    var parent = document.querySelector(".tab-parent");
    if (parent) {
      parent.addEventListener("keydown", handleTabKeydown);
    }

    // Global shortcut
    document.addEventListener("keydown", handleGlobalKeydown);

    // Observe DOM mutations so we refresh ARIA when Dash re-renders tabs
    var observer = new MutationObserver(function () {
      applyAriaRoles();
      refreshAriaState();
    });

    var container = document.querySelector(".tab-container") || document.body;
    observer.observe(container, { childList: true, subtree: true });
  }

  // Dash may render asynchronously — retry until the tabs exist
  function waitForTabs() {
    if (document.querySelector(".tab-parent")) {
      init();
    } else {
      setTimeout(waitForTabs, 200);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", waitForTabs);
  } else {
    waitForTabs();
  }
})();
