# Phase 3 — scorer and scorecard

## Session prompt
```
You are a development session for alessiowinkel-v2/trading-agent, authorised by the user to implement Phase 3 of the news sleeve.
1. Read CLAUDE.md, plans/news-sleeve/PLAN.md, plans/news-sleeve/STATUS.md (Phase 1–2 notes), plans/news-sleeve/phase-3-scorer.md. PLAN.md §5–§6 are the specification and may not be reinterpreted; §11 binds you.
2. Work on branch claude/news-sleeve-phase-3. Never push to main. Finish with STATUS.md updated and a PR titled "News sleeve — Phase 3: scorer".
```

## Goal
Nightly, every open signal whose horizons have elapsed gets slot-entry prices, outcomes, benchmark and cost-adjusted excess returns exactly as PLAN §5 defines; the scorecard reports every PLAN §6 bucket and says in one line whether the trading gate is met.

## Read first
`scripts/newsscan.py`, `scripts/tlib.py` (`bars_multi`, `parse_ts`, calendar helpers), `scripts/alpaca.sh` (`bars-intraday`, `crypto-bars`, `calendar`), `scripts/ks.py` (`week_block`, how it formats tables), `routines/05_weekly_review.md`, `memory/WEEKLY-REVIEW.md` template.

## Build
1. **`scripts/newsscore.py`** — `python3 scripts/newsscore.py [--since DATE] [--dry-run] [--explain ID]`:
   - slot resolution: stocks → first of {10:12, 13:07} ET ≥ `ts_news + 5 min` on an Alpaca calendar trading day; entry = 1-minute bar open at that minute (fallback: first bar within 5 min, else `unscorable`). Crypto → both `crypto-15m` (next quarter hour) and the next routine slot; store both, score both.
   - horizons d1/d3/d5: stocks = official closes of the 1st/3rd/5th trading day after the entry day (daily bars, SIP); crypto = 15-minute bar close nearest +24/72/120 h. h1 = price 60 min after `ts_news` (1-minute bars; crypto 1-minute bars).
   - benchmark and costs exactly as PLAN §5; `net_excess` sign convention for bears as written.
   - idempotent: already-scored signals are never recomputed unless `--rescore` is given.
   - `--explain ID` prints every price used with its bar timestamp (this is how the user audits 5 signals by hand).
2. **Scorecard**: `memory/news/scorecard.json` (machine) + `memory/NEWS-SCORECARD.md` (human): bucket table per PLAN §6 (n, mean, median, t, first/second-half sign, tradeable yes/no) at d3, plus the same at h1/d1/d5 for information; a header block with weeks scanned, signals total/scored/unscorable, uptime % of 15-minute slots (from scan commits), and `GATE: MET|NOT MET — <which condition fails>`. Confidence intervals, no p-value theatre.
3. **`.github/workflows/newsscore.yml`** — nightly 02:00 ET (`0 7 * * *` UTC, with a comment on DST), `workflow_dispatch`; commits with `newsscore <DATE>: OK - scored n, gate <MET|NOT MET>`.
4. **Weekly routine**: add STEP 2b to `routines/05_weekly_review.md`: `bash scripts/memtail.sh memory/NEWS-SCORECARD.md 1` → paste the header block and the tradeable rows (or "none") into a `### News sleeve` section of the review; no grading impact in Phases 1–4.
5. **Tests**: mock bars for one stock and one crypto signal with known prices; assert slot, horizons, bench, cost math to the cent; assert a weekend headline resolves to Monday 10:12; assert bear sign convention; assert idempotency.

## Acceptance
- offline tests PASS; `newsscore.py --explain` on 5 real signals matches a hand calculation the user can repeat from the printed bars.
- Scorecard renders with every bucket present even when n = 0.
- STATUS note states the current gate status and the three biggest sources of `unscorable`.
