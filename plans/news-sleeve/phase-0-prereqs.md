# Phase 0 — what only the user can do

Everything else in Phases 0–4 was done by the agent (amendments, universe, scripts, workflows, dashboard). Three items remain; none needs a Claude session.

## 1. GitHub Actions secrets (repo Settings → Secrets and variables → Actions → New repository secret)
- [ ] `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` — the **paper** keys the cloud environment already uses. Until they exist the `newsscan` and `newsscore` workflows exit with a warning and do nothing.
- [ ] `ANTHROPIC_API_KEY` — see item 2. Until it exists the scanner still runs; headlines wait up to 48 h for classification.
- `NOTIFY_WEBHOOK_URL` (and `NOTIFY_MENTION`) already exist for the watchdog.
- Optional repository **variable** `CLASSIFIER_MODEL` to override `claude-sonnet-5-5`.

## 2. Anthropic API key
- [ ] console.anthropic.com → API keys → create `trading-agent-classifier`, add ≈ $10 of credit (expected ≈ $9/month at ~300 headlines/day on Sonnet 5.5; Haiku ≈ $0.50). Billed separately from the Claude subscription.

## 3. Merge the PR, then check two things
- [ ] Merge `News sleeve — Phases 1–4` into `main`.
- [ ] Repo Settings → Pages → Source = **GitHub Actions** (required: the workflow token cannot switch Pages on). Until then each `pages` run succeeds with a warning and deploys nothing. The dashboard URL is printed by the deploy step (expected https://alessiowinkel-v2.github.io/trading-agent/).
- [ ] Actions → `newsscan` → Run workflow once by hand; a `newsscan <DATE> <HH:MM>Z: OK - …` commit should appear on `main` within a minute. The run then keeps going for ~5.5 h (it is a loop by design, PLAN D14) and the hourly schedule takes over.

Not needed: changing the Actions "workflow permissions" setting — each workflow declares the permissions it needs.
