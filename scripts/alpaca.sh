#!/usr/bin/env bash
# Alpaca API wrapper. All trading and market-data calls go through here.
# Usage: bash scripts/alpaca.sh <subcommand> [args...]   (no args = help)
#
# Defaults to PAPER trading. Override with ALPACA_ENDPOINT env var for live.
# Auth: ALPACA_API_KEY + ALPACA_SECRET_KEY env vars, or ALPACA_AUTH=proxy when the
# cloud environment injects the keys as network secrets.
#
# Safety rails (enforced here, not in prompts):
#   - every order needs a client_order_id in the convention (Alpaca rejects
#     duplicates, so a retried routine can never double-buy)
#   - whole shares only; buys are limit/day and their notional must fit in CASH
#     (never margin buying power); sells can never exceed the position (no shorts)
#   - buys refused while PAUSED.flag exists; all orders refused on a live endpoint
#     unless LIVE_TRADING_CONFIRMED=yes; bulk close/cancel need ALPACA_ALLOW_BULK=1
#   - ALPACA_DRY_RUN=1 prints orders instead of sending them (local rehearsal only)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=scripts/env.sh
source "$ROOT/scripts/env.sh"

PY="$(command -v python3 || command -v python || true)"
[[ -n "$PY" ]] || { echo "python3 not found" >&2; exit 1; }
py() { "$PY" "$@" | tr -d '\r'; }   # tr: Windows Python writes CRLF
TLIB="$ROOT/scripts/tlib.py"

API="${ALPACA_ENDPOINT:-https://paper-api.alpaca.markets/v2}"
DATA="${ALPACA_DATA_ENDPOINT:-https://data.alpaca.markets/v2}"
FEED="${ALPACA_DATA_FEED:-iex}"   # real-time quotes/snapshots; history uses SIP (see bars)
DATA_ROOT="${DATA%/v2}"           # news (v1beta1) and crypto (v1beta3) live beside /v2

AUTH=()
if [[ "${ALPACA_AUTH:-}" != "proxy" ]]; then
    : "${ALPACA_API_KEY:?ALPACA_API_KEY not set in environment (or set ALPACA_AUTH=proxy)}"
    : "${ALPACA_SECRET_KEY:?ALPACA_SECRET_KEY not set in environment}"
    AUTH=(-H "APCA-API-KEY-ID: $ALPACA_API_KEY" -H "APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY")
fi

# req METHOD URL [BODY] - prints the response body (also on HTTP errors, so
# rejection reasons are visible) and returns non-zero on transport failure or
# HTTP >= 400. GETs retry twice on 429/5xx/transport errors; writes never retry.
req() {
    local method="$1" url="$2" body="${3:-}" tries=1 out code i
    [[ "$method" == GET ]] && tries=3
    out="$(mktemp)"
    for ((i = 1; i <= tries; i++)); do
        local args=(-sS --max-time 30 -o "$out" -w '%{http_code}' -X "$method" "${AUTH[@]}")
        [[ -n "$body" ]] && args+=(-H "Content-Type: application/json" --data "$body")
        code="$(curl "${args[@]}" "$url" 2>/dev/null)" || code="000"
        if [[ "$code" =~ ^(000|429|5[0-9][0-9])$ && $i -lt $tries ]]; then
            sleep 2
            continue
        fi
        break
    done
    cat "$out"
    rm -f "$out"
    echo
    if [[ "$code" == 000 || "$code" -ge 400 ]]; then
        echo "[alpaca] HTTP $code on $method ${url%%\?*}" >&2
        return 1
    fi
}

# Historical bars: SIP (full consolidated volume, official closes) is free when
# the window ends >= 15 min ago; fall back to IEX if the plan refuses it.
bars_get() {
    local url="$1" out
    if out="$(req GET "$url&feed=sip" 2>/dev/null)"; then
        echo "$out"
    else
        echo "FEED_USED=iex (SIP refused; volumes are IEX-only)" >&2
        req GET "$url&feed=iex"
    fi
}

live_guard() {
    if [[ "$API" != *paper-api* && "${LIVE_TRADING_CONFIRMED:-}" != "yes" ]]; then
        echo "REFUSED: live endpoint ($API) without LIVE_TRADING_CONFIRMED=yes" >&2
        exit 5
    fi
}

