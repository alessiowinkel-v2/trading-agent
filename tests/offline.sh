#!/usr/bin/env bash
# Offline end-to-end test: runs the scripts against tests/mock_alpaca.py in a
# throwaway copy of the repo (your working tree and remote are never touched).
# Usage: bash tests/offline.sh

set -uo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
PY="$(command -v python3 || command -v python)"
py() { "$PY" "$@" | tr -d '\r'; }
PORT="${PORT:-8765}"
W="$(mktemp -d)"
cp -r "$SRC/." "$W/"
cd "$W"
rm -f .env memory/STATE.json memory/PAUSED.flag
# The copy must never be able to push anywhere.
git remote remove origin 2>/dev/null || true
export GIT_PUSH_DISABLED=1

export MOCK_WEBHOOK_LOG="$W/webhook.log"
MOCK_OPEN=1 "$PY" tests/mock_alpaca.py "$PORT" &
MOCK_PID=$!
trap 'kill $MOCK_PID 2>/dev/null; rm -rf "$W"' EXIT
sleep 1.5

cat > .env <<EOF
ALPACA_ENDPOINT=http://127.0.0.1:$PORT/paper-api/v2
ALPACA_DATA_ENDPOINT=http://127.0.0.1:$PORT/data/v2
ALPACA_API_KEY=test
ALPACA_SECRET_KEY=test
NOTIFY_WEBHOOK_URL=http://127.0.0.1:$PORT/webhook
EOF
eval "$(py scripts/tlib.py now)"
sed -i "s/^- start_date: .*/- start_date: $DATE/; s/^- account_number: .*/- account_number: PA0TEST/" memory/PROJECT-CONTEXT.md
git config user.name >/dev/null || git config user.name test
git config user.email >/dev/null || git config user.email test@example.com

pass=0
fail=0
check() {  # check <label> <command...>: passes if the command succeeds
    local label="$1"
    shift
    if "$@" >/dev/null 2>&1; then echo "PASS  $label"; pass=$((pass + 1)); else echo "FAIL  $label"; fail=$((fail + 1)); fi
}
has() { grep -q -- "$2" <<<"$1"; }   # has <text> <pattern>
A="bash scripts/alpaca.sh"

echo "== preflight"
out="$(bash scripts/preflight.sh market-open 2>&1)"
check "preflight market-open exits 0" has "$out" "PREFLIGHT_EXIT=0"
check "preflight prints EARNINGS_OK_FROM" has "$out" "EARNINGS_OK_FROM="
out="$(MOCK_OPEN=0 bash scripts/preflight.sh eod 2>&1)"
check "preflight eod exits 0" has "$out" "PREFLIGHT_EXIT=0"

echo "== screen"
out="$(py scripts/screen.py sectors 2>&1)"; echo "$out" | head -n 4
check "sectors prints REGIME + 11 ranked rows" test "$(grep -c '^| [0-9]' <<<"$out")" -eq 11
out="$(py scripts/screen.py watchlist 2>&1)"; echo "$out" | head -n 6
check "watchlist screen ran" has "$out" "WATCHLIST SCREEN"
check "watchlist dropped >\$300 names via G1" has "$out" "pass G1 price"
SYM="$(grep -E '^\| 1 \|' <<<"$out" | awk -F'|' '{gsub(/ /,"",$3); print $3}')"
echo "   top passer: ${SYM:-none}"
out="$(py scripts/screen.py candidate NVDA 2>&1)"
check "candidate table has G8" has "$out" "| G8 |"

echo "== core buy"
out="$(py scripts/ks.py 2>&1)"
check "ks.py KS-9 PASS (account matches)" has "$out" "KS-9 account | PASS"
cmd="$(grep -o "bash scripts/alpaca.sh order '[^']*'" <<<"$(grep CORE_ACTION= <<<"$out")")"
check "core action is a BUY command" has "$cmd" '"side":"buy"'
o="$(eval "$cmd" 2>/dev/null)"
check "core order filled" has "$o" '"status": "filled"'
out="$(py scripts/ks.py 2>&1)"
check "second core action is DONE_TODAY" has "$out" "CORE_ACTION=DONE_TODAY"
check "invested >= 70% after core buy" py -c "import re,sys; m=re.search(r'invested ([0-9.]+)%', sys.argv[1]); sys.exit(0 if float(m.group(1))>=70 else 1)" "$out"

echo "== satellite entry"
if [[ -n "$SYM" ]]; then
    ref="$(grep -E '^\| 1 \|' <<<"$(py scripts/screen.py watchlist 2>/dev/null)" | awk -F'|' '{gsub(/ /,"",$5); print $5}')"
    out="$(py scripts/ks.py --check "$SYM" 2>&1)"
    check "check refuses $SYM before it is a research CANDIDATE" has "$out" "PLAN FAIL"
    printf '
