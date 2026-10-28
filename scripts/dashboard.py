#!/usr/bin/env python3
"""Build the static dashboard (Phase 4 of plans/news-sleeve/PLAN.md) from memory/ only.

  python3 scripts/dashboard.py [--out DIR]   write DIR/data.json and copy site/* into DIR
  python3 scripts/dashboard.py --check       build in memory, validate, print one summary line

No API calls, no secrets. Every number is copied from files the scripts already wrote
(STATE.json, scorecard.json, news/state.json, signals, git commit subjects, the weekly
review); the only derived values are the equity/SPY index to 100 and drawdowns.
"""

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import newslib  # noqa: E402
import tlib  # noqa: E402

SITE = os.path.join(tlib.ROOT, "site")
ROUTINES = ["pre-market", "market-open", "midday", "eod"]


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def git_subjects(n=4000):
    try:
        out = subprocess.run(["git", "log", "-n", str(n), "--format=%s"], cwd=tlib.ROOT, capture_output=True, text=True, timeout=30).stdout
        return out.splitlines()
    except Exception:  # noqa: BLE001
        return []


def git_sha():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=tlib.ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def drawdown(series):
    peak, out, mdd = None, [], 0.0
    for v in series:
        if v is None:
            out.append(None)
            continue
        peak = v if peak is None else max(peak, v)
        d = v / peak - 1
        mdd = min(mdd, d)
        out.append(round(d, 5))
    return out, round(mdd, 5)


def account_block(state, cfg):
    eod = state.get("eod") or {}
    dates = sorted(eod)
    latest = eod[dates[-1]] if dates else {}
    try:
        start_eq = float(cfg.get("start_equity") or 0)
    except ValueError:
        start_eq = 0.0
    equity = [eod[d].get("equity") for d in dates]
    spy = [eod[d].get("spy_close") for d in dates]
    base_i = next((i for i, (e, s) in enumerate(zip(equity, spy)) if e and s), None)
    eq_idx = [round(e / equity[base_i] * 100, 3) if (base_i is not None and e) else None for e in equity]
    spy_idx = [round(s / spy[base_i] * 100, 3) if (base_i is not None and s) else None for s in spy]
    eq_dd, eq_mdd = drawdown(equity)
    spy_dd, spy_mdd = drawdown(spy)
    last_eq = latest.get("equity")
    return {
        "phase": cfg.get("phase", ""), "start_date": cfg.get("start_date", ""), "start_equity": start_eq,
        "account_tail": (cfg.get("account_number") or "")[-4:], "asof": state.get("asof"),
        "equity": last_eq, "cash": latest.get("cash"), "invested": latest.get("invested"), "sat_pct": latest.get("sat_pct"),
        "regime": latest.get("regime") or state.get("regime"), "ks_fail": state.get("ks_fail") or [],
        "paused": bool(tlib.paused()),
        "phase_return": (last_eq / start_eq - 1) if (last_eq and start_eq) else None,
        "spy_phase_return": (spy[-1] / spy[base_i] - 1) if (base_i is not None and spy and spy[-1]) else None,
        "day_return": (equity[-1] / equity[-2] - 1) if len(equity) >= 2 and equity[-1] and equity[-2] else None,
        "max_dd": eq_mdd, "spy_max_dd": spy_mdd, "days": len(dates),
        "series": {"dates": dates, "equity": equity, "spy_close": spy, "equity_idx": eq_idx, "spy_idx": spy_idx,
                   "drawdown": eq_dd, "spy_drawdown": spy_dd, "invested": [eod[d].get("invested") for d in dates]},
        "positions": latest.get("positions") or [{"sym": s, "qty": q, "role": "core" if s == "SPYM" else "satellite"}
                                                  for s, q in (state.get("positions") or {}).items()],
    }


