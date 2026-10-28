#!/usr/bin/env python3
"""Kill switches, core sizing, satellite slots and state - computed from live
Alpaca data, never estimated. Prints ready-to-run order commands.

  python3 scripts/ks.py                       KS table, core action, slots, stop maintenance
  python3 scripts/ks.py --check SYM ...       execution gates PLAN/G0/G8-G11 per candidate (ref from
                                              today's CANDIDATE: lines in RESEARCH-LOG.md)
  python3 scripts/ks.py --eod                 + EOD snapshot block (P&L vs SPY, invested, floor streak)
  python3 scripts/ks.py --week                + weekly statistics for the Friday review
  --write-state  update memory/STATE.json + STATE.md and alert on newly failing switches

Exit 0 = computed (read the table). Exit 2 = could not compute: treat as KS-6, place no orders.
"""

import argparse
import collections
import datetime as dt
import json
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tlib  # noqa: E402

STATE_JSON = os.path.join(tlib.MEM, "STATE.json")
STATE_MD = os.path.join(tlib.MEM, "STATE.md")
WORKING = {"new", "accepted", "pending_new", "partially_filled", "accepted_for_bidding", "held",
           "pending_replace", "pending_cancel", "calculated"}
LATCHED = ("KS-1", "KS-2", "KS-3")   # stay failed after the condition clears (see KILL-SWITCHES.md)


def cmd_order(body):
    return "bash scripts/alpaca.sh order '%s'" % json.dumps(body, separators=(",", ":"))


def money(x):
    return tlib.fmt_usd(x)


class Ctx:
    """Everything one run needs, loaded once."""

    def __init__(self):
        self.P = tlib.params()
        self.cfg = tlib.account_config()
        self.now = tlib.utc_now()
        self.now_et = tlib.to_et(self.now)
        self.today = self.now_et.date()
        self.mode = "PAPER" if "paper-api" in os.environ.get("ALPACA_ENDPOINT", "paper-api") else "LIVE"
        self.core = self.P["core_symbol"]
        sd = self.cfg.get("start_date", "")
        try:
            self.start_date, self.start_date_ok = dt.date.fromisoformat(sd), True
        except ValueError:
            self.start_date, self.start_date_ok = self.today, False   # KS-9 fails until it is set
        try:
            self.start_equity = float(self.cfg.get("start_equity") or 0)
        except ValueError:
            self.start_equity = 0.0
        self.state = {}
        if os.path.exists(STATE_JSON):
            with open(STATE_JSON, encoding="utf-8") as f:
                self.state = json.load(f)

    def load_book(self):
        """Positions and orders - reloaded once by KS-8 before it declares a mismatch."""
        a = tlib.alpaca
        self.positions = a("positions") or []
        self.open_orders = a("orders", "open") or []
        after = tlib.iso(tlib.et_midnight_utc(self.start_date - dt.timedelta(days=1)))
        closed, until = {}, ""
        for _ in range(20):                       # page backwards, 500 at a time
            page = a("orders", "closed", after, "500", until) or []
            for o in page:
                closed[o["id"]] = o
            if len(page) < 500:
                break
            until = min(o["submitted_at"] for o in page)
        self.closed_orders = list(closed.values())

    def load(self):
        a = tlib.alpaca
        self.acct = a("account")
        self.load_book()
        self.clock = a("clock")
        cal = a("calendar", (self.start_date - dt.timedelta(days=21)).isoformat(),
                (self.today + dt.timedelta(days=21)).isoformat()) or []
        self.trading_days = [dt.date.fromisoformat(d["date"]) for d in cal]
        self.equity = float(self.acct["equity"])
        self.cash = float(self.acct["cash"])
        # Alpaca's cash does not reserve working buy orders; sizing must.
        self.reserved = sum((float(o.get("qty") or 0) - float(o.get("filled_qty") or 0)) * float(o.get("limit_price") or 0)
                            for o in self.open_orders if o.get("side") == "buy")
        self.cash_avail = self.cash - self.reserved
        self.last_equity = float(self.acct.get("last_equity") or 0)
        if not self.start_equity:
            self.start_equity = self.last_equity or self.equity
        try:
            self.history = a("history", "3M", "1D", quiet=True) or {}
        except tlib.AlpacaError:
            self.history = {}   # KS-2 then falls back to the EOD equity stored in STATE.json
        syms = list({self.core, "SPY"} | {p["symbol"] for p in self.positions})
        try:
            snaps = tlib.snapshots(syms)
        except tlib.AlpacaError:
            snaps = {}
        is_open = bool(self.clock.get("is_open"))
        self.quotes = {s: tlib.quote_from_snapshot(snaps[s], is_open, self.now) for s in snaps}
        try:
            spy, _ = tlib.bars_multi(["SPY"], 260)
            self.reg = tlib.regime(spy.get("SPY", []), int(self.P["regime_confirm_days"]))
        except tlib.AlpacaError:
            prev = self.state.get("regime", "risk-on")
            self.reg = {"state": prev, "close": None, "sma200": None, "streak": 0,
                        "note": "SPY bars unavailable - kept previous regime %s" % prev}
        self.fills = self._fills()
        self.trips = self._round_trips()

    # ---------------------------------------------------------------- fills
    def _fills(self):
        out, seen = [], set()
        for o in self.closed_orders + self.open_orders:
            if o["id"] in seen:
                continue
            seen.add(o["id"])
            q = float(o.get("filled_qty") or 0)
            ts = o.get("filled_at") or o.get("updated_at") or o.get("submitted_at")
            if q > 0 and ts:
                out.append({"id": o["id"], "sym": o["symbol"], "side": o["side"], "qty": q,
                            "px": float(o.get("filled_avg_price") or 0), "t": tlib.parse_ts(ts),
                            "coid": o.get("client_order_id") or ""})
        out.sort(key=lambda f: f["t"])
        return out

    def _round_trips(self):
        lots = collections.defaultdict(collections.deque)
        trips = []
        for f in self.fills:
            if f["sym"] == self.core:
                continue
            if f["side"] == "buy":
                lots[f["sym"]].append([f["qty"], f["px"], f["t"]])
                continue
            q, cost, matched, entry_t = f["qty"], 0.0, 0.0, None
            while q > 1e-9 and lots[f["sym"]]:
                lot = lots[f["sym"]][0]
                take = min(q, lot[0])
                cost += take * lot[1]
                matched += take
                entry_t = entry_t or lot[2]
                lot[0] -= take
                q -= take
                if lot[0] <= 1e-9:
                    lots[f["sym"]].popleft()
            if matched:
                trips.append({"sym": f["sym"], "qty": matched, "entry": cost / matched, "exit": f["px"],
                              "pnl": matched * f["px"] - cost, "pnl_pct": f["px"] / (cost / matched) - 1,
                              "entry_t": entry_t, "exit_t": f["t"], "sector": tlib.sector_of(f["sym"])})
        return trips

    def et_date(self, t):
        return tlib.to_et(t).date()

    def trading_days_after(self, d):
        """Trading days strictly after d up to and including today."""
        return sum(1 for x in self.trading_days if d < x <= self.today)

    # ---------------------------------------------------------- portfolio
    def mv(self, p):
        return float(p.get("market_value") or 0)

    def core_pos(self):
        return next((p for p in self.positions if p["symbol"] == self.core), None)

    def sats(self):
        return [p for p in self.positions if p["symbol"] != self.core]

    def sat_pct(self):
        return sum(self.mv(p) for p in self.sats()) / self.equity if self.equity else 0

    def invested(self):
        return sum(self.mv(p) for p in self.positions) / self.equity if self.equity else 0

    def stop_orders(self, sym):
        return [o for o in self.open_orders if o["symbol"] == sym and o["side"] == "sell"
                and o.get("type") in ("trailing_stop", "stop", "stop_limit")]

    def entries(self, since):
        return [f for f in self.fills if f["side"] == "buy" and f["coid"].startswith("sat-")
                and self.et_date(f["t"]) >= since]

    def price(self, sym, side="buy"):
        q = self.quotes.get(sym)
        if not q:
            return None
        if side == "buy":
            return q["ask"] if q["ask"] > 0 else (q["last"] or q["prev_close"])
        return q["bid"] if q["bid"] > 0 else (q["last"] or q["prev_close"])

    def next_coid(self, base):
        used = {o.get("client_order_id") for o in self.closed_orders + self.open_orders}
        if base not in used:
            return base
        k = 2
        while "%s-r%d" % (base, k) in used:
            k += 1
        return "%s-r%d" % (base, k)


