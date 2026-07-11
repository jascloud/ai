#!/usr/bin/env python3
"""
Phase 2 — SEC filings parser (10-K/10-Q/8-K).

SEC EDGAR's XBRL company-facts API and full-text search are free and
keyless, but SEC's fair-use policy requires a descriptive User-Agent
header (e.g. "MyCompany contact@example.com") on every request — SEC
rate-limits/blocks generic or missing User-Agents more aggressively.
This client treats SEC_EDGAR_USER_AGENT as a required "key": unset means
degraded, exactly like a missing API key, because calling SEC without
one would be both against their policy and less reliable.

Extracts revenue and diluted EPS trend from XBRL company facts, plus a
simple keyword-based guidance-sentiment scan over recent 8-K full-text
search hits (a real 8-K-language classifier is future work — this pass
uses word presence, not fabricated sentiment).
"""

import requests

from data_clients.base_client import BaseRealDataClient, DataClientError

GUIDANCE_POSITIVE_WORDS = ("raised guidance", "increased guidance", "above expectations", "raises full-year")
GUIDANCE_NEGATIVE_WORDS = ("lowered guidance", "reduced guidance", "below expectations", "cuts full-year")


class SECTickerLookupClient(BaseRealDataClient):
    API_KEY_ENV = "SEC_EDGAR_USER_AGENT"
    CACHE_NAMESPACE = "sec_ticker_lookup"
    CACHE_TTL_SECONDS = 604800  # ticker->CIK mapping barely changes; cache a week
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 10.0

    def _fetch_live(self) -> dict:
        try:
            resp = requests.get(
                "https://www.sec.gov/files/company_tickers.json",
                headers={"User-Agent": self.api_key},
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"SEC ticker lookup request failed: {e}") from e
        return resp.json()


class SECCompanyFactsClient(BaseRealDataClient):
    API_KEY_ENV = "SEC_EDGAR_USER_AGENT"
    CACHE_NAMESPACE = "sec_company_facts"
    CACHE_TTL_SECONDS = 21600
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 10.0

    def _fetch_live(self, cik_padded: str) -> dict:
        try:
            resp = requests.get(
                f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json",
                headers={"User-Agent": self.api_key},
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"SEC company facts request failed for CIK{cik_padded}: {e}") from e
        return resp.json()


class SECFullTextSearchClient(BaseRealDataClient):
    API_KEY_ENV = "SEC_EDGAR_USER_AGENT"
    CACHE_NAMESPACE = "sec_full_text_search"
    CACHE_TTL_SECONDS = 3600
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 10.0

    def _fetch_live(self, symbol: str) -> dict:
        try:
            resp = requests.get(
                "https://efts.sec.gov/LATEST/search-index",
                params={"q": symbol, "forms": "8-K"},
                headers={"User-Agent": self.api_key},
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"SEC full-text search failed for {symbol}: {e}") from e
        return resp.json()


def _cik_for_symbol(symbol: str) -> tuple:
    client = SECTickerLookupClient()
    data, source, reason = client.fetch()
    if source not in ("real", "cached_real") or not data:
        return None, "degraded", reason or "no ticker map returned"

    for entry in data.values():
        if entry.get("ticker", "").upper() == symbol.upper():
            return str(entry["cik_str"]).zfill(10), source, None

    return None, "degraded", f"{symbol} not found in SEC ticker map"


def get_fundamentals_from_filings(symbol: str) -> tuple:
    """Returns (fundamentals, data_source, reason).
    fundamentals = {revenue_trend, eps_trend, guidance_sentiment}."""
    cik, cik_source, cik_reason = _cik_for_symbol(symbol)
    if cik is None:
        return None, "degraded", cik_reason

    facts_client = SECCompanyFactsClient()
    facts, facts_source, facts_reason = facts_client.fetch(cik_padded=cik)
    if facts_source not in ("real", "cached_real") or not facts:
        return None, "degraded", facts_reason or "no company facts returned"

    us_gaap = facts.get("facts", {}).get("us-gaap", {})

    def _latest_trend(tag_candidates):
        for tag in tag_candidates:
            entry = us_gaap.get(tag)
            if not entry:
                continue
            units = entry.get("units", {})
            for _, values in units.items():
                annual = [v for v in values if v.get("form") in ("10-K", "10-Q")]
                annual.sort(key=lambda v: v.get("end", ""))
                if len(annual) >= 2:
                    latest, prior = annual[-1]["val"], annual[-2]["val"]
                    if prior:
                        return (latest - prior) / abs(prior)
        return None

    revenue_trend = _latest_trend(["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"])
    eps_trend = _latest_trend(["EarningsPerShareDiluted"])

    search_client = SECFullTextSearchClient()
    search_data, search_source, search_reason = search_client.fetch(symbol=symbol)
    guidance_sentiment = "unknown"
    if search_source in ("real", "cached_real") and search_data:
        text_blob = " ".join(
            h.get("_source", {}).get("display_names", [""])[0].lower()
            for h in search_data.get("hits", {}).get("hits", [])
        )
        if any(w in text_blob for w in GUIDANCE_POSITIVE_WORDS):
            guidance_sentiment = "positive"
        elif any(w in text_blob for w in GUIDANCE_NEGATIVE_WORDS):
            guidance_sentiment = "negative"
        else:
            guidance_sentiment = "neutral"

    return {
        "revenue_trend_pct": revenue_trend,
        "eps_trend_pct": eps_trend,
        "guidance_sentiment": guidance_sentiment,
    }, facts_source, None
