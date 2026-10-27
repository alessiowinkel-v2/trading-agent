#!/usr/bin/env bash
# Offline end-to-end test: runs the scripts against tests/mock_alpaca.py in a
# throwaway copy of the repo (your working tree and remote are never touched).
# Usage: bash tests/offline.sh

set -uo pipefail

# This test must never reach a real endpoint or webhook: scripts/env.sh lets an exported
# variable win over .env, so drop anything the shell inherited before pointing at the mock.
unset ALPACA_API_KEY ALPACA_SECRET_KEY ALPACA_ENDPOINT ALPACA_DATA_ENDPOINT ALPACA_DATA_FEED \
      NOTIFY_WEBHOOK_URL NOTIFY_MENTION PERPLEXITY_API_KEY PERPLEXITY_AUTH ALPACA_AUTH \
      ANTHROPIC_API_KEY LIVE_TRADING_CONFIRMED ALPACA_DRY_RUN

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
check "Phase-1 commit subjects don't count as deployed routines (no false alert)" has "$out" "MISSING_COMMITS=none"
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
check "screen prints SCREEN_OK, never CANDIDATE" bash -c '! grep -q "^CANDIDATE:" <<<"$1"' _ "$out"
out="$(py scripts/screen.py candidate QLD 2>&1)"
check "screen fails G1 for an off-watchlist ticker" has "$out" "NOT A CANDIDATE: fails G1"

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
    printf '\n## %s - Pre-market Research (offline test)\nSCREEN_OK: %s ref=%s stop_pct=7.0 sector=XLP\n' "$DATE" "$SYM" "$ref" >> memory/RESEARCH-LOG.md
    out="$(py scripts/ks.py --check "$SYM" 2>&1)"
    check "a pasted SCREEN_OK line authorises nothing (G6/G7 not done)" has "$out" "PLAN FAIL"
    printf 'CANDIDATE: %s ref=%s stop_pct=7.0 sector=XLP g6=FAIL g7=PASS\n' "$SYM" "$ref" >> memory/RESEARCH-LOG.md
    out="$(py scripts/ks.py --check "$SYM" 2>&1)"
    check "a CANDIDATE line with g6=FAIL authorises nothing" has "$out" "PLAN FAIL"
    printf 'CANDIDATE: %s ref=%s stop_pct=7.0 sector=XLP g6=PASS g7=PASS\nCANDIDATE: QLD ref=100 stop_pct=7.0 sector=XLK g6=PASS g7=PASS\n' "$SYM" "$ref" >> memory/RESEARCH-LOG.md
    out="$(py scripts/ks.py --check QLD 2>&1)"
    check "off-watchlist QLD (2x leveraged) fails G1 even with a CANDIDATE line" has "$out" "G1 FAIL"
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
    lim="$(py -c "print('%.2f' % ($ref*1.01))")"
    $A order '{"symbol":"'"$SYM"'","qty":"1","side":"buy","type":"limit","limit_price":"'"$lim"'","time_in_force":"day","client_order_id":"sat-'"$DATE"'-'"$SYM"'-extra"}' >/dev/null 2>&1
    out="$(py scripts/ks.py 2>&1)"
    check "partially covered position: ORPHAN asks only for the uncovered share" has "$out" "ORPHAN $SYM: 1 sh without a stop"
    check "...and its command uses qty 1" has "$(grep "ORPHAN $SYM" <<<"$out")" '"qty":"1"'
    check "KS-8 still reconciles after the extra fill" has "$out" "KS-8 reconcile | PASS"
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
check "maintenance prints no order commands while KS-9 fails" has "$(grep -A3 '^MAINTENANCE' <<<"$out")" "BLOCKED - no orders"
out="$(NOTIFY_WEBHOOK_URL=http://127.0.0.1:$PORT/webhook/fail py scripts/ks.py --write-state 2>&1)"
check "undelivered KS alert is reported as FAILED" has "$out" "ALERT FAILED"
out="$(py scripts/ks.py --write-state 2>&1)"
check "...and is retried (and delivered) on the next run" has "$out" "ALERT sent for newly failing: .*KS-9"
sed -i "s/^- account_number: .*/- account_number: PA0TEST/" memory/PROJECT-CONTEXT.md
sed -i "s/^- start_date: .*/- start_date: UNSET/" memory/PROJECT-CONTEXT.md
check "UNSET start_date fails KS-9" has "$(py scripts/ks.py 2>&1)" "start_date is UNSET"
sed -i "s/^- start_date: .*/- start_date: $DATE/" memory/PROJECT-CONTEXT.md

