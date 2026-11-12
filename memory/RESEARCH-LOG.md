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

## 2026-11-02 — Pre-market Research

### Preflight
NOW_ET=2026-11-02 07:30 | EVENT_TODAY=none | PAUSED=no | MISSING_COMMITS=none | PREFLIGHT_EXIT=0 | EARNINGS_OK_FROM=2026-11-10

### Regime and sectors
REGIME risk-on | SPY 755.72 vs SMA200 728.85 (+3.7%) | 61 consecutive closes above
Top sectors (bars through 2026-10-30): 1 XLE (+16.06) | 2 XLV (+13.26) | 3 XLP (+9.01) | 4 XLB (+6.69) | 5 XLU (+4.35) | 6 XLF (+2.76) | 7 XLY (+2.49)

### Kill switches and core
All 12 switches PASS. ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=0 (positions 3/3, today 0/2, week 0/3)
REGIME risk-on (SPY 755.72 vs SMA200 728.85; 61 consecutive closes above)
CORE SPYM: 12 sh = $1,071.96 (54.2%) | target 55.0% | band +/-5pp
CORE_ACTION=HOLD (in band)
MAINTENANCE=none

### Screen
Screened 68 (0 no data) | ALL 7
Top: ABBV (XLV), PG (XLP, held), PM (XLP), KO (XLP, held), NUE (XLB), JNJ (XLV), XLF
Near misses: PLTR G3; AMZN G3; TJX G3; BAC G3; SCHW G3; XOM G4; CVX G4; EOG G4; SLB G4; CEG G3; VST G3; FCX G3

### Yesterday's candidates (10-30 plan)
- PG: FILLED 1 @ 163.28, stop 440e2534 live.
- KO: FILLED 2 @ 94.525, stop 47621c1f live.
- PM: not filled: G11 spread 5.06% at open; re-check midday G9 no slots/XLP cap. Dropped.

### Candidates
(Screen tables: all G1-G5, G8 PASS for each; see screen.py candidate output 2026-11-02.)
#### Rejected / not used
- PG, KO: G0 FAIL — already held
- PM (XLP): screen OK but XLP sector cap (2 positions) reached; not checked further for G6/G7
- XLF (ETF): screen OK; backup only, not checked further (3 stock candidates from 2 sectors found)

#### 1. ABBV — AbbVie (XLV, rank 2)
G1 PASS $294.89 vs cap $296.82 | G2 PASS ADV20 $1488M | G3 PASS 294.89 > SMA50 269.29 > SMA200 237.10 | G4 PASS R5 +3.2%, close 294.89 vs 295.44 | G5 PASS rank 2, RS63 +20.6% | G8 PASS stop 7.0% (~274.25), target 336.17, qty 1 = $294.89 (14.9%)
G6 PASS — next report 2027-02-03 (estimated) >= 2026-11-10; Q3 reported 2026-10-30 [perplexity: theearningsmadness]
G7 PASS — Q3 beat (adj EPS $3.82, rev $17.4B), FY26 EPS outlook raised, Skyrizi +22.9%, Breakthrough designations, Apogee acquisition closed; XLV rank 2 above SMA50>SMA200. Risk: post-earnings run at 52w high (-1.3%), price near the G1 cap.
News feed: (none)
CANDIDATE: ABBV ref=294.89 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 2. NUE — Nucor (XLB, rank 4)
G1 PASS $273.87 vs cap $296.82 | G2 PASS ADV20 $338M | G3 PASS 273.87 > SMA50 253.79 > SMA200 223.99 | G4 PASS R5 +6.1%, close 273.87 vs 276.06 | G5 PASS rank 4, RS63 +5.1% | G8 PASS stop 7.0% (~254.70), target 312.21, qty 1 = $273.87 (13.8%)
G6 PASS — next report 2027-01-26 (estimated) >= 2026-11-10; Q3 reported 2026-10-26 [perplexity: fiscal.ai]
G7 PASS — Q3 EPS $5.80, record shipments, ASP +18.7% y/y, Q4 guided in line/above Q3, backlog extended into 2028, PT raises (Barclays $320). Risk: commissioning costs/startup margin headwind into 2027; prior spread issues at open (5.09% on 10-30).
News feed: (none)
CANDIDATE: NUE ref=273.87 stop_pct=7.0 sector=XLB g6=PASS g7=PASS

#### 3. JNJ — Johnson & Johnson (XLV, rank 2)
G1 PASS $273.20 vs cap $296.82 | G2 PASS ADV20 $1990M | G3 PASS 273.20 > SMA50 265.60 > SMA200 246.99 | G4 PASS R5 +3.6%, close 273.20 vs 276.27 | G5 PASS rank 2, RS63 +7.6% | G8 PASS stop 7.0% (~254.08), target 311.45, qty 1 = $273.20 (13.8%)
G6 PASS — next report 2027-01-26 (estimated) >= 2026-11-10; last report <45d [perplexity: barrons]
G7 PASS — Q3 rev $25.4B, 2026 guidance raised, oncology data (amivantamab SC, Erleada PROTEUS), new 12-month high; XLV rank 2 above SMA50>SMA200. Risk: near highs after a run; sector concentration with ABBV (XLV cap 2).
News feed: (none)
CANDIDATE: JNJ ref=273.20 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

### Decision
EVENT_TODAY=none, but SAT_SLOTS=0 (3/3 positions: XLE, KO, PG): no new satellite entries unless a slot frees (stop-out). Pipeline minimum met: 3 candidates, 2 sectors (XLV, XLB). Core HOLD (in band), no core order. Next: NFP 2026-11-06 blocks entries.

Health: run 07:30 ET | preflight=0 | mode=PAPER | ks=0 failing | notify=ok | perplexity=ok

## 2026-11-03 — Pre-market Research

### Preflight
NOW_ET=2026-11-03 07:10 | EVENT_TODAY=none | PAUSED=no | MISSING_COMMITS=none | PREFLIGHT_EXIT=0 | EARNINGS_OK_FROM=2026-11-11

### Regime and sectors
REGIME risk-on | SPY 752.10 vs SMA200 729.15 (+3.1%) | 61 consecutive closes above
Top sectors (bars through 2026-11-02): 1 XLV (+14.87) | 2 XLE (+13.37) | 3 XLP (+11.98) | 4 XLB (+8.91) | 5 XLU (+6.71) | 6 XLY (+6.02) | 7 XLF (+5.91)

### Kill switches and core
All 12 switches PASS. ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=0 (positions 3/3, today 0/2, week 0/3)
REGIME risk-on (SPY 752.10 vs SMA200 729.15; 61 consecutive closes above)
CORE SPYM: 12 sh = $1,060.30 (53.9%) | target 55.0% | band +/-5pp
CORE_ACTION=HOLD (in band)
MAINTENANCE=none

### Screen
Screened 68 (0 no data) | ALL 11
Top: COP (XLE), CVX (XLE), ABBV (XLV), XOM (XLE), XLE (held), PM (XLP), PG (held), EOG (XLE), NUE (XLB), JNJ (XLV)
Near misses: PLTR G3; AMZN G3; TJX G3; BAC G3; SCHW G3; SLB G3; KO G4; CEG G3; VST G3; FCX G3; NEM G3; AMT G3

