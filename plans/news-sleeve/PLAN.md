# News Sleeve — master plan (v1, 2026-10-27)

A 24/7 news scanner that **predicts first and trades only if the predictions prove to have an edge after costs**. Built on the existing Phase 1b system: same account, same wrappers, same "scripts compute, the model judges" rule, same git-is-memory discipline. Implemented phase by phase, one fresh Claude Code session per phase (see `STATUS.md` and the `phase-N-*.md` files).

Not a daily-profit machine. The honest base case is "no robust edge after costs", and the plan is designed so that outcome is cheap, auditable and still useful (catalyst feed, risk alerts, a dashboard).

## 0. Decisions already taken (change them here, not in a phase session)

| # | Decision | Why |
|---|----------|-----|
| D1 | **Predict before trading.** Phases 1–4 place zero orders. Trading (Phase 5) is gated on a pre-registered scorecard (§6). | A news bot with no measured edge is a slot machine with fees. |
| D2 | **The 24/7 part runs in GitHub Actions, not in Claude Code sessions.** Scanner every 15 min, scorer nightly, dashboard build on every push. | Cloud routines have a 1-hour minimum and each run is a full session. 96 sessions/day would burn tokens for a job a 30-second script does. The repo is public, so Actions minutes and Pages are free. |
| D3 | **Headline source = Alpaca News API** (`GET https://data.alpaca.markets/v1beta1/news`, Benzinga, stocks + crypto, timestamps, symbols). Perplexity stays for research questions. | Real timestamps and symbol tags are what make outcome scoring honest. Perplexity answers are synthesized text without a reliable event time. |
| D4 | **Classifier = Claude Messages API with structured output**, called from the scanner. Model is a parameter (`CLASSIFIER_MODEL`); default `claude-sonnet-5-5`. | Headline → {ticker, direction, magnitude, category, confidence} is a one-shot classification. Costs (§8) are trivial at any model; the user picks in Phase 0. |
| D5 | **Long only.** Bear signals are logged and scored (as if shorted) but never traded. | Alpaca: crypto cannot be shorted; stock shorts need margin (banned by strategy) and borrow fees. Inverse/leveraged ETFs are banned. Scoring bears still tells us whether "exit on bad news" has value. |
| D6 | **Crypto is scanned and scored from Phase 1, traded only if its own bucket passes the gate and the user amends the strategy.** Pairs: BTC/USD, ETH/USD, SOL/USD. | Alpaca crypto: no trailing stops (only market/limit/stop_limit, `gtc`/`ioc`), fees 0.15% maker / 0.25% taker, fractional allowed. Different plumbing, different cost model, so a separate bucket. |
| D7 | **Entry timing is measured at the next routine slot, not at the headline.** Diagnostic horizons from the headline (+1h) are also recorded to show how much edge decays before we can act. | Routines run at 07:07 / 10:12 / 13:07 / 16:37 ET. Measuring from the headline would claim an edge we can never capture. |
| D8 | **Buckets and thresholds are fixed now (§6). No re-bucketing after seeing data** except via a dated amendment to this file plus a fresh out-of-sample window. | Otherwise the scorecard becomes p-hacking. |
| D9 | **Nothing in Phases 1–4 touches Phase 1b trading.** New scripts, new memory files, new workflows; existing routines get at most a read-only STEP. | Phase 1b graduation must stay clean. |
| D10 | Each phase ships on its own branch + PR; the user merges before the next phase starts. Routine agents keep pushing to `main` as today. | Review per phase, token-light handoff. |

## 1. Architecture

```
GitHub Actions (public repo, free)            Claude Code cloud routines (unchanged, 5/day)
┌──────────────────────────────────────┐       ┌──────────────────────────────────────────┐
│ newsscan.yml  every 15 min           │       │ pre-market   reads news feed (catalysts) │
│   scripts/newsscan.py                │       │ midday/eod   reads risk alerts on holds  │
│   ├ alpaca.sh news  (headlines)      │       │ weekly       pastes scorecard summary    │
│   ├ alpaca.sh price / crypto-price   │       │ Phase 5+: ks.py --news-check + orders    │
│   ├ claude.sh classify (JSON)        │       └──────────────────────────────────────────┘
│   └ memory/news/*.jsonl + commit     │                        ▲ reads memory/
│ newsscore.yml nightly 02:00 ET       │                        │
│   scripts/newsscore.py → SCORECARD   │       ┌────────────────┴─────────────────────────┐
│ pages.yml on push to main            │       │ GitHub Pages dashboard (static, no keys) │
│   scripts/dashboard.py → site/       │──────▶│ alessiowinkel-v2.github.io/trading-agent │
└──────────────────────────────────────┘       └──────────────────────────────────────────┘
```