# ======================================================================== KS
def kill_switches(c):
    P, E, rows = c.P, c.equity, []

    def add(name, ok, value, limit, warn=False):
        rows.append((name, "WARN" if (ok and warn) else ("PASS" if ok else "FAIL"), value, limit))

    latch = c.state.get("latch") or {}
    c.fail_now = {}

    def latched_note(k):
        v = latch.get(k)
        if not v:
            return ""
        if k == "KS-1" and v.get("date") != c.today.isoformat():
            return ""                                   # KS-1 resets the next trading day
        if k == "KS-3" and (v.get("start_date"), v.get("start_equity")) != (c.start_date.isoformat(), c.start_equity):
            return ""                                   # manual reset: user changed start_date/start_equity
        return " - LATCHED since %s" % v.get("date")

    # KS-1 daily drawdown
    base, base_name = c.last_equity, "last_equity"
    lo, hi = P["ks9_equity_low"] * c.start_equity, P["ks9_equity_high"] * c.start_equity
    if c.today <= c.start_date or not (lo <= base <= hi):
        base, base_name = c.start_equity, "start_equity"
    d1 = E / base - 1 if base else 0
    c.fail_now["KS-1"] = d1 <= -P["ks1_daily_dd"]
    note = latched_note("KS-1")
    add("KS-1 daily DD", not c.fail_now["KS-1"] and not note,
        "%s vs %s (%s)%s" % (tlib.fmt_pct(d1, 2), money(base), base_name, note), "> -%.0f%%" % (P["ks1_daily_dd"] * 100))
    # KS-2 weekly drawdown vs prior Friday close (Alpaca history, else our own EOD records)
    monday = tlib.monday_of(c.today)
    wk_base, wk_name = None, ""
    h = c.history or {}
    for ts, eq in zip(h.get("timestamp") or [], h.get("equity") or []):
        d = tlib.to_et(dt.datetime.fromtimestamp(ts, tlib.UTC)).date()
        if eq and c.start_date <= d < monday:
            wk_base, wk_name = float(eq), "close %s" % d
    if wk_base is None:
        for d, v in sorted((c.state.get("eod") or {}).items()):
            if c.start_date.isoformat() <= d < monday.isoformat():
                wk_base, wk_name = float(v["equity"]), "EOD record %s" % d
    if wk_base is None and c.start_date >= monday:
        wk_base, wk_name = c.start_equity, "start_equity (phase began this week)"
    c.week_base, c.week_base_name = wk_base or c.start_equity, wk_name or "unavailable"
    note = latched_note("KS-2")
    if wk_base is None:
        c.fail_now["KS-2"] = True
        add("KS-2 weekly DD", False, "baseline unavailable (no history, no EOD record before %s)%s" % (monday, note),
            "> -%.0f%%" % (P["ks2_weekly_dd"] * 100))
    else:
        d2 = E / wk_base - 1
        c.fail_now["KS-2"] = d2 <= -P["ks2_weekly_dd"]
        add("KS-2 weekly DD", not c.fail_now["KS-2"] and not note,
            "%s vs %s (%s)%s" % (tlib.fmt_pct(d2, 2), money(wk_base), wk_name, note), "> -%.0f%%" % (P["ks2_weekly_dd"] * 100))
    # KS-3 total drawdown
    d3 = E / c.start_equity - 1 if c.start_equity else 0
    c.fail_now["KS-3"] = d3 <= -P["ks3_total_dd"]
    note = latched_note("KS-3")
    add("KS-3 total DD", not c.fail_now["KS-3"] and not note,
        "%s vs start %s%s" % (tlib.fmt_pct(d3, 2), money(c.start_equity), note), "> -%.0f%%" % (P["ks3_total_dd"] * 100))
    # Latch immediately, so a crash later in this run cannot lose the trip.
    new_latch = dict(latch)
    for k in LATCHED:
        if c.fail_now.get(k) and not latched_note(k):
            new_latch[k] = {"date": c.today.isoformat(), "start_date": c.start_date.isoformat(),
                            "start_equity": c.start_equity}
    if new_latch != latch:
        c.state["latch"] = new_latch
        save_state_field(c, "latch", new_latch)
    # KS-4 single satellite size
    big = max([(c.mv(p) / E, p["symbol"]) for p in c.sats()] or [(0, "-")])
    add("KS-4 position size", big[0] <= P["ks4_position_max"], "largest satellite %s %.1f%%" % (big[1], big[0] * 100),
        "<= %.0f%%" % (P["ks4_position_max"] * 100))
    # KS-5 activity
    # working satellite buys that have not filled yet still use an entry slot
    c.pending_sat = [o for o in c.open_orders if o.get("side") == "buy"
                     and (o.get("client_order_id") or "").startswith("sat-") and float(o.get("filled_qty") or 0) == 0]
    today_n = len(c.entries(c.today)) + len(c.pending_sat)
    week_n = len(c.entries(monday)) + len(c.pending_sat)
    c.entries_today, c.entries_week = today_n, week_n
    add("KS-5 activity", today_n <= P["entries_per_day"] and week_n <= P["entries_per_week"],
        "entries today %d, this week %d" % (today_n, week_n),
        "<= %d / <= %d" % (P["entries_per_day"], P["entries_per_week"]))
    # KS-6 API errors this run
    add("KS-6 API errors", len(tlib.ERRORS) <= 2, "%d failed calls" % len(tlib.ERRORS), "<= 2")
    # KS-7 stale core data
    q = c.quotes.get(c.core)
    if not c.clock.get("is_open"):
        add("KS-7 stale data", True, "market closed - n/a", "<= 15 min")
    else:
        ok = bool(q) and q["status"] == "OK"
        add("KS-7 stale data", ok, "%s last trade %s min old" % (c.core, "n/a" if not q or q["age_min"] is None
                                                                 else "%.0f" % q["age_min"]), "<= 15 min")
    # KS-8 reconciliation
    prev = c.state.get("positions")
    if prev is None or "filled" not in c.state:
        add("KS-8 reconcile", True, "no previous STATE.json - initialising", "exact")
    else:
        diff = reconcile(c, prev)
        if diff:                                   # a fill can land between two API calls: reload once
            c.load_book()
            c.fills = c._fills()
            diff = reconcile(c, prev)
        add("KS-8 reconcile", not diff, "matches STATE.json + new fills" if not diff else
            "unexplained: " + ", ".join("%s expected %g got %g" % (s, e, a) for s, (e, a) in sorted(diff.items())),
            "exact")
    # KS-9 account identity / endpoint sanity
    num, want = c.acct.get("account_number", "?"), (c.cfg.get("account_number") or "UNSET")
    ratio = E / c.start_equity if c.start_equity else 0
    in_band = P["ks9_equity_low"] <= ratio <= P["ks9_equity_high"]
    if not c.start_date_ok:
        add("KS-9 account", False, "start_date is UNSET/invalid in PROJECT-CONTEXT.md (%r) - drawdowns and counts "
            "cannot be computed" % c.cfg.get("start_date", ""), "valid YYYY-MM-DD")
    elif want in ("", "UNSET"):
        add("KS-9 account", c.mode == "PAPER" and in_band, "%s (PROJECT-CONTEXT account_number UNSET), equity %.2fx start"
            % (num, ratio), "match, %.1f-%.1fx" % (P["ks9_equity_low"], P["ks9_equity_high"]), warn=True)
    else:
        add("KS-9 account", num == want and in_band, "%s vs expected %s, equity %.2fx start" % (num, want, ratio),
            "match, %.1f-%.1fx" % (P["ks9_equity_low"], P["ks9_equity_high"]))
    # KS-10 every satellite protected by a stop
    unprotected, c.uncovered = [], {}
    for p in c.sats():
        covered = sum(float(o.get("qty") or 0) - float(o.get("filled_qty") or 0) for o in c.stop_orders(p["symbol"]))
        if covered + 1e-6 < float(p["qty"]):
            unprotected.append(p["symbol"])
            c.uncovered[p["symbol"]] = int(round(float(p["qty"]) - covered))
    c.unprotected = unprotected
    add("KS-10 stops", not unprotected, "%d satellites, unprotected: %s" % (len(c.sats()), ", ".join(unprotected) or "none"),
        "all protected")
    # KS-11 consecutive satellite losers
    streak, last_loss = 0, None
    for t in c.trips:
        if t["pnl"] < 0:
            streak += 1
            last_loss = c.et_date(t["exit_t"])
        else:
            streak = 0
    cooling = streak >= P["ks11_loss_streak"] and last_loss and c.trading_days_after(last_loss) < P["ks11_cooldown_days"]
    add("KS-11 loss streak", not cooling, "%d consecutive losers%s" % (streak, " (last %s)" % last_loss if last_loss else ""),
        "< %d (else %d-day pause)" % (P["ks11_loss_streak"], P["ks11_cooldown_days"]))
    # PDT guard
    dtc = int(c.acct.get("daytrade_count") or 0)
    pdt_ok = dtc <= P["pdt_max_daytrades"] and not c.acct.get("pattern_day_trader")
    add("PDT", pdt_ok, "daytrade_count %d%s" % (dtc, ", FLAGGED PDT" if c.acct.get("pattern_day_trader") else ""),
        "<= %d for new satellites" % P["pdt_max_daytrades"])
    c.ks_rows = rows
    return rows


