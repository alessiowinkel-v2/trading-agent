#!/usr/bin/env bash
# First command of every routine. Prints KEY=VALUE facts the routine must use
# (never compute dates yourself) and exits with a code that decides the run:
#   0 proceed | 10 env/tool missing | 20 paused (no buys) | 30 market closed today
#   31 trading day but market closed right now | 40 Alpaca unreachable
#   50 live endpoint without LIVE_TRADING_CONFIRMED=yes | 51 live equity above MAX_LIVE_EQUITY
# It alerts the user itself (notify.sh --alert) for 10/40/50/51 and for missing
# earlier routine commits, so a confused agent cannot hide a failure.
# Usage: bash scripts/preflight.sh <pre-market|market-open|midday|eod|weekly>

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
routine="${1:-}"
case "$routine" in
    pre-market|market-open|midday|eod|weekly) ;;
    *) echo "usage: bash scripts/preflight.sh <pre-market|market-open|midday|eod|weekly>" >&2; exit 1 ;;
esac

LOCAL=0
[[ -f "$ROOT/.env" ]] && LOCAL=1
# shellcheck source=scripts/env.sh
source "$ROOT/scripts/env.sh"

PY="$(command -v python3 || command -v python || true)"
py() { "$PY" "$@" | tr -d '\r'; }   # tr: Windows Python writes CRLF
alert() { bash "$ROOT/scripts/notify.sh" --alert "$routine preflight: $*" >&2 || true; }
finish() {
    echo "PREFLIGHT_EXIT=$1"
    exit "$1"
}

echo "ROUTINE=$routine"
echo "LOCAL_RUN=$LOCAL"

# ---- tools and environment ------------------------------------------------
missing=()
[[ -n "$PY" ]] || missing+=(python3)
command -v git >/dev/null || missing+=(git)
command -v curl >/dev/null || missing+=(curl)
if [[ "${ALPACA_AUTH:-}" != "proxy" ]]; then
    [[ -n "${ALPACA_API_KEY:-}" ]] || missing+=(ALPACA_API_KEY)
    [[ -n "${ALPACA_SECRET_KEY:-}" ]] || missing+=(ALPACA_SECRET_KEY)
fi
[[ -n "${ALPACA_ENDPOINT:-}" ]] || missing+=(ALPACA_ENDPOINT)
[[ -n "${NOTIFY_WEBHOOK_URL:-}" ]] || missing+=(NOTIFY_WEBHOOK_URL)
if [[ "$routine" == pre-market || "$routine" == weekly ]]; then
    if [[ "${PERPLEXITY_AUTH:-}" != "proxy" && -z "${PERPLEXITY_API_KEY:-}" ]]; then
        echo "WARN=PERPLEXITY_API_KEY missing - research must fall back to WebSearch"
    fi
fi
if [[ "$LOCAL" == 0 && ( -n "${ALPACA_DRY_RUN:-}" || -n "${PREFLIGHT_FORCE_EXIT:-}" ) ]]; then
    missing+=("ALPACA_DRY_RUN/PREFLIGHT_FORCE_EXIT set in the cloud environment (test-only variables)")
fi
if ((${#missing[@]})); then
    echo "MISSING=${missing[*]}"
    alert "environment problem: ${missing[*]}. No trading this run."
    finish 10
fi

eval "$(py scripts/tlib.py now)"   # NOW_ET DATE WEEKDAY MONDAY DATE_MINUS_7 DATE_MINUS_14 EARNINGS_OK_FROM
for k in NOW_ET DATE WEEKDAY MONDAY DATE_MINUS_7 DATE_MINUS_14 EARNINGS_OK_FROM; do
    echo "$k=${!k}"
done
case "$ALPACA_ENDPOINT" in
    *paper-api*) MODE=PAPER ;;
    *) MODE=LIVE ;;
esac
echo "MODE=$MODE"
# Configuration guard first - it must not depend on the API being reachable.
if [[ "$MODE" == LIVE && "${LIVE_TRADING_CONFIRMED:-}" != yes ]]; then
    alert "live endpoint configured but LIVE_TRADING_CONFIRMED is not 'yes'. Nothing will trade."
    finish 50
fi

# ---- git history must be deep enough for the cadence check ------------------
if [[ "$(git rev-parse --is-shallow-repository 2>/dev/null)" == true ]]; then
    git fetch --quiet --deepen=400 origin main 2>/dev/null || true
fi
git fetch --quiet origin main 2>/dev/null || true

# ---- Alpaca reachability, clock and calendar -----------------------------------
clock=""
for i in 1 2 3; do
    clock="$(bash scripts/alpaca.sh clock 2>/dev/null)" && break
    clock=""
    sleep 3
done
if [[ -z "$clock" ]]; then
    echo "ALPACA=unreachable"
    alert "Alpaca API unreachable after 3 tries (KS-6). No orders this run."
    finish 40
fi
start7="$(py scripts/tlib.py et-date-offset -240)"
cal="$(bash scripts/alpaca.sh calendar "$start7" "$DATE" 2>/dev/null || echo '[]')"
eval "$(py - "$clock" "$cal" "$DATE" <<'PYEOF'
import json, sys
clock, cal, today = json.loads(sys.argv[1]), json.loads(sys.argv[2] or "[]"), sys.argv[3]
days = [d["date"] for d in cal]
prev = [d for d in days if d < today]
close = next((d["close"] for d in cal if d["date"] == today), "")
print("MARKET_OPEN=%s" % ("yes" if clock.get("is_open") else "no"))
print("NEXT_OPEN='%s'" % clock.get("next_open", ""))
print("NEXT_CLOSE='%s'" % clock.get("next_close", ""))
print("TODAY_TRADING=%s" % ("yes" if today in days else "no"))
print("TODAY_CLOSE_ET=%s" % close)
print("PREV_TRADING_DAY=%s" % (prev[-1] if prev else ""))
PYEOF
)"
for k in MARKET_OPEN NEXT_OPEN NEXT_CLOSE TODAY_TRADING TODAY_CLOSE_ET PREV_TRADING_DAY; do
    echo "$k=${!k}"
