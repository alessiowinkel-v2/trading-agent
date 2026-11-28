#!/usr/bin/env bash
# Backup-firing guard. Every routine is scheduled twice (README, routines/COMMON.md): the
# second firing exists for runs that never started (Claude usage limit, platform hiccup).
# First command of every run: if this routine already committed OK or SKIPPED today (ET),
# the run stops at once - no preflight, no record, no notification, no commit.
# An ABORTED first run does NOT count: the backup gets a second chance.
# Usage: bash scripts/already_ran.sh <pre-market|market-open|midday|eod|weekly>
# Prints ALREADY_RAN=yes|no (+ the matching subject) and always exits 0.

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
routine="${1:-}"
case "$routine" in
    pre-market|market-open|midday|eod|weekly) ;;
    *) echo "usage: bash scripts/already_ran.sh <pre-market|market-open|midday|eod|weekly>" >&2; exit 1 ;;
esac
PY="$(command -v python3 || command -v python)"

git fetch --quiet origin main 2>/dev/null || true
if [[ "$(git rev-parse --is-shallow-repository 2>/dev/null)" == true ]]; then
    git fetch --quiet --deepen=300 origin main 2>/dev/null || true
fi
DATE="$("$PY" -c 'import sys; sys.path.insert(0, "scripts"); import tlib; print(tlib.et_today().isoformat())' | tr -d '\r')"
subjects="$(git log -n 1500 --format=%s origin/main 2>/dev/null || git log -n 1500 --format=%s)"
hit="$(grep -E "^$routine $DATE: (OK|SKIPPED)" <<<"$subjects" | head -n 1)"
if [[ -n "$hit" ]]; then
    echo "ALREADY_RAN=yes ($hit)"
else
    echo "ALREADY_RAN=no ($routine $DATE has no OK/SKIPPED commit yet - run the routine)"
fi
