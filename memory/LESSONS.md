# Lessons

What the agent has learned. Every routine reads the "Standing lessons" section (first ~60 lines) and the newest dated entries (`bash scripts/memtail.sh memory/LESSONS.md 3`).
Append new dated entries at the bottom. A lesson may suggest a rule; only the user changes TRADING-STRATEGY.md.
Full Phase-1 lessons (359 lines) are archived in `memory/archive/phase1-2026/LESSONS.md`.

## Standing lessons

### Phase 1 in one paragraph (2026-05-27 → 09-18)
81 trading days, zero trades, while SPY rose. No single gate was wrong; the system was. The executor fired at 9:45 ET and exited before 10:00, never committing a record. Research kept one candidate (XOM, gated on WTI > $90) and, when oil finally cleared the bar in September, vetoed it nine times as a "fragile premium" — XOM then went $164 → $184. Timing blocks were widened far beyond the written rule. Prices came from a search engine and were wrong by $5–9. Ten weeks of escalations went to a file nobody read, and the routines were eventually deleted without anyone noticing. Rebuild principles: the core is always invested; scripts compute, the agent judges; every run records and commits; every failure alerts a human.

### Carried forward
- **0% is not neutral** (05-27, 05-29). Flat while SPY rises is a relative loss. Patience means avoiding bad trades, not all trades.
- **Plans need outcome records** (06-02, 06-28). A plan without a logged decision is unfalsifiable. Every planned order gets an outcome line: filled, not filled and why, or dropped and which gate.
- **Deferral is avoidance** (06-05). A candidate that keeps passing but never executes is a process failure. No narrative vetoes on a full PASS.
- **Use blocks to build the pipeline** (06-21). Event days are research days; the next session should execute, not start from scratch.
- **A selloff after good news is information** (07-03). Two down days on an earnings beat means the market is repricing the thesis, not offering a discount.
- **Compute percentages from the prices you cite** (07-10). Better: let `ks.py` compute them and copy its output.
- **Re-flagging is not screening** (07-17). A name worth mentioning gets a full gate table the same session, or it is dropped.
- **Breadth beats a single candidate** (08-16). Each rejection can be right while the pipeline is still wrong. Keep ≥2 candidates across ≥2 sectors.
- **Correct gates can still fail the mission** (08-21). A gate that never fires across a whole window is mis-calibrated, however "disciplined" it looks.
- **Silence is the worst failure** (09-06, 09-18). A missing run or an unread alert is worse than a bad trade: it can't be graded and it hides risk. Every run commits; failures alert the user directly.
- **Quote command output verbatim; delete debris instead of re-deriving it** (PAUSED.flag thread, Jun–Sep).

### Pre-loaded (kept)
- **Survivorship bias is real.** Past winners are visible; the losers were delisted and forgotten.
- **A 30-day track record proves nothing.** Judge process quality, not month-to-month outcomes.
- **Stops prevent catastrophe; they don't optimise.** Never move a stop down or widen it to avoid a loss.
- **Earnings are volatility, not edge.** Hence gate G6.
- **Tight stops shake you out of winners.** Initial stops are 7–10% (ATR-based); tighten only at +15% / +20%.
- **Options destroy compound returns.** Absolute prohibition, enforced by `alpaca.sh`.
- **The model itself can drift.** If behaviour changes after a model update, flag it in the weekly review.
- **Paper habits become real habits.** Every paper order is treated as real money.
- **Idle capital was Phase 1's most expensive habit** (replaces "doing something is the most expensive habit").

### Superseded Phase-1 lessons (do not apply)
- 06-05 "NFP timing blocks earn their keep" / "Cash IS a position in event-dense weeks" — blocks cost far more than they saved; only FOMC/CPI/NFP days block, and the core is always held.
- 06-12, 09-13, 09-18 "geopolitical premiums are fragile" — a narrative veto on a gate PASS is no longer allowed.
- 06-21 "update the sector list after FOMC" — sector ranks are computed daily by screen.py.
- 06-28 "P/E > 50 needs a tighter entry" — not checkable by the tools; the ATR stop and G4 replace it.
- 07-10 "passive-flow events are not catalysts" — not disqualifying; the gates decide.
- 09-18 "not carrying forward a conditional plan avoids documentation gaps" — fixed by design: every run records.

## Blacklist (tickers to avoid)
Currently empty. Add a ticker with a reason only after repeated bad decisions on it (user approval).

## Format for new entries

```
## YYYY-MM-DD — Lesson title
**Context**: what happened (with numbers from the logs)
**Insight**: what we learned
**Suggested rule change**: none / proposal for the user (never edit the strategy yourself)
```

---

## 2026-10-27 — Phase 1b reset
**Context**: Phase 1 placed zero trades in 81 days; root causes listed under "Standing lessons". The system was rebuilt: deterministic scripts for every number, a core index sleeve that is always held, a closed list of timing blocks, real-time alerts, a GitHub watchdog, and a $2,000 paper account that mirrors the planned live size.
**Insight**: The failure was structural, not a bad call. Judge Phase 1b on execution fidelity first: did every plan produce an outcome, every fill a stop, every run a commit?
**Suggested rule change**: none.

## 2026-10-30 — Unplanned orders need a source
**Context**: 10-29 midday found two open buys created 07:59 UTC, before any routine ran (`test-2026-10-29-dup`, `sat-2026-10-29-WMT-extra`); both cancelled, origin unknown. A WMT fill would have been a satellite with no stop.
**Insight**: Midday's open-order sweep caught it. Anything unplanned in the order book is a possible stop-less position, so it stays flagged until the user explains it.
**Suggested rule change**: none.

## 2026-11-06 — The core band can leave freed satellite cash idle
**Context**: ABBV stopped out 11-06 at 09:34 ET; EOD invested fell 86.7% → 72.1% (cash $540, 27.9%) while CORE_ACTION stayed HOLD (SPYM 53.7% vs target 56.6%, inside the ±5pp band) and NFP blocked re-entry.
**Insight**: With an empty satellite slot, the ±5pp core band plus an event block can park ~28% in cash for days, against "deployed > idle".
**Suggested rule change**: Consider core_band ±3pp, or a core top-up when a slot is empty and cash exceeds cash_min by a set amount.

## 2026-11-06 — Trailing stops fire in the opening minutes
**Context**: Both stop-outs this week (XLE 11-04 09:33 ET, ABBV 11-06 09:34 ET) filled within 4 minutes of the open, after prior-day selloffs (SPY -4.41% on 11-05).
**Insight**: 7% trailing stops are most exposed to the first minutes after a down day; the loss is the cost of the stop design, not an execution error. KS-11 is now at 2 of 3.
**Suggested rule change**: none (watch the pattern for another week before proposing).

## 2026-11-13 — Full slots plus min-size gate strand ~13% cash
**Context**: Week of 11-09: slots 3/3 from 11-09 open; cash $262.94 (13.3%) idle on all 5 EODs while every candidate failed G8 (qty 0 or qty 1-2 < 8% min) or G9. Core stayed HOLD (53.6% vs 55.0% target, inside ±5pp band). Bot -0.43pp vs SPY on the week.
**Insight**: With three small defensive satellites and a ~$263 budget, the system cannot deploy the last ~13% by either route; this is structural, repeating the 11-06 lesson.
**Suggested rule change**: Top up the core when slots are full and cash exceeds cash_min by a set amount, or narrow core_band to ±3pp.
