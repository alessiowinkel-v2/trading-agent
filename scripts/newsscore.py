#!/usr/bin/env python3
"""News-sleeve scorer (Phase 3 of plans/news-sleeve/PLAN.md). Resolves outcomes for open
signals exactly as PLAN §5 defines and writes the pre-registered scorecard of PLAN §6.

  python3 scripts/newsscore.py [--dry-run] [--limit N] [--rescore] [--explain ID] [--slot-of ISO SYM]

Entry is measured at the next ROUTINE slot (10:12 / 13:07 ET on a trading day, >= ts_news
+ 5 min), never at the headline. Crypto is also measured at the hypothetical 15-minute
lane ("crypto-15m": first quarter hour >= ts_news + 15 min). Horizons d1/d3/d5 are
official closes (stocks) or +24/72/120 h 15-minute closes (crypto) after the entry slot;
h1 (60 min after the headline) is diagnostic only. Benchmark SPY for stocks/ETFs/indices,
BTC/USD for other crypto, 0 for SPY and BTC. Costs: 0.10% stocks, 0.60% crypto, round trip.
Bears are scored as if shorted (net_excess = -excess - cost) and are never tradeable.
Prices come only from Alpaca bars through scripts/alpaca.sh. Nothing here trades.
"""

import argparse
import datetime as dt
import json
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import newslib  # noqa: E402
import tlib  # noqa: E402

SLOTS_ET = ((10, 12), (13, 7))
COST = {"stock": 0.0010, "etf": 0.0010, "index": 0.0010, "crypto": 0.0060}
HORIZON_DAYS = {"d1": 1, "d3": 3, "d5": 5}
HORIZON_HOURS = {"d1": 24, "d3": 72, "d5": 120}
GATE = {"n_min": 40, "t_min": 2.0, "weeks_min": 6, "scored_min": 150, "uptime_min": 0.95, "slots_per_day": 96}
SCORECARD_JSON = os.path.join(newslib.NEWS_DIR, "scorecard.json")
SCORECARD_MD = os.path.join(tlib.MEM, "NEWS-SCORECARD.md")


# ---------------------------------------------------------------- time helpers

def et_dt(d, hh, mm):
    """UTC instant of ET wall clock hh:mm on date d."""
    return tlib.et_midnight_utc(d) + dt.timedelta(hours=hh, minutes=mm)


def routine_slot(ts, trading_days):
    """First routine slot (10:12 / 13:07 ET on a trading day) >= ts + 5 min."""
    t = ts + dt.timedelta(minutes=5)
    d = tlib.to_et(t).date()
    for _ in range(15):
        if d in trading_days:
            for hh, mm in SLOTS_ET:
                s = et_dt(d, hh, mm)
                if s >= t:
                    return s
        d += dt.timedelta(days=1)
    return None


def quarter_slot(ts):
    t = ts + dt.timedelta(minutes=15)
    t = t.replace(second=0, microsecond=0)
    add = (-t.minute) % 15
    return t + dt.timedelta(minutes=add)


def in_rth(t, trading_days):
    e = tlib.to_et(t)
    return e.date() in trading_days and (9, 30) <= (e.hour, e.minute) < (16, 0)


def first_bar_at_or_after(bars, t):
    for b in bars:
        bt = tlib.parse_ts(b["t"])
        if bt and bt >= t:
            return b
    return None


def bar_ending_at(bars, t, step_min):
    """Bar whose window [t-step, t) closes at t (or the latest one closing <= t within one step)."""
    best = None
    for b in bars:
        bt = tlib.parse_ts(b["t"])
        if bt is None:
            continue
        end = bt + dt.timedelta(minutes=step_min)
        if end <= t and (t - end) < dt.timedelta(minutes=step_min) and (best is None or bt > tlib.parse_ts(best["t"])):
            best = b
    return best


# ---------------------------------------------------------------- market data (cached per run)