done
[[ -n "$TODAY_CLOSE_ET" && "$TODAY_CLOSE_ET" != "16:00" ]] && echo "EARLY_CLOSE=yes"

EVENT_TODAY="$(py scripts/tlib.py events "$DATE")"
echo "EVENT_TODAY=$EVENT_TODAY"

PAUSED=no
for f in memory/PAUSED.flag PAUSED.flag; do
    if [[ -f "$f" ]]; then
        PAUSED="$f: $(head -c 200 "$f" | tr '\n' ' ')"
        break
    fi
done
echo "PAUSED=$PAUSED"

# ---- live-money guards ---------------------------------------------------------
if [[ "$MODE" == LIVE ]]; then
    eq="$(bash scripts/alpaca.sh account 2>/dev/null | py -c 'import json,sys; print(json.load(sys.stdin).get("equity","0"))' || echo 0)"
    if py -c "import sys; sys.exit(0 if float('$eq') <= float('${MAX_LIVE_EQUITY:-3000}') else 1)"; then
        echo "LIVE_EQUITY=$eq"
    else
        alert "live equity $eq exceeds MAX_LIVE_EQUITY ${MAX_LIVE_EQUITY:-3000}. Wrong account? Nothing will trade."
        finish 51
    fi
fi

# ---- cadence: did the earlier routines commit? ------------------------------------
# Commit subjects: "<routine> <DATE>: OK|SKIPPED|ABORTED - <summary>"
subjects="$(git log -n 400 --format=%s origin/main 2>/dev/null || git log -n 400 --format=%s)"
has() { grep -Eq "^$1 $2: (OK|SKIPPED)" <<<"$subjects"; }
expect=()
if [[ "$TODAY_TRADING" == yes ]]; then
    case "$routine" in
        market-open) expect=("pre-market $DATE") ;;
        midday) expect=("pre-market $DATE" "market-open $DATE") ;;
        eod) expect=("pre-market $DATE" "market-open $DATE" "midday $DATE") ;;
    esac
fi
if [[ "$routine" == pre-market && -n "$PREV_TRADING_DAY" ]]; then
    expect+=("eod $PREV_TRADING_DAY")
    # first trading day of a new week: last Friday's review must exist
    if [[ "$(py -c "import datetime as d; print(d.date.fromisoformat('$PREV_TRADING_DAY').isocalendar()[1] != d.date.fromisoformat('$DATE').isocalendar()[1])")" == True ]]; then
        lastfri="$(py -c "import datetime as d; t=d.date.fromisoformat('$DATE'); print(t - d.timedelta(days=(t.weekday()-4) % 7 or 7))")"
        expect+=("weekly $lastfri")
    fi
fi
# Before the first ever run of a routine there is nothing to expect.
missing_commits=()
for e in "${expect[@]}"; do
    name="${e% *}"
    d="${e##* }"
    if grep -Eq "^$name [0-9]{4}-" <<<"$subjects" && ! has "$name" "$d"; then
        missing_commits+=("$e")
    fi
done
echo "MISSING_COMMITS=${missing_commits[*]:-none}"
last_ct="$(git log -1 --format=%ct origin/main 2>/dev/null || git log -1 --format=%ct)"
echo "LAST_COMMIT_AGE_H=$(( ( $(date +%s) - ${last_ct:-0} ) / 3600 ))"
if ((${#missing_commits[@]})); then
    alert "no OK/SKIPPED commit found for: ${missing_commits[*]}. A routine failed or never ran - check claude.ai/code/routines."
fi

# ---- decide -----------------------------------------------------------------------
if [[ -n "${PREFLIGHT_FORCE_EXIT:-}" ]]; then
    echo "FORCED_EXIT=$PREFLIGHT_FORCE_EXIT (test)"
    finish "$PREFLIGHT_FORCE_EXIT"
fi
if [[ "$routine" != weekly && "$TODAY_TRADING" != yes ]]; then
    finish 30
fi
if [[ ( "$routine" == market-open || "$routine" == midday ) && "$MARKET_OPEN" != yes ]]; then
    finish 31
fi
if [[ "$PAUSED" != no ]]; then
    finish 20
fi
finish 0
