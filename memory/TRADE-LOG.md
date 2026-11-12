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

### 2026-10-30 - EOD Snapshot (Day 3, Friday)
**Portfolio:** $1,976.76 | **Cash:** $349.39 (17.7%) | **Invested:** 82.3% (floor 70%, days below: 0) | **Day P&L:** $-20.83 (-1.04%) | **Phase P&L:** $-23.24 (-1.16%) | **SPY today:** -1.77% | **SPY phase:** -1.81% | **Regime:** risk-on

| Ticker | Role | Shares | Entry | Last | Day chg | Unrealized | % of equity | Stop |
|---|---|---|---|---|---|---|---|---|
| SPYM | core | 12 | 90.71 | 88.97 | -1.8% | $-20.94 (-1.9%) | 54.0% | - |
| XLE | satellite | 3 | 68.78 | 69.98 | +1.9% | $3.62 (+1.8%) | 10.6% | trailing_stop 7%/hwm 70.151 (f301574d) |
| KO | satellite | 2 | 94.53 | 94.27 | +1.6% | $-0.51 (-0.3%) | 9.5% | trailing_stop 7%/hwm 94.6399 (47621c1f) |
| PG | satellite | 1 | 163.28 | 161.30 | +0.4% | $-1.98 (-1.2%) | 8.2% | trailing_stop 7%/hwm 163.66 (440e2534) |

**Fills today:** buy 1 PG @ 163.28 (sat-2026-10-30-PG); buy 2 KO @ 94.53 (sat-2026-10-30-KO); sell 2 SPYM @ 89.26 (core-2026-10-30)

KS failing: none
MISSING_COMMITS: none
**Notes:** Equity -1.04% on the day vs SPY -1.77%; phase -1.16% vs SPY -1.81%, with satellites (XLE/KO/PG) cushioning the core drop. All 3 satellites carry live 7% trailing stops, no orphans. Monday 2026-11-02: no blocking event (next is NFP 2026-11-06); satellite slots are 0/3 so no new entries until a slot frees.
Health: run 16:38 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=ok | perplexity=n/a

### 2026-11-02 — Market-Open Decision (run 10:48 ET)
Preflight: exit 0 | EVENT_TODAY=none | PAUSED=no | note: fired 10:48 ET vs 10:12 schedule (~36 min late)
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 | failing: none
Core: CORE_ACTION=HOLD (in band) - SPYM 12 sh = $1,077.00 (54.2%), target 55.0%; no order
Maintenance: none
| Candidate | Ref | G0 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|
| ABBV | 294.89 | PASS | FAIL (qty 0, budget $250.10) | FAIL (no slots 3/3) | PASS | FAIL (ask -2.0% ok; spread 1.40%) | SKIP | - | - | - |
| NUE | 273.87 | PASS | FAIL (qty 0) | FAIL (no slots) | PASS | FAIL (ask +4.7%) | SKIP | - | - | - |
| JNJ | 273.20 | PASS | FAIL (qty 0) | FAIL (no slots) | PASS | PASS | SKIP | - | - | - |
New positions: none. Outcome: all 3 candidates skipped, no slot (XLE, KO, PG held with stops).
Health: run 10:48 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-02 — Midday (run 13:15 ET)
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 | failing: none | Maintenance: none
Core: CORE_ACTION=HOLD (in band) - SPYM 12 sh = $1,071.60 (54.1%), target 55.0%
Stops: KO, PG, XLE all have live trailing stops (STATE.md). Positions: XLE change_today -3.36% (above -4% threshold, no news check); no satellite below stop; newsfeed 0 signals (KO, PG, XLE).
Exits: none | Retries: ABBV, NUE, JNJ re-checked via ks.py --check: SKIP (G8 qty 0, G9 no slots 3/3; ABBV/NUE also G11). Dropped for today. PM was dropped in pre-market.
Health: run 13:15 ET | preflight=0 | mode=PAPER | ks=0 | notify=n/a | perplexity=n/a

