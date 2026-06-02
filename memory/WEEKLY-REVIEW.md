# Weekly Review

Friday reviews appended here. The agent grades itself honestly each week.

## Template for each entry

```
## Week ending YYYY-MM-DD

### Stats
| Metric | Value |
|--------|-------|
| Starting portfolio (Monday open) | $X |
| Ending portfolio (Friday close) | $X |
| Week return | ±$X (±X%) |
| S&P 500 week | ±X% |
| Bot vs S&P | ±X% |
| Max intraweek drawdown | X% |
| Trades placed | N (W:X / L:Y / open:Z) |
| Trade limit usage | N/3 |
| Win rate (closed trades) | X% |
| Best trade | TICKER +X% |
| Worst trade | TICKER -X% |
| Profit factor (sum wins / |sum losses|) | X.XX |

### Closed trades this week
| Ticker | Entry | Exit | P&L | Days held | Reason for exit |

### Open positions at week end
| Ticker | Entry | Close | Unrealized | Stop |

### Process review (per trade made this week)
For each trade:
- Was the thesis followed?
- Was sizing appropriate?
- Was the stop respected?
- In hindsight, would I make this trade again? Why/why not?
- Don't confuse outcome with process — a winning trade with bad reasoning is still a bad trade.

### Self-grades (be HARSH)
- Process discipline: [A-F]
- Documentation quality: [A-F]
- Risk management: [A-F]
- Outcome (weighted least): [A-F]
- **Overall: [A-F]**

### What worked (3-5 bullets)
- ...

### What didn't work (3-5 bullets)
- ...

### Key lessons (added to LESSONS.md)
- ...

### Strategy suggestions for user (DO NOT change strategy unilaterally)
- ...

### Graduation criteria status (from TRADING-STRATEGY.md)
- [ ] 30+ consecutive trading days without intervention: (✅/🟡/❌)
- [ ] Max drawdown under 15%: (✅/🟡/❌)
- [ ] Matched or beat SPY: (✅/🟡/❌)
- [ ] No uncaught kill-switch breaches: (✅/🟡/❌)
- [ ] User-reviewed all trade entries: (manual check)
- [ ] Memory files functional: (✅/🟡/❌)
- [ ] Handled at least one 5%+ drawdown correctly: (✅/🟡/❌)

Days running counter: N
```

---

(no reviews yet — first Friday will populate)

---

## Week ending 2026-05-27

### Stats
| Metric | Value |
|--------|-------|
| Starting portfolio (Monday open) | $10,000.00 (pre-launch baseline) |
| Ending portfolio (Friday close) | $10,000.00 |
| Week return | $0.00 (0.00%) |
| S&P 500 week | ~+1.00% |
| Bot vs S&P | -1.00% |
| Max intraweek drawdown | 0.00% |
| Trades placed | 0 (W:0 / L:0 / open:0) |
| Trade limit usage | 0/3 |
| Win rate (closed trades) | N/A |
| Best trade | N/A |
| Worst trade | N/A |
| Profit factor (sum wins / \|sum losses\|) | N/A |

### Closed trades this week
| Ticker | Entry | Exit | P&L | Days held | Reason for exit |
|--------|-------|------|-----|-----------|-----------------|
| — | — | — | — | — | No trades this week |

### Open positions at week end
| Ticker | Entry | Close | Unrealized | Stop |
|--------|-------|-------|------------|------|
| — | — | — | — | — |

**Note**: Alpaca paper account created 2026-05-27T15:19:53Z — the bot launched on Day 0 (this Friday). No trading window existed Mon–Thu. First full trading week begins 2026-06-02.

### Process review (per trade made this week)
No trades placed. Bot launched today; there was no operational window earlier in the week.

Pre-market research: not run (system not yet active).
EOD snapshots Mon–Thu: not run (system not yet active).
Kill switch checks: all clear — no triggers were possible with no capital deployed.

### Self-grades (be HARSH)
- Process discipline: **N/A** — No trades to grade; system just initialized. However, the fact that no research log entries, EOD snapshots, or pre-market routines ran this week is a documentation gap regardless of cause.
- Documentation quality: **C** — WEEKLY-REVIEW template exists and format is correct. TRADE-LOG has only Day 0 baseline. RESEARCH-LOG empty. `lessons.md` exists (lowercase — minor naming inconsistency vs references in CLAUDE.md that say `LESSONS.md`). No week's worth of cadence logs despite the cadence existing in TRADING-STRATEGY.md.
- Risk management: **A** — No positions, no losses, all kill switches clear, capital fully preserved.
- Outcome (weighted least): **D** — 0% vs SPY +1.00%. The market ran its 8th consecutive up week and we captured none of it. Opportunity cost is real even on paper.
- **Overall: C** — Launch week. Structural baseline is solid; the memory system, scripts, and rules are all in place. But we are 1% behind SPY on Day 0 with zero trades and zero documentation cadence yet established. No grade inflation for "at least we didn't lose money."

