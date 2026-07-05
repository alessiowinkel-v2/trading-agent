# Lessons

What the agent has learned. Append new entries; do not delete old ones. If file exceeds 500 lines, rotate older entries to `LESSONS-ARCHIVE.md`.

## Format

```
## YYYY-MM-DD — Lesson title

**Context**: What happened?
**Mistake or insight**: What did we learn?
**Rule change**: What should we do differently? (If permanent, flag for user to add to TRADING-STRATEGY.md — DO NOT change strategy unilaterally.)
```

---

## Initial lessons (pre-loaded — do not delete)

### Survivorship bias is real
Past winners are visible; past losers were delisted and forgotten. Don't anchor on "this stock has been a great long-term hold" without checking how many similar-sounding stocks failed.

### A 30-day track record proves nothing
Whether up 10% or down 10% in the first month, it's noise. Make decisions based on process quality, not month-to-month outcomes.

### "Doing something" is the most expensive habit
Every trade costs spread + potential bad timing + mental load. Default action is no action.

### Stops exist to prevent catastrophe, not to optimize
Don't move stops to avoid taking a loss. The stop was set when thinking clearly; moving it is almost always emotional.

### Earnings are volatility, not edge
Entering a position right before earnings is gambling on a coin flip with skew. Unless the thesis is explicitly an earnings thesis (rare), avoid.

### Tight stops shake you out of winners (from source guide's experience)
The previous trading challenge learned this the hard way. 10% trailing is the floor, not the ceiling. Tightening too early on a winner with normal volatility = forced exit before the move.

### Sector momentum trumps individual conviction (from source guide)
Don't force a thesis if the whole sector is rolling over. Two failed trades in a sector = exit that sector entirely. The market is telling you something.

### Options destroy compound returns (from source guide)
A single options trade wiped out a full month of gains in the previous challenge. Hence the absolute prohibition. Even "safe" options strategies (covered calls, defined-risk spreads) are out for this agent.

### The model itself can drift
When Claude updates, my "instincts" may shift even though prompts didn't. If trading behavior changes noticeably after an apparent model update, pause and review before continuing.

### Paper habits become real habits
Sloppy entries during paper trading produce sloppy entries with real money. Treat every paper trade like real money.

## Blacklist (tickers to avoid)

Currently empty. Add tickers here with reason if a stock causes repeated bad decisions.

---

## 2026-05-27 — Launch week: 0% return is not neutral

**Context**: Bot launched on Friday 2026-05-27. No trades placed. SPY returned ~+1% for the week (8th consecutive up week).
**Insight**: Being flat while the benchmark gains is a -1% relative result. Inaction is not free. The opportunity cost is real on paper and will be even more real with real money.
**Rule change**: None. Strategy already says "Patience > activity" — but that refers to avoiding bad trades, not avoiding good ones. Entry into Week 2 should be active research and opportunistic deployment if criteria are met.

## 2026-05-27 — Cadence must run from Day 1, no exceptions

**Context**: No EOD snapshots, no pre-market research log entries for the launch week because the system initialized today.
**Insight**: Even with zero trades, the daily documentation cadence (pre-market research, EOD snapshot) must run every trading day. Without it, there is no audit trail, no drawdown baseline, and no accountability.
**Rule change**: None. The cadence is already defined in TRADING-STRATEGY.md. Just execute it starting Monday.

## 2026-05-27 — 8-week SPY streak = late-cycle alert

**Context**: SPY has gained ~8 consecutive weeks entering June 2026.
**Insight**: Extended momentum runs revert. Entering the portfolio into a late-cycle run requires exceptional selectivity — only the highest-conviction, fundamentally-supported setups. Buying "because the market is going up" violates the philosophy explicitly.
**Rule change**: None. Strategy already prohibits thesis-free trades. Flagging for heightened discipline.

## 2026-05-27 — Always pull live SPY data for weekly review; never estimate

