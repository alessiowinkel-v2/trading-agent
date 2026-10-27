# Trading Strategy (v2 — core + satellite)

The agent may NOT edit this file. Suggest changes in the Friday review; the user decides.
Every number the scripts use comes from the `params` block below — the text explains it, the block is the law.

## Mission
Beat SPY with lower max drawdown by **always** holding a core index sleeve and adding satellite stock picks under gates computed from real price data.
Idle capital is not neutral: it is a position that earns 0% while SPY earns its return (Phase 1 sat in cash for 81 days and placed zero trades).

## Philosophy
- **Deployed > idle.** Patience applies to satellite picks, never to the core.
- **Trend first, fundamentals confirm.** The screen finds names in confirmed uptrends; your thesis explains why the trend should continue.
- **Exclude setups by price behaviour, never by label.** "AI", "tech", "momentum", "geopolitical" are not reasons to skip. Chasing (gate G4) is.
- **Scripts compute, you judge.** Indicators, kill switches, sizing and P&L come from `scripts/screen.py` and `scripts/ks.py`. You never estimate a number they print.

## Capital & instruments
- Account: Alpaca, $2,000 (paper in Phase 1b, live in Phase 2 — see PROJECT-CONTEXT.md).
- US-listed stocks and ETFs in `memory/WATCHLIST.md` (plus the 11 sector ETFs). **Whole shares only** (fractional orders cannot carry GTC trailing stops).
- Core ETF: **SPYM** (State Street SPDR Portfolio S&P 500, formerly ticker SPLG — renamed 2025-10-31).
- Never: options, futures, crypto, leveraged/inverse ETFs, OTC, IPOs < 90 days, pending-M&A targets, margin (orders must fit in cash), short sales, extended-hours orders.

## Allocation

| Sleeve | Rule |
|--------|------|
| Core (SPYM, always held) | target = clamp(75% − satellite%, 55%, 80%); rebalance only when actual is more than ±5pp from target |
| Core in risk-off regime | target 30% |
| Satellites | ≤3 positions (≤2 in risk-off); each ≤15% and ≥8% of equity; total ≤35%; ≤2 per sector and ≤25% of equity per sector; share price ≤15% of equity |
| Cash | ≥5% of equity at all times |
| Deployment floor (health metric) | invested ≥70% at EOD — structural: with no satellites the core sits at 75% ±5pp |

Whole-share sizing at $2,000: one satellite is usually 1–2 shares (sizes snap to 8–15%), so "3 satellites" is realistically two full positions plus one small one. That is expected.

## Regime filter (the core's only risk rule)
- SPY vs its 200-day SMA on completed daily closes. Risk-off after 3 consecutive closes below; back to risk-on after 3 consecutive closes above. Replayed from bars every run (`ks.py`, `screen.py sectors`) — never carried in a log.
- The core has **no trailing stop and no −7% cut**. A stop on a 55–80% index sleeve would sell every ordinary correction and recreate Phase 1's cash drag.

## Core orders
- `ks.py` prints `CORE_ACTION=` with the exact order. Limit = ask +0.1% (buys) / bid −0.1% (sells), time_in_force day, `client_order_id core-<DATE>`.
- At most one core order per day; never sell core shares bought the same day (day trade). Never timing-blocked.
- Day 1 of a phase: buy core to target at the first market-open.

## Satellite entry gates
Every candidate gets a table with every gate as PASS/FAIL **and its number**. G1–G5 and G8 come from `screen.py`; G6–G7 are yours; G0 and G8–G11 are re-checked live by `ks.py --check` at execution, which also refuses any symbol that is not on a `CANDIDATE: … g6=PASS g7=PASS` line in today's research entry (gate PLAN), re-checks the universe and price cap (G1), and takes the reference price from that line. Several candidates in one check are sized one after another, so they can never jointly exceed slots, cash or sector caps.

| # | Gate | Source |
|---|------|--------|
| G0 | Not already held, no open order for the symbol | ks.py |
| G1 | In WATCHLIST.md or a sector ETF; share price ≤15% of equity | screen.py |
| G2 | 20-day average dollar volume ≥ $50M (SIP history) | screen.py |
| G3 | Close > SMA50 and SMA50 > SMA200 | screen.py |
| G4 | Not chasing: 5-day return ≤ +15% AND close ≤ SMA20 + 2×ATR14 | screen.py |
| G5 | Sector rank ≤7 of 11, OR the stock's 63-day return beats SPY by >5pp | screen.py |
| G6 | No earnings report in the next 5 trading days (Perplexity with recency filter; fallback WebSearch; if still unconfirmed, PASS only if the last report was < 45 days ago) | you |
| G7 | Thesis: 2–3 sentences naming the specific driver for the next 1–3 months. "Leader of a top-3 sector at a 20-day high" is an acceptable thesis | you |
| G8 | Stop = max(7%, 2×ATR14/price), capped at 10%; target ≥ entry + 2×risk; qty = floor(min(15% of equity, cash − 5% reserve) / limit) ≥ 1 and ≥ 8% of equity | screen.py / ks.py |
| G9 | Slots: ≤2 entries today, ≤3 this week, position/sector/total caps, cash reserve, `daytrade_count` ≤1, no kill switch, no sector cooldown | ks.py |
| G10 | Today is not an FOMC / CPI / NFP day listed in EVENTS.md | preflight / ks.py |
| G11 | Market open; last trade ≤15 min old; spread ≤1%; ask within ±3% of the research reference price | ks.py |

