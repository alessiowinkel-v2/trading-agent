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
