#!/usr/bin/env python3
"""
Phase 2 — Revenue/EPS estimate revisions tracker.

Uses Finnhub's EPS-estimate and revenue-estimate endpoints
(FINNHUB_API_KEY, shared with analyst_ratings.py) to detect whether
Street estimates for the current fiscal period have been revised up or
down recently.
"""

import requests

from data_clients.base_client import BaseRealDataClient, DataClientError


class FinnhubEPSEstimateClient(BaseRealDataClient):
    API_KEY_ENV = "FINNHUB_API_KEY"
    CACHE_NAMESPACE = "finnhub_eps_estimate"
    CACHE_TTL_SECONDS = 21600
    RATE_LIMIT_CALLS = 30
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, symbol: str) -> dict:
        try:
            resp = requests.get(
                "https://finnhub.io/api/v1/stock/eps-estimate",
                params={"symbol": symbol, "freq": "quarterly", "token": self.api_key},
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"Finnhub EPS estimate request failed for {symbol}: {e}") from e

        payload = resp.json()
        data = payload.get("data")
        if not data:
            raise DataClientError(f"Finnhub returned no EPS estimates for {symbol}")
        return {"symbol": symbol, "estimates": data}


class FinnhubRevenueEstimateClient(BaseRealDataClient):
    API_KEY_ENV = "FINNHUB_API_KEY"
    CACHE_NAMESPACE = "finnhub_revenue_estimate"
    CACHE_TTL_SECONDS = 21600
    RATE_LIMIT_CALLS = 30
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, symbol: str) -> dict:
        try:
            resp = requests.get(
                "https://finnhub.io/api/v1/stock/revenue-estimate",
                params={"symbol": symbol, "freq": "quarterly", "token": self.api_key},
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"Finnhub revenue estimate request failed for {symbol}: {e}") from e

        payload = resp.json()
        data = payload.get("data")
        if not data:
            raise DataClientError(f"Finnhub returned no revenue estimates for {symbol}")
        return {"symbol": symbol, "estimates": data}


def get_estimate_revision_direction(symbol: str) -> tuple:
    """Returns (revisions, data_source, reason).
    revisions = {eps_revision_direction, revenue_revision_direction},
    each one of 'up'/'down'/'flat', comparing the two most recent
    quarterly estimate submissions for the nearest fiscal period."""

    def _direction(estimates):
        if not estimates or len(estimates) < 2:
            return None
        by_period = {}
        for e in estimates:
            period = e.get("period")
            by_period.setdefault(period, []).append(e)
        for period, rows in by_period.items():
            if len(rows) >= 2:
                rows_sorted = sorted(rows, key=lambda r: r.get("period", ""))
                latest_val = rows_sorted[-1].get("epsAvg") or rows_sorted[-1].get("revenueAvg")
                prior_val = rows_sorted[-2].get("epsAvg") or rows_sorted[-2].get("revenueAvg")
                if latest_val is None or prior_val is None:
                    continue
                if latest_val > prior_val:
                    return "up"
                if latest_val < prior_val:
                    return "down"
                return "flat"
        return None

    eps_client = FinnhubEPSEstimateClient()
    eps_data, eps_source, eps_reason = eps_client.fetch(symbol=symbol)

    rev_client = FinnhubRevenueEstimateClient()
    rev_data, rev_source, rev_reason = rev_client.fetch(symbol=symbol)

    eps_ok = eps_source in ("real", "cached_real") and eps_data
    rev_ok = rev_source in ("real", "cached_real") and rev_data

    if not eps_ok and not rev_ok:
        return None, "degraded", f"eps: {eps_reason}; revenue: {rev_reason}"

    eps_direction = _direction(eps_data.get("estimates")) if eps_ok else None
    revenue_direction = _direction(rev_data.get("estimates")) if rev_ok else None

    return {
        "eps_revision_direction": eps_direction,
        "revenue_revision_direction": revenue_direction,
    }, "real" if (eps_ok or rev_ok) else "degraded", None
