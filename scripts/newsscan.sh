#!/usr/bin/env bash
# One scanner run + commit, used by .github/workflows/newsscan.yml (and by hand).
# Commits when there are new rows, when the run aborted, or when the last scanner
# commit is older than 2 h (heartbeat) - see plans/news-sleeve/PLAN.md D12.
# Usage: bash scripts/newsscan.sh [newsscan.py args]

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=scripts/env.sh
source "$ROOT/scripts/env.sh"
PY="$(command -v python3 || command -v python)"
py() { "$PY" "$@" | tr -d '\r'; }

eval "$(py scripts/tlib.py now)"   # DATE (ET)
stamp="$(py -c 'import sys; sys.path.insert(0,"scripts"); import tlib; print(tlib.utc_now().strftime("%H:%MZ"))')"

out="$(py scripts/newsscan.py "$@" 2>&1)"
rc=$?
echo "$out"
line="$(grep -E '^NEWSSCAN ' <<<"$out" | tail -n 1)"
new="$(grep -oE 'new=[0-9]+' <<<"$line" | head -n 1 | cut -d= -f2)"
sig="$(grep -oE 'signals=[0-9]+' <<<"$line" | head -n 1 | cut -d= -f2)"

if [[ $rc -ne 0 ]]; then
    err="$(sed -E 's/^NEWSSCAN ABORTED error=//' <<<"$line" | cut -c1-120)"
    subject="newsscan $DATE $stamp: ABORTED - ${err:-unknown error}"
elif [[ "${new:-0}" -gt 0 ]]; then
    subject="newsscan $DATE $stamp: OK - $new new headlines, ${sig:-0} signals"
elif py scripts/newslib.py heartbeat-due 2; then
    subject="newsscan $DATE $stamp: OK - 0 new (heartbeat)"
else
    echo "[newsscan] nothing new, heartbeat not due - no commit"
    exit 0
fi
py scripts/newslib.py mark-commit
bash scripts/gitpush.sh "$subject"
