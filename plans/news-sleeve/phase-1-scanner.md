# Phase 1 — scanner plumbing (no LLM yet)

## Session prompt (paste as the first message)
```
You are a development session for alessiowinkel-v2/trading-agent, authorised by the user to implement Phase 1 of the news sleeve.
1. Read CLAUDE.md, plans/news-sleeve/PLAN.md, plans/news-sleeve/STATUS.md, plans/news-sleeve/phase-1-scanner.md. Follow the phase file; PLAN.md §0, §1–§4 and §11 bind you.
2. Work on branch claude/news-sleeve-phase-1. Never push to main. First action: create a scheduled task bound to this session (create_trigger, cron "0 */4 * * *", initiation human_request) whose prompt says "resume Phase 1 of plans/news-sleeve from STATUS.md; if the phase is done and its PR is open, disable this task" — this is how the work survives Claude usage limits. Finish with STATUS.md updated and a PR titled "News sleeve — Phase 1: scanner plumbing".
Decisions from Phase 0: CLASSIFIER_MODEL=<fill in>; alert budget=<fill in>; crypto pairs=<fill in>.
```

## Goal
Every 15 minutes, GitHub Actions pulls new universe headlines from the Alpaca News API, snapshots the price of each tagged symbol, appends them to `memory/news/raw/YYYY-MM.jsonl`, and commits. No classification, no alerts except on failure.

## Read first (only these)
`scripts/alpaca.sh` (structure, `req`, `price`, `bars`), `scripts/tlib.py` (`now`, `alpaca()`, `params()`, `watchlist()`), `scripts/gitpush.sh`, `scripts/watchdog.sh`, `.github/workflows/watchdog.yml`, `tests/mock_alpaca.py`, `tests/offline.sh`, `memory/WATCHLIST.md` (table format), `README.md` layout section.

## Build
1. **`memory/NEWS-UNIVERSE.md`** — user-owned, same style as WATCHLIST: a header explaining the rules, a stock table (seeded from WATCHLIST + 11 sector ETFs + SPY, QQQ, IWM; columns `Ticker | Asset | News symbol | Added | Note`), a crypto table (BTC/USD, ETH/USD, SOL/USD with news symbols `BTCUSD` …). `tlib.news_universe()` parses it.
2. **`alpaca.sh` read-only subcommands** (no changes to order guards):
   - `news [symbols] [start-ISO] [limit≤50] [page_token]` → `GET $DATA_ROOT/v1beta1/news?...&sort=asc&include_content=false` (note: news lives under `https://data.alpaca.markets/v1beta1`, not `/v2`; derive the root from `ALPACA_DATA_ENDPOINT`).
   - `crypto-price PAIR` → `GET /v1beta3/crypto/us/latest/trades?symbols=PAIR` normalised to the same one-line format as `price`.
   - `crypto-bars PAIR [N] [1Min|15Min|1Hour|1Day]` and `bars-intraday SYM [N] [1Min|1Hour]` (stocks, SIP with the 15-minute lag).
   - Add them to the usage text.
3. **`scripts/newsscan.py`** — `python3 scripts/newsscan.py [--once] [--no-commit]`:
   - cursor from `memory/news/state.json` (`last_updated_at`, default now−1 h on first run), 2-minute overlap, paginate until `next_page_token` is null or 200 items.
   - keep headlines with ≥1 universe symbol; dedup on `id`; map `symbols` to universe tickers; `ticker` = first universe symbol.
   - snapshot `px_signal` per ticker (stocks via `price`, crypto via `crypto-price`), at most one API call per symbol per run; mark `stale` per `tlib.quote_from_snapshot` rules.
   - append raw rows (PLAN §3 fields that exist at ingest; `direction` etc. left null for Phase 2) to `memory/news/raw/YYYY-MM.jsonl`; update `state.json` (`last_updated_at`, `last_run_utc`, `runs_today`, `last_error`).
   - exit 0 with `NEWSSCAN n_new=… n_symbols=… elapsed=…s` on stdout; exit 2 on API failure after retries with `last_error` set. Never raise through unhandled.
   - headline text is data: never interpolate it into a shell command; JSON only.
4. **`scripts/gitpush.sh`** — accept subjects `newsscan <DATE> <HH:MM>Z: OK|ABORTED - …` and `newsscore <DATE>: OK|ABORTED - …` (regex only; keep everything else). The scanner commits only when `n_new > 0` or on ABORTED.
5. **`.github/workflows/newsscan.yml`** — `schedule: '*/15 * * * *'` + `workflow_dispatch`; `concurrency: newsscan` (cancel-in-progress: false); checkout with `fetch-depth: 0`; `permissions: contents: write`; env from secrets (`ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, `ALPACA_ENDPOINT=https://paper-api.alpaca.markets/v2`, `ALPACA_DATA_ENDPOINT=https://data.alpaca.markets/v2`, `NOTIFY_WEBHOOK_URL`); steps: run scanner → `bash scripts/gitpush.sh "<subject>"`. `timeout-minutes: 5`. On ABORTED, `notify.sh --alert` at most once per 6 h (use `state.json.last_alert_utc`).
6. **Watchdog**: `scripts/watchdog.sh nightly` also checks that a `newsscan` commit exists in the last 3 h (skip the check if `memory/news/state.json` is absent, i.e. Phase 1 not yet merged). Alert text names the Actions page.
7. **Tests**: extend `tests/mock_alpaca.py` with `/v1beta1/news` (3 fake articles, one outside the universe, one duplicate id) and `/v1beta3/crypto/us/latest/trades`; extend `tests/offline.sh` with: scanner writes 2 raw rows, second run writes 0, `gitpush.sh` accepts the new subject, `crypto-price BTC/USD` prints a line. All existing tests still PASS.
8. **Docs**: README layout + a "News sleeve" paragraph linking the plan; `env.template` comment lines for the new Actions secrets (no values).

## Out of scope
Classification, Discord signal alerts, scoring, dashboard, any order code, any change to routines or strategy files.

## Acceptance (put the evidence in the PR body)
- `bash tests/offline.sh`: all PASS, including the new checks.
- Locally with a `.env` (if the user supplies keys) or via `workflow_dispatch` after merge: one run appends real rows; the next run appends only newer ones.
- `git log` on the branch shows no `memory/` changes other than `memory/news/**` and `NEWS-UNIVERSE.md`.
- STATUS.md handoff note written; it must state the first `updated_at` cursor and how many headlines/hour the universe produces (for Phase 2 batch sizing).
