# News sleeve — phase tracker

Every phase session reads this first and updates it last. Keep entries short; the PR has the detail.

| Phase | Branch | PR | State | Merged |
|-------|--------|----|-------|--------|
| 0 prerequisites | — | — | 🟡 agent did the amendments; 4 user-only items left (see phase-0) | — |
| 1 scanner plumbing | `claude/affectionate-bohr-jrfyok` | — | ✅ built + tested (offline and live), awaiting PR merge | — |
| 2 classifier | `claude/news-sleeve-phase-2` | — | ☐ not started | — |
| 3 scorer | `claude/news-sleeve-phase-3` | — | ☐ not started | — |
| 4 dashboard | `claude/news-sleeve-phase-4` | — | ☐ not started | — |
| 5 paper execution | `claude/news-sleeve-phase-5` | — | ☐ blocked by PLAN §6 gate + strategy amendment | — |
| 6 crypto fast lane | — | — | ☐ optional, decide with data | — |

States: `not started` · `in progress (session <date>)` · `PR open` · `merged` · `blocked: <why>`.

## Handoff notes (newest first)

### Template
```
### Phase N — <title> — <YYYY-MM-DD>
Done: …
Not done / deviations from PLAN.md: …
How the user verifies: …
Open questions for the user: …
Next phase must know: …
```

### Phase 1 — scanner plumbing — 2026-10-27 (planning session, Fable)
Done: `memory/NEWS-UNIVERSE.md` (74 symbols), `scripts/newslib.py`, `alpaca.sh news|crypto-latest|crypto-price|crypto-bars|bars-intraday`, `scripts/newsscan.py` + `newsscan.sh` (heartbeat commits, loud aborts, 6 h alert rate limit), `.github/workflows/newsscan.yml` (skips quietly until secrets exist), `gitpush.sh` accepts `newsscan`/`newsscore` subjects, watchdog flags a scanner older than 3 h, preflight/watchdog read 1500/2000 commit subjects (scanner commits would otherwise push routine subjects out of the window), mock routes + 22 offline checks, README/env.template.
Live test (session had paper keys): 24 h lookback → 303 universe headlines, 47 tickers, 2.2 s; second run 0 new. Those rows and `memory/news/state.json` are committed, so the Action continues from the cursor after merge.
Not done / deviations: none from PLAN §1–§4. `tests/offline.sh` now unsets inherited credentials (it had reached the real paper API and webhook from this session; three resting test orders were cancelled, no fills, no positions). Three pre-existing offline checks (cadence/watchdog grid) fail on any day the real routines already committed — unrelated, date-dependent.
How the user verifies: `bash tests/offline.sh` → only those 3 date-dependent checks may fail; after merge + secrets: Actions → newsscan → Run workflow → a `newsscan <DATE> <HH:MM>Z: OK - …` commit appears on main within a minute, then every 15 min when there is news.
Open questions for the user: none.
Next phase must know: raw rows ≈ 300/day (SPY-tagged macro ≈ 13%, crypto ≈ 6%); Benzinga `symbols` are alphabetical, so `pick_primary` matches names from the universe Note column; `px.status` is OK on 99.7% of rows at ingest.
