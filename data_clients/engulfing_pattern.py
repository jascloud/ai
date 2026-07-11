#!/usr/bin/env python3
"""
Engulfing candlestick pattern detection on 5-minute bars.

Detects bullish/bearish engulfing patterns during regular trading hours (9:30-16:00 ET).
Returns pattern signals (bullish/bearish/none) with confidence based on volume and SMA confirmation.
"""

import requests
from datetime import datetime, timezone
from typing import Tuple, Optional, List, Dict, Any

from data_clients.base_client import BaseRealDataClient, DataClientError


class PolygonIntraday5MinClient(BaseRealDataClient):
    """Pulls 5-minute OHLCV bars from Polygon for a given symbol and date range."""
    API_KEY_ENV = "POLYGON_API_KEY"
    CACHE_NAMESPACE = "polygon_5min_bars"
    CACHE_TTL_SECONDS = 300  # 5 minutes (intraday data changes rapidly)
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, symbol: str, start_date: str, end_date: str) -> dict:
        """
        Fetch 5-min bars from Polygon (start_date and end_date as YYYY-MM-DD).
        Returns sorted list ascending by timestamp.
        """
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/5/minute/{start_date}/{end_date}"
        try:
            resp = requests.get(
                url,
                params={"apiKey": self.api_key, "sort": "asc", "limit": 50000},
                timeout=20,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"Polygon 5-min bars request failed for {symbol}: {e}") from e

        payload = resp.json()
        results = payload.get("results", [])
        if not results:
            raise DataClientError(f"Polygon returned no 5-min bars for {symbol}")

        bars = [
            {
                "timestamp": r["t"],
                "open": r["o"],
                "high": r["h"],
                "low": r["l"],
                "close": r["c"],
                "volume": r.get("v", 0),
            }
            for r in results
        ]
        return {"symbol": symbol, "bars": bars}


def is_regular_hours(timestamp_ms: int) -> bool:
    """Check if timestamp falls within regular trading hours (9:30-16:00 ET)."""
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    # Convert to ET
    et_offset = -4  # EDT offset (UTC-4)
    et_hour = (dt.hour + et_offset) % 24
    et_minute = dt.minute

    # Regular hours: 9:30-16:00 ET
    if et_hour < 9:
        return False
    if et_hour == 9 and et_minute < 30:
        return False
    if et_hour >= 16:
        return False
    return True