## %s — Pre-market Research (offline test)
CANDIDATE: %s ref=%s stop_pct=7.0 sector=XLP
' "$DATE" "$SYM" "$ref" >> memory/RESEARCH-LOG.md
    out="$(py scripts/ks.py --check "$SYM" XLK 2>&1)"; grep -E 'PLAN |G[0-9]+ |VERDICT' <<<"$out"
    check "unplanned XLK is refused even if live gates pass" has "$(sed -n '/CHECK XLK/,$p' <<<"$out")" "VERDICT SKIP - fails PLAN"
    check "check verdict BUY for $SYM" has "$out" "VERDICT BUY"
    buy="$(grep -o "bash scripts/alpaca.sh order '[^']*'" <<<"$(grep 'VERDICT BUY' <<<"$out")")"
    o="$(eval "$buy" 2>/dev/null)"
    oid="$(py -c 'import json,sys; print(json.loads(sys.argv[1])["id"])' "$o" 2>/dev/null)"
    w="$($A wait-fill "$oid" 10 2>/dev/null)"
    check "satellite filled" has "$w" '"status": "filled"'
    fq="$(py -c 'import json,sys; print(json.loads(sys.argv[1])["filled_qty"])' "$w")"
    stop="$(grep -o "bash scripts/alpaca.sh order '[^']*'" <<<"$(grep 'THEN' <<<"$out")" | sed "s/<filled_qty>/$fq/")"
    so="$(eval "$stop" 2>/dev/null)"
    check "trailing stop accepted" has "$so" '"type": "trailing_stop"'
    stop_id="$(py -c 'import json,sys; print(json.loads(sys.argv[1])["id"])' "$so" 2>/dev/null)"
    out="$(py scripts/ks.py --check "$SYM" 2>&1)"
    check "G0 blocks a second buy of $SYM" has "$out" "G0 FAIL"
    out="$(py scripts/ks.py --write-state 2>&1)"
    check "KS-10 PASS with stop in place" has "$out" "KS-10 stops | PASS"
    check "STATE.json written" test -f memory/STATE.json
    $A cancel "$stop_id" >/dev/null 2>&1
    out="$(py scripts/ks.py 2>&1)"
    check "KS-10 FAIL after stop cancelled" has "$out" "KS-10 stops | FAIL"
    check "ORPHAN command printed" has "$out" "ORPHAN $SYM"
    orphan="$(grep -o "bash scripts/alpaca.sh order '[^']*'" <<<"$(grep "ORPHAN $SYM" <<<"$out")")"
    eval "$orphan" >/dev/null 2>&1
    out="$(py scripts/ks.py --write-state 2>&1)"
    check "KS-10 PASS after orphan stop placed" has "$out" "KS-10 stops | PASS"
    check "KS-8 reconcile PASS" has "$out" "KS-8 reconcile | PASS"
fi

echo "== guards"
D="$DATE"
r() { $A order "$1" 2>&1 >/dev/null; }
check "refuse missing client_order_id" has "$(r '{"symbol":"SPYM","qty":"1","side":"buy","type":"limit","limit_price":"80","time_in_force":"day"}')" REFUSED
check "refuse fractional qty" has "$(r '{"symbol":"SPYM","qty":"0.5","side":"buy","type":"limit","limit_price":"80","time_in_force":"day","client_order_id":"test-'$D'-a"}')" REFUSED
check "refuse market buy" has "$(r '{"symbol":"SPYM","qty":"1","side":"buy","type":"market","time_in_force":"day","client_order_id":"test-'$D'-b"}')" REFUSED
check "refuse buy beyond cash" has "$(r '{"symbol":"SPYM","qty":"20","side":"buy","type":"limit","limit_price":"80","time_in_force":"day","client_order_id":"test-'$D'-c"}')" REFUSED
check "refuse short sale" has "$(r '{"symbol":"KO","qty":"1","side":"sell","type":"limit","limit_price":"70","time_in_force":"day","client_order_id":"test-'$D'-d"}')" REFUSED
check "refuse option symbol" has "$(r '{"symbol":"SPY261218C00700000","qty":"1","side":"buy","type":"limit","limit_price":"1","time_in_force":"day","client_order_id":"test-'$D'-e"}')" REFUSED
check "refuse close-all without ALPACA_ALLOW_BULK" has "$($A close-all 2>&1)" REFUSED
o1="$($A order '{"symbol":"SPYM","qty":"1","side":"buy","type":"limit","limit_price":"1.00","time_in_force":"day","client_order_id":"test-'$D'-dup"}' 2>&1)"
o2="$($A order '{"symbol":"SPYM","qty":"1","side":"buy","type":"limit","limit_price":"1.00","time_in_force":"day","client_order_id":"test-'$D'-dup"}' 2>&1)"
check "duplicate client_order_id rejected" has "$o2" "must be unique"
# The $1.00 order above is still working (limit far below market), so $1 of cash is reserved:
# a buy priced at cash - $0.50 fits in cash but not in cash minus reservations.
lim="$(py -c "import json,sys; print('%.2f' % (float(json.loads(sys.argv[1])['cash']) - 0.5))" "$($A account)")"
check "working buy order reserves cash" has "$(r '{"symbol":"KO","qty":"1","side":"buy","type":"limit","limit_price":"'"$lim"'","time_in_force":"day","client_order_id":"test-'$D'-res"}')" "reserved"
check "refuse widening a trailing stop" has "$($A order-replace "$(py -c 'import json,sys; print([o["id"] for o in json.loads(sys.argv[1]) if o["type"]=="trailing_stop"][0])' "$($A orders open)")" '{"trail":"14"}' 2>&1)" REFUSED