def sector_cooldowns(c):
    by_sector = collections.defaultdict(list)
    for t in c.trips:
        by_sector[t["sector"]].append(t)
    out = {}
    n, days = int(c.P["sector_loss_streak"]), c.P["sector_cooldown_days"]
    for s, ts in by_sector.items():
        last = ts[-n:]
        if len(last) == n and all(t["pnl"] < 0 for t in last):
            d = c.et_date(last[-1]["exit_t"])
            left = days - c.trading_days_after(d)
            if left > 0:
                out[s] = "%d losers in a row, last %s - %d trading days left" % (n, d, left)
    return out


def flags(c):
    failed = {r[0].split()[0] for r in c.ks_rows if r[1] == "FAIL"}
    c.failed = failed
    blocked = bool(c.acct.get("trading_blocked") or c.acct.get("account_blocked"))
    c.paused = tlib.paused()
    c.orders_allowed = not ({"KS-6", "KS-8", "KS-9"} & failed) and not blocked
    c.buys_allowed = c.orders_allowed and not ({"KS-1", "KS-2", "KS-3", "KS-7"} & failed) and not c.paused
    c.sat_allowed = c.buys_allowed and not ({"KS-4", "KS-5", "KS-10", "KS-11", "PDT"} & failed)
    maxpos = c.P["sat_max_positions_riskoff"] if c.reg["state"] == "risk-off" else c.P["sat_max_positions"]
    c.maxpos = int(maxpos)
    c.slots = max(0, min(c.maxpos - len(c.sats()) - len(c.pending_sat), int(c.P["entries_per_day"]) - c.entries_today,
                         int(c.P["entries_per_week"]) - c.entries_week)) if c.sat_allowed else 0
    c.sim = {"slots": 0, "cash": 0.0, "sat": 0.0, "sector_n": collections.Counter(), "sector_v": collections.Counter()}
    for o in c.pending_sat:                        # working buys count as exposure already
        v = float(o.get("qty") or 0) * float(o.get("limit_price") or 0)
        s = tlib.sector_of(o["symbol"])
        c.sim["sat"] += v
        c.sim["sector_n"][s] += 1
        c.sim["sector_v"][s] += v


