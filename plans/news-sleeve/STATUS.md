# News sleeve — phase tracker

Every phase session reads this first and updates it last. Keep entries short; the PR has the detail.

| Phase | Branch | PR | State | Merged |
|-------|--------|----|-------|--------|
| 0 prerequisites | — | — | 🟡 agent did the amendments; 3 user-only items left (see phase-0) | — |
| 1 scanner plumbing | `claude/affectionate-bohr-jrfyok` | — | ✅ built + tested (offline and live), awaiting PR merge | — |
| 2 classifier | `claude/affectionate-bohr-jrfyok` | — | ✅ built + mock-tested; live run needs ANTHROPIC_API_KEY (user) | — |
| 3 scorer | `claude/affectionate-bohr-jrfyok` | — | ✅ built + mock-tested; first live run happens the night after the first classified signal | — |
| 4 dashboard | `claude/affectionate-bohr-jrfyok` | — | ✅ built + tested + screenshotted; goes live on the first `pages` run after merge | — |
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

### Phase 4 — dashboard — 2026-10-27 (planning session, Fable)
Done: `scripts/dashboard.py` (builds `data.json` from STATE.json, git subjects, WEEKLY-REVIEW.md, notifications, news state/scorecard/signals, STATUS.md; `--check` validates), `site/index.html` + `app.js` + `style.css` (vanilla JS, inline SVG line charts with crosshair tooltip and keyboard navigation, table view, light/dark via `prefers-color-scheme` plus a toggle, no CDN, no secrets), `.github/workflows/pages.yml` (on push to main + every 30 min + manual; `configure-pages` with `enablement: true` tries to switch Pages on by itself), `ks.py --eod` now also stores cash, SPY close, regime, failing switches, satellite % and a positions table per EOD (additive keys). Palette validated with the dataviz validator in both modes. Screenshots taken at 1200 px light and 390 px dark: no console errors.
Not done / deviations: the Playwright smoke test is local-only (not in CI). Max drawdown and the SPY index are derived by `dashboard.py` from the stored EOD series (the only computed values on the page). `cash` shows n/a until the first EOD run with the new ks.py (2026-10-28).
How the user verifies: after merge, Actions → pages → the URL printed by the deploy step (expected https://alessiowinkel-v2.github.io/trading-agent/). If the run fails on "Pages not enabled", set repo Settings → Pages → Source = GitHub Actions once and re-run.
Next phase must know: `data.json` is the only interface between scripts and page; Phase 5 adds news positions and sleeve P&L to `account.positions` / a new `news.positions` key.

### Phase 3 — scorer — 2026-10-27 (planning session, Fable)
Done: `scripts/newsscore.py` per PLAN §5–§6 (routine slot = first 10:12/13:07 ET on a trading day ≥ ts_news + 5 min; crypto also `crypto-15m` = first quarter hour ≥ ts_news + 15 min; entry = 1-minute bar open at the slot; d1/d3/d5 = official closes of the 1st/3rd/5th trading day after entry, crypto +24/72/120 h 15-minute closes; h1 diagnostic only, stocks only in regular hours; benchmark SPY / BTC / none; costs 0.10% / 0.60%; bears scored as shorts; unscorable when no entry bar; idempotent; `--explain ID` prints every bar; `--slot-of`), `memory/news/scorecard.json` + `memory/NEWS-SCORECARD.md` (fine/conf/asset buckets at h1/d1/d3/d5, gate line with reasons, uptime from scan runs), `.github/workflows/newsscore.yml` nightly 07:00 UTC, weekly review STEP 2b + template section, 17 offline checks (slots, benchmark/cost algebra, bear sign, crypto lane, explain, idempotency, memtail).
Not done / deviations: never run against live data (there are no classified signals until the API key exists). Mock crypto bars for old windows are flat by construction (mock change). The `uptime` figure counts scanner runs per calendar day / 96.
How the user verifies: `python3 scripts/newsscore.py --explain <id>` on any scored signal and compare the printed bars with the Alpaca chart; `bash scripts/memtail.sh memory/NEWS-SCORECARD.md 1`.
Next phase must know: the gate is read by Phase 5 from `scorecard.json → gate.tradeable[]` (asset, direction, conf, mag, category); `crypto_15m` rows exist only for the Phase 6 decision.

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