echo "== latches"
cp memory/STATE.json /tmp/state.bak.$$
py -c "
import json, sys; sys.path.insert(0, 'scripts'); import tlib
s = json.load(open('memory/STATE.json'))
d = tlib.et_today().isoformat()
cfg = tlib.account_config()
s['latch'] = {'KS-1': {'date': d, 'start_date': cfg['start_date'], 'start_equity': float(cfg['start_equity'])},
              'KS-3': {'date': d, 'start_date': cfg['start_date'], 'start_equity': float(cfg['start_equity'])}}
json.dump(s, open('memory/STATE.json', 'w'))"
out="$(py scripts/ks.py 2>&1)"
check "KS-1 stays FAILED (latched) after equity recovers" has "$out" "KS-1 daily DD | FAIL"
check "KS-3 stays FAILED (latched)" has "$out" "KS-3 total DD | FAIL"
check "latched KS-1/KS-3 block buys" has "$out" "BUYS_ALLOWED=no"
check "KS-3 drives the core target to 30%" has "$out" "target 30.0% (KS-3 halt)"
check "...but never sells core shares bought today (no day trade)" has "$out" "CORE_ACTION=DONE_TODAY"
sed -i "s/^- start_equity: .*/- start_equity: 2001/" memory/PROJECT-CONTEXT.md
out="$(py scripts/ks.py 2>&1)"
check "a new start_equity (manual reset) clears the KS-3 latch" has "$out" "KS-3 total DD | PASS"
sed -i "s/^- start_equity: .*/- start_equity: 2000/" memory/PROJECT-CONTEXT.md
cp /tmp/state.bak.$$ memory/STATE.json

echo "== misc fixes"
check "wait-fill on a failing poll times out with exit 4 (not 1)" bash -c 'bash scripts/alpaca.sh wait-fill no-such-order 6 >/dev/null 2>&1; [ $? -eq 4 ]'
check "parse_ts handles 5-digit fractions" py -c "import sys; sys.path.insert(0,'scripts'); import tlib; tlib.parse_ts('2026-10-27T13:23:45.12345Z')"
check "preflight computes EARNINGS_OK_FROM from the calendar" has "$(bash scripts/preflight.sh pre-market 2>&1)" "EARNINGS_OK_FROM=20"

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
before="$(wc -l < "$W/webhook.log")"
out="$(PREFLIGHT_NO_ALERT=1 bash scripts/preflight.sh eod 2>&1)"
check "PREFLIGHT_NO_ALERT (local only) suppresses the alert" has "$out" "ALERT (suppressed, local test)"
check "...and nothing reaches the webhook" test "$(wc -l < "$W/webhook.log")" -eq "$before"
check "watchdog grid shows OK for market-open" has "$(bash scripts/watchdog.sh grid "$MONDAY")" "| $DATE | OK | OK | MISSING"
check "memtail returns the latest dated entry" has "$(bash scripts/memtail.sh memory/LESSONS.md 1)" "Phase 1b reset"
check "webhook received messages" test -s "$W/webhook.log"

