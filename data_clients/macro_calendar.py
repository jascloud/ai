#!/usr/bin/env python3
"""
Phase 5 — Macro data: FOMC calendar + rate decisions, CPI/PCE/jobs
releases, and the 2s10s Treasury yield curve.

Real values (fed funds target rate, CPI/PCE/payrolls levels, 2Y/10Y
yields) come from FRED (Federal Reserve Economic Data, FRED_API_KEY) —
a free, official St. Louis Fed data API.

There is no free API that serves "next FOMC meeting date" or "next CPI
release date" directly — those are public-knowledge schedules the Fed/
BLS/BEA each publish years in advance on their own sites, not a
data-licensing API endpoint. This module pairs FRED's real released
values with a small, explicitly-maintained static calendar of those
publicly-announced dates (FOMC_MEETING_DATES_2026 /
MACRO_RELEASE_DATES_2026 below) — this is the same category of
situation as "TradingView has no OHLCV API" from market_data.py: the
schedule itself is public information, just not served through a REST
endpoint, so a maintained constant is the honest way to get it rather
than pretending a calendar API exists.
"""

from datetime import date, datetime

import requests

from data_clients.base_client import BaseRealDataClient, DataClientError

# Publicly-announced 2026 FOMC meeting dates (decision day of each
# 2-day meeting). Source: federalreserve.gov meeting calendar, published
# in advance. Update this list when the Fed publishes the next year's
# schedule — it is NOT fetched from an API because none exists for it.
FOMC_MEETING_DATES_2026 = [
    date(2026, 1, 28),
    date(2026, 3, 18),
    date(2026, 4, 29),
    date(2026, 6, 17),
    date(2026, 7, 29),
    date(2026, 9, 16),
    date(2026, 10, 28),
    date(2026, 12, 16),
]

# Approximate monthly release-day-of-month for CPI/PCE/jobs, per
# BLS/BEA's publicly-announced release calendars (exact days shift
# slightly month to month around these anchors).
MACRO_RELEASE_ANCHOR_DAY = {
    "CPI": 13,    # BLS CPI release, typically ~2nd week
    "PCE": 27,    # BEA PCE release, typically last week of month
    "JOBS": 5,    # BLS employment situation, first Friday-ish
}


class FREDSeriesClient(BaseRealDataClient):
    API_KEY_ENV = "FRED_API_KEY"
    CACHE_NAMESPACE = "fred_series"
    CACHE_TTL_SECONDS = 3600
    RATE_LIMIT_CALLS = 20
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, series_id: str, limit: int = 12) -> dict:
        try:
            resp = requests.get(
                "https://api.stlouisfed.org/fred/series/observations",
                params={
                    "series_id": series_id,
                    "api_key": self.api_key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": limit,
                },
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"FRED request failed for series {series_id}: {e}") from e

        payload = resp.json()
        observations = payload.get("observations")
        if not observations:
            raise DataClientError(f"FRED returned no observations for {series_id}: {payload.get('error_message')}")

        parsed = []
        for obs in observations:
            try:
                parsed.append({"date": obs["date"], "value": float(obs["value"])})
            except (ValueError, KeyError):
                continue  # FRED uses "." for missing values — skip, don't fabricate a number

        if not parsed:
            raise DataClientError(f"FRED returned only unparseable/missing observations for {series_id}")

        return {"series_id": series_id, "observations": parsed}


def get_yield_curve_spread() -> tuple:
    """2s10s spread (DGS10 - DGS2), in percentage points. Negative means
    inverted — a well-known recession-risk signal. Returns (spread,
    data_source, reason)."""
    client = FREDSeriesClient()
    ten_year, source_10, reason_10 = client.fetch(series_id="DGS10", limit=1)
    two_year, source_2, reason_2 = client.fetch(series_id="DGS2", limit=1)

    if source_10 not in ("real", "cached_real") or source_2 not in ("real", "cached_real"):
        return None, "degraded", f"DGS10: {reason_10}; DGS2: {reason_2}"

    spread = ten_year["observations"][0]["value"] - two_year["observations"][0]["value"]
    return spread, "real", None


def get_fed_funds_rate_trend() -> tuple:
    """Direction of the fed funds target rate ceiling (DFEDTARU) over its
    last two observations: 'up'/'down'/'flat'. Returns (direction, data_source, reason)."""
    client = FREDSeriesClient()
    data, source, reason = client.fetch(series_id="DFEDTARU", limit=2)

    if source not in ("real", "cached_real") or not data or len(data["observations"]) < 2:
        return None, "degraded", reason or "insufficient DFEDTARU observations"

    latest, prior = data["observations"][0]["value"], data["observations"][1]["value"]
    direction = "up" if latest > prior else "down" if latest < prior else "flat"
    return direction, source, None


def get_recent_macro_releases() -> tuple:
    """Most recent CPI (CPIAUCSL), PCE (PCEPI), and nonfarm payrolls
    (PAYEMS) month-over-month % change. Returns (releases, data_source,
    reason); a partial result (some series available) is tagged
    'real_partial'."""
    client = FREDSeriesClient()
    series_map = {"CPI": "CPIAUCSL", "PCE": "PCEPI", "JOBS": "PAYEMS"}
    releases = {}
    reasons = []

    for label, series_id in series_map.items():
        data, source, reason = client.fetch(series_id=series_id, limit=2)
        if source in ("real", "cached_real") and data and len(data["observations"]) >= 2:
            latest, prior = data["observations"][0]["value"], data["observations"][1]["value"]
            releases[label] = (latest - prior) / abs(prior) if prior else None
        else:
            reasons.append(f"{label}: {reason}")

    if not releases:
        return None, "degraded", "; ".join(reasons)

    data_source = "real" if len(releases) == len(series_map) else "real_partial"
    return releases, data_source, ("; ".join(reasons) if reasons else None)


def days_until_next_fomc_meeting(today: date = None) -> int:
    """Purely local calendar math against the static schedule above —
    not a network call, so it has no data_source/degraded concept."""
    today = today or date.today()
    upcoming = [d for d in FOMC_MEETING_DATES_2026 if d >= today]
    if not upcoming:
        return 999  # schedule exhausted (next year's dates not yet published)
    return (upcoming[0] - today).days


def days_since_last_fomc_meeting(today: date = None) -> int:
    today = today or date.today()
    past = [d for d in FOMC_MEETING_DATES_2026 if d <= today]
    if not past:
        return 999
    return (today - past[-1]).days
