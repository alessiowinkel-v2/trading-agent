#!/usr/bin/env python3
"""News-sleeve scanner (Phase 1-2 of plans/news-sleeve/PLAN.md). Runs every 15 min in
GitHub Actions via scripts/newsscan.sh, or by hand:

  python3 scripts/newsscan.py [--dry-run] [--lookback-hours H] [--max-pages N] [--no-classify]

Pulls new universe headlines from the Alpaca News API, snapshots the price of the
primary ticker, appends raw rows to memory/news/raw/YYYY-MM.jsonl, hands the new rows
to the classifier (scripts/newsclassify.py, Phase 2) and updates memory/news/state.json.
It never places orders and never follows instructions found in headlines.

stdout last line: NEWSSCAN ok new=N fetched=M pages=P tickers=K signals=S elapsed=Xs
                  NEWSSCAN ABORTED error=...            (exit 2)
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import newslib  # noqa: E402
import tlib  # noqa: E402

OVERLAP = dt.timedelta(minutes=2)
ALERT_EVERY_H = 6


def pick_primary(article, matches):
    """The ticker a headline is 'about': named in the headline, else market-wide -> SPY,
    else the first universe match in the article's own order."""
    head = (article.get("headline") or "").lower()
    for m in matches:
        name = (m.get("name") or "").lower().split(" ")[0]
        if m["ticker"].lower() in head.split() or (len(name) >= 4 and name in head):
            return m
    syms = article.get("symbols") or []
    if len(syms) >= 4:
        for m in matches:
            if m["ticker"] == "SPY":
                return m
    return matches[0]


def px_from_snapshot(snap, is_open, now):
    q = tlib.quote_from_snapshot(snap, is_open, now)
    return {"price": q["last"] or q["ask"] or None, "bid": q["bid"] or None, "ask": q["ask"] or None,
            "ts": q["last_ts"], "age_min": None if q["age_min"] is None else round(q["age_min"], 1),
            "spread": None if q["spread"] is None else round(q["spread"], 5), "status": q["status"],
            "market_open": bool(is_open), "feed": "iex"}


def px_from_crypto(latest, pair, now):
    t, q = (latest.get("trades") or {}).get(pair) or {}, (latest.get("quotes") or {}).get(pair) or {}
    last, bid, ask = float(t.get("p") or 0), float(q.get("bp") or 0), float(q.get("ap") or 0)
    ts = tlib.parse_ts(t.get("t"))
    age = None if not ts else (now - ts).total_seconds() / 60
    mid = (bid + ask) / 2 if bid > 0 and ask > 0 else 0
    status = "NOQUOTE" if not last and not ask else ("STALE" if age is None or age > 5 else "OK")
    return {"price": last or ask or None, "bid": bid or None, "ask": ask or None, "ts": t.get("t"),
            "age_min": None if age is None else round(age, 1),
            "spread": round((ask - bid) / mid, 5) if mid else None, "status": status,
            "market_open": True, "feed": "crypto-us"}