**Context**: First weekly review estimated SPY WTD at ~+1.00%. Confirmed live data (Perplexity/Investing.com) shows +0.51% — nearly 2x overestimate.
**Insight**: Memory of "roughly +1%" is unreliable when the actual figure is +0.51%. The weekly review template already requires perplexity.sh query; just execute it every time without exception.
**Rule change**: None. The process is correct; execution was lazy. Pull live data, always.

## 2026-05-29 — perplexity.sh cannot retrieve same-day closing prices

**Context**: EOD snapshot for May 29 could not obtain SPY closing price via perplexity.sh — returned "unavailable." Weekly review SPY data is also imprecise due to conflicting source closes for the same dates.
**Insight**: perplexity.sh has meaningful latency on same-day data. It is unreliable as a primary source for the day's SPY closing return in the EOD snapshot. Need a fallback query.
**Rule change**: Flag for user: add `bash scripts/alpaca.sh quote SPY` as fallback for EOD SPY close. No unilateral change.

## 2026-05-29 — PCE +3.8% YoY (hottest since May 2023): sector implications

**Context**: April 2026 PCE came in at +3.8% YoY (consensus +3.5%), monthly +0.40% vs consensus +0.53%. Core PCE +3.3% YoY. Fed June hold effectively locked in.
**Insight**: Higher-for-longer means compressed multiples for growth/tech. For new positions, prioritize sectors that held up best in 2022–23 rising-rate periods: Energy (XLE), Industrials (XLI), Consumer Staples (XLP). Rate-sensitive sectors (XLRE, XLU) and high-multiple tech become lower priority until rate picture softens.
**Rule change**: None. Strategy already says to follow sector momentum; this informs which sectors to screen first for the next few weeks.

## 2026-05-29 — Three consecutive HOLDs in a bull market: opportunity cost is real

**Context**: Bot has run 3 trading days across a +1.2% SPY week with 0 positions taken. Cumulative lag vs SPY approximately -1.71% since inception.
**Insight**: "Patience > activity" means avoiding bad trades, not all trades. Prolonged zero-deployment in a bull run means the benchmark moves further ahead, requiring larger future gains to catch up. If week 3 is also 0 positions, user-level review of candidate screening and gate calibration is warranted.
**Rule change**: None. Flag to user: if the next week is also 0 positions in a rising market, worth reviewing whether the buy-side gate is being applied correctly vs applied too conservatively.

## 2026-05-29 — Use near-month futures for WTI oil reference, not FRED spot data

**Context**: Three research sessions encountered a $20+/bbl discrepancy between FRED WTI spot ($112/bbl, stale from May 18) and WTI near-month futures (CLN26 ~$89-92/bbl). This gap blocked Energy thesis from being accurately sized.
**Insight**: FRED spot WTI is published with ~10-day delay. WTI near-month futures (front-month active contract on CME) are the correct real-time price reference for Energy sector analysis.
**Rule change**: Flag for user to add to TRADING-STRATEGY.md: "Use WTI near-month futures as canonical oil price, not FRED spot data." Flagging for user approval only.

## 2026-06-01 — Weekly review cadence still not firing on Fridays

**Context**: Four reviews run since launch (2026-05-27, 2026-05-27 duplicate, 2026-05-29, 2026-06-01). Only one fired on a Friday (May 29). The June 1 review fired Monday morning.
**Insight**: The scheduling/trigger for the weekly review routine is misconfigured. This is not a process failure by the agent but an orchestration issue. The agent should flag when a "Friday weekly review" fires on a non-Friday.
**Rule change**: None. Flag to user: check the cron/trigger schedule for the weekly review routine.

## 2026-06-01 — Standardize SPY price source to avoid data conflicts

**Context**: EOD snapshot for June 1 reported SPY +0.34%; Investing.com via Perplexity reported −0.03% for the same day. These figures are irreconcilable and create noise in phase tracking.
**Insight**: Multiple sources for SPY daily price produce conflicting data, especially for same-day or recently completed sessions. Alpaca's `bash scripts/alpaca.sh quote SPY` returns bid/ask in real time; TRADE-LOG.md prior close provides the reference. This is the most direct and reliable combination.
**Rule change**: Flag to user: adopt Alpaca quote as primary SPY reference for EOD snapshots and weekly reviews.