guard_order() {
    local body="$1" sym side acct pos=""
    live_guard
    read -r sym side < <(py -c 'import json,sys
b=json.loads(sys.argv[1]); print(str(b.get("symbol","-")).upper() or "-", b.get("side") or "-")' "$body")
    acct="$(req GET "$API/account")"
    open_orders="$(req GET "$API/orders?status=open&limit=500")"
    if [[ "$side" == sell ]]; then
        pos="$(req GET "$API/positions/$sym" 2>/dev/null || true)"
    fi
    py - "$body" "$acct" "$pos" "$ROOT" "$open_orders" <<'PYEOF'
import json, os, re, sys
body, acct, pos, root, open_orders = sys.argv[1:6]

def refuse(msg):
    print("REFUSED: " + msg, file=sys.stderr)
    sys.exit(5)

try:
    b = json.loads(body)
except Exception as e:
    refuse("order body is not valid JSON: %s" % e)
a = json.loads(acct)
sym = str(b.get("symbol", "")).upper()
side, typ, tif = b.get("side"), b.get("type"), b.get("time_in_force")
coid = b.get("client_order_id") or ""
if not re.match(r"^[A-Z]{1,5}(\.[A-Z])?$", sym):
    refuse("symbol %r is not a plain stock/ETF ticker (options are forbidden)" % sym)
if not re.match(r"^(core|sat|stop|exit|trim|test)-\d{4}-\d{2}-\d{2}[A-Za-z0-9-]*$", coid):
    refuse("client_order_id %r missing or not in convention (core|sat|stop|exit|trim)-<DATE>-..." % coid)
if "notional" in b:
    refuse("notional orders are not allowed (whole shares only)")
qty_s = str(b.get("qty", ""))
if not re.match(r"^[1-9][0-9]*$", qty_s):
    refuse("qty must be a whole-number string like \"3\", got %r" % qty_s)
qty, maxq = int(qty_s), int(os.environ.get("MAX_ORDER_QTY", "25"))
if qty > maxq:
    refuse("qty %d exceeds MAX_ORDER_QTY %d" % (qty, maxq))
if a.get("trading_blocked") or a.get("account_blocked"):
    refuse("account is blocked")
if side == "buy":
    for p in ("memory/PAUSED.flag", "PAUSED.flag"):
        if os.path.exists(os.path.join(root, p)):
            refuse("paused (%s): buys are disabled" % p)
    if typ != "limit":
        refuse("buys must be type=limit")
    if tif != "day":
        refuse("buys must be time_in_force=day")
    if b.get("extended_hours"):
        refuse("extended-hours orders are not allowed")
    lp = float(b.get("limit_price") or 0)
    if lp <= 0:
        refuse("limit_price is required")
    notional = qty * lp
    cash, equity = float(a.get("cash", 0)), float(a.get("equity", 0))
    # Alpaca's cash does not reserve working buy orders - subtract them ourselves.
    reserved = sum((float(o.get("qty") or 0) - float(o.get("filled_qty") or 0)) * float(o.get("limit_price") or 0)
                   for o in json.loads(open_orders or "[]") if o.get("side") == "buy")
    if notional > cash - reserved:
        refuse("notional $%.2f > cash $%.2f minus $%.2f reserved by open buy orders (margin is never used)"
               % (notional, cash, reserved))
    if notional > 0.85 * equity:
        refuse("notional $%.2f > 85%% of equity $%.2f" % (notional, equity))
elif side == "sell":
    try:
        held = float(json.loads(pos).get("qty", 0)) if pos.strip() else 0.0
    except Exception:
        held = 0.0
    if held <= 0 or qty > held:
        refuse("sell qty %d > position %g in %s (sells may never open a short)" % (qty, held, sym))
    if typ not in ("market", "limit", "stop", "stop_limit", "trailing_stop"):
        refuse("order type %r not allowed" % typ)
    if typ == "trailing_stop":
        tp = float(b.get("trail_percent") or 0)
        if not 1 <= tp <= 15:
            refuse("trail_percent must be between 1 and 15")
        if tif != "gtc":
            refuse("trailing stops must be time_in_force=gtc")
else:
    refuse("side must be buy or sell")
print("[guard] OK %s %s %d %s" % (side, sym, qty, coid), file=sys.stderr)
PYEOF
}

dry() {
    echo "{\"dry_run\": true, \"request\": \"$1\", \"id\": \"dry-run\", \"status\": \"dry_run\"}"
    echo "[alpaca] DRY RUN - nothing sent" >&2
    exit 0
}

cmd="${1:-}"
shift || true

case "$cmd" in
    account)
        req GET "$API/account"
        ;;
    positions)
        req GET "$API/positions"
        ;;
    position)
        sym="${1:?usage: position SYM}"
        req GET "$API/positions/$sym"
        ;;
    clock)
        req GET "$API/clock"
        ;;
    calendar)
        start="${1:-$(py "$TLIB" et-date-offset 0)}"
        end="${2:-$(py "$TLIB" et-date-offset 168)}"
        req GET "$API/calendar?start=$start&end=$end"
        ;;
    quote)
        sym="${1:?usage: quote SYM}"
        req GET "$DATA/stocks/$sym/quotes/latest?feed=$FEED"
        ;;
    snapshot)
        sym="${1:?usage: snapshot SYM}"
        req GET "$DATA/stocks/$sym/snapshot?feed=$FEED"
        ;;
    snapshots)
        syms="${1:?usage: snapshots SYM1,SYM2,...}"
        req GET "$DATA/stocks/snapshots?symbols=$syms&feed=$FEED"
        ;;
    price)
        # One normalised line: bid/ask/last, trade age, spread, prev close, STALE flag.
        sym="${1:?usage: price SYM}"
        snap="$(req GET "$DATA/stocks/$sym/snapshot?feed=$FEED")"
        clk="$(req GET "$API/clock")"
        py - "$sym" "$snap" "$clk" "$ROOT/scripts" <<'PYEOF'