### What worked (3-5 bullets)
- Full strategy rulebook, kill switches, and memory architecture in place from Day 0
- Capital preserved at $10,000 — no drawdown
- No impulsive trades placed just to "do something" on launch day (correct behavior)
- All hard rules (options prohibition, position limits, PDT rules) are documented and accessible
- No kill switches active; clean slate entering Week 2

### What didn't work (3-5 bullets)
- System launched on a Friday — missed the entire Mon–Thu trading window for what turned out to be a +1% SPY week
- No research log entries this week — cadence routines not yet established
- No EOD snapshots for Mon–Thu — historical baseline for Week 2 drawdown calculations will use today's $10,000 only
- SPY is in an 8-week winning streak; entering during a potential late-cycle stretch means buying into extended momentum (risk to monitor)
- `lessons.md` file uses lowercase name while CLAUDE.md references `LESSONS.md` — minor inconsistency to note

### Key lessons (added to lessons.md)
- **Launch week is still week 1**: A 0% return week when SPY is +1% is a -1% relative result. Don't treat inaction as neutral when the benchmark is moving.
- **Document from Day 1**: Even with no trades, EOD snapshots and pre-market research entries should run every trading day to establish the baseline cadence and audit trail.
- **SPY 8-week streak = late-cycle caution**: Extended momentum runs eventually correct. Enter Week 2 with heightened selectivity — only high-conviction setups.

### Strategy suggestions for user (DO NOT change strategy unilaterally)
- **Naming consistency**: `lessons.md` in repo is lowercase but all references in CLAUDE.md and TRADING-STRATEGY.md say `LESSONS.md`. Suggest user renames to `LESSONS.md` for consistency, or updates all references. No functional impact, but reduces confusion.
- **Launch-day handling**: Strategy doesn't address what to do when the system initializes mid-week. Suggest adding: "If the bot launches mid-week, treat remaining trading days in that week as the first partial week — full documentation cadence begins immediately." Not changing strategy; flagging a gap.

### Graduation criteria status (from TRADING-STRATEGY.md)
- [ ] 30+ consecutive trading days without intervention: ❌ (Day 0 — 0 days)
- [ ] Max drawdown under 15%: ✅ (0.00% drawdown)
- [ ] Matched or beat SPY: ❌ (0% vs SPY ~+1%; behind by ~1%)
- [ ] No uncaught kill-switch breaches: ✅ (none fired, none missed)
- [ ] User-reviewed all trade entries: 🟡 (no trade entries yet — vacuously satisfied)
- [ ] Memory files functional: ✅ (all files readable, no corruption)
- [ ] Handled at least one 5%+ drawdown correctly: ❌ (no drawdown experienced yet)

**Graduation criteria met: 3/7**

Days running counter: **0** (launches Monday 2026-06-02 as Day 1)

---

## Week ending 2026-05-27 — Confirmed Review (second run, live data)

> Prior entry above was written during the setup session with estimated data. This entry uses confirmed live Alpaca + Perplexity data. SPY WTD corrected from ~+1.00% estimate to confirmed +0.51%.

### Stats
| Metric | Value |
|--------|-------|
| Starting portfolio (Monday open) | $10,000.00 (pre-launch; bot created 2026-05-27T15:19Z) |
| Ending portfolio (Wed close) | $10,000.00 |
| Week return | $0.00 (0.00%) |
| S&P 500 week (WTD through Wed) | +0.51% (SPY: 745.64 → 749.47) |
| Bot vs S&P | -0.51% |
| Max intraweek drawdown | 0.00% |
| Trades placed | 0 (W:0 / L:0 / open:0) |
| Trade limit usage | 0/3 |
| Win rate (closed trades) | N/A |
| Best trade | N/A |
| Worst trade | N/A |
| Profit factor | N/A |

### Closed trades this week
| Ticker | Entry | Exit | P&L | Days held | Reason for exit |
|--------|-------|------|-----|-----------|-----------------|
| — | — | — | — | — | No trades this week |

### Open positions at week end
| Ticker | Entry | Close | Unrealized | Stop |
|--------|-------|-------|------------|------|
| — | — | — | — | — |

**Note**: Today is Wednesday May 27, not Friday. The weekly review routine triggered on launch day (Wednesday). Week is not complete — Thu May 28 and Fri May 29 still ahead. This review covers the one partial trading session since launch.

### Process review (per trade made this week)
No trades placed. Bot initialized mid-day Wednesday May 27.

