#!/usr/bin/env bash
# Notification wrapper. Posts to a ClickUp Chat channel if configured.
# Usage: bash scripts/notify.sh "<message>"
# If credentials are unset, appends to a local fallback file (this is fine and
# expected during Phase 1 paper trading — ClickUp can be added later).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
FALLBACK="$ROOT/memory/notifications/notifications.md"

if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
fi

if [[ $# -gt 0 ]]; then
    msg="$*"
else
    msg="$(cat)"
fi

if [[ -z "${msg// /}" ]]; then
    echo "usage: bash scripts/notify.sh \"<message>\"" >&2
    exit 1
fi

stamp="$(date '+%Y-%m-%d %H:%M %Z')"

# Always append to local fallback so we have a record regardless of channel
mkdir -p "$(dirname "$FALLBACK")"
printf "\n---\n## %s\n%s\n" "$stamp" "$msg" >> "$FALLBACK"

# If ClickUp not configured, that's fine — we still have the local log
if [[ -z "${CLICKUP_API_KEY:-}" || -z "${CLICKUP_WORKSPACE_ID:-}" || -z "${CLICKUP_CHANNEL_ID:-}" ]]; then
    echo "[notify] appended to $FALLBACK (ClickUp not configured — this is fine)"
    echo "$msg"
    exit 0
fi

# Send to ClickUp if configured
payload="$(python3 -c "
import json, sys
print(json.dumps({'type': 'message', 'content': sys.argv[1], 'content_format': 'text/md'}))
" "$msg")"

curl -fsS -X POST \
    "https://api.clickup.com/api/v3/workspaces/$CLICKUP_WORKSPACE_ID/chat/channels/$CLICKUP_CHANNEL_ID/messages" \
    -H "Authorization: $CLICKUP_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"

echo
