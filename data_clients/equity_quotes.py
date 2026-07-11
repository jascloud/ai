#!/usr/bin/env python3
"""
Phase 1 — Real-time equity Level 1 quotes.

Primary: Polygon.io (POLYGON_API_KEY)
Fallback: IEX Cloud (IEX_CLOUD_API_KEY)

Used for: live rating (Technical Analyst's live-mode enrichment) and as
a realistic fill-price source for paper-trading. Backtests continue to
use the historical daily closes from market_data.py — quoting today's
Level 1 price for a historical day would be lookahead bias, not a
strengthening of the backtest.
"""

import requests

from data_clients.base_client import BaseRealDataClient, DataClientError


class PolygonQuoteClient(BaseRealDataClient):
    API_KEY_ENV = "POLYGON_API_KEY"
    CACHE_NAMESPACE = "polygon_quote"
    CACHE_TTL_SECONDS = 15  # Level 1 quotes are only useful very fresh
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, symbol: str) -> dict:
        url = f"https://api.polygon.io/v2/last/nbbo/{symbol}"
        try:
            resp = requests.get(url, params={"apiKey": self.api_key}, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"Polygon quote request failed for {symbol}: {e}") from e

        payload = resp.json()
        result = payload.get("results")
        if not result:
            raise DataClientError(f"Polygon returned no quote for {symbol}: {payload}")

        return {
            "symbol": symbol,
            "bid": result.get("p"),
            "ask": result.get("P"),
            "bid_size": result.get("s"),
            "ask_size": result.get("S"),
            "timestamp": result.get("t"),
            "provider": "polygon",
        }


class IEXCloudQuoteClient(BaseRealDataClient):
    API_KEY_ENV = "IEX_CLOUD_API_KEY"
    CACHE_NAMESPACE = "iex_quote"
    CACHE_TTL_SECONDS = 15
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, symbol: str) -> dict:
        url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote"
        try:
            resp = requests.get(url, params={"token": self.api_key}, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"IEX Cloud quote request failed for {symbol}: {e}") from e

        payload = resp.json()
        if not payload:
            raise DataClientError(f"IEX Cloud returned no quote for {symbol}")

        return {
            "symbol": symbol,
            "bid": payload.get("iexBidPrice"),
            "ask": payload.get("iexAskPrice"),
            "latest_price": payload.get("latestPrice"),
            "timestamp": payload.get("latestUpdate"),
            "provider": "iex_cloud",
        }


def get_level1_quote(symbol: str) -> tuple:
    """Tries Polygon first, then IEX Cloud. Returns (data, data_source, reason)
    exactly like BaseRealDataClient.fetch() — 'degraded' means neither
    source produced a real quote, data is None, and reason lists both
    attempts. Never fabricates a quote."""
    polygon = PolygonQuoteClient()
    data, source, reason = polygon.fetch(symbol=symbol)
    if source in ("real", "cached_real"):
        return data, source, None

    iex = IEXCloudQuoteClient()
    data2, source2, reason2 = iex.fetch(symbol=symbol)
    if source2 in ("real", "cached_real"):
        return data2, source2, None

    return None, "degraded", f"polygon: {reason}; iex_cloud: {reason2}"
