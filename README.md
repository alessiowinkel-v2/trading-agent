# Trading Agent

An autonomous trading agent built on Claude Code cloud routines (scheduled tasks) and Alpaca. Core + satellite strategy: a broad S&P 500 core that is always held, plus a few gated stock picks. Paper trading ($2,000) until measurable graduation criteria are met, then a $2,000 live account.

Not financial advice. Not a backtested strategy. No guarantee of returns.

## How it works

- Four weekday routines + a Friday review run in Anthropic's cloud. Each run clones this repo, follows `routines/COMMON.md` + its routine file, appends a dated record under `memory/`, and commits to `main`. Git is the memory.
- **Scripts compute, the model judges.** `scripts/preflight.sh` (dates, market clock, holidays, events, pause, cadence), `scripts/screen.py` (indicators and entry gates), `scripts/ks.py` (kill switches, core sizing, satellite slots, P&L vs SPY, ready-to-run order commands).
- **Order guards live in code**: `scripts/alpaca.sh` refuses fractional shares, market buys, buys beyond cash (never margin), shorts, options, orders without an idempotent `client_order_id`, buys while paused, and any live order without `LIVE_TRADING_CONFIRMED=yes`.
- **Alerts reach a human**: `scripts/notify.sh` posts to a Discord or Slack webhook. A GitHub Actions watchdog (`.github/workflows/watchdog.yml`) alerts — and makes GitHub email you — if any routine fails to report, even if the whole Claude setup is gone.

| Routine | ET time | File |
|---|---|---|
| Pre-market research | 07:07 Mon–Fri | `routines/01_pre_market.md` |
| Market-open execution | 10:12 Mon–Fri | `routines/02_market_open.md` |
| Midday protection | 13:07 Mon–Fri | `routines/03_midday.md` |
| EOD snapshot | 16:37 Mon–Fri | `routines/04_daily_summary.md` |
| Weekly review | 18:07 Friday | `routines/05_weekly_review.md` |

## Layout

```
CLAUDE.md                 standing instructions (auto-loaded)
routines/COMMON.md        shared rules every routine reads first
routines/0X_*.md          schedule, paste block (the routine prompt), STEPs
scripts/alpaca.sh         Alpaca API + order guards        scripts/preflight.sh  run facts + exit codes
scripts/screen.py         sector ranks, regime, gates      scripts/ks.py         kill switches, sizing, P&L, state
scripts/notify.sh         webhook alerts                   scripts/perplexity.sh news/earnings research
scripts/gitpush.sh        commit + push to main            scripts/memtail.sh    read the tail of a log
scripts/watchdog.sh       cadence check (GitHub Actions)   scripts/selftest.sh   end-to-end self-test
scripts/tlib.py           shared library (ET time, indicators, params)
memory/TRADING-STRATEGY.md   rules + params block   memory/KILL-SWITCHES.md   halts
memory/WATCHLIST.md          satellite universe     memory/EVENTS.md          FOMC/CPI/NFP days
memory/PROJECT-CONTEXT.md    phase + account block  memory/STATE.md/.json     written by ks.py
memory/RESEARCH-LOG.md, TRADE-LOG.md, WEEKLY-REVIEW.md, LESSONS.md, notifications/YYYY-MM.md
memory/archive/phase1-2026/  everything from Phase 1 (May-Sep 2026, zero trades)
plans/news-sleeve/           news-signal research sleeve: PLAN.md, STATUS.md, one prompt file per phase
```

## Setup (in this order)

1. **Reset the Alpaca paper account to $2,000** (Alpaca dashboard → paper account → reset). Resetting issues **new API keys** — copy them afterwards, and note the account number.
2. **Webhook**: create a Discord channel webhook (Channel settings → Integrations → Webhooks) or a Slack incoming webhook. For Discord pings, note your user id (`<@123…>`).
3. **Fill in `memory/PROJECT-CONTEXT.md` → `## Account`**: `start_date` (first trading day the routines will run) and `account_number`. Commit.
4. **Local self-test**: `cp env.template .env`, fill in the paper keys and webhook, then
   ```bash
   bash scripts/selftest.sh --notify            # read-only checks, guard refusals, webhook
   bash scripts/selftest.sh --orders            # also places and cancels one far-off paper order
   ```
   All lines must say PASS. Never commit `.env`.