echo "== news sleeve: scanner plumbing"
rm -rf memory/news
out="$($A news NVDA,BTCUSD,SPY 2>&1)"
check "alpaca.sh news returns articles" has "$out" '"headline"'
out="$($A crypto-price BTC/USD 2>&1)"
check "alpaca.sh crypto-price prints a status line" has "$out" "BTC/USD bid=.*status=OK"
out="$($A crypto-bars BTC/USD 3 15Min 2>&1)"
check "alpaca.sh crypto-bars returns 15Min bars" has "$out" '"BTC/USD"'
out="$($A bars-intraday SPY 1Min "$(py -c 'import sys; sys.path.insert(0,"scripts"); import tlib,datetime as d; print(tlib.iso(tlib.utc_now()-d.timedelta(minutes=30)))')" "$(py -c 'import sys; sys.path.insert(0,"scripts"); import tlib; print(tlib.iso(tlib.utc_now()))')" 2>&1)"
check "alpaca.sh bars-intraday returns minute bars" test "$(py -c 'import json,sys; print(len(json.loads(sys.argv[1])["bars"]))' "$out")" -ge 20
check "news universe parses 74 symbols" has "$(py scripts/newslib.py universe)" "74 symbols"
out="$(py scripts/newsscan.py --lookback-hours 3 --no-classify 2>&1)"; echo "   $out"
check "first scan keeps 3 universe headlines (drops off-universe + duplicate id)" has "$out" "NEWSSCAN ok new=3"
raw="memory/news/raw/$(py -c 'import sys; sys.path.insert(0,"scripts"); import tlib; print(tlib.et_today().strftime("%Y-%m"))').jsonl"
check "raw jsonl written" test "$(wc -l < "$raw")" -eq 3
check "NVDA headline keeps NVDA as primary ticker (named in headline)" has "$(grep 62600001 "$raw")" '"ticker":"NVDA"'
check "5-symbol Fed story maps to SPY" has "$(grep 62600004 "$raw")" '"ticker":"SPY"'
check "crypto row carries a crypto price snapshot" has "$(grep 62600002 "$raw")" '"feed":"crypto-us"'
check "stock row carries a price snapshot" has "$(grep 62600001 "$raw")" '"feed":"iex"'
out="$(py scripts/newsscan.py --no-classify 2>&1)"
check "second scan adds nothing (cursor + dedup)" has "$out" "NEWSSCAN ok new=0"
check "state.json has a cursor and last_ok" bash -c 'grep -q cursor_updated_at memory/news/state.json && grep -q last_ok_utc memory/news/state.json'
check "gitpush accepts a newsscan subject" bash -c 'bash scripts/gitpush.sh "newsscan 2026-10-27 21:00Z: OK - 3 new headlines" >/dev/null 2>&1'
check "gitpush still rejects a bad subject" bash -c '! bash scripts/gitpush.sh "scanner 2026-10-27: OK - x" >/dev/null 2>&1'
py scripts/newslib.py mark-commit
out="$(bash scripts/newsscan.sh --no-classify 2>&1)"
check "newsscan.sh: nothing new and heartbeat not due -> no commit" has "$out" "no commit"
py -c "
import json; s=json.load(open('memory/news/state.json')); s['last_commit_utc']='2026-01-01T00:00:00Z'; json.dump(s, open('memory/news/state.json','w'))"
out="$(bash scripts/newsscan.sh --no-classify 2>&1)"
check "newsscan.sh: heartbeat commit when the last commit is old" has "$out" "0 new (heartbeat)"
out="$(ALPACA_DATA_ENDPOINT=http://127.0.0.1:1/data/v2 py scripts/newsscan.py 2>&1)"
check "scanner aborts loudly when the API is unreachable" has "$out" "NEWSSCAN ABORTED"
check "...and records the error in state.json" has "$(cat memory/news/state.json)" '"last_error": "AlpacaError'
check "watchdog sees a fresh scanner as healthy" bash -c '! bash scripts/watchdog.sh nightly 2>&1 | grep -q "newsscan=STALE"'
py -c "
import json; s=json.load(open('memory/news/state.json')); s['last_ok_utc']='2026-01-01T00:00:00Z'; json.dump(s, open('memory/news/state.json','w'))"
check "watchdog flags a stale scanner" bash -c 'bash scripts/watchdog.sh nightly 2>&1 | grep -q "newsscan=STALE"'

