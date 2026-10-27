#!/usr/bin/env python3
"""Deterministic screens for the pre-market routine. The agent never computes
indicators by hand - it runs these and copies the output.

  python3 scripts/screen.py sectors               regime + ranked sector table
  python3 scripts/screen.py watchlist [--top 10]  gates G1-G5 + G8 sizing for every watchlist name
  python3 scripts/screen.py candidate SYM [SYM..] full gate table for chosen names (+ CANDIDATE line)

Equity for G1/G8 comes from the live account (override with --equity N).
Bars are completed daily sessions only (through yesterday), SIP when allowed.
"""

import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tlib  # noqa: E402

N_BARS = 260


def sector_table(bars):
    spy = tlib.closes(bars.get("SPY", []))
    s21, s63 = tlib.ret(spy, 21), tlib.ret(spy, 63)
    rows = []
    for etf in tlib.SECTOR_ETFS:
        c = tlib.closes(bars.get(etf, []))
        r21, r63 = tlib.ret(c, 21), tlib.ret(c, 63)
        row = {"etf": etf, "r21": r21, "r63": r63, "rs21": None, "rs63": None, "score": None,
               "rank": None, "label": "no data"}
        if None not in (r21, r63, s21, s63):
            row.update(rs21=r21 - s21, rs63=r63 - s63)
            row["score"] = 0.5 * row["rs21"] + 0.5 * row["rs63"]
        rows.append(row)
    ranked = sorted([r for r in rows if r["score"] is not None], key=lambda r: -r["score"])
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
        r["label"] = "Leading" if i <= 4 else "Neutral" if i <= 7 else "Lagging"
        if r["rs21"] > 0 > r["rs63"]:
            r["label"] += "/Improving"
    return ranked + [r for r in rows if r["score"] is None]


def evaluate(sym, sector, bars, spy_bars, ranks, equity, P, feed):
    """Gate results G1-G5 + G8 sizing for one symbol, all from completed bars."""
    res = {"sym": sym, "sector": sector, "rank": ranks.get(sector), "gates": {}, "ok": False}
    if len(bars) < 30:
        res["error"] = "only %d bars" % len(bars)
        return res
    c = tlib.closes(bars)
    last = c[-1]
    s20, s50, s200 = tlib.sma(c, 20), tlib.sma(c, 50), tlib.sma(c, 200)
    a = tlib.atr(bars, 14)
    r5, r21, r63 = tlib.ret(c, 5), tlib.ret(c, 21), tlib.ret(c, 63)
    sc = tlib.closes(spy_bars)
    rs21 = None if r21 is None else r21 - tlib.ret(sc, 21)
    rs63 = None if r63 is None else r63 - tlib.ret(sc, 63)
    hi52 = max(b["h"] for b in bars[-252:])
    adv = tlib.adv_usd(bars, 20)
    res.update(close=last, sma20=s20, sma50=s50, sma200=s200, atr=a, r5=r5, r21=r21, r63=r63,
               rs21=rs21, rs63=rs63, vs_high=last / hi52 - 1, adv=adv, date=bars[-1]["t"][:10])
    g = res["gates"]
    price_cap = P["sat_price_max_pct"] * equity
    if sector == "UNKNOWN":
        g["G1"] = (False, "%s is not in WATCHLIST.md or the sector ETFs" % sym)
    else:
        g["G1"] = (last <= price_cap, "close %s vs cap %s (%.0f%% of equity)"
                   % (tlib.fmt_usd(last), tlib.fmt_usd(price_cap), P["sat_price_max_pct"] * 100))
    if feed == "iex":
        g["G2"] = (True, "SKIPPED - IEX-only volume (SIP unavailable); watchlist names are pre-vetted large caps")
    else:
        g["G2"] = (adv is not None and adv >= P["min_adv_usd"],
                   "ADV20 $%.0fM vs $%.0fM" % ((adv or 0) / 1e6, P["min_adv_usd"] / 1e6))
    if s200 is None:
        g["G3"] = (False, "insufficient history for SMA200 (%d bars)" % len(c))
    else:
        g["G3"] = (last > s50 > s200, "close %.2f %s SMA50 %.2f %s SMA200 %.2f (needs close > SMA50 > SMA200)"
                   % (last, ">" if last > s50 else "<=", s50, ">" if s50 > s200 else "<=", s200))
    cap = s20 + P["chase_atr_mult"] * a
    g["G4"] = (r5 is not None and r5 <= P["chase_r5_max"] and last <= cap,
               "R5 %s (max +%.0f%%); close %.2f vs SMA20+%.0fxATR %.2f"
               % (tlib.fmt_pct(r5), P["chase_r5_max"] * 100, last, P["chase_atr_mult"], cap))
    rank = ranks.get(sector)
    g5 = (rank is not None and rank <= P["sector_rank_max"]) or (rs63 is not None and rs63 > P["rs63_override"])
    g["G5"] = (g5, "%s rank %s (max %d); RS63 %s (override > +%.0f%%)"
               % (sector, rank, P["sector_rank_max"], tlib.fmt_pct(rs63), P["rs63_override"] * 100))
    stop = min(max(P["stop_min"], P["stop_atr_mult"] * a / last), P["stop_max"])
    qty = int(math.floor(P["sat_max_pct"] * equity / last))
    size = qty * last
    size_ok = qty >= 1 and size >= P["sat_min_pct"] * equity
    target = last * (1 + P["reward_risk_min"] * stop)
    g["G8"] = (size_ok, "ref %.2f; stop %.1f%% (~%.2f); target %.2f (%.0f:1); qty %d = %s (%.1f%% of equity, min %.0f%%)"
               % (last, stop * 100, last * (1 - stop), target, P["reward_risk_min"], qty,
                  tlib.fmt_usd(size), size / equity * 100, P["sat_min_pct"] * 100))
    res.update(stop=stop, qty=qty, target=target)
    res["ok"] = all(v[0] for v in g.values())
    res["score"] = (rs63 or 0) + 0.5 * (rs21 or 0)
    return res