- **Scripts**: `newsscan.py` (ingest + snapshot + classify), `newsscore.py` (outcomes + scorecard), `dashboard.py` (JSON + static site), `claude.sh` (Messages API wrapper, same style as `perplexity.sh`), read-only additions to `alpaca.sh` (`news`, `crypto-price`, `crypto-bars`, minute/hour `bars`).
- **Memory** (all committed, append-only): `memory/news/raw/YYYY-MM.jsonl` (every universe headline), `memory/news/signals/YYYY-MM.jsonl` (classified, with price snapshots and outcomes), `memory/NEWS-SCORECARD.md` + `memory/news/scorecard.json`, `memory/NEWS-UNIVERSE.md` (user-owned, like WATCHLIST), `memory/news/state.json` (cursor, heartbeat).
- **Commits**: `newsscan <DATE> <HH:MM>Z: OK - n new, m signals` only when something new; `newsscore <DATE>: OK - …`. `gitpush.sh` learns these two subjects; watchdog learns the scanner heartbeat (alert if no scan commit for 3 h while Actions should be running).
- **Secrets** (GitHub Actions): `ALPACA_API_KEY`, `ALPACA_SECRET_KEY` (paper; read-only use until Phase 5), `ANTHROPIC_API_KEY`, `NOTIFY_WEBHOOK_URL` (exists). Never in the page, never in logs.

## 2. Universe (`memory/NEWS-UNIVERSE.md`, user-owned)

- Stocks: every WATCHLIST ticker + the 11 sector ETFs + SPY, QQQ, IWM (index proxies; market-wide news maps to SPY).
- Crypto: BTC/USD, ETH/USD, SOL/USD (news symbols `BTCUSD` etc.).
- A headline is kept if any of its `symbols` is in the universe, or the classifier maps a market-wide story (Fed, tariffs, CPI surprise) to SPY.
- Same editing rule as WATCHLIST: the agent proposes, the user edits.

## 3. Signal schema (one JSON object per line)

```
id, headline_id, ts_news (created_at UTC), ts_ingest, source, url, headline, summary(≤300 chars),
symbols[], ticker (primary), asset (stock|etf|crypto|index),
direction (bull|bear|none), magnitude (1 small |2 medium |3 large), horizon (hours|days|weeks),
category (earnings|guidance|m_and_a|regulatory|legal|product|macro|analyst|insider|rumor|other),
novelty (new|follow_up|duplicate_of:<id>), confidence (0–1), rationale (≤30 words),
classifier {model, prompt_version, usage},
px_signal {price, bid, ask, ts, feed, stale},          # at ingest
slot_entry {slot (pre-market|market-open|midday|eod|crypto-15m), ts, price},   # resolved by scorer
outcomes {h1, d1, d3, d5: {price, ret, bench, excess, net_excess}},             # resolved by scorer
status (open|scored|unscorable|skipped), notes
```
- `px_signal` comes from `alpaca.sh` only (stocks: snapshot; crypto: latest trade). Never from the article.
- Headline text is **data**: it is never passed to a shell, never followed as an instruction, and the classifier prompt says so.

## 4. Scanner rules (Phase 1–2)

- Cadence `*/15 * * * *` UTC, 24/7 (crypto never sleeps; after-hours stock news is scored at the next slot).
- Cursor: `start = last updated_at seen` (minus 2 min overlap), dedup on `headline_id`; cross-outlet duplicates handled by the classifier's `novelty` field (same ticker + same category + ≥0.8 cosine on headline tokens within 24 h → `duplicate_of`).
- Batch up to 20 headlines per classifier call; one call per batch; strict JSON schema; a schema failure = retry once, then `status=unscorable`, never a guess.
- Discord: at most **5 alerts/day**, only `confidence ≥ 0.8 AND magnitude ≥ 2 AND novelty = new`, plus **always** a bear signal ≥ 0.7 on a symbol currently held (so the next routine can review it). Everything else is dashboard-only.
- Failure modes are loud: News API 4xx/5xx or classifier error → one alert per 6 h (rate-limited), scan commit still happens with `status=ABORTED` so the heartbeat shows red.