echo "== news sleeve: classifier (mock)"
rm -rf memory/news
out="$(py scripts/newsclassify.py 2>&1)"
check "classifier with nothing pending is a no-op" has "$out" "NEWSCLASSIFY ok classified=0"
out="$(printf '[{"id":1,"ticker":"KO","tickers":[],"asset":"stock","headline":"x","summary":"","ts_news":"t"}]' | CLAUDE_DRY=1 ANTHROPIC_API_KEY=dry bash scripts/claude.sh json scripts/prompts/classify-schema.json --system scripts/prompts/classify-v1.md 2>&1)"
check "claude.sh dry run builds a structured-output request" bash -c 'grep -q "\"output_config\"" <<<"$1" && grep -q "\"type\": \"json_schema\"" <<<"$1" && grep -q "\"fallbacks\": \"default\"" <<<"$1"' _ "$out"
check "...with no sampling parameters" bash -c '! grep -q temperature <<<"$1"' _ "$out"
out="$(py scripts/newsscan.py --lookback-hours 3 2>&1)"   # ANTHROPIC_API_KEY was unset above
check "without an API key the classifier skips and the scan still succeeds" has "$out" "NEWSCLASSIFY skipped.*reason=no_api_key"
check "...and the scan line reports 0 signals" has "$out" "NEWSSCAN ok new=3.*signals=0"
check "...pending headlines are recorded in state" has "$(cat memory/news/state.json)" "ANTHROPIC_API_KEY missing - 3 headlines pending"
before="$(wc -l < "$W/webhook.log")"
out="$(CLAUDE_MOCK=1 py scripts/newsclassify.py 2>&1)"; echo "   $out"
check "mock classifier classifies the 3 pending rows" has "$out" "NEWSCLASSIFY ok classified=3 signals=3"
sigf="memory/news/signals/$(py -c 'import sys; sys.path.insert(0,"scripts"); import tlib; print(tlib.et_today().strftime("%Y-%m"))').jsonl"
check "signals file has 3 rows" test "$(wc -l < "$sigf")" -eq 3
check "NVDA guidance -> bull guidance 0.85" has "$(grep 62600001 "$sigf")" '"direction":"bull".*"status":"open"'
check "classifier model + prompt version recorded" has "$(grep 62600001 "$sigf")" '"prompt_version":"classify-v1"'
check "Fed story stays on SPY" has "$(grep 62600004 "$sigf")" '"ticker":"SPY"'
check "token usage and cost accounted" has "$(cat memory/news/state.json)" '"cost_usd"'
check "one strong new signal alerted (NVDA 0.85 m2), weaker ones not" test "$(( $(wc -l < "$W/webhook.log") - before ))" -eq 1
out="$(CLAUDE_MOCK=1 py scripts/newsclassify.py 2>&1)"
check "second classify run finds nothing pending" has "$out" "classified=0 signals=0"
# near-duplicate: same ticker, almost the same words, within 24 h -> no API call
NOWISO="$(py -c 'import sys; sys.path.insert(0,"scripts"); import tlib; print(tlib.iso(tlib.utc_now()))')"
printf '{"id":62600099,"ts_news":"%s","ts_updated":"%s","ts_ingest":"%s","source":"benzinga","url":"u","headline":"Nvidia Raises Its Full-Year Guidance On Strong Data Center Demand","summary":"","symbols":["NVDA"],"tickers":[{"ticker":"NVDA","asset":"stock"}],"ticker":"NVDA","asset":"stock","benchmark":"SPY","px":null,"status":"raw"}\n' "$NOWISO" "$NOWISO" "$NOWISO" >> "$raw"
out="$(CLAUDE_MOCK=1 py scripts/newsclassify.py 2>&1)"
check "near-duplicate headline is tagged without an API call" has "$out" "dup=1 unscorable=0 calls=0"
check "...as duplicate_of the original id" has "$(grep 62600099 "$sigf")" '"novelty":"duplicate_of:62600001"'
# coverage failure: the model omits an item -> unscorable, never a guess
printf '{"id":62600098,"ts_news":"%s","ts_updated":"%s","ts_ingest":"%s","source":"benzinga","url":"u","headline":"BADJSON Coca-Cola Announces Recall Of Bottled Water","summary":"","symbols":["KO"],"tickers":[{"ticker":"KO","asset":"stock"}],"ticker":"KO","asset":"stock","benchmark":"SPY","px":null,"status":"raw"}\n' "$NOWISO" "$NOWISO" "$NOWISO" >> "$raw"
out="$(CLAUDE_MOCK=1 py scripts/newsclassify.py 2>&1)"
check "an item missing from the model response becomes unscorable" has "$out" "unscorable=1"
check "...with the reason recorded" has "$(grep 62600098 "$sigf")" '"status":"unscorable"'
# alert budget + held-symbol bear rule
before="$(wc -l < "$W/webhook.log")"
printf '{"id":62600097,"ts_news":"%s","ts_updated":"%s","ts_ingest":"%s","source":"benzinga","url":"u","headline":"Regulators Open Probe Into Walmart Pricing Practices","summary":"","symbols":["WMT"],"tickers":[{"ticker":"WMT","asset":"stock"}],"ticker":"WMT","asset":"stock","benchmark":"SPY","px":null,"status":"raw"}\n{"id":62600096,"ts_news":"%s","ts_updated":"%s","ts_ingest":"%s","source":"benzinga","url":"u","headline":"Microsoft To Acquire Cloud Security Startup","summary":"","symbols":["MSFT"],"tickers":[{"ticker":"MSFT","asset":"stock"}],"ticker":"MSFT","asset":"stock","benchmark":"SPY","px":null,"status":"raw"}\n' "$NOWISO" "$NOWISO" "$NOWISO" "$NOWISO" "$NOWISO" "$NOWISO" >> "$raw"
py -c "
import json; s=json.load(open('memory/STATE.json')) if __import__('os').path.exists('memory/STATE.json') else {}
s['positions']={'WMT':1.0}; json.dump(s, open('memory/STATE.json','w'))"
out="$(CLAUDE_MOCK=1 ALERT_BUDGET=1 py scripts/newsclassify.py 2>&1)"
check "held-symbol bear alerts even when the daily budget is spent" test "$(( $(wc -l < "$W/webhook.log") - before ))" -eq 1
check "...and the MSFT deal (0.9 m3) was held back by the budget" has "$out" "alerts=1"
check "the held-position alert is flagged" has "$(tail -n 1 "$W/webhook.log")" "HELD POSITION"
out="$(bash scripts/newsfeed.sh --since 24 2>&1)"; echo "$out" | head -n 4
check "newsfeed lists open signals" has "$out" "| NVDA | bull | 2 | 0.85 | guidance |"
check "newsfeed filters by symbol" has "$(bash scripts/newsfeed.sh --since 24 --symbols SPY)" "1 signals for SPY"