## Timing blocks — CLOSED list
No **new satellite entries** on exactly these days, as listed in `memory/EVENTS.md`:
1. FOMC decision day
2. CPI release day
3. NFP (jobs report) day

Explicitly **not** blocks — never cite them as a reason to skip: the day before anything, PPI, PCE, GDP, JOLTS, ADP, ISM, retail sales, jobless claims, Fed minutes or speeches, options expiry / triple witching, other companies' earnings, holiday-adjacent sessions, geopolitical headlines.
Core orders and all exits are never blocked. Citing a block that is not on this list is a rule violation — log it as one.

## Pipeline minimum
- Pre-market must produce **≥2 gate-checked candidates from ≥2 different sectors**, or list the failing gate for every screen passer it rejected. "Nothing looked good" is not an answer.
- Fallback candidate: the #1-ranked sector ETF if it passes G3 and G4.
- Every candidate from yesterday gets a one-line outcome today: FILLED / not filled: <reason> / dropped: <gate>.
- No narrative vetoes: if a candidate passes every gate, it is planned. A concern that no gate captures goes into the weekly review as a suggested rule, not into a skip.

## Exits (satellites only)
- Immediately after a fill: GTC trailing stop at the G8 stop % for `filled_qty` (cancel any unfilled remainder first). Verify with `order-get`. A satellite without a stop is kill switch KS-10.
- Tighten to 7% trail at +15% unrealized, to 5% at +20% — via `order-replace` (no unprotected window). Never within 3% of the current price. Never widen.
- Manual close only if price is below the stop level and the stop order is missing/unfilled (gap), or on a logged thesis break (fraud, failed M&A, guidance withdrawn). Cancel the stop first, then `alpaca.sh close SYM`.
- No separate −7% hard cut — the ATR-based trailing stop is the cut.
- Two consecutive losing satellites in one sector → no new entries in that sector for 10 trading days (ks.py tracks it).

## Graduation (Phase 1b paper → Phase 2 live) — all required, after ≥4 weeks
1. ≥15 trading days in which all four daily routines committed `OK` or `SKIPPED`
2. Core bought on Day 1 and ≥1 later core rebalance filled
3. ≥4 satellite entries filled, ≥2 closed, each with a verified trailing stop placed in the same session
4. Invested ≥70% on ≥90% of EOD snapshots
5. ≥2 candidates across ≥2 sectors (or every rejection's failing gate) on ≥90% of research days; every planned order has an outcome line
6. Zero timing blocks cited outside the closed list
7. Max drawdown ≤8% and ≤ SPY's max drawdown + 1pp over the same period
8. Return within −3pp of SPY over the paper phase
9. ks.py output in every EOD record; zero kill-switch breaches the scripts did not catch
10. User sign-off: a committed `Reviewed: <date>` line under each weekly review
11. Day-1 mechanics test passed (see STRESS_TEST.md)

```params
core_symbol: SPYM
core_target_base: 0.75        # core target = clamp(base - satellite%, min, max)
core_target_min: 0.55
core_target_max: 0.80
core_band: 0.05               # rebalance only outside target +/- band
core_riskoff_target: 0.30
cash_min: 0.05
deploy_floor: 0.70            # EOD health metric
regime_confirm_days: 3
sat_max_positions: 3
sat_max_positions_riskoff: 2
sat_max_pct: 0.15
sat_min_pct: 0.08
sat_total_max: 0.35
sat_sector_max_positions: 2
sat_sector_max_pct: 0.25
sat_price_max_pct: 0.15
entries_per_day: 2
entries_per_week: 3
min_adv_usd: 50000000
chase_r5_max: 0.15
chase_atr_mult: 2.0
sector_rank_max: 7
rs63_override: 0.05
stop_min: 0.07
stop_max: 0.10
stop_atr_mult: 2.0
reward_risk_min: 2.0
earnings_buffer_days: 5
max_spread: 0.01
max_ref_deviation: 0.03
pdt_max_daytrades: 1
ks1_daily_dd: 0.03
ks2_weekly_dd: 0.07
ks3_total_dd: 0.15
ks4_position_max: 0.20
ks9_equity_low: 0.5
ks9_equity_high: 1.5
ks11_loss_streak: 3
ks11_cooldown_days: 5
sector_loss_streak: 2
sector_cooldown_days: 10
```
