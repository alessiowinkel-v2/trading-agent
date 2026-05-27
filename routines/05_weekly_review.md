# Weekly Review Routine

**Schedule**: 4:30 PM ET, Friday
**Cron**: `30 16 * * 5` (timezone: America/New_York)
**Purpose**: Self-evaluation, lesson extraction, graduation criteria tracking.

---

## Prompt

You are running the weekly review. This is your honest report card.

### Step 1: Load full context
Read everything:
- All memory files
- Last 50 trade log entries
- All daily plans from this week
- All notifications from this week

### Step 2: Compute weekly metrics
- Portfolio value Monday open → Friday close
- Weekly return %
- SPY weekly return %
- Difference vs benchmark
- Max intraweek drawdown
- Number of trades (vs limit of 8)
- Win rate so far overall

### Step 3: Trade-by-trade honest review
For each trade made this week:
- Was the thesis followed?
- Was the size appropriate?
- Was the stop respected?
- In hindsight, would you make this trade again? Why/why not?
- DO NOT confuse outcome with process. A winning trade with bad reasoning is still a bad trade.

### Step 4: Self-grade
Grade yourself A through F on:
- **Process discipline**: Did you follow strategy.md?
- **Documentation quality**: Were trade log entries complete and honest?
- **Risk management**: Were kill switches respected?
- **Outcome** (separately, and weighted least): Did the portfolio do well?

Be harsh. A C with honest reasoning beats an A you can't defend.

### Step 5: Extract lessons
Add 0-3 new entries to `memory/lessons.md`. Focus on:
- Mistakes you can prevent next week
- Patterns you're noticing in winning/losing trades
- Strategy rules that might need refinement (flag for user, don't change unilaterally)

### Step 6: Graduation criteria check
From strategy.md Phase 2 criteria, mark each as:
- ✅ currently met
- 🟡 trending toward met
- ❌ not met

Days running counter: increment.

### Step 7: Write the full weekly report
Create `memory/weekly_reviews/YYYY-WW.md` with all of the above. This is what the user actually reads.

### Step 8: Commit & push
Commit: `weekly review YYYY-WW: grade [X]`.

### Step 9: Notification
Brief summary to `memory/notifications/YYYY-MM-DD-1630.md`:
- Week's return vs SPY
- Grade summary
- Top lesson
- Graduation criteria status

### Important
- You are reviewing yourself. Bias toward harsh, not generous.
- Do NOT modify strategy.md or kill_switches.md unilaterally. Flag suggested changes for the user instead.
- If you notice you've been drifting from strategy rules even slightly, flag it loudly.
