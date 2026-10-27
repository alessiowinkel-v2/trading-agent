#!/usr/bin/env bash
# Dead-man's switch, run by .github/workflows/watchdog.yml on GitHub (outside
# the Claude cloud, so it still fires if routines, the environment or the
# subscription stop). Checks routine commit subjects on main and alerts if any
# is missing or ABORTED. Exits 1 on a problem so GitHub also emails the owner.
# Usage: bash scripts/watchdog.sh <midday|nightly|grid MONDAY>

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="$(command -v python3 || command -v python)"
py() { "$PY" "$@" | tr -d '\r'; }
mode="${1:?usage: watchdog.sh <midday|nightly|grid MONDAY>}"
subjects="$(git log -n 600 --format=%s)"

status_of() {  # status_of <routine> <date> -> OK|SKIPPED|ABORTED|MISSING
    local s
    s="$(grep -E "^$1 $2: " <<<"$subjects" | head -n 1 | sed -E "s/^$1 $2: ([A-Z]+).*/\1/")"
    echo "${s:-MISSING}"
}

if [[ "$mode" == grid ]]; then
    monday="${2:?grid needs the Monday date}"
    echo "| Day | pre-market | market-open | midday | eod |"
    echo "|---|---|---|---|---|"
    for i in 0 1 2 3 4; do
        d="$(py -c "import datetime as d; print(d.date.fromisoformat('$monday') + d.timedelta(days=$i))")"
        echo "| $d | $(status_of pre-market "$d") | $(status_of market-open "$d") | $(status_of midday "$d") | $(status_of eod "$d") |"
    done
    exit 0
fi

case "$mode" in
    midday)  date_et="$(py scripts/tlib.py et-date-offset 0)"; routines=(pre-market market-open) ;;
    nightly) date_et="$(py scripts/tlib.py et-date-offset -2)"; routines=(pre-market market-open midday eod) ;;
    *) echo "unknown mode $mode" >&2; exit 2 ;;
esac
dow="$(py -c "import datetime as d; print(d.date.fromisoformat('$date_et').isoweekday())")"
if ((dow > 5)); then
    echo "weekend ($date_et) - nothing to check"
    exit 0
fi
[[ "$mode" == nightly && "$dow" == 5 ]] && routines+=(weekly)

problems=()
for r in "${routines[@]}"; do
    st="$(status_of "$r" "$date_et")"
    echo "$r $date_et: $st"
    [[ "$st" == OK || "$st" == SKIPPED ]] || problems+=("$r=$st")
done

if ((${#problems[@]} == 0)); then
    echo "all routines reported for $date_et"
    exit 0
fi

msg="ALERT - watchdog ($mode): trading routines for $date_et not healthy: ${problems[*]}. Check claude.ai/code/routines (routine paused? environment deleted? usage limit? GitHub connection?)."
echo "$msg"
if [[ -n "${NOTIFY_WEBHOOK_URL:-}" ]]; then
    payload="$(py -c 'import json,sys
u,m=sys.argv[1],sys.argv[2]
print(json.dumps({"text": m} if "hooks.slack.com" in u else {"content": m[:1900]}))' "$NOTIFY_WEBHOOK_URL" "${NOTIFY_MENTION:+$NOTIFY_MENTION }$msg")"
    curl -fsS --max-time 15 --retry 3 -o /dev/null -H "Content-Type: application/json" -d "$payload" "$NOTIFY_WEBHOOK_URL" \
        || echo "webhook delivery FAILED as well" >&2
else
    echo "NOTIFY_WEBHOOK_URL secret not set" >&2
fi
exit 1
