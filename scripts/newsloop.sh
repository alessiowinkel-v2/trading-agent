#!/usr/bin/env bash
# Long-running news-sleeve loop for GitHub Actions (plans/news-sleeve/PLAN.md D14).
# GitHub delays and drops `*/15` cron triggers (observed: 2 runs in 14 h), so one job
# scans every 15 minutes for ~5.5 hours and an hourly cron keeps a successor queued.
# Once per ET day after 02:00 it also runs the scorer (in the same job, so the scanner
# and scorer can never race on memory/news/signals).
# Env: NEWSLOOP_MINUTES (330) NEWSLOOP_EVERY_SEC (900) NEWSLOOP_NO_PULL=1 (tests)
#      NEWSLOOP_SCORE=auto|always|never (auto)
# Usage: bash scripts/newsloop.sh

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="$(command -v python3 || command -v python)"
py() { "$PY" "$@" | tr -d '\r'; }

minutes="${NEWSLOOP_MINUTES:-330}"
every="${NEWSLOOP_EVERY_SEC:-900}"
score_mode="${NEWSLOOP_SCORE:-auto}"
end=$((SECONDS + minutes * 60))
i=0

score() {
    py scripts/newslib.py mark-score-attempt
    local out rc line
    out="$(py scripts/newsscore.py 2>&1)"
    rc=$?
    echo "$out"
    eval "$(py scripts/tlib.py now)"   # DATE (ET)
    line="$(grep -E '^NEWSSCORE ' <<<"$out" | tail -n 1 | cut -c1-150)"
    if [[ $rc -ne 0 ]]; then
        bash scripts/notify.sh --alert "newsscore: ${line:-crashed}" || true
        bash scripts/gitpush.sh "newsscore $DATE: ABORTED - ${line#NEWSSCORE ABORTED }"
    else
        bash scripts/gitpush.sh "newsscore $DATE: OK - ${line#NEWSSCORE ok }"
    fi
}

while :; do
    i=$((i + 1))
    start=$SECONDS
    if [[ "${NEWSLOOP_NO_PULL:-}" != 1 ]]; then
        # pick up routine commits (STATE.json for held symbols) before writing anything
        if ! git pull --quiet --rebase origin main 2>/dev/null; then
            git rebase --abort 2>/dev/null || true
            echo "[newsloop] pull failed - continuing on local state (gitpush.sh rebases on push)" >&2
        fi
    fi
    echo "[newsloop] iteration $i at $(date -u +%H:%MZ)"
    bash scripts/newsscan.sh || echo "[newsloop] newsscan.sh exit $?" >&2
    if [[ "$score_mode" == always ]] || { [[ "$score_mode" == auto ]] && py scripts/newslib.py score-due; }; then
        score || echo "[newsloop] scorer step exit $?" >&2
    fi
    next=$((start + every))
    if ((next + 60 > end)); then
        echo "[newsloop] done after $i iterations"
        break
    fi
    wait_s=$((next - SECONDS))
    ((wait_s > 0)) && sleep "$wait_s"
done
