# Midday Routine

**Schedule**: 12:00 PM ET, Monday-Friday
**Cron**: `0 12 * * 1-5` (timezone: America/New_York)
**Purpose**: Risk management — cut losers, protect winners. Rarely opens new positions.

---

## Prompt

You are running the midday routine. This is a risk-management routine, not an entry routine.

### Step 1: Load context (same as other routines)
Read kill switches, strategy, portfolio, recent trade log, lessons.

### Step 2: Sync with Alpaca
Pull current account, positions, and quotes for all holdings.

### Step 3: Per-position check
For each open position:
- Calculate current P/L (vs entry price from trade log)
- Has it hit any sell trigger from strategy.md?
  - Down 15% from entry → SELL (hard stop)
  - Down 8% AND look up news to see if thesis is damaged → if damaged, SELL
  - Up 30%+ → check fundamentals; if deteriorating, SELL
- Trailing stop: if up 20%+, note the trailing stop level (-10% from peak)

### Step 4: Execute sells (if any)
- Limit orders only, near current bid
- Document each in trade_log.md with reasoning
- Update portfolio.md

### Step 5: Run all kill switches against new state
Recalculate drawdowns after any trades. Update kill_switches.md if any triggered.

### Step 6: Rare midday entries
Only enter a new position midday if ALL of:
- A candidate from this morning's daily_plan that didn't fill at open is now at a clearly better price (>2% better)
- All strategy rules still satisfied
- No kill switches active
- We haven't hit max trades for day/week

If yes, treat exactly like a market-open trade: full 5-point reasoning, limit order, full documentation. Otherwise, no new entries.

### Step 7: Commit and notify
Commit: `midday YYYY-MM-DD: N sells, M buys`
Notification to `memory/notifications/YYYY-MM-DD-1200.md`.

### Bias toward inaction
Most midday runs should result in zero trades. That is correct behavior. Do not invent reasons to trade.
