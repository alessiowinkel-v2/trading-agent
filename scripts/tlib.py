"""Shared helpers for screen.py, ks.py and the bash scripts.

Everything numeric the agent relies on is computed here, deterministically:
ET dates, indicators, strategy parameters, watchlist/events parsing, and
Alpaca access (always through scripts/alpaca.sh so auth and guards live in
one place). Standard library only.
"""

import datetime as dt
import json
import math
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEM = os.path.join(ROOT, "memory")
UTC = dt.timezone.utc

SECTOR_ETFS = ["XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC"]


# --------------------------------------------------------------------------
# Time (America/New_York without needing tzdata)
# --------------------------------------------------------------------------

def _et_offset(utc_now):
    try:
        from zoneinfo import ZoneInfo
        return utc_now.astimezone(ZoneInfo("America/New_York")).utcoffset()
    except Exception:
        pass
    y = utc_now.year
    mar1 = dt.date(y, 3, 1)
    dst_start = mar1 + dt.timedelta(days=(6 - mar1.weekday()) % 7 + 7)   # 2nd Sunday March
    nov1 = dt.date(y, 11, 1)
    dst_end = nov1 + dt.timedelta(days=(6 - nov1.weekday()) % 7)         # 1st Sunday Nov
    start = dt.datetime(y, 3, dst_start.day, 7, 0, tzinfo=UTC)            # 02:00 EST
    end = dt.datetime(y, 11, dst_end.day, 6, 0, tzinfo=UTC)               # 02:00 EDT
    return dt.timedelta(hours=-4) if start <= utc_now < end else dt.timedelta(hours=-5)


def utc_now():
    override = os.environ.get("TRADING_NOW_UTC")  # tests only
    if override:
        return dt.datetime.fromisoformat(override.replace("Z", "+00:00")).astimezone(UTC)
    return dt.datetime.now(UTC)


def to_et(ts):
    """UTC-aware datetime -> naive ET wall-clock datetime."""
    return (ts + _et_offset(ts)).replace(tzinfo=None)


def et_now():
    return to_et(utc_now())


def et_today():
    return et_now().date()


def parse_ts(s):
    """Alpaca RFC3339 (with nanoseconds or Z) -> aware UTC datetime."""
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    m = re.match(r"(.*T\d\d:\d\d:\d\d)(\.\d+)?(.*)$", s)
    if m:
        frac = (m.group(2) or "")[:7]
        s = m.group(1) + frac + m.group(3)
    return dt.datetime.fromisoformat(s).astimezone(UTC)


def et_date_of(ts_str):
    t = parse_ts(ts_str)
    return to_et(t).date() if t else None


def et_midnight_utc(d):
    """UTC instant of 00:00 ET on date d."""
    probe = dt.datetime(d.year, d.month, d.day, 12, tzinfo=UTC)
    off = _et_offset(probe)
    return dt.datetime(d.year, d.month, d.day, tzinfo=UTC) - off


def iso(t):
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def monday_of(d):
    return d - dt.timedelta(days=d.weekday())


# --------------------------------------------------------------------------
# Alpaca access via scripts/alpaca.sh
# --------------------------------------------------------------------------

class AlpacaError(Exception):
    pass


ERRORS = []  # every failed call this process; KS-6 counts these


def _bash():
    exe = os.environ.get("TRADING_BASH") or shutil.which("bash")
    if not exe:
        raise AlpacaError("bash not found")
    return exe


def alpaca(*args, parse=True, quiet=False):
    cmd = [_bash(), os.path.join(ROOT, "scripts", "alpaca.sh")] + [str(a) for a in args]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        msg = "alpaca.sh %s failed (exit %d): %s %s" % (
            " ".join(map(str, args)), p.returncode, p.stdout.strip()[:300], p.stderr.strip()[:300])
        ERRORS.append(msg)
        raise AlpacaError(msg)
    if p.stderr.strip() and not quiet:
        sys.stderr.write(p.stderr)
    if not parse:
        return p.stdout
    out = p.stdout.strip()
    return json.loads(out) if out else None


def bars_multi(symbols, n, through="yesterday"):
    """{SYM: [bar,...]} oldest->newest, last n completed daily bars (SIP when allowed).

    Returns (bars, feed_used)."""
    out, feed = {}, "sip"
    syms = list(dict.fromkeys(symbols))
    for i in range(0, len(syms), 50):
        chunk = ",".join(syms[i:i + 50])
        token = ""
        while True:
            p = subprocess.run([_bash(), os.path.join(ROOT, "scripts", "alpaca.sh"),
                                "bars-multi", chunk, str(n), through, token],
                               capture_output=True, text=True, encoding="utf-8")
            if p.returncode != 0:
                msg = "bars-multi failed: %s %s" % (p.stdout.strip()[:300], p.stderr.strip()[:300])
                ERRORS.append(msg)
                raise AlpacaError(msg)
            if "FEED_USED=iex" in p.stderr:
                feed = "iex"
            data = json.loads(p.stdout)
            for sym, rows in (data.get("bars") or {}).items():
                out.setdefault(sym, []).extend(rows)
            token = data.get("next_page_token") or ""
            if not token:
                break
    for sym in out:
        out[sym].sort(key=lambda b: b["t"])
        out[sym] = out[sym][-n:]
    return out, feed


