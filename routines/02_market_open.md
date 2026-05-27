# Market Open Routine

**Schedule**: 9:45 AM ET, Monday-Friday (note: 15 min after open, deliberately)
**Cron**: `45 9 * * 1-5` (timezone: America/New_York)
**Purpose**: Execute the pre-market plan, if conditions still hold.

---

## Prompt

You are running the market open routine.

### Step 1: Load context
Read in order:
1. `memory/kill_switches.md` — exit if any active
2. `memory/strategy.md`
3. `memory/portfolio.md`
4. `memory/daily_plan/YYYY-MM-DD.md` (today's plan from pre-market)
5. Last 10 entries of `memory/trade_log.md`

If today's daily plan doesn't exist (pre-market routine didn't run), do NOT trade. Log this and exit.

### Step 2: Sync portfolio with Alpaca
Hit Alpaca's `/v2/account` and `/v2/positions` endpoints. Compare with `memory/portfolio.md`.
- If they disagree materially, trust Alpaca and update the file. Log the discrepancy.
- Use env vars `APCA_API_KEY_ID`, `APCA_API_SECRET_KEY`.
- Base URL for paper: `https://paper-api.alpaca.markets`

### Step 3: Run kill switch checks
Using the freshly synced data:
- Calculate daily, weekly, total drawdown
- Check position concentration limits
- Check trade count limits
- Check API health (you just used it, so this should be fine)

If any kill switch triggers, write to `memory/kill_switches.md` "Currently active" section and exit without trading.

### Step 4: Validate planned trades against current data
For each candidate trade from the daily plan:
- Get current quote via Alpaca
- Has the price moved more than 2% from the plan's reference price? If so, re-evaluate the thesis. The original setup may no longer apply.
- Are we still inside strategy.md rules (position limits, sector caps)?
- Are we past 10:00 ET (avoid the first 30 min)? If still before 10:00, wait by sleeping/exiting; next routine will pick up.

### Step 5: Execute valid trades
For each trade that survives validation:
- Place a limit order via Alpaca's `/v2/orders` endpoint
- Limit price: current ask + 0.1% for buys, current bid - 0.1% for sells (don't chase)
- Time in force: `day`
- Wait up to 60 seconds for fill confirmation
- If not filled, cancel and log "not filled, will not chase"

### Step 6: Document every action
For each filled trade, append a FULL entry to `memory/trade_log.md` with all 5 reasoning points + kill switch check.

### Step 7: Update portfolio
Update `memory/portfolio.md` with new positions, new cash, new total value.

### Step 8: Commit and notify
Commit: `market-open YYYY-MM-DD: N trades placed`.
Write `memory/notifications/YYYY-MM-DD-0945.md` with summary.

### Hard rules
- NEVER place a market order. Always limit orders.
- NEVER trade between 9:30-10:00 ET.
- NEVER override a kill switch.
- If anything feels off, write a note and exit without trading. The cost of not trading is zero.
