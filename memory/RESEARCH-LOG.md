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

## 2026-10-28 — Pre-market Research

### Preflight
NOW_ET=2026-10-28 07:18 | EVENT_TODAY=FOMC | PAUSED=no | MISSING_COMMITS=none | PREFLIGHT_EXIT=0 | EARNINGS_OK_FROM=2026-11-05

### Regime and sectors
REGIME risk-on | SPY 769.66 vs SMA200 727.76 (+5.8%) | 61 consecutive closes above
Top sectors (bars through 2026-10-27): 1 XLE (+10.05) | 2 XLV (+3.18) | 3 XLK (+2.56) | 4 XLY | 5 XLP | 6 XLB | 7 XLU

### Kill switches and core
All 12 switches PASS. ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=2
REGIME risk-on
CORE SPYM: 0 sh = $0.00 (0.0%) | target 75.0% | band +/-5pp
CORE_ACTION=BUY 17 SPYM limit 90.68 ($1,541.56) -> bash scripts/alpaca.sh order '{"symbol":"SPYM","qty":"17","side":"buy","type":"limit","limit_price":"90.68","time_in_force":"day","client_order_id":"core-2026-10-28"}'
MAINTENANCE=none

### Screen
Screened 68 (0 no data) | ALL 9
Top: PLTR (XLK), XLE, XOM (XLE), ABBV (XLV), XLV, KO (XLP), PM (XLP), XLP, JNJ (XLV)
Near misses: NVDA G3; ORCL G3; ANET G3; AMZN G3; TJX G3; CMG G3; CVX G4; COP G4; EOG G4; SLB G4; PG G8; CEG G3

### Yesterday's candidates
- KO: not filled: market-open/midday ran after the close (preflight 31), no entries. Re-screened today, passes.
- JNJ: not filled: same reason. Re-screened today, passes.
- NUE: not filled: same reason. Not in today's top-9 (G3/G4/G5 re-screen); dropped from today's list.