import json, sys
sys.path.insert(0, sys.argv[4])
import tlib
sym, snap, clk = sys.argv[1], json.loads(sys.argv[2]), json.loads(sys.argv[3])
q = tlib.quote_from_snapshot(snap, clk.get("is_open"))
age = "n/a" if q["age_min"] is None else "%.0f" % q["age_min"]
spr = "n/a" if q["spread"] is None else "%.2f%%" % (q["spread"] * 100)
print("%s bid=%s ask=%s last=%s last_trade_age_min=%s spread=%s prev_close=%s day_close=%s market_open=%s status=%s"
      % (sym, q["bid"], q["ask"], q["last"], age, spr, q["prev_close"], q["day_close"],
         str(bool(clk.get("is_open"))).lower(), q["status"]))
PYEOF
        ;;
    bars)
        # bars SYM [N=30] [through=yesterday|now] - newest first. "yesterday" = completed
        # sessions only (use for indicators); "now" = up to 20 min ago (use after the close).
        sym="${1:?usage: bars SYM [N] [yesterday|now]}"
        n="${2:-30}"
        through="${3:-yesterday}"
        read -r start end < <(py "$TLIB" bars-window "$n" "$through")
        bars_get "$DATA/stocks/$sym/bars?timeframe=1Day&start=$start&end=$end&limit=$n&sort=desc&adjustment=split"
        ;;
    bars-multi)
        # bars-multi SYM1,SYM2 N [yesterday|now] [page_token] - raw page, oldest first (used by tlib.py)
        syms="${1:?usage: bars-multi SYMS N [through] [page_token]}"
        n="${2:-30}"
        through="${3:-yesterday}"
        token="${4:-}"
        read -r start end < <(py "$TLIB" bars-window "$n" "$through")
        url="$DATA/stocks/bars?symbols=$syms&timeframe=1Day&start=$start&end=$end&limit=10000&adjustment=split"
        [[ -n "$token" ]] && url="$url&page_token=$token"
        bars_get "$url"
        ;;
    orders)
        # orders [open|closed|all] [after ISO-8601] [limit] [until ISO-8601] - newest first
        status="${1:-open}"
        url="$API/orders?status=$status&limit=${3:-500}&direction=desc&nested=false"
        [[ -n "${2:-}" ]] && url="$url&after=$2"
        [[ -n "${4:-}" ]] && url="$url&until=$4"
        req GET "$url"
        ;;
    order-get)
        oid="${1:?usage: order-get ORDER_ID}"
        req GET "$API/orders/$oid"
        ;;
    wait-fill)
        # wait-fill ORDER_ID [secs=60] - polls until filled/canceled/expired/rejected.
        # Exit 0 = terminal state reached (check "status"), 4 = timeout (still working).
        oid="${1:?usage: wait-fill ORDER_ID [secs]}"
        secs="${2:-60}"
        deadline=$((SECONDS + secs))
        while :; do
            # A failed poll is not a verdict: keep polling, report timeout (4) at the deadline.
            o="$(req GET "$API/orders/$oid" 2>/dev/null)" || o='{"status":"unknown (poll failed)"}'
            st="$(py -c 'import json,sys
