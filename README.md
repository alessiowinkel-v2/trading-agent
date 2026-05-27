# Trading Agent

An autonomous, cloud-scheduled trading agent built on Claude Code Routines. Paper trading, fundamentals-driven, designed to beat the S&P 500 over 90+ days with strict discipline before any real-money graduation.

## What this is

- 4 weekday routines + 1 weekly Friday review, all running on Claude Code cron
- Reads state from markdown files in `memory/`, writes back at the end of each run
- Git is the memory: every routine clones, runs, commits, pushes, exits
- API access via three wrapper scripts (`alpaca.sh`, `perplexity.sh`, `notify.sh`)
- Hard kill switches enforced before any trade
- Paper trading until explicit graduation criteria are met

## What this is NOT

- Not financial advice
- Not a backtested strategy
- Not a guarantee of returns
- Not a substitute for understanding what you own

## Layout

```
.
├── CLAUDE.md                   # Agent standing instructions (auto-loaded)
├── README.md                   # This file
├── STRESS_TEST.md              # Checklist before going autonomous
├── env.template                # Local .env template (cloud uses routine env vars)
├── .gitignore                  # Excludes .env, PAUSED.flag
├── memory/                     # Agent state — committed to main
│   ├── TRADING-STRATEGY.md     # Rulebook
│   ├── KILL-SWITCHES.md        # Hard halts
│   ├── TRADE-LOG.md            # Every trade + daily EOD snapshots
│   ├── RESEARCH-LOG.md         # Daily pre-market research
│   ├── LESSONS.md              # Accumulated learnings
│   ├── WEEKLY-REVIEW.md        # Friday self-evaluations
│   ├── PROJECT-CONTEXT.md      # Mission and constraints
│   └── notifications/          # Local notification fallback log
├── routines/                   # Cloud routine prompts
│   ├── 01_pre_market.md
│   ├── 02_market_open.md
│   ├── 03_midday.md
│   ├── 04_daily_summary.md
│   └── 05_weekly_review.md
└── scripts/                    # API wrappers — never curl directly
    ├── alpaca.sh
    ├── perplexity.sh
    └── notify.sh
```

## Setup

### 1. Accounts
- Alpaca paper trading: `https://app.alpaca.markets/paper/dashboard/overview`
- Perplexity API: `https://www.perplexity.ai/settings/api`
- (Optional) ClickUp for notifications — local file fallback works fine without

### 2. Make scripts executable (once)
```bash
chmod +x scripts/*.sh
```

### 3. Create Claude Code remote environment named `trading` with:
- Network access: full
- Environment variables:
  - `ALPACA_API_KEY` (required)
  - `ALPACA_SECRET_KEY` (required)
  - `ALPACA_ENDPOINT` = `https://paper-api.alpaca.markets/v2` (required — pins us to paper)
  - `PERPLEXITY_API_KEY` (required for research)
  - `PERPLEXITY_MODEL` = `sonar` (optional, defaults to sonar)
  - `CLICKUP_API_KEY`, `CLICKUP_WORKSPACE_ID`, `CLICKUP_CHANNEL_ID` (optional — skip for Phase 1)

### 4. Connect this GitHub repo to the environment.

### 5. Create 5 routines in Claude Code desktop, one per file in `routines/`. For each:
- Paste the prompt from inside the code block (verbatim)
- Set the cron and timezone (America/New_York)
- Enable "Allow unrestricted branch pushes"

### 6. Stress test before letting it run autonomous. See `STRESS_TEST.md`.

## Phase 1 (paper) → Phase 2 (real money) graduation

Defined in `memory/TRADING-STRATEGY.md`. All criteria must be met after 90+ days before any real money. Real-money phase starts with $500-$2000, NOT scaled-up paper.

## Operational rules

- Memory files grow. Rotate `TRADE-LOG.md` to archive when over ~1000 lines.
- Test every routine manually after any prompt change.
- Review `memory/notifications/notifications.md` daily for the first 2 weeks.
- Read `memory/WEEKLY-REVIEW.md` carefully — that's where you decide if the agent is trustworthy.
- If the agent ever does something that violates a hard rule, pause it (create `memory/PAUSED.flag`) and review before resuming.

## Pause / resume

To pause the agent:
```bash
echo "paused: <reason>" > memory/PAUSED.flag
git add memory/PAUSED.flag && git commit -m "pause: <reason>" && git push
```

To resume:
```bash
git rm memory/PAUSED.flag
git commit -m "resume" && git push
```