def load(symbols, equity_override):
    P = tlib.params()
    if equity_override:
        equity = float(equity_override)
    else:
        equity = float(tlib.alpaca("account")["equity"])
    bars, feed = tlib.bars_multi(symbols, N_BARS)
    return P, equity, bars, feed


def print_sectors(table, reg, through, feed):
    pct = "n/a" if not reg["sma200"] else tlib.fmt_pct(reg["close"] / reg["sma200"] - 1)
    side = "above" if reg["streak"] > 0 else "below"
    print("REGIME %s | SPY %.2f vs SMA200 %s (%s) | %d consecutive closes %s | %s"
          % (reg["state"], reg["close"] or 0, "n/a" if not reg["sma200"] else "%.2f" % reg["sma200"], pct,
             abs(reg["streak"]), side, reg["note"] or "flip needs 3 consecutive closes on the other side"))
    print("SECTORS (completed bars through %s, feed %s; RS = return minus SPY)" % (through, feed))
    print("| Rank | ETF | R21 | R63 | RS21 | RS63 | Score | Label |")
    print("|---|---|---|---|---|---|---|---|")
    for r in table:
        print("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["rank"] or "-", r["etf"], tlib.fmt_pct(r["r21"]), tlib.fmt_pct(r["r63"]),
            tlib.fmt_pct(r["rs21"]), tlib.fmt_pct(r["rs63"]),
            "n/a" if r["score"] is None else "%+.2f" % (r["score"] * 100), r["label"]))