5. **Cloud environment** at claude.ai/code → environment selector → New environment, named `trading`:
   - Network access: **Full** (or Custom: `*.alpaca.markets`, `api.perplexity.ai`, `discord.com` / `hooks.slack.com`, plus defaults). The default "Trusted" level blocks these APIs.
   - Environment variables: `ALPACA_ENDPOINT=https://paper-api.alpaca.markets/v2`, `ALPACA_DATA_FEED=iex`, `NOTIFY_WEBHOOK_URL=…`, optional `NOTIFY_MENTION=…`, `PERPLEXITY_MODEL=sonar`.
   - API keys, either as plain variables (`ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, `PERPLEXITY_API_KEY`) — simplest for paper — or, **recommended for live**, as network secrets (the key never enters the session): host `*.alpaca.markets` with custom headers `APCA-API-KEY-ID` and `APCA-API-SECRET-KEY` (no prefix), host `api.perplexity.ai` with `Authorization: Bearer`; then set `ALPACA_AUTH=proxy` and `PERPLEXITY_AUTH=proxy`. *Unverified*: whether one secret can carry both Alpaca headers (otherwise two secrets on the identical host). Check with "Run now" on the pre-market routine — if preflight exits 40, fall back to plain variables.
6. **GitHub**: repository Settings → Secrets and variables → Actions → add `NOTIFY_WEBHOOK_URL` (and optionally `NOTIFY_MENTION`). Make sure Actions are enabled; run the `watchdog` workflow once by hand.
7. **Routines**: create the five routines (Claude can do this with `/schedule` from this repo), each with: this repository, the `trading` environment, the model and tools from its file, the cron from its file (`CRON_TZ=America/New_York …`), and the 4-line paste block as the prompt. Remove connectors the routines don't need.
8. **Run now**, outside market hours, in order 01 → 05. Each must produce one commit on `main` in the convention `<routine> <DATE>: OK|SKIPPED|ABORTED - …` and one webhook message.
9. Work through `STRESS_TEST.md`.

## Operating it

- **Daily**: read the EOD message. No EOD message by 18:00 ET = incident: check claude.ai/code/routines.
- **Weekly**: read the Friday review in `memory/WEEKLY-REVIEW.md`, then add `Reviewed: YYYY-MM-DD` under it (graduation criterion 10).
- **Quarterly**: extend `memory/EVENTS.md` from the Fed and BLS calendars (the weekly review warns when < 8 weeks remain).
- **Pause**: commit `memory/PAUSED.flag` (any content). Buys stop immediately; stops and exits continue. **Resume**: delete it and commit.
- **Model changes**: routines use `claude-sonnet-5-5`; if behaviour shifts after a model update, pause and review.

## Phase 2 — going live (only after every graduation criterion and your sign-off)

1. Open and fund a **separate live Alpaca account with $2,000** (start the application early — approval and ACH settlement take days).
2. In `memory/PROJECT-CONTEXT.md`: `phase: 2-live`, new `start_date`, `start_equity: 2000`, the live `account_number`. Commit.
3. In the cloud environment only: `ALPACA_ENDPOINT=https://api.alpaca.markets/v2`, the live keys (preferably as network secrets), `LIVE_TRADING_CONFIRMED=yes`, `MAX_LIVE_EQUITY=3000`. Preflight and alpaca.sh refuse live trading without the confirmation flag; KS-9 halts if the account number or equity doesn't match.
4. Week 1: core only (pause satellites by temporarily setting `sat_max_positions: 0` in the params block). Weeks 2–3: `sat_max_positions: 2`. Week 4+: 3.
5. Stop or delete the paper routines' environment so only one account is traded. Rollback: commit `memory/PAUSED.flag`, or point `ALPACA_ENDPOINT` back to paper.
