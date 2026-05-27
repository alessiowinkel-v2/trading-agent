# Market Close Routine

**Schedule**: 3:30 PM ET, Monday-Friday
**Cron**: `30 15 * * 1-5` (timezone: America/New_York)
**Purpose**: End-of-day reconciliation, no new positions.

---

## Prompt

You are running the close routine. NO NEW POSITIONS in this routine — period. Sells allowed only for existing planned stops.

### Step 1: Load context
Standard file reads.

### Step 2: Sync with Alpaca
Pull final state of the day. This is what gets recorded.

### Step 3: Execute any remaining protective stops
If a position hit -15% and somehow wasn't sold midday → sell now via limit order.
Do NOT initiate any other trades.

### Step 4: Compute the day's performance
- Portfolio value at close vs prior close → daily return
- Pull SPY's daily return from Alpaca (or Perplexity if needed) → benchmark return
- Cumulative performance vs benchmark since start

### Step 5: Update portfolio.md fully
- Performance table: add today's row
- Sector allocation: recalculate
- Notes: any meaningful changes

### Step 6: Brief daily summary
Write `memory/notifications/YYYY-MM-DD-1530.md` with:
- Total value, daily change, vs SPY
- Trades made today (count + summary)
- Active kill switches
- Top concern for tomorrow (one sentence)

### Step 7: Commit & push
Commit: `close YYYY-MM-DD: $X.XX (Y% vs SPY's Z%)`.
Push to remote so the morning routine can pick up the state.

### Step 8: Reset daily counters
Kill switch KS-5 (excessive activity) daily counter resets at midnight — no action needed, just note that tomorrow is a fresh count.
