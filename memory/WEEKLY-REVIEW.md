# Weekly Review

Written every Friday evening by the weekly routine. Numbers come from `python3 scripts/ks.py --week` and `bash scripts/watchdog.sh grid <monday>`; judgement is the agent's, sign-off is the user's.
Phase 1 reviews: `memory/archive/phase1-2026/WEEKLY-REVIEW.md`.

## Template

```
## Week ending YYYY-MM-DD

### Stats
(paste `python3 scripts/ks.py --week` WEEK STATS table)

### Cadence
(paste `bash scripts/watchdog.sh grid <monday>` — every cell must be OK or SKIPPED)

### Execution
- Planned orders: N | with an outcome line: N | filled: N | stops verified same session: N/N
- Per closed trade: thesis followed? stop honoured? sized per G8? one line each

### Pipeline
- Research days with ≥2 candidates from ≥2 sectors (or every rejection's gate listed): N/5
- Timing blocks cited outside EVENTS.md: N (must be 0)

### News sleeve
(paste the GATE line, counts and tradeable buckets from `bash scripts/memtail.sh memory/NEWS-SCORECARD.md 1`, or "scorer not yet running")

### Grade: <A–F>
Caps applied: none / "PASS candidate with free slots but 0 entries → max C" / "invested < 70% on ≥2 EODs → max C−" / "planned order without outcome → max D"
One honest sentence on why.

### What worked (≤3) / What didn't (≤3)

### Lessons (also appended to LESSONS.md)

### Suggestions for the user (never applied by the agent)
- … (include: EVENTS.md runway if < 8 weeks of dates remain; watchlist changes, max 5/month)

### Graduation checklist (TRADING-STRATEGY.md)
1–11: ✅ / 🟡 / ❌ with one line of evidence each

Reviewed: (the user adds "Reviewed: YYYY-MM-DD" here)
```

---