- **Pre-market research (run 1)**: Completed; identified no qualifying setups. JOLTS data risk, AMC earnings noise, market at ATH — correct HOLD decision.
- **Market-open (run 1)**: HALTED — research log wasn't committed before market-open fired. Correct behavior per framework (halt, notify, don't trade blind).
- **Pre-market research (run 2)**: Completed; confirmed no new qualifying setups (WTI -4.73% weakens Energy thesis; no fresh catalyst clears buy-side gate item 6).
- **EOD snapshot**: Filed correctly for 2026-05-27.

No trade-by-trade review possible — no trades.

### Self-grades (be HARSH)
- Process discipline: **C** — Market-open fired before research was committed (sequencing failure). Halt was correct behavior, but the root cause (wrong execution order) is a process flaw. Two separate sessions created overlapping log entries.
- Documentation quality: **C** — Logs filed, format matches template. But: (1) weekly review written twice for same date, (2) SPY estimate in prior review was 2x actual, (3) lessons.md filename inconsistency with all references unresolved.
- Risk management: **A** — No positions, no losses, 0.00% drawdown. Kill switches all clear. Capital 100% preserved. No violations possible.
- Outcome (weighted least): **D** — 0% vs SPY +0.51% WTD. Opportunity cost is real even in paper; benchmark moved while we held 100% cash.
- **Overall: C** — Structural foundation solid. Real deductions for sequencing failure and documentation gaps. No grade inflation for "at least we didn't lose."

### What worked (3-5 bullets)
- Capital 100% preserved; no impulsive trades on launch day
- Kill-switch halt fired correctly on first market-open attempt (missing research log)
- Both pre-market sessions correctly concluded HOLD — no thesis forced
- All memory files functional and committed to main
- Sector momentum analysis complete with specific tickers evaluated and rejected with documented reasons

### What didn't work (3-5 bullets)
- Market-open routine ran before pre-market research was committed → sequencing failure → halt
- Two sessions same day created duplicate RESEARCH-LOG entries and overlapping log noise
- Weekly review triggered Wednesday instead of Friday — routine cadence misaligned
- SPY estimate (+1.00%) in first review was nearly 2x actual confirmed figure (+0.51%)
- `lessons.md` filename (lowercase) inconsistent with all documentation references (`LESSONS.md` uppercase)

### Key lessons (added to lessons.md)
- **Always pull live SPY data before publishing weekly review**: estimates drift by up to 2x. Use perplexity.sh every time, never rely on memory.

### Strategy suggestions for user (DO NOT change strategy unilaterally)
1. **Filename fix**: Rename `memory/lessons.md` → `memory/LESSONS.md`. All CLAUDE.md and TRADING-STRATEGY.md references use uppercase. No functional impact; reduces confusion.
2. **Sequencing guard**: Market-open routine must verify a same-day RESEARCH-LOG entry exists before proceeding. Suggest explicit check: if today's date not found in RESEARCH-LOG.md → halt and request pre-market run first.
3. **Weekly review cadence**: Routine fired on a Wednesday (not Friday). For mid-week launches, the first full weekly review should run on the following Friday, not launch day. Suggest rule: "If bot launches mid-week, run abbreviated launch-day summary; full weekly review runs Friday."

### Graduation criteria status (from TRADING-STRATEGY.md)
- [ ] 30+ consecutive trading days without intervention: ❌ (Day 1 — launched today)
- [ ] Max drawdown under 15%: ✅ (0.00%)
- [ ] Matched or beat SPY: ❌ (0.00% vs SPY +0.51% WTD)
- [ ] No uncaught kill-switch breaches: ✅ (all switches checked; market-open halt fired correctly)
- [ ] User-reviewed all trade entries: 🟡 (no trade entries to review)
- [ ] Memory files functional: ✅ (all readable, no corruption)
- [ ] Handled at least one 5%+ drawdown correctly: ❌ (no drawdown yet)

**Graduation criteria met: 3/7**

Days running counter: **1** (Day 1 = 2026-05-27; full cadence resumes Thu 2026-05-28)

---

## Week ending 2026-05-29

### Stats
| Metric | Value |
|--------|-------|
| Starting portfolio (prior Friday close — May 22) | $10,000.00 (bot launched 2026-05-27; May 22 is prior-week baseline) |
| Ending portfolio (Friday May 29 close) | $10,000.00 |
| Week return | $0.00 (0.00%) |
| S&P 500 week | ~+1.20% (Perplexity synthesis; SPY May 22 close ~$748.94 → May 29 ~$754.60; data sources conflict, range +0.76–1.20%) |
| Bot vs S&P | -1.20% this week (est.) |
| Max intraweek drawdown | 0.00% (100% cash all week) |
| Trades placed | 0 (W:0 / L:0 / open:0) |
| Trade limit usage | 0/3 |
| Win rate (closed trades) | N/A |
| Best trade | N/A |
| Worst trade | N/A |
| Profit factor (sum wins / \|sum losses\|) | N/A |

