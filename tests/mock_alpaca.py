#!/usr/bin/env python3
"""Minimal in-memory Alpaca mock for offline tests (tests/offline.sh).

Serves the trading API under /paper-api/v2 and market data under /data/v2 with
deterministic synthetic prices. Buy limits at/above the ask fill instantly;
trailing stops rest as working orders. Not a market simulator - just enough
to exercise scripts/alpaca.sh, screen.py and ks.py end to end.

  python3 tests/mock_alpaca.py PORT
Env: MOCK_OPEN=1|0 (market open), MOCK_SIP_403=1 (refuse SIP history),
     MOCK_ACCOUNT=PA0TEST, MOCK_CASH=2000
"""

import datetime as dt
import hashlib
import json
import math
import os
import random
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

UTC = dt.timezone.utc
LOCK = threading.Lock()
BASE = {"SPY": 760, "SPYM": 80, "NVDA": 180, "AVGO": 330, "MSFT": 510, "AMD": 160, "ORCL": 290,
        "ANET": 140, "PLTR": 170, "GOOGL": 250, "META": 720, "NFLX": 1200, "TMUS": 240, "AMZN": 230,
        "TSLA": 430, "HD": 400, "TJX": 140, "CMG": 45, "JPM": 300, "GS": 780, "BAC": 50, "V": 340,
        "MA": 570, "SCHW": 95, "LLY": 800, "UNH": 320, "ABBV": 220, "JNJ": 190, "ISRG": 550,
        "VRTX": 420, "CAT": 520, "GE": 300, "DE": 470, "ETN": 380, "RTX": 160, "UNP": 230, "PWR": 400,
        "XOM": 165, "CVX": 160, "COP": 95, "EOG": 115, "SLB": 36, "COST": 940, "WMT": 103, "PG": 150,
        "KO": 70, "PM": 160, "NEE": 80, "SO": 95, "CEG": 330, "VST": 190, "LIN": 470, "FCX": 45,
        "NEM": 90, "NUE": 140, "PLD": 115, "AMT": 190, "WELL": 170, "EQIX": 800}
for e in ["XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC"]:
    BASE.setdefault(e, 90)


def now():
    return dt.datetime.now(UTC)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def trading_days(n_back=420):
    d, out = now().date(), []
    while len(out) < n_back:
        d -= dt.timedelta(days=1)
        if d.weekday() < 5:
            out.append(d)
    return list(reversed(out))   # completed sessions, oldest first, through yesterday


DAYS = trading_days()


def series(sym):
    """Deterministic daily OHLCV ending yesterday, last close == BASE price."""
    seed = int(hashlib.md5(sym.encode()).hexdigest()[:8], 16)
    rnd = random.Random(seed)
    drift = rnd.uniform(-0.0004, 0.0012)
    if sym in ("SPY", "SPYM"):   # bull market by default; MOCK_BEAR=1 ends in a fresh downtrend
        drift = 0.0008
        if os.environ.get("MOCK_BEAR") == "1":
            n = len(DAYS)
            rets = [rnd.gauss(0.0008 if i < n - 60 else -0.004, 0.006) for i in range(n)]
            return _build(sym, rnd, rets, 0.006)
    vol = 0.012 if sym in ("SPY", "SPYM") or sym.startswith("XL") else rnd.uniform(0.012, 0.03)
    rets = [rnd.gauss(drift, vol) for _ in DAYS]
    return _build(sym, rnd, rets, vol)


def _build(sym, rnd, rets, vol):
    closes, c = [], 1.0
    for r in rets:
        c *= math.exp(r)
        closes.append(c)
    scale = BASE.get(sym, 100) / closes[-1]
    shares = 60e6 if sym == "SPY" else rnd.uniform(3e6, 25e6)
    bars = []
    for day, cl in zip(DAYS, closes):
        cl *= scale
        o = cl * (1 + rnd.gauss(0, vol / 3))
        h, l = max(o, cl) * (1 + abs(rnd.gauss(0, vol / 2))), min(o, cl) * (1 - abs(rnd.gauss(0, vol / 2)))
        t = dt.datetime(day.year, day.month, day.day, 4, tzinfo=UTC)
        bars.append({"t": iso(t), "o": round(o, 2), "h": round(h, 2), "l": round(l, 2), "c": round(cl, 2),
                     "v": int(shares * rnd.uniform(0.7, 1.3)), "n": 1000, "vw": round(cl, 2)})
    return bars


