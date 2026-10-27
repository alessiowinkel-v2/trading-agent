# EOD Routine (daily summary)

| | |
|---|---|
| Schedule | 16:37 ET, Monday–Friday (after the 16:00 close, so closes are final) |
| Cron | `CRON_TZ=America/New_York 37 16 * * 1-5` (UTC fallback `37 21 * * 1-5` = 17:37 EDT / 16:37 EST) |
| Model | claude-sonnet-5-5 |
| Tools | Bash, Read, Write, Edit, Glob, Grep |
| Purpose | EOD snapshot vs SPY, deployment metric, state, one notification. Only protective stop placement — no other trades. |

## Paste block (the routine's prompt)

```
Routine: eod. This is a fresh clone of alessiowinkel-v2/trading-agent; all commits go to main.
1. Read routines/COMMON.md, then routines/04_daily_summary.md. Follow its STEPs in order.
2. Never skip STEP 0 (preflight), the EOD snapshot, or the commit.
If either file is missing: bash scripts/notify.sh --alert "eod: routine files missing" and stop.
```

## STEPs

**STEP 0 — Preflight** per COMMON.md (`bash scripts/preflight.sh eod`). The market is closed at this hour — that is expected; only exit 30 (non-trading day) skips.

**STEP 1 — Read**: the COMMON reading list and `bash scripts/memtail.sh memory/TRADE-LOG.md 2`.

**STEP 2 — Compute**: `python3 scripts/ks.py --eod --write-state`. It prints the KS table, the full EOD snapshot block (equity, cash, invested % vs the 70% floor and days below it, day and phase P&L, SPY day and phase return, positions with stops, today's fills) and writes STATE. Exit 2 → record ABORTED with the error, alert, commit.

**STEP 3 — Protect**: if `MAINTENANCE` lists an `ORPHAN`, place that stop now (GTC — it activates at tomorrow's open). No other orders.

**STEP 4 — Record**: append to memory/TRADE-LOG.md: the EOD block exactly as printed, then `KS failing: <list or none>`, `MISSING_COMMITS: <from preflight>`, and **Notes:** 1–3 plain sentences (what happened, how it compares with SPY, what tomorrow holds — check EVENTS.md for tomorrow). End with the Health footer.

**STEP 5 — Notify** (always, ≤12 lines):
```
bash scripts/notify.sh "EOD <DATE>
Equity $X (day ±X%, phase ±X%) | SPY day ±X%, phase ±X%
Invested X% (floor 70%) | cash $X | regime <state>
Fills today: <list or none>
Positions: SYM ±X% (stop x%), …
KS failing: <list or none> | missed routines: <MISSING_COMMITS>
Tomorrow: <EVENTS.md entry or 'no blocking event'>"
```
Use `--alert` if any switch fails, invested < 70% for 2+ days, or `MISSING_COMMITS` is not none.

**STEP 6 — Commit**: `bash scripts/gitpush.sh "eod <DATE>: OK - equity $X, day ±X%, SPY ±X%"`.
