# Stress Test Checklist

Work through this before trusting the routines, and again after any change to scripts or routines.

## 1. Local (with `.env` pointing at the $2,000 paper account)
- [ ] `bash scripts/selftest.sh --notify` — all PASS; the test message arrives in Discord/Slack; the bad-webhook test exits 2
- [ ] `bash scripts/selftest.sh --orders` — far-off order accepted, duplicate `client_order_id` rejected by Alpaca, cancel confirmed
- [ ] `bars SPY 250` returned 250 bars from SIP (no "fell back to IEX" line). If it fell back, liquidity gate G2 is skipped — note it
- [ ] `python3 scripts/screen.py watchlist` prints a top-10 table with names from ≥2 sectors
- [ ] `python3 scripts/ks.py` shows KS-9 PASS (account number and $2,000 equity match PROJECT-CONTEXT.md)
- [ ] `bash scripts/perplexity.sh -r day --text "…"` answers with sources (if it fails: Sonar may have moved to the Agent API — fix the script before go-live)

## 2. Cloud plumbing ("Run now", outside market hours)
- [ ] Each routine 01 → 05 produces exactly one commit on `main` in the convention and one webhook message
- [ ] Outside market hours, market-open and midday commit `SKIPPED - market closed at run time` (exit 31)
- [ ] No `.env` created; no commit touches anything outside `memory/`
- [ ] The run logs (claude.ai/code/routines → run) show preflight output and no permission prompts waiting
- [ ] The routine's `CRON_TZ=America/New_York` schedule was accepted (or the UTC fallback is in place and noted)
- [ ] GitHub → Actions → watchdog → "Run workflow" (mode nightly) on a day with all four commits: green

## 3. Day-1 mechanics test (first trading day, then cancel)
- [ ] Market-open bought the core (SPYM) to target with a limit order and logged the fill
- [ ] Manually, in a local shell: place a 1-share trailing stop on SPYM
      `bash scripts/alpaca.sh order '{"symbol":"SPYM","qty":"1","side":"sell","type":"trailing_stop","trail_percent":"10","time_in_force":"gtc","client_order_id":"test-<DATE>-trail"}'`
      → `order-get <id>` shows status new/accepted/held with `hwm` and `stop_price` → `cancel <id>` (the core never keeps a stop). Record both ids in TRADE-LOG.
- [ ] The EOD message shows equity, day P&L, SPY day return and invested % — compare with the Alpaca dashboard

## 4. Failure drills (paper)
- [ ] **Pause**: commit `memory/PAUSED.flag` → next run reports PAUSED, `alpaca.sh` refuses buys, stops still work → delete it
- [ ] **Bad key**: set `ALPACA_SECRET_KEY` wrong in the environment → run now → preflight exits 40 (or 10), user alerted, ABORTED commit, no orders → restore
- [ ] **Wrong account**: put a wrong `account_number` in PROJECT-CONTEXT.md → ks.py shows KS-9 FAIL, `ORDERS_ALLOWED=no` → restore
- [ ] **Missing run**: disable one routine for a day → the next routine's preflight alerts `MISSING_COMMITS`, the nightly watchdog alerts and its job fails (GitHub email)
- [ ] **Bad webhook**: wrong `NOTIFY_WEBHOOK_URL` → commit subjects show `notify=FAILED`; the watchdog still reaches you by GitHub email
- [ ] **Orphan stop**: cancel a satellite's stop by hand → next midday/EOD shows KS-10 FAIL and re-places it
- [ ] **Concurrent runs**: "Run now" the same routine twice within a minute → both commits land (rebase), no duplicate orders (client_order_id)

## 5. First weeks (soft launch)
- [ ] Every research entry has ≥2 candidates from ≥2 sectors or each rejection's failing gate
- [ ] Every CANDIDATE line has an outcome line the next day
- [ ] Every satellite fill has a stop id recorded in the same run
- [ ] No timing block cited outside EVENTS.md
- [ ] First EST day (2026-11-02, if on UTC fallback crons): health footers show the expected ET times
- [ ] Friday review grades the process honestly and the cadence grid is all OK/SKIPPED

## Red flags — commit `memory/PAUSED.flag` and review
- The agent invents data when a script fails, or edits rules, scripts or routines
- An order not printed by ks.py, or an order that alpaca.sh refused being retried in another form
- A satellite without a stop after a run ends
- Self-grades higher than the cadence grid and execution counts justify
- Records getting shorter or vaguer over time; the same lesson repeating weekly
- Position sizes or trade counts creeping up; any attempt at margin, shorts or options
- Any `.env` in the cloud workspace, any force-push