# ====================================================================== core
def core_plan(c):
    P, E = c.P, c.equity
    cp = c.core_pos()
    core_qty = float(cp["qty"]) if cp else 0.0
    core_mv = c.mv(cp) if cp else 0.0
    sat = c.sat_pct()
    if "KS-3" in c.failed:
        target, why = P["core_riskoff_target"], "KS-3 halt"
    elif c.reg["state"] == "risk-off":
        target, why = P["core_riskoff_target"], "risk-off"
    else:
        target = min(max(P["core_target_base"] - sat, P["core_target_min"]), P["core_target_max"])
        why = "risk-on: %.0f%% - satellites %.1f%%, clamped %.0f-%.0f%%" % (
            P["core_target_base"] * 100, sat * 100, P["core_target_min"] * 100, P["core_target_max"] * 100)
    pct = core_mv / E if E else 0
    c.core_line = "CORE %s: %g sh = %s (%.1f%%) | target %.1f%% (%s) | band +/-%.0fpp" % (
        c.core, core_qty, money(core_mv), pct * 100, target * 100, why, P["core_band"] * 100)
    today_core = [o for o in c.closed_orders + c.open_orders
                  if (o.get("client_order_id") or "").startswith("core-%s" % c.today)]
    live = [o for o in today_core if o["status"] in WORKING or float(o.get("filled_qty") or 0) > 0]
    if live:
        return "DONE_TODAY (%s %s)" % (live[0]["client_order_id"], live[0]["status"])
    if abs(pct - target) <= P["core_band"]:
        return "HOLD (in band)"
    if not c.orders_allowed:
        return "BLOCKED (%s)" % ", ".join(sorted(c.failed & {"KS-6", "KS-8", "KS-9"}) or ["account blocked"])
    if pct < target:
        if not c.buys_allowed:
            return "BLOCKED buy (%s)" % (", ".join(sorted(c.failed & {"KS-1", "KS-2", "KS-3", "KS-7"})) or "paused: %s" % c.paused)
        px = c.price(c.core, "buy")
        if not px:
            return "BLOCKED (no %s quote)" % c.core
        limit = round(px * 1.001, 2)
        qty = int(round((target * E - core_mv) / limit))
        qty = min(qty, int(math.floor((c.cash_avail - P["cash_min"] * E) / limit)), int(os.environ.get("MAX_ORDER_QTY", "25")))
        if qty < 1:
            return "HOLD (below band but cash reserve allows 0 shares)"
        body = {"symbol": c.core, "qty": str(qty), "side": "buy", "type": "limit", "limit_price": "%.2f" % limit,
                "time_in_force": "day", "client_order_id": c.next_coid("core-%s" % c.today)}
        return "BUY %d %s limit %.2f (%s) -> %s" % (qty, c.core, limit, money(qty * limit), cmd_order(body))
    bought_today = any(f["sym"] == c.core and f["side"] == "buy" and c.et_date(f["t"]) == c.today for f in c.fills)
    if bought_today:
        return "DEFER sell to tomorrow (core bought today - selling now would be a day trade)"
    px = c.price(c.core, "sell")
    if not px:
        return "BLOCKED (no %s quote)" % c.core
    limit = round(px * 0.999, 2)
    qty = min(int(round((core_mv - target * E) / limit)), int(core_qty))
    if qty < 1:
        return "HOLD (above band by less than one share)"
    if c.stop_orders(c.core):
        return "BLOCKED sell (core has a stop order - core must not have one; cancel it first)"
    body = {"symbol": c.core, "qty": str(qty), "side": "sell", "type": "limit", "limit_price": "%.2f" % limit,
            "time_in_force": "day", "client_order_id": c.next_coid("core-%s" % c.today)}
    return "SELL %d %s limit %.2f (%s) -> %s" % (qty, c.core, limit, money(qty * limit), cmd_order(body))


# ============================================================ maintenance
def atr_stop_pct(c, sym, price):
    try:
        b, _ = tlib.bars_multi([sym], 30)
        a = tlib.atr(b.get(sym, []), 14)
    except tlib.AlpacaError:
        a = None
    if not a or not price:
        return c.P["stop_max"]
    return min(max(c.P["stop_min"], c.P["stop_atr_mult"] * a / price), c.P["stop_max"])


