# Research Log

One entry per trading day, written by the pre-market routine. Market-open executes the `CANDIDATE:` lines of today's entry; nothing else.
Read with `bash scripts/memtail.sh memory/RESEARCH-LOG.md 1` (today) — never the whole file. Phase 1 log: `memory/archive/phase1-2026/RESEARCH-LOG.md`.

## Entry format

```
## YYYY-MM-DD — Pre-market Research

### Preflight
NOW_ET=… | EVENT_TODAY=… | PAUSED=… | MISSING_COMMITS=…

### Regime and sectors
(paste `python3 scripts/screen.py sectors` output)

### Kill switches and core
(paste the ks.py lines: failing switches, ORDERS/BUYS/SAT flags, CORE, CORE_ACTION, MAINTENANCE)

### Screen
(paste the summary line + top-10 table of `python3 scripts/screen.py watchlist`)

### Yesterday's candidates
- SYM: FILLED / not filled: <reason> / dropped: <gate>

### Candidates (≥2, from ≥2 sectors)
#### 1. SYM — Name (sector ETF, rank N)
(paste `python3 scripts/screen.py candidate SYM` table, ending in its SCREEN_OK: line)
| G6 | PASS/FAIL | next earnings YYYY-MM-DD (confirmed/estimated) vs EARNINGS_OK_FROM — source [n] |
| G7 | PASS/FAIL | thesis in 2–3 sentences naming the specific driver |
- Catalysts last 7 days: … [n]
- Risk (what would make this wrong): …
CANDIDATE: SYM ref=123.45 stop_pct=8.2 sector=XLK g6=PASS g7=PASS
(only when G6 and G7 both passed — market-open can buy nothing else)

### Rejected screen passers
- SYM: G6 (earnings 2026-11-04) / G7 (no specific driver found) — one line each

### Decision
PLAN: core <CORE_ACTION summary or "in band">; satellites <SYM, SYM or none>
or
HOLD justified: core in band; every passer failed a named gate (see above)

Health: run HH:MM ET | preflight=N | mode=PAPER | ks=<n failing> | perplexity=ok|fallback
```

---

## 2026-10-27 — Phase 1b baseline (no research yet)
Log restarted for Phase 1b. First real entry is written by the first pre-market run.

## 2026-10-27 — Pre-market Research

NOTE: run executed at 15:37 ET (scheduled 07:07) — late; market open at run time. No orders in this routine.

### Preflight
NOW_ET=2026-10-27 15:37 | EVENT_TODAY=none | PAUSED=no | MISSING_COMMITS=none

### Regime and sectors
```
REGIME risk-on | SPY 765.37 vs SMA200 727.39 (+5.2%) | 61 consecutive closes above | flip needs 3 consecutive closes on the other side
SECTORS (completed bars through 2026-10-26, feed sip; RS = return minus SPY)
| Rank | ETF | R21 | R63 | RS21 | RS63 | Score | Label |
|---|---|---|---|---|---|---|---|
| 1 | XLE | +12.3% | +21.0% | +13.0% | +17.7% | +15.34 | Leading |
| 2 | XLV | +5.0% | +7.2% | +5.8% | +3.9% | +4.84 | Leading |
| 3 | XLP | +7.2% | +1.0% | +8.0% | -2.3% | +2.85 | Leading/Improving |
| 4 | XLY | +3.3% | +1.6% | +4.1% | -1.7% | +1.20 | Leading/Improving |
| 5 | XLK | -5.1% | +8.9% | -4.3% | +5.6% | +0.65 | Neutral |
| 6 | XLB | +3.2% | -1.8% | +3.9% | -5.1% | -0.60 | Neutral/Improving |
| 7 | XLU | +7.7% | -6.5% | +8.5% | -9.8% | -0.68 | Neutral/Improving |
| 8 | XLF | +2.2% | -2.7% | +2.9% | -6.1% | -1.56 | Lagging/Improving |
| 9 | XLRE | +3.0% | -7.0% | +3.8% | -10.3% | -3.26 | Lagging/Improving |
| 10 | XLI | -2.0% | -8.5% | -1.3% | -11.8% | -6.54 | Lagging |
| 11 | XLC | -8.1% | -5.3% | -7.3% | -8.6% | -7.95 | Lagging |
```

