#!/usr/bin/env bash
# Compact view of recent news signals for the routines (read-only: input to G7 and to the
# midday review of held names - never a gate, never an order).
# Usage: bash scripts/newsfeed.sh [--since HOURS=24] [--symbols A,B] [--min-conf 0.0] [--all]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$(command -v python3 || command -v python)"
"$PY" "$ROOT/scripts/newsfeed.py" "$@" | tr -d '\r'