### Candidates
(screen.py candidate tables 2026-11-03: G1-G5, G8 PASS for COP, ABBV, NUE, JNJ, PM.)
#### Rejected / not used
- COP (XLE): G6 FAIL — earnings 2026-11-05 confirmed < EARNINGS_OK_FROM 2026-11-11 [simplywall.st / alphastreet]
- CVX, XOM, EOG (XLE): not checked — XLE already held; COP covered the sector and failed G6
- PM (XLP): screen OK; XLP holds 2 (KO, PG) = sector cap; not checked further
- PG, XLE: G0 FAIL — held

#### 1. ABBV — AbbVie (XLV, rank 1)
G1 PASS $288.84 vs cap $294.87 | G2 PASS ADV20 $1516M | G3 PASS 288.84 > 269.77 > 237.46 | G4 PASS R5 +0.7%, close 288.84 vs 296.45 | G5 PASS rank 1, RS63 +21.0% | G8 PASS stop 7.0% (~268.62), target 329.28, qty 1 = $288.84 (14.7%)
G6 PASS — next report 2027-02-03 (estimated) >= 2026-11-11; Q3 reported 2026-10-30 [perplexity: theearningsmadness]
G7 PASS — Q3 beat (adj EPS $3.82, rev $17.4B), FY26 EPS outlook raised to $13.95–13.99, Skyrizi/Rinvoq growth, etentamig BLA accepted (10-29), Barclays PT $325 (11-02). XLV rank 1, trend intact. Risk: near 52w high and near the G1 price cap.
News feed: (none)
CANDIDATE: ABBV ref=288.84 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 2. NUE — Nucor (XLB, rank 4)
G1 PASS $277.65 vs cap $294.87 | G2 PASS ADV20 $343M | G3 PASS 277.65 > 254.47 > 224.51 | G4 PASS R5 +7.9%, close 277.65 vs 278.86 | G5 PASS rank 4, RS63 +3.8% (rank <=7) | G8 PASS stop 7.0% (~258.21), target 316.52, qty 1 = $277.65 (14.1%)
G6 PASS — next report 2027-01-25 (estimated) >= 2026-11-11; Q3 reported 2026-10-27 [perplexity: zacks]
G7 PASS — Strongest quarter in 3+ yrs (EPS $5.80, record shipments), Q4 guided flat to higher, towers/structures backlog into 2028, new mills shipping, PT raises (Barclays $320, BofA $300). Risk: startup costs ($124M) and close to G4 chase limit (close 277.65 vs 278.86).
News feed: 11-02 14:01 ET bull — Nucor Secures Automotive Steel Contract with General Motors (conf 0.55).
CANDIDATE: NUE ref=277.65 stop_pct=7.0 sector=XLB g6=PASS g7=PASS

#### 3. JNJ — Johnson & Johnson (XLV, rank 1)
G1 PASS $270.56 vs cap $294.87 | G2 PASS ADV20 $1975M | G3 PASS 270.56 > 265.61 > 247.24 | G4 PASS R5 +1.6%, close 270.56 vs 275.32 | G5 PASS rank 1, RS63 +8.6% | G8 PASS stop 7.0% (~251.62), target 308.44, qty 1 = $270.56 (13.8%)
G6 PASS — next report 2027-01-26 (estimated) >= 2026-11-11; last report 2026-10-27 (<45d) [perplexity: barrons]
G7 PASS — Q3 beat, FY26 guidance reaffirmed; oncology (amivantamab SC, Erleada), icotrokinra Ph2b UC hit (11-02), MedTech data; 12-month high; Enterprise Business Review 2026-12-08. Risk: XLV concentration with ABBV (sector cap 2), Stelara erosion.
News feed: (none)
CANDIDATE: JNJ ref=270.56 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

### Decision
EVENT_TODAY=none, but SAT_SLOTS=0 (3/3: XLE, KO, PG): no new satellite entries unless a slot frees (stop-out). Pipeline minimum met: 3 candidates, 2 sectors (XLV, XLB). Core HOLD (in band), no core order. NFP 2026-11-06 blocks entries.

Health: run 07:10 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=ok

## 2026-11-04 — Pre-market Research

### Preflight
NOW_ET=2026-11-04 07:13 | EVENT_TODAY=none | PAUSED=no | MISSING_COMMITS=none | PREFLIGHT_EXIT=0 | EARNINGS_OK_FROM=2026-11-12

### Regime and sectors
REGIME risk-on | SPY 754.35 vs SMA200 729.47 (+3.4%) | 61 consecutive closes above
Top sectors (bars through 2026-11-03): 1 XLV (+13.35) | 2 XLE (+13.04) | 3 XLP (+9.33) | 4 XLU (+6.37) | 5 XLB (+5.40) | 6 XLY (+4.90) | 7 XLF (+4.70)

### Kill switches and core
All 12 switches PASS. ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=0 (positions 3/3, today 0/2, week 0/3)
REGIME risk-on (SPY 754.35 vs SMA200 729.47; 61 consecutive closes above)
CORE SPYM: 12 sh = $1,074.48 (54.3%) | target 55.0% | band +/-5pp
CORE_ACTION=HOLD (in band)
MAINTENANCE=none

### Screen
Screened 68 (0 no data) | ALL 11
Top: COP (XLE), CVX (XLE), XOM (XLE), ABBV (XLV), XLE (held), PG (held), PM (XLP), KO (held), XLP, JNJ (XLV)
Near misses: PLTR G3; AMZN G3; EOG G8; SLB G3; SO G3; CEG G3; VST G3; FCX G3; NEM G3

### Candidates
(screen.py candidate tables 2026-11-04: G1-G5, G8 PASS for ABBV, CVX, XOM, JNJ, COP.)
#### Rejected / not used
- COP (XLE): G6 FAIL — earnings 2026-11-05 confirmed (< EARNINGS_OK_FROM 2026-11-12) [simplywall.st / alphastreet, per 11-03 check]
- PG, XLE, KO: G0 FAIL — held. PM, XLP: XLP holds 2 (KO, PG) = sector cap; not checked further.

#### 1. ABBV — AbbVie (XLV, rank 1)
G1 PASS $286.00 vs cap $296.92 | G2 PASS ADV20 $1533M | G3 PASS 286.00 > 270.20 > 237.81 | G4 PASS R5 -0.1%, close 286.00 vs 296.79 | G5 PASS rank 1, RS63 +18.2% | G8 PASS stop 7.0% (~265.98), target 326.04, qty 1 = $286.00 (14.4%)
G6 PASS — next report 2027-02-03 (estimated) >= 2026-11-12; Q3 reported 2026-10-30 [perplexity: theearningsmadness / marketbeat]
G7 PASS — Q3 beat, FY26 EPS guidance raised, Skyrizi/Rinvoq growth, etentamig BLA accepted; XLV rank 1 and trend intact (carried from 11-03 research). Risk: near 52w high and near the G1 price cap.
News feed: (none)
CANDIDATE: ABBV ref=286.00 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 2. CVX — Chevron (XLE, rank 2)
G1 PASS $225.27 vs cap $296.92 | G2 PASS ADV20 $1729M | G3 PASS 225.27 > 214.04 > 193.94 | G4 PASS R5 -1.3%, close 225.27 vs 233.57 | G5 PASS rank 2, RS63 +22.9% | G8 PASS stop 7.0% (~209.50), target 256.81, qty 1 = $225.27 (11.4%)
G6 PASS — next report 2027-01-29 (estimated) >= 2026-11-12; Q3 reported 2026-10-30 [perplexity: theearningsmadness, source updated 2026-11-03]
G7 PASS — Q3 beat (adj EPS $5.28 vs $4.89), downstream earnings $3.58B, net debt -$7.8B, William Blair upgrade to Buy (10-28), Venezuela and Iraq West Qurna-2 growth. Sector XLE rank 2, strong trend. Risk: oil-price sensitivity; Middle East security headlines (execs cancelled ADIPEC travel 11-03).
News feed: 11-03 09:32 ET bull — Iraq Reaches Agreement with Chevron on West Qurna-2 Oilfield (conf 0.55).
CANDIDATE: CVX ref=225.27 stop_pct=7.0 sector=XLE g6=PASS g7=PASS