### Kill switches and core
All 12 switches PASS (KS-1..11, PDT). ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=2 (positions 0/3, today 0/2, week 0/3)
REGIME risk-on (SPY 765.37 vs SMA200 727.39; 61 consecutive closes above)
CORE SPYM: 0 sh = $0.00 (0.0%) | target 75.0% | band +/-5pp
CORE_ACTION=BUY 17 SPYM limit 90.83 ($1,544.11) -> bash scripts/alpaca.sh order '{"symbol":"SPYM","qty":"17","side":"buy","type":"limit","limit_price":"90.83","time_in_force":"day","client_order_id":"core-2026-10-27"}'
SECTOR_COOLDOWNS=none | MAINTENANCE=none
(Note: ks.py shows start date 2026-10-28; Day-1 core buy not yet executed.)

### Screen
Screened 68 (0 no data) | pass G1 price 46 | G2 liquidity 68 | G3 trend 23 | G4 not-chasing 49 | G5 sector 46 | G8 size 44 | ALL 6
| # | Ticker | Sector (rank) | Close | R5 | R21 | R63 | RS63 | vs 52wH | Stop | Qty | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | PLTR | XLK (5) | 198.84 | +2.4% | +4.8% | +61.0% | +57.7% | -6.6% | 9.2% | 1 | +60.46 |
| 2 | ABBV | XLV (2) | 286.74 | +1.4% | +8.5% | +8.9% | +5.6% | -1.6% | 7.0% | 1 | +10.26 |
| 3 | KO | XLP (3) | 92.70 | -0.8% | +5.6% | +5.0% | +1.7% | -2.8% | 7.0% | 3 | +4.88 |
| 4 | PM | XLP (3) | 201.87 | +0.4% | +6.0% | +0.8% | -2.5% | -4.1% | 7.0% | 1 | +0.92 |
| 5 | JNJ | XLV (2) | 266.30 | +4.9% | -1.8% | -0.2% | -3.5% | -5.3% | 7.0% | 1 | -3.99 |
| 6 | NUE | XLB (6) | 257.35 | -1.3% | +4.1% | -3.1% | -6.4% | -8.1% | 7.0% | 1 | -3.99 |
Near misses (one gate): NVDA G3; ORCL G3; ANET G3; AMZN G3; TJX G3; CMG G3; RTX G5; XOM G4; CVX G4; EOG G4; SLB G4; PG G8

### Yesterday's candidates
- none (Phase 1b Day 0; no prior candidates)

### Candidates (EARNINGS_OK_FROM=2026-11-04)

#### Rejected at G6
- PLTR (XLK): G6 FAIL — Q3 earnings 2026-11-02 confirmed (< 2026-11-04) [perplexity: vantagemarkets/marketscreener]
- ABBV (XLV): G6 FAIL — Q3 earnings 2026-10-30 confirmed (< 2026-11-04) [perplexity: barrons/alphastreet]
- PM (XLP): not checked — second XLP name; KO already covers XLP, JNJ/NUE give 3 sectors

#### 1. KO — Coca-Cola (XLP, rank 3)
CANDIDATE CHECK KO (XLP, sector rank 3) - completed bars through 2026-10-26, equity $2,000.00
| Gate | Result | Detail |
|---|---|---|
| G1 | PASS | close $92.70 vs cap $300.00 (15% of equity) |
| G2 | PASS | ADV20 $1525M vs $50M |
| G3 | PASS | close 92.70 > SMA50 89.20 > SMA200 81.71 (needs close > SMA50 > SMA200) |
| G4 | PASS | R5 -0.8% (max +15%); close 92.70 vs SMA20+2xATR 93.18 |
| G5 | PASS | XLP rank 3 (max 7); RS63 +1.7% (override > +5%) |
| G8 | PASS | ref 92.70; stop 7.0% (~86.21); target 105.68 (2:1); qty 3 = $278.10 (13.9% of equity, min 8%) |
Next: G6 (earnings) and G7 (thesis). Only if both pass, write the final line 'CANDIDATE: KO ref=92.70 stop_pct=7.0 sector=XLP g6=PASS g7=PASS'.
| G6 | PASS | reported Q3 today 2026-10-27; next report 2027-02-16 (estimated) >= 2026-11-04; last report <45d — source [investors.coca-colacompany.com] |
| G7 | PASS | Q3 beat (EPS $0.91 vs $0.88, revenue $13.35B vs $12.92B) and FY26 EPS growth guidance raised to >=11%; XLP is a top-3 sector and KO is a trend leader above SMA50>SMA200. Risk: North America volume flat, higher logistics costs, post-earnings gap/“sell the news” (TipRanks: slipped despite raise). |
CANDIDATE: KO ref=92.70 stop_pct=7.0 sector=XLP g6=PASS g7=PASS

