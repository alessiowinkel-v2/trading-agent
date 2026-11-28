#!/usr/bin/env bash
# Long-running news-sleeve loop for GitHub Actions (plans/news-sleeve/PLAN.md D14).
# GitHub delays and drops `*/15` cron triggers (observed: 2 runs in 14 h), so one job
# scans every 15 minutes for ~5.5 hours and an hourly cron keeps a successor queued.
# Once per ET day after 02:00 it also runs the scorer (in the same job, so the scanner
# and scorer can never race on memory/news/signals).
# Env: NEWSLOOP_MINUTES (330) NEWSLOOP_EVERY_SEC (900) NEWSLOOP_NO_PULL=1 (tests)
#      NEWSLOOP_SCORE=auto|always|never (auto)
#      NEWSLOOP_CHAIN=1 + GH_TOKEN + GITHUB_REPOSITORY (Actions only): when the loop has run its
#      full window it starts its own successor (workflow_dispatch), so coverage no longer depends
#      on GitHub firing the hourly cron (observed ~50% of 15-min slots in Nov 2026, PLAN D15).
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

chain_next() {
    # Only after a full window: a run that dies early must not spawn runs in a tight loop.
    [[ "${NEWSLOOP_CHAIN:-}" == 1 && -n "${GH_TOKEN:-}" && -n "${GITHUB_REPOSITORY:-}" ]] || return 0
    local need=$((minutes * 60 - 30 * 60))
    ((need < 3600)) && need=3600   # never chain a run shorter than an hour
    ((SECONDS >= need)) || { echo "[newsloop] ended early (${SECONDS}s) - not chaining (hourly cron is the backup)"; return 0; }
    local code
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 -X POST \
        -H "Authorization: Bearer $GH_TOKEN" -H "Accept: application/vnd.github+json" \
        "https://api.github.com/repos/$GITHUB_REPOSITORY/actions/workflows/newsscan.yml/dispatches" \
        -d '{"ref":"main"}')" || code=000
    echo "[newsloop] successor dispatched: HTTP $code (204 = queued)"
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
        chain_next
        break
    fi
    wait_s=$((next - SECONDS))
    ((wait_s > 0)) && sleep "$wait_s"
done