## 2026-06-01 — Four zero-position trading days: next week is a test

**Context**: Bot has run 4 trading days (May 27–June 1) with 0 positions opened. SPY has gained ~+1.02% since launch. Each correct HOLD is individually defensible; four in a row in a bull run raises the question of gate calibration.
**Insight**: "Patience > activity" is a rule for avoiding bad trades, not all trades. If week 3 also produces 0 positions, the user should review whether the buy-side gate (especially item 6, documented catalyst) is being applied correctly vs over-conservatively. The correct answer may still be HOLD — but it needs explicit user-level validation after a third consecutive zero week.
**Rule change**: None. Flag to user for gate calibration review if week 3 is also zero trades.

## 2026-06-02 — Conditional trade plans require decision documentation

**Context**: June 2 pre-market identified XOM as a legitimate buy candidate, conditional on JOLTS (10:00 AM ET). Pre-market research was excellent — all 9 gate checks documented. But neither the JOLTS result nor the XOM decision (execute, defer, or abort) was documented in TRADE-LOG or EOD snapshot. The EOD says "no trades" with no explanation.
**Insight**: A conditional trade plan that produces no decision record is worse than a simple HOLD entry. The plan creates an expectation; the missing follow-through hides whether the process worked. Every conditional entry must produce a decision document by EOD: data result, condition met/failed, action taken.
**Rule change**: Flag to user: market-open routine must log the triggering data result and the resulting decision when a conditional plan exists. This is a documentation process requirement, not a strategy change.

## 2026-06-02 — stockanalysis.com is the reliable historical SPY source

**Context**: SPY daily closes have diverged across sources in every weekly review (Perplexity text estimates, EOD log +0.34% for Jun 1, Barchart -0.23%, Investing.com -0.03%). This review used stockanalysis.com historical data via Perplexity search, which returned internally consistent data matching prior confirmed reference points (May 27 $751.38, confirmed in multiple sessions).
**Insight**: stockanalysis.com historical ETF data is the most reliable reference for confirmed closes. When the Alpaca quote is unavailable for prior-day SPY, use stockanalysis.com as the primary lookup via Perplexity: "site:stockanalysis.com SPY history". Alpaca quote (bid/ask mid) is the correct real-time reference for today's close.
**Rule change**: Flag to user: adopt stockanalysis.com + Alpaca quote as the canonical SPY data combination for all reviews going forward.

## 2026-06-05 — NFP timing blocks earn their keep

**Context**: SPY fell −2.71% in the week ending June 5, with −2.58% on NFP Friday alone. The pre-NFP-day block (Jun 4) and NFP-day block (Jun 5) prevented any new positions. Portfolio held 0.00% drawdown.
**Insight**: Timing blocks (NFP day + day before, PCE day, CPI day) feel frustrating when the market is trending up, but protect capital when macro prints disappoint. One NFP miss week can offset 2-3 weeks of benchmark drift. The blocks are working as designed.
**Rule change**: None. Process confirmed correct.

## 2026-06-05 — Cash IS a position in high-event-density weeks

**Context**: Week of June 1–5 had JOLTS (Tue), ADP + ISM Services (Wed), Jobless Claims (Thu), and NFP (Fri). Every session had a blocking data event. The cumulative effect was 0 valid entry windows for 5 consecutive days.
**Insight**: When a week contains 4+ material macro prints, "cash" is the explicit position — not a failure to act. The research value came from building the XOM thesis with each print, not from placing a trade. Do not force an entry just because the week is ending.
**Rule change**: None. Strategy already covers this. Flagging the pattern as confirmed behavior.

## 2026-06-05 — Phase P&L can turn in one week; track both directions

