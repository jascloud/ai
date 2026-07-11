#!/usr/bin/env python3
"""
Phase 6 — Geopolitical risk index + commodity supply-disruption tracker
(oil/energy priority, per the requirement — the biggest SPX-relevant
macro lever among commodities).

Geopolitical risk: the Caldara-Iacoviello Geopolitical Risk (GPR) Index
is a real, public, academically-maintained index (Federal Reserve Board
economists; the current release is hosted as a plain data file, keyless,
no API). Historical GPR values average roughly 100 in calm periods and
have spiked into the 200-400+ range during major crises (Gulf War, 9/11,
the 2022 Ukraine invasion) — the elevated/crisis thresholds below are
set against that documented real distribution, not arbitrary numbers.

Oil supply disruption: EIA (U.S. Energy Information Administration,
EIA_API_KEY, free) WTI spot price series is used as a real proxy for
disruption — there is no clean "disruption alert" feed, so an abnormally
large short-window price move stands in for one, exactly like using
volume/open-interest ratios as an "unusual options activity" proxy in
Phase 7.
"""

import requests

from data_clients.base_client import BaseRealDataClient, DataClientError

GPR_ELEVATED_THRESHOLD = 150  # documented GPR historical average is ~100
GPR_CRISIS_THRESHOLD = 250    # documented GPR crisis-era peaks are 200-400+
OIL_DISRUPTION_PCT_THRESHOLD = 0.05  # >5% short-window move in WTI spot


class GPRIndexClient(BaseRealDataClient):
    API_KEY_ENV = None  # public data file, no key
    CACHE_NAMESPACE = "gpr_index"
    CACHE_TTL_SECONDS = 43200  # GPR updates monthly; 12h cache is plenty
    RATE_LIMIT_CALLS = 2
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self) -> dict:
        try:
            resp = requests.get(
                "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls",
                timeout=20,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"GPR index download failed: {e}") from e

        try:
            import io
            import pandas as pd
            df = pd.read_excel(io.BytesIO(resp.content))
        except Exception as e:
            raise DataClientError(f"GPR index file could not be parsed: {e}") from e

        if "GPR" not in df.columns:
            raise DataClientError("GPR index file did not contain expected 'GPR' column")

        latest_value = float(df["GPR"].dropna().iloc[-1])
        historical_mean = float(df["GPR"].dropna().mean())
        return {"latest_gpr": latest_value, "historical_mean_gpr": historical_mean}


class EIAPetroleumClient(BaseRealDataClient):
    API_KEY_ENV = "EIA_API_KEY"
    CACHE_NAMESPACE = "eia_petroleum"
    CACHE_TTL_SECONDS = 3600
    RATE_LIMIT_CALLS = 10
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self) -> dict:
        try:
            resp = requests.get(
                "https://api.eia.gov/v2/petroleum/pri/spt/data/",
                params={
                    "api_key": self.api_key,
                    "frequency": "daily",
                    "data[0]": "value",
                    "facets[series][]": "RWTC",  # WTI Cushing spot price
                    "sort[0][column]": "period",
                    "sort[0][direction]": "desc",
                    "length": 5,
                },
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"EIA petroleum price request failed: {e}") from e

        payload = resp.json()
        rows = payload.get("response", {}).get("data", [])
        if len(rows) < 2:
            raise DataClientError("EIA returned insufficient WTI spot price history")

        prices = [float(r["value"]) for r in rows if r.get("value") is not None]
        if len(prices) < 2:
            raise DataClientError("EIA WTI spot price rows had no usable values")

        return {"latest_price": prices[0], "prior_price": prices[-1]}


def get_geopolitical_risk_level() -> tuple:
    """Returns (risk_level, latest_gpr, data_source, reason).
    risk_level is one of 'normal'/'elevated'/'crisis'."""
    client = GPRIndexClient()
    data, source, reason = client.fetch()

    if source not in ("real", "cached_real") or not data:
        return None, None, "degraded", reason or "no GPR data returned"

    latest = data["latest_gpr"]
    if latest >= GPR_CRISIS_THRESHOLD:
        level = "crisis"
    elif latest >= GPR_ELEVATED_THRESHOLD:
        level = "elevated"
    else:
        level = "normal"

    return level, latest, source, None


def get_oil_disruption_signal() -> tuple:
    """Returns (disrupted: bool, pct_change, data_source, reason)."""
    client = EIAPetroleumClient()
    data, source, reason = client.fetch()

    if source not in ("real", "cached_real") or not data:
        return None, None, "degraded", reason or "no EIA data returned"

    pct_change = (data["latest_price"] - data["prior_price"]) / data["prior_price"]
    disrupted = abs(pct_change) > OIL_DISRUPTION_PCT_THRESHOLD
    return disrupted, pct_change, source, None
