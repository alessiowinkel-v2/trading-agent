# Weekly Review

Written every Friday evening by the weekly routine. Numbers come from `python3 scripts/ks.py --week` and `bash scripts/watchdog.sh grid <monday>`; judgement is the agent's, sign-off is the user's.
Phase 1 reviews: `memory/archive/phase1-2026/WEEKLY-REVIEW.md`.

## Template

```
## Week ending YYYY-MM-DD

### Stats
(paste `python3 scripts/ks.py --week` WEEK STATS table)

### Cadence
(paste `bash scripts/watchdog.sh grid <monday>` — every cell must be OK or SKIPPED)

### Execution
- Planned orders: N | with an outcome line: N | filled: N | stops verified same session: N/N
- Per closed trade: thesis followed? stop honoured? sized per G8? one line each

### Pipeline
- Research days with ≥2 candidates from ≥2 sectors (or every rejection's gate listed): N/5
- Timing blocks cited outside EVENTS.md: N (must be 0)

### News sleeve
(paste the GATE line, counts and tradeable buckets from `bash scripts/memtail.sh memory/NEWS-SCORECARD.md 1`, or "scorer not yet running")

### Grade: <A–F>
Caps applied: none / "PASS candidate with free slots but 0 entries → max C" / "invested < 70% on ≥2 EODs → max C−" / "planned order without outcome → max D"
One honest sentence on why.

### What worked (≤3) / What didn't (≤3)

### Lessons (also appended to LESSONS.md)

### Suggestions for the user (never applied by the agent)
- … (include: EVENTS.md runway if < 8 weeks of dates remain; watchlist changes, max 5/month)

### Graduation checklist (TRADING-STRATEGY.md)
1–11: ✅ / 🟡 / ❌ with one line of evidence each

Reviewed: (the user adds "Reviewed: YYYY-MM-DD" here)
```

---

## Week ending 2026-10-30

### Stats
| Metric | Value |
|---|---|
| Start (start_equity (phase began this week)) | $2,000.00 |
| End | $1,977.30 |
| Week return | -1.13% |
| SPY week | -0.56% |
| Bot vs SPY (week) | -0.58% |
| Phase return / SPY phase | -1.13% / -1.81% |
| Max intraweek DD (daily closes) | -1.13% |
| Max DD since start | -1.29% |
| Entries this week | 3 (cap 3) |
| Closed round trips | 0 (W:0 / L:0) |
| Profit factor | n/a |
| Avg invested at EOD | 58.3% |
| EODs below 70% floor | 1 of 4 |

### Cadence
| Day | pre-market | market-open | midday | eod |
|---|---|---|---|---|
| 2026-10-26 | MISSING | MISSING | MISSING | MISSING |
| 2026-10-27 | OK | SKIPPED | SKIPPED | OK |
| 2026-10-28 | OK | OK | OK | OK |
| 2026-10-29 | OK | OK | OK | OK |
| 2026-10-30 | OK | OK | OK | OK |

10-26 predates the phase start (10-27), but the grid shows MISSING, so the cap applies. 10-27: pre-market ran late (15:37 ET); market-open and midday ran after the close and SKIPPED, so the core was not bought on Day 0.

### Execution
- Planned orders: 7 | with an outcome line: 7 | filled: 6 | stops verified same session: 3/3
- Planned: core BUY 10-28 (filled 17 @ 90.71), core SELL 10-29 (3 @ 90.54), core SELL 10-30 (2 @ 89.26); satellites XLE 10-29, PG 10-30, KO 10-30 (all filled, 7% trailing stops, status `new`). The seventh, the 10-27 core BUY, was not placed (market closed at run time) and is explained in the 10-27 EOD notes.
- Closed trades: none.
- Anomaly: 10-29 midday found 2 unplanned open buys created 07:59 UTC (`test-2026-10-29-dup` SPYM $1, `sat-2026-10-29-WMT-extra` WMT $104.03). Both cancelled, source unknown. Not placed by any routine in the logs.

