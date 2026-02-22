# Contributing

Thank you for considering a contribution. This project exists to reduce accessibility barriers for blind and low-vision candidates preparing for CFA, FRM and other competitive finance exams, and first-time contributors are absolutely welcome.

## Development setup

1. Clone the repository and move into project root:
   - `calculators/financial/ba-ii-plus`
2. Create and activate a virtual environment.
3. Install dependencies.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install dash dash-bootstrap-components pytest
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install dash dash-bootstrap-components pytest
```

## Run tests before submitting a PR

From project root:

```bash
pytest tests/ -s -q
```

The `-s` flag is expected for this project because tests print pass/fail details and summary tables.

## How to contribute

- Fork and create a branch with a clear name (example: `fix/tvm-live-region-message`).
- Keep changes focused and small when possible.
- Add or update tests for behavior changes.
- Update docs and changelog when relevant.
- Open a PR using the repository template.

## Highest-impact areas where help is needed

1. **Screen reader testing**
   - NVDA, JAWS, and VoiceOver workflow validation
   - Announcement timing and clarity for live regions
2. **Exam workflow validation (CFA, FRM and others)**
   - Additional question-by-question verification against physical BA II Plus workflows
3. **Mobile accessibility**
   - Touch target and zoom behavior across iOS/Android browsers
4. **Bond worksheet parity**
   - Match TI manual p.56 exact pricing behavior more closely
5. **Test architecture cleanup**
   - Add `conftest.py` fixtures to reduce duplication in test modules

## Code style and architecture constraints

- Keep formula logic as pure functions/methods in `src/calculator.py` (no UI dependencies).
- Keep all style rules in `src/assets/custom.css` (do not use `html.Style()` in Dash 4).
- Prefer semantic HTML wrappers for ARIA attributes.
- `dbc.Col` cannot reliably host ARIA attributes for this app; wrap content in `html.Div` and apply ARIA there.
- Preserve sign convention: outflows negative, inflows positive.

## Further reading

- [ARCHITECTURE.md](ARCHITECTURE.md) — design decisions, color system and ARIA implementation
- [FORMULA_VERIFICATION.md](FORMULA_VERIFICATION.md) — test verification against TI manual examples
- [.github/PROJECTGUIDE.md](.github/PROJECTGUIDE.md) — detailed project guide with full backend/UI specification

## Pull request checklist

- [ ] Tests pass with `pytest tests/ -s -q`
- [ ] New tests were added for new functionality
- [ ] Accessibility behavior validated for changed UI paths
- [ ] CSS changes are only in `src/assets/custom.css`
- [ ] No `html.Style()` added
- [ ] ARIA attributes are on `html.*` elements (not `dbc.*`)
- [ ] `CHANGELOG.md` updated when user-visible behavior changes

## Code of collaboration

Please be kind, specific, and constructive in issues and reviews. Accessibility work improves through shared iteration and real user feedback.