def maintenance(c):
    """Orphan stops (KS-10), trailing-stop tightening, KS-4 trims, KS-3 liquidation."""
    acts = []
    if not c.orders_allowed:
        bad = ", ".join(sorted(c.failed & {"KS-6", "KS-8", "KS-9"})) or "account blocked"
        return ["BLOCKED - no orders of any kind while %s fail(s); fix that first%s" % (
            bad, " (unprotected: %s)" % ", ".join(c.unprotected) if c.unprotected else "")]
    if "KS-3" in c.failed:
        acts.append("KS-3 HALT: cancel every satellite stop, close every satellite (alpaca.sh close SYM), "
                    "sell core down to %.0f%%, alert the user. Manual reset required." % (c.P["core_riskoff_target"] * 100))
    for sym in c.unprotected:
        p = next(p for p in c.positions if p["symbol"] == sym)
        px = float(p.get("current_price") or 0)
        stop = atr_stop_pct(c, sym, px)
        body = {"symbol": sym, "qty": str(c.uncovered[sym]), "side": "sell", "type": "trailing_stop",
                "trail_percent": "%.1f" % (stop * 100), "time_in_force": "gtc",
                "client_order_id": c.next_coid("stop-%s-%s" % (c.today, sym))}
        acts.append("ORPHAN %s: %d sh without a stop - place now -> %s" % (sym, c.uncovered[sym], cmd_order(body)))
    for p in c.sats():
        sym, up = p["symbol"], float(p.get("unrealized_plpc") or 0)
        px = float(p.get("current_price") or 0)
        if px > 0 and c.mv(p) / c.equity > c.P["ks4_position_max"]:
            trim = math.ceil((c.mv(p) - c.P["sat_max_pct"] * c.equity) / px)
            acts.append("KS-4 TRIM %s: sell %d sh back to %.0f%% (cancel its stop, sell, re-place stop for the rest)"
                        % (sym, trim, c.P["sat_max_pct"] * 100))
        want = 5.0 if up >= 0.20 else 7.0 if up >= 0.15 else None
        if want is None:
            continue
        for o in c.stop_orders(sym):
            if o.get("type") != "trailing_stop":
                continue
            cur = float(o.get("trail_percent") or 0)
            hwm = float(o.get("hwm") or px)
            if want >= cur:
                continue
            new_stop = hwm * (1 - want / 100)
            if new_stop > px * 0.97:
                acts.append("TIGHTEN %s skipped: %.0f%% trail would put the stop within 3%% of price" % (sym, want))
                continue
            acts.append("TIGHTEN %s (unrealized %s): trail %.1f -> %.1f -> bash scripts/alpaca.sh order-replace %s '{\"trail\":\"%g\"}'"
                        % (sym, tlib.fmt_pct(up), cur, want, o["id"], want))
    if c.core_pos() and c.stop_orders(c.core):
        acts.append("CORE has a stop order (%s) - the core never carries a stop: cancel it"
                    % ", ".join(o["id"] for o in c.stop_orders(c.core)))
    return acts


# ================================================================ --check
def check(c, spec):
    sym = spec.partition(":")[0].upper()
    P, E = c.P, c.equity
    planned = tlib.research_candidates(c.today).get(sym)
    ref = "%.2f" % planned["ref"] if planned else ""
    out = ["CHECK %s (research ref %s)" % (sym, ref or "none")]
    gates = [("PLAN", bool(planned), "CANDIDATE line in today's research entry (G1-G7 passed pre-market)" if planned
              else "not a CANDIDATE line in today's (%s) RESEARCH-LOG entry - only planned names may be bought" % c.today)]
    sector = tlib.sector_of(sym)
    gates.append(("G1", sector != "UNKNOWN", "%s in WATCHLIST/sector ETFs" % sym if sector != "UNKNOWN"
                  else "%s is not in WATCHLIST.md or the sector ETFs" % sym))
    held = any(p["symbol"] == sym for p in c.positions)
    working = [o for o in c.open_orders if o["symbol"] == sym]
    gates.append(("G0", not held and not working, "held" if held else ("open order %s" % working[0]["id"] if working
                                                                     else "not held, no open order")))
    try:
        snap = tlib.snapshots([sym]).get(sym)
    except tlib.AlpacaError:
        snap = None
    q = tlib.quote_from_snapshot(snap, bool(c.clock.get("is_open")), c.now) if snap else None
    ask = q["ask_or_last"] if q else 0
    limit = round(ask * 1.001, 2) if ask else 0
    stop = atr_stop_pct(c, sym, ask) if ask else P["stop_max"]
    cash_avail = c.cash_avail - c.sim["cash"]
    budget = min(P["sat_max_pct"] * E, cash_avail - P["cash_min"] * E)
    qty = int(math.floor(budget / limit)) if limit else 0
    size = qty * limit
    g8 = qty >= 1 and size >= P["sat_min_pct"] * E
    gates.append(("G8", g8, "qty %d @ limit %.2f = %s (%.1f%% of equity; budget %s, min %.0f%%); trailing stop %.1f%%"
                  % (qty, limit, money(size), size / E * 100 if E else 0, money(budget), P["sat_min_pct"] * 100, stop * 100)))
    if ask and ask > P["sat_price_max_pct"] * E:
        gates[1] = ("G1", False, "ask %.2f above the %.0f%%-of-equity price cap %s" % (ask, P["sat_price_max_pct"] * 100,
                                                                                    money(P["sat_price_max_pct"] * E)))
    sec_pos = [p for p in c.sats() if tlib.sector_of(p["symbol"]) == sector]
    sec_n = len(sec_pos) + c.sim["sector_n"][sector]
    sec_pct = (sum(c.mv(p) for p in sec_pos) + c.sim["sector_v"][sector] + size) / E if E else 0
    tot_pct = c.sat_pct() + (c.sim["sat"] + size) / E if E else 0
    cash_after = cash_avail - size
    slots = c.slots - c.sim["slots"]
    cool = sector_cooldowns(c)
    why = []
    if not c.sat_allowed:
        why.append("satellite entries blocked (%s)" % (", ".join(sorted(c.failed)) or ("paused" if c.paused else "account")))
    if slots < 1:
        why.append("no slots (positions %d/%d, today %d/%d, week %d/%d, approved earlier in this check %d)" % (
            len(c.sats()), c.maxpos, c.entries_today, P["entries_per_day"], c.entries_week, P["entries_per_week"],
            c.sim["slots"]))
    if sec_n >= P["sat_sector_max_positions"]:
        why.append("%s already has %d satellites (incl. working/approved)" % (sector, sec_n))
    if sec_pct > P["sat_sector_max_pct"]:
        why.append("%s would be %.1f%% > %.0f%%" % (sector, sec_pct * 100, P["sat_sector_max_pct"] * 100))
    if tot_pct > P["sat_total_max"]:
        why.append("satellites would be %.1f%% > %.0f%%" % (tot_pct * 100, P["sat_total_max"] * 100))
    if cash_after < P["cash_min"] * E:
        why.append("cash after %s < %.0f%% reserve" % (money(cash_after), P["cash_min"] * 100))
    if sector in cool:
        why.append("sector cooldown: " + cool[sector])
    gates.append(("G9", not why, "; ".join(why) or "slots %d, %s %d/%d sats %.1f%%, total sats %.1f%%, cash after %s"
                  % (slots, sector, sec_n, P["sat_sector_max_positions"], sec_pct * 100, tot_pct * 100, money(cash_after))))
    ev = tlib.events_on(c.today)
    gates.append(("G10", not ev, "event today: %s" % ",".join(ev) if ev else "no FOMC/CPI/NFP today (EVENTS.md)"))
    if not q:
        gates.append(("G11", False, "no snapshot"))
    else:
        r = float(ref) if ref else 0
        dev = ask / r - 1 if r else None
        ok = q["status"] == "OK" and q["spread"] is not None and q["spread"] <= P["max_spread"] \
            and dev is not None and abs(dev) <= P["max_ref_deviation"] and bool(c.clock.get("is_open"))
        gates.append(("G11", ok, "market %s, status %s, last trade %s min, spread %s, ask %.2f vs ref %s (%s; max +/-%.0f%%)" % (
            "open" if c.clock.get("is_open") else "CLOSED", q["status"],
            "n/a" if q["age_min"] is None else "%.0f" % q["age_min"],
            "n/a" if q["spread"] is None else "%.2f%%" % (q["spread"] * 100), ask, ref or "none",
            tlib.fmt_pct(dev), P["max_ref_deviation"] * 100)))
    for g, ok, why_ in gates:
        out.append("  %s %s - %s" % (g, "PASS" if ok else "FAIL", why_))
    if all(ok for _, ok, _ in gates):
        coid = c.next_coid("sat-%s-%s" % (c.today, sym))
        body = {"symbol": sym, "qty": str(qty), "side": "buy", "type": "limit", "limit_price": "%.2f" % limit,
                "time_in_force": "day", "client_order_id": coid}
        out.append("  VERDICT BUY -> %s" % cmd_order(body))
        c.sim["slots"] += 1                        # later candidates in this same call see the reduced room
        c.sim["cash"] += size
        c.sim["sat"] += size
        c.sim["sector_n"][sector] += 1
        c.sim["sector_v"][sector] += size
        out.append("  THEN wait-fill; on fill (use filled_qty, cancel any unfilled rest first) -> " + cmd_order(
            {"symbol": sym, "qty": "<filled_qty>", "side": "sell", "type": "trailing_stop",
             "trail_percent": "%.1f" % (stop * 100), "time_in_force": "gtc",
             "client_order_id": c.next_coid("stop-%s-%s" % (c.today, sym))}))
    else:
        out.append("  VERDICT SKIP - fails %s" % ",".join(g for g, ok, _ in gates if not ok))
    return out