Cumulative phase since launch (May 27): Bot +0.00% vs SPY approx +0.43% (SPY $751.38 May 27 close → ~$754.60 May 29). Cumulative since inception (May 22 baseline): Bot 0.00% vs SPY ~+1.71%.

### Closed trades this week
| Ticker | Entry | Exit | P&L | Days held | Reason for exit |
|--------|-------|------|-----|-----------|-----------------|
| — | — | — | — | — | No trades this week |

### Open positions at week end
| Ticker | Entry | Close | Unrealized | Stop |
|--------|-------|-------|------------|------|
| — | — | — | — | — |

**Note**: First proper Friday weekly review. Bot launched Wed May 27 (Day 1). Week covered May 27–29 in this review (May 25 = Memorial Day closed; May 26 = no bot activity, not yet launched).

### Process review (per trade made this week)
No trades placed. All three active trading days ran full documentation cadence. Each produced a documented HOLD decision.

**May 27 (Day 1 — Wednesday):**
- 2 pre-market sessions (carryover sequencing from launch). Decision: HOLD. Rationale: ATH, JOLTS at 10:00 AM ET, AMC earnings noise (CRM/MRVL/SNOW), no candidate with documented 2:1 R:R catalyst. Buy-side gate item 6 not satisfied for any name.
- EOD snapshot filed. SPY +0.61%.
- Verdict: Correct HOLD. Minor: duplicate research sessions added log noise.

**May 28 (Day 2 — Thursday):**
- 1 pre-market session. Decision: HOLD. Rationale: PCE + Q1 GDP second estimate at 8:30 AM ET = strategy explicitly prohibits trading on/before major macro releases. Hard gate, no exceptions. SNOW +30% gap-up correctly rejected (chasing gap ≠ thesis).
- EOD snapshot filed. SPY -0.07%.
- Verdict: Correct HOLD. Clean execution of PCE-day rule.

**May 29 (Day 3 — Friday):**
- 1 pre-market session. Decision: HOLD. Rationale: PCE landed at +3.8% YoY (hottest since May 2023) → "higher for longer" locked in → compressed multiples. Market at/near ATH. XLE/XOM/OVV blocked by negative near-term technicals (MACD negative, below 50-day MA). No earnings catalyst; low-impact data day.
- EOD snapshot filed. SPY close unavailable from Perplexity (same-day latency) — noted honestly in log.
- Verdict: Correct HOLD. No setup cleared all 9 buy-side gate checks this week.

### Self-grades (be HARSH)
- Process discipline: **B** — All HOLD decisions documented with specific gate reasoning. PCE-day rule applied correctly. EOD snapshots filed 3/3 days. Deductions: May 27 duplicate research sessions (sequencing issue); May 26 (first post-Memorial Day trading day) had no coverage because bot launched the following day.
- Documentation quality: **B-** — Research log and EOD snapshots complete for 3 days. Gaps: May 29 SPY close filed as "unavailable" (data latency), May 26 has no entry, prior session left two redundant "week ending 2026-05-27" reviews cluttering the file.
- Risk management: **A** — 0.00% drawdown. Kill switches checked daily; none fired, none missed. No rule violations. PDT count 0. Full capital preserved.
- Outcome (weighted least): **D** — 0.00% vs SPY +1.20% this week. Cumulative approximately -1.71% vs SPY since inception (prior week -0.51%, this week -1.20%). The S&P extended its longest winning streak since 2023. Every HOLD day is a day the benchmark moves further ahead.
- **Overall: C+** — Process is sound and disciplined. Each HOLD was correct given the available setup quality and gate criteria. But a C+ is honest: three days of market action, zero participation, widening benchmark gap. "Correct process in a rising market" is not the same as "good outcome." The HOLDs were right; a week-3 repeat would be a concern.

### What worked (3-5 bullets)
- PCE prohibition applied without hesitation on May 28 — no trade on the Fed's preferred inflation day
- All HOLD decisions backed by specific buy-side gate failures, not vague caution
- EOD snapshot cadence established and consistent (3/3 days)
- Energy (XLE/XOM/OVV), Cloud-AI (SNOW), Healthcare candidates all evaluated and correctly rejected with data-specific reasons
- No impulsive buys at ATH just to "be invested"