### 2026-11-02 - EOD Snapshot (Day 4, Monday)
**Portfolio:** $1,970.24 | **Cash:** $349.37 (17.7%) | **Invested:** 82.3% (floor 70%, days below: 0) | **Day P&L:** $-6.32 (-0.32%) | **Phase P&L:** $-29.76 (-1.49%) | **SPY today:** -0.48% | **SPY phase:** -2.28% | **Regime:** risk-on

| Ticker | Role | Shares | Entry | Last | Day chg | Unrealized | % of equity | Stop |
|---|---|---|---|---|---|---|---|---|
| SPYM | core | 12 | 90.71 | 88.62 | -0.4% | $-25.08 (-2.3%) | 54.0% | - |
| XLE | satellite | 3 | 68.78 | 67.38 | -3.8% | $-4.19 (-2.0%) | 10.3% | trailing_stop 7%/hwm 70.151 (f301574d) |
| KO | satellite | 2 | 94.53 | 95.87 | +1.9% | $2.68 (+1.4%) | 9.7% | trailing_stop 7%/hwm 96.255 (47621c1f) |
| PG | satellite | 1 | 163.28 | 163.56 | +1.2% | $0.28 (+0.2%) | 8.3% | trailing_stop 7%/hwm 164.355 (440e2534) |

**Fills today:** none
KS failing: none
MISSING_COMMITS: none
**Notes:** Flat day, no fills; equity -0.32% vs SPY -0.48%, phase -1.49% vs SPY -2.28%. All 3 satellites stopped, no orphans. Tomorrow: no blocking event (NFP is 2026-11-06).
Health: run 16:37 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-03 — Market-Open Decision (run 10:13 ET)
Preflight: exit 0 | EVENT_TODAY=none | PAUSED=no
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 | failing: none
Core: CORE_ACTION=HOLD (in band; SPYM 12 sh = 54.2% vs target 55.0%, band +/-5pp) - no order. MAINTENANCE=none.
| Candidate | Ref | G0 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|
| ABBV | 288.84 | PASS | FAIL (qty 0, budget $251.07) | FAIL (no slots 3/3) | PASS | FAIL (spread 1.79%) | SKIP | - | - | - |
| NUE | 277.65 | PASS | FAIL (qty 0) | FAIL (no slots) | PASS | FAIL (spread 3.99%) | SKIP | - | - | - |
| JNJ | 270.56 | PASS | FAIL (qty 0) | FAIL (no slots) | PASS | FAIL (ask +3.2% vs ref; spread 3.69%) | SKIP | - | - | - |
| COP (checked, not planned) | none | PASS | FAIL | FAIL | PASS | FAIL | SKIP | - | - | - |
New positions: none. Slots 3/3 (XLE, KO, PG), as the pre-market plan anticipated.
Health: run 10:13 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-03 — Midday (run 13:08 ET)
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 | failing: none | Maintenance: none (all 3 satellites have stops; no tighten/trim)
Exits: none (no satellite below stop; none down ≥4% today; newsfeed 0 signals KO/PG/XLE) | Retries: core HOLD (54.2%, in band). ABBV, NUE, JNJ re-checked: SKIP again (G8 qty 0, budget $250.79; G9 no slots 3/3); G11 now PASS. Dropped for today.
Health: run 13:08 ET | preflight=0 | mode=PAPER | ks=0 | notify=n/a | perplexity=n/a

### 2026-11-03 - EOD Snapshot (Day 5, Tuesday)
**Portfolio:** $1,966.92 | **Cash:** $349.37 (17.8%) | **Invested:** 82.2% (floor 70%, days below: 0) | **Day P&L:** $-1.66 (-0.08%) | **Phase P&L:** $-33.08 (-1.65%) | **SPY today:** +0.30% | **SPY phase:** -1.99% | **Regime:** risk-on

| Ticker | Role | Shares | Entry | Last | Day chg | Unrealized | % of equity | Stop |
|---|---|---|---|---|---|---|---|---|
| SPYM | core | 12 | 90.71 | 88.92 | +0.4% | $-21.51 (-2.0%) | 54.2% | - |
| XLE | satellite | 3 | 68.78 | 66.57 | -1.0% | $-6.62 (-3.2%) | 10.2% | trailing_stop 7%/hwm 70.151 (f301574d) |
| KO | satellite | 2 | 94.53 | 94.66 | -1.2% | $0.27 (+0.1%) | 9.6% | trailing_stop 7%/hwm 96.255 (47621c1f) |
| PG | satellite | 1 | 163.28 | 161.51 | -1.3% | $-1.77 (-1.1%) | 8.2% | trailing_stop 7%/hwm 164.355 (440e2534) |

