#!/usr/bin/env bash
# Print the last N dated entries of a memory log (headings "## YYYY-MM-DD" or
# "### YYYY-MM-DD"). Routines read logs only through this - never cat a whole log.
# Usage: bash scripts/memtail.sh memory/RESEARCH-LOG.md [N=1]

set -euo pipefail

f="${1:?usage: memtail.sh FILE [N]}"
n="${2:-1}"
[[ -f "$f" ]] || { echo "(no $f)"; exit 0; }

starts="$(grep -nE '^#{2,3} [0-9]{4}-[0-9]{2}-[0-9]{2}' "$f" | cut -d: -f1 || true)"
if [[ -z "$starts" ]]; then
    echo "(no dated entries in $f yet)"
    exit 0
fi
from="$(tail -n "$n" <<<"$starts" | head -n 1)"
tail -n +"$from" "$f"