### What didn't work (3-5 bullets)
- Zero capital deployed vs SPY +1.20% week; cumulative lag growing (-1.71% vs SPY since inception)
- May 26 had no bot activity — first post-Memorial Day trading day entirely missed due to launch timing
- SPY daily close unavailable from Perplexity on May 29; EOD snapshot filed with data gap
- Oil price data unreliable across sources (FRED spot vs near-month futures diverge by $20+/bbl), blocking Energy thesis from being accurately sized
- Weekly review was written twice for "week ending 2026-05-27" (Wednesday launch day), creating WEEKLY-REVIEW.md clutter

### Key lessons (added to lessons.md)
- Perplexity cannot retrieve same-day closing prices reliably — need alpaca.sh quote SPY as EOD fallback
- PCE +3.8% YoY (hottest since May 2023) → higher-for-longer locked in → prefer Energy, Industrials, Consumer Staples for new longs vs growth/rate-sensitive sectors
- Three consecutive HOLD sessions in a bull run is correct process; a fourth consecutive zero-position week warrants user-level review of candidate screening

### Strategy suggestions for user (DO NOT change strategy unilaterally)
1. **SPY fallback data**: `perplexity.sh` unreliable for same-day closes. Add `alpaca.sh quote SPY` as fallback for EOD SPY column. No strategy change — operational fix only.
2. **WTI reference price**: FRED spot WTI is 10+ days stale; near-month futures (e.g., CLN26) are the real-time reference for Energy sector analysis. Suggest adding to TRADING-STRATEGY.md: "Use WTI near-month futures as canonical oil price, not FRED spot data." Flagging for user approval.
3. **Extended HOLD alert**: Suggest that if the bot runs 2+ consecutive full weeks with 0 positions while SPY outperforms by 1%+, agent flags to user for review of gate calibration. No rule change; transparency mechanism only.
4. **Naming inconsistency (carried over)**: `memory/lessons.md` is lowercase; all references in CLAUDE.md and TRADING-STRATEGY.md use `LESSONS.md`. Suggest rename. Flagged in prior two reviews — no action yet.

### Graduation criteria status (from TRADING-STRATEGY.md)
- [ ] 30+ consecutive trading days without intervention: ❌ (3/30 trading days elapsed)
- [ ] Max drawdown under 15%: ✅ (0.00% drawdown)
- [ ] Matched or beat SPY: ❌ (0.00% vs SPY; behind ~1.71% cumulative since inception)
- [ ] No uncaught kill-switch breaches: ✅ (all switches checked daily; none fired, none missed)
- [ ] User-reviewed all trade entries: 🟡 (no trades placed — vacuously satisfied)
- [ ] Memory files functional: ✅ (all files readable, no corruption)
- [ ] Handled at least one 5%+ drawdown correctly: ❌ (no drawdown experienced)

**Graduation criteria met: 3/7**

Days running counter: **3** (Day 1 = 2026-05-27; Day 3 = 2026-05-29)

---

## Week ending 2026-06-01

> **Note**: Routine triggered Monday June 1, not Friday. Week contains 1 trading day (June 1 only); prior Friday's review (May 29) is already filed above. Reviewing Day 4 activity.

### Stats
| Metric | Value |
|--------|-------|
| Starting portfolio (prior Friday May 29 close) | $10,000.00 |
| Ending portfolio (Mon June 1 close) | $10,000.00 |
| Week return | $0.00 (0.00%) |
| S&P 500 week (May 29 → June 1) | +0.34% (per EOD log; Investing.com shows −0.03% — data source conflict noted) |
| Bot vs S&P this week | −0.34% |
| Phase P&L since launch (May 27) | Bot 0.00% vs SPY ~+1.02% |
| Max intraweek drawdown | 0.00% |
| Trades placed | 0 (W:0 / L:0 / open:0) |
| Trade limit usage | 0/3 |
| Win rate (closed trades) | N/A |
| Best trade | N/A |
| Worst trade | N/A |
| Profit factor (sum wins / \|sum losses\|) | N/A |

### Closed trades this week
| Ticker | Entry | Exit | P&L | Days held | Reason for exit |
|--------|-------|------|-----|-----------|-----------------|
| — | — | — | — | — | No trades placed |

### Open positions at week end
| Ticker | Entry | Close | Unrealized | Stop |
|--------|-------|-------|------------|------|
| — | — | — | — | — |

### Process review (per trade made this week)
No trades placed. One trading day (June 1, Monday).

**June 1 (Day 4 — Monday):**
- Pre-market research: Complete. Correct HOLD. Primary blockers: (1) WTI −1.73% on the day undercuts Energy entry timing; (2) ISM Manufacturing PMI at 10:00 AM ET was unknown pre-entry — strategy prohibits entering before sector-relevant macro prints; (3) S&P at 21st record close with narrow breadth; (4) Five major data prints in five sessions (JOLTS, ADP, ISM Services, Jobless Claims, NFP) = elevated macro uncertainty all week.
- XOM watch setup documented with specific entry conditions (WTI hold above $87 + ISM ≥52.7).
- EOD snapshot: Filed. SPY +0.34%.
- Kill switches: all clear.
- Verdict: Correct HOLD. Every blocker was data-specific and rule-based, not vague caution.

