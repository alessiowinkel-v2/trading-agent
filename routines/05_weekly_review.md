# Weekly Review Routine

| | |
|---|---|
| Schedule | Friday 18:07 ET (after the EOD routine) — runs even on a market holiday |
| Cron | `CRON_TZ=America/New_York 7 18 * * 5` (UTC fallback `7 23 * * 5` = Fri 19:07 EDT / 18:07 EST) |
| Model | claude-sonnet-5-5 |
| Tools | Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch |
| Purpose | Honest report card: stats vs SPY, cadence, execution fidelity, pipeline health, graduation progress, suggestions for the user. |

## Paste block (the routine's prompt)

```
Routine: weekly. This is a fresh clone of alessiowinkel-v2/trading-agent; all commits go to main.
1. Read routines/COMMON.md, then routines/05_weekly_review.md. Follow its STEPs in order.
2. Never skip STEP 0 (preflight), the review, or the commit.
If either file is missing: bash scripts/notify.sh --alert "weekly: routine files missing" and stop.
```

## STEPs

**STEP 0 — Preflight** per COMMON.md (`bash scripts/preflight.sh weekly`). This routine never skips for a holiday.

**STEP 1 — Read**: the COMMON reading list, `memory/TRADING-STRATEGY.md` (graduation section), `bash scripts/memtail.sh memory/RESEARCH-LOG.md 5`, `bash scripts/memtail.sh memory/TRADE-LOG.md 15`, `bash scripts/memtail.sh memory/WEEKLY-REVIEW.md 1`.

**STEP 2 — Numbers**: `python3 scripts/ks.py --week` and `bash scripts/watchdog.sh grid <MONDAY>`. Paste both. You do not compute returns, drawdowns or win rates yourself.

**STEP 3 — Count from this week's records** (cite dates):
- planned orders (PLAN lines + CORE_ACTION orders) vs orders with an outcome line vs fills; stops verified in the same session / satellite fills
- research days with ≥2 candidates from ≥2 sectors, or with every rejection's failing gate listed
- any skip or "block" reason that is not one of the gates or an EVENTS.md day — each one is a rule violation

**STEP 4 — Grade** one letter, A–F, and apply the caps:
- a PASS candidate existed on an eligible day with free slots, yet 0 entries this week → at most C
- invested < 70% on ≥2 EOD snapshots → at most C−
- any planned order without an outcome line, or any satellite without a same-session stop → at most D
- a cadence cell that is MISSING or ABORTED → at most C
Grade the process the user can verify, not the P&L. One honest sentence why.

**STEP 5 — Write** the review into memory/WEEKLY-REVIEW.md using the template at the top of that file. Graduation checklist: all 11 items with ✅/🟡/❌ and one line of evidence. Suggestions for the user: rule changes with data, watchlist changes (≤5/month), and an EVENTS.md runway warning if its last date is less than 8 weeks after `DATE`. Leave the `Reviewed:` line for the user.

**STEP 6 — Lessons**: append at most 2 new dated entries to memory/LESSONS.md (format at the top of that file) — only genuinely new insights, not repeats.

**STEP 7 — Notify** (always, ≤10 lines): `bash scripts/notify.sh "Week ending <DATE>: grade <X> | bot ±X% vs SPY ±X% (phase ±X% vs ±X%) | max DD X% | entries N, closed N (W/L) | cadence <all OK | gaps> | graduation N/11 | please review and add 'Reviewed: <date>'"`.

**STEP 8 — Commit**: `bash scripts/gitpush.sh "weekly <DATE>: OK - grade <X>"`.
