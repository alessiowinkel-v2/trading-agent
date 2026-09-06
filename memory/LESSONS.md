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

## 2026-07-10 — Mechanical/passive-flow events are not fundamentals catalysts

**Context**: SPCX's forced Nasdaq-100 inclusion (Jul 7) was a real, large ($4.3-10B) mechanical buying event but was correctly rejected as a trade candidate — it's index-mechanics-driven, not company-fundamentals-driven.
**Insight**: Large dollar flows alone don't make something a thesis. Passive-flow/index-mechanics events belong in the same "not a thesis" bucket as meme momentum and AI hype, even when the flow size is large and the catalyst is genuinely dated.
**Rule change**: None. Buy-side gate item 6 (documented catalyst) already covers this; confirming correct application under a new catalyst type.

## 2026-07-10 — Passive phase-lead vs SPY has now reversed to bot-behind

**Context**: Bot's cumulative phase P&L vs SPY was +0.88% ahead as of the Jul 3 review (SPY still below its May 27 launch close of $751.38). By Jul 10, SPY closed back above $751.38, flipping the comparison to bot ~0.3-0.5% behind for the first time since the week of Jun 5.
**Insight**: The 2026-06-05 and 2026-07-03 lessons about the passive lead being an artifact of SPY's position relative to the launch date, not earned alpha, are now confirmed operating in both directions across a full cycle (behind → ahead → behind). With 31 trading days and 0 trades, the bot has generated zero information about its own edge — only about SPY's path.
**Rule change**: None. Restating for emphasis given half the 90-day window has now elapsed with zero trades in either direction.

## 2026-07-10 — Same-day EOD arithmetic must be checked against its own cited prices, not just cross-checked against other sources

