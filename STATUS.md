# STATUS

## What was built

FFXIV Freebies Kit — a fillable, printable, client-side kit of FFXIV printables.
Fan project: no game assets, no account needed, nothing saved to a server.

Files:
- index.html — landing page with links to all printables and usage instructions
- duty-rotator.html — per-duty skill rotation planner (6 fillable rows)
- gil-tracker.html — gil income/expense ledger with auto-calculating totals and running balance (8 rows)
- leve-planner.html — levequest planner with location, level, turn-ins, allowances, status (6 rows)
- mount-checklist.html — mount collection checklist with acquisition source and obtained checkboxes (10 rows)
- style.css — shared styles with screen chrome and `@media print` layout (Letter/A4 via `@page size: letter a4`, controls hidden on print)
- verify.py — structural verification script (well-formed HTML, link resolution, fillable inputs, print trigger, credits, license, secret scan)
- README.md — description, how to use, fan-project disclaimer, credit to Asdale Dynamics, LLC, MIT license pointer
- LICENSE — MIT License, copyright line exactly "Copyright (c) 2026 Asdale Dynamics, LLC"
- .gitignore — excludes dependency/build/OS/editor artifacts

Credit: Asdale Dynamics, LLC is credited in README.md, LICENSE, and the footer of every HTML page.

## How to run

No build step, no install, no account. Open any HTML file directly in a browser:

- File > Print (Ctrl+P / Cmd+P) prints the current page cleanly at 100% scale on Letter or A4 paper.
- Screen-only controls (Print button) are hidden when printing.
- Fields can be filled on screen before printing, or printed blank and completed by hand.
- In Gil Tracker, enter income as positive amounts and expenses as negative amounts; totals and running balance update automatically.

From this folder:

```
open index.html        # macOS
xdg-open index.html    # Linux
start index.html       # Windows
```

## Verification results

Ran `python3 verify.py` — PASSED:

- 5 HTML pages parse as well-formed (custom structural parser)
- All internal links resolve to existing files
- All 4 printable pages have fillable `<input>` fields, a `window.print()` trigger, and a `<footer>`
- `style.css` contains `@media print` and `@page size: letter a4`
- Every HTML page credits "Asdale Dynamics, LLC"
- LICENSE contains the exact line "Copyright (c) 2026 Asdale Dynamics, LLC"
- README.md credits Asdale Dynamics, LLC and references the MIT license
- No `.github/workflows` directory
- No secrets/API keys/private-key patterns detected

Note: print rendering was not tested against a physical printer or browser print preview; verify visually before bulk printing.

## Known gaps

- No browser print-preview screenshot/render test performed.
- Single shared CSS file; no per-page overrides.
- Gil Tracker auto-calculation runs in-browser only; printed totals reflect whatever values are filled in before printing.
