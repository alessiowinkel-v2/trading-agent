# Kill Switches

Computed by `python3 scripts/ks.py` on every run — you never evaluate them by hand. Thresholds live in the `params` block of TRADING-STRATEGY.md. The agent may NOT edit this file.
`ks.py --write-state` alerts the user automatically when a switch newly fails.

| Switch | Fails when | Effect |
|--------|------------|--------|
| KS-1 daily drawdown | equity < 97% of `last_equity` (start equity on day 1 or if `last_equity` is implausible) | no buys today, core included |
| KS-2 weekly drawdown | equity < 93% of the prior Friday close | no buys until the weekly review |
| KS-3 total drawdown | equity < 85% of start equity | cancel satellite stops, close all satellites, sell core to 30%, halt, alert. **Manual reset only** |
| KS-4 position size | a satellite > 20% of equity | no new satellites; trim it back to 15% |
| KS-5 activity | > 2 entries today or > 3 this week | no new satellites |
| KS-6 API errors | > 2 failed Alpaca calls in a run, or ks.py exits 2 | no orders this run |
| KS-7 stale data | core ETF's last trade > 15 min old while the market is open | no buys |
| KS-8 reconciliation | positions differ from STATE.json + recorded fills | no orders; alert; investigate |
| KS-9 account identity | `start_date` not set, `account_number` ≠ PROJECT-CONTEXT.md, or equity outside 0.5–1.5× start equity (wrong endpoint / wrong keys) | no orders; alert |
| KS-10 unprotected satellite | a satellite has no open stop order covering its shares | place the stop now (ks.py prints the command); if rejected, close it at midday |
| KS-11 losing streak | 3 consecutive losing satellites | no new satellites for 5 trading days; write a LESSONS entry |
| PDT guard | `daytrade_count` ≥ 2 or account flagged PDT | no new satellites (keeps a day trade free for a same-day stop) |

## Rules
- A failing switch never sells the core, except KS-3 and the regime rule.
- Exits and stop placement are always allowed (except KS-6/8/9, where nothing is sent until the data is trustworthy).
- Never work around a switch (smaller orders, different symbol, splitting orders).

## Manual pause (user-controlled)
Pause: commit `memory/PAUSED.flag` (any content) to main — e.g. on GitHub "Add file". A root-level `PAUSED.flag` is honoured too.
While paused: `alpaca.sh` refuses all buys; exits, stops and records continue; every run says so.
Resume: delete the file and commit.

## Resets
KS-1, KS-2 and KS-3 **latch**: once tripped they stay failed (recorded under `latch` in memory/STATE.json) even if equity bounces back.
- KS-1: latched for the rest of the trading day; clears the next trading day.
- KS-2: latched until a weekly review (`ks.py --week --write-state`) runs while the weekly drawdown is back above −7%.
- KS-3: **user only** — set a new start_equity/start_date in PROJECT-CONTEXT.md (that clears the latch) and add a LESSONS entry.
- KS-4/5/7/10/PDT: clear by themselves once the condition is gone. KS-6/8/9: once the underlying problem is fixed (KS-8 may need the user to delete memory/STATE.json after investigating).