class Data:
    def __init__(self, now, dry):
        self.now, self.dry = now, dry
        self.daily, self.intraday, self.cbars, self.calls = {}, {}, {}, 0
        self.trading_days = set()
        self.final_daily_cutoff = tlib.to_et(now).date() if tlib.to_et(now).time() >= dt.time(16, 20) else tlib.to_et(now).date() - dt.timedelta(days=1)

    def load_calendar(self, start, end):
        cal = tlib.alpaca("calendar", start.isoformat(), end.isoformat()) or []
        self.calls += 1
        self.trading_days = {dt.date.fromisoformat(c["date"]) for c in cal}

    def daily_closes(self, sym, n=90):
        if sym not in self.daily:
            try:
                d = tlib.alpaca("bars", sym, str(n), "now") or {}
                self.calls += 1
                closes = {}
                for b in d.get("bars") or []:
                    day = dt.date.fromisoformat(b["t"][:10])
                    if day <= self.final_daily_cutoff:
                        closes[day] = float(b["c"])
                self.daily[sym] = closes
            except tlib.AlpacaError:
                self.daily[sym] = {}
        return self.daily[sym]

    def stock_minutes(self, sym, start, end):
        key = (sym, tlib.iso(start), tlib.iso(end))
        if key not in self.intraday:
            try:
                d = tlib.alpaca("bars-intraday", sym, "1Min", tlib.iso(start), tlib.iso(end), "20", quiet=True) or {}
                self.calls += 1
                self.intraday[key] = d.get("bars") or []
            except tlib.AlpacaError:
                self.intraday[key] = []
        return self.intraday[key]

    def crypto_bars(self, pair, tf, start, end):
        key = (pair, tf, tlib.iso(start), tlib.iso(end))
        if key not in self.cbars:
            try:
                d = tlib.alpaca("crypto-bars", pair, "1000", tf, tlib.iso(start), tlib.iso(end)) or {}
                self.calls += 1
                self.cbars[key] = (d.get("bars") or {}).get(pair) or []
            except tlib.AlpacaError:
                self.cbars[key] = []
        return self.cbars[key]

    # --- prices
    def stock_open_at(self, sym, t):
        b = first_bar_at_or_after(self.stock_minutes(sym, t, t + dt.timedelta(minutes=10)), t)
        return (float(b["o"]), b["t"]) if b else (None, None)

    def crypto_open_at(self, pair, t):
        b = first_bar_at_or_after(self.crypto_bars(pair, "1Min", t, t + dt.timedelta(minutes=10)), t)
        if not b:
            b = first_bar_at_or_after(self.crypto_bars(pair, "15Min", t, t + dt.timedelta(minutes=30)), t)
        return (float(b["o"]), b["t"]) if b else (None, None)

    def crypto_close_at(self, pair, t, span_start):
        bars = self.crypto_bars(pair, "15Min", span_start, span_start + dt.timedelta(hours=121))
        b = bar_ending_at(bars, t, 15)
        return (float(b["c"]), b["t"]) if b else (None, None)


# ---------------------------------------------------------------- scoring one signal

def nth_trading_day(d, n, trading_days):
    cur, k = d, 0
    for _ in range(40):
        cur += dt.timedelta(days=1)
        if cur in trading_days:
            k += 1
            if k == n:
                return cur
    return None


def outcome(direction, asset, p_entry, p_exit, b_entry, b_exit):
    ret = p_exit / p_entry - 1
    bench = (b_exit / b_entry - 1) if (b_entry and b_exit) else 0.0
    excess = ret - bench
    cost = COST.get(asset, 0.001)
    net = (excess if direction == "bull" else -excess) - cost
    return {"price": round(p_exit, 6), "ret": round(ret, 6), "bench": round(bench, 6), "excess": round(excess, 6),
            "net_excess": round(net, 6)}


