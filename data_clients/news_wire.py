#!/usr/bin/env python3
"""
Phase 3 — Real-time news wire client.

Uses NewsAPI.org's /everything endpoint (NEWS_API_KEY), filtered by
ticker/company name, restricted to a recent lookback window so results
are actually "breaking" rather than historical background noise.
"""

from datetime import datetime, timedelta, timezone

import requests

from data_clients.base_client import BaseRealDataClient, DataClientError


class NewsAPIClient(BaseRealDataClient):
    API_KEY_ENV = "NEWS_API_KEY"
    CACHE_NAMESPACE = "newsapi_headlines"
    CACHE_TTL_SECONDS = 300  # 5 min — headlines should be reasonably fresh
    RATE_LIMIT_CALLS = 10
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, query: str, lookback_hours: int = 24) -> dict:
        since = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).isoformat()
        try:
            resp = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "from": since,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "apiKey": self.api_key,
                },
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"NewsAPI request failed for '{query}': {e}") from e

        payload = resp.json()
        if payload.get("status") != "ok":
            raise DataClientError(f"NewsAPI returned an error for '{query}': {payload.get('message')}")

        articles = payload.get("articles", [])
        return {
            "query": query,
            "headlines": [
                {
                    "title": a.get("title"),
                    "source": (a.get("source") or {}).get("name"),
                    "published_at": a.get("publishedAt"),
                    "url": a.get("url"),
                }
                for a in articles
            ],
        }


def get_recent_headlines(symbol: str, company_name: str = None, lookback_hours: int = 24) -> tuple:
    """Returns (headlines_data, data_source, reason). Queries by
    ticker + company name (when given) so results are relevant, not just
    any story mentioning the raw ticker string."""
    client = NewsAPIClient()
    query = f"{symbol} OR {company_name}" if company_name else symbol
    data, source, reason = client.fetch(query=query, lookback_hours=lookback_hours)

    if source not in ("real", "cached_real") or not data or not data.get("headlines"):
        return None, "degraded", reason or "no headlines returned"

    return data, source, None
