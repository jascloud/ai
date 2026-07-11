#!/usr/bin/env python3
"""
Phase 1 — Pre-market / after-hours quote puller.

Feeds Technical Analyst's overnight-gap detection: a large pre-market
gap (up or down) is real momentum information the daily-close-only
indicators (RSI/MACD/SMA computed on regular-session closes) can't see
until the next full session closes.
"""

import requests

from data_clients.base_client import BaseRealDataClient, DataClientError


class PolygonExtendedHoursClient(BaseRealDataClient):
    API_KEY_ENV = "POLYGON_API_KEY"
    CACHE_NAMESPACE = "polygon_extended_hours"
    CACHE_TTL_SECONDS = 30
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, symbol: str) -> dict:
        url = f"https://api.polygon.io/v2/last/trade/{symbol}"
        try:
            resp = requests.get(url, params={"apiKey": self.api_key}, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"Polygon extended-hours request failed for {symbol}: {e}") from e

        payload = resp.json()
        result = payload.get("results")
        if not result:
            raise DataClientError(f"Polygon returned no extended-hours trade for {symbol}: {payload}")

        return {
            "symbol": symbol,
            "price": result.get("p"),
            "size": result.get("s"),
            "timestamp": result.get("t"),
            "conditions": result.get("c"),
        }


def get_overnight_gap(symbol: str, prior_regular_close: float) -> tuple:
    """Returns (gap_pct, data_source, error_reason). gap_pct is
    (extended_hours_price - prior_regular_close) / prior_regular_close,
    or None if degraded — callers must not assume a zero gap when the
    feed is down, that's silently fabricating 'no gap' as if it were
    observed."""
    client = PolygonExtendedHoursClient()
    data, source, reason = client.fetch(symbol=symbol)

    if source not in ("real", "cached_real") or not data or not data.get("price"):
        return None, "degraded", reason or "no extended-hours price returned"

    gap_pct = (data["price"] - prior_regular_close) / prior_regular_close
    return gap_pct, source, None