def snapshots(symbols):
    res = {}
    syms = list(dict.fromkeys(symbols))
    for i in range(0, len(syms), 100):
        data = alpaca("snapshots", ",".join(syms[i:i + 100])) or {}
        res.update(data)
    return res


def quote_from_snapshot(snap, clock_open, now=None):
    """Normalised price facts from one snapshot. Staleness uses the latest TRADE
    (IEX quotes are not NBBO and go quiet for thin names)."""
    now = now or utc_now()
    lq, lt = snap.get("latestQuote") or {}, snap.get("latestTrade") or {}
    db, pdb = snap.get("dailyBar") or {}, snap.get("prevDailyBar") or {}
    bid, ask, last = lq.get("bp") or 0.0, lq.get("ap") or 0.0, lt.get("p") or 0.0
    t = parse_ts(lt.get("t"))
    age = (now - t).total_seconds() / 60 if t else None
    mid = (bid + ask) / 2 if bid > 0 and ask > 0 else 0.0
    spread = (ask - bid) / mid if mid > 0 else None
    ref_ask = ask if ask > 0 else last
    status = "OK"
    if not last and not ask:
        status = "NOQUOTE"
    elif clock_open and (age is None or age > 15):
        status = "STALE"
    return {"bid": bid, "ask": ask, "last": last, "ask_or_last": ref_ask, "age_min": age,
            "spread": spread, "prev_close": pdb.get("c"), "day_close": db.get("c"),
            "status": status, "last_ts": lt.get("t")}


# --------------------------------------------------------------------------
# Indicators
# --------------------------------------------------------------------------

def closes(bars):
    return [b["c"] for b in bars]


def sma(vals, n):
    return sum(vals[-n:]) / n if len(vals) >= n else None


def ret(vals, n):
    return vals[-1] / vals[-1 - n] - 1 if len(vals) > n and vals[-1 - n] else None


def atr(bars, n=14):
    if len(bars) < n + 1:
        return None
    trs = []
    for prev, cur in zip(bars[-n - 1:-1], bars[-n:]):
        trs.append(max(cur["h"] - cur["l"], abs(cur["h"] - prev["c"]), abs(cur["l"] - prev["c"])))
    return sum(trs) / n


def adv_usd(bars, n=20):
    if len(bars) < n:
        return None
    return sum(b["c"] * b["v"] for b in bars[-n:]) / n


def regime(spy_bars, confirm=3):
    """Risk-on/off state machine on SPY vs its 200-day SMA, replayed over the
    available history so the result never depends on a log. Returns dict."""
    c = closes(spy_bars)
    if len(c) < 200 + confirm:
        return {"state": "risk-on", "note": "insufficient history (%d bars) - default risk-on" % len(c),
                "close": c[-1] if c else None, "sma200": None, "streak": 0}
    rel = []  # +1 above, -1 below, per day where SMA200 exists
    for i in range(199, len(c)):
        s = sum(c[i - 199:i + 1]) / 200
        rel.append(1 if c[i] > s else -1)
    state = "risk-on" if rel[0] > 0 else "risk-off"
    run_sign, run_len = rel[0], 0
    for r in rel:
        if r == run_sign:
            run_len += 1
        else:
            run_sign, run_len = r, 1
        if run_len >= confirm:
            state = "risk-on" if run_sign > 0 else "risk-off"
    return {"state": state, "close": c[-1], "sma200": sum(c[-200:]) / 200,
            "streak": run_len * run_sign, "note": ""}


# --------------------------------------------------------------------------
# Memory files (single source of truth for parameters)
# --------------------------------------------------------------------------

def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def params():
    """Key: value lines inside the ```params fence of TRADING-STRATEGY.md."""
    text = _read(os.path.join(MEM, "TRADING-STRATEGY.md"))
    m = re.search(r"```params\n(.*?)```", text, re.S)
    if not m:
        raise SystemExit("TRADING-STRATEGY.md has no ```params block")
    out = {}
    for line in m.group(1).splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, v = [x.strip() for x in line.split(":", 1)]
        try:
            out[k] = float(v) if re.match(r"^-?\d+(\.\d+)?$", v) else v
        except ValueError:
            out[k] = v
    return out