def score_signal(s, data, explain=False):
    """Fill s['entries'], s['outcomes'], s['status']; return a list of explain lines."""
    lines = []
    ts = tlib.parse_ts(s["ts_news"])
    asset, sym, bench_sym = s.get("asset"), s["ticker"], s.get("benchmark") or ""
    crypto = asset == "crypto"
    if not ts:
        s["status"], s["notes"] = "unscorable", "no ts_news"
        return lines
    entries, outs = s.get("entries") or {}, s.get("outcomes") or {}
    now = data.now

    # h1 diagnostic (from the headline)
    if "h1" not in outs:
        t60 = ts + dt.timedelta(minutes=60)
        if t60 + dt.timedelta(minutes=20) <= now:
            if crypto:
                p0, _ = data.crypto_open_at(sym, ts)
                p1, t1 = data.crypto_open_at(sym, t60)
                b0, b1 = (data.crypto_open_at(bench_sym, ts)[0], data.crypto_open_at(bench_sym, t60)[0]) if bench_sym else (None, None)
            elif in_rth(ts, data.trading_days) and in_rth(t60, data.trading_days):
                p0, _ = data.stock_open_at(sym, ts)
                p1, t1 = data.stock_open_at(sym, t60)
                b0, b1 = (data.stock_open_at(bench_sym, ts)[0], data.stock_open_at(bench_sym, t60)[0]) if bench_sym else (None, None)
            else:
                p0 = p1 = t1 = b0 = b1 = None
                outs["h1"] = None   # outside regular hours: no h1 for stocks
            if p0 and p1:
                outs["h1"] = dict(outcome(s["direction"], asset, p0, p1, b0, b1), entry_price=round(p0, 6), ts=t1)
                lines.append("h1: %s %.4f -> %.4f at %s (bench %s)" % (sym, p0, p1, t1, bench_sym or "-"))
            elif "h1" not in outs:
                outs["h1"] = None

    # entry slots
    slots = {"routine": routine_slot(ts, data.trading_days)}
    if crypto:
        slots["crypto-15m"] = quarter_slot(ts)
    for name, slot in slots.items():
        if slot is None:
            continue
        if name not in entries:
            if slot + dt.timedelta(minutes=20) > now:
                continue   # not yet reachable
            if crypto:
                p, bt = data.crypto_open_at(sym, slot)
                bp = data.crypto_open_at(bench_sym, slot)[0] if bench_sym else None
            else:
                p, bt = data.stock_open_at(sym, slot)
                bp = data.stock_open_at(bench_sym, slot)[0] if bench_sym else None
            if p is None:
                entries[name] = {"ts": tlib.iso(slot), "price": None, "bench_price": None, "note": "no entry bar"}
                lines.append("%s entry: no bar for %s at %s" % (name, sym, tlib.iso(slot)))
                continue
            entries[name] = {"ts": tlib.iso(slot), "bar_ts": bt, "price": round(p, 6), "bench_price": None if bp is None else round(bp, 6)}
            lines.append("%s entry: %s open %.4f at %s (bench %s %s)" % (name, sym, p, bt, bench_sym or "-", bp))
        e = entries[name]
        if e.get("price") is None:
            continue
        slot_t = tlib.parse_ts(e["ts"])
        o = outs.setdefault(name, {})
        for h in ("d1", "d3", "d5"):
            if h in o:
                continue
            if crypto:
                target = slot_t + dt.timedelta(hours=HORIZON_HOURS[h])
                if target + dt.timedelta(minutes=20) > now:
                    continue
                p, pt = data.crypto_close_at(sym, target, slot_t)
                bp = data.crypto_close_at(bench_sym, target, slot_t)[0] if bench_sym else None
                when = tlib.iso(target)
            else:
                day = nth_trading_day(tlib.to_et(slot_t).date(), HORIZON_DAYS[h], data.trading_days)
                if day is None or day > data.final_daily_cutoff:
                    continue
                p = data.daily_closes(sym).get(day)
                bp = data.daily_closes(bench_sym).get(day) if bench_sym else None
                pt, when = day.isoformat(), day.isoformat()
            if p is None:
                o[h] = None
                lines.append("%s %s: no close for %s at %s" % (name, h, sym, when))
                continue
            o[h] = dict(outcome(s["direction"], asset, e["price"], p, e.get("bench_price"), bp), ts=pt)
            lines.append("%s %s: %s %.4f -> %.4f at %s | bench %s -> %s | net_excess %+.4f" % (
                name, h, sym, e["price"], p, pt, e.get("bench_price"), bp, o[h]["net_excess"]))
    s["entries"], s["outcomes"] = entries, outs
    rt = outs.get("routine") or {}
    if entries.get("routine", {}).get("price") is None and "routine" in entries:
        s["status"], s["notes"] = "unscorable", entries["routine"].get("note", "no entry")
    elif all(h in rt for h in ("d1", "d3", "d5")):
        s["status"] = "scored"
    return lines


