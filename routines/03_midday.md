# Midday Routine

| | |
|---|---|
| Schedule | 13:07 ET, Monday–Friday |
| Cron | `CRON_TZ=America/New_York 7 13 * * 1-5` (UTC fallback `7 17 * * 1-5` = 13:07 EDT / 12:07 EST) |
| Model | claude-sonnet-5-5 |
| Tools | Bash, Read, Write, Edit, Glob, Grep |
| Purpose | Protect and complete: stops on every satellite, tighten winners, trims, gap exits, retry unfilled plan orders. No unplanned positions. |

## Paste block (the routine's prompt)

```
Routine: midday. This is a fresh clone of alessiowinkel-v2/trading-agent; all commits go to main.
1. Read routines/COMMON.md, then routines/03_midday.md. Follow its STEPs in order.
2. Never skip STEP 0 (preflight), the midday record, or the commit.
If either file is missing: bash scripts/notify.sh --alert "midday: routine files missing" and stop.
```

## STEPs

**STEP 0 — Preflight** per COMMON.md (`bash scripts/preflight.sh midday`).

**STEP 1 — Read**: the COMMON reading list, `bash scripts/memtail.sh memory/RESEARCH-LOG.md 1`, `bash scripts/memtail.sh memory/TRADE-LOG.md 1` (this morning's decision record).

**STEP 2 — Compute**: `python3 scripts/ks.py`. Exit 2 → no orders (KS-6), record, alert, commit ABORTED.

**STEP 3 — Maintenance**: execute every `MAINTENANCE` line:
- `ORPHAN` → run the printed stop command; verify with `order-get`.
- `TIGHTEN` → run the printed `order-replace` command; record old and new trail.
- `KS-4 TRIM` → cancel the stop, sell the printed number of shares with a limit at the bid (`client_order_id trim-<DATE>-<SYM>`), then a new trailing stop for the remaining shares.
- `KS-3 HALT` → follow it exactly and alert.
- `CORE has a stop order` → cancel it.

**STEP 4 — Gap exits and thesis breaks** (satellites only):
- `bash scripts/alpaca.sh positions`: for any satellite whose price is below its stop level while its stop order is missing or unfilled → cancel the stop if any, `bash scripts/alpaca.sh close <SYM>`, record.
- For a satellite down ≥4% today (`change_today` ≤ -0.04): one `perplexity.sh -r day --text` news check. Close only on a concrete thesis break (fraud, guidance withdrawn, failed deal, regulatory action) — never on price alone; the stop handles price.

**STEP 5 — Retries** (only what was planned today):
- `CORE_ACTION=BUY/SELL` still showing (market-open's core order did not fill) → run it, `wait-fill`.
- Today's `CANDIDATE:` lines that were not filled at market-open → `python3 scripts/ks.py --check SYM …` → execute `VERDICT BUY` exactly as market-open STEP 5 does. A candidate that failed G11 at open may pass now; one that is `SKIP` again is recorded and dropped for today.

**STEP 6 — Record**: append the Midday record to memory/TRADE-LOG.md (format at the top of that file), with the Health footer.

**STEP 7 — State**: `python3 scripts/ks.py --write-state`.

**STEP 8 — Notify** only if an order was placed, replaced or cancelled, or a switch fails: `bash scripts/notify.sh "midday <DATE>: <actions>"` (`--alert` for KS-3, a rejected stop, or an exit on thesis break). Otherwise stay silent.

**STEP 9 — Commit**: `bash scripts/gitpush.sh "midday <DATE>: OK - <actions or no action>"`.
