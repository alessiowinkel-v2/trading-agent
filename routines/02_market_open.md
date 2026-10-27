# Market-Open Routine

| | |
|---|---|
| Schedule | 10:12 ET, Monday–Friday (after the volatile first 30 minutes — the routine never waits or exits for time reasons) |
| Cron | `CRON_TZ=America/New_York 12 10 * * 1-5` (UTC fallback `12 15 * * 1-5` = 11:12 EDT / 10:12 EST) |
| Model | claude-sonnet-5-5 |
| Tools | Bash, Read, Write, Edit, Glob, Grep |
| Purpose | Execute: core rebalance, then today's candidates. Always record every decision. |

## Paste block (the routine's prompt)

```
Routine: market-open. This is a fresh clone of alessiowinkel-v2/trading-agent; all commits go to main.
1. Read routines/COMMON.md, then routines/02_market_open.md. Follow its STEPs in order.
2. Never skip STEP 0 (preflight), the decision record, or the commit.
If either file is missing: bash scripts/notify.sh --alert "market-open: routine files missing" and stop.
```

## STEPs

**STEP 0 — Preflight** per COMMON.md (`bash scripts/preflight.sh market-open`).

**STEP 1 — Read**: the COMMON reading list and `bash scripts/memtail.sh memory/RESEARCH-LOG.md 1`. Collect today's `CANDIDATE:` lines. If the latest entry is not dated `DATE`, there is no plan: satellites are skipped (Action `NO_PLAN`), the core is still handled, and the notification uses `--alert`.

**STEP 2 — Compute**: `python3 scripts/ks.py --check SYM SYM …` with every candidate's symbol (no candidates → plain `python3 scripts/ks.py`). ks.py reads the reference prices from today's `CANDIDATE:` lines itself and refuses any symbol that is not one (gate `PLAN`). If it exits 2: no orders (KS-6), record, notify with `--alert`, commit ABORTED.

**STEP 3 — Core**: if `CORE_ACTION=BUY …` or `SELL …`, run the printed command exactly, then `bash scripts/alpaca.sh wait-fill <id> 60` (exit 4 → cancel, read `filled_qty`; midday retries). `HOLD`, `DONE_TODAY`, `DEFER` or `BLOCKED` → no order, record the reason. Core orders are never timing-blocked.

**STEP 4 — Maintenance**: run any `ORPHAN` stop command from `MAINTENANCE` now (KS-10). Leave TIGHTEN/TRIM to midday. If `MAINTENANCE` says `BLOCKED`, place nothing and alert.

**STEP 5 — Satellites**, in the order of the research entry:
1. If the core order in STEP 3 changed cash, or after any fill, re-run `python3 scripts/ks.py --check` for the remaining candidates — sizing and slots depend on live cash.
2. `VERDICT SKIP` → record the failing gates. `VERDICT BUY` → run the BUY command exactly → `wait-fill <id> 60`:
   - filled → run the `THEN` stop command with `"qty":"<filled_qty>"` → `bash scripts/alpaca.sh order-get <stop_id>` → status must be new/accepted/held.
   - exit 4 or partial → `cancel <id>`; if `filled_qty` > 0, place the stop for `filled_qty`; record "partial".
   - rejected / REFUSED → record the message verbatim.
   - stop rejected → `bash scripts/alpaca.sh close <SYM>` and record "closed: stop rejected" (a position without a stop is not allowed).
3. Never place an order ks.py did not print. Never change qty, price or ids.

**STEP 6 — Record**: append the Market-Open Decision record to memory/TRADE-LOG.md (format at the top of that file): preflight line, KS line, core line, one table row per candidate (all gates with PASS/FAIL, action, order ids, fills, stop id), and for each new position one line with qty, fill, stop %, target and the one-line thesis from the research entry. End with the Health footer.

**STEP 7 — State**: `python3 scripts/ks.py --write-state` (alerts automatically on newly failing switches).

**STEP 8 — Notify** (always): `bash scripts/notify.sh "market-open <DATE>: core <result> | <SYM bought n @ px, stop x% | SYM skipped: G11 …> | KS failing <list or none>"`. Use `--alert` for NO_PLAN, a rejected stop, or any REFUSED/rejected order.

**STEP 9 — Commit**: `bash scripts/gitpush.sh "market-open <DATE>: OK - core <result>, <n> entries"`.
