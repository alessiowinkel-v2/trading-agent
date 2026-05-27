# Kill Switches

**Read this file FIRST every routine. If ANY condition is active, do not trade. Notify the user.**

## Automatic kill switches (the agent checks these itself)

### KS-1: Daily drawdown
If portfolio is down more than **3%** from yesterday's close → no new trades today, only protective sells allowed.

### KS-2: Weekly drawdown
If portfolio is down more than **7%** from the prior Friday's close → halt all trading until weekly review.

### KS-3: Total drawdown
If portfolio is down more than **15%** from starting capital ($10,000) → halt all trading. Require manual user reset.

### KS-4: Position breach
If any single position exceeds 18% of portfolio (3% buffer over the 15% limit) → trim the position immediately. No new buys until resolved.

### KS-5: Excessive activity
If you've placed more than 3 trades today, or more than 8 this week → no new trades.

### KS-6: API failure
If Alpaca returns errors on more than 2 attempts → do not trade this session. Log and notify.

### KS-7: Stale data
If quote data is more than 15 minutes old, or last portfolio update was more than 24 hours ago → do not trade. Re-fetch first.

### KS-8: Memory file corruption
If `portfolio.md` cannot be parsed, or shows impossible values (negative cash without margin, position size > 100%) → halt and notify.

## Manual kill switches (user sets these)

The user can disable trading by creating a file at `memory/PAUSED.flag` with any content. If this file exists, the agent must:
1. Not place any trades (including sells, unless `memory/PAUSED.flag` contains the word "SELLS_OK")
2. Continue to run risk checks and write to logs
3. Notify the user that paused state is active

## What "halt trading" means

- No buys
- No sells UNLESS the sell is a protective stop already planned in the trade log
- Continue research and logging
- Continue updating portfolio.md (just don't change positions)
- Write a clear notification explaining which kill switch fired
- DO NOT try to "work around" a kill switch by, e.g., placing smaller trades or splitting orders

## Reset procedure

Kill switches reset:
- KS-1: at next day's market open IF the drawdown has recovered
- KS-2: at the next weekly review IF the drawdown has recovered
- KS-3: manual user action only (remove this section and add reset note in lessons.md)
- KS-4: automatically once position is trimmed back under 15%
- KS-5: at midnight ET
- KS-6, KS-7, KS-8: when the underlying issue is resolved

## Currently active kill switches

(none — populate as triggered, clear when reset)