# ================================================================== reports
def spy_return_since(c, since_date):
    """SPY close-to-close return from the last close before since_date to today's close.
    Returns (return, note): return is None unless today's completed bar is available,
    so a missing bar is reported as unavailable instead of a false 0%."""
    try:
        n = max(5, c.trading_days_after(since_date - dt.timedelta(days=1)) + 5)
        b, _ = tlib.bars_multi(["SPY"], min(n, 300), "now")
        bars = b.get("SPY", [])
    except tlib.AlpacaError as e:
        return None, "unavailable (%s)" % str(e)[:80]
    base = [x for x in bars if x["t"][:10] < since_date.isoformat()]
    if not bars or not base:
        return None, "unavailable (no SPY bars)"
    if bars[-1]["t"][:10] != c.today.isoformat():
        return None, "unavailable (latest SPY bar is %s)" % bars[-1]["t"][:10], bars[-1]["c"], bars[-1]["t"][:10]
    return bars[-1]["c"] / base[-1]["c"] - 1, "", bars[-1]["c"], bars[-1]["t"][:10]


def spy_fmt(r):
    return tlib.fmt_pct(r[0], 2) if r[0] is not None else r[1]


def eod_block(c):
    E, P = c.equity, c.P
    day = E - c.last_equity if c.last_equity else 0
    phase = E - c.start_equity
    spy_day = spy_return_since(c, c.today)
    spy_phase = spy_return_since(c, c.start_date)
    hist = dict(c.state.get("eod") or {})
    spy_close = spy_day[2] if len(spy_day) > 2 and spy_day[3] == c.today.isoformat() else None
    pos_rows = []
    for p in c.positions:
        sym = p["symbol"]
        so = c.stop_orders(sym)
        pos_rows.append({"sym": sym, "role": "core" if sym == c.core else "satellite", "qty": float(p["qty"]),
                         "avg": float(p["avg_entry_price"]), "last": float(p.get("current_price") or 0),
                         "plpc": float(p.get("unrealized_plpc") or 0), "pct": round(c.mv(p) / E, 4) if E else 0,
                         "stop": "; ".join("%s%%" % (o.get("trail_percent") or "?") for o in so) or ("-" if sym == c.core else "NONE")})
    hist[c.today.isoformat()] = {"equity": round(E, 2), "invested": round(c.invested(), 4), "cash": round(c.cash, 2),
                                 "spy_close": spy_close, "regime": c.reg["state"], "ks_fail": sorted(c.failed),
                                 "positions": pos_rows, "sat_pct": round(c.sat_pct(), 4)}
    c.eod_hist = hist
    floor, streak = P["deploy_floor"], 0
    for d in sorted(hist, reverse=True):
        if hist[d]["invested"] < floor:
            streak += 1
        else:
            break
    n_day = sum(1 for d in c.trading_days if c.start_date <= d <= c.today)
    lines = ["### %s - EOD Snapshot (Day %d, %s)" % (c.today, n_day, c.today.strftime("%A")),
             "**Portfolio:** %s | **Cash:** %s (%.1f%%) | **Invested:** %.1f%% (floor %.0f%%, days below: %d) | "
             "**Day P&L:** %s (%s) | **Phase P&L:** %s (%s) | **SPY today:** %s | **SPY phase:** %s | **Regime:** %s"
             % (money(E), money(c.cash), c.cash / E * 100, c.invested() * 100, floor * 100, streak,
                money(day), tlib.fmt_pct(day / c.last_equity if c.last_equity else 0, 2), money(phase),
                tlib.fmt_pct(phase / c.start_equity if c.start_equity else 0, 2),
                spy_fmt(spy_day), spy_fmt(spy_phase), c.reg["state"]),
             "", "| Ticker | Role | Shares | Entry | Last | Day chg | Unrealized | % of equity | Stop |",
             "|---|---|---|---|---|---|---|---|---|"]
    for p in sorted(c.positions, key=lambda p: -c.mv(p)):
        sym = p["symbol"]
        so = c.stop_orders(sym)
        st = "-" if sym == c.core else (
            "; ".join("%s %s%%/hwm %s (%s)" % (o["type"], o.get("trail_percent") or "", o.get("hwm") or "-", o["id"][:8])
                      for o in so) or "NONE")
        lines.append("| %s | %s | %g | %.2f | %.2f | %s | %s (%s) | %.1f%% | %s |" % (
            sym, "core" if sym == c.core else "satellite", float(p["qty"]), float(p["avg_entry_price"]),
            float(p.get("current_price") or 0), tlib.fmt_pct(float(p.get("change_today") or 0)),
            money(float(p.get("unrealized_pl") or 0)), tlib.fmt_pct(float(p.get("unrealized_plpc") or 0)),
            c.mv(p) / E * 100, st))
    if not c.positions:
        lines.append("| - | - | - | - | - | - | - | - | - |")
    today_fills = [f for f in c.fills if c.et_date(f["t"]) == c.today]
    lines.append("")
    lines.append("**Fills today:** " + ("; ".join("%s %g %s @ %.2f (%s)" % (f["side"], f["qty"], f["sym"], f["px"], f["coid"])
                                                  for f in today_fills) or "none"))
    return lines