#### 2. JNJ — Johnson & Johnson (XLV, rank 2)
CANDIDATE CHECK JNJ (XLV, sector rank 2) - completed bars through 2026-10-26, equity $2,000.00
| Gate | Result | Detail |
|---|---|---|
| G1 | PASS | close $266.30 vs cap $300.00 (15% of equity) |
| G2 | PASS | ADV20 $2027M vs $50M |
| G3 | PASS | close 266.30 > SMA50 265.32 > SMA200 245.78 (needs close > SMA50 > SMA200) |
| G4 | PASS | R5 +4.9% (max +15%); close 266.30 vs SMA20+2xATR 273.40 |
| G5 | PASS | XLV rank 2 (max 7); RS63 -3.5% (override > +5%) |
| G8 | PASS | ref 266.30; stop 7.0% (~247.66); target 303.58 (2:1); qty 1 = $266.30 (13.3% of equity, min 8%) |
Next: G6 (earnings) and G7 (thesis). Only if both pass, write the final line 'CANDIDATE: JNJ ref=266.30 stop_pct=7.0 sector=XLV g6=PASS g7=PASS'.
| G6 | PASS | next earnings 2027-01-20 (estimated) >= 2026-11-04; last report Oct (<45d) — source [theearningsmadness.com/company/JNJ] |
| G7 | PASS | Pharma oncology pipeline momentum (JNJ-6143 75-77% response, PROTEUS Phase 3 positive, Tremfya data) in XLV (rank 2, Leading) with price above SMA50>SMA200. Risk: Stelara erosion, MedTech slower growth, pricing/litigation; R21 -1.8% shows momentum is soft. |
CANDIDATE: JNJ ref=266.30 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 3. NUE — Nucor (XLB, rank 6)
CANDIDATE CHECK NUE (XLB, sector rank 6) - completed bars through 2026-10-26, equity $2,000.00
| Gate | Result | Detail |
|---|---|---|
| G1 | PASS | close $257.35 vs cap $300.00 (15% of equity) |
| G2 | PASS | ADV20 $304M vs $50M |
| G3 | PASS | close 257.35 > SMA50 252.48 > SMA200 221.89 (needs close > SMA50 > SMA200) |
| G4 | PASS | R5 -1.3% (max +15%); close 257.35 vs SMA20+2xATR 266.22 |
| G5 | PASS | XLB rank 6 (max 7); RS63 -6.4% (override > +5%) |
| G8 | PASS | ref 257.35; stop 7.0% (~239.34); target 293.38 (2:1); qty 1 = $257.35 (12.9% of equity, min 8%) |
Next: G6 (earnings) and G7 (thesis). Only if both pass, write the final line 'CANDIDATE: NUE ref=257.35 stop_pct=7.0 sector=XLB g6=PASS g7=PASS'.
| G6 | PASS | reported Q3 2026-10-26; next earnings 2027-01-25 (estimated) >= 2026-11-04 — source [simplywall.st/NUE] |
| G7 | PASS | Record Q3 shipments (7.2Mt), earnings more than doubled, Q4 guided flat-to-up, data-center structural-steel demand visible in order book, capex moderating -> FCF. Risk: steel pricing cyclicality; RS63 -6.4% (sector rank 6 passes G5). |
CANDIDATE: NUE ref=257.35 stop_pct=7.0 sector=XLB g6=PASS g7=PASS

### Decision
Core: BUY 17 SPYM (limit 90.83) per CORE_ACTION — market-open/next executes. Satellites: KO (XLP), JNJ (XLV), NUE (XLB) planned, 3 sectors; EVENT_TODAY=none so entries allowed. Sizing/slots (2 today) decided by ks.py --check. Late run flagged: pre-market executed 15:37 ET, same session as market open.

Health: run 15:37 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=ok | perplexity=ok
