#!/usr/bin/env python3
"""
Phase 2 — Analyst rating / price-target aggregator.

Uses Finnhub's recommendation-trends and price-target endpoints
(FINNHUB_API_KEY). Shared key with estimate_revisions.py, same pattern
as Polygon covering all four Phase 1 clients under one key.
"""

import requests

from data_clients.base_client import BaseRealDataClient, DataClientError


class FinnhubRecommendationClient(BaseRealDataClient):
    API_KEY_ENV = "FINNHUB_API_KEY"
    CACHE_NAMESPACE = "finnhub_recommendation"
    CACHE_TTL_SECONDS = 21600
    RATE_LIMIT_CALLS = 30
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, symbol: str) -> dict:
        try:
            resp = requests.get(
                "https://finnhub.io/api/v1/stock/recommendation",
                params={"symbol": symbol, "token": self.api_key},
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"Finnhub recommendation request failed for {symbol}: {e}") from e

        payload = resp.json()
        if not payload:
            raise DataClientError(f"Finnhub returned no recommendation data for {symbol}")
        return {"symbol": symbol, "trends": payload}


class FinnhubPriceTargetClient(BaseRealDataClient):
    API_KEY_ENV = "FINNHUB_API_KEY"
    CACHE_NAMESPACE = "finnhub_price_target"
    CACHE_TTL_SECONDS = 21600
    RATE_LIMIT_CALLS = 30
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, symbol: str) -> dict:
        try:
            resp = requests.get(
                "https://finnhub.io/api/v1/stock/price-target",
                params={"symbol": symbol, "token": self.api_key},
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"Finnhub price-target request failed for {symbol}: {e}") from e

        payload = resp.json()
        if not payload or payload.get("targetMean") is None:
            raise DataClientError(f"Finnhub returned no price target for {symbol}")
        return payload


def get_analyst_consensus(symbol: str, current_price: float) -> tuple:
    """Returns (consensus, data_source, reason).
    consensus = {rating_lean, upside_pct} where rating_lean is one of
    'strong_buy'/'buy'/'hold'/'sell'/'strong_sell' derived from the most
    recent recommendation-trend row, and upside_pct is (target_mean -
    current_price) / current_price."""
    rec_client = FinnhubRecommendationClient()
    rec_data, rec_source, rec_reason = rec_client.fetch(symbol=symbol)

    if rec_source not in ("real", "cached_real") or not rec_data:
        return None, "degraded", rec_reason or "no recommendation data"

    trends = rec_data.get("trends", [])
    if not trends:
        return None, "degraded", "recommendation data returned but empty"

    latest = trends[0]
    counts = {
        "strong_buy": latest.get("strongBuy", 0),
        "buy": latest.get("buy", 0),
        "hold": latest.get("hold", 0),
        "sell": latest.get("sell", 0),
        "strong_sell": latest.get("strongSell", 0),
    }
    rating_lean = max(counts, key=counts.get)

    target_client = FinnhubPriceTargetClient()
    target_data, target_source, target_reason = target_client.fetch(symbol=symbol)

    upside_pct = None
    if target_source in ("real", "cached_real") and target_data and current_price:
        target_mean = target_data.get("targetMean")
        if target_mean:
            upside_pct = (target_mean - current_price) / current_price

    return {
        "rating_lean": rating_lean,
        "counts": counts,
        "upside_pct": upside_pct,
    }, rec_source, None
