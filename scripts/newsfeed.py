#!/usr/bin/env python3
"""See scripts/newsfeed.sh."""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import newslib  # noqa: E402
import tlib  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--since", type=float, default=24)
ap.add_argument("--symbols", default="")
ap.add_argument("--min-conf", type=float, default=0.0)
ap.add_argument("--all", action="store_true", help="include direction=none and duplicates")
a = ap.parse_args()
now = tlib.utc_now()
cut = tlib.iso(now - dt.timedelta(hours=a.since))
syms = {s.strip().upper() for s in a.symbols.split(",") if s.strip()}
rows = [s for s in newslib.recent_rows("signals", 2, now) if (s.get("ts_news") or "") >= cut]
if syms:
    rows = [s for s in rows if s.get("ticker") in syms]
if not a.all:
    rows = [s for s in rows if s.get("status") in ("open", "scored") and (s.get("confidence") or 0) >= a.min_conf]
rows.sort(key=lambda s: s.get("ts_news") or "", reverse=True)
st = newslib.load_state()
print("NEWSFEED last %gh | %d signals%s | scanner last OK %s | pending %s" % (
    a.since, len(rows), " for %s" % ",".join(sorted(syms)) if syms else "", st.get("last_ok_utc", "never"),
    st.get("pending_after_run", "n/a")))
if not rows:
    print("(none)")
    sys.exit(0)
print("| time ET | ticker | dir | m | conf | category | novelty | outcome | headline |")
print("|---|---|---|---|---|---|---|---|---|")
for s in rows[:40]:
    t = tlib.to_et(tlib.parse_ts(s["ts_news"])).strftime("%m-%d %H:%M")
    o = s.get("outcomes") or {}
    oc = "d1 %s" % tlib.fmt_pct(o["d1"]["net_excess"], 2) if o.get("d1") else "-"
    print("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        t, s.get("ticker"), s.get("direction") or "-", s.get("magnitude") or "-",
        "%.2f" % s["confidence"] if s.get("confidence") is not None else "-", s.get("category") or "-",
        s.get("novelty") or "-", oc, newslib.clip(s.get("headline"), 80)))
