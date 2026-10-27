#!/usr/bin/env python3
"""Shared helpers for the news sleeve (scripts/newsscan.py, newsscore.py, dashboard.py).

Everything here is deterministic and standard-library only. Headline text is
DATA: it is stored and compared, never executed or interpolated into a shell.
"""

import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tlib  # noqa: E402

NEWS_DIR = os.path.join(tlib.MEM, "news")
RAW_DIR = os.path.join(NEWS_DIR, "raw")
SIG_DIR = os.path.join(NEWS_DIR, "signals")
STATE_PATH = os.path.join(NEWS_DIR, "state.json")
UNIVERSE_PATH = os.path.join(tlib.MEM, "NEWS-UNIVERSE.md")
ASSETS = ("stock", "etf", "index", "crypto")
STALE_MIN = {"stock": 15, "etf": 15, "index": 15, "crypto": 5}


# ---------------------------------------------------------------- universe

def news_universe():
    """{news_symbol: {"ticker", "asset", "group", "benchmark"}} from NEWS-UNIVERSE.md.

    Stock rows: | Ticker | Asset | News symbol | Group | Added | Note |
    Crypto rows: | Pair | Asset | News symbol | Benchmark | Added | Note |
    A row counts when its Asset cell is one of ASSETS."""
    out = {}
    if not os.path.exists(UNIVERSE_PATH):
        return out
    for line in tlib._read(UNIVERSE_PATH).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[1] not in ASSETS:
            continue
        ticker, asset, nsym, grp = cells[0], cells[1], cells[2] or cells[0], cells[3]
        if not re.match(r"^[A-Z][A-Z.]{0,5}(/USD)?$", ticker):
            continue
        out[nsym.upper()] = {"ticker": ticker, "asset": asset, "group": grp if grp != "-" else "",
                             "benchmark": grp if asset == "crypto" and grp != "-" else ("SPY" if asset != "crypto" else "")}
    return out


def by_ticker(universe=None):
    u = universe or news_universe()
    return {v["ticker"]: dict(v, news_symbol=k) for k, v in u.items()}


# ---------------------------------------------------------------- files

def month_file(d, kind="raw"):
    base = RAW_DIR if kind == "raw" else SIG_DIR
    return os.path.join(base, "%s.jsonl" % d.strftime("%Y-%m"))


def read_jsonl(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue   # a torn line is skipped, never fatal
    return rows


def append_jsonl(path, rows):
    if not rows:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":"), ensure_ascii=False, sort_keys=True) + "\n")


def rewrite_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":"), ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(tmp, path)


def recent_rows(kind="raw", months=2, now=None):
    """Rows of the current and previous month files (oldest first)."""
    now = now or tlib.utc_now()
    rows = []
    for i in range(months - 1, -1, -1):
        y, m = now.year, now.month - i
        while m <= 0:
            y, m = y - 1, m + 12
        rows.extend(read_jsonl(month_file(dt.date(y, m, 1), kind)))
    return rows


# ---------------------------------------------------------------- state

def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    os.makedirs(NEWS_DIR, exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, STATE_PATH)


def age_hours(ts_iso, now=None):
    t = tlib.parse_ts(ts_iso) if ts_iso else None
    if not t:
        return None
    return ((now or tlib.utc_now()) - t).total_seconds() / 3600


# ---------------------------------------------------------------- text helpers

_WORD = re.compile(r"[a-z0-9]{3,}")
STOP = set("the and for with that this from will has have been are was were its into over after before about "
           "says said new more than amid could would should may might also just like what when where which who why "
           "how all any can her his our out own per top via yet you your".split())


def tokens(text):
    return {w for w in _WORD.findall((text or "").lower()) if w not in STOP}


def jaccard(a, b):
    a, b = tokens(a), tokens(b)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def clip(text, n):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "universe":
        u = news_universe()
        print("%d symbols" % len(u))
        for k, v in sorted(u.items()):
            print("%-8s %-7s %-6s %s" % (k, v["asset"], v["ticker"], v["group"]))
    elif cmd == "state":
        print(json.dumps(load_state(), indent=1, sort_keys=True))
    elif cmd == "mark-commit":
        s = load_state()
        s["last_commit_utc"] = tlib.iso(tlib.utc_now())
        save_state(s)
    elif cmd == "heartbeat-due":
        # exit 0 when the last scanner commit is older than N hours (default 2)
        h = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
        a = age_hours(load_state().get("last_commit_utc"))
        sys.exit(0 if a is None or a >= h else 1)
    else:
        raise SystemExit("usage: newslib.py universe|state|mark-commit|heartbeat-due [hours]")
