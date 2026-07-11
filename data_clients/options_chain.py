#!/usr/bin/env python3
"""
Phase 1 — SPX/SPY options chain + Greeks client.

Also the data source Phase 7 uses to repoint Bull/Bear Researcher onto
real unusual-options-activity / put-call-ratio signals instead of
random generation.
"""

import requests

from data_clients.base_client import BaseRealDataClient, DataClientError


class PolygonOptionsChainClient(BaseRealDataClient):
    API_KEY_ENV = "POLYGON_API_KEY"
    CACHE_NAMESPACE = "polygon_options_chain"
    CACHE_TTL_SECONDS = 300  # options chains don't need to be fresher than 5 min for this use case
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, underlying: str = "SPY") -> dict:
        url = f"https://api.polygon.io/v3/snapshot/options/{underlying}"
        try:
            resp = requests.get(url, params={"apiKey": self.api_key, "limit": 250}, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"Polygon options chain request failed for {underlying}: {e}") from e

        payload = resp.json()
        results = payload.get("results")
        if not results:
            raise DataClientError(f"Polygon returned no options chain for {underlying}: {payload.get('status')}")

        contracts = []
        for r in results:
            details = r.get("details", {})
            greeks = r.get("greeks", {})
            day = r.get("day", {})
            contracts.append({
                "contract_type": details.get("contract_type"),  # 'call' or 'put'
                "strike": details.get("strike_price"),
                "expiration": details.get("expiration_date"),
                "delta": greeks.get("delta"),
                "gamma": greeks.get("gamma"),
                "theta": greeks.get("theta"),
                "vega": greeks.get("vega"),
                "implied_volatility": r.get("implied_volatility"),
                "volume": day.get("volume"),
                "open_interest": r.get("open_interest"),
            })

        return {"underlying": underlying, "contracts": contracts}


def get_options_chain(underlying: str = "SPY") -> tuple:
    client = PolygonOptionsChainClient()
    return client.fetch(underlying=underlying)


def summarize_options_flow(chain: dict) -> dict:
    """Reduces a raw options chain into the signals Phase 7 needs:
    put/call volume ratio, call-side skew (unusual call volume vs open
    interest, a bullish-flow proxy), and put-side skew (unusual put
    volume vs open interest, a hedging-demand/bearish-flow proxy).

    Returns None if the chain has no usable contracts — callers must
    treat that as "no signal available", not "neutral signal"."""
    contracts = chain.get("contracts", []) if chain else []
    calls = [c for c in contracts if c.get("contract_type") == "call" and c.get("volume") is not None]
    puts = [c for c in contracts if c.get("contract_type") == "put" and c.get("volume") is not None]

    if not calls and not puts:
        return None

    call_volume = sum(c["volume"] for c in calls)
    put_volume = sum(c["volume"] for c in puts)
    total_volume = call_volume + put_volume

    if total_volume == 0:
        return None

    put_call_ratio = put_volume / call_volume if call_volume > 0 else float("inf")

    def _unusual_skew(contracts_side):
        # volume/open_interest > 1 means today's volume already exceeds
        # standing open interest — a classic "unusual activity" proxy.
        ratios = [
            c["volume"] / c["open_interest"]
            for c in contracts_side
            if c.get("open_interest") not in (None, 0) and c.get("volume") is not None
        ]
        return max(ratios) if ratios else 0.0

    return {
        "call_volume": call_volume,
        "put_volume": put_volume,
        "put_call_ratio": put_call_ratio,
        "call_skew": _unusual_skew(calls),
        "put_skew": _unusual_skew(puts),
    }
