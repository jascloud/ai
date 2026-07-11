#!/usr/bin/env python3
"""
Converts raw Interactive Brokers MCP connector get_price_history responses
(STK, step=FIVE_MINS, outside_rth=false) into intraday_5min_cache.json, the
format data_clients/engulfing_pattern.py's cache-file loader expects:
    {"SYMBOL": {"bars": [{"t": epoch_ms, "o":.., "h":.., "l":.., "c":.., "v":..}, ...],
                "source": ..., "chart_start": ..., "chart_end": ...}, ...}

The committed intraday_5min_cache.json in this repo is a real snapshot
fetched this way on 2026-07-11, one call per symbol against these contract
IDs (resolved via search_contracts, exact-symbol NASDAQ primary listings):
    AAPL=265598  MSFT=272093  GOOGL=208813719  AMZN=3691937  TSLA=76792991
get_price_history's step_count is capped at 1000 data points per call with
no explicit start/end window param, so each pull returned the trailing
1000 five-minute regular-hours bars available at call time (~13 trading
days, 2026-06-23 to 2026-07-10) rather than a full requested date range —
that's a real limit of this MCP tool, not a bug in this script.

To regenerate: call get_price_history once per symbol (security_type=STK,
step=FIVE_MINS, step_count=1000, outside_rth=false), save each raw response
as raw_ibkr_5min/{SYMBOL}.json (the tool's native
{time, open, high, low, close, volume, chart_start, chart_end} shape), then
run this script.
"""

import json
import os
from datetime import datetime

RAW_DIR = "raw_ibkr_5min"
SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
OUTPUT_FILE = "intraday_5min_cache.json"


def convert_one(symbol: str, raw: dict) -> dict:
    times = raw["time"]
    opens = raw["open"]
    highs = raw["high"]
    lows = raw["low"]
    closes = raw["close"]
    volumes = raw["volume"]

    bars = []
    for i in range(len(times)):
        ts = datetime.fromisoformat(times[i].replace("Z", "+00:00"))
        bars.append({
            "t": int(ts.timestamp() * 1000),
            "o": opens[i],
            "h": highs[i],
            "l": lows[i],
            "c": closes[i],
            "v": volumes[i],
        })

    return {
        "bars": bars,
        "source": "ibkr_mcp_get_price_history",
        "chart_start": raw["chart_start"],
        "chart_end": raw["chart_end"],
    }


def main():
    cache = {}
    for symbol in SYMBOLS:
        raw_path = os.path.join(RAW_DIR, f"{symbol}.json")
        if not os.path.isfile(raw_path):
            print(f"skip {symbol}: {raw_path} not found (re-run get_price_history and save the raw response there)")
            continue
        with open(raw_path) as f:
            raw = json.load(f)
        cache[symbol] = convert_one(symbol, raw)
        print(f"{symbol}: {len(cache[symbol]['bars'])} real 5-min bars, "
              f"{cache[symbol]['chart_start']} to {cache[symbol]['chart_end']}")

    if not cache:
        print(f"Nothing to convert -- populate {RAW_DIR}/{{SYMBOL}}.json first.")
        return

    with open(OUTPUT_FILE, "w") as f:
        json.dump(cache, f)
    print(f"\nWrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