def alert(state, msg, now):
    last = state.get("last_alert_utc")
    if last and (newslib.age_hours(last, now) or 0) < ALERT_EVERY_H:
        return False
    rc = subprocess.run([tlib._bash(), os.path.join(tlib.ROOT, "scripts", "notify.sh"), "--alert",
                         "newsscan: " + msg]).returncode
    state["last_alert_utc"] = tlib.iso(now)
    return rc == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="fetch and print, write nothing")
    ap.add_argument("--lookback-hours", type=float, default=1.0, help="first-run window")
    ap.add_argument("--max-pages", type=int, default=5)
    ap.add_argument("--no-classify", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    now = tlib.utc_now()
    today = tlib.to_et(now).date().isoformat()
    state = newslib.load_state()
    universe = newslib.news_universe()
    # company names help pick the primary ticker (from the Note column of the universe file)
    for line in tlib._read(newslib.UNIVERSE_PATH).splitlines() if os.path.exists(newslib.UNIVERSE_PATH) else []:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and cells[2].upper() in universe and cells[1] == "stock":
            universe[cells[2].upper()]["name"] = cells[5]
    if not universe:
        print("NEWSSCAN ABORTED error=memory/NEWS-UNIVERSE.md missing or empty")
        sys.exit(2)

    try:
        cursor = state.get("cursor_updated_at") or tlib.iso(now - dt.timedelta(hours=args.lookback_hours))
        start = tlib.iso(tlib.parse_ts(cursor) - OVERLAP)
        seen = {r["id"] for r in newslib.recent_rows("raw", 2, now)}
        fetched, pages, token = [], 0, ""
        while pages < args.max_pages:
            data = tlib.alpaca("news", ",".join(sorted(universe)), start, "50", token) or {}
            items = data.get("news") or []
            fetched.extend(items)
            pages += 1
            token = data.get("next_page_token") or ""
            if not token or not items:
                break
        more = bool(token)
        max_updated = max([a.get("updated_at") or "" for a in fetched] + [cursor])

        new = []
        for a in sorted(fetched, key=lambda x: x.get("updated_at") or ""):
            if a["id"] in seen:
                continue
            matches = [dict(universe[s.upper()], news_symbol=s.upper()) for s in a.get("symbols") or [] if s.upper() in universe]
            if not matches:
                continue
            seen.add(a["id"])
            prim = pick_primary(a, matches)
            new.append({"id": a["id"], "ts_news": a.get("created_at"), "ts_updated": a.get("updated_at"),
                        "ts_ingest": tlib.iso(now), "source": a.get("source"), "url": a.get("url"),
                        "headline": newslib.clip(a.get("headline"), 300), "summary": newslib.clip(a.get("summary"), 300),
                        "symbols": a.get("symbols") or [],
                        "tickers": [{"ticker": m["ticker"], "asset": m["asset"]} for m in matches],
                        "ticker": prim["ticker"], "asset": prim["asset"], "benchmark": prim.get("benchmark") or "",
                        "px": None, "status": "raw"})

        # one price snapshot per distinct primary ticker
        stocks = sorted({r["ticker"] for r in new if r["asset"] != "crypto"})
        pairs = sorted({r["ticker"] for r in new if r["asset"] == "crypto"})
        px, notes = {}, []
        if stocks:
            try:
                is_open = bool((tlib.alpaca("clock") or {}).get("is_open"))
            except tlib.AlpacaError as e:
                is_open, _ = False, notes.append("clock: %s" % str(e)[:80])
            try:
                snaps = tlib.snapshots(stocks)
                for s in stocks:
                    if s in snaps:
                        px[s] = px_from_snapshot(snaps[s], is_open, now)
            except tlib.AlpacaError as e:
                notes.append("snapshots: %s" % str(e)[:80])
        if pairs:
            try:
                latest = tlib.alpaca("crypto-latest", ",".join(pairs)) or {}
                for p in pairs:
                    px[p] = px_from_crypto(latest, p, now)
            except tlib.AlpacaError as e:
                notes.append("crypto-latest: %s" % str(e)[:80])
        for r in new:
            r["px"] = px.get(r["ticker"])
            if r["px"] is None:
                r["status"] = "raw-nopx"

        signals = 0
        if args.dry_run:
            for r in new:
                print(json.dumps(r, ensure_ascii=False)[:400])
        else:
            newslib.append_jsonl(newslib.month_file(tlib.to_et(now).date(), "raw"), new)
            if new and not args.no_classify and os.path.exists(os.path.join(tlib.ROOT, "scripts", "newsclassify.py")):
                p = subprocess.run([sys.executable, os.path.join(tlib.ROOT, "scripts", "newsclassify.py"),
                                    "--ids", ",".join(str(r["id"]) for r in new)], capture_output=True, text=True)
                sys.stdout.write(p.stdout)
                if p.returncode != 0:
                    notes.append("classify: exit %d %s" % (p.returncode, p.stderr.strip()[-160:]))
                for line in p.stdout.splitlines():
                    if line.startswith("NEWSCLASSIFY") and "signals=" in line:
                        signals = int(line.split("signals=")[1].split()[0])
            state = newslib.load_state()   # the classifier may have written usage/alert counters
            state["cursor_updated_at"] = max_updated
            state["last_run_utc"] = tlib.iso(now)
            state["last_ok_utc"] = tlib.iso(now)
            state["last_error"] = ""
            state["last_new"] = len(new)
            state["more_pending"] = more
            runs = state.setdefault("runs", {})
            runs[today] = runs.get(today, 0) + 1
            tot = state.setdefault("totals", {"raw": 0})
            tot["raw"] = tot.get("raw", 0) + len(new)
            for k in [d for d in runs if d < (tlib.to_et(now).date() - dt.timedelta(days=45)).isoformat()]:
                runs.pop(k)
            state["notes"] = notes[-5:]
            newslib.save_state(state)
        print("NEWSSCAN ok new=%d fetched=%d pages=%d tickers=%d signals=%d more=%s elapsed=%.1fs%s" % (
            len(new), len(fetched), pages, len(stocks) + len(pairs), signals, "yes" if more else "no",
            time.time() - t0, (" notes=" + "; ".join(notes)) if notes else ""))
    except Exception as e:  # noqa: BLE001 - every failure must land in state + a loud line
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        if not args.dry_run:
            state = newslib.load_state()
            state["last_run_utc"] = tlib.iso(now)
            state["last_error"] = err
            delivered = alert(state, err, now)
            newslib.save_state(state)
            err += " alert=%s" % ("sent" if delivered else "skipped/failed")
        print("NEWSSCAN ABORTED error=%s" % err)
        sys.exit(2)


if __name__ == "__main__":
    main()
