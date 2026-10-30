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

### 2026-10-28 — Market-Open Decision (run 10:26 ET)
Preflight: exit 0 | EVENT_TODAY=FOMC | PAUSED=no (run fired 14:26 UTC, scheduled 14:12)
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=2 | failing: none
Core: CORE_ACTION=BUY 17 SPYM limit 90.80 → order 2b8a256f-a8c9-429c-b8fc-c9ddd0282816 (core-2026-10-28) filled, 17 @ 90.71
| Candidate | Ref | G0 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|
| XLE | 68.21 | PASS | PASS | PASS | FAIL (FOMC) | PASS | SKIP | - | - | - |
| JNJ | 268.73 | PASS | PASS | PASS | FAIL (FOMC) | FAIL (spread 3.45%, ask +3.0%) | SKIP | - | - | - |
| KO | 91.18 | PASS | PASS | PASS | FAIL (FOMC) | PASS | SKIP | - | - | - |
New positions: none (satellites blocked by FOMC; carried to next non-event session, refs must be re-screened).
Health: run 10:26 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=ok | perplexity=n/a

### 2026-10-28 — Midday (run 13:11 ET)
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=2 | failing: none | Maintenance: none
Core: CORE_ACTION=DONE_TODAY (core-2026-10-28 filled) | Satellites held: none (no gap exits, no thesis checks)
Exits: none | Retries: XLE, JNJ, KO dropped for today (EVENT_TODAY=FOMC, G10 FAIL); refs re-screened next non-event session. No orders placed.
Health: run 13:11 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=n/a | perplexity=n/a

### 2026-10-28 - EOD Snapshot (Day 1, Wednesday)
**Portfolio:** $1,998.98 | **Cash:** $457.93 (22.9%) | **Invested:** 77.1% (floor 70%, days below: 0) | **Day P&L:** $-1.02 (-0.05%) | **Phase P&L:** $-1.02 (-0.05%) | **SPY today:** +0.34% | **SPY phase:** +0.34% | **Regime:** risk-on

| Ticker | Role | Shares | Entry | Last | Day chg | Unrealized | % of equity | Stop |
|---|---|---|---|---|---|---|---|---|
| SPYM | core | 17 | 90.71 | 90.65 | +0.1% | $-1.02 (-0.1%) | 77.1% | - |

**Fills today:** buy 17 SPYM @ 90.71 (core-2026-10-28)

KS failing: none
MISSING_COMMITS: none
**Notes:** Core SPYM bought (17 sh); satellites blocked by FOMC, no orders otherwise. Trailing SPY by 0.39pp on the day (core filled at the 10:26 ET limit, 25% cash). Tomorrow: no blocking event (next is NFP 2026-11-06); XLE/JNJ/KO need re-screening.
Health: run 16:38 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=ok | perplexity=n/a

### 2026-10-29 — Market-Open Decision (run 10:22 ET)
Preflight: exit 0 | EVENT_TODAY=none | PAUSED=no
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=1 | failing: none
Core: first check CORE_ACTION=HOLD (77.1% vs target 75.0%). After the XLE fill the target fell to 64.7% (77.1% outside band), ks.py re-check printed SELL 3 SPYM → order 51c94cea-0115-4174-812d-c214dc13ce5f (core-2026-10-29) filled 3 @ 90.543333. Core now 14 sh (63.5%), DONE_TODAY.
| Candidate | Ref | G1 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|
| XLE | 68.45 | PASS | PASS | PASS | PASS | PASS | BUY 3 | 2724744a-fcc2-4fdb-9d4c-c5fa8273b556 | 3 @ 68.776667 | f301574d-382b-4e97-82d7-8c73cbbc8d85 (new) |
| JNJ | 271.04 | PASS | FAIL (qty 0) | FAIL (no slot) | PASS | FAIL (spread 4.54%) | SKIP | - | - | - |
| KO | 91.73 | PASS | FAIL (qty 0) | FAIL (no slot) | PASS | PASS | SKIP | - | - | - |
| NUE | 271.79 | PASS | FAIL (qty 0) | FAIL (no slot) | PASS | FAIL (spread 5.09%) | SKIP | - | - | - |
New positions: XLE 3 sh @ 68.776667, trailing stop 7.0% (f301574d, status new), target $78.03, thesis: rank-1 sector, oil leadership (WTI >$101), above SMA50>SMA200. Risk: XOM earnings 10-30.
Note: KO/JNJ/NUE skipped on slots/sizing after XLE; slots were 1 (week 2/3, today 2/2 incl. core buy).
Health: run 10:22 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=ok | perplexity=n/a

