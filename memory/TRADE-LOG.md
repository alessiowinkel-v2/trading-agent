# Trade Log

Append-only record of every trade and daily EOD snapshot. Newest entries at the bottom; latest is what tomorrow's run will read for "yesterday's equity."

## Trade entry format

```
## [YYYY-MM-DD HH:MM ET] BUY/SELL TICKER

**Quantity**: N shares
**Price**: $X.XX (actual fill)
**Total**: $X,XXX.XX
**% of portfolio**: X.X%

**Thesis**: (2-3 sentences)
**Catalyst**: (specific reason for timing)
**Risk**: (what would make this wrong)
**Sector momentum**: (with us / against us / neutral)
**Stop level**: $X.XX (X% below entry)
**Target**: $X.XX (R:R = X:1)
**Exit plan**: (sell conditions)

**Kill switch check**: (all clear / which fired)
**Buy-side gate**: (all 9 checks passed)
```

## EOD snapshot format

```
### YYYY-MM-DD — EOD Snapshot (Day N, Weekday)
**Portfolio:** $X.XX | **Cash:** $X.XX (X%) | **Day P&L:** ±$X (±X%) | **Phase P&L:** ±$X (±X%) | **SPY today:** ±X.XX%

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |

**Notes:** One-paragraph plain-english summary.
**Active kill switches:** (none / list)
```

---

## Day 0 — EOD Snapshot (pre-launch baseline)
**Portfolio:** $10,000.00 | **Cash:** $10,000.00 (100%) | **Day P&L:** $0 | **Phase P&L:** $0 | **SPY today:** baseline

No positions yet. Bot launches on the next trading day.

**Notes:** Pre-launch baseline so Day 1's daily-summary routine has prior equity to compute Day P&L against.
**Active kill switches:** none.

---

### 2026-05-27 — EOD Snapshot (Day 1, Wednesday)
**Portfolio:** $10,000.00 | **Cash:** $10,000.00 (100%) | **Day P&L:** $0 (0.00%) | **Phase P&L:** $0 (0.00%) | **SPY today:** +0.61%

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| — | — | — | — | — | — | — |

**Notes:** First live trading day. No positions opened; account holds full $10,000 starting capital in cash. SPY gained +0.61% today while we held cash — we trail by 0.61% on Day 1, which is acceptable as no qualifying setups were identified today.
**Active kill switches:** none.
