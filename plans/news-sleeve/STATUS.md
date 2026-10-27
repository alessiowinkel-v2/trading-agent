# News sleeve — phase tracker

Every phase session reads this first and updates it last. Keep entries short; the PR has the detail.

| Phase | Branch | PR | State | Merged |
|-------|--------|----|-------|--------|
| 0 prerequisites | — | — | 🟡 agent did the amendments; 4 user-only items left (see phase-0) | — |
| 1 scanner plumbing | `claude/affectionate-bohr-jrfyok` | — | ✅ built + tested (offline and live), awaiting PR merge | — |
| 2 classifier | `claude/affectionate-bohr-jrfyok` | — | ✅ built + mock-tested; live run needs ANTHROPIC_API_KEY (user) | — |
| 3 scorer | `claude/affectionate-bohr-jrfyok` (draft) | — | 🟡 DRAFT committed, NOT finished — continue in a fresh Opus 5.5 session | — |
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

### Phase 3 — scorer — 2026-10-27 — DRAFT, stopped by the user (planning session, Fable)
State: `scripts/newsscore.py`, `.github/workflows/newsscore.yml`, weekly-review STEP 2b, the `### News sleeve` section in the WEEKLY-REVIEW template and 15 offline checks are written and committed as a draft. **Not finished.** Against the mock, `--explain 62600001` resolves h1, the routine entry and d1/d3/d5 with benchmark and cost correctly (verified by hand), and `--slot-of` passes all four slot tests.
Known failing offline checks (5): the "flat prices" assertions are wrong — the mock's daily closes are not flat, only its intraday bars are, so the expected `net_excess == -cost` must be replaced by a check against the mock's own daily closes; one of the five backdated signals ends `unscorable` (not yet investigated — print `--explain` for 62600002/62600096/62600097); the gate regex expects "5 of 150" but only 4 score. Nothing live was run (no scorer run against real data; no commits by the workflow).
Next session (Opus 5.5, xhigh, prompt in `phase-3-scorer.md`): read `scripts/newsscore.py` in full before changing it, fix the tests rather than the maths unless `--explain` shows a real error, verify PLAN §5 rules line by line (slot, horizons, benchmark, costs, bear sign, unscorable handling, idempotency), then run the scorer once live and audit 5 signals by hand.

### Phase 2 — classifier — 2026-10-27 (planning session, Fable)
Done: `scripts/claude.sh json` (Messages API, `output_config.format` json_schema, API version 2026-10-21, effort low, no sampling params, `fallbacks:"default"` with its beta header, retries on 429/5xx, exit 3 without a key, `CLAUDE_DRY=1` prints the request, `CLAUDE_MOCK=1` → `tests/mock_claude.py`); `scripts/prompts/classify-v1.md` + `classify-schema.json` (prompt_version stored per signal); `scripts/newsclassify.py` (pending = given ids + anything ingested < 48 h without a signal; Jaccard ≥ 0.6 same-ticker dedup within 24 h without an API call; ≤ 20 per call, ≤ 3 calls/run; every field re-validated client-side, ticker remaps allowed only to the article's own universe symbols, SPY or BTC/USD; Discord ≤ `ALERT_BUDGET`=5/day for conf ≥ 0.8 ∧ mag ≥ 2 ∧ new, held-symbol bear ≥ 0.7 always alerts with `--alert`; token/cost accounting per day in `state.json`); `scripts/newsfeed.sh` (+ `.py`) for the routines; read-only hooks in `routines/01_pre_market.md` STEP 5 and `routines/03_midday.md` STEP 4; 27 offline checks.
Not done / deviations: no live classification yet — this session has no `ANTHROPIC_API_KEY`. Without the key the scanner still runs and keeps headlines pending for 48 h; the first run after the key arrives clears 60 per run. Measured volume ≈ 300 headlines/day → ≈ 15 calls/day → ≈ $9/month on Sonnet 5.5 (updated in PLAN §8).
How the user verifies: after adding the key (repo secret `ANTHROPIC_API_KEY`), run the `newsscan` workflow by hand: the commit subject shows `N new headlines, M signals`, `memory/news/signals/2026-10.jsonl` grows, `memory/news/state.json.classifier_usage` shows cost. Locally: `bash scripts/newsfeed.sh --since 24`.
Open questions for the user: none (model choice recorded as D11; change it via the repo variable `CLASSIFIER_MODEL`).
Next phase must know: signal rows carry `status` open|none|duplicate|unscorable; only `open` rows are scoreable; `ticker` may differ from the raw row's (remapped to SPY / BTC/USD), in which case `px` is null — the scorer must take entry prices from bars, never from `px`.

### Phase 1 — scanner plumbing — 2026-10-27 (planning session, Fable)
Done: `memory/NEWS-UNIVERSE.md` (74 symbols), `scripts/newslib.py`, `alpaca.sh news|crypto-latest|crypto-price|crypto-bars|bars-intraday`, `scripts/newsscan.py` + `newsscan.sh` (heartbeat commits, loud aborts, 6 h alert rate limit), `.github/workflows/newsscan.yml` (skips quietly until secrets exist), `gitpush.sh` accepts `newsscan`/`newsscore` subjects, watchdog flags a scanner older than 3 h, preflight/watchdog read 1500/2000 commit subjects (scanner commits would otherwise push routine subjects out of the window), mock routes + 22 offline checks, README/env.template.
Live test (session had paper keys): 24 h lookback → 303 universe headlines, 47 tickers, 2.2 s; second run 0 new. Those rows and `memory/news/state.json` are committed, so the Action continues from the cursor after merge.
Not done / deviations: none from PLAN §1–§4. `tests/offline.sh` now unsets inherited credentials (it had reached the real paper API and webhook from this session; three resting test orders were cancelled, no fills, no positions). Three pre-existing offline checks (cadence/watchdog grid) fail on any day the real routines already committed — unrelated, date-dependent.
How the user verifies: `bash tests/offline.sh` → only those 3 date-dependent checks may fail; after merge + secrets: Actions → newsscan → Run workflow → a `newsscan <DATE> <HH:MM>Z: OK - …` commit appears on main within a minute, then every 15 min when there is news.
Open questions for the user: none.
Next phase must know: raw rows ≈ 300/day (SPY-tagged macro ≈ 13%, crypto ≈ 6%); Benzinga `symbols` are alphabetical, so `pick_primary` matches names from the universe Note column; `px.status` is OK on 99.7% of rows at ingest.