No bad-process winners or losers to dissect.

### Self-grades (be HARSH)
- Process discipline: **B+** — Pre-market research complete with rigorous HOLD rationale. XOM candidate framework documented with clear entry conditions. EOD filed. Deduction: weekly review firing on Monday rather than Friday is a cadence failure — 4 trading days in and the Friday routine still hasn't run on a Friday.
- Documentation quality: **B** — Research log, EOD snapshot, and now this review all complete. Deduction: SPY data conflict (EOD log shows +0.34%, Investing.com shows −0.03%) unresolved — data sourcing inconsistency persists. `lessons.md` still lowercase vs all references using `LESSONS.md`.
- Risk management: **A** — 0.00% drawdown. Kill switches checked; none fired; none missed. PDT count 0. Full capital intact.
- Outcome (weighted least): **D** — 0.00% vs SPY +0.34% today; −1.02% cumulative vs SPY since phase launch. Four trading days; four zero-trade days. Every day SPY moves further ahead.
- **Overall: C+** — Process is disciplined and each HOLD was defensible. But "correctly not losing" is not performance. The cumulative SPY gap is widening. A fourth consecutive zero-position week would be a process concern, not a process strength.

### What worked (3-5 bullets)
- WTI downmove correctly blocked an Energy entry that would have required chasing a falling-input trade
- ISM Manufacturing timing rule applied cleanly — no pre-data entry despite a watchlist candidate (XOM)
- XOM candidate framework documented with specific entry conditions for follow-up (WTI >$87 AND ISM ≥52.7)
- EOD snapshot cadence maintained (4/4 trading days since launch)
- All kill switches checked and clear; no violations

### What didn't work (3-5 bullets)
- Weekly review routine fired on Monday (not Friday) — cadence remains misaligned; prior three reviews were also mis-timed
- Cumulative benchmark gap: −1.02% vs SPY since phase launch with 0 positions taken
- SPY data source conflict (EOD log vs Investing.com) unresolved; two sources giving different figures for same day
- `lessons.md` filename inconsistency still unresolved after 4 reviews flagging it
- Four consecutive trading days with zero deployment; XOM watch candidate not yet actionable

### Key lessons (added to lessons.md)
- Weekly review cadence (Friday 4:30 PM ET) has not fired on a Friday in 4 reviews — the trigger is firing at wrong times. This is a scheduling/orchestration gap, not a process gap.
- SPY data from Investing.com via Perplexity and from EOD snapshot are diverging (−0.03% vs +0.34% for June 1). Need to standardize on a single source. Alpaca `quote SPY` is the most direct and should be canonical.
- After 4 trading days with 0 positions and SPY +1.02%, the next week must either produce 1+ qualifying entry or explicitly flag to user for gate calibration review.

### Strategy suggestions for user (DO NOT change strategy unilaterally)
1. **Weekly review scheduling**: Review has fired Wednesday (launch), Wednesday (duplicate), Friday (correct), Monday — 1/4 on schedule. Suggest checking cron/trigger configuration. No strategy change; orchestration fix only.
2. **SPY canonical source**: `bash scripts/alpaca.sh quote SPY` returns real-time price with bid/ask; Investing.com via Perplexity returns potentially incomplete intraday data. Suggest adopting Alpaca quote as primary SPY reference, using prior day's close from TRADE-LOG.md for day-over-day comparison. No strategy change; data hygiene fix.
3. **4-week zero-position alert**: If week 3 also produces 0 trades while SPY outperforms, user should review whether the buy-side gate (particularly item 6 — documented catalyst) is being applied at the right stringency level. Not changing the gate; flagging for transparency.
4. **Filename fix (repeated)**: Rename `memory/lessons.md` → `memory/LESSONS.md`. Still unresolved after 4 reviews.

### Graduation criteria status (from TRADING-STRATEGY.md)
- [ ] 30+ consecutive trading days without intervention: ❌ (4/30 days elapsed)
- [ ] Max drawdown under 15%: ✅ (0.00%)
- [ ] Matched or beat SPY: ❌ (0.00% vs SPY; −1.02% cumulative since launch)
- [ ] No uncaught kill-switch breaches: ✅ (all switches clear; none fired, none missed)
- [ ] User-reviewed all trade entries: 🟡 (no trade entries to review — vacuously satisfied)
- [ ] Memory files functional: ✅ (all readable, no corruption)
- [ ] Handled at least one 5%+ drawdown correctly: ❌ (no drawdown experienced)