def cadence_block(subjects, days=10):
    status = {}
    for s in subjects:
        m = re.match(r"^(pre-market|market-open|midday|eod|weekly) (\d{4}-\d{2}-\d{2}): (OK|SKIPPED|ABORTED)", s)
        if m and (m.group(1), m.group(2)) not in status:
            status[(m.group(1), m.group(2))] = m.group(3)
    dates = sorted({d for (_, d) in status}, reverse=True)[:days]
    rows = []
    for d in sorted(dates):
        row = {"date": d}
        for r in ROUTINES:
            row[r] = status.get((r, d), "MISSING")
        if dt.date.fromisoformat(d).weekday() == 4:
            row["weekly"] = status.get(("weekly", d), "MISSING")
        rows.append(row)
    return rows


def graduation_block():
    path = os.path.join(tlib.MEM, "WEEKLY-REVIEW.md")
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return {"week": None, "items": [], "grade": None}
    heads = list(re.finditer(r"^## Week ending (\d{4}-\d{2}-\d{2})", text, re.M))
    if not heads:
        return {"week": None, "items": [], "grade": None}
    entry = text[heads[-1].start():]
    items = []
    for line in entry.splitlines():
        m = re.match(r"^\s*(?:\d+\.|[-*])\s*(✅|🟡|❌)\s*(.+)$", line) or re.match(r"^\s*(?:\d+\.|[-*])\s*(.+?)\s*(✅|🟡|❌)\s*(.*)$", line)
        if m:
            g = m.groups()
            mark = g[0] if g[0] in "✅🟡❌" else g[1]
            txt = (g[1] if g[0] in "✅🟡❌" else g[0] + " " + (g[2] or "")).strip()
            items.append({"mark": mark, "text": txt[:160]})
    gm = re.search(r"^### Grade:\s*([A-F][+−-]?)", entry, re.M)
    rev = re.search(r"^Reviewed:\s*(\d{4}-\d{2}-\d{2})", entry, re.M)
    return {"week": heads[-1].group(1), "items": items[:11], "grade": gm.group(1) if gm else None,
            "reviewed": rev.group(1) if rev else None}


