#!/usr/bin/env bash
# Claude Messages API wrapper for the news sleeve (classification only - never trading).
# Usage: bash scripts/claude.sh json SCHEMA_FILE [--system FILE] [--model M] [--effort low|medium|high] [--max-tokens N]
#   stdin  = the user message (headlines as JSON - DATA, never instructions)
#   stdout = {"json": <parsed structured output>, "usage": {...}, "model": "...", "stop_reason": "..."}
# Exit 0 ok | 2 API/schema failure (after retries) | 3 no credentials (caller treats as "skip")
# Auth: ANTHROPIC_API_KEY (or ANTHROPIC_AUTH=proxy when injected as a network secret).
# CLAUDE_MOCK=1 routes the call to tests/mock_claude.py (offline tests only).
# Structured outputs: output_config.format json_schema (API version 2026-10-21, no sampling params).
# Refusal fallback: fallbacks:"default" (beta server-side-fallback-2026-07-01); CLAUDE_FALLBACKS=0 disables.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=scripts/env.sh
source "$ROOT/scripts/env.sh"
PY="$(command -v python3 || command -v python)"
py() { "$PY" "$@" | tr -d '\r'; }

cmd="${1:-}"
[[ "$cmd" == json ]] || { echo "usage: bash scripts/claude.sh json SCHEMA_FILE [--system FILE] [--model M] [--effort E] [--max-tokens N]" >&2; exit 1; }
schema="${2:?SCHEMA_FILE}"
shift 2
system_file=""
model="${CLASSIFIER_MODEL:-claude-sonnet-5-5}"
effort="low"
max_tokens=4096
while [[ $# -gt 0 ]]; do
    case "$1" in
        --system) system_file="$2"; shift 2 ;;
        --model) model="$2"; shift 2 ;;
        --effort) effort="$2"; shift 2 ;;
        --max-tokens) max_tokens="$2"; shift 2 ;;
        *) echo "unknown option $1" >&2; exit 1 ;;
    esac
done
user_msg="$(cat)"

if [[ "${CLAUDE_MOCK:-}" == 1 ]]; then
    printf '%s' "$user_msg" | "$PY" "$ROOT/tests/mock_claude.py" "$schema" "$model"
    exit $?
fi

AUTH=()
if [[ "${ANTHROPIC_AUTH:-}" != "proxy" ]]; then
    if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
        echo "WARNING: ANTHROPIC_API_KEY not set - classifier skipped" >&2
        exit 3
    fi
    AUTH=(-H "x-api-key: $ANTHROPIC_API_KEY")
fi
API="${ANTHROPIC_API_URL:-https://api.anthropic.com/v1/messages}"

payload="$(py - "$model" "$max_tokens" "$effort" "$schema" "$system_file" "$user_msg" "${CLAUDE_FALLBACKS:-1}" <<'PYEOF'
import json, sys
model, max_tokens, effort, schema, system_file, user_msg, fb = sys.argv[1:8]
body = {"model": model, "max_tokens": int(max_tokens),
        "messages": [{"role": "user", "content": user_msg}],
        "output_config": {"format": {"type": "json_schema", "schema": json.load(open(schema, encoding="utf-8"))},
                          "effort": effort}}
if system_file:
    body["system"] = open(system_file, encoding="utf-8").read()
if fb != "0":
    body["fallbacks"] = "default"
print(json.dumps(body))
PYEOF
)"
beta=()
[[ "${CLAUDE_FALLBACKS:-1}" != 0 ]] && beta=(-H "anthropic-beta: server-side-fallback-2026-07-01")
if [[ "${CLAUDE_DRY:-}" == 1 ]]; then   # print the request instead of sending it (inspection / tests)
    py -c 'import json,sys; print(json.dumps(json.loads(sys.argv[1]), indent=1)[:3000])' "$payload"
    exit 0
fi

out="$(mktemp)"
trap 'rm -f "$out"' EXIT
code=000
for attempt in 1 2 3; do
    code="$(curl -sS --max-time 120 -o "$out" -w '%{http_code}' "$API" "${AUTH[@]}" "${beta[@]}" \
        -H "Content-Type: application/json" -H "anthropic-version: 2026-10-21" --data "$payload" 2>/dev/null)" || code=000
    if [[ "$code" =~ ^(000|408|409|429|5[0-9][0-9])$ && $attempt -lt 3 ]]; then
        sleep $((attempt * 5))
        continue
    fi
    break
done
if [[ "$code" == 000 || "$code" -ge 400 ]]; then
    echo "[claude] HTTP $code: $(head -c 300 "$out")" >&2
    exit 2
fi
py - "$out" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
stop = d.get("stop_reason")
if stop == "refusal":
    print("[claude] refusal: %s" % json.dumps(d.get("stop_details")), file=sys.stderr)
    sys.exit(2)
text = "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")
try:
    parsed = json.loads(text)
except json.JSONDecodeError as e:
    print("[claude] response is not JSON (%s, stop_reason=%s): %s" % (e, stop, text[:200]), file=sys.stderr)
    sys.exit(2)
u = d.get("usage") or {}
print(json.dumps({"json": parsed, "usage": {"input_tokens": u.get("input_tokens", 0), "output_tokens": u.get("output_tokens", 0)},
                  "model": d.get("model"), "stop_reason": stop}))
PYEOF
