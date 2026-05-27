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