echo "== news sleeve: scorer"
# slot rules are pure functions of the calendar: Friday 15:00 ET -> Monday 10:12; Tuesday 11:00 -> 13:07 same day
out="$(py scripts/newsscore.py --slot-of 2026-11-06T20:00:00Z SPY)"      # Fri 15:00 EST
check "Friday afternoon headline -> Monday 10:12 ET routine slot" has "$out" "routine_slot=2026-11-09T15:12:00Z"
check "...crypto 15m slot is the next quarter hour >= +15 min" has "$out" "crypto_15m=2026-11-06T20:15:00Z"
out="$(py scripts/newsscore.py --slot-of 2026-11-10T16:00:00Z NVDA)"     # Tue 11:00 EST
check "Tuesday 11:00 ET headline -> 13:07 same day" has "$out" "routine_slot=2026-11-10T18:07:00Z"
out="$(py scripts/newsscore.py --slot-of 2026-11-10T14:30:00Z NVDA)"     # Tue 09:30 EST
check "Tuesday 09:30 ET headline -> 10:12 same day" has "$out" "routine_slot=2026-11-10T15:12:00Z"
# backdate the three mock signals 8 trading days so every horizon resolves against the flat mock prices
py - <<'PYEOF'
import json, sys, datetime as d
sys.path.insert(0, 'scripts'); import tlib, newslib
rows = newslib.recent_rows('signals', 2)
old = tlib.utc_now() - d.timedelta(days=12)
old = old.replace(hour=15, minute=0, second=0, microsecond=0)   # 10:00/11:00 ET on a weekday or earlier
while tlib.to_et(old).weekday() >= 5:
    old -= d.timedelta(days=1)