### Candidates
#### Rejected
- PLTR (XLK): G6 FAIL — earnings 2026-11-02 confirmed (< 2026-11-05) [yesterday's perplexity check, unchanged]
- ABBV (XLV): G6 FAIL — earnings 2026-10-30 confirmed (< 2026-11-05) [yesterday's check, unchanged]
- XOM (XLE): G6 FAIL — Q3 earnings 2026-10-30 confirmed, company-announced [perplexity: simplywall.st, 247wallst]
- XLV (XLV): not checked — same sector as JNJ; JNJ covers XLV
- PM (XLP): not checked — KO covers XLP

#### 1. XLE — Energy Select Sector SPDR (XLE, rank 1)
G1 PASS $68.21 vs cap $300 | G2 PASS ADV20 $2117M | G3 PASS 68.21 > SMA50 64.61 > SMA200 58.40 | G4 PASS R5 +0.4%, close 68.21 vs 69.10 | G5 PASS rank 1, RS63 +10.8% | G8 PASS stop 7.0% (~63.44), target 77.76, qty 4 = $272.84 (13.6%)
G6 PASS — sector ETF, no single earnings report of its own; largest holding XOM reports 2026-10-30 (noted as risk, not a gate: G6 applies to single-company reports).
G7 PASS — Oil leadership: WTI >$100 and Brent >$117 on Middle East supply risk (Oct 23), SPR at lowest since 1982 (Oct 26); XLE #1 sector, record high Oct 23, above SMA50>SMA200. Risk: ceasefire / reduced Middle East tension removes the crude premium; XOM earnings 10-30.
News feed: (none) for XLE-held names checked (XOM none).
CANDIDATE: XLE ref=68.21 stop_pct=7.0 sector=XLE g6=PASS g7=PASS

#### 2. JNJ — Johnson & Johnson (XLV, rank 2)
G1 PASS $268.73 vs cap $300 | G2 PASS ADV20 $2030M | G3 PASS 268.73 > SMA50 265.45 > SMA200 246.10 | G4 PASS R5 +3.6%, close 268.73 vs 273.23 | G5 PASS rank 2, RS63 -4.3% | G8 PASS stop 7.0% (~249.92), target 306.35, qty 1 = $268.73 (13.4%)
G6 PASS — next earnings 2027-01-20 (estimated) >= 2026-11-05; last report October (<45d) [perplexity: theearningsmadness.com/company/JNJ]
G7 PASS — Oncology pipeline momentum (JNJ-6143 12/16 responses, ERLEADA perioperative −62% recurrence/death, RYBREVANT FASPRO 77% ORR; possible approval by YE2026) in XLV (rank 2, Leading), price above SMA50>SMA200. Risk: 2027 EPS dilution ($1.36) from deals, MedTech growth, talc settlement; R63 vs SPY negative.
News feed: (none)
CANDIDATE: JNJ ref=268.73 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 3. KO — Coca-Cola (XLP, rank 5)
G1 PASS $91.18 vs cap $300 | G2 PASS ADV20 $1546M | G3 PASS 91.18 > SMA50 89.29 > SMA200 81.81 | G4 PASS R5 -2.5%, close 91.18 vs 93.52 | G5 PASS rank 5, RS63 -3.2% | G8 PASS stop 7.0% (~84.80), target 103.95, qty 3 = $273.54 (13.7%)
G6 PASS — reported Q3 2026-10-27; next report 2027-02 (Q4 results, 2027 guidance) >= 2026-11-05; last report <45d [perplexity: fidelity/cnbc 2026-10-27]
G7 PASS — Q3 beat (EPS $0.91 vs $0.88, rev $13.4B +7%), FY26 EPS growth guide raised to >=11%, KFC US fountain win from early 2027; XLP rank 5, above SMA50>SMA200. Risk: North America volume flat, logistics costs, post-earnings "sell the news".
CANDIDATE: KO ref=91.18 stop_pct=7.0 sector=XLP g6=PASS g7=PASS

### Decision
EVENT_TODAY=FOMC: market-open will NOT open new satellites today (G10). Core is not blocked: market-open buys 17 SPYM per CORE_ACTION (Day-1 core still unbought). Candidates XLE (XLE), JNJ (XLV), KO (XLP) = 3 sectors recorded for the next non-event session; refs must be re-screened then (ks.py takes ref from today's line only on today's entry).

Health: run 07:18 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=ok | perplexity=ok

## 2026-10-29 — Pre-market Research

### Preflight
NOW_ET=2026-10-29 07:11 | EVENT_TODAY=none | PAUSED=no | MISSING_COMMITS=none | PREFLIGHT_EXIT=0 | EARNINGS_OK_FROM=2026-11-06

### Regime and sectors
REGIME risk-on | SPY 772.31 vs SMA200 728.15 (+6.1%) | 61 consecutive closes above
Top sectors (bars through 2026-10-28): 1 XLE (+11.07) | 2 XLV (+4.99) | 3 XLY (+1.54) | 4 XLP (+1.25) | 5 XLK (+0.85) | 6 XLB (+0.43) | 7 XLF (-1.40)

### Kill switches and core
All 12 switches PASS. ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=1 (positions 0/3, today 1/2, week 1/3)
REGIME risk-on (SPY 772.31 vs SMA200 728.15; 61 consecutive closes above)
CORE SPYM: 17 sh = $1,542.24 (77.1%) | target 75.0% | band +/-5pp
CORE_ACTION=HOLD (in band)
MAINTENANCE=none
Note: ks.py counts "entries today 1 / week 1" (the 10-28 core buy); it leaves SAT_SLOTS=1, so market-open can fill at most one satellite today.

### Screen
Screened 68 (0 no data) | ALL 11
Top: PLTR (XLK), XLE, ABBV (XLV), NUE (XLB), XLV, PM (XLP), XLK, JNJ (XLV), KO (XLP), XLP
Near misses: NVDA G3; ORCL G3; ANET G3; AMZN G3; TJX G3; CMG G3; BAC G3; SCHW G3; RTX G5; XOM G4; CVX G4; COP G4

### Yesterday's candidates
- XLE: not filled: FOMC (G10) blocked satellites 10-28. Re-screened today, passes.
- JNJ: not filled: FOMC (G10) + G11 spread 3.45%. Re-screened today, passes.
- KO: not filled: FOMC (G10). Re-screened today, passes.

### Candidates
#### Rejected
- PLTR (XLK): G6 FAIL — earnings 2026-11-02 confirmed (< 2026-11-06) [carried from 10-28 check]
- ABBV (XLV): G6 FAIL — earnings 2026-10-30 confirmed (< 2026-11-06) [carried from 10-28 check]
- XLV, XLK, XLP, PM: not checked in full — XLV covered by JNJ, XLP by KO, XLK's lone pass-through (PLTR) failed G6; PM screened OK but KO already covers XLP (backup only)

#### 1. XLE — Energy Select Sector SPDR (XLE, rank 1)
G1 PASS $68.45 vs cap $300.02 | G2 PASS ADV20 $2138M | G3 PASS 68.45 > SMA50 64.70 > SMA200 58.51 | G4 PASS R5 +0.4%, close 68.45 vs 69.26 | G5 PASS rank 1, RS63 +12.0% | G8 PASS stop 7.0% (~63.66), target 78.03, qty 4 = $273.80 (13.7%)
G6 PASS — sector ETF has no earnings report of its own (same treatment as 10-28). Risk noted, not a gate: largest holding XOM reports 2026-10-30 (confirmed) [perplexity: simplywall.st, yahoo finance].
G7 PASS — Oil leadership: WTI >$101 (Oct 28) on Iran/Houthi supply risk, XLE record high Oct 23, rank 1 sector, above SMA50>SMA200. Risk: de-escalation removes the crude premium; XOM+CVX ≈39% of fund with XOM earnings tomorrow.
News feed: (none)
SCREEN_OK: XLE ref=68.45 stop_pct=7.0 sector=XLE
CANDIDATE: XLE ref=68.45 stop_pct=7.0 sector=XLE g6=PASS g7=PASS

#### 2. JNJ — Johnson & Johnson (XLV, rank 2)
G1 PASS $271.04 vs cap $300.02 | G2 PASS ADV20 $2032M | G3 PASS 271.04 > SMA50 265.45 > SMA200 246.40 | G4 PASS R5 +5.1%, close 271.04 vs 273.83 | G5 PASS rank 2, RS63 +1.8% | G8 PASS stop 7.0% (~252.07), target 308.99, qty 1 = $271.04 (13.6%)
G6 PASS — next report January 2027 (estimated, date unconfirmed) >= 2026-11-06; last report October (<45d) [perplexity: trefis 2026-10-27, marketbeat 2026-10-26]
G7 PASS — Oncology pipeline momentum (JNJ-6143 75% response, ERLEADA PROTEUS −62% recurrence/death, RYBREVANT FASPRO >75% ORR; FDA decision possible by YE2026; Dec 8 business review) in XLV (rank 2), above SMA50>SMA200. Risk: deal dilution, MedTech growth, talc litigation; spread was wide at the 10-28 open.
News feed: (none)
SCREEN_OK: JNJ ref=271.04 stop_pct=7.0 sector=XLV
CANDIDATE: JNJ ref=271.04 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 3. KO — Coca-Cola (XLP, rank 4)
G1 PASS $91.73 vs cap $300.02 | G2 PASS ADV20 $1538M | G3 PASS 91.73 > SMA50 89.34 > SMA200 81.92 | G4 PASS R5 -1.0%, close 91.73 vs 93.74 | G5 PASS rank 4, RS63 -0.5% | G8 PASS stop 7.0% (~85.31), target 104.57, qty 3 = $275.19 (13.8%)
G6 PASS — reported Q3 2026-10-27; next report 2027-02-16 (estimated) >= 2026-11-06; last report <45d [perplexity: investing.com, cnbc 2026-10-27]
G7 PASS — Q3 beat (EPS $0.91 vs $0.88, rev $13.4B +7%), FY26 EPS growth guide raised to >=11%, KFC US win from Jan 2027, Citi/Piper PT $103; XLP rank 4, above SMA50>SMA200. Risk: North America volume flat, "sell the beat" reaction, 2027 FX headwind.
News feed: 10-27 12:00 ET KO bull m2 conf 0.65 earnings "Coca-Cola Raises Profit Outlook…" (consistent with thesis)
SCREEN_OK: KO ref=91.73 stop_pct=7.0 sector=XLP
CANDIDATE: KO ref=91.73 stop_pct=7.0 sector=XLP g6=PASS g7=PASS

#### 4. NUE — Nucor (XLB, rank 6)
G1 PASS $271.79 vs cap $300.02 | G2 PASS ADV20 $329M | G3 PASS 271.79 > SMA50 252.59 > SMA200 222.96 | G4 PASS R5 +2.7%, close 271.79 vs 272.50 | G5 PASS rank 6, RS63 +1.6% | G8 PASS stop 7.0% (~252.76), target 309.84, qty 1 = $271.79 (13.6%)
G6 PASS — reported Q3 2026-10-26; next report 2027-01-27 (estimated) >= 2026-11-06; last report <45d [perplexity: simplywall.st, marketbeat]
G7 PASS — Steel prices at highest since spring 2022, record shipments 7.2M tons, Q4 guided in line/above Q3, towers-and-structures backlog doubled into 2028, capex moderating. Risk: $124M startup costs persisting into 2027, EPS slight miss, G4 close to upper band (271.79 vs 272.50).
News feed: (none)
SCREEN_OK: NUE ref=271.79 stop_pct=7.0 sector=XLB
CANDIDATE: NUE ref=271.79 stop_pct=7.0 sector=XLB g6=PASS g7=PASS

### Decision
EVENT_TODAY=none: satellites allowed. SAT_SLOTS=1 → market-open fills at most one; rank order XLE (XLE), JNJ (XLV), KO (XLP), NUE (XLB). 4 candidates / 4 sectors. Core HOLD (in band), no core order.

Health: run 07:11 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=ok | perplexity=ok

## 2026-10-30 — Pre-market Research

### Preflight
NOW_ET=2026-10-30 07:13 | EVENT_TODAY=none | PAUSED=no | MISSING_COMMITS=none | PREFLIGHT_EXIT=0 | EARNINGS_OK_FROM=2026-11-09

### Regime and sectors
REGIME risk-on | SPY 769.36 vs SMA200 728.53 (+5.6%) | 61 consecutive closes above
Top sectors (bars through 2026-10-29): 1 XLE (+11.62) | 2 XLV (+9.31) | 3 XLP (+4.61) | 4 XLB (+4.08) | 5 XLY (+1.49) | 6 XLU (+1.39) | 7 XLF (+1.38)

### Kill switches and core
All 12 switches PASS. ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=2 (positions 1/3, today 0/2, week 1/3)
REGIME risk-on (SPY 769.36 vs SMA200 728.53; 61 consecutive closes above)
CORE SPYM: 14 sh = $1,255.66 (63.2%) | target 64.5% | band +/-5pp
CORE_ACTION=HOLD (in band)
MAINTENANCE=none

### Screen
Screened 68 (0 no data) | ALL 7
Top: PLTR (XLK), ABBV (XLV), XLE (held), PG (XLP), PM (XLP), KO (XLP), XLP
Near misses: AMZN G3; TJX G3; CMG G3; BAC G3; SCHW G3; JNJ G4; XOM G4; CVX G4; EOG G4; SLB G4; NEE G3; CEG G3

### Yesterday's candidates
- XLE: FILLED 3 @ 68.78, stop f301574d live.
- JNJ: dropped: G8 qty 0 / no slot / G11 spread 4.54%; today fails G4.
- KO: not filled: no slot after XLE; re-screened today, passes.
- NUE: dropped: no slot / G11 spread 5.09%; absent from today's pass list.

### Candidates
#### Rejected
- PLTR (XLK): G6 FAIL — earnings 2026-11-02 (estimated, not confirmed) < 2026-11-09 [perplexity: marketbeat]
- ABBV (XLV): G6 FAIL — earnings 2026-10-30 confirmed (today) [perplexity: AbbVie]
- XLE: G0 FAIL — already held
- XLV: G4 FAIL — close 184.04 vs SMA20+2xATR 181.06
- XLP (ETF): screen OK; not checked further — single-stock XLP names cover the sector (backup only)

#### 1. PG — Procter & Gamble (XLP, rank 3)
G1 PASS $160.59 vs cap $298.16 | G2 PASS ADV20 $1555M | G3 PASS 160.59 > SMA50 149.62 > SMA200 148.85 | G4 PASS R5 -3.0%, close 160.59 vs 161.82 | G5 PASS rank 3, RS63 +8.2% | G8 PASS stop 7.0% (~149.35), target 183.07, qty 1 = $160.59 (8.1%)
G6 PASS — reported Q1 FY27 ~2026-10-24; next 2027-01-20 (estimated) >= 2026-11-09; last report <45d [perplexity: stockrow, yahoo finance]
G7 PASS — Q1 beat (adj EPS $2.00, organic sales +4%), Freedom Broker upgrade to Buy, BNP PT $189; XLP rank 3, above SMA50>SMA200. Risk: input-cost/FX headwind raised to ~11% of core EPS, Health Care volume -2.9%.
News feed: (none)
SCREEN_OK: PG ref=160.59 stop_pct=7.0 sector=XLP
CANDIDATE: PG ref=160.59 stop_pct=7.0 sector=XLP g6=PASS g7=PASS

#### 2. PM — Philip Morris International (XLP, rank 3)
G1 PASS $208.50 vs cap $298.16 | G2 PASS ADV20 $914M | G3 PASS 208.50 > SMA50 193.80 > SMA200 181.69 | G4 PASS R5 +3.4%, close 208.50 vs 210.55 | G5 PASS rank 3, RS63 +6.3% | G8 PASS stop 7.0% (~193.91), target 237.69, qty 1 = $208.50 (10.5%)
G6 PASS — reported Q3 2026-10-23; next 2027-02-04 (estimated) >= 2026-11-09; last report <45d [perplexity: investbamboo]
G7 PASS — Q3 beat (adj EPS $2.36 vs +$0.06), smoke-free growth (IQOS/ZYN), dividend +8.8%, Argus PT $220; XLP rank 3, above SMA50>SMA200. Risk: US ZYN investment/pricing pressure on Q4 operating income, Ukraine disruption.
News feed: (none)
SCREEN_OK: PM ref=208.50 stop_pct=7.0 sector=XLP
CANDIDATE: PM ref=208.50 stop_pct=7.0 sector=XLP g6=PASS g7=PASS

#### 3. KO — Coca-Cola (XLP, rank 3)
G1 PASS $92.82 vs cap $298.16 | G2 PASS ADV20 $1531M | G3 PASS 92.82 > SMA50 89.39 > SMA200 82.02 | G4 PASS R5 -2.6%, close 92.82 vs 94.12 | G5 PASS rank 3, RS63 +3.0% | G8 PASS stop 7.0% (~86.32), target 105.81, qty 3 = $278.46 (14.0%)
G6 PASS — reported Q3 2026-10-27; next 2027-02-12 (estimated) >= 2026-11-09; last report <45d [perplexity: investors.coca-colacompany.com, cnbc 2026-10-27]
G7 PASS — Q3 beat (EPS $0.91 vs $0.88, rev $13.4B), FY26 comp EPS growth guide raised to >=11%, FCF guide >=$13.0B, KFC US win from Jan 2027. Risk: 2027 FX headwind, Africa bottler sale dilution, post-rally "sell the beat".
News feed: 10-28 17:32 ET KO bull m1 conf 0.50 earnings "Files Q3 2026 Quarterly Report" (neutral/consistent)
SCREEN_OK: KO ref=92.82 stop_pct=7.0 sector=XLP
CANDIDATE: KO ref=92.82 stop_pct=7.0 sector=XLP g6=PASS g7=PASS

### Decision
EVENT_TODAY=none: satellites allowed. SAT_SLOTS=2; rank order PG, PM, KO (all XLP; sector cap 2 positions / 25% applies). Pipeline minimum NOT met on sectors: 3 candidates but only 1 sector (XLP). Every other screen passer rejected above with its failing gate (PLTR G6, ABBV G6, XLE G0, XLV G4); no other name passed the screen. Core HOLD (in band), no core order.

Health: run 07:13 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=ok | perplexity=ok
