# Phase 5 — paper execution of the news sleeve

**Do not start this phase unless both are true**: `memory/NEWS-SCORECARD.md` says `GATE: MET`, and the user has committed the news-sleeve rules (PLAN §7, finalised) into `memory/TRADING-STRATEGY.md` with a `params` block extension and updated `memory/PROJECT-CONTEXT.md`. The session must stop and say so if either is missing.

## Session prompt
```
You are a development session for alessiowinkel-v2/trading-agent, authorised by the user to implement Phase 5 of the news sleeve.
1. Read CLAUDE.md, plans/news-sleeve/PLAN.md (§6, §7 especially), plans/news-sleeve/STATUS.md, plans/news-sleeve/phase-5-execution.md, memory/TRADING-STRATEGY.md (news sleeve section + params), memory/KILL-SWITCHES.md, memory/NEWS-SCORECARD.md.
2. Verify the two preconditions in the phase file. If either fails, write that in STATUS.md and stop.
3. Work on branch claude/news-sleeve-phase-5. Never push to main. First action: create a scheduled task bound to this session (create_trigger, cron "0 */4 * * *", initiation human_request) whose prompt says "resume Phase 5 of plans/news-sleeve from STATUS.md; if the phase is done and its PR is open, disable this task" — this is how the work survives Claude usage limits. Finish with STATUS.md updated and a PR titled "News sleeve — Phase 5: paper execution".
```

## Read first
`scripts/ks.py` (whole file: `check`, `maintenance`, `kill_switches`, `write_state`, `reconcile`), `scripts/alpaca.sh` (whole file), `routines/02_market_open.md`, `routines/03_midday.md`, `routines/COMMON.md`, `tests/offline.sh`, `tests/mock_alpaca.py`.

## Build
1. **`ks.py --news-check`**: reads the latest scorecard's tradeable buckets and the open signals since the previous routine slot; prints an N1–N8 table per candidate (PLAN §7), `VERDICT BUY|SKIP`, sizing from the news-sleeve params, and the exact order command(s): stocks → existing `alpaca.sh order` buy + `THEN` trailing stop; crypto → `alpaca.sh crypto-order` buy + `THEN` `stop_limit`. Also prints `NEWS_EXITS` for positions whose `d3` slot has arrived (N7). Nothing is executed by ks.py.
2. **`alpaca.sh crypto-order '<json>'`** — a separate command with its own guard: pair must be in NEWS-UNIVERSE; `client_order_id` `news-<DATE>-<PAIR>`; buys: `type=limit`, `time_in_force=gtc`, notional ≤ `news_crypto_max_pct × equity` and ≤ cash − reserve, no margin ever; sells: ≤ position, `stop_limit` with `stop_price` ≥ 0.90 × last and `limit_price` ≥ 0.985 × `stop_price`, or `limit` for exits; `ALPACA_DRY_RUN` honoured; `REFUSED` semantics identical to stock orders. The stock `guard_order` is not modified.
3. **Crypto awareness in ks.py**: positions with `asset_class = crypto` count in invested %, sleeve caps and KS-8 reconciliation; `KS-10` for a crypto news position means "no open `stop_limit` covering it" (the maintenance command re-places it); KS-7 staleness for crypto uses 5 minutes.
4. **Routines**: market-open and midday get a `STEP 5b — News sleeve` that runs `--news-check`, executes printed commands exactly, verifies stops, records a `| News | …` table in TRADE-LOG (same columns as satellites plus `signal id`, `bucket`), and uses `--alert` on any REFUSED/rejected. EOD gets `NEWS_EXITS` for the next day's plan. Weekly review grades the sleeve with the same caps (planned order without outcome → max D; position without stop → max D).
5. **Dashboard**: news positions and their exit date appear in the positions table; sleeve P&L vs its benchmark on a separate tile.
6. **Tests**: mock positions with a crypto leg; N-gate table for one tradeable and one non-tradeable bucket; crypto-order guard refusals (wrong pair, margin, short, missing id, bad stop); N8 same-day exit refused; offline suite green.

## Acceptance
- Dry-run of a full market-open with one news candidate shows the N table, the buy, the stop, the record and the notification.
- First real paper fill (after merge, on a trading day) has its stop verified in the same run and appears on the dashboard within one build.
- STATUS note lists every rule in PLAN §7 that the implementation enforces and where (file:line).