echo "== pause and live guards"
echo test > memory/PAUSED.flag
out="$(bash scripts/preflight.sh market-open 2>&1)"
check "preflight exit 20 when paused" has "$out" "PREFLIGHT_EXIT=20"
check "buys refused while paused" has "$(r '{"symbol":"KO","qty":"1","side":"buy","type":"limit","limit_price":"75","time_in_force":"day","client_order_id":"test-'$D'-p"}')" "paused"
rm -f memory/PAUSED.flag
out="$(ALPACA_ENDPOINT=http://127.0.0.1:$PORT/live/v2 bash scripts/preflight.sh market-open 2>&1)"
check "preflight exit 50 on live endpoint without confirmation" has "$out" "PREFLIGHT_EXIT=50"
check "orders refused on live endpoint without confirmation" has "$(ALPACA_ENDPOINT=http://127.0.0.1:$PORT/live/v2 $A order '{}' 2>&1)" "LIVE_TRADING_CONFIRMED"
sed -i "s/^- account_number: .*/- account_number: PA9WRONG/" memory/PROJECT-CONTEXT.md
out="$(py scripts/ks.py 2>&1)"
check "KS-9 FAIL on wrong account number" has "$out" "KS-9 account | FAIL"
check "ORDERS_ALLOWED=no on KS-9" has "$out" "ORDERS_ALLOWED=no"
sed -i "s/^- account_number: .*/- account_number: PA0TEST/" memory/PROJECT-CONTEXT.md

echo "== EOD, week, notify, commits, cadence"
out="$(MOCK_OPEN=0 py scripts/ks.py --eod --write-state 2>&1)"; grep -E '^### |\*\*Portfolio' <<<"$out"
check "EOD block printed" has "$out" "EOD Snapshot"
check "week block printed" has "$(py scripts/ks.py --week 2>&1)" "WEEK STATS"
check "notify delivered (exit 0)" bash scripts/notify.sh "offline test"
NOTIFY_WEBHOOK_URL="http://127.0.0.1:$PORT/webhook/fail" bash scripts/notify.sh "x" >/dev/null 2>&1
check "notify exits 2 when the webhook fails" test $? -eq 2
check "gitpush rejects a bad subject" bash -c '! bash scripts/gitpush.sh "nonsense"'
check "gitpush commits pre-market" bash scripts/gitpush.sh "pre-market $DATE: OK - offline test"
check "gitpush commits market-open" bash scripts/gitpush.sh "market-open $DATE: OK - offline test"
git commit -q --allow-empty -m "midday 2026-01-05: OK - fake history so midday counts as deployed"
out="$(MOCK_OPEN=0 bash scripts/preflight.sh eod 2>&1)"
check "eod preflight detects the missing midday commit" has "$out" "MISSING_COMMITS=midday $DATE"
check "watchdog grid shows OK for market-open" has "$(bash scripts/watchdog.sh grid "$MONDAY")" "| $DATE | OK | OK | MISSING"
check "memtail returns the latest dated entry" has "$(bash scripts/memtail.sh memory/LESSONS.md 1)" "Phase 1b reset"
check "webhook received messages" test -s "$W/webhook.log"

echo "== SIP refused -> IEX fallback"
kill $MOCK_PID 2>/dev/null
sleep 0.5
MOCK_SIP_403=1 "$PY" tests/mock_alpaca.py "$PORT" &
MOCK_PID=$!
sleep 1.5
out="$(py scripts/screen.py watchlist --equity 2000 2>&1)"
check "watchlist falls back to IEX and skips G2" has "$out" "feed iex"

echo "== bear market -> regime risk-off, core target 30%"
kill $MOCK_PID 2>/dev/null
sleep 0.5
MOCK_BEAR=1 "$PY" tests/mock_alpaca.py "$PORT" &
MOCK_PID=$!
sleep 1.5
out="$(py scripts/ks.py 2>&1)"
check "KS-8 blocks orders when holdings vanish (mock restarted, state kept)" has "$out" "CORE_ACTION=BLOCKED (KS-8)"
rm -f memory/STATE.json                     # now simulate a fresh, empty account
out="$(py scripts/ks.py 2>&1)"; grep -E '^REGIME|^CORE' <<<"$out"
check "regime risk-off in a downtrend" has "$out" "REGIME risk-off"
check "core target drops to 30%" has "$out" "target 30.0% (risk-off)"
check "core buys only up to 30% in risk-off" has "$out" "CORE_ACTION=BUY 7 SPYM"

echo
echo "offline: $pass passed, $fail failed"
((fail == 0))
