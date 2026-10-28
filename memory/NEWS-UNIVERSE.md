# News Universe

The symbols the news sleeve scans (`scripts/newsscan.py`) and scores (`scripts/newsscore.py`). Scanning is not trading: nothing here authorises an order. See `plans/news-sleeve/PLAN.md` §2.
Owner: the user. The agent may propose additions/removals in the Friday review; keep the column order — `scripts/newslib.py` parses it. `News symbol` is the tag Alpaca/Benzinga uses (crypto pairs are tagged without the slash).

## Stocks, sector ETFs and index proxies

| Ticker | Asset | News symbol | Group | Added | Note |
|--------|-------|-------------|-------|-------|------|
| NVDA | stock | NVDA | XLK | 2026-10-27 | NVIDIA |
| AVGO | stock | AVGO | XLK | 2026-10-27 | Broadcom |
| MSFT | stock | MSFT | XLK | 2026-10-27 | Microsoft |
| AMD | stock | AMD | XLK | 2026-10-27 | Advanced Micro Devices |
| ORCL | stock | ORCL | XLK | 2026-10-27 | Oracle |
| ANET | stock | ANET | XLK | 2026-10-27 | Arista Networks |
| PLTR | stock | PLTR | XLK | 2026-10-27 | Palantir |
| GOOGL | stock | GOOGL | XLC | 2026-10-27 | Alphabet |
| META | stock | META | XLC | 2026-10-27 | Meta Platforms |
| NFLX | stock | NFLX | XLC | 2026-10-27 | Netflix |
| TMUS | stock | TMUS | XLC | 2026-10-27 | T-Mobile US |
| AMZN | stock | AMZN | XLY | 2026-10-27 | Amazon |
| TSLA | stock | TSLA | XLY | 2026-10-27 | Tesla |
| HD | stock | HD | XLY | 2026-10-27 | Home Depot |
| TJX | stock | TJX | XLY | 2026-10-27 | TJX Companies |
| CMG | stock | CMG | XLY | 2026-10-27 | Chipotle |
| JPM | stock | JPM | XLF | 2026-10-27 | JPMorgan Chase |
| GS | stock | GS | XLF | 2026-10-27 | Goldman Sachs |
| BAC | stock | BAC | XLF | 2026-10-27 | Bank of America |
| V | stock | V | XLF | 2026-10-27 | Visa |
| MA | stock | MA | XLF | 2026-10-27 | Mastercard |
| SCHW | stock | SCHW | XLF | 2026-10-27 | Charles Schwab |
| LLY | stock | LLY | XLV | 2026-10-27 | Eli Lilly |
| UNH | stock | UNH | XLV | 2026-10-27 | UnitedHealth |
| ABBV | stock | ABBV | XLV | 2026-10-27 | AbbVie |
| JNJ | stock | JNJ | XLV | 2026-10-27 | Johnson & Johnson |
| ISRG | stock | ISRG | XLV | 2026-10-27 | Intuitive Surgical |
| VRTX | stock | VRTX | XLV | 2026-10-27 | Vertex Pharmaceuticals |
| CAT | stock | CAT | XLI | 2026-10-27 | Caterpillar |
| GE | stock | GE | XLI | 2026-10-27 | GE Aerospace |
| DE | stock | DE | XLI | 2026-10-27 | Deere |
| ETN | stock | ETN | XLI | 2026-10-27 | Eaton |
| RTX | stock | RTX | XLI | 2026-10-27 | RTX |
| UNP | stock | UNP | XLI | 2026-10-27 | Union Pacific |
| PWR | stock | PWR | XLI | 2026-10-27 | Quanta Services |
| XOM | stock | XOM | XLE | 2026-10-27 | Exxon Mobil |
| CVX | stock | CVX | XLE | 2026-10-27 | Chevron |
| COP | stock | COP | XLE | 2026-10-27 | ConocoPhillips |
| EOG | stock | EOG | XLE | 2026-10-27 | EOG Resources |
| SLB | stock | SLB | XLE | 2026-10-27 | SLB |
| COST | stock | COST | XLP | 2026-10-27 | Costco |
| WMT | stock | WMT | XLP | 2026-10-27 | Walmart |
| PG | stock | PG | XLP | 2026-10-27 | Procter & Gamble |
| KO | stock | KO | XLP | 2026-10-27 | Coca-Cola |
| PM | stock | PM | XLP | 2026-10-27 | Philip Morris |
| NEE | stock | NEE | XLU | 2026-10-27 | NextEra Energy |
| SO | stock | SO | XLU | 2026-10-27 | Southern Company |
| CEG | stock | CEG | XLU | 2026-10-27 | Constellation Energy |
| VST | stock | VST | XLU | 2026-10-27 | Vistra |
| LIN | stock | LIN | XLB | 2026-10-27 | Linde |
| FCX | stock | FCX | XLB | 2026-10-27 | Freeport-McMoRan |
| NEM | stock | NEM | XLB | 2026-10-27 | Newmont |
| NUE | stock | NUE | XLB | 2026-10-27 | Nucor |
| PLD | stock | PLD | XLRE | 2026-10-27 | Prologis |
| AMT | stock | AMT | XLRE | 2026-10-27 | American Tower |
| WELL | stock | WELL | XLRE | 2026-10-27 | Welltower |
| EQIX | stock | EQIX | XLRE | 2026-10-27 | Equinix |
| XLK | etf | XLK | XLK | 2026-10-27 | sector ETF |
| XLF | etf | XLF | XLF | 2026-10-27 | sector ETF |
| XLE | etf | XLE | XLE | 2026-10-27 | sector ETF |
| XLV | etf | XLV | XLV | 2026-10-27 | sector ETF |
| XLI | etf | XLI | XLI | 2026-10-27 | sector ETF |
| XLY | etf | XLY | XLY | 2026-10-27 | sector ETF |
| XLP | etf | XLP | XLP | 2026-10-27 | sector ETF |
| XLU | etf | XLU | XLU | 2026-10-27 | sector ETF |
| XLB | etf | XLB | XLB | 2026-10-27 | sector ETF |
| XLRE | etf | XLRE | XLRE | 2026-10-27 | sector ETF |
| XLC | etf | XLC | XLC | 2026-10-27 | sector ETF |
| SPY | index | SPY | - | 2026-10-27 | S&P 500 — market-wide stories map here |
| QQQ | index | QQQ | - | 2026-10-27 | Nasdaq-100 |
| IWM | index | IWM | - | 2026-10-27 | Russell 2000 |

## Crypto (scanned and scored; traded only after PLAN §6 + strategy amendment)

| Pair | Asset | News symbol | Benchmark | Added | Note |
|------|-------|-------------|-----------|-------|------|
| BTC/USD | crypto | BTCUSD | - | 2026-10-27 | benchmark for the other pairs; crypto-market stories map here |
| ETH/USD | crypto | ETHUSD | BTC/USD | 2026-10-27 | |
| SOL/USD | crypto | SOLUSD | BTC/USD | 2026-10-27 | |

## Changelog
- 2026-10-27: initial universe — 57 watchlist names, 11 sector ETFs, 3 index proxies, 3 crypto pairs.
