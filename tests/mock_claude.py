#!/usr/bin/env python3
"""Deterministic stand-in for scripts/claude.sh (CLAUDE_MOCK=1). Reads the user message
(JSON array of headline items) from stdin and classifies by keyword so the offline tests
can exercise newsclassify.py, alerts and dedup without an API key.
  headline contains "BADJSON" -> that item is omitted (schema/coverage failure path)."""

import json
import re
import sys

text = sys.stdin.read()
m = re.search(r"\[.*\]", text, re.S)
items = json.loads(m.group(0)) if m else []
res = []
for it in items:
    h = (it.get("headline") or "").lower()
    if "badjson" in h:
        continue
    r = {"id": it["id"], "ticker": it["ticker"], "direction": "none", "magnitude": 1, "horizon": "days",
         "category": "other", "novelty": "new", "confidence": 0.0, "rationale": "mock: not price-relevant"}
    if "raises" in h and "guidance" in h:
        r.update(direction="bull", magnitude=2, category="guidance", confidence=0.85, rationale="mock: guidance raised")
    elif "slips" in h or "falls" in h or "outflows" in h:
        r.update(direction="bear", magnitude=2, category="macro" if it["ticker"] == "BTC/USD" else "other", confidence=0.7,
                 rationale="mock: negative flow")
    elif "fed" in h or "rate" in h:
        r.update(ticker="SPY", direction="bear", magnitude=2, category="macro", confidence=0.65, rationale="mock: hawkish fed")
    elif "probe" in h or "lawsuit" in h or "recall" in h:
        r.update(direction="bear", magnitude=2, category="legal", confidence=0.8, rationale="mock: legal risk")
    elif "acquire" in h or "merger" in h:
        r.update(direction="bull", magnitude=3, category="m_and_a", confidence=0.9, rationale="mock: deal")
    res.append(r)
print(json.dumps({"json": {"results": res}, "usage": {"input_tokens": 120 * max(1, len(items)), "output_tokens": 40 * max(1, len(items))},
                  "model": sys.argv[2] if len(sys.argv) > 2 else "mock", "stop_reason": "end_turn"}))