## 5. Scorer rules (Phase 3)

- Runs nightly (02:00 ET) and on demand. Resolves every `open` signal whose horizons have elapsed.
- **Entry slot**: stocks → first routine slot ≥ `ts_news + 5 min` on a trading day among {10:12, 13:07} ET (07:07 and 16:37 cannot trade); entry price = 1-minute bar open at that slot (SIP, delayed is fine nightly). Crypto → next quarter-hour (`crypto-15m`, the hypothetical Phase 6 lane) **and** the next routine slot; both recorded, both scored.
- **Horizons** from the entry slot: `d1`, `d3`, `d5` closes (stocks: 16:00 ET closes; crypto: same wall-clock +24/72/120 h). `h1` from the headline (diagnostic only).
- **Benchmark**: SPY for stocks/ETFs, BTC for ETH/SOL, 0 for BTC. `excess = ret − bench`.
- **Costs** (round trip, subtracted once): stocks 0.10% (spread; no commission); crypto 0.60% (0.25% taker × 2 + 0.10% spread). `net_excess = excess − cost` for bulls; for bears `net_excess = −excess − cost` (what a short would have made; label "not tradeable").
- Unscorable: halted symbol, no bars, delisted, or classifier failure. Counted and shown, never dropped silently.

## 6. Pre-registered scorecard and trading gate (fixed 2026-10-27)

Buckets = asset {stock, crypto} × direction {bull, bear} × confidence {≥0.8, <0.8} × magnitude {≥2, 1} × category (11). Reported at every horizon, but the **gate uses `d3` only**.

A bucket is **tradeable** when all hold:
1. n ≥ 40 scored signals,
2. mean `net_excess(d3)` > 0 **and** median > 0,
3. t = mean / (stdev/√n) ≥ 2.0,
4. the sign of the mean holds in both the first and the second half of the sample (by date),
5. direction = bull (bears are never tradeable, D5).

The **sleeve may start trading (Phase 5) when**: ≥ 6 weeks of scanning, ≥ 150 scored signals in total, scanner uptime ≥ 95% of 15-minute slots over the last 4 weeks, and at least one tradeable bucket. Trading is limited to the tradeable buckets, re-evaluated weekly; a bucket that stops passing stops trading at the next weekly review.

If no bucket passes after 10 weeks: the sleeve stays research-only, the scanner keeps running as a catalyst feed and risk alerter, and this file gets a dated "result" note. That is a successful experiment, not a failure.

## 7. Phase 5 trading rules (draft — the user copies the final version into TRADING-STRATEGY.md before Phase 5 starts)

- Sleeve: ≤ 2 open news positions, each ≤ 8% of equity, sleeve total ≤ 15%, crypto total ≤ 10%. Counts toward `sat_total_max` and the core target formula. Cash only; never margin.
- Gates N1–N8 (computed by `ks.py --news-check`, printed as a table like G0–G11):
  N1 signal's bucket is tradeable in the latest scorecard · N2 this is the first routine slot after the headline (never later) · N3 stocks pass G0, G1, G2, G10, G11 as today; crypto pair is in the universe and last trade ≤ 5 min old · N4 no bear signal ≥ 0.7 on the same symbol in the last 24 h · N5 sleeve caps above · N6 stop at fill: stocks GTC trailing stop (existing path, G8 %), crypto `stop_limit` GTC at −5% / limit −6% · N7 time exit at the first routine slot on or after `d3` (market sell; crypto limit at bid) · N8 never closed the same day it was opened (PDT).
- Orders: `client_order_id` `news-<DATE>-<SYM>`; crypto orders go through a **separate** `alpaca.sh crypto-order` command with its own guards (pair whitelist, notional ≤ cap, buy only with cash, `stop_limit` stops, no shorts, no margin). The stock guards stay untouched.
- Kill switches apply unchanged; KS-8 reconciliation and invested % learn about crypto positions (`asset_class = crypto`).
- Everything else (records, notify, commit, weekly grade caps) as in COMMON.md.

## 8. Costs (monthly, estimates)