def week_block(c):
    E = c.equity
    monday = tlib.monday_of(c.today)
    wk_ret = E / c.week_base - 1 if c.week_base else 0
    spy_wk_r = spy_return_since(c, monday)
    spy_ph_r = spy_return_since(c, c.start_date)
    spy_wk = spy_wk_r[0]
    h = c.history or {}
    eqs = [(tlib.to_et(dt.datetime.fromtimestamp(ts, tlib.UTC)).date(), float(eq))
           for ts, eq in zip(h.get("timestamp") or [], h.get("equity") or []) if eq]
    phase_eq = [e for d, e in eqs if d >= c.start_date] + [E]
    peak, mdd = -1.0, 0.0
    for e in phase_eq:
        peak = max(peak, e)
        mdd = min(mdd, e / peak - 1)
    week_eq = [e for d, e in eqs if d >= monday] + [E]
    wk_dd = min([e / c.week_base - 1 for e in week_eq] + [0]) if c.week_base else 0
    trips = [t for t in c.trips if c.et_date(t["exit_t"]) >= monday]
    wins = [t for t in trips if t["pnl"] > 0]
    losses = [t for t in trips if t["pnl"] <= 0]
    pf = (sum(t["pnl"] for t in wins) / abs(sum(t["pnl"] for t in losses))) if losses and sum(t["pnl"] for t in losses) else None
    eod = c.state.get("eod") or {}
    wk_eod = {d: v for d, v in eod.items() if d >= monday.isoformat()}
    avg_inv = sum(v["invested"] for v in wk_eod.values()) / len(wk_eod) if wk_eod else None
    below = sum(1 for v in wk_eod.values() if v["invested"] < c.P["deploy_floor"])
    lines = ["WEEK STATS (week of %s)" % monday,
             "| Metric | Value |", "|---|---|",
             "| Start (%s) | %s |" % (c.week_base_name, money(c.week_base)),
             "| End | %s |" % money(E),
             "| Week return | %s |" % tlib.fmt_pct(wk_ret, 2),
             "| SPY week | %s |" % spy_fmt(spy_wk_r),
             "| Bot vs SPY (week) | %s |" % (tlib.fmt_pct(wk_ret - spy_wk, 2) if spy_wk is not None else "n/a"),
             "| Phase return / SPY phase | %s / %s |" % (tlib.fmt_pct(E / c.start_equity - 1, 2), spy_fmt(spy_ph_r)),
             "| Max intraweek DD (daily closes) | %s |" % tlib.fmt_pct(wk_dd, 2),
             "| Max DD since start | %s |" % tlib.fmt_pct(mdd, 2),
             "| Entries this week | %d (cap %d) |" % (c.entries_week, c.P["entries_per_week"]),
             "| Closed round trips | %d (W:%d / L:%d) |" % (len(trips), len(wins), len(losses)),
             "| Profit factor | %s |" % ("n/a" if pf is None else "%.2f" % pf),
             "| Avg invested at EOD | %s |" % ("n/a" if avg_inv is None else "%.1f%%" % (avg_inv * 100)),
             "| EODs below %.0f%% floor | %d of %d |" % (c.P["deploy_floor"] * 100, below, len(wk_eod))]
    for t in trips:
        lines.append("  closed %s %g sh: %.2f -> %.2f = %s (%s)" % (t["sym"], t["qty"], t["entry"], t["exit"],
                                                                  money(t["pnl"]), tlib.fmt_pct(t["pnl_pct"])))
    return lines


def save_state_field(c, key, value):
    """Persist one field immediately (used for kill-switch latches)."""
    cur = {}
    if os.path.exists(STATE_JSON):
        with open(STATE_JSON, encoding="utf-8") as f:
            cur = json.load(f)
    cur[key] = value
    with open(STATE_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cur, f, indent=1, sort_keys=True)
        f.write("\n")


def reconcile(c, prev):
    """Positions expected from the last snapshot plus every fill since, per order id."""
    seen = c.state.get("filled") or {}
    exp = collections.Counter({k: float(v) for k, v in prev.items()})
    orders = {o["id"]: o for o in c.closed_orders + c.open_orders}
    for oid, o in orders.items():
        delta = float(o.get("filled_qty") or 0) - float(seen.get(oid, 0))
        if abs(delta) > 1e-9:
            exp[o["symbol"]] += delta if o["side"] == "buy" else -delta
    act = {p["symbol"]: float(p["qty"]) for p in c.positions}
    return {s: (exp.get(s, 0), act.get(s, 0)) for s in set(exp) | set(act) if abs(exp.get(s, 0) - act.get(s, 0)) > 1e-6}