**Graduation criteria met: 3/7**

Days running counter: **4** (Day 1 = 2026-05-27; Day 4 = 2026-06-01)

---

## Week ending 2026-06-02

> **Note**: Routine triggered Tuesday June 2 — not Friday. Fifth consecutive non-Friday trigger (cadence misconfigured). Week covers June 1–June 2 (2 trading days since prior Friday May 29). June 1 was partially reviewed in "week ending 2026-06-01" entry; that entry is retained; this review stands as the complete Friday-window record through today.

### Stats
| Metric | Value |
|--------|-------|
| Starting portfolio (prior Friday May 29 close) | $10,000.00 |
| Ending portfolio (Tuesday June 2 close) | $10,000.00 |
| Week return | $0.00 (0.00%) |
| S&P 500 week (May 29 → June 2) | +0.23% (SPY $758.08 → ~$759.84; stockanalysis.com + Alpaca quote) |
| Bot vs S&P this week | −0.23% |
| Phase P&L since launch (May 27) | Bot 0.00% vs SPY +1.13% ($751.38 → ~$759.84) |
| Max intraweek drawdown | 0.00% (100% cash) |
| Trades placed | 0 (W:0 / L:0 / open:0) |
| Trade limit usage | 0/3 |
| Win rate (closed trades) | N/A |
| Best trade | N/A |
| Worst trade | N/A |
| Profit factor (sum wins / \|sum losses\|) | N/A |

**SPY daily confirmation** (stockanalysis.com, reconciled):
- May 27 close: $751.38 | May 28: $755.15 | May 29: $758.08 | Jun 1: $760.28 (+0.29%) | Jun 2 est.: ~$759.84 (−0.06%, Alpaca quote)
- Note: Prior EOD snapshots logged June 1 as +0.34%; correct figure is +0.29%. Discrepancy due to stale Perplexity data — corrected here.

### Closed trades this week
| Ticker | Entry | Exit | P&L | Days held | Reason for exit |
|--------|-------|------|-----|-----------|-----------------|
| — | — | — | — | — | No trades placed |

### Open positions at week end
| Ticker | Entry | Close | Unrealized | Stop |
|--------|-------|-------|------------|------|
| — | — | — | — | — |

**XOM watch still active**: Entry conditions partially met (WTI +5.49% Jun 1, ISM Mfg 54.0 beat). JOLTS Jun 2 outcome undocumented (see process review). Next evaluation window: Wed June 4 post-ISM Services + ADP, and Thu June 5 pre-NFP.

### Process review (per trade made this week)

**June 1 (Day 4 — Monday)**: Previously reviewed in "week ending 2026-06-01" entry. Summary: Correct HOLD. ISM Manufacturing at 10:00 AM blocked 9:45 AM entry per strategy rule. No process deficiencies beyond what was noted in that entry.

**June 2 (Day 5 — Tuesday):**
- Pre-market research: Outstanding. First real trade candidate in 5 sessions. XOM fully documented: all 9 buy-side gate checks passed, entry/stop/target/R:R calculated, specific JOLTS timing blocker correctly flagged. This is exactly what buy-side gate item 6 requires.
- Was the thesis followed? Yes — XOM thesis is sound (WTI elevated, ISM beat, sector momentum leading, no near-term earnings). Entry conditions (WTI >$87 AND ISM ≥52.7) were both confirmed met going into June 2.
- Was sizing appropriate? Yes — 9 shares × ~$156 = ~$1,404 = 14.0% of equity (within the 15% limit).
- Was the stop respected? N/A — trade not executed.
- Critical documentation gap: Pre-market research correctly deferred entry to 10:10 AM post-JOLTS. The JOLTS result (April 2026 job openings) and the resulting decision (execute or defer to Wednesday) are not documented anywhere — not in TRADE-LOG, not in EOD snapshot. The EOD snapshot says "no trades" but gives no reason. This is the most significant process failure of the week.
- In hindsight, would I make this trade again? The thesis is valid; the conditional structure was correct. But I cannot evaluate the execution decision without knowing the JOLTS result.
- Don't confuse outcome with process: Having a good pre-market plan and zero follow-through documentation is still a process failure, regardless of whether the JOLTS outcome justified deferral.