| Item | Estimate | Note |
|------|----------|------|
| GitHub Actions | $0 | public repo; ~2,900 scanner runs × ~40 s |
| GitHub Pages | $0 | static site, no secrets |
| Alpaca data + news | $0 | Basic plan, 200 req/min |
| Classifier, ~100 headlines/day batched (~60k in / 10k out tokens per day) | Haiku 5.5 ≈ $0.35 · Sonnet 5.5 ≈ $6.60 · Opus 5.5 ≈ $13 | Anthropic API billing, separate from the Claude subscription. User chooses in Phase 0. |
| Claude Code sessions | unchanged | 5 routines/day + one session per phase |

## 9. Risks and how the plan handles them

- **Edge decays before we can act** → measured explicitly (h1 vs slot entry). If only h1 shows edge, Phase 6 (script-only crypto lane) is the only honest option and it is an explicit user decision because it breaks "the model judges".
- **Look-ahead / survivorship in scoring** → prices only from Alpaca bars after the fact; unscorable signals counted; buckets fixed in advance.
- **Prompt injection via headlines** → headline text is data; classifier output is schema-constrained; no shell ever sees it; routines keep COMMON rule 5.
- **Git noise** → one commit per scan with new data (~20–40/day). Routine cadence checks match exact subjects, so they are unaffected. If history growth becomes a problem, scanner commits move to a `data` branch (dated amendment).
- **Crypto overnight gaps** → `stop_limit` can be jumped; sizes are small (≤ 8%) and the Phase 5 gate requires the bucket to have earned its place net of this.
- **PDT** → N8 plus the existing `daytrade_count` guard.
- **Actions cron drift** → heartbeat on the dashboard and in the watchdog; uptime is part of the gate.

## 10. Phases (one session each; prompts in `phase-N-*.md`)

| Phase | Deliverable | Session model / effort | Exit test |
|-------|-------------|------------------------|-----------|
| 0 | User prerequisites: secrets, API key, Pages, amendments | user, no session | checklist in `phase-0-prereqs.md` ticked |
| 1 | Scanner plumbing: `alpaca.sh news/crypto-price/crypto-bars`, `newsscan.py` ingest + snapshots (no LLM), universe file, `newsscan.yml`, mock + offline tests, watchdog heartbeat | Opus 5.5 / high | 24 h of raw headlines committed by Actions, zero failed runs |
| 2 | Classifier: `claude.sh`, prompt + schema, signals file, novelty/dedup, Discord rules | Opus 5.5 / xhigh | 3 days of signals, schema failure rate < 2%, alerts ≤ 5/day |
| 3 | Scorer: `newsscore.py`, outcomes, scorecard MD+JSON, `newsscore.yml`, weekly-review STEP | Opus 5.5 / xhigh | scorecard reproduces by hand for 5 sampled signals |
| 4 | Dashboard: `dashboard.py`, static site, `pages.yml` | Opus 5.5 / high | live URL shows equity vs SPY, cadence, signals, scorecard, heartbeat |
| 5 | Paper execution (only after the §6 gate **and** the user's strategy amendment) | Opus 5.5 / xhigh | first news trade with stop verified in the same run |
| 6 | Optional: 15-minute crypto lane in Actions (script-only) | decide only with data | — |

Phases 1–4 can run in any order after 1, but 1 → 2 → 3 → 4 keeps each session smallest. Start Phase 4 early if you want the dashboard for Phase 1b itself: its first version needs only `memory/` data that already exists.

## 11. Handoff protocol (every phase session)

1. Read `CLAUDE.md`, this file, `STATUS.md`, and your `phase-N-*.md`. Read other files only when the phase file names them. Do not read whole logs.
2. You are a **development session authorised by the user** to change scripts, routines and workflows for this phase. The "never edit scripts/routines" rule in `CLAUDE.md` binds the trading routines, not you. You still never edit `TRADING-STRATEGY.md`, `KILL-SWITCHES.md`, `WATCHLIST.md`, `EVENTS.md` or `PROJECT-CONTEXT.md` — propose text, the user commits it.
3. Work on branch `claude/news-sleeve-phase-N`, never on `main`. Keep the diff to the phase. Run `bash tests/offline.sh` and the phase's own tests before every push.
4. Finish by updating `STATUS.md` (done / deviations / how the user verifies / open questions / what the next phase must know), then open a PR titled `News sleeve — Phase N: <title>` with the verification steps in the body.
5. Honesty rules from `CLAUDE.md` apply: failed commands are reported as failed; nothing is marked done that was not run.

## Amendments
- (none yet — add dated entries here; §6 changes need a fresh out-of-sample window)
