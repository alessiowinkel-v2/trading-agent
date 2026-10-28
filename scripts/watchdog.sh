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
subjects="$(git log -n 2000 --format=%s)"

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

# GitHub runs scheduled jobs late (hours late is common), so the date to check comes from
# the ET wall clock at RUN time, not from the cron slot:
#   midday  - today's pre-market + market-open, only once 10:45 ET has passed (else nothing to check yet)
#   nightly - today's four routines if it is already >= 18:00 ET, else yesterday's
read -r et_date et_hm < <(py -c 'import sys; sys.path.insert(0,"scripts"); import tlib; n=tlib.et_now(); print(n.date().isoformat(), n.strftime("%H:%M"))')
case "$mode" in
    midday)
        if [[ "$et_hm" < "10:45" ]]; then
            echo "midday check at $et_hm ET: too early for today's routines (delayed run?) - nothing to check"
            exit 0
        fi
        date_et="$et_date"; routines=(pre-market market-open) ;;
    nightly)
        if [[ "$et_hm" < "18:00" ]]; then
            date_et="$(py -c "import datetime as d; print(d.date.fromisoformat('$et_date') - d.timedelta(days=1))")"
        else
            date_et="$et_date"
        fi
        routines=(pre-market market-open midday eod) ;;
    *) echo "unknown mode $mode" >&2; exit 2 ;;
esac
echo "watchdog $mode at $et_date $et_hm ET -> checking $date_et"
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

# News-sleeve scanner heartbeat (GitHub Actions loop, every 15 min; commits at least every 2 h).
# Only checked once the scanner is deployed, i.e. it has committed from Actions at least once
# (a "newsscan ..." subject exists). Until the Alpaca secrets are set it never commits, so
# no alert - see plans/news-sleeve/PLAN.md D12/D14.
if [[ -f memory/news/state.json ]] && grep -q '^newsscan ' <<<"$subjects"; then
    age="$(py -c 'import json,sys,datetime as d
s=json.load(open("memory/news/state.json")); t=s.get("last_ok_utc") or s.get("last_run_utc")
print("none" if not t else round((d.datetime.now(d.timezone.utc)-d.datetime.fromisoformat(t.replace("Z","+00:00"))).total_seconds()/3600,1))')"
    if [[ "$age" == none ]] || py -c "import sys; sys.exit(0 if float('$age') > 3 else 1)"; then
        echo "newsscan: last OK run ${age}h ago"
        problems+=("newsscan=STALE(${age}h)")
    else
        echo "newsscan: last OK run ${age}h ago"
    fi
fi

if ((${#problems[@]} == 0)); then
    echo "all routines reported for $date_et"
    exit 0
fi

msg="ALERT - watchdog ($mode): trading routines for $date_et not healthy: ${problems[*]}. Check claude.ai/code/routines (routine paused? environment deleted? usage limit? GitHub connection?) or, for newsscan, the Actions tab of the repository."
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