def write_state(c, weekly=False):
    prev_fail = set(c.state.get("ks_fail") or [])
    now_fail = sorted(c.failed)
    latch = dict(c.state.get("latch") or {})
    if weekly and "KS-2" in latch and not c.fail_now.get("KS-2"):
        latch.pop("KS-2")                          # reset at the weekly review once recovered
    filled = {o["id"]: float(o.get("filled_qty") or 0) for o in c.closed_orders + c.open_orders
              if float(o.get("filled_qty") or 0) > 0}
    state = {"asof": tlib.iso(c.now), "positions": {p["symbol"]: float(p["qty"]) for p in c.positions},
             "filled": filled, "latch": latch,
             "ks_fail": now_fail, "regime": c.reg["state"], "eod": getattr(c, "eod_hist", c.state.get("eod") or {})}
    with open(STATE_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, indent=1, sort_keys=True)
        f.write("\n")
    md = ["# STATE (generated by scripts/ks.py --write-state - do not edit)", "",
          "- asof: %s ET" % c.now_et.strftime("%Y-%m-%d %H:%M"),
          "- mode: %s | account: %s" % (c.mode, c.acct.get("account_number")),
          "- equity: %s | cash: %s | last_equity: %s | start: %s on %s" % (
              money(c.equity), money(c.cash), money(c.last_equity), money(c.start_equity), c.start_date),
          "- invested: %.1f%% | satellites: %.1f%% | regime: %s" % (c.invested() * 100, c.sat_pct() * 100, c.reg["state"]),
          "- entries today/week: %d/%d | daytrade_count: %s | slots: %d" % (
              c.entries_today, c.entries_week, c.acct.get("daytrade_count"), c.slots),
          "- failing switches: %s" % (", ".join(now_fail) or "none"),
          "- paused: %s" % (c.paused or "no"), "", "| Symbol | Qty | Avg | Last | Stop orders |", "|---|---|---|---|---|"]
    for p in c.positions:
        so = c.stop_orders(p["symbol"])
        md.append("| %s | %g | %.2f | %.2f | %s |" % (p["symbol"], float(p["qty"]), float(p["avg_entry_price"]),
                                                     float(p.get("current_price") or 0),
                                                     ", ".join("%s %s %s%%" % (o["id"], o["type"], o.get("trail_percent") or "")
                                                               for o in so) or "-"))
    md.append("")
    md.append("Open orders: " + ("; ".join("%s %s %s %s (%s)" % (o["side"], o.get("qty"), o["symbol"], o["type"],
                                                                o.get("client_order_id")) for o in c.open_orders) or "none"))
    with open(STATE_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")
    new = [k for k in now_fail if k not in prev_fail]
    if new:
        detail = "; ".join("%s %s" % (r[0], r[2]) for r in c.ks_rows if r[0].split()[0] in new)
        rc = subprocess.run([tlib._bash(), os.path.join(tlib.ROOT, "scripts", "notify.sh"), "--alert",
                             "Kill switch newly FAILING: %s" % detail]).returncode
        if rc != 0:
            # not delivered: forget these so the next run alerts again
            state["ks_fail"] = [k for k in now_fail if k not in new]
            with open(STATE_JSON, "w", encoding="utf-8", newline="\n") as f:
                json.dump(state, f, indent=1, sort_keys=True)
                f.write("\n")
            return new, False
    return new, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", nargs="*", default=[])
    ap.add_argument("--eod", action="store_true")
    ap.add_argument("--week", action="store_true")
    ap.add_argument("--write-state", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")

    c = Ctx()
    try:
        c.load()
    except tlib.AlpacaError as e:
        print("KS-6 FAIL - could not load account state: %s" % e)
        print("ORDERS_ALLOWED=no (treat as KS-6: place no orders this run)")
        sys.exit(2)
    kill_switches(c)
    flags(c)
    core_action = core_plan(c)

    print("KS REPORT %s ET | %s | market %s | account %s" % (
        c.now_et.strftime("%Y-%m-%d %H:%M"), c.mode, "OPEN" if c.clock.get("is_open") else "closed",
        c.acct.get("account_number")))
    print("Equity %s | cash %s | last_equity %s | start %s (%s) | invested %.1f%% | satellites %.1f%%" % (
        money(c.equity), money(c.cash), money(c.last_equity), money(c.start_equity), c.start_date,
        c.invested() * 100, c.sat_pct() * 100))
    print("| Switch | Status | Value | Limit |")
    print("|---|---|---|---|")
    for r in c.ks_rows:
        print("| %s | %s | %s | %s |" % r)
    print("ORDERS_ALLOWED=%s | BUYS_ALLOWED=%s | SAT_ENTRIES_ALLOWED=%s | SAT_SLOTS=%d (positions %d/%d, today %d/%d, week %d/%d)%s" % (
        "yes" if c.orders_allowed else "no", "yes" if c.buys_allowed else "no", "yes" if c.sat_allowed else "no",
        c.slots, len(c.sats()), c.maxpos, c.entries_today, c.P["entries_per_day"], c.entries_week,
        c.P["entries_per_week"], " | PAUSED (%s)" % c.paused if c.paused else ""))
    reg = c.reg
    print("REGIME %s (SPY %s vs SMA200 %s; %s)" % (reg["state"], "%.2f" % reg["close"] if reg["close"] else "n/a",
                                                  "%.2f" % reg["sma200"] if reg["sma200"] else "n/a",
                                                  reg["note"] or "%d consecutive closes %s" % (
                                                      abs(reg["streak"]), "above" if reg["streak"] > 0 else "below")))
    print(c.core_line)
    print("CORE_ACTION=%s" % core_action)
    cool = sector_cooldowns(c)
    print("SECTOR_COOLDOWNS=%s" % ("; ".join("%s: %s" % kv for kv in cool.items()) or "none"))
    acts = maintenance(c)
    print("MAINTENANCE=%s" % ("none" if not acts else ""))
    for a in acts:
        print("  " + a)
    for spec in args.check:
        print()
        print("\n".join(check(c, spec)))
    if args.eod:
        print()
        print("\n".join(eod_block(c)))
    if args.week:
        print()
        print("\n".join(week_block(c)))
    if args.write_state:
        new, delivered = write_state(c, weekly=args.week)
        print()
        print("STATE written (memory/STATE.json, memory/STATE.md)%s" % (
            "" if not new else ("; ALERT sent for newly failing: " if delivered
                                else "; ALERT FAILED (webhook) for newly failing: ") + ", ".join(new)))


if __name__ == "__main__":
    main()
