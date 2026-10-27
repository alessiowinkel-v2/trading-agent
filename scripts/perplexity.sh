#!/usr/bin/env bash
# Research wrapper: news, catalysts, earnings dates. NEVER use it for prices
# (prices come from scripts/alpaca.sh only).
# Usage: bash scripts/perplexity.sh [-r day|week|month] [--text] "<query>"
#   -r      restrict search results to that recency window
#   --text  print only the answer + citations instead of raw JSON (saves context)
# Exits 3 if no credentials so callers can fall back to WebSearch.
# Auth: PERPLEXITY_API_KEY, or PERPLEXITY_AUTH=proxy when injected as a network secret.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=scripts/env.sh
source "$ROOT/scripts/env.sh"

PY="$(command -v python3 || command -v python)"
py() { "$PY" "$@" | tr -d '\r'; }   # tr: Windows Python writes CRLF
recency=""
text=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        -r) recency="${2:?-r needs day|week|month}"; shift 2 ;;
        --text) text=1; shift ;;
        *) break ;;
    esac
done

query="${1:-}"
if [[ -z "$query" ]]; then
    echo "usage: bash scripts/perplexity.sh [-r day|week|month] [--text] \"<query>\"" >&2
    exit 1
fi

AUTH=()
if [[ "${PERPLEXITY_AUTH:-}" != "proxy" ]]; then
    if [[ -z "${PERPLEXITY_API_KEY:-}" ]]; then
        echo "WARNING: PERPLEXITY_API_KEY not set. Fall back to WebSearch." >&2
        exit 3
    fi
    AUTH=(-H "Authorization: Bearer $PERPLEXITY_API_KEY")
fi

MODEL="${PERPLEXITY_MODEL:-sonar}"

payload="$(py -c "
import json, sys
body = {
    'model': sys.argv[1],
    'messages': [
        {'role': 'system', 'content': 'You are a precise financial research assistant. Cite every claim with its date. Be concise. Never state a stock price.'},
        {'role': 'user', 'content': sys.argv[2]},
    ],
}
if sys.argv[3]:
    body['search_recency_filter'] = sys.argv[3]
print(json.dumps(body))
" "$MODEL" "$query" "$recency")"

resp="$(curl -fsS --max-time 60 --retry 2 https://api.perplexity.ai/chat/completions \
    "${AUTH[@]}" \
    -H "Content-Type: application/json" \
    -d "$payload")"

if [[ "$text" == 1 ]]; then
    py -c "
import json, sys
d = json.loads(sys.argv[1])
print(d['choices'][0]['message']['content'].strip())
cites = d.get('citations') or [r.get('url') for r in d.get('search_results') or []]
if cites:
    print('Sources:')
    for i, c in enumerate(cites, 1):
        print('  [%d] %s' % (i, c))
" "$resp"
else
    echo "$resp"
fi
