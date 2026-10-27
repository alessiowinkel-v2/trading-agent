#!/usr/bin/env bash
# End-to-end self-test of every script against the configured PAPER account.
# Run locally with a .env before (re)creating the cloud routines:
#   bash scripts/selftest.sh            read-only checks + guard refusals
#   bash scripts/selftest.sh --orders   also place and cancel one far-off paper order
#   bash scripts/selftest.sh --notify   also send a test message to the webhook
# Never run with --orders against a live endpoint (it refuses).

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=scripts/env.sh
source "$ROOT/scripts/env.sh"
PY="$(command -v python3 || command -v python)"
py() { "$PY" "$@" | tr -d '\r'; }
A="bash scripts/alpaca.sh"
pass=0
fail=0
ok() { echo "PASS  $1"; pass=$((pass + 1)); }
ko() { echo "FAIL  $1"; fail=$((fail + 1)); }
expect_refused() {  # expect_refused <label> <json>
    local err
    err="$($A order "$2" 2>&1 >/dev/null)"
    if [[ $? -ne 0 && "$err" == *REFUSED* ]]; then ok "guard refuses: $1"; else ko "guard should refuse: $1 ($err)"; fi
}
want_orders=0
want_notify=0
for a in "$@"; do
    [[ "$a" == --orders ]] && want_orders=1
    [[ "$a" == --notify ]] && want_notify=1
done

eval "$(py scripts/tlib.py now)"
CORE="$(py -c 'import sys; sys.path.insert(0,"scripts"); import tlib; print(tlib.params()["core_symbol"])')"
echo "selftest $NOW_ET ET  endpoint=${ALPACA_ENDPOINT:-unset}  core=$CORE"

# --- read endpoints ---------------------------------------------------------------
for c in account positions clock "orders open" "calendar" "history 1M 1D" "price SPY" "price $CORE"; do
    if out="$($A $c 2>&1)"; then ok "alpaca.sh $c"; else ko "alpaca.sh $c: ${out:0:200}"; fi
done
acct="$($A account)"
cash="$(py -c 'import json,sys; print(json.loads(sys.argv[1])["cash"])' "$acct")"
echo "      account $(py -c 'import json,sys; a=json.loads(sys.argv[1]); print(a["account_number"], "equity", a["equity"], "cash", a["cash"], "buying_power", a["buying_power"])' "$acct")"

# --- bars: SIP history depth and volume ------------------------------------------------
sipv="$($A bars SPY 250 2>/tmp/st_err | py -c 'import json,sys; b=json.load(sys.stdin)["bars"]; print(len(b), b[0]["v"])')"
if grep -q FEED_USED=iex /tmp/st_err; then ko "bars SPY 250 fell back to IEX (SIP history refused) - liquidity gate G2 will be skipped"; fi
n="${sipv% *}"
[[ "${n:-0}" -ge 250 ]] && ok "bars SPY 250 returned $n bars (latest volume ${sipv#* })" || ko "bars SPY 250 returned ${n:-0} bars"

# --- deterministic tools ---------------------------------------------------------------
for c in "screen.py sectors" "screen.py watchlist --top 5" "screen.py candidate XLK" "ks.py"; do
    if out="$(py scripts/$c 2>&1)"; then ok "$c"; echo "$out" | head -n 6 | sed 's/^/      /'; else ko "$c: ${out:0:300}"; fi
done
for r in pre-market market-open midday eod weekly; do
    out="$(bash scripts/preflight.sh "$r" 2>&1)"
    code="$(grep -E '^PREFLIGHT_EXIT=' <<<"$out" | cut -d= -f2)"
    [[ "$code" =~ ^(0|20|30|31)$ ]] && ok "preflight $r -> $code" || ko "preflight $r -> ${code:-?}: $(tail -n 3 <<<"$out")"
done
out="$(PREFLIGHT_FORCE_EXIT=30 bash scripts/preflight.sh eod 2>&1 | tail -n 1)"
[[ "$out" == "PREFLIGHT_EXIT=30" ]] && ok "preflight forced exit path" || ko "preflight forced exit: $out"
[[ -n "$(bash scripts/memtail.sh memory/LESSONS.md 1)" ]] && ok "memtail.sh" || ko "memtail.sh"

