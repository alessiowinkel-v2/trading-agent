# Phase 0 — user prerequisites (no Claude session needed)

Tick everything before starting Phase 1. Items marked (P2) can wait until Phase 2, (P4) until Phase 4.

## Accounts and secrets
- [ ] **Anthropic API key** (P2): console.anthropic.com → API keys → new key, named `trading-agent-classifier`. Put $10 of credit on it. This is billed separately from the Claude subscription (PLAN §8).
- [ ] **GitHub → repo Settings → Secrets and variables → Actions**: add `ALPACA_API_KEY`, `ALPACA_SECRET_KEY` (the paper keys — the same ones the cloud environment uses), `ANTHROPIC_API_KEY` (P2). `NOTIFY_WEBHOOK_URL` already exists for the watchdog.
- [ ] **GitHub → repo Settings → Pages** (P4): Source = **GitHub Actions**. Nothing else.
- [ ] **GitHub → repo Settings → Actions → General**: Workflow permissions = **Read and write** (the scanner commits to `main`). Allow GitHub Actions to create and approve pull requests: not needed.

## Decisions to write down (reply in the Phase 1 session prompt or edit PLAN.md §0)
- [ ] Classifier model (`CLASSIFIER_MODEL`): `claude-sonnet-5-5` (plan default, ≈ $7/month), `claude-haiku-5-5` (≈ $0.35/month), or `claude-opus-5-5` (≈ $13/month).
- [ ] Discord alert budget: 5/day (plan default) or another number.
- [ ] Crypto pairs to scan: BTC/USD, ETH/USD, SOL/USD (plan default). Scanning is not trading.

## Rule amendments (you edit, the agent may not)
- [ ] `memory/PROJECT-CONTEXT.md` → "Out of scope": change "crypto" to "crypto trading (crypto news is scanned and scored from Phase 1 of the news sleeve; trading only after PLAN §6 and a strategy amendment)". Commit to `main`.
- [ ] `CLAUDE.md` first paragraph: append "A news-signal research sleeve runs beside it; see `plans/news-sleeve/PLAN.md`. It places no orders until Phase 5." Commit to `main`.
- [ ] Nothing in `TRADING-STRATEGY.md` changes until Phase 5.

## How to run a phase session
1. New Claude Code cloud session on this repo, model **Claude Opus 5.5**, effort as the PLAN §10 table says (set it with `/model` or `/config` in the session; the prompt cannot set it).
2. Paste the "Session prompt" block from the phase file. Nothing else.
3. When the PR arrives: read `STATUS.md`'s new handoff note, run the "How the user verifies" steps, merge, then start the next phase in a **new** session.
