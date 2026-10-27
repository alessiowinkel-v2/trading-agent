# Pre-Market Routine

| | |
|---|---|
| Schedule | 07:07 ET, Monday–Friday |
| Cron | `CRON_TZ=America/New_York 7 7 * * 1-5` (UTC fallback `37 11 * * 1-5` = 07:37 EDT / 06:37 EST) |
| Model | claude-sonnet-5-5 |
| Tools | Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch |
| Purpose | Research only: regime, sectors, screen, ≥2 gate-checked candidates, core plan. No orders. |

## Paste block (the routine's prompt)

```
Routine: pre-market. This is a fresh clone of alessiowinkel-v2/trading-agent; all commits go to main.
1. Read routines/COMMON.md, then routines/01_pre_market.md. Follow its STEPs in order.
2. Never skip STEP 0 (preflight), the research record, or the commit.
If either file is missing: bash scripts/notify.sh --alert "pre-market: routine files missing" and stop.
```

## STEPs

**STEP 0 — Preflight** per COMMON.md (`bash scripts/preflight.sh pre-market`).

**STEP 1 — Read**: the COMMON reading list, `memory/TRADING-STRATEGY.md` (all of it — these are the rules), `bash scripts/memtail.sh memory/RESEARCH-LOG.md 1` (yesterday) and `bash scripts/memtail.sh memory/TRADE-LOG.md 3` (yesterday's outcomes).

**STEP 2 — Regime and sectors**: `python3 scripts/screen.py sectors`. Paste the output.

**STEP 3 — Kill switches and core plan**: `python3 scripts/ks.py`. Paste the switch lines that are not PASS, the `ORDERS_ALLOWED…` line, `REGIME`, `CORE`, `CORE_ACTION`, `MAINTENANCE`. Nothing is executed in this routine — market-open recomputes and executes.

**STEP 4 — Screen**: `python3 scripts/screen.py watchlist`. Paste the summary line and the top-10 table.

**STEP 5 — Candidates** (aim: ≥2 passing candidates from ≥2 different sectors):
1. Take names from the top-10 table in rank order (skip a second name from a sector you already have until you have two sectors). If the table has fewer than 2 sectors, add the #1-ranked sector ETF from STEP 2 if it passes.
2. One call for your shortlist (up to 5 names): `python3 scripts/screen.py candidate SYM SYM …`. Paste each table.
3. For each name that printed a `SCREEN_OK:` line (this authorises nothing yet):
   - **G6 earnings**: `bash scripts/perplexity.sh -r week --text "What is the date of <SYM> (<Name>)'s next quarterly earnings report? Reply as YYYY-MM-DD and say whether it is confirmed or estimated. Use only sources updated after <DATE_MINUS_14>."`
     PASS if the date is on or after `EARNINGS_OK_FROM`, or the last report was less than 45 days ago and no date is announced. FAIL otherwise. Quote the source.
   - **Catalysts**: `bash scripts/perplexity.sh -r week --text "News and catalysts for <SYM> (<Name>) since <DATE_MINUS_7>. Cite dates. Ignore anything older."`
   - **News feed** (input to G7, never a gate): `bash scripts/newsfeed.sh --since 48 --symbols <SYM>` — timestamped signals from the news sleeve; cite the headline time if you use one. `(none)` or a missing file is fine.
   - If perplexity.sh exits 3 or errors, use WebSearch for the same questions and set `perplexity=fallback`.
   - **G7 thesis**: 2–3 sentences naming the specific driver for the next 1–3 months. Trend leadership in a top-3 sector is an acceptable driver. Write the main risk in one line.
4. Keep going through the top-10 until you have 2 candidates from 2 sectors or have checked them all. Every rejected name gets one line with its failing gate. **No narrative vetoes**: a name that passes every gate is a candidate; a concern no gate captures goes to the Friday review as a rule suggestion.
5. For each candidate that passed G6 **and** G7, write the final line exactly as screen.py suggested:
   `CANDIDATE: SYM ref=… stop_pct=… sector=… g6=PASS g7=PASS` (values copied from its `SCREEN_OK:` line). Market-open can only buy symbols with this exact line in today's entry; never write it for a name that failed or was not checked.

**STEP 6 — Yesterday's candidates**: one line each from yesterday's TRADE-LOG records: FILLED / not filled: reason / dropped: gate.

**STEP 7 — Record**: append today's entry to memory/RESEARCH-LOG.md in the format at the top of that file, ending with the Decision and the Health footer. `EVENT_TODAY` ≠ none means market-open will not open new satellites today — still write the candidates and say so in the Decision.

**STEP 8 — Notify** (always, ≤6 lines): `bash scripts/notify.sh "pre-market <DATE>: regime <state> | core <CORE_ACTION summary> | candidates <SYM (sector), …> or none: <reason> | event <EVENT_TODAY> | KS failing <list or none>"`. Use `--alert` if any switch fails or `MISSING_COMMITS` is not none.

**STEP 9 — Commit**: `bash scripts/gitpush.sh "pre-market <DATE>: OK - <PLAN summary | HOLD justified: reason>"`.

No orders in this routine. Prices only from scripts — never from Perplexity or the web.