**Context**: Cumulative phase return vs SPY was −1.13% as of June 2 (bot behind). By June 5, it was +1.84% (bot ahead). A single −2.71% SPY week reversed 2+ weeks of accumulated relative underperformance.
**Insight**: Relative performance tracking is volatile at short time horizons. Do not over-adjust strategy after 2–3 bad relative weeks, nor declare victory after 1 good relative week. The 90-day assessment is what matters.
**Rule change**: None.

## 2026-06-05 — Perpetual deferral is a strategy failure, not a virtue

**Context**: XOM thesis has been valid since June 2 (9+ pre-market sessions). Every day has produced a different blocking reason. Each individual block was defensible; the cumulative pattern of never executing a valid thesis is itself a problem.
**Insight**: If a thesis clears all 9 buy-side gate checks repeatedly but keeps hitting timing blocks, eventually the thesis ages out and the original catalyst is gone. There must be a deadline — if XOM is not entered by June 13 post-CPI, either execute with explicit reasoning or formally close the thesis with documented explanation. Open-ended deferral is not patience; it is avoidance.
**Rule change**: Flag to user: add a "thesis expiry" concept to TRADING-STRATEGY.md — if a setup clears the gate 3+ times but is blocked by timing each time, it must be executed or formally abandoned within 10 trading days of first qualifying, or the catalyst is assumed stale.

## 2026-06-12 — WTI below thesis floor is a correct gate-6 rejection

**Context**: XOM entry plan required WTI >$90. On June 12 (the first clean macro window after CPI/PPI), WTI was $86.21 — below the documented floor. Entry was blocked by gate 6 (catalyst condition fails).
**Insight**: When a thesis is explicitly conditional on a specific price level for the underlying commodity, finding the commodity below that level is not "close enough." The floor was set based on FCF economics and supply/demand reasoning; entering below it means paying for a thesis that no longer exists. Honor the floor, don't drift to "well, it's only $4 below."
**Rule change**: None. Buy-side gate 6 already covers this. Confirming it works as designed.

## 2026-06-12 — Recurring market-open documentation gaps are systemic, not isolated

**Context**: June 2 (JOLTS conditional), June 8 (NFP/WTI conditional) — both produced conditional trade plans in pre-market research; neither documented what happened at market open. This is the third consecutive week with the same gap.
**Insight**: A one-time documentation gap is an oversight. Three consecutive weeks of the same gap is a systemic process failure. The market-open routine clearly does not have a requirement to log: (a) triggering data result, (b) condition met/failed, (c) action taken. Until this is fixed at the process level, conditional trade plans are unfalsifiable.
**Rule change**: Flag to user (5th escalation): market-open routine must log the decision record when a conditional plan exists. Cannot be fixed by the agent — requires process/orchestration change.

## 2026-06-12 — Geopolitical oil premiums can reverse in days; do not treat them as structural

**Context**: The Iran war thesis drove WTI from ~$87 (June 1) to $93–98 (June 8–9) on supply disruption fears. By June 12, WTI had fallen to $86 on US-Iran deal signals and partial Hormuz reopening pricing. A ~$9/bbl swing in 3 trading days.
**Insight**: Geopolitical premiums are fragile thesis drivers. When the primary thesis catalyst is geopolitical (supply disruption risk premium rather than fundamental demand), the thesis can evaporate overnight on a ceasefire rumor or a diplomatic signal. Build in a wider safety margin for geopolitical-driven entries, or require confirmation that the supply disruption is structural (e.g., confirmed physical damage to infrastructure, not just political tension).
**Rule change**: Flagging for user: consider whether future geopolitical-premium theses should require WTI above a higher floor ($92–95 vs $90) to provide more buffer before the thesis breaks. No unilateral change.

## 2026-06-21 — Honoring hard thesis deadlines prevents worse outcomes

**Context**: XOM thesis reached Day 10 on June 15. WTI was $80.73 — $9 below the $90 floor. Thesis was formally abandoned. WTI continued falling to ~$74 by June 18. Had we entered XOM on June 15, we would have been down ~7%+ within days.
**Insight**: The 10-day thesis expiry rule works. When you set a deadline, honor it. The temptation to say "maybe next week" is always present; the rule prevents it. A thesis that has been deferring for 10+ sessions due to timing blocks is an old thesis — the catalyst has either played out or evaporated.
**Rule change**: None. This confirms the lessons.md 2026-06-05 "perpetual deferral" entry. Expiry rule is working correctly.

