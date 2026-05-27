# Strategy

**Status**: Paper trading. Starting capital: $10,000.
**Benchmark**: SPY (S&P 500 ETF).
**Goal**: Beat SPY total return over 3+ months, with lower max drawdown.
**Phase**: Phase 1 — Paper trading. Phase 2 (real money) begins ONLY after graduation criteria met.

## Investment philosophy

- **Fundamentals over technicals.** We care about business quality, not chart patterns.
- **Concentration is fine, recklessness is not.** 5-10 positions, not 50, not 2.
- **Time in market > timing the market.** Hold winners, cut losers, don't churn.
- **Boring is good.** If a thesis can be summarized as "AI hype" or "meme momentum," it's not a thesis.

## Position rules (HARD LIMITS)

| Rule | Limit |
|---|---|
| Max position size (one ticker) | 15% of portfolio |
| Max sector concentration | 35% of portfolio |
| Min cash reserve | 5% of portfolio |
| Max number of open positions | 10 |
| Min position size | 2% of portfolio (no token positions) |
| Max trades per day | 3 |
| Max trades per week | 8 |

If a calculation says you should exceed any of these, the trade is rejected. Do not "almost" violate these. The whole point is discipline.

## Universe

Tradeable: US-listed common stocks and ETFs with:
- Market cap > $2B
- Average daily volume > $10M
- Listed on NYSE or NASDAQ

Do NOT trade:
- Options, futures, crypto
- Leveraged ETFs (anything 2x, 3x, inverse)
- OTC / pink sheet stocks
- IPOs in their first 90 days
- Stocks with pending merger/acquisition deals
- Anything in your "blacklist" section in lessons.md

## Buy criteria (need AT LEAST 3 of 5)

1. **Quality**: Profitable (positive net income or strong cash flow), or clear path to profitability with growing revenue >20% YoY
2. **Reasonable price**: P/E or P/S not in nosebleed territory relative to sector + growth
3. **Catalyst**: A specific reason this 3-12 month window matters (product launch, earnings setup, sector rotation, undervaluation correction)
4. **Moat or differentiation**: Brand, network effects, switching costs, scale, IP — something defensible
5. **No imminent disaster**: No earnings within 5 trading days, no pending regulatory action, no obvious accounting concerns

## Sell criteria

Sell if ANY of these:
- Position down 15% from entry (hard stop, no exceptions)
- Position down 8% AND thesis has materially changed
- Position up 30%+ AND fundamentals have deteriorated
- Better opportunity available AND need to free capital (rare — must document explicitly)
- Held >12 months AND original thesis has played out

Trailing stops: Once a position is up 20%, set a mental trailing stop at -10% from peak. Document in trade log.

## When NOT to trade (do nothing days)

- First 30 minutes after market open (9:30-10:00 ET) — too volatile
- Last 15 minutes (3:45-4:00 ET) — too thin
- Day of FOMC announcement
- Day before / day of major economic releases (CPI, jobs report) unless thesis specifically incorporates them
- When you don't have a clear thesis. "Feels like a good time" is not a thesis.

## Cadence

- **Pre-market (6:00 AM ET)**: Research only. No trades. Identify candidates for the day.
- **Market open (9:45 AM ET)**: Execute planned trades from pre-market, if conditions hold.
- **Midday (12:00 PM ET)**: Risk check. Cut losers hitting stops. Tighten stops on winners.
- **Close (3:30 PM ET)**: Final risk check. Update portfolio. No new positions.
- **Weekly review (Friday 4:30 PM ET)**: Self-evaluation, lessons, performance vs SPY.

## Graduation criteria for Phase 2 (real money)

ALL of these must be true after at least 90 days of paper trading:
- [ ] System has run without manual intervention for 30+ consecutive trading days
- [ ] Max drawdown stayed under 15%
- [ ] Beat OR matched SPY total return (within 2%)
- [ ] No kill-switch breaches not caught by the agent itself
- [ ] User has read every trade log entry and agrees the reasoning was sound
- [ ] Memory files are still under context budget (trade_log.md rotated if needed)

If graduated, Phase 2 starts with $500-$2000 of real money, NOT scaled-up paper amount.