#### 3. JNJ — Johnson & Johnson (XLV, rank 1)
G1 PASS $266.17 vs cap $296.92 | G2 PASS ADV20 $1990M | G3 PASS 266.17 > 265.47 > 247.48 | G4 PASS R5 -1.0%, close 266.17 vs 275.94 | G5 PASS rank 1, RS63 +5.3% | G8 PASS stop 7.0% (~247.54), target 303.43, qty 1 = $266.17 (13.4%)
G6 PASS — next report 2027-01-26 (estimated) >= 2026-11-12; last report 2026-10-27 (<45d) [perplexity: barrons, updated 2026-11-01]
G7 PASS — Q3 beat, FY26 guidance reaffirmed; oncology and icotrokinra Ph2b UC data (11-02); XLV rank 1 (carried from 11-03). Risk: thin margin over SMA50 (266.17 vs 265.47); XLV concentration with ABBV; Stelara erosion.
News feed: (none)
CANDIDATE: JNJ ref=266.17 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 4. XOM — Exxon Mobil (XLE, rank 2)
G1 PASS $177.46 vs cap $296.92 | G2 PASS ADV20 $2199M | G3 PASS 177.46 > 168.32 > 155.09 | G4 PASS R5 -1.4%, close 177.46 vs 186.34 | G5 PASS rank 2, RS63 +19.0% | G8 PASS stop 7.0% (~165.04), target 202.30, qty 1 = $177.46 (9.0%)
G6 PASS — next report 2027-01-29 (estimated) >= 2026-11-12; Q3 reported 2026-10-30 [perplexity: theearningsmadness, updated 2026-11-04]
G7 PASS — Q3 beat ($15.4B, refining-led), $20B 2027 buyback, dividend +3.9%, Rovuma/Papua LNG stake increases, Kashagan claim dismissed; XLE rank 2. Risk: oil sensitivity; DZ Bank downgrade to Sell (11-04 06:31 ET).
News feed: 11-04 06:31 ET bear — DZ Bank Downgrades Exxon Mobil to Sell (conf 0.52); 11-02 07:31 ET bull — Rovuma/Papua LNG stakes (conf 0.55). Input to G7 only, not a gate.
CANDIDATE: XOM ref=177.46 stop_pct=7.0 sector=XLE g6=PASS g7=PASS

### Yesterday's candidates (11-03)
- ABBV: not filled — G8 qty 0 (budget), G9 no slots 3/3
- NUE: not filled — G8 qty 0, G9 no slots; not in today's top-10
- JNJ: not filled — G8 qty 0, G9 no slots
- COP: dropped — G6 (earnings 11-05)

### Decision
EVENT_TODAY=none. Pipeline minimum met: 4 candidates, 2 sectors (XLV, XLE). SAT_SLOTS=0 (3/3: XLE, KO, PG), so no new entries unless a slot frees; also cash $349.37 vs ~$250 budget after reserve makes qty 0 likely (as on 11-03). Core HOLD (54.3%, in band), no core order. NFP 2026-11-06 blocks entries.

Health: run 07:13 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=ok

## 2026-11-05 — Pre-market Research

### Preflight
NOW_ET=2026-11-05 07:10 | EVENT_TODAY=none | PAUSED=no | MISSING_COMMITS=none | PREFLIGHT_EXIT=0 | EARNINGS_OK_FROM=2026-11-13

### Regime and sectors
REGIME risk-on | SPY 766.81 vs SMA200 729.91 (+5.1%) | 61 consecutive closes above
Top sectors (bars through 2026-11-04): 1 XLV (+15.32) | 2 XLP (+11.11) | 3 XLY (+7.44) | 4 XLF (+6.91) | 5 XLB (+6.75) | 6 XLRE (+6.14) | 7 XLE (+5.33)

### Kill switches and core
All 12 switches PASS. ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=0 (positions 3/3, today 0/2, week 1/3)
REGIME risk-on (SPY 766.81 vs SMA200 729.91; 61 consecutive closes above)
CORE SPYM: 12 sh = $1,085.28 (54.2%) | target 55.0% | band +/-5pp
CORE_ACTION=HOLD (in band)
MAINTENANCE=none

### Screen
Screened 68 (0 no data) | ALL 9
Top: ABBV (held), COP (XLE), PM (XLP), CVX (XLE), KO (held), JNJ (XLV), XOM (XLE), NUE (XLB), AMZN (XLY)
Near misses: PLTR G3; TJX G3; BAC G3; SCHW G3; EOG G3; SLB G3; PG G4; FCX G3; NEM G3; PLD G3; AMT G3; WELL G4

### Candidates
(screen.py candidate tables 2026-11-05: G1-G5, G8 PASS for CVX, JNJ, PM, XOM, NUE.)
#### Rejected / not used
- ABBV, KO: G0 FAIL — held.
- COP (XLE): G6 FAIL — earnings 2026-11-05 confirmed (< EARNINGS_OK_FROM 2026-11-13) [11-03/11-04 check; not re-queried]
- NUE (XLB): screen passes (ref 267.91, stop 7.6%) but G6/G7 not checked — two sectors' worth of candidates already complete; first in line if one drops.

#### 1. JNJ — Johnson & Johnson (XLV, rank 1)
G1 PASS $276.32 vs cap $300.49 | G2 PASS ADV20 $2053M | G3 PASS 276.32 > 265.53 > 247.77 | G4 PASS R5 +1.9%, close 276.32 vs 277.03 | G5 PASS rank 1, RS63 +7.8% | G8 PASS stop 7.0% (~256.98), target 315.00, qty 1 = $276.32 (13.8%)
G6 PASS — next report 2027-01-26 (estimated) >= 2026-11-13 [perplexity: tradytics/barrons, updated 2026-11-01..05]
G7 PASS — XLV rank 1; Q3 beat, FY26 guidance reaffirmed; Tremfya/Rybrevant/Shockwave data flow; Enterprise Business Review 2026-12-08. Risk: close only 0.9% over G4 ceiling (276.32 vs 277.03), Stelara erosion, XLV concentration with held ABBV.
News feed: (none)
CANDIDATE: JNJ ref=276.32 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 2. PM — Philip Morris International (XLP, rank 2)
G1 PASS $211.28 vs cap $300.49 | G2 PASS ADV20 $938M | G3 PASS 211.28 > 195.22 > 182.45 | G4 PASS R5 +4.3%, close 211.28 vs 214.01 | G5 PASS rank 2, RS63 +12.6% | G8 PASS stop 7.0% (~196.49), target 240.86, qty 1 = $211.28 (10.5%)
G6 PASS — next report 2027-02-05 (estimated) >= 2026-11-13 [perplexity: tradytics, updated 2026-11-05]
G7 PASS — Q3 beat (adj EPS $2.36, organic revenue +7.1%, op income +10.5%), smoke-free/ZYN/IQOS growth, analyst target raises (Jefferies, Stifel); XLP rank 2, 12-month high 10-30. Risk: ZYN price cuts and US investment pressure near-term profit; Baltimore litigation; XLP already holds KO + PG (sector cap 2 — G9 will block at execution unless a staple exits).
News feed: (none)
CANDIDATE: PM ref=211.28 stop_pct=7.0 sector=XLP g6=PASS g7=PASS

