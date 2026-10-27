#!/usr/bin/env python3
"""Classify raw headlines into signals (Phase 2 of plans/news-sleeve/PLAN.md).

  python3 scripts/newsclassify.py [--ids 1,2,3] [--max-calls 3] [--batch 20] [--dry-run]

Reads raw rows (memory/news/raw) that have no signal yet (the given ids plus anything
ingested in the last 48 h), tags near-duplicates without an API call, sends the rest to
scripts/claude.sh in strict-JSON batches, appends one signal row per headline to
memory/news/signals/YYYY-MM.jsonl, sends the few Discord alerts PLAN §4 allows and
accounts tokens/cost in memory/news/state.json.  Exit 0 always except a crash (2);
without ANTHROPIC_API_KEY it prints "skipped" and leaves the rows pending.

stdout last line: NEWSCLASSIFY ok classified=N signals=S none=K dup=D unscorable=U calls=C alerts=A cost=$X
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import newslib  # noqa: E402
import tlib  # noqa: E402

PROMPT = os.path.join(tlib.ROOT, "scripts", "prompts", "classify-v1.md")
SCHEMA = os.path.join(tlib.ROOT, "scripts", "prompts", "classify-schema.json")
PROMPT_VERSION = "classify-v1"
PENDING_H = 48
DUP_JACCARD = 0.6
DUP_WINDOW_H = 24
ALERT_MIN_CONF, ALERT_MIN_MAG = 0.8, 2
HELD_BEAR_CONF = 0.7
PRICE_PER_M = {"claude-sonnet-5-5": (2.0, 10.0), "claude-haiku-5-5": (0.10, 0.50), "claude-opus-5-5": (4.0, 20.0)}
ENUMS = {"direction": {"bull", "bear", "none"}, "magnitude": {1, 2, 3}, "horizon": {"hours", "days", "weeks"},
         "category": {"earnings", "guidance", "m_and_a", "regulatory", "legal", "product", "macro", "analyst",
                      "insider", "rumor", "other"}, "novelty": {"new", "follow_up"}}


def held_symbols():
    p = os.path.join(tlib.MEM, "STATE.json")
    try:
        with open(p, encoding="utf-8") as f:
            return set((json.load(f).get("positions") or {}).keys())
    except (OSError, ValueError):
        return set()


def valid(r, row):
    """Return (clean_result, error) - enums, range and ticker membership checked here, not trusted."""
    try:
        out = {"id": int(r["id"]), "ticker": str(r["ticker"]).upper(), "direction": r["direction"],
               "magnitude": int(r["magnitude"]), "horizon": r["horizon"], "category": r["category"],
               "novelty": r["novelty"], "confidence": float(r["confidence"]), "rationale": newslib.clip(r["rationale"], 200)}
    except (KeyError, TypeError, ValueError) as e:
        return None, "malformed: %s" % e
    for k, allowed in ENUMS.items():
        if out[k] not in allowed:
            return None, "bad %s %r" % (k, out[k])
    if not 0.0 <= out["confidence"] <= 1.0:
        return None, "confidence out of range"
    allowed_t = {t["ticker"] for t in row.get("tickers") or []} | {row["ticker"], "SPY", "BTC/USD"}
    if out["ticker"] not in allowed_t:
        out["rationale"] = ("ticker %s not allowed, kept %s; " % (out["ticker"], row["ticker"])) + out["rationale"]
        out["ticker"] = row["ticker"]
    if out["direction"] == "none":
        out["confidence"] = 0.0
    return out, ""


def classify_batch(items, model):
    msg = json.dumps([{k: it[k] for k in ("id", "ticker", "tickers", "asset", "headline", "summary", "ts_news")} for it in items],
                     ensure_ascii=False)
    p = subprocess.run([tlib._bash(), os.path.join(tlib.ROOT, "scripts", "claude.sh"), "json", SCHEMA, "--system", PROMPT,
                        "--model", model, "--effort", "low"], input=msg, capture_output=True, text=True, encoding="utf-8")
    if p.returncode == 3:
        return None, "nokey", {}
    if p.returncode != 0:
        return None, "claude.sh exit %d: %s" % (p.returncode, p.stderr.strip()[-200:]), {}
    try:
        d = json.loads(p.stdout)
        results = d["json"]["results"]
        assert isinstance(results, list)
    except (ValueError, KeyError, AssertionError) as e:
        return None, "unparseable wrapper: %s" % e, {}
    return results, "", {"usage": d.get("usage") or {}, "model": d.get("model") or model}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    ap.add_argument("--max-calls", type=int, default=3)
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    now = tlib.utc_now()
    today = tlib.to_et(now).date().isoformat()
    model = os.environ.get("CLASSIFIER_MODEL", "claude-sonnet-5-5")
    budget = int(os.environ.get("ALERT_BUDGET", "5"))

    raw = newslib.recent_rows("raw", 2, now)
    sigs = newslib.recent_rows("signals", 2, now)
    done = {s["id"] for s in sigs}
    want = {int(x) for x in args.ids.split(",") if x.strip()}
    cutoff = tlib.iso(now - dt.timedelta(hours=PENDING_H))
    pending = [r for r in raw if r["id"] not in done and (r["id"] in want or (r.get("ts_ingest") or "") >= cutoff)]
    pending.sort(key=lambda r: r.get("ts_news") or "")

    # 1. near-duplicates: same ticker, last 24 h, Jaccard >= 0.6 against an existing signal -> no API call
    recent_sigs = [s for s in sigs if (s.get("ts_news") or "") >= tlib.iso(now - dt.timedelta(hours=DUP_WINDOW_H))]
    out_rows, todo, dup = [], [], 0
    for r in pending:
        hit = None
        for s in recent_sigs:
            if s.get("ticker") == r["ticker"] and s.get("status") in ("open", "none") and newslib.jaccard(s["headline"], r["headline"]) >= DUP_JACCARD:
                hit = s
                break
        if hit:
            out_rows.append(dict(r, direction=None, magnitude=None, horizon=None, category=hit.get("category"),
                                 novelty="duplicate_of:%s" % hit["id"], confidence=None, rationale="near-duplicate headline",
                                 classifier={"model": "dedup", "prompt_version": PROMPT_VERSION}, status="duplicate"))
            recent_sigs.append(out_rows[-1])
            dup += 1
        else:
            todo.append(r)

    # 2. classifier batches
    calls, classified, unscorable, usage_in, usage_out, skipped_nokey = 0, 0, 0, 0, 0, False
    served_model = model
    for i in range(0, len(todo), args.batch):
        if calls >= args.max_calls:
            break
        batch = todo[i:i + args.batch]
        calls += 1
        results, err, meta = classify_batch(batch, model)
        if err == "nokey":
            skipped_nokey, calls = True, calls - 1
            break
        by_id = {}
        if results is not None:
            for r in results:
                try:
                    by_id[int(r.get("id"))] = r
                except (TypeError, ValueError):
                    pass
            usage_in += int((meta.get("usage") or {}).get("input_tokens") or 0)
            usage_out += int((meta.get("usage") or {}).get("output_tokens") or 0)
            served_model = meta.get("model") or model
        for row in batch:
            res = by_id.get(row["id"])
            clean, verr = (None, err or "missing from response") if res is None else valid(res, row)
            if clean is None:
                unscorable += 1
                out_rows.append(dict(row, direction=None, magnitude=None, horizon=None, category=None, novelty=None,
                                     confidence=None, rationale=None, status="unscorable", notes=verr,
                                     classifier={"model": served_model, "prompt_version": PROMPT_VERSION}))
                continue
            classified += 1
            px = row.get("px") if clean["ticker"] == row["ticker"] else None
            out_rows.append(dict(row, ticker=clean["ticker"], px=px, direction=clean["direction"], magnitude=clean["magnitude"],
                                 horizon=clean["horizon"], category=clean["category"], novelty=clean["novelty"],
                                 confidence=clean["confidence"], rationale=clean["rationale"],
                                 asset=("crypto" if clean["ticker"].endswith("/USD") else ("index" if clean["ticker"] == "SPY" else row["asset"])),
                                 benchmark=("" if clean["ticker"] in ("BTC/USD", "SPY") else row.get("benchmark") or ""),
                                 classifier={"model": served_model, "prompt_version": PROMPT_VERSION},
                                 status="open" if clean["direction"] in ("bull", "bear") else "none",
                                 ts_classified=tlib.iso(now)))
            recent_sigs.append(out_rows[-1])

    # 3. alerts (PLAN §4): <= budget/day for strong new signals; always a bear >= 0.7 on a held symbol
    state = newslib.load_state()
    alerts = state.setdefault("alerts", {})
    sent_today = alerts.get(today, 0)
    held = held_symbols()
    n_alerts = 0
    for s in out_rows:
        if s.get("status") != "open":
            continue
        strong = s["confidence"] >= ALERT_MIN_CONF and s["magnitude"] >= ALERT_MIN_MAG and s["novelty"] == "new"
        held_bear = s["direction"] == "bear" and s["confidence"] >= HELD_BEAR_CONF and s["ticker"] in held
        if not (held_bear or (strong and sent_today + n_alerts < budget)):
            continue
        px = (s.get("px") or {}).get("price")
        msg = "news %s: %s %s m%d c%.2f — %s | px %s | %s" % (
            tlib.to_et(tlib.parse_ts(s["ts_news"])).strftime("%H:%M") + " ET", s["ticker"], s["direction"], s["magnitude"],
            s["confidence"], newslib.clip(s["headline"], 120), "n/a" if px is None else px, s.get("url") or "")
        if held_bear:
            msg = "HELD POSITION — " + msg + " | review at the next routine, do not sell on price alone"
        if not args.dry_run:
            cmd = [tlib._bash(), os.path.join(tlib.ROOT, "scripts", "notify.sh")] + (["--alert"] if held_bear else []) + [msg]
            rc = subprocess.run(cmd, capture_output=True, text=True).returncode
            s["alerted"] = "sent" if rc == 0 else "failed"
        n_alerts += 1

    # 4. persist
    sig_count = sum(1 for s in out_rows if s.get("status") == "open")
    none_count = sum(1 for s in out_rows if s.get("status") == "none")
    pi, po = PRICE_PER_M.get(model, (2.0, 10.0))
    cost = usage_in / 1e6 * pi + usage_out / 1e6 * po
    if not args.dry_run:
        by_month = {}
        for s in out_rows:
            d = tlib.to_et(tlib.parse_ts(s.get("ts_news")) or now).date()
            by_month.setdefault(newslib.month_file(d, "signals"), []).append(s)
        for path, rows in by_month.items():
            newslib.append_jsonl(path, rows)
        alerts[today] = sent_today + n_alerts
        cu = state.setdefault("classifier_usage", {})
        day = cu.setdefault(today, {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "unscorable": 0, "model": model})
        day["calls"] += calls
        day["input_tokens"] += usage_in
        day["output_tokens"] += usage_out
        day["cost_usd"] = round(day["cost_usd"] + cost, 4)
        day["unscorable"] += unscorable
        day["model"] = model
        for k in [d for d in list(cu) if d < (tlib.to_et(now).date() - dt.timedelta(days=45)).isoformat()]:
            cu.pop(k)
        tot = state.setdefault("totals", {})
        tot["signals"] = tot.get("signals", 0) + sig_count
        tot["classified"] = tot.get("classified", 0) + classified
        state["pending_after_run"] = max(0, len(todo) - classified - unscorable)
        if skipped_nokey:
            state["classifier_note"] = "ANTHROPIC_API_KEY missing - %d headlines pending" % len(todo)
        else:
            state.pop("classifier_note", None)
        newslib.save_state(state)
    print("NEWSCLASSIFY %s classified=%d signals=%d none=%d dup=%d unscorable=%d calls=%d alerts=%d cost=$%.4f pending=%d%s" % (
        "skipped" if skipped_nokey else "ok", classified, sig_count, none_count, dup, unscorable, calls, n_alerts, cost,
        max(0, len(todo) - classified - unscorable), " reason=no_api_key" if skipped_nokey else ""))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        print("NEWSCLASSIFY ABORTED error=%s: %s" % (type(e).__name__, str(e)[:300]))
        sys.exit(2)