CACHE = {}


def bars_for(sym):
    if sym not in CACHE:
        CACHE[sym] = series(sym)
    return CACHE[sym]


def price(sym):
    return bars_for(sym)[-1]["c"]


STATE = {"cash": float(os.environ.get("MOCK_CASH", "2000")), "positions": {}, "orders": []}


def position_list():
    out = []
    for sym, p in STATE["positions"].items():
        px = price(sym)
        mv = p["qty"] * px
        cost = p["qty"] * p["avg"]
        out.append({"symbol": sym, "qty": str(p["qty"]), "avg_entry_price": "%.4f" % p["avg"],
                    "market_value": "%.2f" % mv, "current_price": "%.2f" % px, "unrealized_pl": "%.2f" % (mv - cost),
                    "unrealized_plpc": "%.4f" % ((mv - cost) / cost if cost else 0), "change_today": "0.0",
                    "qty_available": str(p["qty"] - held(sym)), "side": "long"})
    return out


def held(sym):
    return sum(float(o["qty"]) for o in STATE["orders"] if o["symbol"] == sym and o["side"] == "sell"
               and o["status"] in ("new", "accepted", "held", "partially_filled"))


def equity():
    return STATE["cash"] + sum(p["qty"] * price(s) for s, p in STATE["positions"].items())