**Fills today:** none
KS failing: none
MISSING_COMMITS: none
**Notes:** No trades; core HOLD in band (54.2% vs 55% target), all 3 satellites stopped. Day -0.08% vs SPY +0.30%; phase -1.65% vs SPY -1.99% (still ahead). Tomorrow 11-04: no blocking event (NFP is 11-06).
Health: run 16:38 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-04 — Market-Open Decision (run 10:14 ET)
Preflight: exit 0 | EVENT_TODAY=none | PAUSED=no
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=1 (pre-order) → 0 (post) | failing: none
Core: CORE_ACTION=HOLD (SPYM 54.7%, in band) → no order
Note: positions were 2/3 at run time (STATE.md showed 3/3 from 11-03 EOD); KS-11 shows a loser on 2026-11-04 — an earlier position closed today. Not investigated here; midday to review.
| Candidate | Ref | G0 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|
| ABBV | 286.00 | PASS | PASS | PASS | PASS | PASS | BUY | 20a64454-b4d4-4203-903d-9fe47bbffc3e (sat-2026-11-04-ABBV) | 1 @ 284.78 | a306f4a4-4a63-4755-a963-dde7219f0007 (new) |
| CVX | 225.27 | PASS | FAIL (qty 0) | FAIL (no slots) | PASS | PASS | SKIP | - | - | - |
| JNJ | 266.17 | PASS | FAIL (qty 0) | FAIL (no slots) | PASS | PASS | SKIP | - | - | - |
| XOM | 177.46 | PASS | FAIL (qty 0) | FAIL (no slots) | PASS | FAIL (spread 1.59%) | SKIP | - | - | - |
New positions: ABBV 1 sh @ 284.78, trailing stop 7.0% (a306f4a4-4a63-4755-a963-dde7219f0007, status new), target $326.04, thesis: Q3 beat, FY26 guidance raised, XLV rank 1, trend intact.
Health: run 10:14 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-04 — Midday (run 13:08 ET)
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 (3/3) | failing: none | Maintenance: none (CORE_ACTION=HOLD, SPYM 54.5%)
Stops verified: ABBV a306f4a4 (new, 7%), KO 47621c1f (new, 7%), PG 440e2534 (new, 7%). No orphans, no open buys.
Exits: XLE 3 sh stopped out by trailing stop at 64.67 (filled 2026-11-04 14:33 UTC = 09:33 ET, stop-2026-10-29-XLE; before market-open's run, explains the 2/3 positions and KS-11 loser). No exit placed by midday. Gap check: no satellite below its stop; none down ≥4% today; newsfeed 6h: 0 signals on ABBV/KO/PG.
Retries: no core retry (HOLD). CVX/JNJ/XOM `--check` → SKIP again (G8 qty 0, G9 no slots 3/3; XOM also G11 ask -5.3% vs ref) — dropped for today.
Health: run 13:08 ET | preflight=0 | mode=PAPER | ks=0 | notify=n/a | perplexity=n/a

### 2026-11-04 - EOD Snapshot (Day 6, Wednesday)
**Portfolio:** $1,996.38 | **Cash:** $258.60 (13.0%) | **Invested:** 87.0% (floor 70%, days below: 0) | **Day P&L:** $29.95 (+1.52%) | **Phase P&L:** $-3.62 (-0.18%) | **SPY today:** +1.65% | **SPY phase:** -0.37% | **Regime:** risk-on

| Ticker | Role | Shares | Entry | Last | Day chg | Unrealized | % of equity | Stop |
|---|---|---|---|---|---|---|---|---|
| SPYM | core | 12 | 90.71 | 90.39 | +1.8% | $-3.84 (-0.4%) | 54.3% | - |
| ABBV | satellite | 1 | 284.78 | 294.49 | +3.0% | $9.71 (+3.4%) | 14.8% | trailing_stop 7%/hwm 295.4 (a306f4a4) |
| KO | satellite | 2 | 94.53 | 95.82 | +1.1% | $2.58 (+1.4%) | 9.6% | trailing_stop 7%/hwm 96.56 (47621c1f) |
| PG | satellite | 1 | 163.28 | 166.98 | +3.0% | $3.70 (+2.3%) | 8.4% | trailing_stop 7%/hwm 168.17 (440e2534) |

**Fills today:** sell 3 XLE @ 64.67 (stop-2026-10-29-XLE); buy 1 ABBV @ 284.78 (sat-2026-11-04-ABBV)
KS failing: none
MISSING_COMMITS: none
**Notes:** XLE stopped out at open (09:33 ET), ABBV bought as replacement with stop set; all 3 satellites protected, core in band (HOLD). Day +1.52% trailed SPY +1.65%; phase -0.18% vs SPY -0.37%. Tomorrow 11-05: no blocking event (NFP is Fri 11-06).
Health: run 16:37 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-05 — Market-Open Decision (run 10:15 ET)
Preflight: exit 0 | EVENT_TODAY=none | PAUSED=no
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 (positions 3/3, today 0/2, week 1/3) | failing: none
Core: CORE_ACTION=HOLD (SPYM 12 sh = $1,059.96, 53.4% vs target 55.0%, in band) - no order. MAINTENANCE=none.
| Candidate | Ref | G0 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|
| JNJ | 276.32 | PASS | FAIL (qty 0, budget $159.32) | FAIL (no slots 3/3) | PASS | FAIL (spread 4.40%, ask +6.2%) | SKIP | - | - | - |
| PM | 211.28 | PASS | FAIL (qty 0) | FAIL (no slots; XLP has 2) | PASS | FAIL (spread 6.19%) | SKIP | - | - | - |
| CVX | 216.96 | PASS | FAIL (qty 0) | FAIL (no slots 3/3) | PASS | PASS | SKIP | - | - | - |
| XOM | 169.27 | PASS | FAIL (qty 0) | FAIL (no slots 3/3) | PASS | PASS | SKIP | - | - | - |
New positions: none.
Health: run 10:15 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-05 — Midday (run 13:09 ET)
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 (3/3) | failing: none | Maintenance: none (MAINTENANCE=none; no ORPHAN/TIGHTEN/TRIM)
Core: CORE_ACTION=HOLD (SPYM 12 sh = $1,039.44, 53.3% vs target 55.0%, in band). SPYM change_today -0.04 (core, no stop, no action).
Satellites: ABBV -0.14%, KO +0.07%, PG +0.13% today; all stops present (KS-10 PASS). None down ≥4%; newsfeed 6h: 0 signals for ABBV,KO,PG.
Exits: none | Retries: none (core in band; JNJ/PM/CVX/XOM all blocked at open by G8 qty 0 / G9 no slots 3/3, dropped for today)
Health: run 13:09 ET | preflight=0 | mode=PAPER | ks=0 | notify=n/a | perplexity=n/a

### 2026-11-05 - EOD Snapshot (Day 7, Thursday)
**Portfolio:** $1,940.52 | **Cash:** $258.58 (13.3%) | **Invested:** 86.7% (floor 70%, days below: 0) | **Day P&L:** $-54.81 (-2.75%) | **Phase P&L:** $-59.48 (-2.97%) | **SPY today:** -4.41% | **SPY phase:** -4.76% | **Regime:** risk-on

| Ticker | Role | Shares | Entry | Last | Day chg | Unrealized | % of equity | Stop |
|---|---|---|---|---|---|---|---|---|
| SPYM | core | 12 | 90.71 | 86.20 | -4.5% | $-54.12 (-5.0%) | 53.3% | - |
| ABBV | satellite | 1 | 284.78 | 289.00 | -2.0% | $4.22 (+1.5%) | 14.9% | trailing_stop 7%/hwm 302.93 (a306f4a4) |
| KO | satellite | 2 | 94.53 | 95.80 | +0.0% | $2.55 (+1.3%) | 9.9% | trailing_stop 7%/hwm 97.39 (47621c1f) |
| PG | satellite | 1 | 163.28 | 166.94 | -0.2% | $3.66 (+2.2%) | 8.6% | trailing_stop 7%/hwm 170.52 (440e2534) |

**Fills today:** none
KS failing: none (KS-1 daily DD -2.75% vs -3% limit, close call)
MISSING_COMMITS: none
**Notes:** SPY fell -4.41% today; SPYM -4.5% drove the day loss, satellites held (ABBV -2.0%, KO/PG flat). Portfolio -2.75% vs SPY -4.41%, ahead of SPY by 1.66pp on the day and 1.79pp on the phase. Tomorrow 2026-11-06 is NFP: blocks new satellite entries (no slots free anyway); core in band, HOLD.
Health: run 16:37 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-06 — Market-Open Decision (run 10:15 ET)
Preflight: exit 0 | EVENT_TODAY=NFP | PAUSED=no
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=1 | failing: none
Core: CORE_ACTION=HOLD (SPYM 12 sh = $1,046.82, 53.9%, in band) → no order
Note: ABBV trailing stop (a306f4a4, stop-2026-11-04-ABBV) filled 1 sh @ 281.43 at 14:34 UTC (09:34 ET), before this run; entry 284.78 → loss; KS-11 shows 2 consecutive losers (limit <3). Positions now KO, PG, SPYM (slots 1).
| Candidate | Ref | G0 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|
| WELL | 245.43 | PASS | PASS | PASS | FAIL (NFP) | FAIL (spread 6.33%, ask +3.2%) | SKIP | - | - | - |
| NEM | 119.71 | PASS | PASS | PASS | FAIL (NFP) | FAIL (spread 4.70%, ask +4.9%) | SKIP | - | - | - |
| JNJ | 272.32 | PASS | PASS | PASS | FAIL (NFP) | FAIL (spread 3.32%) | SKIP | - | - | - |
| PM | 201.50 | PASS | PASS | FAIL (XLP cap) | FAIL (NFP) | FAIL (spread 10.60%, ask +4.3%) | SKIP | - | - | - |
New positions: none.
Health: run 10:15 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-06 — Midday Record (run 13:08 ET)
Preflight: exit 0 | EVENT_TODAY=NFP | PAUSED=no
KS: all 12 PASS | ORDERS_ALLOWED=yes | SAT_SLOTS=1 | equity $1,939.83
Core: CORE_ACTION=HOLD (SPYM 12 sh = $1,041.30, 53.7%, in band) → no retry
Maintenance: none | Positions: KO 2 (+1.77%), PG 1 (+1.75%), SPYM 12; both stops `new`, no gap exits; no satellite ≤ -4% today.
Newsfeed (6h, KO/PG): 0 signals.
Retries (--check): WELL SKIP (G10 NFP, G11 spread 10.54%, ask +4.5%) | NEM SKIP (G10 NFP; G11 passes) | JNJ SKIP (G10 NFP, G11 spread 4.13%, ask +5.2%) | PM SKIP (G9 XLP cap, G10, G11 spread 10.60%) → all dropped for today.
Orders placed/replaced/cancelled: none. Notification: none (no action).
Health: run 13:08 ET | preflight=0 | mode=PAPER | ks=0 | notify=n/a | perplexity=n/a

### 2026-11-06 - EOD Snapshot (Day 8, Friday)
**Portfolio:** $1,935.60 | **Cash:** $540.01 (27.9%) | **Invested:** 72.1% (floor 70%, days below: 0) | **Day P&L:** $-5.38 (-0.28%) | **Phase P&L:** $-64.40 (-3.22%) | **SPY today:** +0.31% | **SPY phase:** -4.47% | **Regime:** risk-on

| Ticker | Role | Shares | Entry | Last | Day chg | Unrealized | % of equity | Stop |
|---|---|---|---|---|---|---|---|---|
| SPYM | core | 12 | 90.71 | 86.56 | +0.3% | $-49.77 (-4.6%) | 53.7% | - |
| KO | satellite | 2 | 94.53 | 95.72 | -0.0% | $2.39 (+1.3%) | 9.9% | trailing_stop 7%/hwm 97.39 (47621c1f) |
| PG | satellite | 1 | 163.28 | 165.40 | -1.0% | $2.12 (+1.3%) | 8.5% | trailing_stop 7%/hwm 170.52 (440e2534) |

**Fills today:** sell 1 ABBV @ 281.43 (stop-2026-11-04-ABBV)
KS failing: none
MISSING_COMMITS: none
**Notes:** ABBV stopped out at 09:34 ET (loss; KS-11 streak 2, limit <3). Equity -0.28% vs SPY +0.31% on the day; phase -3.22% vs SPY -4.47%. No NFP-day entries (all candidates failed G10/G11). Next: Monday 11-09 has no blocking event; CPI is Tue 11-10 (blocks entries).
Health: run 16:38 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-09 — Market-Open Decision (run 10:17 ET)
Preflight: exit 0 | EVENT_TODAY=none | PAUSED=no
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=1 | failing: none
Core: CORE_ACTION=HOLD (SPYM 12 sh = $1,057.80, 54.1% vs target 56.8%, in band) → no order
| Candidate | Ref | G0 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|
| ABBV | 291.31 | PASS | PASS | PASS | PASS | FAIL (spread 4.74%) | SKIP | - | - | - |
| JNJ | 276.22 | PASS | PASS | PASS | PASS | PASS (spread 0.38%, ask +0.6%) | BUY | 47034bd2-73bd-48cd-93a3-7bf25af5c4ba (sat-2026-11-09-JNJ) | 1 @ 277.04 | e322b867-b33e-4c65-b1ef-ecdf4e288919 (new) |
| WELL | 245.01 | PASS | FAIL (qty 0) | FAIL (no slots after JNJ) | PASS | PASS | SKIP | - | - | - |
| NEM | 120.91 | PASS | FAIL | FAIL (no slots; sats 38.9% > 35%) | PASS | FAIL (spread 4.97%, ask +4.3%) | SKIP | - | - | - |
New positions: JNJ 1 sh @ 277.04, trailing stop 7.0% (e322b867, status new), target $314.89, thesis: XLV rank 1; FY26 guidance raised, OTTAVA FDA authorization, positive Ph3 data.
Health: run 10:17 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a
KS failing: none
MISSING_COMMITS: midday 2026-11-09
**Notes:** Midday routine missed today (no commit). JNJ bought at open and stopped; equity +1.71% vs SPY +2.37% on the day (lag from 13% cash); phase -1.57% vs SPY -2.20%. Tomorrow 11-10 is CPI (blocks new satellite entries).
Health: run 16:38 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-10 — Market-Open Decision (run 10:18 ET)
Preflight: exit 0 | EVENT_TODAY=CPI | PAUSED=no
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 | failing: none
Core: CORE_ACTION=HOLD (SPYM 12 sh = 54.0%, target 55.0%, in band) - no order. MAINTENANCE=none.
| Candidate | Ref | G0 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|
| ABBV | 293.30 | PASS | FAIL (qty 0) | FAIL (no slots 3/3) | FAIL (CPI) | PASS | SKIP | - | - | - |
| WELL | 247.35 | PASS | FAIL (qty 0) | FAIL (no slots) | FAIL (CPI) | FAIL (spread 5.32%, ask +3.9%) | SKIP | - | - | - |
| AMZN | 266.93 | PASS | FAIL (qty 0) | FAIL (no slots) | FAIL (CPI) | PASS | SKIP | - | - | - |
| XLF | 57.99 | PASS | FAIL (qty 2 = 5.9% < 8%) | FAIL (no slots; sats 38.6% > 35%) | FAIL (CPI) | PASS | SKIP | - | - | - |
New positions: none. Cash $262.94 (13.3%) idle - same band/cash issue as the 11-06 lesson.
Health: run 10:18 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-10 — Midday (run 13:08 ET)
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 | failing: none | Maintenance: none (all 3 satellites hold trailing stops; no TIGHTEN/ORPHAN/TRIM)
Core: CORE_ACTION=HOLD (SPYM 12 sh = 53.7%, target 55.0%, in band) - no order.
Exits: none (JNJ +1.5%, KO +2.3%, PG +3.8% vs entry; none down >=4% today; newsfeed: 2 bull JNJ signals, no bear) | Retries: none (no CORE_ACTION; today's candidates ABBV/WELL/AMZN/XLF were SKIP at open - CPI G10 block, SAT_SLOTS=0; dropped for today)
Equity $1,960.49 | cash $262.94 | invested 86.6%. No notification (no orders).
Health: run 13:08 ET | preflight=0 | mode=PAPER | ks=0 | notify=n/a | perplexity=n/a

### 2026-11-10 - EOD Snapshot (Day 10, Tuesday)
**Portfolio:** $1,967.08 | **Cash:** $262.94 (13.4%) | **Invested:** 86.6% (floor 70%, days below: 0) | **Day P&L:** $-1.43 (-0.07%) | **Phase P&L:** $-32.92 (-1.65%) | **SPY today:** -0.37% | **SPY phase:** -2.56% | **Regime:** risk-on

| Ticker | Role | Shares | Entry | Last | Day chg | Unrealized | % of equity | Stop |
|---|---|---|---|---|---|---|---|---|
| SPYM | core | 12 | 90.71 | 88.40 | -0.2% | $-27.72 (-2.5%) | 53.9% | - |
| JNJ | satellite | 1 | 277.04 | 280.99 | -0.4% | $3.95 (+1.4%) | 14.3% | trailing_stop 7%/hwm 283.2502 (e322b867) |
| KO | satellite | 2 | 94.53 | 96.90 | +0.9% | $4.75 (+2.5%) | 9.9% | trailing_stop 7%/hwm 97.39 (47621c1f) |
| PG | satellite | 1 | 163.28 | 168.55 | +0.1% | $5.27 (+3.2%) | 8.6% | trailing_stop 7%/hwm 170.52 (440e2534) |

**Fills today:** none
KS failing: none
MISSING_COMMITS: none
**Notes:** CPI day, no orders; slots full (3/3), core HOLD in band. Equity -0.07% vs SPY -0.37% on the day; phase -1.65% vs SPY -2.56%. Tomorrow: no blocking event in EVENTS.md.
Health: run 16:37 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-11 — Market-Open Decision (run 10:15 ET)
Preflight: exit 0 | EVENT_TODAY=none | PAUSED=no
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 | failing: none
Core: CORE_ACTION=HOLD (in band; SPYM 54.3% vs target 55.0%, band ±5pp) | MAINTENANCE=none
| Candidate | Ref | G0 | G1 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ABBV | 293.89 | PASS | FAIL (ask 306.81 > cap 295.02) | FAIL (qty 0) | FAIL (no slots 3/3) | PASS | FAIL (spread 10.67%, ask +4.4%) | SKIP | - | - | - |
| WELL | 247.66 | PASS | PASS | FAIL (qty 0) | FAIL (no slots) | PASS | PASS | SKIP | - | - | - |
| AMZN | 270.87 | PASS | PASS | FAIL (qty 0) | FAIL (no slots) | PASS | PASS | SKIP | - | - | - |
| XLF | 58.29 | PASS | PASS | FAIL (qty 2 = 5.9% < min 8%) | FAIL (no slots; sats 38.3% > 35%) | PASS | PASS | SKIP | - | - | - |
| AMT | 190.37 | PASS | PASS | FAIL (qty 0) | FAIL (no slots) | PASS | FAIL (spread 4.99%) | SKIP | - | - | - |
No new positions. Slots 3/3 (JNJ, KO, PG); cash $262.94 idle (13.4%) — same band/cash pattern as the 11-06 lesson.
Health: run 10:15 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-11 — Midday (run 13:09 ET)
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 | failing: none | Maintenance: none
Core: CORE_ACTION=HOLD (SPYM 54.4% vs target 55.0%, in band)
Stops: JNJ, KO, PG all protected (KS-10 PASS). No satellite down ≥4% (JNJ -1.03%, KO -0.10%, PG -1.00%). Newsfeed 6h: 1 bull JNJ (conf 0.55), no bear signals.
Exits: none | Retries: ABBV, WELL, AMZN, XLF, AMT re-checked — all SKIP (G8, G9 no slots 3/3; WELL/AMT also G11 spread). Dropped for today.
Health: run 13:09 ET | preflight=0 | mode=PAPER | ks=0 | notify=n/a | perplexity=n/a

### 2026-11-11 - EOD Snapshot (Day 11, Wednesday)
**Portfolio:** $1,979.30 | **Cash:** $262.94 (13.3%) | **Invested:** 86.7% (floor 70%, days below: 0) | **Day P&L:** $13.74 (+0.70%) | **Phase P&L:** $-20.70 (-1.04%) | **SPY today:** +1.32% | **SPY phase:** -1.28% | **Regime:** risk-on

| Ticker | Role | Shares | Entry | Last | Day chg | Unrealized | % of equity | Stop |
|---|---|---|---|---|---|---|---|---|
| SPYM | core | 12 | 90.71 | 89.44 | +1.3% | $-15.24 (-1.4%) | 54.2% | - |
| JNJ | satellite | 1 | 277.04 | 280.41 | -0.1% | $3.37 (+1.2%) | 14.2% | trailing_stop 7%/hwm 283.2502 (e322b867) |
| KO | satellite | 2 | 94.53 | 97.50 | +0.6% | $5.95 (+3.1%) | 9.9% | trailing_stop 7%/hwm 97.825 (47621c1f) |
| PG | satellite | 1 | 163.28 | 167.67 | -0.6% | $4.39 (+2.7%) | 8.5% | trailing_stop 7%/hwm 170.52 (440e2534) |

**Fills today:** none
KS failing: none
MISSING_COMMITS: none
**Notes:** No trades; slots 3/3, core in band (54.2% vs 55.0%). Day +0.70% vs SPY +1.32% (lagged); phase -1.04% vs SPY -1.28% (ahead). Tomorrow 2026-11-12: no blocking event in EVENTS.md.
Health: run 16:37 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-12 — Market-Open Decision (run 10:15 ET)
Preflight: exit 0 | EVENT_TODAY=none | PAUSED=no
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 | failing: none
Core: CORE_ACTION=HOLD (SPYM 54.0% vs target 55.0%, in band) | Maintenance: none
| Candidate | Ref | G0 | G8 | G9 | G10 | G11 | Action | Buy order | Fill | Stop order |
|---|---|---|---|---|---|---|---|---|---|---|
| ABBV | 294.98 | PASS | FAIL (qty 0) | FAIL (no slots 3/3) | PASS | FAIL (spread 4.19%) | SKIP | - | - | - |
| WELL | 247.35 | PASS | FAIL (qty 0) | FAIL (no slots 3/3) | PASS | FAIL (spread 5.25%) | SKIP | - | - | - |
| COP | 137.86 | PASS | FAIL (qty 1, 7.4% < 8%) | FAIL (no slots; sats 40.1% > 35%) | PASS | FAIL (ask +6.2%, spread 6.00%) | SKIP | - | - | - |
| XLF | 58.63 | PASS | FAIL (qty 2, 5.9% < 8%) | FAIL (no slots; sats 38.6% > 35%) | PASS | PASS | SKIP | - | - | - |
New positions: none. Cash $262.94 (13.3%) idle; slots full (JNJ, KO, PG) — same band/cash issue as 11-06 lesson.
Health: run 10:15 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=n/a

### 2026-11-12 — Midday (run 13:08 ET)
KS: ORDERS_ALLOWED=yes BUYS_ALLOWED=yes SAT_ENTRIES_ALLOWED=yes SAT_SLOTS=0 | failing: none | Maintenance: none (no ORPHAN/TIGHTEN/TRIM; JNJ, KO, PG each have a trailing stop)
Core: CORE_ACTION=HOLD (SPYM 54.1% vs target 55.0%, in band)
Exits: none (no satellite below stop; change_today JNJ +1.59%, KO +0.56%, PG +0.65%; news feed 0 signals 6h) | Retries: none — open candidates ABBV/WELL/COP/XLF dropped for today, slots 3/3 (G9)
Health: run 13:08 ET | preflight=0 | mode=PAPER | ks=0 | notify=n/a | perplexity=n/a