def notifications_block(now, days=7):
    out = []
    for i in range(1, -1, -1):
        y, m = now.year, now.month - i
        while m <= 0:
            y, m = y - 1, m + 12
        path = os.path.join(tlib.MEM, "notifications", "%04d-%02d.md" % (y, m))
        if not os.path.exists(path):
            continue
        cur = None
        for line in open(path, encoding="utf-8"):
            h = re.match(r"^## (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) ET", line)
            if h:
                cur = {"time": h.group(1), "text": ""}
                out.append(cur)
            elif cur is not None and line.strip() and line.strip() != "---" and not cur["text"]:
                cur["text"] = re.sub(r"<@!?\d+>", "", line.strip())[:200]
    cutoff = (tlib.to_et(now) - dt.timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
    return [n for n in out if n["time"] >= cutoff][-40:][::-1]


def news_block(now):
    st = newslib.load_state()
    card = load_json(os.path.join(newslib.NEWS_DIR, "scorecard.json"), {})
    sigs = [s for s in newslib.recent_rows("signals", 2, now) if s.get("status") in ("open", "scored")]
    sigs.sort(key=lambda s: s.get("ts_news") or "", reverse=True)
    feed = []
    for s in sigs[:60]:
        rt = (s.get("outcomes") or {}).get("routine") or {}
        feed.append({"id": s["id"], "ts": s.get("ts_news"), "ticker": s.get("ticker"), "dir": s.get("direction"),
                     "mag": s.get("magnitude"), "conf": s.get("confidence"), "cat": s.get("category"), "nov": s.get("novelty"),
                     "headline": s.get("headline"), "url": s.get("url"), "status": s.get("status"),
                     "d1": (rt.get("d1") or {}).get("net_excess"), "d3": (rt.get("d3") or {}).get("net_excess"),
                     "d5": (rt.get("d5") or {}).get("net_excess")})
    runs = st.get("runs") or {}
    days = []
    for i in range(6, -1, -1):
        d = (tlib.to_et(now).date() - dt.timedelta(days=i)).isoformat()
        days.append({"date": d, "runs": runs.get(d, 0), "uptime": min(1.0, runs.get(d, 0) / 96)})
    today = tlib.to_et(now).date().isoformat()
    cu = (st.get("classifier_usage") or {}).get(today) or {}
    raw_n = (st.get("totals") or {}).get("raw", 0)
    return {"state": {"last_ok_utc": st.get("last_ok_utc"), "last_run_utc": st.get("last_run_utc"), "last_error": st.get("last_error"),
                      "last_commit_utc": st.get("last_commit_utc"), "last_score_utc": st.get("last_score_utc"),
                      "pending": st.get("pending_after_run"), "classifier_note": st.get("classifier_note"),
                      "age_h": newslib.age_hours(st.get("last_ok_utc"), now), "raw_total": raw_n,
                      "cost_today": cu.get("cost_usd"), "calls_today": cu.get("calls"), "model": cu.get("model")},
            "uptime": days, "scorecard": {"gate": card.get("gate"), "counts": card.get("counts"), "asof": card.get("asof"),
                                           "asset": [b for b in card.get("buckets", []) if b.get("level") == "asset"],
                                           "conf": [b for b in card.get("buckets", []) if b.get("level") == "conf"],
                                           "fine": sorted([b for b in card.get("buckets", []) if b.get("level") == "fine" and (b.get("horizons") or {}).get("d3", {}).get("n")],
                                                          key=lambda b: -b["horizons"]["d3"]["n"])[:25],
                                           "crypto_15m": card.get("crypto_15m", [])},
            "feed": feed}


def plan_block():
    path = os.path.join(tlib.ROOT, "plans", "news-sleeve", "STATUS.md")
    rows = []
    try:
        for line in open(path, encoding="utf-8"):
            m = re.match(r"^\|\s*(\d)\s+([^|]+?)\s*\|[^|]*\|[^|]*\|\s*([^|]+?)\s*\|", line)
            if m:
                rows.append({"phase": int(m.group(1)), "title": m.group(2), "state": m.group(3)})
    except OSError:
        pass
    return rows


def build(now):
    state = load_json(os.path.join(tlib.MEM, "STATE.json"), {})
    cfg = tlib.account_config()
    subjects = git_subjects()
    data = {"meta": {"built_at": tlib.iso(now), "built_at_et": tlib.to_et(now).strftime("%Y-%m-%d %H:%M"), "commit": git_sha(),
                     "repo": "https://github.com/alessiowinkel-v2/trading-agent"},
            "account": account_block(state, cfg), "cadence": cadence_block(subjects),
            "graduation": graduation_block(), "notifications": notifications_block(now),
            "news": news_block(now), "plan": plan_block()}
    return data


def check(data):
    problems = []
    for k in ("meta", "account", "cadence", "graduation", "notifications", "news", "plan"):
        if k not in data:
            problems.append("missing %s" % k)
    a = data.get("account", {})
    s = a.get("series", {})
    if len({len(v) for v in s.values()}) > 1:
        problems.append("series length mismatch")
    json.dumps(data)   # must be serialisable
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="_site")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    now = tlib.utc_now()
    data = build(now)
    problems = check(data)
    if args.check:
        a, n = data["account"], data["news"]
        print("DASHBOARD %s eod_days=%d positions=%d cadence_days=%d signals=%d feed=%d problems=%s" % (
            "ok" if not problems else "PROBLEM", a["days"], len(a["positions"]), len(data["cadence"]),
            (n["scorecard"].get("counts") or {}).get("signals", 0), len(n["feed"]), ",".join(problems) or "none"))
        sys.exit(1 if problems else 0)
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    for name in os.listdir(SITE):
        src = os.path.join(SITE, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(out, name))
    with open(os.path.join(out, "data.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, separators=(",", ":"), ensure_ascii=False)
    with open(os.path.join(out, ".nojekyll"), "w") as f:
        f.write("")
    print("DASHBOARD built %s (%d bytes data.json)%s" % (out, os.path.getsize(os.path.join(out, "data.json")),
                                                        " problems=" + ",".join(problems) if problems else ""))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
