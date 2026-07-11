#!/usr/bin/env python3
"""
Phase 1 — Historical OHLCV multi-timeframe puller.

Feeds the existing Technical Analyst with timeframes it didn't have
before (1min / 5min intraday bars, in addition to the daily closes
already sourced from market_data.py). Used for live/paper-trading
intraday confirmation, not for the historical backtest loop — the
backtester's window is a fixed set of historical daily closes, and
short-timeframe historical bars for those exact past days aren't
retrievable from this client's live-quote-style endpoint without a
separate (paid, higher-tier) historical tick archive, which is out of
scope for this pass.
"""

import requests

from data_clients.base_client import BaseRealDataClient, DataClientError

TIMEFRAME_TO_POLYGON = {
    "1min": (1, "minute"),
    "5min": (5, "minute"),
    "1day": (1, "day"),
}


class PolygonAggregatesClient(BaseRealDataClient):
    API_KEY_ENV = "POLYGON_API_KEY"
    CACHE_NAMESPACE = "polygon_aggregates"
    CACHE_TTL_SECONDS = 60
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, symbol: str, timeframe: str, lookback_bars: int = 100) -> dict:
        if timeframe not in TIMEFRAME_TO_POLYGON:
            raise DataClientError(f"Unsupported timeframe '{timeframe}', expected one of {list(TIMEFRAME_TO_POLYGON)}")

        multiplier, span = TIMEFRAME_TO_POLYGON[timeframe]
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{multiplier}/{span}/now/now"
        try:
            resp = requests.get(
                url,
                params={"apiKey": self.api_key, "limit": lookback_bars, "sort": "desc"},
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"Polygon aggregates request failed for {symbol}/{timeframe}: {e}") from e

        payload = resp.json()
        results = payload.get("results")
        if not results:
            raise DataClientError(f"Polygon returned no {timeframe} bars for {symbol}: {payload.get('status')}")

        bars = [
            {"t": r["t"], "o": r["o"], "h": r["h"], "l": r["l"], "c": r["c"], "v": r["v"]}
            for r in results
        ]
        return {"symbol": symbol, "timeframe": timeframe, "bars": bars}


def get_multi_timeframe_ohlcv(symbol: str, timeframes=("1min", "5min", "1day")) -> dict:
    """Fetches each requested timeframe independently. Returns a dict
    keyed by timeframe, each value a (data, data_source, reason) tuple —
    a feed being degraded for one timeframe doesn't block the others."""
    client = PolygonAggregatesClient()
    out = {}
    for tf in timeframes:
        data, source, reason = client.fetch(symbol=symbol, timeframe=tf)
        out[tf] = {"data": data, "data_source": source, "error_reason": reason}
    return out