## 2026-06-21 — FOMC dot plot changes the macro regime; update sector screening accordingly

**Context**: Warsh FOMC June 17: held at 3.50–3.75% but hawkish shift — median dot raised to 3.8%, 9/19 dots expect ≥1 hike in 2026, easing language dropped. Market now pricing possible Oct 2026 rate hike.
**Insight**: A single FOMC meeting can change the rate regime for months. The sector priority list (Energy, Industrials, Staples) was calibrated for "hold steady / higher for longer is fine." In a possible-hike environment, Financials/banks (NIM expansion) become more viable; long-duration growth and rate-sensitive sectors (XLRE, XLU) face additional compression. Update sector screening after each FOMC.
**Rule change**: Flag for user: sector priority list should be reviewed after each FOMC meeting with material language shift. No unilateral change.

## 2026-06-21 — Build the post-block pipeline during the block, not after

**Context**: Week of June 15–18 (FOMC week): all individual decisions were correct but the pipeline was empty when the block cleared. Entered the week with KR and ACN as potential candidates; both failed entry conditions. Exited the week with zero candidates.
**Insight**: Blocking periods (CPI week, FOMC week, NFP week) are research windows. The first session after a block should be executing a pre-built candidate, not starting research from scratch. If the blocking period ends with no candidates, the first clean session adds days to an already-long cash streak.
**Rule change**: Flag for user: consider requiring the agent to screen for 2–3 post-block candidates during each blocking period (i.e., run a sector screen on the day of the block event, when no trade can be placed anyway). No strategy change — operational improvement only.

## 2026-06-28 — Market-open documentation failure cost a real entry

**Context**: GNRC cleared all 9 gate checks on June 22. Pre-market set $293 as the entry threshold. GNRC opened at approximately $279 — well within range. No market-open routine executed; no decision record was created. The opportunity was missed not due to a strategy rule but due to process failure.
**Insight**: The gap between "pre-market plan" and "market-open execution" is where trades actually happen or don't. A pre-market research entry without a corresponding market-open decision record is unfalsifiable — we can never know if the entry would have been correct. When GNRC subsequently never returned to $279, the opportunity cost became permanent.
**Rule change**: Flag to user (6th escalation): the market-open routine must produce a timestamped log entry for every session where a conditional trade plan exists: (a) triggering data result, (b) condition met/failed, (c) action taken. This is a systemic process failure that has now recurred 4 consecutive weeks. Cannot be fixed by the agent — requires orchestration change.

## 2026-06-28 — Four consecutive market-open failures is systemic, not incidental

**Context**: June 2 (JOLTS conditional), June 8 (NFP/WTI conditional), June 22 (GNRC conditional), June 25–26 (GNRC/VIX conditional) — four consecutive weeks with conditional trade plans that produced zero market-open decision records.
**Insight**: One missed documentation is an oversight. Two is a pattern. Four in a row is a broken process. The agent cannot self-fix this; it requires the orchestration layer (cron trigger, session initialization) to guarantee a market-open routine fires every day a conditional plan exists. Without it, every gate-passing thesis is silently skipped, and the trade log says "HOLD" with no audit of whether the entry condition was reached.
**Rule change**: None (cannot change strategy unilaterally). Flagging as a critical process gap requiring user intervention in the scheduling/trigger configuration.

## 2026-06-28 — High-multiple stocks require tighter entry conditions in hawkish rate regimes