#### 3. CVX — Chevron (XLE, rank 7)
G1 PASS $216.96 vs cap $300.49 | G2 PASS ADV20 $1796M | G3 PASS 216.96 > 214.38 > 194.20 | G4 PASS R5 -5.3%, close 216.96 vs 234.91 | G5 PASS rank 7 (max 7), RS63 +14.9% | G8 PASS stop 7.0% (~201.77), target 247.33, qty 1 = $216.96 (10.8%)
G6 PASS — next report 2027-01-29 (estimated) >= 2026-11-13 [perplexity: theearningsmadness, updated 2026-11-04]
G7 PASS — Q3 beat (adj EPS $5.28), refining >$4.9B at ~98% utilisation, Venezuela $7B program, Egypt/Argentina growth; RS63 +14.9%. Risk: oil sensitivity, US–Iran headlines; sector rank 7 is the G5 limit (RS63 override applies).
News feed: 11-03 09:32 ET bull — Iraq Reaches Agreement with Chevron on West Qurna-2 (conf 0.55).
CANDIDATE: CVX ref=216.96 stop_pct=7.0 sector=XLE g6=PASS g7=PASS

#### 4. XOM — Exxon Mobil (XLE, rank 7)
G1 PASS $169.27 vs cap $300.49 | G2 PASS ADV20 $2338M | G3 PASS 169.27 > 168.49 > 155.28 | G4 PASS R5 -7.0%, close 169.27 vs 187.31 | G5 PASS rank 7 (max 7), RS63 +9.5% | G8 PASS stop 7.0% (~157.42), target 192.97, qty 1 = $169.27 (8.4%)
G6 PASS — next report 2027-01-29 (estimated) >= 2026-11-13 [perplexity: theearningsmadness, updated 2026-11-04]
G7 PASS — Q3 beat ($15.4B), $20B 2027 buyback, Rovuma/Papua LNG stake increases, Evercore target $200; RS63 +9.5%. Risk: DZ Bank downgrade to Sell (11-04 06:31 ET); oil sensitivity; thin margin over SMA50 (169.27 vs 168.49).
News feed: 11-04 06:31 ET bear — DZ Bank downgrades Exxon to Sell (conf 0.52). Input to G7 only, not a gate.
CANDIDATE: XOM ref=169.27 stop_pct=7.0 sector=XLE g6=PASS g7=PASS

### Yesterday's candidates (11-04)
- ABBV: FILLED — 1 @ 284.78, stop a306f4a4 (new, 7%)
- CVX: not filled — G8 qty 0 (budget), G9 no slots 3/3
- JNJ: not filled — G8 qty 0, G9 no slots 3/3
- XOM: not filled — G8 qty 0, G9 no slots; G11 spread 1.59% at open

### Decision
EVENT_TODAY=none (NFP is 2026-11-06, not today). Pipeline minimum met: 4 candidates, 3 sectors (XLV, XLP, XLE). SAT_SLOTS=0 (3/3: ABBV, KO, PG), cash $258.58 vs reserve — no new entries unless a slot frees; XLP is also at the 2-position sector cap, so PM cannot be bought regardless. Core HOLD (54.2%, in band), no core order.

Health: run 07:10 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=ok

## 2026-11-06 — Pre-market Research

### Preflight
NOW_ET=2026-11-06 07:11 | EVENT_TODAY=NFP | PAUSED=no | MISSING_COMMITS=none | PREFLIGHT_EXIT=0 | EARNINGS_OK_FROM=2026-11-16

### Regime and sectors
REGIME risk-on | SPY 733.00 vs SMA200 730.15 (+0.4%) | 61 consecutive closes above | flip needs 3 consecutive closes on the other side
Top sectors (bars through 2026-11-05): 1 XLV (+16.02) | 2 XLP (+14.89) | 3 XLRE (+9.29) | 4 XLF (+8.85) | 5 XLB (+8.37) | 6 XLU (+7.70) | 7 XLE (+7.67)

### Kill switches and core
All 12 switches PASS. ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=0 (positions 3/3, today 0/2, week 1/3)
REGIME risk-on (SPY 733.00 vs SMA200 730.15; 61 consecutive closes above)
CORE SPYM: 12 sh = $1,038.81 (53.8%) | target 55.0% | band +/-5pp
CORE_ACTION=HOLD (in band)
MAINTENANCE=none

### Screen
Screened 68 (0 no data) | ALL 8
Top: ABBV (held), XLV, KO (held), WELL (XLRE), NEM (XLB), PM (XLP), JNJ (XLV), XLF
Near misses: AMZN G5; BAC G3; SCHW G3; XOM G3; CVX G3; COP G3; EOG G3; SLB G3; PG G4; SO G3; CEG G3; VST G3

### Candidates (screen.py candidate tables 2026-11-06: G1-G5, G8 PASS for WELL, NEM, PM, JNJ, XLF)
#### Rejected / not used
- ABBV, KO: G0 FAIL — held.
- XLV, XLF: screen passes (XLF ref 57.50) but G6/G7 not checked — four candidates already complete.
- CVX, XOM, COP (XLE): dropped — G3 FAIL today (close fell below SMA50).

#### 1. WELL — Welltower (XLRE, rank 3)
G1 PASS $245.43 vs cap $289.85 | G2 PASS ADV20 $719M | G3 PASS 245.43 > 233.68 > 219.58 | G4 PASS R5 +5.3%, close 245.43 vs 248.49 | G5 PASS rank 3, RS63 +8.8% | G8 PASS stop 7.0% (~228.25), target 279.79, qty 1 = $245.43 (12.7%)
G6 PASS — next report 2027-02-08 (estimated) >= 2026-11-16 [perplexity: morningstar]
G7 PASS — XLRE rank 3; Q3 same-store NOI +15.8%, FFO guidance midpoint raised $0.10 to $6.50 (11-05), Evercore PT 265. Risk: close only 1.2% under G4 ceiling; rate sensitivity.
News feed: (none)
CANDIDATE: WELL ref=245.43 stop_pct=7.0 sector=XLRE g6=PASS g7=PASS

#### 2. NEM — Newmont (XLB, rank 5)
G1 PASS $119.71 | G2 PASS ADV20 $760M | G3 PASS 119.71 > 119.12 > 112.38 | G4 PASS R5 +7.1%, close 119.71 vs 123.41 | G5 PASS rank 5, RS63 +11.2% | G8 PASS stop 7.8% (~110.37), target 138.40, qty 2 = $239.42 (12.4%)
G6 PASS — next report 2027-01-27 (estimated); last report 2026-10-22 (<45 days) [perplexity: simplywall.st/yahoo]
G7 PASS — XLB rank 5, realised gold prices >20% y/y, 2026 production guidance maintained (5.26Moz), Q4 higher-grade ramp-ups. Risk: thin margin over SMA50 (0.5%), gold-price sensitivity, Lihir drought.
News feed: (none)
CANDIDATE: NEM ref=119.71 stop_pct=7.8 sector=XLB g6=PASS g7=PASS

