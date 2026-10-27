# Phase 6 — optional 15-minute crypto lane (script-only execution)

**Only if** the scorecard shows a tradeable crypto bull bucket at the `crypto-15m` slot **and** no tradeable bucket at the routine slot — i.e. the edge exists but decays before a Claude routine can act. Otherwise skip this phase permanently.

Why it is separate: it breaks "scripts compute, the model judges". A script in GitHub Actions would place crypto orders every 15 minutes from scorecard rules alone. That is a different risk posture and needs the user's explicit decision, written as a dated amendment in PLAN.md.

If approved, the design is:
- `scripts/newsexec.py` runs at the end of each scanner run; it may only act on signals from tradeable `crypto-15m` buckets, with the Phase 5 `crypto-order` guards, ≤ 1 order per run, ≤ 2 open fast-lane positions, ≤ 5% of equity each, `stop_limit` at fill, time exit at `d3`, and a hard daily loss stop of 1% of equity for the lane (it then disables itself until the weekly review).
- Every order is recorded in TRADE-LOG by the script with the same fields a routine would write, and every fill is a Discord alert.
- The weekly review grades the lane separately; two consecutive weeks of negative net P&L disable it.

Write the session prompt for this phase only after the amendment exists.