# --- order guards (refused before anything is sent) -------------------------------------
D="$(py scripts/tlib.py et-date-offset 0)"
expect_refused "missing client_order_id" '{"symbol":"'"$CORE"'","qty":"1","side":"buy","type":"limit","limit_price":"1.00","time_in_force":"day"}'
expect_refused "fractional qty" '{"symbol":"'"$CORE"'","qty":"0.5","side":"buy","type":"limit","limit_price":"1.00","time_in_force":"day","client_order_id":"test-'"$D"'-frac"}'
expect_refused "market buy" '{"symbol":"'"$CORE"'","qty":"1","side":"buy","type":"market","time_in_force":"day","client_order_id":"test-'"$D"'-mkt"}'
expect_refused "notional above cash" '{"symbol":"'"$CORE"'","qty":"25","side":"buy","type":"limit","limit_price":"'"$(py -c "print(round(float('$cash')/10+1,2))")"'","time_in_force":"day","client_order_id":"test-'"$D"'-big"}'
expect_refused "short sale" '{"symbol":"ZZZZ","qty":"1","side":"sell","type":"limit","limit_price":"1.00","time_in_force":"day","client_order_id":"test-'"$D"'-short"}'
expect_refused "option symbol" '{"symbol":"SPY261218C00700000","qty":"1","side":"buy","type":"limit","limit_price":"1.00","time_in_force":"day","client_order_id":"test-'"$D"'-opt"}'
err="$($A close-all 2>&1 >/dev/null)"; [[ "$err" == *REFUSED* ]] && ok "close-all needs ALPACA_ALLOW_BULK" || ko "close-all not guarded"

# --- real paper order round trip (opt-in) -------------------------------------------------
if [[ "$want_orders" == 1 ]]; then
    if [[ "${ALPACA_ENDPOINT:-}" != *paper-api* ]]; then
        ko "--orders refused: endpoint is not paper"
    else
        px="$($A price "$CORE" | sed -E 's/.* last=([0-9.]+).*/\1/')"
        lim="$(py -c "print('%.2f' % (float('$px')*0.5))")"
        coid="test-$D-$(date +%H%M%S)"
        body='{"symbol":"'"$CORE"'","qty":"1","side":"buy","type":"limit","limit_price":"'"$lim"'","time_in_force":"day","client_order_id":"'"$coid"'"}'
        if o="$($A order "$body")"; then
            oid="$(py -c 'import json,sys; print(json.loads(sys.argv[1])["id"])' "$o")"
            ok "paper order accepted ($oid, buy 1 $CORE @ $lim)"
            dup="$($A order "$body" 2>&1)"; [[ $? -ne 0 ]] && ok "duplicate client_order_id rejected by Alpaca" || ko "duplicate client_order_id accepted: ${dup:0:200}"
            $A cancel "$oid" >/dev/null 2>&1
            sleep 2
            st="$($A order-get "$oid" | py -c 'import json,sys; print(json.load(sys.stdin)["status"])')"
            [[ "$st" == canceled || "$st" == pending_cancel ]] && ok "cancel -> $st" || ko "cancel -> $st"
        else
            ko "paper order rejected: ${o:0:300}"
        fi
    fi
fi

# --- notifications and research ---------------------------------------------------------------
if [[ "$want_notify" == 1 ]]; then
    bash scripts/notify.sh "selftest $NOW_ET ET - if you can read this, alerts work" >/dev/null 2>&1 && ok "notify.sh delivered" || ko "notify.sh delivery failed"
    NOTIFY_WEBHOOK_URL="https://discord.com/api/webhooks/0/invalid" bash scripts/notify.sh "selftest bad url" >/dev/null 2>&1
    [[ $? -eq 2 ]] && ok "notify.sh exits 2 on a bad webhook" || ko "notify.sh did not report the bad webhook"
    git checkout -- memory/notifications 2>/dev/null || true
fi
if out="$(bash scripts/perplexity.sh -r week --text "What was the S&P 500's most recent closing level? One sentence with the date." 2>&1)"; then
    ok "perplexity.sh (-r week --text)"; echo "      ${out:0:160}"
else
    ko "perplexity.sh: ${out:0:200} - check the API/endpoint (Sonar is migrating to the Agent API)"
fi

echo
echo "selftest: $pass passed, $fail failed"
((fail == 0))