# ---------------------------------------------------------------- scorecard

def conf_bucket(c):
    return "hi" if (c or 0) >= 0.8 else "lo"


def mag_bucket(m):
    return "m2+" if (m or 0) >= 2 else "m1"


def asset_group(a):
    return {"stock": "stock", "etf": "stock", "index": "index", "crypto": "crypto"}.get(a, "stock")


def stats(vals):
    n = len(vals)
    if n == 0:
        return {"n": 0}
    mean = sum(vals) / n
    med = statistics.median(vals)
    sd = statistics.stdev(vals) if n >= 2 else 0.0
    if n < 2:
        t = None   # undefined for a single observation
    else:
        t = (mean / (sd / math.sqrt(n))) if sd > 0 else (99.0 if mean > 0 else (-99.0 if mean < 0 else 0.0))
        t = max(-99.0, min(99.0, t))
    h = n // 2
    first, second = vals[:h], vals[h:]
    return {"n": n, "mean": round(mean, 5), "median": round(med, 5), "sd": round(sd, 5), "t": None if t is None else round(t, 2),
            "first_half_mean": round(sum(first) / len(first), 5) if first else None,
            "second_half_mean": round(sum(second) / len(second), 5) if second else None,
            "pos_rate": round(sum(1 for v in vals if v > 0) / n, 3)}


def tradeable(st, direction):
    return bool(direction == "bull" and st.get("n", 0) >= GATE["n_min"] and st.get("mean", 0) > 0 and st.get("median", 0) > 0
                and (st.get("t") or 0) >= GATE["t_min"] and (st.get("first_half_mean") or 0) > 0 and (st.get("second_half_mean") or 0) > 0)