**Context**: GNRC was P/E ~86× at the time of analysis. PCE came in at 4.1% headline (hottest since 2023), driving ~80% Sep 2026 rate hike probability. The stock fell from ~$295 (June 23) to ~$279 (June 22 open) to a ~$290 PCE-day spike before pulling back. The $293 threshold was set before the PCE print confirmed the macro picture.
**Insight**: High-multiple growth stocks (P/E > 60×) compress faster than the market in hawkish environments because their valuation is disproportionately sensitive to the risk-free rate. When PCE confirms a hawkish regime, the correct response is to tighten entry thresholds (not loosen them) and require a larger margin of safety. A $293 threshold on a $86× P/E stock with PCE at 4.1% is aggressive, not conservative.
**Rule change**: Flag for user: consider adding a screen condition for hawkish-rate environments — stocks with P/E > 50× require entry price ≥ 5% below the initial threshold set, or the thesis must explicitly include rate-sensitivity analysis. No unilateral change.

## 2026-07-03 — Broken-catalyst-vs-discount reasoning validated a second time

**Context**: GNRC beat Q1 EPS by 35% on Jul 1 but sold off −7.3–7.7%, then fell another −6.3–7.3% on Jul 2 (two consecutive post-earnings-beat selloffs). Both days, the agent explicitly declined to buy the dip, reasoning it was a broken catalyst (AI-capex-ROI skepticism spreading, same pattern as Broadcom Jun 30) rather than a discount.
**Insight**: Two consecutive down days on an earnings beat is strong, falsifiable evidence the market is repricing the thesis, not offering a bargain. This confirms the 2026-06-28 lesson under live conditions — a good beat that the market still sells is information, not noise.
**Rule change**: None. Confirms existing sell-side logic ("thesis materially damaged = exit") applies equally to entry decisions. Buy-side gate already covers this via catalyst documentation (item 6).

## 2026-07-03 — Market-open documentation gap obscured a genuinely live entry window

**Context**: On Jun 30, pre-market research set explicit entry conditions for GNRC (price < $289, VIX < 21, no negative news at 9:45 AM ET). GNRC opened pre-market at $282.71 — inside the valid window. No market-open decision (execute or skip, and why) was ever logged. This is the same gap first flagged June 2, now recurring across a 3rd distinct week (Jun 2/8, Jun 22/26, Jun 30) over a month unresolved.
**Insight**: This is not a hypothetical near-miss — GNRC was actually tradeable at the documented threshold. Whether the eventual outcome (GNRC fell ~13% over the next two days) would have made this a stopped-out loser or a win is unknowable, and that unknowability is the real cost: it means the market-open execution layer cannot be audited, learned from, or improved regardless of outcome.
**Rule change**: Flag to user (7th+ escalation): market-open routine must log the triggering condition check and decision every day a conditional plan exists. Cannot be fixed by the agent alone — requires an orchestration-level guarantee that the routine fires and writes a record.

## 2026-07-03 — Passive phase-lead narrows on SPY rallies, confirming it isn't earned alpha

**Context**: Phase lead vs SPY (bot flat since May 27 launch, SPY down from its launch-day level) narrowed from +2.29% (week of Jun 28) to +0.88% this week, entirely because SPY rallied +1.45% while the bot held 100% cash with zero offsetting risk avoided.
**Insight**: The 2026-06-05 lesson ("phase P&L can turn in one week") is confirmed operating in both directions now — the lead shrinks on up-SPY weeks just as it grew on down-SPY weeks. It has never been a function of agent-generated returns, only of where SPY happens to sit relative to the arbitrary May 27 launch date.
**Rule change**: None. Restating for emphasis: the mission ("beat SPY over 90 days") cannot be satisfied by a lead that is purely a launch-date artifact — the bot needs to actually execute trades and generate real returns before the 90-day mark, not just avoid losses.

## 2026-07-05 — Renamed lessons.md to LESSONS.md

**Context**: File naming inconsistency (`memory/lessons.md` lowercase vs `LESSONS.md` referenced everywhere in CLAUDE.md and TRADING-STRATEGY.md) was flagged in 8 consecutive weekly reviews starting 2026-05-27, with no action taken.
**Insight**: This was a pure filesystem/naming fix, not a strategy change, and within the agent's authority to correct directly rather than defer indefinitely to the user.
**Rule change**: None — renamed the file this session. All future sessions should reference `memory/LESSONS.md`.
