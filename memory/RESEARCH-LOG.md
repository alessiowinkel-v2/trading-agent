# Research Log

One entry per trading day, written by the pre-market routine. Market-open executes the `CANDIDATE:` lines of today's entry; nothing else.
Read with `bash scripts/memtail.sh memory/RESEARCH-LOG.md 1` (today) — never the whole file. Phase 1 log: `memory/archive/phase1-2026/RESEARCH-LOG.md`.

## Entry format

```
## YYYY-MM-DD — Pre-market Research

### Preflight
NOW_ET=… | EVENT_TODAY=… | PAUSED=… | MISSING_COMMITS=…

### Regime and sectors
(paste `python3 scripts/screen.py sectors` output)

### Kill switches and core
(paste the ks.py lines: failing switches, ORDERS/BUYS/SAT flags, CORE, CORE_ACTION, MAINTENANCE)

### Screen
(paste the summary line + top-10 table of `python3 scripts/screen.py watchlist`)

### Yesterday's candidates
- SYM: FILLED / not filled: <reason> / dropped: <gate>

### Candidates (≥2, from ≥2 sectors)
#### 1. SYM — Name (sector ETF, rank N)
(paste `python3 scripts/screen.py candidate SYM` table, ending in its SCREEN_OK: line)
| G6 | PASS/FAIL | next earnings YYYY-MM-DD (confirmed/estimated) vs EARNINGS_OK_FROM — source [n] |
| G7 | PASS/FAIL | thesis in 2–3 sentences naming the specific driver |
- Catalysts last 7 days: … [n]
- Risk (what would make this wrong): …
CANDIDATE: SYM ref=123.45 stop_pct=8.2 sector=XLK g6=PASS g7=PASS
(only when G6 and G7 both passed — market-open can buy nothing else)

### Rejected screen passers
- SYM: G6 (earnings 2026-11-04) / G7 (no specific driver found) — one line each

### Decision
PLAN: core <CORE_ACTION summary or "in band">; satellites <SYM, SYM or none>
or
HOLD justified: core in band; every passer failed a named gate (see above)

Health: run HH:MM ET | preflight=N | mode=PAPER | ks=<n failing> | perplexity=ok|fallback
```

---

## 2026-10-27 — Phase 1b baseline (no research yet)
Log restarted for Phase 1b. First real entry is written by the first pre-market run.