def build_scorecard(all_sigs, raw_rows, state, now):
    scoreable = [s for s in all_sigs if s.get("status") in ("open", "scored") and s.get("direction") in ("bull", "bear")]
    scoreable.sort(key=lambda s: s.get("ts_news") or "")

    def collect(key_fn, slot):
        groups = {}
        for s in scoreable:
            o = (s.get("outcomes") or {}).get(slot) or {}
            for h in ("d1", "d3", "d5"):
                if o.get(h):
                    groups.setdefault(key_fn(s), {}).setdefault(h, []).append(o[h]["net_excess"])
            h1 = (s.get("outcomes") or {}).get("h1")
            if h1 and (slot == "routine"):
                groups.setdefault(key_fn(s), {}).setdefault("h1", []).append(h1["net_excess"])
        return groups

    fine_key = lambda s: (asset_group(s["asset"]), s["direction"], conf_bucket(s.get("confidence")), mag_bucket(s.get("magnitude")), s.get("category") or "other")  # noqa: E731
    agg_key = lambda s: (asset_group(s["asset"]), s["direction"], conf_bucket(s.get("confidence")), "all", "all")  # noqa: E731
    top_key = lambda s: (asset_group(s["asset"]), s["direction"], "all", "all", "all")  # noqa: E731
    buckets = []
    for level, kf in (("fine", fine_key), ("conf", agg_key), ("asset", top_key)):
        for key, hs in collect(kf, "routine").items():
            row = {"level": level, "asset": key[0], "direction": key[1], "conf": key[2], "mag": key[3], "category": key[4],
                   "horizons": {h: stats(v) for h, v in hs.items()}}
            row["tradeable"] = level == "fine" and tradeable(row["horizons"].get("d3", {}), key[1])
            buckets.append(row)
    lane = []
    for key, hs in collect(fine_key, "crypto-15m").items():
        lane.append({"level": "fine", "asset": key[0], "direction": key[1], "conf": key[2], "mag": key[3], "category": key[4],
                     "horizons": {h: stats(v) for h, v in hs.items()}, "tradeable_15m": tradeable(stats(hs.get("d3", [])), key[1])})

    first_ingest = min([r.get("ts_ingest") or "9" for r in raw_rows] + ["9"])
    weeks = 0.0 if first_ingest == "9" else max(0.0, (now - tlib.parse_ts(first_ingest)).total_seconds() / 86400 / 7)
    scored_n = sum(1 for s in scoreable if ((s.get("outcomes") or {}).get("routine") or {}).get("d3"))
    runs = state.get("runs") or {}
    days = sorted(runs)[-28:]
    uptime = (sum(runs[d] for d in days) / (len(days) * GATE["slots_per_day"])) if days else 0.0
    # the first and the current day are partial; cap at 1
    uptime = min(1.0, uptime * (len(days) / max(1, len(days) - 1))) if len(days) > 1 else min(1.0, uptime)
    trade_b = [b for b in buckets if b["tradeable"]]
    reasons = []
    if weeks < GATE["weeks_min"]:
        reasons.append("only %.1f of %d weeks scanned" % (weeks, GATE["weeks_min"]))
    if scored_n < GATE["scored_min"]:
        reasons.append("only %d of %d signals scored at d3" % (scored_n, GATE["scored_min"]))
    if uptime < GATE["uptime_min"]:
        reasons.append("scanner uptime %.0f%% < %.0f%%" % (uptime * 100, GATE["uptime_min"] * 100))
    if not trade_b:
        reasons.append("no bucket passes (n>=%d, mean>0, median>0, t>=%.1f, both halves>0, bull)" % (GATE["n_min"], GATE["t_min"]))
    counts = {"raw": len(raw_rows), "signals": len(all_sigs),
              "open": sum(1 for s in all_sigs if s.get("status") == "open"),
              "scored": sum(1 for s in all_sigs if s.get("status") == "scored"),
              "none": sum(1 for s in all_sigs if s.get("status") == "none"),
              "duplicate": sum(1 for s in all_sigs if s.get("status") == "duplicate"),
              "unscorable": sum(1 for s in all_sigs if s.get("status") == "unscorable"),
              "bull": sum(1 for s in scoreable if s["direction"] == "bull"),
              "bear": sum(1 for s in scoreable if s["direction"] == "bear")}
    return {"asof": tlib.iso(now), "prompt_versions": sorted({(s.get("classifier") or {}).get("prompt_version") or "?" for s in scoreable}),
            "gate": {"met": not reasons, "reasons": reasons, "weeks": round(weeks, 1), "scored_d3": scored_n,
                     "uptime_28d": round(uptime, 3), "tradeable": [{k: b[k] for k in ("asset", "direction", "conf", "mag", "category")} | {"n": b["horizons"]["d3"]["n"], "mean": b["horizons"]["d3"]["mean"], "t": b["horizons"]["d3"]["t"]} for b in trade_b],
                     "params": GATE, "costs": COST},
            "counts": counts, "buckets": buckets, "crypto_15m": lane}


def fmt_st(st):
    if not st or not st.get("n"):
        return "n=0"
    return "n=%d mean=%+.2f%% med=%+.2f%% t=%s halves=%s/%s" % (
        st["n"], st["mean"] * 100, st["median"] * 100, "-" if st["t"] is None else "%.1f" % st["t"],
        "+" if (st.get("first_half_mean") or 0) > 0 else "-", "+" if (st.get("second_half_mean") or 0) > 0 else "-")