def detect_engulfing_pattern(
    bars: List[Dict[str, Any]],
    body_ratio_threshold: float = 1.0,
    volume_multiplier: float = 1.2,
    sma_period: int = 20,
    use_volume_confirmation: bool = True,
    use_sma_confirmation: bool = True,
) -> List[Dict[str, Any]]:
    """
    Detect engulfing patterns in a list of 5-min bars.

    Args:
        bars: List of bar dicts with keys: timestamp, open, high, low, close, volume
        body_ratio_threshold: Min body size ratio (N/N-1) for engulfing, default 1.0
        volume_multiplier: Volume confirmation multiplier (>= 1.2x 20-bar avg), default 1.2
        sma_period: SMA period for directional confirmation, default 20
        use_volume_confirmation: Apply volume filter, default True
        use_sma_confirmation: Apply SMA directional filter, default True

    Returns:
        List of dicts with keys:
        - timestamp: bar timestamp
        - pattern_type: 'bullish_engulfing' or 'bearish_engulfing' or 'none'
        - confidence: float 0.0-1.0
        - body_size_n: current bar body size
        - body_size_n_1: previous bar body size
        - volume_check: True if volume >= threshold
        - sma_check: True if above/below SMA as appropriate
    """
    if len(bars) < 2:
        return []

    results = []

    # Compute 20-bar rolling SMA and volume average
    sma_values = []
    vol_averages = []

    for i in range(len(bars)):
        if i < sma_period:
            sma_values.append(None)
            vol_averages.append(None)
        else:
            lookback_closes = [b["close"] for b in bars[i - sma_period : i]]
            sma = sum(lookback_closes) / len(lookback_closes)
            sma_values.append(sma)

            lookback_vols = [b["volume"] for b in bars[i - sma_period : i]]
            vol_avg = sum(lookback_vols) / len(lookback_vols) if lookback_vols else 0
            vol_averages.append(vol_avg)

    for i in range(1, len(bars)):
        bar_n_1 = bars[i - 1]
        bar_n = bars[i]

        # Skip if outside regular hours
        if not is_regular_hours(bar_n["timestamp"]):
            results.append(
                {
                    "timestamp": bar_n["timestamp"],
                    "pattern_type": "none",
                    "confidence": 0.0,
                    "body_size_n": 0,
                    "body_size_n_1": 0,
                    "volume_check": False,
                    "sma_check": False,
                    "reason": "outside_regular_hours",
                }
            )
            continue

        # Compute body sizes
        body_n_1 = abs(bar_n_1["close"] - bar_n_1["open"])
        body_n = abs(bar_n["close"] - bar_n["open"])

        volume_check = False
        if use_volume_confirmation and vol_averages[i] is not None:
            volume_check = bar_n["volume"] >= (vol_averages[i] * volume_multiplier)
        elif not use_volume_confirmation:
            volume_check = True

        sma_check = True  # default pass
        sma_value = sma_values[i] if i < len(sma_values) else None

        # Bullish engulfing
        is_bullish_engulfing = (
            bar_n_1["close"] < bar_n_1["open"]  # N-1 is bearish (down candle)
            and bar_n["close"] > bar_n["open"]  # N is bullish (up candle)
            and bar_n["open"] <= bar_n_1["close"]  # N's open <= N-1's close
            and bar_n["close"] >= bar_n_1["open"]  # N's close >= N-1's open
            and body_n >= (body_n_1 * body_ratio_threshold)
        )

        # Bearish engulfing
        is_bearish_engulfing = (
            bar_n_1["close"] > bar_n_1["open"]  # N-1 is bullish (up candle)
            and bar_n["close"] < bar_n["open"]  # N is bearish (down candle)
            and bar_n["open"] >= bar_n_1["close"]  # N's open >= N-1's close
            and bar_n["close"] <= bar_n_1["open"]  # N's close <= N-1's open
            and body_n >= (body_n_1 * body_ratio_threshold)
        )

        pattern_type = "none"
        sma_check = True

        if is_bullish_engulfing:
            pattern_type = "bullish_engulfing"
            if use_sma_confirmation and sma_value is not None:
                sma_check = bar_n["close"] >= sma_value  # bullish engulfing above SMA

        elif is_bearish_engulfing:
            pattern_type = "bearish_engulfing"
            if use_sma_confirmation and sma_value is not None:
                sma_check = bar_n["close"] <= sma_value  # bearish engulfing below SMA

        # Confidence: volume check + SMA check + body ratio premium
        confidence = 0.0
        if pattern_type != "none":
            confidence = 0.5  # base confidence
            if volume_check:
                confidence += 0.25
            if sma_check:
                confidence += 0.25

        results.append(
            {
                "timestamp": bar_n["timestamp"],
                "pattern_type": pattern_type,
                "confidence": confidence,
                "body_size_n": body_n,
                "body_size_n_1": body_n_1,
                "volume_check": volume_check,
                "sma_check": sma_check,
                "reason": None if pattern_type != "none" else "no_pattern",
            }
        )

    return results


def get_engulfing_patterns_for_period(
    symbol: str,
    start_date: str,
    end_date: str,
    body_ratio_threshold: float = 1.0,
    volume_multiplier: float = 1.2,
) -> Tuple[Optional[List[Dict[str, Any]]], str, Optional[str]]:
    """
    Fetch 5-min bars and detect engulfing patterns.

    Returns: (patterns_list, data_source, error_reason)
    data_source: 'real', 'cached_real', or 'degraded'
    """
    client = PolygonIntraday5MinClient()
    data, source, reason = client.fetch(
        symbol=symbol, start_date=start_date, end_date=end_date
    )

    if source in ("real", "cached_real") and data:
        bars = data.get("bars", [])
        patterns = detect_engulfing_pattern(
            bars,
            body_ratio_threshold=body_ratio_threshold,
            volume_multiplier=volume_multiplier,
            use_volume_confirmation=True,
            use_sma_confirmation=True,
        )
        return patterns, source, None
    else:
        return None, source, reason or "Failed to fetch 5-min bars"