### Pipeline
- Research days with ≥2 candidates from ≥2 sectors (or every rejection's gate listed): 4/4 (10-27: KO, JNJ, NUE; 10-28: XLE, JNJ, KO; 10-29: XLE, JNJ, KO, NUE; 10-30: only XLP (PG, PM, KO) but every other rejection listed with its gate)
- Timing blocks cited outside EVENTS.md: 0 (10-28 FOMC block was correct)

### News sleeve
**GATE: NOT MET** — only 0.3 of 6 weeks scanned; only 0 of 150 signals scored at d3; scanner uptime 43% < 95%; no bucket passes.
- weeks scanned: 0.3 (need 6) | signals scored at d3: 0 (need 150) | scanner uptime 28d: 43% (need 95%)
- raw headlines 1017 | signals 1017 (bull 139, bear 46, none 761, duplicate 32, unscorable 39) | open 185, scored 0
Tradeable buckets: none

### Grade: C
Caps applied: "cadence cell MISSING → max C" (10-26, pre-phase). Not triggered: invested <70% on only 1 EOD (Day 0), every planned order has an outcome, every satellite has a same-session stop, no PASS candidate went unexecuted (slots filled 3/3).
Every fill got its stop and every run committed from 10-28, but Day 0 was lost to a late run, the cadence grid still shows a MISSING row, and an unexplained pair of orders appeared.

### What worked (≤3) / What didn't (≤3)
Worked:
- 3 satellites entered with verified 7% stops, 0 unprotected; all 12 KS PASS all week.
- Core rebalance sells fired as satellites grew (target 75% → 55%), keeping deployed 82.3%.
- Phase -1.13% vs SPY -1.81% (+0.68pp), but 4 days prove nothing.
Didn't:
- Day 0 (10-27) ran after the close: core unbought, 0% invested, 3 slots idle.
- Unplanned orders on 10-29 of unknown origin.
- 10-30 candidates all XLP; slots now 0/3 with two XLP names and XLE ~10.6%, so concentration is rising.

### Lessons (also appended to LESSONS.md)
- 2026-10-30 — Unplanned orders need a source.

### Suggestions for the user (never applied by the agent)
- Investigate the 10-29 07:59 UTC orders (`test-2026-10-29-dup`, `sat-2026-10-29-WMT-extra`): a manual or test script, or a stale process? Check API keys / other callers.
- Consider ignoring pre-phase days in `watchdog.sh grid` so a MISSING row before the start date does not cap the grade.
- Check why the 10-27 routines ran late (15:37 ET vs 07:07 scheduled).
- Watchlist: no changes proposed. PM and JNJ repeatedly fail G11 on wide spreads (3-5%); consider whether they belong.
- EVENTS.md runway: last date 2027-12-10, well over 8 weeks. No warning.

### Graduation checklist (TRADING-STRATEGY.md)
1. 🟡 4 of 15 trading days with all four routines OK/SKIPPED (10-27..10-30).
2. ✅ Core bought 10-28; rebalance sells filled 10-29 and 10-30.
3. 🟡 3 of ≥4 entries filled, 0 of ≥2 closed; stops verified 3/3.
4. 🟡 3 of 4 EODs ≥70% (75%); needs ≥90%. Day 0 was 0%.
5. ✅ 4/4 research days compliant; every planned order has an outcome line.
6. ✅ Zero timing blocks outside the closed list.
7. 🟡 Max DD -1.29% (≤8%); SPY phase -1.81%; too few days.
8. 🟡 Phase -1.13% vs SPY -1.81% (+0.68pp); too few days.
9. ✅ ks.py output in EOD records; no uncaught breaches so far.
10. ❌ No `Reviewed:` line yet (first review).
11. ❌ STRESS_TEST.md checklist boxes are all unchecked in the repo.

Reviewed: (the user adds "Reviewed: YYYY-MM-DD" here)

---

## Week ending 2026-11-06

### Stats
| Metric | Value |
|---|---|
| Start (close 2026-10-30) | $1,976.56 |
| End | $1,937.40 |
| Week return | -1.98% |
| SPY week | -2.70% |
| Bot vs SPY (week) | +0.72% |
| Phase return / SPY phase | -3.13% / -4.47% |
| Max intraweek DD (daily closes) | -1.98% |
| Max DD since start | -3.29% |
| Entries this week | 1 (cap 3) |
| Closed round trips | 2 (W:0 / L:2) |
| Profit factor | 0.00 |
| Avg invested at EOD | 82.1% |
| EODs below 70% floor | 0 of 5 |

Closed: XLE 3 sh 68.78 -> 64.67 = $-12.32 (-6.0%); ABBV 1 sh 284.78 -> 281.43 = $-3.35 (-1.2%).

### Cadence
| Day | pre-market | market-open | midday | eod |
|---|---|---|---|---|
| 2026-11-02 | OK | OK | OK | OK |
| 2026-11-03 | OK | OK | OK | OK |
| 2026-11-04 | OK | OK | OK | OK |
| 2026-11-05 | OK | OK | OK | OK |
| 2026-11-06 | OK | OK | OK | OK |

Note: 11-02 market-open ran 10:48 ET vs 10:12 schedule (~36 min late); it still committed.

### Execution
- Planned orders: 1 | with an outcome line: 1 | filled: 1 | stops verified same session: 1/1
- Plan: ABBV buy 11-04 (sat-2026-11-04-ABBV, 1 @ 284.78, trailing stop a306f4a4 status `new`). Every other candidate (11-02..11-06) has a skip line with its failing gates; no core orders (HOLD in band all week).
- XLE (11-04, stop fill 64.67 at 09:33 ET): thesis not followed to target, stop honoured, sized per G8 (entered 10-29). Loss -6.0%.
- ABBV (11-06, stop fill 281.43 at 09:34 ET): stop honoured (hwm 302.93 after the 11-05 selloff), sized per G8. Loss -1.2%. KS-11 streak is now 2 (limit <3): one more loser triggers the 5-day pause.
- Both stop-outs hit within 4 minutes of the open; stops worked as designed but opening volatility is where trailing 7% stops fire.

### Pipeline
- Research days with ≥2 candidates from ≥2 sectors (or every rejection's gate listed): 5/5 (11-02 ABBV/NUE/JNJ; 11-03 same; 11-04 ABBV/CVX/JNJ/XOM; 11-05 JNJ/PM/CVX/XOM/NUE; 11-06 WELL/NEM/JNJ/PM)
- Timing blocks cited outside EVENTS.md: 0 (11-06 NFP block correct; "no slots 3/3", XLP cap, G8 qty 0 and G11 spreads are gates, not timing blocks)
- Capital constraint: G8 qty 0 (budget ~$250 vs $270-295 share prices) and 3/3 slots blocked all candidates 11-02, 11-03, 11-05. Only 11-04 had both a free slot and budget; it executed.

### News sleeve
**GATE: NOT MET** — only 1.3 of 6 weeks scanned; scanner uptime 72% < 95%; no bucket passes (n>=40, mean>0, median>0, t>=2.0, both halves>0, bull)
- weeks scanned: 1.3 (need 6) | signals scored at d3: 276 (need 150) | scanner uptime 28d: 72% (need 95%)
- raw headlines 2537 | signals 2537 (bull 291, bear 130, none 1990, duplicate 87, unscorable 39) | open 256, scored 165
Tradeable buckets: none

### Grade: B
Caps applied: none. (Eligible day with a free slot + PASS candidate: 11-04 → entry made. 11-06 had a free slot but NFP blocks entries. Invested ≥70% every EOD, lowest 72.1%. No planned order without outcome; the one satellite fill had a same-session stop. Cadence 5/5 OK.)
Execution fidelity was clean all week; held to B (not A) for the 36-minute-late 11-02 market-open and the 11-04 market-open noting an unexplained position change ("not investigated") instead of resolving it.

### What worked (≤3) / What didn't (≤3)
Worked:
- Every run committed (20/20 cells OK) and every fill had its stop; KS all PASS at close.
- Beat SPY on the week (+0.72pp) and phase (+1.34pp) with lower DD (max DD -3.29%) in a -4.4% SPY day (11-05).
- A freed slot was refilled the same day (ABBV 11-04) with no narrative veto.
Didn't:
- Both closed trades were losers via trailing stops at the open (profit factor 0.00); KS-11 streak at 2.
- Cash reached 27.9% after the ABBV exit; core stayed HOLD (53.7% vs 56.6% target, inside the ±5pp band) so deployed fell to 72.1%, close to the 70% floor.
- Wide IEX spreads (3-10%) failed G11 for JNJ/PM/WELL/NEM at the 10:15 check on 11-02, 11-03, 11-05, 11-06.

### Lessons (also appended to LESSONS.md)
- 2026-11-06 — The core band can leave freed satellite cash idle
- 2026-11-06 — Trailing stops fire in the opening minutes

### Suggestions for the user (never applied by the agent)
- Core band vs "deployed > idle": with a satellite slot empty, CORE_ACTION stays HOLD until the core drifts 5pp below target. 11-06 EOD: invested 72.1% (floor 70%), core 53.7% vs 56.6%. Consider a narrower band (e.g. ±3pp) or topping up the core when a slot is empty and cash > cash_min + ~$200. Data: EOD invested 87.0% → 86.7% → 72.1% across the ABBV exit.
- G8 budget: qty 0 on $270-295 names on 3 of 5 days (budget ~$250). Either lower sat_price_max_pct-limited names or accept that most XLV/XLB candidates are un-buyable at $2,000; consider trimming watchlist names priced >$250 (ABBV, NUE, JNJ) or revisiting sat_min_pct.
- G11 spreads: IEX quotes show 3-10% spreads on liquid large caps (JNJ, PM) at 10:15 ET; this looks like a data artifact (IEX is not NBBO). Consider a G11 check on SIP-based last-trade vs ref, or an alternative spread source.
- KS-11: two consecutive losers; a third triggers a 5-day pause. Nothing to change, but note that the next stop-out pauses entries.
- Watchlist: no changes proposed beyond the price-cap note above (≤5/month).
- EVENTS.md runway: last date 2027-12-10, well over 8 weeks. No warning.
- Still open from last week: source of the 10-29 07:59 UTC unplanned orders.

### Graduation checklist (TRADING-STRATEGY.md)
1. 🟡 Cadence: 9 trading days with all four routines OK/SKIPPED since 10-28 (need ≥15).
2. 🟡 Core bought 10-28 (17 SPYM, not Day 0 - 10-27 ran after the close); later core SELLs 10-29/10-30 filled, but no later core rebalance BUY yet.
3. ✅ 4 satellite entries filled (XLE, PG, KO, ABBV), 2 closed (XLE, ABBV), each with a stop in the same session.
4. 🟡 Invested ≥70% on every EOD this week (min 72.1%); phase-to-date 1 of 9 EODs below floor (10-27/10-28 Day 0) so ≈89%, just under 90%.
5. 🟡 5/5 research days compliant this week; every planned order has an outcome; 10-30 was only one sector but gates listed.
6. ✅ Zero timing blocks outside the closed list (weeks 1 and 2).
7. 🟡 Max DD -3.29% (≤8%) and below SPY's phase drawdown; only 2 weeks of data.
8. 🟡 Phase -3.13% vs SPY -4.47% (+1.34pp); only 2 weeks of data.
9. ✅ ks.py in every EOD record; no breach missed by the scripts (KS-1 -2.75% on 11-05 caught as a close call).
10. ❌ No `Reviewed:` line under either weekly review yet.
11. ❌ STRESS_TEST.md not present in the repo; Day-1 mechanics test cannot be evidenced.

Reviewed: (the user adds "Reviewed: YYYY-MM-DD" here)

---

## Week ending 2026-11-13

### Stats
| Metric | Value |
|---|---|
| Start (close 2026-11-06) | $1,935.45 |
| End | $1,977.42 |
| Week return | +2.17% |
| SPY week | +2.59% |
| Bot vs SPY (week) | -0.43% |
| Phase return / SPY phase | -1.13% / -1.99% |
| Max intraweek DD (daily closes) | +0.00% |
| Max DD since start | -3.38% |
| Entries this week | 1 (cap 3) |
| Closed round trips | 0 (W:0 / L:0) |
| Profit factor | n/a |
| Avg invested at EOD | 86.7% |
| EODs below 70% floor | 0 of 5 |

### Cadence
| Day | pre-market | market-open | midday | eod |
|---|---|---|---|---|
| 2026-11-09 | OK | OK | MISSING | OK |
| 2026-11-10 | OK | OK | OK | OK |
| 2026-11-11 | OK | OK | OK | OK |
| 2026-11-12 | OK | OK | OK | OK |
| 2026-11-13 | OK | OK | OK | OK |

Note: 11-09 midday never ran/committed (flagged by MISSING_COMMITS in the 11-09 EOD record). Cause unknown from the repo; no order depended on it (JNJ stop was set at open).

### Execution
- Planned orders: 1 | with an outcome line: 1 | filled: 1 | stops verified same session: 1/1
- Plan: JNJ buy 11-09 (sat-2026-11-09-JNJ, 1 @ 277.04, trailing stop e322b867 status `new`). No CORE_ACTION orders (HOLD in band all week). Every other candidate each day has a skip line with failing gates (11-09 ABBV G11, WELL G8/G9, NEM G8/G9/G11; 11-10..11-13 G8 qty/min size, G9 no slots 3/3 or sats cap, G10 CPI on 11-10, G11 spreads).
- No trades closed this week. KS-11 streak stays 2 (last loser 11-06).

### Pipeline
- Research days with ≥2 candidates from ≥2 sectors (or every rejection's gate listed): 5/5 (11-09 XLV/XLRE/XLB; 11-10 XLV/XLRE/XLY/XLF; 11-11 5 names, 4 sectors; 11-12 XLV/XLRE/XLE/XLF; 11-13 XLV/XLRE/XLE/XLF)
- Timing blocks cited outside EVENTS.md: 0 (11-10 CPI block is in EVENTS.md; "no slots 3/3", G8 qty, G11 spread are gates)
- Slots were 3/3 from 11-09 open onward, so no candidate had a free slot after JNJ filled. Cash $262.94 (13.3%) sat idle all week.

### News sleeve
**GATE: NOT MET** — only 2.3 of 6 weeks scanned; scanner uptime 75% < 95%; no bucket passes (n>=40, mean>0, median>0, t>=2.0, both halves>0, bull)
- weeks scanned: 2.3 (need 6) | signals scored at d3: 508 (need 150) | scanner uptime 28d: 75% (need 95%)
- raw headlines 3871 | signals 3871 (bull 411, bear 269, none 3035, duplicate 117, unscorable 39) | open 273, scored 407
Tradeable buckets: none

### Grade: C
Caps applied: cadence cell MISSING (11-09 midday) → max C. No other cap: invested ≥70% on 5/5 EODs (86.7%), the one entry had a same-session stop, no planned order lacks an outcome, and no eligible day had a free slot with a PASS candidate after 11-09.
Process was otherwise clean, but a missed routine is unverifiable by design and the grade is capped accordingly.

### What worked (≤3) / What didn't (≤3)
Worked:
- 19/20 cadence cells OK; every skip line lists its failing gate; zero out-of-list timing blocks.
- JNJ entered at the first open with a free slot (11-09) with a verified stop; no narrative vetoes.
- Phase return -1.13% vs SPY -1.99% (+0.86pp) with all KS PASS; invested 86.7% every EOD.
Didn't:
- Midday 11-09 missed entirely.
- Lagged SPY on the week (-0.43pp) with 13% idle cash; core held in band (53.6% vs 55.0% target) while cash sat unused.
- Max DD since start -3.38% (11-05/11-06 period); graduation needs ≤ SPY DD + 1pp, not yet evidenced.

### Lessons (also appended to LESSONS.md)
- 2026-11-13 — Full slots plus min-size gate strand ~13% cash

### Suggestions for the user (never applied by the agent)
- Idle cash (repeat of 11-06 lesson): 13.3% cash ($262.94) for 5 straight EODs, core HOLD inside ±5pp band, slots 3/3. Consider core_band ±3pp or a core top-up when cash > cash_min + a set amount. Data: core 53.6% vs target 55.0%.
- G8 min size: ABBV/WELL/COP/XLF all fail G8 (qty 0, or qty 1-2 below sat_min_pct 8%) on a ~$263 budget; most watchlist names priced >$150 are structurally unbuyable at $2,000. Consider price-capped watchlist additions (≤5/month) or revisiting sat_min_pct.
- G11 spreads: IEX spreads of 3-10% on liquid large caps (ABBV 10.67%, WELL 10.38%) recur; likely IEX-not-NBBO artifact. Consider a SIP-based check.
- Midday 11-09 miss: check the scheduler/run logs for that slot.
- KS-11 at 2 of 3 consecutive losers; the next stop-out loser pauses entries 5 days.
- EVENTS.md runway: last date 2027-12-10, well over 8 weeks. No warning.
- Watchlist: no changes proposed.

### Graduation checklist (TRADING-STRATEGY.md)
1. 🟡 13 trading days with all four routines OK/SKIPPED since 10-28 (11-09 midday MISSING breaks that day); need ≥15.
2. 🟡 Core bought 10-28; later core SELLs 10-29/10-30 filled; no later core BUY rebalance yet.
3. ✅ 5 satellite entries filled (XLE, PG, KO, ABBV, JNJ), 2 closed (XLE, ABBV), each with a same-session stop.
4. ✅ Invested ≥70% on every EOD this and last week; phase-to-date ~1 of 14 EODs below floor (Day 0/1), ≈93%.
5. 🟡 5/5 research days compliant this week; every planned order has an outcome; 10-30 was one sector but gates listed.
6. ✅ Zero timing blocks outside the closed list (weeks 1-3).
7. 🟡 Max DD -3.38% (≤8%); SPY phase DD not printed by scripts, only 3 weeks of data.
8. ✅ Phase -1.13% vs SPY -1.99% (+0.86pp), within -3pp; short sample.
9. ✅ ks.py in every EOD record; no breach the scripts missed.
10. ❌ No `Reviewed:` line under any weekly review yet.
11. ❌ Day-1 mechanics test not evidenced in memory/ (STRESS_TEST.md at repo root has procedure only, no recorded pass).

Reviewed: (the user adds "Reviewed: YYYY-MM-DD" here)