#### 3. JNJ — Johnson & Johnson (XLV, rank 1)
G1 PASS $272.32 | G2 PASS ADV20 $2103M | G3 PASS 272.32 > 265.58 > 248.04 | G4 PASS R5 -1.0%, close 272.32 vs 278.68 | G5 PASS rank 1, RS63 +10.3% | G8 PASS stop 7.0% (~253.26), target 310.44, qty 1 = $272.32 (14.1%)
G6 PASS — next report 2027-01-26 (estimated) [perplexity: tradytics/barrons]
G7 PASS — XLV rank 1; Q3 revenue ~+6%, FY guidance raised despite ~$7B talc/deal charge; Tremfya/Darzalex/Rybrevant growth, PROTEUS Erleada data. Risk: talc settlement, Stelara erosion, XLV overlap with held ABBV.
News feed: 11-05 17:36 ET bull — FDA Grants Accelerated Approval To Rybrevant Faspro (conf 0.60).
CANDIDATE: JNJ ref=272.32 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 4. PM — Philip Morris International (XLP, rank 2)
G1 PASS $201.50 | G2 PASS ADV20 $973M | G3 PASS 201.50 > 195.37 > 182.62 | G4 PASS R5 -3.4%, close 201.50 vs 214.69 | G5 PASS rank 2, RS63 +11.5% | G8 PASS stop 7.0% (~187.39), target 229.71, qty 1 = $201.50 (10.4%)
G6 PASS — next report 2027-02-05 (estimated) [perplexity: tradytics]
G7 PASS — XLP rank 2; Q3 beat (organic rev +7.1%, op income +10.5%), dividend +8.8%, IQOS/ZYN growth, Stifel Buy. Risk: ZYN 20-pouch pricing margin pressure; XLP already holds KO + PG (sector cap 2 blocks at execution).
News feed: (none)
CANDIDATE: PM ref=201.50 stop_pct=7.0 sector=XLP g6=PASS g7=PASS

### Yesterday's candidates (11-05)
- JNJ: not filled — G8 qty 0, G9 no slots 3/3, G11 spread 4.40%
- PM: not filled — G8 qty 0, G9 no slots / XLP cap, G11 spread 6.19%
- CVX: not filled — G8 qty 0, G9 no slots 3/3
- XOM: not filled — G8 qty 0, G9 no slots 3/3

### Decision
EVENT_TODAY=NFP: market-open will not open new satellites today (G10); candidates recorded for the next session. Pipeline minimum met: 4 candidates, 4 sectors (XLRE, XLB, XLV, XLP). SAT_SLOTS=0 (3/3) so no entries possible even without the block. Core HOLD (53.8%, in band), no core order.

Health: run 07:12 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=ok

## 2026-11-09 — Pre-market Research

### Preflight
NOW_ET=2026-11-09 07:13 | EVENT_TODAY=none | PAUSED=no | MISSING_COMMITS=none | PREFLIGHT_EXIT=0 | EARNINGS_OK_FROM=2026-11-17

### Regime and sectors
REGIME risk-on | SPY 735.29 vs SMA200 730.38 (+0.7%) | 61 consecutive closes above | flip needs 3 consecutive closes on the other side
Top sectors (bars through 2026-11-06): 1 XLV (+14.74) | 2 XLP (+11.95) | 3 XLRE (+8.34) | 4 XLU (+7.45) | 5 XLF (+7.08) | 6 XLY (+6.69) | 7 XLB (+6.50)

### Kill switches and core
All 12 switches PASS. ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=1 (positions 2/3, today 0/2, week 0/3)
REGIME risk-on (SPY 735.29 vs SMA200 730.38; 61 consecutive closes above)
CORE SPYM: 12 sh = $1,045.32 (53.8%) | target 56.6% | band +/-5pp
CORE_ACTION=HOLD (in band)
MAINTENANCE=none

### Screen
Screened 68 (0 no data) | ALL 11
Top: ABBV (XLV), PG (held), XLV, KO (held), XLP, JNJ, WELL, PM, NEM, XLF
Near misses: TJX G3; BAC G3; SCHW G3; UNP G5; XOM G3; CVX G3; COP G3; WMT G3; SO G3; CEG G3; VST G3; FCX G3

### Candidates (screen.py candidate tables 2026-11-09: G1-G5, G8 PASS for ABBV, JNJ, WELL, NEM, XLF)
#### Rejected / not used
- PG, KO: G0 FAIL — held. PM, XLP: XLP already has 2 positions (sector cap, G9) — not checked.
- XLF: screen passes (ref 57.16) but G6/G7 not checked — four candidates already complete.

#### 1. ABBV — AbbVie (XLV, rank 1)
G1 PASS $291.31 vs cap $291.55 | G2 PASS ADV20 $1626M | G3 PASS 291.31 > 271.95 > 238.94 | G4 PASS R5 -1.2%, close vs 302.40 | G5 PASS rank 1, RS63 +22.4% | G8 PASS stop 7.0% (~270.92), target 332.09, qty 1 = $291.31 (15.0%)
G6 PASS — next report 2027-02-03 (estimated) >= 2026-11-17 [perplexity: utilarium, updated 11-09]
G7 PASS — XLV rank 1; Q3 beat, 2026 revenue guide raised (~$67.8B), lutikizumab Ph3 HS positive (11-06), 5.2% dividend raise, analyst PT hikes. Risk: price $0.24 under G1 cap — a gap up kills sizing; stopped out 11-06 (KS-11 streak 2).
News feed: (none)
CANDIDATE: ABBV ref=291.31 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 2. JNJ — Johnson & Johnson (XLV, rank 1)
G1 PASS $276.22 | G2 PASS ADV20 $2153M | G3 PASS 276.22 > 265.79 > 248.33 | G4 PASS R5 +1.1%, close vs 280.39 | G5 PASS rank 1, RS63 +10.4% | G8 PASS stop 7.0% (~256.88), target 314.89, qty 1 = $276.22 (14.2%)
G6 PASS — next report 2027-01-26 (estimated) [perplexity: tradytics/barrons]
G7 PASS — XLV rank 1; FY26 guidance raised (EPS $11.05-11.15), OTTAVA robot FDA authorization, IMAAVY approval, positive Ph3 data (ICOTYDE, myeloma). Risk: talc litigation, medtech softness; XLV overlap with ABBV.
News feed: 11-09 03:10 ET bull (pasritamig/JNJ-9401 PSA data, conf 0.55); 11-07 21:01 ET bull (ICOTYDE Ph3, conf 0.55).
CANDIDATE: JNJ ref=276.22 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 3. WELL — Welltower (XLRE, rank 3)
G1 PASS $245.01 | G2 PASS ADV20 $718M | G3 PASS 245.01 > 233.79 > 219.90 | G4 PASS R5 +4.4%, close vs 249.50 | G5 PASS rank 3, RS63 +9.1% | G8 PASS stop 7.0% (~227.86), target 279.31, qty 1 = $245.01 (12.6%)
G6 PASS — next report 2027-02-09 (estimated) >= 2026-11-17 [perplexity: globalbankingandfinance]
G7 PASS — XLRE rank 3; Q3 FFO guide midpoint raised $0.10 to $6.50, SHO margin 66%, $7.7B YTD investments. Risk: close only 1.8% under G4 ceiling; rate sensitivity; ex-dividend 11-10 ($0.85).
News feed: (none)
CANDIDATE: WELL ref=245.01 stop_pct=7.0 sector=XLRE g6=PASS g7=PASS

