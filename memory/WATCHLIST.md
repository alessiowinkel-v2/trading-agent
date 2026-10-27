# Watchlist

The satellite universe. `scripts/screen.py` screens every row below plus the 11 sector ETFs (XLK XLF XLE XLV XLI XLY XLP XLU XLB XLRE XLC) every morning.
Gate G1 drops names whose share price exceeds 15% of equity (≈$300 at $2,000) automatically — the expensive names stay listed for when capital grows.

Rules: the agent may propose additions/removals in the Friday review (max 5 per month, with a reason); the user edits this table. Keep the column order — `tlib.py` parses it.
"Earnings months" is a hint only: gate G6 must still confirm the actual date.

| Ticker | Sector ETF | Name | Earnings months (hint) | Added | Note |
|--------|------------|------|------------------------|-------|------|
| NVDA | XLK | NVIDIA | Feb May Aug Nov | 2026-10-27 | |
| AVGO | XLK | Broadcom | Mar Jun Sep Dec | 2026-10-27 | |
| MSFT | XLK | Microsoft | Jan Apr Jul Oct | 2026-10-27 | |
| AMD | XLK | Advanced Micro Devices | Feb May Aug Nov | 2026-10-27 | |
| ORCL | XLK | Oracle | Mar Jun Sep Dec | 2026-10-27 | |
| ANET | XLK | Arista Networks | Feb May Aug Nov | 2026-10-27 | |
| PLTR | XLK | Palantir | Feb May Aug Nov | 2026-10-27 | |
| GOOGL | XLC | Alphabet | Feb Apr Jul Oct | 2026-10-27 | |
| META | XLC | Meta Platforms | Jan Apr Jul Oct | 2026-10-27 | |
| NFLX | XLC | Netflix | Jan Apr Jul Oct | 2026-10-27 | |
| TMUS | XLC | T-Mobile US | Jan Apr Jul Oct | 2026-10-27 | |
| AMZN | XLY | Amazon | Feb Apr Jul Oct | 2026-10-27 | |
| TSLA | XLY | Tesla | Jan Apr Jul Oct | 2026-10-27 | |
| HD | XLY | Home Depot | Feb May Aug Nov | 2026-10-27 | |
| TJX | XLY | TJX Companies | Feb May Aug Nov | 2026-10-27 | |
| CMG | XLY | Chipotle | Feb Apr Jul Oct | 2026-10-27 | |
| JPM | XLF | JPMorgan Chase | Jan Apr Jul Oct | 2026-10-27 | |
| GS | XLF | Goldman Sachs | Jan Apr Jul Oct | 2026-10-27 | |
| BAC | XLF | Bank of America | Jan Apr Jul Oct | 2026-10-27 | |
| V | XLF | Visa | Jan Apr Jul Oct | 2026-10-27 | |
| MA | XLF | Mastercard | Jan Apr Jul Oct | 2026-10-27 | |
| SCHW | XLF | Charles Schwab | Jan Apr Jul Oct | 2026-10-27 | |
| LLY | XLV | Eli Lilly | Feb Apr Aug Oct | 2026-10-27 | |
| UNH | XLV | UnitedHealth | Jan Apr Jul Oct | 2026-10-27 | |
| ABBV | XLV | AbbVie | Feb Apr Jul Oct | 2026-10-27 | |
| JNJ | XLV | Johnson & Johnson | Jan Apr Jul Oct | 2026-10-27 | |
| ISRG | XLV | Intuitive Surgical | Jan Apr Jul Oct | 2026-10-27 | |
| VRTX | XLV | Vertex Pharmaceuticals | Feb May Aug Nov | 2026-10-27 | |
| CAT | XLI | Caterpillar | Feb Apr Aug Oct | 2026-10-27 | |
| GE | XLI | GE Aerospace | Jan Apr Jul Oct | 2026-10-27 | |
| DE | XLI | Deere | Feb May Aug Nov | 2026-10-27 | |
| ETN | XLI | Eaton | Feb May Aug Nov | 2026-10-27 | |
| RTX | XLI | RTX | Jan Apr Jul Oct | 2026-10-27 | |
| UNP | XLI | Union Pacific | Jan Apr Jul Oct | 2026-10-27 | |
| PWR | XLI | Quanta Services | Feb May Aug Nov | 2026-10-27 | |
| XOM | XLE | Exxon Mobil | Jan May Aug Oct | 2026-10-27 | |
| CVX | XLE | Chevron | Jan May Aug Oct | 2026-10-27 | |
| COP | XLE | ConocoPhillips | Feb May Aug Nov | 2026-10-27 | |
| EOG | XLE | EOG Resources | Feb May Aug Nov | 2026-10-27 | |
| SLB | XLE | SLB | Jan Apr Jul Oct | 2026-10-27 | |
| COST | XLP | Costco | Mar May Sep Dec | 2026-10-27 | |
| WMT | XLP | Walmart | Feb May Aug Nov | 2026-10-27 | |
| PG | XLP | Procter & Gamble | Jan Apr Jul Oct | 2026-10-27 | |
| KO | XLP | Coca-Cola | Feb Apr Jul Oct | 2026-10-27 | |
| PM | XLP | Philip Morris | Feb Apr Jul Oct | 2026-10-27 | |
| NEE | XLU | NextEra Energy | Jan Apr Jul Oct | 2026-10-27 | |
| SO | XLU | Southern Company | Feb Apr Jul Oct | 2026-10-27 | |
| CEG | XLU | Constellation Energy | Feb May Aug Nov | 2026-10-27 | |
| VST | XLU | Vistra | Feb May Aug Nov | 2026-10-27 | |
| LIN | XLB | Linde | Feb May Aug Oct | 2026-10-27 | |
| FCX | XLB | Freeport-McMoRan | Jan Apr Jul Oct | 2026-10-27 | |
| NEM | XLB | Newmont | Feb Apr Jul Oct | 2026-10-27 | |
| NUE | XLB | Nucor | Jan Apr Jul Oct | 2026-10-27 | |
| PLD | XLRE | Prologis | Jan Apr Jul Oct | 2026-10-27 | |
| AMT | XLRE | American Tower | Feb Apr Jul Oct | 2026-10-27 | |
| WELL | XLRE | Welltower | Feb Apr Jul Oct | 2026-10-27 | |
| EQIX | XLRE | Equinix | Feb Apr Jul Oct | 2026-10-27 | |

## Changelog
- 2026-10-27: initial list (57 names) for Phase 1b.