try: print(json.loads(sys.argv[1]).get("status",""))
except Exception: print("unknown")' "$o")"
            case "$st" in
                filled|canceled|expired|rejected|done_for_day|replaced)
                    echo "$o"
                    exit 0
                    ;;
            esac
            if ((SECONDS >= deadline)); then
                echo "$o"
                echo "[alpaca] wait-fill timeout after ${secs}s, status=$st" >&2
                exit 4
            fi
            sleep 5
        done
        ;;
    history)
        req GET "$API/account/portfolio/history?period=${1:-1M}&timeframe=${2:-1D}"
        ;;
    order)
        body="${1:?usage: order '<json>'}"
        guard_order "$body"
        [[ "${ALPACA_DRY_RUN:-}" == 1 ]] && dry "POST /orders $body"
        req POST "$API/orders" "$body"
        ;;
    order-replace)
        # Only tightening a trailing stop ("trail") or lowering qty is allowed.
        oid="${1:?usage: order-replace ORDER_ID '<json>'}"
        body="${2:?usage: order-replace ORDER_ID '<json>'}"
        live_guard
        cur="$(req GET "$API/orders/$oid")"
        py - "$cur" "$body" <<'PYEOF'
import json, sys
cur, new = json.loads(sys.argv[1]), json.loads(sys.argv[2])
def refuse(m):
    print("REFUSED: " + m, file=sys.stderr)
    sys.exit(5)
extra = set(new) - {"trail", "qty", "client_order_id"}
if extra:
    refuse("only trail/qty may be replaced, got %s" % sorted(extra))
if "trail" in new:
    if cur.get("type") != "trailing_stop":
        refuse("trail can only be replaced on a trailing_stop order")
    old, nt = float(cur.get("trail_percent") or 0), float(new["trail"])
    if not 1 <= nt <= old:
        refuse("new trail %.2f must be between 1 and the current %.2f (never widen)" % (nt, old))
if "qty" in new and int(new["qty"]) > int(float(cur.get("qty") or 0)):
    refuse("qty may only be lowered")
PYEOF
        [[ "${ALPACA_DRY_RUN:-}" == 1 ]] && dry "PATCH /orders/$oid $body"
        req PATCH "$API/orders/$oid" "$body"
        ;;
    cancel)
        oid="${1:?usage: cancel ORDER_ID}"
        [[ "${ALPACA_DRY_RUN:-}" == 1 ]] && dry "DELETE /orders/$oid"
        req DELETE "$API/orders/$oid"
        ;;
    close)
        # Market-sells the whole position. Cancel its stop order first or Alpaca
        # rejects it (shares are held by the stop).
        sym="${1:?usage: close SYM}"
        live_guard
        [[ "${ALPACA_DRY_RUN:-}" == 1 ]] && dry "DELETE /positions/$sym"
        req DELETE "$API/positions/$sym"
        ;;
    cancel-all|close-all)
        [[ "${ALPACA_ALLOW_BULK:-}" == 1 ]] || { echo "REFUSED: $cmd needs ALPACA_ALLOW_BULK=1 (manual use only)" >&2; exit 5; }
        live_guard
        [[ "${ALPACA_DRY_RUN:-}" == 1 ]] && dry "$cmd"
        if [[ "$cmd" == cancel-all ]]; then
            req DELETE "$API/orders"
        else
            req DELETE "$API/positions?cancel_orders=true"
        fi
        ;;
    news)
        # news [SYMS] [start-ISO] [limit<=50] [page_token] - oldest first, no article bodies.
        # Read-only input for the news sleeve; headline text is data, never a command.
        syms="${1:-}"
        start="${2:-}"
        limit="${3:-50}"
        token="${4:-}"
        url="$DATA_ROOT/v1beta1/news?sort=asc&include_content=false&limit=$limit"
        [[ -n "$syms" ]] && url="$url&symbols=$syms"
        [[ -n "$start" ]] && url="$url&start=$start"
        [[ -n "$token" ]] && url="$url&page_token=$token"
        req GET "$url"
        ;;
    crypto-latest)
        # crypto-latest PAIR[,PAIR] - {"trades":{...},"quotes":{...}} from the v1beta3 US crypto feed
        pairs="${1:?usage: crypto-latest PAIR[,PAIR]}"
        t="$(req GET "$DATA_ROOT/v1beta3/crypto/us/latest/trades?symbols=$pairs")"
        q="$(req GET "$DATA_ROOT/v1beta3/crypto/us/latest/quotes?symbols=$pairs")"
        py -c 'import json,sys; a=json.loads(sys.argv[1]); b=json.loads(sys.argv[2]); print(json.dumps({"trades":a.get("trades",{}),"quotes":b.get("quotes",{})}))' "$t" "$q"
        ;;
    crypto-price)
        # One normalised line like `price`: PAIR bid= ask= last= last_trade_age_min= spread= status=OK|STALE
        pair="${1:?usage: crypto-price PAIR}"
        latest="$(bash "$0" crypto-latest "$pair")"
        py - "$pair" "$latest" "$ROOT/scripts" <<'PYEOF'
