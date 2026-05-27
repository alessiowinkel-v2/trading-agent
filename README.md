# Trading Agent

A scheduled, agentic paper-trading system built with Claude Code Routines, Alpaca, and Perplexity.

## What this is

- 4 weekday routines + 1 weekly review
- Reads state from markdown files, writes back at end of each run
- Hard kill switches enforced in prompts
- Designed for fundamentals-driven, low-activity, beat-the-S&P approach
- Paper trading ONLY until graduation criteria met (see `memory/strategy.md`)

## What this is NOT

- Not financial advice
- Not a backtested strategy
- Not a guarantee of returns
- Not a substitute for understanding what you own

## Setup

1. Set environment variables in your Claude Code remote environment:
   - `APCA_API_KEY_ID`
   - `APCA_API_SECRET_KEY`
   - `PERPLEXITY_API_KEY`
2. Create 5 remote routines in Claude Code desktop, pointing at this repo
3. Use the cron strings and prompts from `routines/`
4. Enable "unrestricted branch pushes" in routine permissions
5. Run each routine manually with "Run Now" before letting cron take over

## Files

```
CLAUDE.md                    # Standing instructions for every run
memory/
  strategy.md                # Trading rules (the brain)
  kill_switches.md           # Hard stops (the brakes)
  portfolio.md               # Current state
  trade_log.md               # Every trade with reasoning
  lessons.md                 # What we've learned
  daily_plan/                # Pre-market plans by date
  weekly_reviews/            # Friday self-evaluations
  notifications/             # Per-run summaries
routines/
  01_pre_market.md
  02_market_open.md
  03_midday.md
  04_close.md
  05_weekly_review.md
```

## Operational notes

- Memory files will grow. Plan to rotate `trade_log.md` to an archive when it exceeds ~1000 lines.
- Test every routine manually after any prompt change.
- Review `memory/notifications/` daily for the first 2 weeks.
- Read `memory/weekly_reviews/` carefully — that's where you decide if the agent is trustworthy.