#### 4. NEM — Newmont (XLB, rank 7)
G1 PASS $120.91 | G2 PASS ADV20 $781M | G3 PASS 120.91 > 118.89 > 112.38 | G4 PASS R5 +13.4% (max 15%), close vs 124.00 | G5 PASS rank 7 (edge), RS63 +8.0% | G8 PASS stop 8.1% (~111.13), target 140.48, qty 2 = $241.82 (12.4%)
G6 PASS — next report 2027-02-18 (estimated) [perplexity: globalbankingandfinance, 11-05]
G7 PASS — XLB rank 7; gold >$4,000/oz, Q3 beat, 2026 production guide kept (5.26Moz), Q4 higher-grade ramp. Risk: R5 +13.4% near chase limit, thin margin over SMA50, 2027 unit costs rising, Lihir drought.
News feed: (none)
CANDIDATE: NEM ref=120.91 stop_pct=8.1 sector=XLB g6=PASS g7=PASS

### Yesterday's candidates (11-06 plan, no entries — NFP)
- WELL: not filled — G10 NFP, G11 spread/ask deviation
- NEM: not filled — G10 NFP, G11 spread/ask deviation
- JNJ: not filled — G10 NFP, G11 spread
- PM: not filled — G9 XLP cap, G10 NFP, G11 spread

### Decision
EVENT_TODAY=none: market-open may enter. Pipeline minimum met: 4 candidates, 3 sectors (XLV, XLRE, XLB). SAT_SLOTS=1, so at most one fills; core HOLD (53.8%, in band), no core order. Note: CPI is Tue 11-10 (blocks entries tomorrow), so today is the entry window. Last two sessions showed wide IEX spreads at the open (G11) — market-open should retry via ks.py --check.

Health: run 07:16 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=ok

## 2026-11-10 — Pre-market Research

### Preflight
NOW_ET=2026-11-10 07:11 | EVENT_TODAY=CPI | PAUSED=no | MISSING_COMMITS=none | PREFLIGHT_EXIT=0 | EARNINGS_OK_FROM=2026-11-18

### Regime and sectors
REGIME risk-on | SPY 752.69 vs SMA200 730.70 (+3.0%) | 61 consecutive closes above | flip needs 3 consecutive closes on the other side
Top sectors (bars through 2026-11-09): 1 XLV (+14.00) | 2 XLP (+10.95) | 3 XLY (+7.18) | 4 XLRE (+7.10) | 5 XLB (+6.09) | 6 XLF (+5.96) | 7 XLU (+5.88)

### Kill switches and core
All 12 switches PASS. ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=0 (positions 3/3, today 0/2, week 1/3)
REGIME risk-on (SPY 752.69 vs SMA200 730.70; 61 consecutive closes above)
CORE SPYM: 12 sh = $1,063.84 (53.9%) | target 55.0% | band +/-5pp
CORE_ACTION=HOLD (in band)
MAINTENANCE=none

### Screen
Screened 68 (0 no data) | ALL 8
Top: PG (held), ABBV (XLV), XLV, KO (held), WELL (XLRE), XLP, XLF, AMZN (XLY)
Near misses: TJX G3; BAC G3; SCHW G3; JNJ G4 (held); XOM G3; CVX G3; COP G3; WMT G3; PM G3; SO G3; CEG G3; VST G3

### Candidates (screen.py candidate 2026-11-10: G1-G5, G8 PASS for ABBV, WELL, AMZN, XLF)
#### Rejected / not used
- PG, KO: G0 FAIL — held. XLV: same sector as ABBV/JNJ; not checked (ABBV preferred single stock). XLP: sector at 2-position cap (G9).
- NEM, PM, JNJ: no longer screen passers (not in top-10; JNJ held).

#### 1. ABBV — AbbVie (XLV, rank 1)
G1 PASS $293.30 vs cap $296.00 | G2 PASS ADV20 $1634M | G3 PASS 293.30 > 272.70 > 239.31 | G4 PASS R5 +1.5%, close vs 302.54 | G5 PASS rank 1, RS63 +19.6% | G8 PASS stop 7.0% (~272.77), target 334.36, qty 1 = $293.30 (14.9%)
G6 PASS — next report 2027-02-03 (estimated) >= 2026-11-18 [perplexity: utilarium, updated 11-09]
G7 PASS — XLV rank 1; Q3 beat ($17.4B rev), FY26 EPS guide raised, Nxera IBD licensing deal (11-04), 5.2% dividend raise, Skyrizi/Rinvoq outgrowing Humira decline. Risk: price only $2.70 under G1 cap; stopped out 11-06 (KS-11 streak 2).
News feed: 0 signals (48h).
CANDIDATE: ABBV ref=293.30 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 2. WELL — Welltower (XLRE, rank 4)
G1 PASS $247.35 | G2 PASS ADV20 $736M | G3 PASS 247.35 > 233.98 > 220.22 | G4 PASS R5 +3.5%, close vs 249.95 | G5 PASS rank 4, RS63 +11.8% | G8 PASS stop 7.0% (~230.04), target 281.98, qty 1 = $247.35 (12.5%)
G6 PASS — next report 2027-02-09 (estimated) >= 2026-11-18 [perplexity: benzinga, updated 11-10]
G7 PASS — XLRE rank 4; Q3 normalized FFO +24.6% y/y, FY26 FFO guide midpoint raised $0.10 to $6.50, same-store NOI +15.8%, $4.1B Q3 investments. Risk: close only 1.1% under G4 ceiling; valuation/rate sensitivity.
News feed: 0 signals (48h).
CANDIDATE: WELL ref=247.35 stop_pct=7.0 sector=XLRE g6=PASS g7=PASS

#### 3. AMZN — Amazon (XLY, rank 3)
G1 PASS $266.93 | G2 PASS ADV20 $12640M | G3 PASS 266.93 > 253.96 > 244.08 | G4 PASS R5 +8.7%, close vs 275.76 | G5 PASS rank 3, RS63 +0.4% | G8 PASS stop 7.9% (~245.82), target 309.16, qty 1 = $266.93 (13.5%)
G6 PASS — next report 2027-02-04 (estimated) >= 2026-11-18 [perplexity: tradytics; last report ~10-30, <45d]
G7 PASS — XLY rank 3; AWS +39.3% y/y to ~$46B, 2026 capacity sold out with 2027 largely committed, record 13.9% op margin; JPMorgan Focus List / top AI pick (11-09). Risk: AI capex weighs on FCF; data-center regulation.
News feed: 11-09 15:01 ET bull (JPMorgan top AI pick, conf 0.55).
CANDIDATE: AMZN ref=266.93 stop_pct=7.9 sector=XLY g6=PASS g7=PASS

#### 4. XLF — Financial Select Sector SPDR (XLF, rank 6)
G1 PASS $57.99 | G2 PASS ADV20 $2057M | G3 PASS 57.99 > 55.91 > 53.84 | G4 PASS R5 +0.7%, close vs 58.41 | G5 PASS rank 6, RS63 +2.6% | G8 PASS stop 7.0% (~53.93), target 66.11, qty 5 = $289.95 (14.7%)
G6 PASS — ETF, no earnings event.
G7 PASS — XLF rank 6, uptrend above SMA50/200 and +6.0% R21; trend-leadership driver. Risk: weakest RS63 (+2.6%) of the list; rate/credit sensitivity.
CANDIDATE: XLF ref=57.99 stop_pct=7.0 sector=XLF g6=PASS g7=PASS

### Yesterday's candidates (11-09 plan)
- JNJ: FILLED 1 @ 277.04, stop e322b867 (new)
- ABBV: not filled — G11 spread 4.74%
- WELL: not filled — G8 qty 0 / G9 no slots after JNJ
- NEM: not filled — G9 sats cap, G11 spread 4.97%; dropped from today's screen (no longer passes)