### 2026-10-29 — Midday (run 13:13 ET)
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 | failing: none | Maintenance: none (ks.py MAINTENANCE=none)
Anomaly: 2 unplanned open buy orders found, created 07:59 UTC (pre-routine, not in any plan): `test-2026-10-29-dup` (buy 1 SPYM limit $1, id faad1776-f400-4a1d-bab6-ea1ac1b7a9c1) and `sat-2026-10-29-WMT-extra` (buy 1 WMT limit $104.03, id 3c39e7ea-40e1-4651-b053-432371df8bd2; a fill would be an unplanned satellite with no stop). Both cancelled, order-get status `canceled`. Source unknown — user to check.
Gap/thesis: XLE $68.395 vs stop 64.07235 (trailing 7%, f301574d status new); change_today -0.0008; newsfeed XLE none. No gap exit.
Exits: none | Retries: none (core DONE_TODAY; JNJ/KO/NUE dropped at open, SAT_SLOTS=0)
Health: run 13:13 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=ok | perplexity=n/a

### 2026-10-29 - EOD Snapshot (Day 2, Thursday)
**Portfolio:** $1,992.64 | **Cash:** $523.22 (26.3%) | **Invested:** 73.7% (floor 70%, days below: 0) | **Day P&L:** $-10.58 (-0.53%) | **Phase P&L:** $-7.36 (-0.37%) | **SPY today:** -0.38% | **SPY phase:** -0.04% | **Regime:** risk-on

| Ticker | Role | Shares | Entry | Last | Day chg | Unrealized | % of equity | Stop |
|---|---|---|---|---|---|---|---|---|
| SPYM | core | 14 | 90.71 | 90.16 | -0.8% | $-7.70 (-0.6%) | 63.3% | - |
| XLE | satellite | 3 | 68.78 | 69.06 | +0.9% | $0.85 (+0.4%) | 10.4% | trailing_stop 7%/hwm 68.895 (f301574d) |

**Fills today:** buy 3 XLE @ 68.78 (sat-2026-10-29-XLE); sell 3 SPYM @ 90.54 (core-2026-10-29)

KS failing: none
MISSING_COMMITS: none
**Notes:** Lagged SPY on the day (-0.53% vs -0.38%) mostly from the core sale at a lower price and SPYM -0.8%; XLE +0.9% with stop live. Midday anomaly (2 unplanned pre-routine buy orders, cancelled) remains unexplained — user to check. Tomorrow: no EVENTS.md entry, no blocking event; XOM earnings 10-30 is an XLE risk, not a block.
Health: run 16:38 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=ok | perplexity=n/a

### 2026-10-30 — Market-Open Decision (run 10:18 ET)
Preflight: exit 0 | EVENT_TODAY=none | PAUSED=no
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=2 | failing: none
Core: initial CORE_ACTION=HOLD (in band). After PG+KO fills, satellites 28.4% → target 55.0% vs 63.0% held (out of band) → CORE_ACTION=SELL 2 SPYM → order 461b52fd-f67c-46fa-97a4-c0b271f79f8b (core-2026-10-30) filled 2 @ 89.26
| Candidate | Ref | G0 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|
| PG | 160.59 | PASS | PASS | PASS | PASS | PASS (spread 0.06%) | BUY | 7b15bf39-3352-44d9-8a64-087666749451 | 1 @ 163.28 | 440e2534-a313-404b-b1ca-2616ac32b092 (new) |
| PM | 208.50 | PASS | PASS | PASS | PASS | FAIL (spread 5.06%) | SKIP | - | - | - |
| KO | 92.82 | PASS | PASS | PASS | PASS | PASS (spread 0.02%) | BUY | a3f3d4e9-8f0e-4693-b3df-592de9b6144e | 2 @ 94.525 | 47621c1f-34bb-4218-8573-47070c831607 (new) |
New positions: PG 1 sh @ 163.28, trailing stop 7.0% (440e2534, new), target $183.07, thesis: Q1 beat, broker upgrades, XLP rank 3 above SMA50>SMA200.
New positions: KO 2 sh @ 94.525, trailing stop 7.0% (47621c1f, new), target $105.81, thesis: Q3 beat, FY26 EPS guide raised, XLP rank 3.
Note: sector XLP now 2 satellites; SPYM trimmed 14→12 to rebalance core to the satellite-adjusted target.
Health: run 10:18 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=ok | perplexity=n/a

### 2026-10-30 — Midday (run 13:08 ET)
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 | failing: none | Maintenance: none
Stops: KO 47621c1f, PG 440e2534, XLE f301574d all live; no price below stop level. Newsfeed 6h (KO,PG,XLE): 0 signals. No satellite down ≥4% (KO +1.9%, PG +1.6%, XLE +1.5%).
Exits: none | Retries: core DONE_TODAY (core-2026-10-30 filled); PM re-checked → VERDICT SKIP (G9 no slots/XLP cap, G11 spread 4.25%), dropped for today.
Health: run 13:08 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=n/a | perplexity=n/a