def account_config():
    """'- key: value' lines under '## Account' in PROJECT-CONTEXT.md."""
    text = _read(os.path.join(MEM, "PROJECT-CONTEXT.md"))
    m = re.search(r"^## Account.*?\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"^- ([a-z_]+):\s*(.*?)\s*$", line)
            if mm:
                out[mm.group(1)] = mm.group(2)
    return out


def watchlist():
    """[(ticker, sector_etf, name)] from the table in WATCHLIST.md."""
    rows = []
    for line in _read(os.path.join(MEM, "WATCHLIST.md")).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.match(r"^[A-Z][A-Z.]{0,5}$", cells[0]) and cells[1] in SECTOR_ETFS:
            rows.append((cells[0], cells[1], cells[2]))
    return rows


def sector_of(symbol):
    if symbol in SECTOR_ETFS:
        return symbol
    for t, s, _ in watchlist():
        if t == symbol:
            return s
    return "UNKNOWN"


def events_on(d):
    """FOMC/CPI/NFP events listed in EVENTS.md for date d."""
    found = []
    for line in _read(os.path.join(MEM, "EVENTS.md")).splitlines():
        m = re.match(r"^\|?\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(FOMC|CPI|NFP)\b", line.strip())
        if m and m.group(1) == d.isoformat():
            found.append(m.group(2))
    return found


def research_candidates(d):
    """{SYM: {"ref": float, "stop_pct": float, "sector": str}} from the CANDIDATE: lines
    of the RESEARCH-LOG entry dated d. Empty if the latest entry is not dated d."""
    path = os.path.join(MEM, "RESEARCH-LOG.md")
    if not os.path.exists(path):
        return {}
    text = _read(path)
    heads = list(re.finditer(r"^## (\d{4}-\d{2}-\d{2})\b.*$", text, re.M))
    if not heads or heads[-1].group(1) != d.isoformat():
        return {}
    out = {}
    for m in re.finditer(r"^CANDIDATE:\s+([A-Z][A-Z.]{0,5})\s+ref=([\d.]+)(?:\s+stop_pct=([\d.]+))?(?:\s+sector=(\w+))?",
                         text[heads[-1].start():], re.M):
        out[m.group(1)] = {"ref": float(m.group(2)), "stop_pct": float(m.group(3)) if m.group(3) else None,
                           "sector": m.group(4) or ""}
    return out


def paused():
    for p in (os.path.join(MEM, "PAUSED.flag"), os.path.join(ROOT, "PAUSED.flag")):
        if os.path.exists(p):
            return os.path.relpath(p, ROOT)
    return None


def fmt_pct(x, digits=1):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else ("%+.*f%%" % (digits, x * 100))


def fmt_usd(x):
    return "n/a" if x is None else "$%s" % format(round(x, 2), ",.2f")


if __name__ == "__main__":
    # Tiny CLI used by the bash scripts: python3 scripts/tlib.py now|today|events DATE
    cmd = sys.argv[1] if len(sys.argv) > 1 else "now"
    if cmd == "now":
        n = et_now()
        d = n.date()
        print("NOW_ET='%s'" % n.strftime("%Y-%m-%d %H:%M"))
        print("DATE=%s" % d.isoformat())
        print("WEEKDAY=%d" % n.isoweekday())
        print("MONDAY=%s" % monday_of(d).isoformat())
        print("DATE_MINUS_7=%s" % (d - dt.timedelta(days=7)).isoformat())
        print("DATE_MINUS_14=%s" % (d - dt.timedelta(days=14)).isoformat())
        # G6: an earnings date on or after this day is outside the next 5 trading days
        print("EARNINGS_OK_FROM=%s" % (d + dt.timedelta(days=8)).isoformat())
    elif cmd == "events":
        d = dt.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else et_today()
        print(",".join(events_on(d)) or "none")
    elif cmd == "et-date-offset":
        # et-date-offset <hours>  -> ET date of (now + hours)
        h = float(sys.argv[2])
        print(to_et(utc_now() + dt.timedelta(hours=h)).date().isoformat())
    elif cmd == "bars-window":
        # bars-window N [yesterday|now] -> "<start> <end>" in UTC for N daily bars.
        # yesterday = completed sessions only; now = up to 20 min ago (SIP-free limit).
        n = int(sys.argv[2])
        through = sys.argv[3] if len(sys.argv) > 3 else "yesterday"
        if through == "now":
            end = utc_now() - dt.timedelta(minutes=20)
        else:
            end = et_midnight_utc(et_today()) - dt.timedelta(seconds=1)
        start = end - dt.timedelta(days=int(n * 1.5) + 10)
        print(iso(start), iso(end))
    else:
        raise SystemExit("usage: tlib.py now|events [DATE]|et-date-offset HOURS|bars-window N [through]")