for r in rows:
    if r.get('status') == 'open':
        r['ts_news'] = tlib.iso(old)
newslib.rewrite_jsonl(newslib.month_file(tlib.et_today(), 'signals'), rows)
PYEOF
out="$(py scripts/newsscore.py 2>&1)"; echo "   $out"
check "scorer resolves the backdated signals" has "$out" "NEWSSCORE ok touched=5 changed=5 scored_total=5"
check "scorecard json + md written" bash -c 'test -f memory/news/scorecard.json && test -f memory/NEWS-SCORECARD.md'
check "gate is NOT MET with a tiny sample (and says why)" has "$out" "gate=NOT MET (only .* weeks scanned; only 5 of 150"
check "flat prices: bull net excess equals minus the stock cost" bash -c "grep 62600001 '$sigf' | py -c 'import json,sys; s=json.loads(sys.stdin.read()); sys.exit(0 if abs(s[\"outcomes\"][\"routine\"][\"d3\"][\"net_excess\"] + 0.001) < 1e-9 else 1)'"
check "flat prices: crypto bear net excess equals minus the crypto cost" bash -c "grep 62600002 '$sigf' | py -c 'import json,sys; s=json.loads(sys.stdin.read()); sys.exit(0 if abs(s[\"outcomes\"][\"routine\"][\"d3\"][\"net_excess\"] + 0.006) < 1e-9 else 1)'"
check "crypto signal also has the 15-minute lane entry" has "$(grep 62600002 "$sigf")" '"crypto-15m":{'
check "entry slot recorded at a routine time" bash -c "grep 62600001 '$sigf' | grep -qE '\"routine\":\{[^}]*\"ts\":\"[0-9T:-]*(15:12|18:07|14:12|17:07):00Z'"
out="$(py scripts/newsscore.py --explain 62600001 2>&1)"
check "--explain prints the bars used" has "$out" "routine d3: NVDA"
check "memtail reads the scorecard entry" has "$(bash scripts/memtail.sh memory/NEWS-SCORECARD.md 1)" "GATE: NOT MET"
out="$(py scripts/newsscore.py 2>&1)"
check "re-run is idempotent (nothing changes)" has "$out" "touched=0 changed=0"
rm -rf memory/news memory/NEWS-SCORECARD.md

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
printf '\n## %s — Pre-market Research (offline test 2)\nCANDIDATE: KO ref=70.00 stop_pct=7.0 sector=XLP g6=PASS g7=PASS\nCANDIDATE: PM ref=160.00 stop_pct=7.0 sector=XLP g6=PASS g7=PASS\nCANDIDATE: WMT ref=103.00 stop_pct=7.0 sector=XLP g6=PASS g7=PASS\n' "$DATE" >> memory/RESEARCH-LOG.md
out="$(py scripts/ks.py --check KO PM WMT 2>&1)"
check "three same-sector candidates in one check: only two approved" test "$(grep -c 'VERDICT BUY' <<<"$out")" -eq 2
check "...the third is refused for sector/slot room" has "$(sed -n '/CHECK WMT/,$p' <<<"$out")" "VERDICT SKIP - fails G9"

echo "== calendar failure"
kill $MOCK_PID 2>/dev/null
sleep 0.5
MOCK_CAL_FAIL=1 "$PY" tests/mock_alpaca.py "$PORT" &
MOCK_PID=$!
sleep 1.5
out="$(bash scripts/preflight.sh market-open 2>&1)"
check "calendar failure -> exit 40, never a SKIPPED trading day" has "$out" "PREFLIGHT_EXIT=40"

echo
echo "offline: $pass passed, $fail failed"
((fail == 0))