**Context**: The Jul 8 EOD snapshot logged a day change of −0.48% while citing $747.71 (prior close) and $741.00 (today's close) — those two figures imply roughly −0.90%, not −0.48%. This is distinct from the long-standing cross-source divergence problem: the entry's own numbers don't agree with each other.
**Insight**: Cross-checking SPY closes against multiple external sources doesn't catch an error where the stated percentage simply wasn't computed from the two prices given in the same entry.
**Rule change**: Flag for user: EOD routine should derive the day-change percentage directly from the two closing prices it cites, as a final arithmetic check, before committing the entry. Operational fix only.

## 2026-07-24 — Zero-trade streak has cleared the majority-of-window threshold

**Context**: 41 trading days / ~58 calendar days elapsed since launch (May 27) with 0 trades — roughly 64% of a typical 90-calendar-day evaluation window, with more trading days already elapsed than remain.
**Insight**: Individual HOLD decisions have been consistently well-reasoned (this week's WTI $90-floor near-touch and reversal, Jul 23-24, is a clean example), but the cumulative absence of trade history means the actual mission — beat SPY through real agent decisions — has never been tested. Past this point in the window, the graduation criteria requiring an actual track record (matched/beat SPY through real action, handled a 5%+ drawdown correctly) risk becoming unsatisfiable purely from running out of calendar, not from any specific bad decision.
**Rule change**: Flag to user: explicitly decide whether the current buy-side gate calibration is intended to remain this conservative for the rest of the window, given there are now fewer trading days left than have already elapsed. No unilateral change.

## 2026-07-24 — Cited artifact ages must be re-derived from source each time, not carried forward

**Context**: Research-log entries from Jul 21-24 stated the root-level `PAUSED.flag` had been "unresolved for 10+ weeks." `git log --follow --diff-filter=A -- PAUSED.flag` shows it was first committed 2026-06-26 — under 5 weeks before the Jul 24 review, not 10+.
**Insight**: A qualitative age claim was repeated and inflated across sessions without being re-checked against the actual git history or file mtime. This is the same failure class as the 2026-07-10 lesson on same-day EOD arithmetic — a stated figure that doesn't hold up against its own source, just applied to a different kind of claim (elapsed time rather than a percentage).
**Rule change**: Flag for user: when re-citing an unresolved artifact's age in any log entry, derive it fresh from `git log` or file mtime that session rather than repeating prior phrasing verbatim. Operational fix only.

## 2026-07-17 — Re-flagging a candidate is not the same as screening it

**Context**: A Financials/bank-earnings breakout thesis was identified Jul 15 as "the top candidate to screen once the macro block clears." It was then repeated, still unscreened, on Jul 16 and Jul 17 — three consecutive sessions with no specific ticker, entry, stop, or target ever documented.
**Insight**: This is a distinct failure mode from the long-standing market-open documentation gap (which fails to log a decision on an existing conditional plan). Here, the conditional plan itself was never built past a one-line flag — the thesis went stale from neglect, not from a timing block or a legitimate gate-6 rejection.
**Rule change**: Flag for user: consider requiring that any candidate flagged as "top thing to screen next session" produce an actual gate-checked pass/fail writeup (ticker, entry, stop, target) within one session of being raised, rather than permitting a recurring one-line re-flag. No unilateral change — operational suggestion only.

## 2026-07-31 — "Re-derive fresh from source" still needs its own verification

**Context**: The 2026-07-24 lesson required re-deriving the root-level `PAUSED.flag` age from git history each session rather than repeating stale phrasing. Every pre-market session from Jul 27-31 did attempt that re-derivation — and produced four different wrong answers (2026-06-26, 2026-06-29, 2026-06-29, 2026-06-30) across five entries. The actual and only commit adding the file, verified this session via `git log --diff-filter=A -- PAUSED.flag`, is **2026-07-02**.
**Insight**: A procedural fix ("check the source each time") is not self-correcting if the command is misremembered, misread, or paraphrased rather than copied directly from its output. This is a new failure distinct from the one it was meant to fix — the earlier lesson was about not carrying forward stale claims; this one is about a "fresh" check still being wrong.
**Rule change**: Flag for user: when a log entry cites a git-log-derived fact, the actual command output should be pasted or closely quoted, not paraphrased from memory of a previous session's result. No unilateral strategy change — operational fix only.

## 2026-07-31 — Runway checkpoint escalated: most of the 90-day window is now gone

**Context**: 46 trading days / 65 calendar days elapsed since launch (2026-05-27) against a 90-calendar-day window closing approximately 2026-08-25. Roughly 25 calendar days (~15-17 trading days) remain. Zero trades placed in either direction throughout.
**Insight**: The 2026-07-24 lesson flagged crossing the halfway point. One week later, the remaining runway has shrunk to roughly 3 weeks. Past this point, the graduation criteria requiring an actual track record (beat/match SPY through real action, handle a 5%+ drawdown correctly) risk going entirely untested — not because of any bad decision, but purely from elapsed calendar time.
**Rule change**: Flag for user (escalated): decide explicitly, this week, whether to accept the current gate calibration and the likelihood the mission goes untested, loosen the gate for the remaining window with specific reasoning, or extend the evaluation window. No unilateral change.

## 2026-08-07 — Runway checkpoint critical: phase P&L moved outside 2% SPY tolerance in a single week

**Context**: 51 trading days / 72 calendar days elapsed since launch (2026-05-27) against a 90-calendar-day window closing ~2026-08-25 — only ~18 calendar days (~12 trading days) remain. SPY gained +3.51% the week of Aug 3-7 (its best week since April, on cooling jobs data) while the bot held 0.00%, flipping cumulative phase P&L from a nominal lead to −2.91% behind — outside the 2% graduation "matched or beat" tolerance for the first time.
**Insight**: A single strong SPY week can erase weeks of nominal "lead" built purely from cash sitting still while SPY dipped below its launch-date level (per the 2026-07-03/07-10 lessons on this being an artifact, not earned alpha). With the runway now down to ~12 trading days and zero trades in either direction, the "beat/match SPY" and "handle a 5%+ drawdown" graduation criteria are at serious risk of closing untested.
**Rule change**: Flag for user (most urgent runway flag yet): decide explicitly this week whether to accept the current gate calibration given the shrinking window, loosen the gate with specific reasoning, or extend the evaluation window. No unilateral change.

## 2026-08-07 — A "converged" answer across sessions is not the same as a correct answer; and check a file's provenance, not just its date

**Context**: The root-level `PAUSED.flag` age was re-derived from `git log` five different (wrong) ways across the weeks ending 2026-07-31 and 2026-08-07 (06-26, 06-29, 06-30, 07-05, 07-06), before the last two sessions of this week (Aug 6, Aug 7) both landed on 2026-07-07. Verifying fresh this session via `git log --follow --diff-filter=A --format='%H|%ad|%s' -- PAUSED.flag` shows the true first (and only) commit is `fcc89a4`, dated **2026-07-08** — one day later than both "converged" answers — and its message is "clean up duplicate notification entry (shell variable interpolation bug)," meaning the file was added incidentally inside an unrelated cleanup commit, not created as a deliberate pause action.
**Insight**: Two sessions agreeing on a date reduces variance but is not proof of correctness — the underlying command output still needs to be checked digit-by-digit against the claim. Separately, the recurring instruction to "re-derive fresh from git log" only ever asked for the date; nobody checked what the commit that added the file actually was, which would have revealed the file's likely-accidental origin weeks earlier.
**Rule change**: Flag for user: the root-level `PAUSED.flag` is very likely test debris from an unrelated commit, not an intentional pause — recommend deleting it or confirming its purpose, since it has consumed several sessions' worth of (still slightly wrong) date-tracking effort. No unilateral change to strategy or kill-switch files.

## 2026-08-16 — Root-level PAUSED.flag is untracked debris, not a persisted artifact

**Context**: Weekly review for week ending 2026-08-14 ran `git ls-files PAUSED.flag` (returns nothing — untracked) and `git log --all --diff-filter=A --format='%H|%ad|%s' -- PAUSED.flag` (shows one commit, `663e0964`, dated 2026-07-15, message "pre-market research 2026-07-15") for the first time, rather than only re-deriving an age from prior phrasing.
**Insight**: The file on disk today is untracked by git, meaning it is not the same persisted object every prior session was dating and could not survive an actual fresh clone. It is local session debris, not a deliberate or committed pause action. This resolves (rather than just re-derives) the multi-week thread started 2026-07-24.
**Rule change**: None to strategy. Recommend user delete the local file. Operationally: when a file repeatedly resists date-tracking across sessions, check `git ls-files` for tracked status before re-deriving dates from `git log` — an untracked file's history is not informative about its current persistence.

## 2026-08-16 — Single-candidate research pipeline risks mistaking narrow search for a quiet market

**Context**: XOM/WTI-floor has been the only buy-side candidate framework actively screened for roughly 10 consecutive weeks (since the Financials thesis was formally closed in mid-July with no replacement). Every "zero candidates" pre-market conclusion during that span checked only this one framework.
**Insight**: A gate that is applied correctly to the only candidate under consideration can still produce a systematically incomplete answer if no second candidate is being screened in parallel. This is distinct from gate-6 rejections being wrong — each rejection was individually correct — the problem is pipeline breadth, not gate calibration.
**Rule change**: Flag for user: consider requiring the pre-market routine to maintain at least one active non-Energy candidate under screen at all times, not only immediately after a prior thesis formally closes. No unilateral change — operational suggestion only.

## 2026-08-21 — 90-day evaluation window closes with zero trades ever placed

**Context**: The Aug 21 weekly review covers the last full trading week (Days 57–61) before the 90-calendar-day window closes ~2026-08-25. Every individual HOLD decision across all 61 trading days was defensible and gate-specific — including this week's hardest test, holding the XOM/WTI price floor at its narrowest-ever gap ($3.5-3.8 below $90) against Energy's best sector week in ~4 years. No single decision was wrong.
**Insight**: A gate that is applied correctly every single day can still produce a phase-level failure if it is calibrated tightly enough that it never fires once across an entire evaluation window. The runway escalation flagged in every review since 2026-07-24 has now reached its terminal state: the mission ("beat SPY through real agent decisions," "handle a 5%+ drawdown correctly") closes untested, not from any bad trade but from the gate's cumulative strictness over 90 days. Correct process and mission failure are not mutually exclusive.
**Rule change**: Flag for user (final, most consequential escalation): decide explicitly whether to treat Phase 1 as concluded on process-quality grounds alone, extend the evaluation window with a new end date, or revisit gate calibration for any future window. No unilateral change made or possible at this point — the window has already closed on trades.

## 2026-08-21 — Three non-converging "fresh verifications" of the same file in five days

**Context**: The root-level `PAUSED.flag`'s tracked-status and add-commit date were each independently "re-verified fresh" three times in five days: 2026-08-16 (LESSONS.md) concluded untracked, commit `663e0964` dated 2026-07-15; 2026-08-18 (pre-market research) found it tracked instead, commit `9225051` dated 2026-07-16; 2026-08-21 (pre-market research) re-checked again and found a third, different commit, `096736bc182f6d9646340dafc3252185c5d29a8`, dated 2026-07-21. Each was stated with full confidence as a corrected, verified answer.
**Insight**: The standing instruction to "re-derive fresh from git log rather than repeat stale phrasing" (2026-07-24 lesson) does not converge on its own even after many repetitions — this is roughly the tenth distinct re-derivation attempt since that lesson was written, and the answers are still changing, not narrowing. A recurring accuracy defect that survives multiple independent "fixes" is evidence the fix itself is inadequate, not that one more attempt will succeed.
**Rule change**: Flag for user: resolve the file directly (delete it or state its purpose once) rather than asking the agent to re-verify again. No unilateral change to strategy or kill-switch files.

## 2026-09-06 — A cadence blackout is a distinct, more severe failure than a documentation gap

**Context**: Weekly review for the week ending 2026-09-04 found that Aug 25, 26, 27, 28, and 31 (five consecutive trading days) had zero routine records of any kind — no pre-market research, no EOD snapshot, no kill-switch check. This was only discovered when the Sep 1 routine resumed and flagged it. Live Alpaca state confirmed no undetected risk materialized (equity flat, 0 positions/orders throughout), but the audit trail for that window does not exist and cannot be reconstructed.
**Insight**: Every prior process gap (the long-running market-open documentation gap, sequencing failures) left at least a partial record that could be graded and learned from. A period with zero routine execution leaves nothing — it cannot be distinguished, after the fact, from a period where a real risk event went completely unmonitored. The only reason this instance was harmless is that the market happened to be quiet and the account happened to hold no positions; the process could not have caught a problem if one had occurred.
**Rule change**: Flag for user (new, most urgent): this is a scheduling/orchestration reliability issue outside the agent's control — no in-session fix is possible. Recommend investigating why the routines silently stopped firing for 5 trading days. No unilateral change to strategy or kill-switch files.

## 2026-09-06 — Root-level PAUSED.flag provenance conclusively resolved

**Context**: Following the 2026-08-21 lesson on non-converging "fresh verifications," this session ran `git log --follow --diff-filter=A --format='%H|%ad|%s' -- PAUSED.flag` directly and is quoting its exact output: one commit, `5db43a1a`, dated 2026-07-30, message "pre-market research 2026-07-30." The file is confirmed tracked via `git ls-files PAUSED.flag`.
**Insight**: This resolves the multi-week thread of conflicting dates/tracked-status claims (2026-08-16, 08-18, 08-21) by quoting the actual command output rather than paraphrasing. The file is root-level debris added incidentally inside an unrelated commit, not a deliberate pause action — consistent with the 2026-08-07 lesson's hypothesis.
**Rule change**: None to strategy. Recommend user delete the file or state its purpose once, to stop consuming further session time on re-verification.