### Decision
EVENT_TODAY=CPI: market-open will NOT open new satellites today (G10). SAT_SLOTS=0 anyway (3/3 positions: JNJ, KO, PG). Core HOLD (53.9%, in band) — no order. Pipeline minimum met: 4 candidates, 4 sectors, ready for the next free slot/non-event day. Cash $262.94 (13.3%) idle; same band/cash issue as the 11-06 lesson.

Health: run 07:25 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=ok

## 2026-11-11 — Pre-market Research

### Preflight
NOW_ET=2026-11-11 07:11 | EVENT_TODAY=none | PAUSED=no | MISSING_COMMITS=none | PREFLIGHT_EXIT=0 | EARNINGS_OK_FROM=2026-11-19

### Regime and sectors
REGIME risk-on | SPY 749.92 vs SMA200 730.99 (+2.6%) | 61 consecutive closes above | flip needs 3 consecutive closes on the other side
Top sectors (bars through 2026-11-10): 1 XLV (+14.25) | 2 XLP (+10.69) | 3 XLY (+8.52) | 4 XLB (+6.98) | 5 XLRE (+6.55) | 6 XLF (+6.53) | 7 XLU (+5.67)

### Kill switches and core
All 12 switches PASS. ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=0 (positions 3/3, today 0/2, week 1/3)
REGIME risk-on (SPY 749.92 vs SMA200 730.99; 61 consecutive closes above)
CORE SPYM: 12 sh = $1,068.26 (54.3%) | target 55.0% | band +/-5pp
CORE_ACTION=HOLD (in band)
MAINTENANCE=none

### Screen
Screened 68 (0 no data) | ALL 12
Top-10: PG (held), ABBV (XLV), XLV, KO (held), AMT (XLRE), WELL (XLRE), XLP, JNJ (held), XLF, AMZN (XLY)
Near misses: TJX G3; BAC G3; SCHW G3; XOM G3; CVX G3; COP G3; EOG G8; WMT G3; PM G3; NEE G3; SO G3; CEG G3

### Candidates (screen.py candidate 2026-11-11: G1-G5, G8 PASS for ABBV, WELL, AMT, AMZN, XLF)
#### Rejected / not used
- PG, KO, JNJ: G0 FAIL — held. XLV: same sector as ABBV/JNJ, ABBV preferred. XLP: sector at 2-position cap (G9).

#### 1. ABBV — AbbVie (XLV, rank 1)
G1 PASS $293.89 vs cap $295.19 | G2 PASS ADV20 $1598M | G3 PASS 293.89 > 273.45 > 239.68 | G4 PASS R5 +2.8%, close vs 303.02 | G5 PASS rank 1, RS63 +21.1% | G8 PASS stop 7.0% (~273.32), target 335.03, qty 1 = $293.89 (14.9%)
G6 PASS — next report 2027-02-03 (estimated) >= 2026-11-19 [perplexity: tradytics/utilarium]
G7 PASS — XLV rank 1; Q3 rev +10.3% to $17.4B, FY adj. EPS guide raised, Skyrizi/Rinvoq outgrowing Humira decline, Nxera IBD deal, Breakthrough designations (11-06). Risk: price only $1.30 under G1 cap; stopped out 11-06 (KS-11 streak 2).
News feed: 0 signals (48h).
CANDIDATE: ABBV ref=293.89 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 2. WELL — Welltower (XLRE, rank 5)
G1 PASS $247.66 | G2 PASS ADV20 $739M | G3 PASS 247.66 > 234.20 > 220.54 | G4 PASS R5 +2.7%, close vs 250.84 | G5 PASS rank 5, RS63 +10.5% | G8 PASS stop 7.0% (~230.32), target 282.33, qty 1 = $247.66 (12.6%)
G6 PASS — next report 2027-02-09 (estimated) >= 2026-11-19 [perplexity: benzinga]
G7 PASS — XLRE rank 5; Q3 FFO beat, FY26 normalized FFO guide midpoint raised $0.10 to $6.50, SHOP flow-through 66%, JPM PT to $273 (11-10). Risk: close 1.3% under G4 ceiling; rate sensitivity.
News feed: 11-10 12:02 ET bull (JPM maintains Overweight, PT $273, conf 0.55).
CANDIDATE: WELL ref=247.66 stop_pct=7.0 sector=XLRE g6=PASS g7=PASS

#### 3. AMZN — Amazon (XLY, rank 3)
G1 PASS $270.87 | G2 PASS ADV20 $12841M | G3 PASS 270.87 > 254.18 > 244.24 | G4 PASS R5 +8.0%, close vs 276.62 | G5 PASS rank 3, RS63 +4.3% (rank <=7) | G8 PASS stop 7.9% (~249.52), target 313.57, qty 1 = $270.87 (13.8%)
G6 PASS — next report 2027-02-04 (estimated); last report ~10-30 (<45d) [perplexity: tradytics]
G7 PASS — XLY rank 3; AWS +39% y/y with large backlog, JPM Focus List / top AI pick (11-09). Risk: AI capex weighs on FCF; recent EPS/rev slight miss; close 2.0% under G4 ceiling.
News feed: 11-09 15:01 ET bull (JPM top AI pick); 11-10 06:38 bull (Anthropic IPO filing, follow-up), conf 0.55.
CANDIDATE: AMZN ref=270.87 stop_pct=7.9 sector=XLY g6=PASS g7=PASS

#### 4. XLF — Financial Select Sector SPDR (XLF, rank 6)
G1 PASS $58.29 | G2 PASS ADV20 $2022M | G3 PASS 58.29 > 55.92 > 53.87 | G4 PASS R5 +1.9%, close vs 58.59 | G5 PASS rank 6, RS63 +3.6% | G8 PASS stop 7.0% (~54.21), target 66.45, qty 5 = $291.45 (14.8%)
G6 PASS — ETF, no earnings event.
G7 PASS — XLF rank 6, above SMA50/200, R21 +5.9%; trend-leadership driver. Risk: weakest RS63 (+3.6%) of the list; close only 0.3 under G4 ceiling.
CANDIDATE: XLF ref=58.29 stop_pct=7.0 sector=XLF g6=PASS g7=PASS

#### 5. AMT — American Tower (XLRE, rank 5)
G1-G5, G8 PASS (qty 1 = $190.37, 9.7%; stop 7.0%). G6 PASS — next report 2027-02-23 (estimated) [perplexity: globalbankingandfinance]. G7 PASS — XLRE rank 5, RS63 +14.6%, Argus Buy, $2B buyback; Risk: $1.5B notes at high coupon, SMA50 only 0.4% above SMA200. Same sector as WELL (cap 2).
CANDIDATE: AMT ref=190.37 stop_pct=7.0 sector=XLRE g6=PASS g7=PASS

### Yesterday's candidates (11-10 plan)
- ABBV: not filled — G10 CPI block, G8 qty 0 / no slots 3/3
- WELL: not filled — G10 CPI, no slots, G11 spread 5.32%
- AMZN: not filled — G10 CPI, no slots
- XLF: not filled — G10 CPI, no slots; sats 38.6% > 35%

### Decision
EVENT_TODAY=none, but SAT_SLOTS=0 (3/3 positions: JNJ, KO, PG; satellites 32.4%) — no new satellite can be bought unless a stop fires and frees a slot. Core HOLD (54.3%, in band). Pipeline minimum met: 5 candidates, 4 sectors (XLV, XLRE, XLY, XLF), ready for the first free slot. Cash $262.94 (13.4%) idle; same band/cash issue as the 11-06 lesson.

