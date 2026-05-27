# Pre-Market Routine

**Schedule**: 6:00 AM ET, Monday-Friday
**Cron**: `0 6 * * 1-5` (timezone: America/New_York)
**Purpose**: Research. No trades will be placed in this routine.

---

## Prompt

You are running the pre-market routine. Today's date is (let the agent fill in via shell).

### Step 1: Load context
Read in order:
1. `memory/kill_switches.md` — check if any are active
2. `memory/strategy.md`
3. `memory/portfolio.md`
4. The last 20 entries of `memory/trade_log.md`
5. `memory/lessons.md`

If any kill switch is active, log it and exit. Do not proceed.

### Step 2: Get market context
Using Perplexity API (key in `PERPLEXITY_API_KEY` env var), research:
- Overnight market news that could move broad indices
- Any earnings announcements TODAY for stocks in our portfolio
- Any macro events today (Fed, CPI, jobs report, etc.)

Use focused queries, don't burn tokens on tangential reading.

### Step 3: Review open positions
For each currently held position, briefly note:
- Any material news?
- Has thesis changed?
- Are we approaching any exit conditions from the original trade log entry?

### Step 4: Identify candidate trades (if any)
Following strategy.md buy criteria strictly:
- Note 0-3 candidates for potential entry today
- For each, draft a tentative 5-point thesis (Thesis, Catalyst, Risk, Size, Exit)
- These are DRAFTS — they will be validated at market open before any actual trade

It is completely fine to identify zero candidates. Most days that is the right answer.

### Step 5: Write the plan
Create `memory/daily_plan/YYYY-MM-DD.md` with:
- Market context summary (3-5 sentences)
- Position status (any concerns?)
- Candidate trades (with 5-point reasoning each)
- "Do nothing" recommendation if no candidates

### Step 6: Commit and exit
Commit changes with message: `pre-market YYYY-MM-DD`. Do not push if no changes.

DO NOT place any trades in this routine. The next routine (market open) will validate the plan against fresh data and execute.

### Notification
Write to `memory/notifications/YYYY-MM-DD-0600.md`:
- Kill switch status
- Number of candidates identified
- Top-of-mind risk for today