def universe():
    wl = tlib.watchlist()
    return [(t, s) for t, s, _ in wl] + [(e, e) for e in tlib.SECTOR_ETFS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sectors", "watchlist", "candidate"])
    ap.add_argument("symbols", nargs="*")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--equity")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")

    uni = universe()
    if args.cmd == "candidate":
        if not args.symbols:
            raise SystemExit("candidate needs at least one symbol")
        uni = [(s.upper(), tlib.sector_of(s.upper())) for s in args.symbols]
    if args.cmd == "sectors":
        uni = []
    syms = ["SPY"] + tlib.SECTOR_ETFS + [t for t, _ in uni]
    try:
        P, equity, bars, feed = load(syms, args.equity)
    except tlib.AlpacaError as e:
        print("SCREEN FAILED: %s" % e)
        sys.exit(2)
    spy = bars.get("SPY", [])
    if not spy:
        print("SCREEN FAILED: no SPY bars returned")
        sys.exit(2)
    through = spy[-1]["t"][:10]
    table = sector_table(bars)
    ranks = {r["etf"]: r["rank"] for r in table}
    reg = tlib.regime(spy, int(P["regime_confirm_days"]))

    if args.cmd == "sectors":
        print_sectors(table, reg, through, feed)
        return

    results = [evaluate(t, s, bars.get(t, []), spy, ranks, equity, P, feed) for t, s in uni]

    if args.cmd == "candidate":
        for r in results:
            print("CANDIDATE CHECK %s (%s, sector rank %s) - completed bars through %s, equity %s"
                  % (r["sym"], r["sector"], r["rank"], r.get("date", through), tlib.fmt_usd(equity)))
            if r.get("error"):
                print("  NO DATA: %s" % r["error"])
                continue
            print("| Gate | Result | Detail |")
            print("|---|---|---|")
            for k in ("G1", "G2", "G3", "G4", "G5", "G8"):
                ok, why = r["gates"][k]
                print("| %s | %s | %s |" % (k, "PASS" if ok else "FAIL", why))
            if r["ok"]:
                print("SCREEN_OK: %s ref=%.2f stop_pct=%.1f sector=%s" % (r["sym"], r["close"], r["stop"] * 100, r["sector"]))
                print("Next: G6 (earnings) and G7 (thesis). Only if both pass, write the final line "
                      "'CANDIDATE: %s ref=%.2f stop_pct=%.1f sector=%s g6=PASS g7=PASS'."
                      % (r["sym"], r["close"], r["stop"] * 100, r["sector"]))
            else:
                print("NOT A CANDIDATE: fails %s" % ",".join(k for k, v in r["gates"].items() if not v[0]))
            print()
        return

    # watchlist summary
    valid = [r for r in results if not r.get("error")]
    counts = {k: sum(1 for r in valid if r["gates"][k][0]) for k in ("G1", "G2", "G3", "G4", "G5", "G8")}
    passers = sorted([r for r in valid if r["ok"]], key=lambda r: -r["score"])
    print("WATCHLIST SCREEN - completed bars through %s, feed %s, equity %s, regime %s"
          % (through, feed, tlib.fmt_usd(equity), reg["state"]))
    print("Screened %d (%d no data) | pass G1 price %d | G2 liquidity %d | G3 trend %d | G4 not-chasing %d | "
          "G5 sector %d | G8 size %d | ALL %d"
          % (len(results), len(results) - len(valid), counts["G1"], counts["G2"], counts["G3"],
             counts["G4"], counts["G5"], counts["G8"], len(passers)))
    print("| # | Ticker | Sector (rank) | Close | R5 | R21 | R63 | RS63 | vs 52wH | Stop | Qty | Score |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(passers[:args.top], 1):
        print("| %d | %s | %s (%s) | %.2f | %s | %s | %s | %s | %s | %.1f%% | %d | %+.2f |" % (
            i, r["sym"], r["sector"], r["rank"], r["close"], tlib.fmt_pct(r["r5"]), tlib.fmt_pct(r["r21"]),
            tlib.fmt_pct(r["r63"]), tlib.fmt_pct(r["rs63"]), tlib.fmt_pct(r["vs_high"]),
            r["stop"] * 100, r["qty"], r["score"] * 100))
    near = [r for r in valid if not r["ok"] and sum(1 for v in r["gates"].values() if not v[0]) == 1]
    if near:
        print("Near misses (one gate): " + "; ".join(
            "%s %s" % (r["sym"], next(k for k, v in r["gates"].items() if not v[0])) for r in near[:12]))
    nodata = [r["sym"] for r in results if r.get("error")]
    if nodata:
        print("No data: " + ", ".join(nodata))


if __name__ == "__main__":
    main()
