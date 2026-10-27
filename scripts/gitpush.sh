#!/usr/bin/env bash
# Commit memory/ and push to main. The ONLY way routines persist their work.
# Usage: bash scripts/gitpush.sh "<routine> <DATE>: OK|SKIPPED|ABORTED - <summary>"
# Always commits (empty commit if nothing changed) so every run leaves a
# heartbeat. Rebases on concurrent pushes; never force-pushes. Alerts and exits 1
# if the push finally fails. GIT_PUSH_DISABLED=1 commits without pushing (tests).

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
subject="${1:?usage: gitpush.sh \"<routine> <DATE>: OK|SKIPPED|ABORTED - <summary>\"}"

if ! grep -Eq '^(pre-market|market-open|midday|eod|weekly|newsscore) [0-9]{4}-[0-9]{2}-[0-9]{2}: (OK|SKIPPED|ABORTED)' <<<"$subject" \
   && ! grep -Eq '^newsscan [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}Z: (OK|ABORTED)' <<<"$subject"; then
    echo "[gitpush] subject must look like '<routine> <YYYY-MM-DD>: OK|SKIPPED|ABORTED - summary' (or 'newsscan <DATE> <HH:MM>Z: OK|ABORTED - …')" >&2
    exit 2
fi

git config user.name >/dev/null || git config user.name "trading-agent"
git config user.email >/dev/null || git config user.email "trading-agent@users.noreply.github.com"

git add -A memory/
git commit --quiet --allow-empty -m "$subject" || { echo "[gitpush] commit failed" >&2; exit 1; }

if [[ "${GIT_PUSH_DISABLED:-}" == 1 ]]; then
    echo "[gitpush] committed, push disabled: $subject"
    exit 0
fi

for attempt in 1 2 3 4; do
    if git push --quiet origin HEAD:main 2>/dev/null; then
        echo "[gitpush] pushed: $subject"
        exit 0
    fi
    ((attempt == 4)) && break
    sleep $((attempt * 5))
    git fetch --quiet origin main || true
    if ! git rebase --quiet origin/main; then
        git rebase --abort 2>/dev/null || true
        echo "[gitpush] rebase conflict on attempt $attempt" >&2
    fi
done

git diff --stat origin/main >&2 || true
bash scripts/notify.sh --alert "push failed after 4 attempts: $subject - this run's records are NOT saved" || true
exit 1