### Self-grades (be HARSH)
- Process discipline: **B−** — Pre-market research for June 2 was genuinely strong (first real candidate, complete gate documentation, timing risk correctly identified). Deduction for: (1) market-open decision not documented, (2) routine again fired Tuesday not Friday, (3) EOD snapshot missing decision rationale.
- Documentation quality: **C** — Pre-market excellent, EOD snapshot filed, but the most important document of the week — the JOLTS result and XOM deferral/execution decision — is completely absent. A conditional trade plan that produces no follow-through record is a first-order documentation failure.
- Risk management: **A** — 0.00% drawdown. All kill switches checked and clear. No rule violations. PDT count 0. Full capital intact.
- Outcome (weighted least): **D** — 0.00% vs SPY +0.23% this week; −1.13% phase. Five consecutive zero-position trading days; first legitimate buy candidate emerged but not executed (or not documented as executed).
- **Overall: C** — Slight regression from last week's C+. The pre-market process improved materially (first real candidate); the documentation gap at market-open erases some of that credit. Six trading days in, -1.13% vs SPY, one conditional candidate pending. Week 3 is the stress test.

### What worked (3-5 bullets)
- First complete buy candidate identified (XOM) with all 9 gate checks documented and explicit entry conditions — correct process improvement vs prior weeks
- JOLTS timing risk correctly identified in pre-market and used to structure a conditional entry rather than a blind 9:45 AM order
- ISM Manufacturing confirmation (54.0 beat) strengthened Energy thesis — sector momentum research compounding across sessions
- EOD snapshot cadence maintained (5/5 trading days since launch)
- All kill switches checked and clear; no violations

### What didn't work (3-5 bullets)
- JOLTS outcome and XOM decision (execute/defer) not documented anywhere — critical gap in the most important routine of the week
- Weekly review triggered Tuesday (again) — 0/5 reviews have fired on a Friday since launch
- SPY data conflict compounded further: EOD log had Jun 1 at +0.34%, now corrected to +0.29% via stockanalysis.com; sources continue to diverge
- Five consecutive zero-position sessions; phase gap vs SPY now -1.13%
- `lessons.md` filename still lowercase (vs LESSONS.md in all references) — flagged in 4 prior reviews with no fix

### Key lessons (added to lessons.md)
- When a conditional trade plan exists (e.g., "enter after JOLTS at 10:00"), the market-open routine MUST document the data release result and the decision taken (execute, defer, or abort) before the session ends — otherwise the conditional plan is an unfalsifiable claim
- stockanalysis.com historical SPY data (accessible via Perplexity) is the most reliable source for confirmed closes; adopt as primary reference over Perplexity's text-synthesis estimates which diverge by up to 2×
- SPY intraday Alpaca quote ($759.84 on Jun 2) + prior confirmed close from stockanalysis.com = reliable EOD snapshot reference; this combination should be standard going forward

### Strategy suggestions for user (DO NOT change strategy unilaterally)
1. **Market-open documentation requirement**: When pre-market research contains a conditional entry (data-dependent), the market-open routine must log: (a) the data release result, (b) whether the condition was met, (c) what action was taken. Without this, conditional plans are phantom entries. No strategy change — documentation process clarification only.
2. **Weekly review scheduling (repeated, 5th flag)**: Review has now triggered Tue, Wed, Wed, Mon, Tue — never on a Friday. Orchestration is clearly misconfigured. Suggest user check the cron/trigger schedule.
3. **XOM entry still potentially live**: XOM entry conditions are met (WTI >$87, ISM 54.0). If JOLTS on June 2 was in-line or better, entry was justified. Recommend user verify whether XOM entry should be taken Wednesday June 4 post-ISM Services + ADP. Entry window closes if NFP (Friday June 5) creates too much uncertainty.
4. **Cumulative lag alert (-1.13% vs SPY)**: Five zero-position trading days in a +1.13% SPY run. Per prior lessons, user-level review of gate calibration is warranted if week 3 also produces 0 trades. This is that week — recommend user explicitly confirm whether XOM (or another candidate) clears the bar or the gate is being applied correctly.
5. **lessons.md rename (5th flag)**: Still lowercase. Still causes tool confusion. Rename to LESSONS.md or update all references. No functional change.

### Graduation criteria status (from TRADING-STRATEGY.md)
- [ ] 30+ consecutive trading days without intervention: ❌ (5/30 days elapsed)
- [ ] Max drawdown under 15%: ✅ (0.00%)
- [ ] Matched or beat SPY: ❌ (0.00% vs SPY; −1.13% phase since launch)
- [ ] No uncaught kill-switch breaches: ✅ (all switches checked; none fired, none missed)
- [ ] User-reviewed all trade entries: 🟡 (no trade entries to review — vacuously satisfied)
- [ ] Memory files functional: ✅ (all readable; lessons.md lowercase naming note persists)
- [ ] Handled at least one 5%+ drawdown correctly: ❌ (no drawdown experienced)

**Graduation criteria met: 3/7**

Days running counter: **5** (Day 1 = 2026-05-27; Day 5 = 2026-06-02)