Health: run 07:25 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=ok

## 2026-11-12 — Pre-market Research

### Preflight
NOW_ET=2026-11-12 07:11 | EVENT_TODAY=none | PAUSED=no | MISSING_COMMITS=none | PREFLIGHT_EXIT=0 | EARNINGS_OK_FROM=2026-11-20

### Regime and sectors
REGIME risk-on | SPY 759.81 vs SMA200 731.31 (+3.9%) | 61 consecutive closes above | flip needs 3 consecutive closes on the other side
Top sectors (bars through 2026-11-11): 1 XLV (+14.12) | 2 XLP (+9.81) | 3 XLY (+7.24) | 4 XLB (+6.33) | 5 XLF (+6.12) | 6 XLRE (+5.04) | 7 XLU (+4.41)

### Kill switches and core
All 12 switches PASS. ORDERS_ALLOWED=yes | BUYS_ALLOWED=yes | SAT_ENTRIES_ALLOWED=yes | SAT_SLOTS=0 (positions 3/3, today 0/2, week 1/3)
REGIME risk-on (SPY 759.81 vs SMA200 731.31; 61 consecutive closes above)
CORE SPYM: 12 sh = $1,068.96 (54.0%) | target 55.0% | band +/-5pp
CORE_ACTION=HOLD (in band)
MAINTENANCE=none

### Screen
Screened 68 (0 no data) | ALL 13
Top-10: ABBV (XLV), PG (held), XLV, KO (held), JNJ (held), AMT (XLRE), XLP, COP (XLE), WELL (XLRE), XLF
Near misses: ANET G5; TJX G3; BAC G3; SCHW G3; XOM G3; CVX G3; EOG G8; WMT G3; NEE G3; SO G3; CEG G3; VST G3

### Candidates (screen.py candidate 2026-11-12: G1-G5, G8 PASS for ABBV, AMT, COP, XLF, WELL)
#### Rejected / not used
- PG, KO, JNJ: G0 FAIL — held. XLV: same sector as ABBV/JNJ, ABBV preferred. XLP: sector at 2-position cap (G9). AMT: same sector as WELL, WELL ranks higher on score; AMT passes G1-G5/G8 (qty 1 = $190.24, 9.6%) but G6/G7 not run today.

#### 1. ABBV — AbbVie (XLV, rank 1)
G1 PASS $294.98 vs cap $296.88 | G2 PASS ADV20 $1566M | G3 PASS 294.98 > 274.15 > 240.04 | G4 PASS R5 +0.1%, close vs 303.30 | G5 PASS rank 1, RS63 +19.9% | G8 PASS stop 7.0% (~274.33), target 336.28, qty 1 = $294.98 (14.9%)
G6 PASS — next report 2027-02-03 (estimated) >= 2026-11-20 [perplexity: pretickt, utilarium]
G7 PASS — XLV rank 1; Q3 beat with raised FY adj. EPS guide, lutikizumab Ph3 HS met primary endpoint (11-06/08), etentamig BLA submitted (11-09/10), QULIPTA Ph3 data. Risk: price only $1.90 under G1 cap; Humira decline; stopped out 11-06 (KS-11 streak 2).
News feed: 0 signals (48h).
CANDIDATE: ABBV ref=294.98 stop_pct=7.0 sector=XLV g6=PASS g7=PASS

#### 2. WELL — Welltower (XLRE, rank 6)
G1 PASS $247.35 | G2 PASS ADV20 $734M | G3 PASS 247.35 > 234.34 > 220.86 | G4 PASS R5 -0.3%, close vs 251.57 | G5 PASS rank 6, RS63 +7.8% | G8 PASS stop 7.0% (~230.04), target 281.98, qty 1 = $247.35 (12.5%)
G6 PASS — next report 2027-02-09 (estimated) >= 2026-11-20 [perplexity: pretickt]
G7 PASS — XLRE rank 6; Q3 results 11-09 with FY26 EPS guide raised to $3.31-3.37 (from $3.11-3.19), PT raises JPM $273 / RBC $266 / UBS $289 (11-10/11). Risk: rate sensitivity; RayJay and Cantor trimmed PTs 11-11.
News feed: 11-10 12:02 ET bull (JPM Overweight, PT $273, conf 0.55).
CANDIDATE: WELL ref=247.35 stop_pct=7.0 sector=XLRE g6=PASS g7=PASS

#### 3. COP — ConocoPhillips (XLE, rank 8)
G1 PASS $137.86 | G2 PASS ADV20 $1038M | G3 PASS 137.86 > 137.10 > 122.93 | G4 PASS R5 +0.7%, close vs 153.22 | G5 PASS rank 8 fails, RS63 +13.0% override | G8 PASS stop 7.0% (~128.21), target 157.16, qty 2 = $275.72 (13.9%)
G6 PASS — next report 2027-02-04 (estimated); last report 11-05 (<45d) [perplexity: tickstock]
G7 PASS — RS63 +13.0% vs SPY, Q3 EPS beat ($3.27, +$0.22 vs consensus), dividend +11% to $0.93, 45% of CFO returned, Willow/LNG ramp. Risk: SMA50 only 0.6% below close (thin G3 margin); Q3 production -4%; Bernstein downgrade to Market Perform (11-11 06:31 ET, bear, conf 0.55) and Freedom Broker to Hold; XLE stopped out 11-04 (sector lagging).
CANDIDATE: COP ref=137.86 stop_pct=7.0 sector=XLE g6=PASS g7=PASS

#### 4. XLF — Financial Select Sector SPDR (XLF, rank 5)
G1 PASS $58.63 | G2 PASS ADV20 $1976M | G3 PASS 58.63 > 55.95 > 53.90 | G4 PASS R5 -1.0%, close vs 58.76 | G5 PASS rank 5, RS63 +3.0% | G8 PASS stop 7.0% (~54.53), target 66.84, qty 5 = $293.15 (14.8%)
G6 PASS — ETF, no earnings event.
G7 PASS — XLF rank 5, above SMA50/200, R21 +7.0%; trend-leadership driver. Risk: weakest RS63 (+3.0%); close 0.13 under G4 ceiling.
CANDIDATE: XLF ref=58.63 stop_pct=7.0 sector=XLF g6=PASS g7=PASS

### Yesterday's candidates (11-11 plan)
- ABBV: not filled — G1 FAIL (ask 306.81 > cap), G8 qty 0, G9 no slots 3/3, G11 spread 10.67%
- WELL: not filled — G8 qty 0, G9 no slots
- AMZN: not filled — G8 qty 0, G9 no slots
- XLF: not filled — G8 qty 2 (5.9% < 8%), G9 no slots, sats 38.3% > 35%
- AMT: not filled — G8 qty 0, G9 no slots, G11 spread 4.99%

### Decision
EVENT_TODAY=none, but SAT_SLOTS=0 (3/3 positions: JNJ, KO, PG; satellites 32.7%) — no new satellite can be bought unless a stop fires and frees a slot. Core HOLD (54.0%, in band). Pipeline minimum met: 4 candidates, 4 sectors (XLV, XLRE, XLE, XLF). Cash $262.94 (13.3%) idle; same band/cash issue as the 11-06 lesson (suggest core_band/top-up rule in Friday review).

Health: run 07:25 ET | preflight=0 | mode=PAPER | ks=0 | notify=ok | perplexity=ok