def fill(o, px):
    q = float(o["qty"])
    sym = o["symbol"]
    if o["side"] == "buy":
        p = STATE["positions"].setdefault(sym, {"qty": 0.0, "avg": 0.0})
        p["avg"] = (p["avg"] * p["qty"] + px * q) / (p["qty"] + q)
        p["qty"] += q
        STATE["cash"] -= q * px
    else:
        p = STATE["positions"][sym]
        p["qty"] -= q
        STATE["cash"] += q * px
        if p["qty"] <= 1e-9:
            del STATE["positions"][sym]
    o.update(status="filled", filled_qty=o["qty"], filled_avg_price="%.2f" % px, filled_at=iso(now()))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, obj=None):
        body = b"" if obj is None else json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        self.route("GET")

    def do_POST(self):
        self.route("POST")

    def do_PATCH(self):
        self.route("PATCH")

    def do_DELETE(self):
        self.route("DELETE")

    def route(self, m):
        if self.path.startswith("/webhook"):          # stands in for Discord/Slack
            msg = self.body()
            with open(os.environ.get("MOCK_WEBHOOK_LOG", os.devnull), "a", encoding="utf-8") as f:
                f.write(json.dumps(msg) + "\n")
            return self.send(500 if self.path.startswith("/webhook/fail") else 204)
        if not self.headers.get("APCA-API-KEY-ID"):
            return self.send(401, {"message": "unauthorized"})
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        p = u.path
        with LOCK:
            if p.startswith("/data/v1beta1/news"):
                return self.news(q)
            if p.startswith("/data/v1beta3/crypto/us/"):
                return self.crypto(p[len("/data/v1beta3/crypto/us/"):], q)
            if p.startswith("/data/v2/"):
                return self.data(p[len("/data/v2/"):], q)
            if p.startswith("/paper-api/v2/"):
                return self.trading(m, p[len("/paper-api/v2/"):], q)
        self.send(404, {"message": "not found"})

    # ------------------------------------------------------------ market data
    def snapshot(self, sym):
        b = bars_for(sym)
        px = price(sym)
        t = iso(now() - dt.timedelta(minutes=1))
        return {"latestTrade": {"p": px, "t": t}, "latestQuote": {"bp": round(px * 0.9995, 2), "ap": round(px * 1.0005, 2), "t": t},
                "dailyBar": b[-1], "prevDailyBar": b[-2], "minuteBar": b[-1]}

    # ------------------------------------------------------------ news + crypto (news sleeve)
    NEWS = [  # three universe articles, one off-universe, one duplicate id (62600001 twice)
        {"id": 62600001, "created_at": "T-90", "updated_at": "T-90", "source": "benzinga", "author": "Mock",
         "headline": "Nvidia Raises Full-Year Guidance On Data Center Demand", "summary": "NVDA guidance up.",
         "symbols": ["NVDA", "AMD"], "url": "https://example.com/1", "images": []},
        {"id": 62600002, "created_at": "T-60", "updated_at": "T-55", "source": "benzinga", "author": "Mock",
         "headline": "Bitcoin Slips Below $80,000 As ETF Outflows Continue", "summary": "BTC down.",
         "symbols": ["BTCUSD"], "url": "https://example.com/2", "images": []},
        {"id": 62600003, "created_at": "T-45", "updated_at": "T-45", "source": "benzinga", "author": "Mock",
         "headline": "Small Cap Biotech Soars On Phase 2 Data", "summary": "off universe",
         "symbols": ["XBIO"], "url": "https://example.com/3", "images": []},
        {"id": 62600001, "created_at": "T-90", "updated_at": "T-30", "source": "benzinga", "author": "Mock",
         "headline": "Nvidia Raises Full-Year Guidance On Data Center Demand (updated)", "summary": "NVDA guidance up.",
         "symbols": ["NVDA", "AMD"], "url": "https://example.com/1", "images": []},
        {"id": 62600004, "created_at": "T-20", "updated_at": "T-20", "source": "benzinga", "author": "Mock",
         "headline": "Fed Officials Signal Patience On Rate Cuts, Stocks Dip", "summary": "macro",
         "symbols": ["SPY", "QQQ", "AAPL", "MSFT", "NVDA"], "url": "https://example.com/4", "images": []},
    ]

    def news(self, q):
        def ts(code):
            return iso(now() - dt.timedelta(minutes=int(code[2:])))
        want = set((q.get("symbols") or "").split(",")) if q.get("symbols") else None
        rows = []
        for a in self.NEWS:
            a = dict(a, created_at=ts(a["created_at"]), updated_at=ts(a["updated_at"]))
            if want and not (want & set(a["symbols"])):
                continue
            if q.get("start") and a["updated_at"] < q["start"]:
                continue
            rows.append(a)
        rows.sort(key=lambda a: a["updated_at"], reverse=q.get("sort") == "desc")
        lim = int(q.get("limit", 10))
        start = int(q.get("page_token") or 0)
        page = rows[start:start + lim]
        nxt = str(start + lim) if start + lim < len(rows) else None
        return self.send(200, {"news": page, "next_page_token": nxt})

    CRYPTO = {"BTC/USD": 81000.0, "ETH/USD": 2340.0, "SOL/USD": 101.0}

    def crypto(self, p, q):
        pairs = [x for x in (q.get("symbols") or "").split(",") if x]
        t = iso(now() - dt.timedelta(seconds=30))
        if p == "latest/trades":
            return self.send(200, {"trades": {s: {"p": self.CRYPTO.get(s, 1.0), "s": 0.01, "t": t, "i": 1, "tks": "B"} for s in pairs}})
        if p == "latest/quotes":
            return self.send(200, {"quotes": {s: {"bp": round(self.CRYPTO.get(s, 1.0) * 0.9998, 3), "ap": round(self.CRYPTO.get(s, 1.0) * 1.0002, 3),
                                                  "bs": 1, "as": 1, "t": t} for s in pairs}})
        if p == "bars":
            step = {"1Min": 1, "15Min": 15, "1Hour": 60, "1Day": 1440}.get(q.get("timeframe", "15Min"), 15)
            n = int(q.get("limit", 100))
            out = {}
            for s in pairs:
                base = self.CRYPTO.get(s, 1.0)
                bars = []
                if q.get("start"):
                    # forward from start (flat price): the scorer's windows can be weeks old
                    t0 = dt.datetime.fromisoformat(q["start"].replace("Z", "+00:00")).astimezone(UTC).replace(second=0, microsecond=0)
                    t0 -= dt.timedelta(minutes=t0.minute % step)
                    t1 = dt.datetime.fromisoformat(q.get("end", iso(now())).replace("Z", "+00:00")).astimezone(UTC)
                    t1 = min(t1, now())
                    tt = t0
                    while tt <= t1 and len(bars) < n:
                        bars.append({"t": iso(tt), "o": base, "h": base, "l": base, "c": base, "v": 1.0, "n": 5, "vw": base})
                        tt += dt.timedelta(minutes=step)
                    if q.get("sort") == "desc":
                        bars = list(reversed(bars))
                else:
                    end = now().replace(second=0, microsecond=0)
                    end -= dt.timedelta(minutes=end.minute % step)
                    for i in range(n):
                        tt = end - dt.timedelta(minutes=step * i)
                        px = base * (1 + 0.0004 * ((i % 7) - 3))
                        bars.append({"t": iso(tt), "o": round(px, 3), "h": round(px * 1.001, 3), "l": round(px * 0.999, 3),
                                     "c": round(px, 3), "v": 1.0, "n": 5, "vw": round(px, 3)})
                    if q.get("sort") != "desc":
                        bars = list(reversed(bars))
                out[s] = bars
            return self.send(200, {"bars": out, "next_page_token": None})
        self.send(404, {"message": "no crypto route %s" % p})

    def data(self, p, q):
        feed = q.get("feed", "iex")
        if p.startswith("stocks/") and p.endswith("/bars") or p == "stocks/bars":
            if feed == "sip" and os.environ.get("MOCK_SIP_403") == "1":
                return self.send(403, {"message": "subscription does not permit querying recent SIP data"})
            end = q.get("end", "9999")
            syms = [p.split("/")[1]] if p != "stocks/bars" else q["symbols"].split(",")
            tf = q.get("timeframe", "1Day")
            if tf != "1Day" and p != "stocks/bars":
                # intraday: flat bars at the last close, one per minute/hour inside [start, end]
                s = syms[0]
                step = 60 if tf == "1Hour" else 1
                px = price(s)
                t0 = dt.datetime.fromisoformat(q["start"].replace("Z", "+00:00")).astimezone(UTC).replace(second=0, microsecond=0)
                t1 = dt.datetime.fromisoformat(end.replace("Z", "+00:00")).astimezone(UTC)
                rows, t = [], t0
                while t <= t1 and len(rows) < int(q.get("limit", 1000)):
                    rows.append({"t": iso(t), "o": px, "h": px, "l": px, "c": px, "v": 1000, "n": 10, "vw": px})
                    t += dt.timedelta(minutes=step)
                return self.send(200, {"bars": rows, "symbol": s, "next_page_token": None})
            out = {}
            for s in syms:
                rows = [b for b in bars_for(s) if q.get("start", "") <= b["t"] <= end]
                if p != "stocks/bars":
                    if q.get("sort") == "desc":
                        rows = list(reversed(rows))
                    rows = rows[:int(q.get("limit", 1000))]
                out[s] = rows
            if p != "stocks/bars":
                return self.send(200, {"bars": out[syms[0]], "symbol": syms[0], "next_page_token": None})
            flat = [(s, b) for s in syms for b in out[s]]
            start = int(q.get("page_token") or 0)
            page = flat[start:start + 2000]          # small pages to exercise pagination
            res = {}
            for s, b in page:
                res.setdefault(s, []).append(b)
            nxt = str(start + 2000) if start + 2000 < len(flat) else None
            return self.send(200, {"bars": res, "next_page_token": nxt})
        if p == "stocks/snapshots":
            return self.send(200, {s: self.snapshot(s) for s in q["symbols"].split(",")})
        if p.endswith("/snapshot"):
            return self.send(200, self.snapshot(p.split("/")[1]))
        if p.endswith("/quotes/latest"):
            s = p.split("/")[1]
            return self.send(200, {"symbol": s, "quote": self.snapshot(s)["latestQuote"]})
        self.send(404, {"message": "no data route %s" % p})

    # ------------------------------------------------------------ trading
    def trading(self, m, p, q):
        if p == "account" and m == "GET":
            e = equity()
            return self.send(200, {"account_number": os.environ.get("MOCK_ACCOUNT", "PA0TEST"), "status": "ACTIVE",
                                   "equity": "%.2f" % e, "cash": "%.2f" % STATE["cash"], "last_equity": "%.2f" % 2000,
                                   "buying_power": "%.2f" % (STATE["cash"] * 2), "daytrade_count": 0,
                                   "pattern_day_trader": False, "trading_blocked": False, "account_blocked": False})
        if p == "clock":
            op = os.environ.get("MOCK_OPEN", "1") == "1"
            return self.send(200, {"timestamp": iso(now()), "is_open": op, "next_open": "2026-11-02T09:30:00-05:00",
                                   "next_close": "2026-11-02T16:00:00-05:00"})
        if p == "calendar":
            if os.environ.get("MOCK_CAL_FAIL") == "1":
                return self.send(500, {"message": "internal error"})
            s, e = dt.date.fromisoformat(q["start"]), dt.date.fromisoformat(q["end"])
            out, d = [], s
            while d <= e:
                if d.weekday() < 5:
                    out.append({"date": d.isoformat(), "open": "09:30", "close": "16:00"})
                d += dt.timedelta(days=1)
            return self.send(200, out)
        if p == "account/portfolio/history":
            return self.send(200, {"timestamp": [], "equity": [], "profit_loss": [], "base_value": 2000})
        if p == "positions" and m == "GET":
            return self.send(200, position_list())
        if p.startswith("positions/"):
            sym = p.split("/")[1]
            if sym not in STATE["positions"]:
                return self.send(404, {"code": 40410000, "message": "position does not exist"})
            if m == "GET":
                return self.send(200, next(x for x in position_list() if x["symbol"] == sym))
            if m == "DELETE":
                if held(sym):
                    return self.send(403, {"message": "insufficient qty available for order (held by open orders)"})
                o = self.new_order({"symbol": sym, "qty": str(STATE["positions"][sym]["qty"]), "side": "sell",
                                    "type": "market", "time_in_force": "day", "client_order_id": "close-" + uuid.uuid4().hex[:6]})
                fill(o, price(sym))
                return self.send(200, o)
        if p == "orders" and m == "GET":
            st = q.get("status", "open")
            rows = [o for o in STATE["orders"] if st == "all"
                    or (st == "open" and o["status"] in ("new", "accepted", "held", "partially_filled"))
                    or (st == "closed" and o["status"] not in ("new", "accepted", "held", "partially_filled"))]
            return self.send(200, list(reversed(rows)))
        if p == "orders" and m == "POST":
            b = self.body()
            if any(o["client_order_id"] == b.get("client_order_id") for o in STATE["orders"]):
                return self.send(422, {"code": 40010001, "message": "client_order_id must be unique"})
            if b["side"] == "sell" and float(b["qty"]) > STATE["positions"].get(b["symbol"], {"qty": 0})["qty"] - held(b["symbol"]):
                return self.send(403, {"message": "insufficient qty available for order"})
            o = self.new_order(b)
            px = price(b["symbol"])
            if b["type"] == "limit" and b["side"] == "buy" and float(b["limit_price"]) >= px * 1.0005:
                fill(o, round(px * 1.0005, 2))
            elif b["type"] == "limit" and b["side"] == "sell" and float(b["limit_price"]) <= px * 0.9995:
                fill(o, round(px * 0.9995, 2))
            elif b["type"] == "trailing_stop":
                o.update(hwm="%.2f" % px, stop_price="%.2f" % (px * (1 - float(b["trail_percent"]) / 100)))
            return self.send(200, o)
        if p.startswith("orders/"):
            oid = p.split("/")[1]
            o = next((x for x in STATE["orders"] if x["id"] == oid), None)
            if not o:
                return self.send(404, {"message": "order not found"})
            if m == "GET":
                return self.send(200, o)
            if m == "DELETE":
                if o["status"] in ("new", "accepted", "held", "partially_filled"):
                    o["status"] = "canceled"
                return self.send(204)
            if m == "PATCH":
                b = self.body()
                o["status"] = "replaced"
                n = dict(o, id=str(uuid.uuid4()), status="new", client_order_id=b.get("client_order_id", uuid.uuid4().hex[:10]),
                         replaces=o["id"])
                if "trail" in b:
                    n["trail_percent"] = b["trail"]
                    n["stop_price"] = "%.2f" % (float(n["hwm"]) * (1 - float(b["trail"]) / 100))
                STATE["orders"].append(n)
                return self.send(200, n)
        self.send(404, {"message": "no trading route %s %s" % (m, p)})

    def new_order(self, b):
        o = {"id": str(uuid.uuid4()), "client_order_id": b.get("client_order_id"), "symbol": b["symbol"],
             "side": b["side"], "type": b["type"], "qty": b["qty"], "filled_qty": "0", "filled_avg_price": None,
             "filled_at": None, "limit_price": b.get("limit_price"), "trail_percent": b.get("trail_percent"),
             "time_in_force": b.get("time_in_force"), "status": "new", "submitted_at": iso(now())}
        STATE["orders"].append(o)
        return o


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
