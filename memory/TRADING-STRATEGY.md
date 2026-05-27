# Trading Strategy

## Mission
Beat the S&P 500 over the 90-day evaluation window with LOWER max drawdown.
**Phase 1: Paper trading.** Graduation criteria below must be met before real money.

## Capital & Constraints
- Starting capital: $10,000 (paper)
- Platform: Alpaca paper trading (`paper-api.alpaca.markets`)
- Instruments: Stocks ONLY — no options, no crypto, no leveraged ETFs
- PDT limit: 3 day trades per 5 rolling days (account < $25k)

## Investment Philosophy
- Fundamentals over technicals
- Concentration is fine, recklessness is not (5-10 positions, not 50, not 2)
- Time in market > timing the market
- Boring is good — if a thesis is "AI hype" or "meme momentum," it's not a thesis
- Patience > activity. Zero trades in a week can be correct.

## Core Rules (HARD LIMITS — non-negotiable)

| Rule | Limit |
|------|-------|
| NO OPTIONS | ever, period |
| Max open positions | 6 |
| Max per position | 15% of equity |
| Max sector concentration | 35% of equity |
| Min position size | 2% (no token positions) |
| Min cash reserve | 5% |
| Target deployment | 75-85% |
| Max new trades per week | 3 |
| Max trades per day | 3 |

## Universe (tradeable)
US-listed common stocks and ETFs with:
- Market cap > $2B
- Average daily volume > $10M
- Listed on NYSE or NASDAQ

## Do NOT Trade
- Options, futures, crypto
- Leveraged ETFs (2x, 3x, inverse)
- OTC / pink sheet stocks
- IPOs in their first 90 days
- Stocks with pending merger/acquisition deals
- Anything in the blacklist section of `memory/LESSONS.md`

## Buy-Side Gate (ALL must pass before any order)

1. Total positions after this fill ≤ 6
2. Trades placed this week (including this one) ≤ 3
3. Position cost ≤ 15% of account equity
4. Position cost ≤ available cash
5. PDT day-trade count leaves room (under 3 on sub-$25k account)
6. Specific catalyst documented in today's `RESEARCH-LOG.md` entry
7. Instrument is a stock (not an option, not anything else)
8. No earnings announcement within next 5 trading days
9. No kill switch currently active

If ANY check fails, skip the trade and log the reason. There is no penalty for skipping; significant penalty for trading without conviction.

## Entry Checklist (document ALL before placing)

1. **Thesis** (2-3 sentences): why this business, why now?
2. **Catalyst**: specific reason for timing
3. **Risk**: what would make this wrong?
4. **Sector momentum**: is the sector with us or against us?
5. **Size**: shares × price, % of equity (must respect limits)
6. **Stop level**: 7-10% below entry
7. **Target**: minimum 2:1 risk/reward
8. **Exit plan**: both win and loss conditions

## Sell-Side Rules

Evaluated at midday scan and opportunistically:
- Unrealized loss ≤ -7% → close immediately (hard stop, no exceptions)
- Down -8% AND thesis materially damaged → close
- Up +15%+ → tighten trailing stop to 7%
- Up +20%+ → tighten trailing stop to 5%
- Up +30%+ AND fundamentals deteriorating → close
- Sector has 2 consecutive failed trades → exit ALL positions in that sector
- Position held > 12 months AND original thesis played out → close
- Never tighten a stop within 3% of current price
- NEVER move a stop down

## When NOT to Trade

- First 30 min of session (9:30-10:00 ET) — too volatile
- Last 15 min (3:45-4:00 ET) — too thin
- Day of FOMC announcement
- Day before / day of major releases (CPI, jobs) unless thesis specifically includes them
- When no clear thesis exists ("feels like a good time" is not a thesis)

## Cadence

| Routine | Time (ET) | Purpose |
|---------|-----------|---------|
| Pre-market | 6:00 AM | Research only, no trades |
| Market-open | 9:45 AM | Execute planned trades (15 min after open, deliberately) |
| Midday | 12:00 PM | Risk check, cut losers, tighten stops |
| Daily summary | 3:30 PM | EOD snapshot, performance vs SPY |
| Weekly review | 4:30 PM Friday | Self-evaluation, lessons, graduation tracking |

## Graduation Criteria for Phase 2 (real money)

ALL of these must be true after at least 90 days of paper trading:

- [ ] System ran without manual intervention for 30+ consecutive trading days
- [ ] Max drawdown stayed under 15%
- [ ] Beat OR matched SPY total return (within 2%)
- [ ] No kill-switch breaches that the agent failed to catch itself
- [ ] User has read every trade log entry and agrees the reasoning was sound
- [ ] Memory files still functional (trade log under context budget, rotated if needed)
- [ ] At least one drawdown of 5%+ was handled correctly (this tests behavior under stress)

If graduated: Phase 2 starts with **$500-$2000 of real money**, NOT scaled-up paper amount. Real-money endpoint: `https://api.alpaca.markets/v2`. Update `ALPACA_ENDPOINT` env var only after explicit user confirmation.

## Strategy Drift Detection

The agent may NOT modify this file unilaterally. If a rule seems wrong based on accumulated evidence:
1. Flag it in the weekly review under "Adjustments for Next Week"
2. Provide specific data (which trades, what outcomes)
3. Wait for user approval before any change
4. If approved, user changes the file directly

Lessons learned go in `LESSONS.md`. Strategy changes require human review.
