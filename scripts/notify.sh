#!/usr/bin/env bash
# Notification wrapper. Posts to a Discord or Slack incoming webhook and always
# appends to memory/notifications/YYYY-MM.md (committed with the routine).
# Usage: bash scripts/notify.sh [--alert] "<message>"
#   --alert  prefixes "ALERT -" and $NOTIFY_MENTION (e.g. <@discord_user_id>)
# Exit codes: 0 delivered, 2 webhook rejected/unreachable, 3 NOTIFY_WEBHOOK_URL unset.
# A non-zero exit means the user did NOT get the message: say so in the commit
# subject ("notify=FAILED"), never pretend it was sent.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=scripts/env.sh
source "$ROOT/scripts/env.sh"

PY="$(command -v python3 || command -v python)"
py() { "$PY" "$@" | tr -d '\r'; }   # tr: Windows Python writes CRLF

alert=0
if [[ "${1:-}" == "--alert" ]]; then
    alert=1
    shift
fi

if [[ $# -gt 0 ]]; then
    msg="$*"
else
    msg="$(cat)"
fi

if [[ -z "${msg// /}" ]]; then
    echo "usage: bash scripts/notify.sh [--alert] \"<message>\"" >&2
    exit 1
fi

if [[ "$alert" == 1 ]]; then
    msg="ALERT - ${NOTIFY_MENTION:+$NOTIFY_MENTION }$msg"
fi

eval "$(py "$ROOT/scripts/tlib.py" now)"   # NOW_ET, DATE
log="$ROOT/memory/notifications/${DATE:0:7}.md"
mkdir -p "$(dirname "$log")"
printf "\n---\n## %s ET\n%s\n" "$NOW_ET" "$msg" >> "$log"

url="${NOTIFY_WEBHOOK_URL:-}"
if [[ -z "$url" ]]; then
    echo "[notify] NOTIFY_WEBHOOK_URL not set - logged to ${log#$ROOT/} only, user NOT notified" >&2
    exit 3
fi

# Discord caps content at 2000 chars, so split; Slack takes one {"text"} body.
mapfile -t payloads < <(py - "$url" "$msg" <<'PYEOF'
import json, sys
url, msg = sys.argv[1], sys.argv[2]
if "hooks.slack.com" in url:
    print(json.dumps({"text": msg}))
else:
    chunks = [msg[i:i + 1900] for i in range(0, len(msg), 1900)] or [msg]
    for c in chunks:
        key = "content" if ("discord.com" in url or "discordapp.com" in url) else "text"
        print(json.dumps({key: c}))
PYEOF
)

for p in "${payloads[@]}"; do
    if ! curl -fsS --max-time 15 --retry 3 --retry-delay 2 -o /dev/null \
        -H "Content-Type: application/json" -d "$p" "$url"; then
        echo "[notify] webhook FAILED - user NOT notified (message kept in ${log#$ROOT/})" >&2
        exit 2
    fi
done
echo "[notify] sent"
