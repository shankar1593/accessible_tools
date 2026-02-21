# Screen Reader Testing Guide

This guide defines repeatable checks for NVDA, JAWS, and VoiceOver against the BA II Plus accessible web app.

## Test prerequisites

- Run app from `src/app.py` and open `http://localhost:8052`
- Use default zoom first, then retest at 200%
- Keep browser dev tools closed during first pass (to avoid focus disruptions)
- Suggested browsers:
  - NVDA: Firefox or Chrome
  - JAWS: Chrome or Edge
  - VoiceOver: Safari

## Common checks (all screen readers)

1. Navigate by heading and confirm worksheet structure is discoverable.
2. Activate skip link and confirm focus jumps to main content.
3. Trigger a calculation and confirm result is announced as a live status message.
4. Confirm calculator display is announced as a **status region**, not an editable text box.

---

## NVDA (Windows)

### Recommended mode usage

- Start in **Browse Mode** for structural navigation (headings, landmarks, links).
- Switch to **Focus Mode** when entering numeric fields or operating controls.

### Step-by-step

1. Open page and press `NVDA+Space` to confirm Browse Mode is active.
2. Press `H` repeatedly to move through headings (`h1`, then worksheet `h2/h3`).
3. Press `Tab` from top of page and verify first actionable item is the skip link.
4. Press `Enter` on skip link and confirm focus jumps to main worksheet content.
5. Tab to a TVM field (e.g., `N` or `I/Y`) and enter values.
6. Activate a compute button (e.g., Compute PMT).
7. Listen for the polite live region announcement of the result.
8. Move to the calculator display and use NVDA element info to confirm role behaves as status (non-editable).

### Pass criteria

- Heading navigation is complete and ordered.
- Skip link works from keyboard only.
- Result announcements are spoken without forcing focus jump.
- Display is not exposed as an editable textbox.

---

## JAWS (Windows)

### Recommended mode usage

- Use **Virtual Cursor** for page exploration and heading checks.
- Use **Forms Mode** when entering values and pressing controls.

### Step-by-step

1. Load app and use `Insert+F6` to open heading list.
2. Verify worksheet headings appear with meaningful labels.
3. Use `Tab` to reach skip link; activate it with `Enter`.
4. Confirm focus lands in main calculator content.
5. Switch into Forms Mode on a worksheet input and enter test values.
6. Trigger computation and listen for status/live region output.
7. Inspect calculator display announcement; it should be reported as a status-like region, not an edit field.

### Pass criteria

- Heading list contains expected worksheet structure.
- Skip link is reachable and functional.
- Status updates are announced with clear content.
- Display role is read appropriately for passive output.

---

## VoiceOver (macOS)

### Recommended mode usage

- Use **Quick Nav ON** for heading and control traversal.
- Turn **Quick Nav OFF** when entering form values if preferred.

### Step-by-step

1. Enable VoiceOver (`Cmd+F5`).
2. With Quick Nav on, use `VO+U` (Rotor) and inspect headings.
3. Confirm heading hierarchy and worksheet naming are meaningful.
4. Tab to skip link and activate it.
5. Verify VoiceOver announces movement to main content.
6. Fill one worksheet example and compute a result.
7. Confirm result is announced as a status update.
8. Navigate to display region and verify it is announced as status/output rather than a text entry field.

### Pass criteria

- Rotor shows clear heading structure.
- Skip navigation works reliably.
- Live result updates are spoken and understandable.
- Display behaves as a status region.

---

## Suggested test script (quick smoke test)

Use this same mini scenario in each screen reader:

1. Go to TVM worksheet.
2. Enter: `N=360`, `I/Y=5.5`, `PV=75000`, `FV=0`, `P/Y=12`, `C/Y=12`.
3. Activate **Compute PMT**.
4. Expected spoken result should reflect approximately `-425.84`.

## Reporting findings

When filing issues, include:

- Screen reader + version
- Browser + version
- OS + version
- Worksheet/control tested
- Exact steps
- Expected spoken output
- Actual spoken output
- Whether issue blocks independent usage
