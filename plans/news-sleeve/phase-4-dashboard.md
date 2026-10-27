# Phase 4 — dashboard (GitHub Pages)

## Session prompt
```
You are a development session for alessiowinkel-v2/trading-agent, authorised by the user to implement Phase 4 of the news sleeve.
1. Read CLAUDE.md, plans/news-sleeve/PLAN.md, plans/news-sleeve/STATUS.md, plans/news-sleeve/phase-4-dashboard.md. PLAN.md §1 and §11 bind you.
2. Load the dataviz skill before writing any chart code.
3. Work on branch claude/news-sleeve-phase-4. Never push to main. Finish with STATUS.md updated and a PR titled "News sleeve — Phase 4: dashboard".
```

## Goal
A static page at `https://alessiowinkel-v2.github.io/trading-agent/` that the user can open on a phone and see, without reading git: how the account is doing vs SPY, whether every routine ran, what the news scanner saw, and whether the news sleeve is anywhere near its gate. Built from `memory/` by a script; no API keys in the page or the build.

## Read first
`memory/STATE.json`, `memory/STATE.md`, `scripts/ks.py` (`eod_block`, `write_state` — what is persisted per EOD), `scripts/watchdog.sh grid`, `memory/TRADE-LOG.md` (EOD block format), `memory/WEEKLY-REVIEW.md` (graduation checklist format), `memory/news/scorecard.json`, `memory/news/state.json`, `memory/notifications/`.

## Build
1. **Data persisted for the dashboard** (small, additive): `ks.py --write-state` stores per EOD `spy_close`, `cash`, `positions[]` (sym, qty, avg, last, stop_pct, stop_status), `ks_fail[]`, `max_dd`, `spy_max_dd`, `phase_ret`, `spy_phase_ret` in `STATE.json.eod[DATE]` (it already stores `equity`, `invested`). Keep backward compatibility with the existing keys.
2. **`scripts/dashboard.py`** → writes `site/data.json` (never committed; built in CI) from: STATE.json, the last 14 days of routine commit subjects (`git log`), WEEKLY-REVIEW.md (latest graduation checklist, 11 items), notifications of the last 7 days (titles only, no mentions), `news/state.json`, `news/scorecard.json`, last 100 signals (ticker, direction, confidence, magnitude, category, ts, outcome so far), scanner uptime for 7 days, plan phase tracker from `STATUS.md`. All numbers are copied, never recomputed, except indexing equity and SPY to 100 at `start_date`.
3. **`site/index.html`** (+ `app.js`, `style.css`): vanilla JS, one chart library from cdnjs pinned to an exact version, dark/light via `prefers-color-scheme`, phone-first. Panels, in this order:
   - header: equity, phase return vs SPY, max DD vs SPY DD, invested %, cash, regime, KS failing (red if any), paused flag, last EOD time;
   - equity vs SPY (indexed) line chart + drawdown strip;
   - positions table with stop status;
   - cadence grid (last 10 trading days × 4 routines + weekly, OK/SKIPPED/ABORTED/MISSING colour-coded);
   - graduation checklist (11 rows with ✅🟡❌ from the latest weekly);
   - news sleeve: heartbeat (last scan, runs in last 24 h / 96, cost today), gate line, bucket table (tradeable rows first), signal feed (last 50, click → source URL);
   - plan tracker (phase states from STATUS.md);
   - footer: built at, commit sha, "numbers come from scripts/ks.py and scripts/newsscore.py".
   Empty states must look intentional ("no signals yet", "scorer has not run").
4. **`.github/workflows/pages.yml`**: on push to `main` (paths `memory/**`, `site/**`, `scripts/dashboard.py`) + `workflow_dispatch`; build → upload-pages-artifact → deploy-pages; concurrency `pages`; no secrets needed.
5. **Tests**: `dashboard.py --check` validates the JSON against a schema and runs in `tests/offline.sh`; a tiny Playwright smoke test (Chromium is preinstalled in the cloud session) opens the built page and asserts the header numbers render — if Playwright is unavailable in CI, keep it local-only and say so.

## Acceptance
- Live URL loads on mobile and desktop, both themes; a screenshot in the PR.
- Every number on the page can be traced to a line in `memory/` (list the mapping in the PR).
- STATUS note: URL, build time, anything not yet shown.
