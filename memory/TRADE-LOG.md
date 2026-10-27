# Trade Log

Append-only. Every market-open, midday and EOD run adds one dated record — including "no trade" and "skipped" runs, so a missing record always means a failed run.
Numbers are copied from `scripts/ks.py` output, never computed by hand. Read with `bash scripts/memtail.sh memory/TRADE-LOG.md 3`. Phase 1 log: `memory/archive/phase1-2026/TRADE-LOG.md`.

## Record formats

```
### YYYY-MM-DD — Market-Open Decision (run HH:MM ET)
Preflight: exit N | EVENT_TODAY=… | PAUSED=…
KS: ORDERS_ALLOWED=… BUYS_ALLOWED=… SAT_ENTRIES_ALLOWED=… SAT_SLOTS=… | failing: none
Core: CORE_ACTION=… → order <id> (core-YYYY-MM-DD) <status>, filled <qty> @ <price> | or HOLD/DONE_TODAY/BLOCKED (reason)
| Candidate | Ref | G0 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|
| SYM | 123.45 | PASS | PASS | PASS | PASS | FAIL (ask +3.4%) | SKIP | - | - | - |
New positions: SYM n sh @ fill, trailing stop x.x% (order id, verified status), target $X, thesis: one line from today's research.
Health: run HH:MM ET | preflight=N | mode=PAPER | ks=<n failing> | notify=ok|FAILED

### YYYY-MM-DD — Midday (run HH:MM ET)
KS: … | Maintenance: ORPHAN/TIGHTEN/TRIM actions with order ids, or none
Exits: SYM n sh @ price (reason, order id) or none | Retries: SYM … or none
Health: …

### YYYY-MM-DD — EOD Snapshot (Day N, Weekday)
(paste the block printed by `python3 scripts/ks.py --eod --write-state`)
KS failing: none | Notes: 1–3 sentences, plain English.
Health: …
```

---

## 2026-10-27 — Phase 1b Day 0 baseline
**Portfolio:** $2,000.00 target after the paper reset | **Positions:** none | **Phase P&L:** $0.00
Day 1 market-open buys the core (SPYM) to target; satellites follow from the pre-market screen.

### 2026-10-27 — market-open: SKIPPED (market closed at run time)
Preflight: exit 31 | NOW_ET=2026-10-27 16:00 | MARKET_OPEN=no | EVENT_TODAY=none | PAUSED=no. No orders placed; run fired after the close (schedule/timezone mismatch?). Core not bought today.
Health: run 16:00 ET | preflight=31 | mode=PAPER | ks=n/a | notify=n/a | perplexity=n/a

### 2026-10-27 — midday: SKIPPED (market closed at run time)
- Preflight exit 31: NOW_ET 16:02, market closed (close 16:00). No orders, no maintenance.
Health: run 16:02 ET | preflight=31 | mode=PAPER | ks=n/a | notify=ok | perplexity=n/a

### 2026-10-27 - EOD Snapshot (Day 0, Tuesday)
**Portfolio:** $2,000.00 | **Cash:** $2,000.00 (100.0%) | **Invested:** 0.0% (floor 70%, days below: 1) | **Day P&L:** $0.00 (+0.00%) | **Phase P&L:** $0.00 (+0.00%) | **SPY today:** +0.56% | **SPY phase:** +0.00% | **Regime:** risk-on

| Ticker | Role | Shares | Entry | Last | Day chg | Unrealized | % of equity | Stop |
|---|---|---|---|---|---|---|---|---|
| - | - | - | - | - | - | - | - | - |

**Fills today:** none

KS failing: none
MISSING_COMMITS: none
**Notes:** No positions; market-open and midday both ran after the close and skipped, so the core SPYM was not bought today (ks.py: BUY 17 SPYM, target 75%). SPY +0.56% vs flat account. Tomorrow 2026-10-28 is FOMC (blocks new satellites; core buy still allowed).
Health: run 16:37 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a
