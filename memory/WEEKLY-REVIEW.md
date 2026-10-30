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
