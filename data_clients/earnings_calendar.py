#!/usr/bin/env python3
"""
Phase 2 — Earnings calendar + surprise history.

Uses Alpha Vantage's EARNINGS endpoint (reuses ALPHA_VANTAGE_API_KEY,
already required for Technical Analyst's price data — no new key for
this one) to get the next earnings date and the last several quarters'
EPS surprise history (reported vs estimated EPS).
"""

import requests

from data_clients.base_client import BaseRealDataClient, DataClientError


class AlphaVantageEarningsClient(BaseRealDataClient):
    API_KEY_ENV = "ALPHA_VANTAGE_API_KEY"
    CACHE_NAMESPACE = "av_earnings"
    CACHE_TTL_SECONDS = 21600  # 6 hours; earnings calendars don't change intraday
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, symbol: str) -> dict:
        url = "https://www.alphavantage.co/query"
        params = {"function": "EARNINGS", "symbol": symbol, "apikey": self.api_key}
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"Alpha Vantage earnings request failed for {symbol}: {e}") from e

        payload = resp.json()
        quarterly = payload.get("quarterlyEarnings")
        if not quarterly:
            note = payload.get("Note") or payload.get("Information") or payload.get("Error Message") or payload
            raise DataClientError(f"Alpha Vantage returned no earnings data for {symbol}: {note}")

        return {"symbol": symbol, "quarterly_earnings": quarterly}


def get_earnings_surprise_history(symbol: str, lookback_quarters: int = 4) -> tuple:
    """Returns (surprises, data_source, reason). `surprises` is a list of
    {reported_eps, estimated_eps, surprise_pct} for the most recent
    quarters, most recent first. None on degraded."""
    client = AlphaVantageEarningsClient()
    data, source, reason = client.fetch(symbol=symbol)

    if source not in ("real", "cached_real") or not data:
        return None, "degraded", reason or "no earnings data returned"

    quarters = data.get("quarterly_earnings", [])[:lookback_quarters]
    surprises = []
    for q in quarters:
        try:
            reported = float(q.get("reportedEPS")) if q.get("reportedEPS") not in (None, "None") else None
            estimated = float(q.get("estimatedEPS")) if q.get("estimatedEPS") not in (None, "None") else None
            surprise_pct = float(q.get("surprisePercentage")) if q.get("surprisePercentage") not in (None, "None") else None
        except (ValueError, TypeError):
            continue
        surprises.append({
            "fiscal_date_ending": q.get("fiscalDateEnding"),
            "reported_eps": reported,
            "estimated_eps": estimated,
            "surprise_pct": surprise_pct,
        })

    if not surprises:
        return None, "degraded", "earnings data returned but no parseable quarters"

    return surprises, source, None