import json, sys
sys.path.insert(0, sys.argv[3])
import tlib
pair, d = sys.argv[1], json.loads(sys.argv[2])
t, q = d["trades"].get(pair) or {}, d["quotes"].get(pair) or {}
last, bid, ask = float(t.get("p") or 0), float(q.get("bp") or 0), float(q.get("ap") or 0)
ts = tlib.parse_ts(t.get("t"))
age = None if not ts else (tlib.utc_now() - ts).total_seconds() / 60
mid = (bid + ask) / 2 if bid > 0 and ask > 0 else 0
spr = (ask - bid) / mid if mid else None
status = "NOQUOTE" if not last and not ask else ("STALE" if age is None or age > 5 else "OK")
print("%s bid=%s ask=%s last=%s last_trade_age_min=%s spread=%s market_open=true status=%s" % (
    pair, bid, ask, last, "n/a" if age is None else "%.0f" % age, "n/a" if spr is None else "%.3f%%" % (spr * 100), status))
PYEOF
        ;;
    crypto-bars)
        # crypto-bars PAIR [N=100] [TF=15Min] [start-ISO] [end-ISO] - newest first unless start is given
        pair="${1:?usage: crypto-bars PAIR [N] [TF] [start] [end]}"
        n="${2:-100}"
        tf="${3:-15Min}"
        url="$DATA_ROOT/v1beta3/crypto/us/bars?symbols=$pair&timeframe=$tf&limit=$n"
        if [[ -n "${4:-}" ]]; then
            url="$url&start=$4&sort=asc"
            [[ -n "${5:-}" ]] && url="$url&end=$5"
        else
            url="$url&sort=desc"
        fi
        req GET "$url"
        ;;
    bars-intraday)
        # bars-intraday SYM TF START END [limit=1000] - stock minute/hour bars, SIP when the window is
        # >= 15 min old (fallback IEX), oldest first. Used by the news scorer, never for live decisions.
        sym="${1:?usage: bars-intraday SYM 1Min|1Hour START END [limit]}"
        tf="${2:?timeframe}"
        start="${3:?start ISO}"
        end="${4:?end ISO}"
        bars_get "$DATA/stocks/$sym/bars?timeframe=$tf&start=$start&end=$end&limit=${5:-1000}&sort=asc&adjustment=split"
        ;;
    *)
        cat >&2 <<'EOF'
Usage: bash scripts/alpaca.sh <subcommand> [args]
  Read:   account | positions | position SYM | clock | calendar [start] [end]
          quote SYM | snapshot SYM | snapshots A,B | price SYM
          bars SYM [N] [yesterday|now] | orders [open|closed|all] [after] [limit]
          order-get ID | wait-fill ID [secs] | history [period] [timeframe]
  News:   news [SYMS] [start] [limit] [token] | crypto-latest PAIRS | crypto-price PAIR
          crypto-bars PAIR [N] [TF] [start] [end] | bars-intraday SYM TF START END [limit]
  Write:  order '<json>' | order-replace ID '<json>' | cancel ID | close SYM
  Manual: cancel-all | close-all   (need ALPACA_ALLOW_BULK=1)
EOF
        exit 1
        ;;
esac