def write_md(card, now):
    g, c = card["gate"], card["counts"]
    L = ["# News Scorecard", "",
         "Generated by `python3 scripts/newsscore.py` (nightly GitHub Action + on demand). Rules: `plans/news-sleeve/PLAN.md` §5–§6. "
         "Numbers are copied from here into the Friday review; nobody recomputes them by hand.", "",
         "## %s — News scorecard" % tlib.to_et(now).date().isoformat(), "",
         "**GATE: %s**%s" % ("MET" if g["met"] else "NOT MET", "" if g["met"] else " — " + "; ".join(g["reasons"])), "",
         "- weeks scanned: %.1f (need %d) | signals scored at d3: %d (need %d) | scanner uptime 28d: %.0f%% (need %.0f%%)" % (
             g["weeks"], GATE["weeks_min"], g["scored_d3"], GATE["scored_min"], g["uptime_28d"] * 100, GATE["uptime_min"] * 100),
         "- raw headlines %d | signals %d (bull %d, bear %d, none %d, duplicate %d, unscorable %d) | open %d, scored %d" % (
             c["raw"], c["signals"], c["bull"], c["bear"], c["none"], c["duplicate"], c["unscorable"], c["open"], c["scored"]),
         "- prompt versions: %s | costs: stocks %.2f%%, crypto %.2f%% round trip | asof %s" % (
             ", ".join(card["prompt_versions"]) or "-", COST["stock"] * 100, COST["crypto"] * 100, card["asof"]), ""]
    L += ["### Tradeable buckets (bull, d3, routine slot)", ""]
    if g["tradeable"]:
        L += ["| asset | conf | mag | category | n | mean net excess | t |", "|---|---|---|---|---|---|---|"]
        L += ["| %s | %s | %s | %s | %d | %+.2f%% | %.1f |" % (b["asset"], b["conf"], b["mag"], b["category"], b["n"], b["mean"] * 100, b["t"]) for b in g["tradeable"]]
    else:
        L.append("none")
    L += ["", "### By asset × direction (routine slot, net of costs, benchmark-adjusted)", "",
          "| asset | dir | h1 (diagnostic) | d1 | d3 | d5 |", "|---|---|---|---|---|---|"]
    for b in sorted([b for b in card["buckets"] if b["level"] == "asset"], key=lambda b: (b["asset"], b["direction"])):
        h = b["horizons"]
        L.append("| %s | %s | %s | %s | %s | %s |" % (b["asset"], b["direction"], fmt_st(h.get("h1")), fmt_st(h.get("d1")), fmt_st(h.get("d3")), fmt_st(h.get("d5"))))
    L += ["", "### By asset × direction × confidence", "", "| asset | dir | conf | d1 | d3 | d5 |", "|---|---|---|---|---|---|"]
    for b in sorted([b for b in card["buckets"] if b["level"] == "conf"], key=lambda b: (b["asset"], b["direction"], b["conf"])):
        h = b["horizons"]
        L.append("| %s | %s | %s | %s | %s | %s |" % (b["asset"], b["direction"], b["conf"], fmt_st(h.get("d1")), fmt_st(h.get("d3")), fmt_st(h.get("d5"))))
    fine = sorted([b for b in card["buckets"] if b["level"] == "fine" and b["horizons"].get("d3", {}).get("n")],
                  key=lambda b: -b["horizons"]["d3"]["n"])
    L += ["", "### Fine buckets with d3 data (pre-registered; top 25 by n)", "",
          "| asset | dir | conf | mag | category | d3 | tradeable |", "|---|---|---|---|---|---|---|"]
    L += ["| %s | %s | %s | %s | %s | %s | %s |" % (b["asset"], b["direction"], b["conf"], b["mag"], b["category"], fmt_st(b["horizons"]["d3"]), "YES" if b["tradeable"] else "no") for b in fine[:25]] or ["| - | - | - | - | - | n=0 | no |"]
    if card["crypto_15m"]:
        L += ["", "### Crypto 15-minute lane (hypothetical, Phase 6 decision only)", "", "| asset | dir | conf | mag | category | d3 |", "|---|---|---|---|---|---|"]
        L += ["| %s | %s | %s | %s | %s | %s |" % (b["asset"], b["direction"], b["conf"], b["mag"], b["category"], fmt_st(b["horizons"].get("d3"))) for b in card["crypto_15m"]]
    with open(SCORECARD_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=400, help="max signals to touch per run (API budget)")
    ap.add_argument("--rescore", action="store_true")
    ap.add_argument("--explain", default="", help="signal id: print every price used")
    ap.add_argument("--slot-of", nargs=2, metavar=("ISO", "SYM"), help="print the routine / 15m slot for a timestamp")
    args = ap.parse_args()
    now = tlib.utc_now()
    data = Data(now, args.dry_run)

    if args.slot_of:
        ts = tlib.parse_ts(args.slot_of[0])
        data.load_calendar(tlib.to_et(ts).date() - dt.timedelta(days=1), tlib.to_et(ts).date() + dt.timedelta(days=20))
        r = routine_slot(ts, data.trading_days)
        print("routine_slot=%s crypto_15m=%s" % (tlib.iso(r) if r else None, tlib.iso(quarter_slot(ts))))
        return

    sigs = newslib.recent_rows("signals", 3, now)
    raw = newslib.recent_rows("raw", 3, now)
    state = newslib.load_state()
    todo = [s for s in sigs if s.get("direction") in ("bull", "bear") and (s.get("status") == "open" or args.rescore or str(s.get("id")) == args.explain)]
    if args.explain:
        todo = [s for s in todo if str(s.get("id")) == args.explain]
        if not todo:
            print("no open/scored signal with id %s" % args.explain)
            return
    todo.sort(key=lambda s: s.get("ts_news") or "")
    todo = todo[: args.limit]
    if todo:
        first = min(tlib.parse_ts(s["ts_news"]) for s in todo)
        data.load_calendar(tlib.to_et(first).date() - dt.timedelta(days=3), tlib.to_et(now).date() + dt.timedelta(days=10))
    changed, scored, unscorable = 0, 0, 0
    for s in todo:
        before = json.dumps(s.get("outcomes"), sort_keys=True), s.get("status")
        if args.rescore or args.explain:
            s.pop("entries", None), s.pop("outcomes", None)   # explain always recomputes (and never saves)
            s["status"] = "open"
        lines = score_signal(s, data, explain=bool(args.explain))
        if args.explain:
            print("signal %s %s %s %s conf %.2f ts_news %s" % (s["id"], s["ticker"], s["direction"], s.get("category"), s.get("confidence") or 0, s["ts_news"]))
            print("\n".join(lines) or "(nothing resolvable yet)")
            print("status=%s entries=%s" % (s["status"], json.dumps(s.get("entries"))))
            print("outcomes=%s" % json.dumps(s.get("outcomes")))
            return
        if (json.dumps(s.get("outcomes"), sort_keys=True), s.get("status")) != before:
            changed += 1
        scored += s.get("status") == "scored"
        unscorable += s.get("status") == "unscorable"

    card = build_scorecard(sigs, raw, state, now)
    if not args.dry_run:
        by_file = {}
        for s in sigs:
            d = tlib.to_et(tlib.parse_ts(s.get("ts_news")) or now).date()
            by_file.setdefault(newslib.month_file(d, "signals"), []).append(s)
        for path, rows in by_file.items():
            newslib.rewrite_jsonl(path, rows)
        os.makedirs(newslib.NEWS_DIR, exist_ok=True)
        with open(SCORECARD_JSON, "w", encoding="utf-8", newline="\n") as f:
            json.dump(card, f, indent=1, sort_keys=True)
            f.write("\n")
        write_md(card, now)
        state["last_score_utc"] = tlib.iso(now)
        state["gate_met"] = card["gate"]["met"]
        newslib.save_state(state)
    print("NEWSSCORE ok touched=%d changed=%d scored_total=%d unscorable=%d api_calls=%d gate=%s%s" % (
        len(todo), changed, card["counts"]["scored"], card["counts"]["unscorable"], data.calls,
        "MET" if card["gate"]["met"] else "NOT MET", "" if card["gate"]["met"] else " (" + "; ".join(card["gate"]["reasons"]) + ")"))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        print("NEWSSCORE ABORTED error=%s: %s" % (type(e).__name__, str(e)[:300]))
        sys.exit(2)
