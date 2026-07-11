#!/usr/bin/env python3
"""
Real market data fetching for S&P 500 momentum backtesting.

TradingView has no public REST API for historical OHLCV data — it is a
charting/broker-integration product, not a data-licensing API. The real
data sources wired in here are:

  1. Alpha Vantage (primary) - requires ALPHA_VANTAGE_API_KEY
  2. Yahoo Finance via yfinance (fallback) - no key required, but the host
     must be reachable from wherever this runs

This module never fabricates data. Every failure raises MarketDataError
with the specific cause so callers can report it and stop, instead of
silently falling back to randomly generated prices.
"""

import os
import time
from typing import Dict, List

import requests


class MarketDataError(Exception):
    """Raised when real market data cannot be fetched or is insufficient."""


def _fetch_alpha_vantage(symbol: str, api_key: str, lookback_days: int) -> List[float]:
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "full" if lookback_days > 100 else "compact",
        "apikey": api_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise MarketDataError(f"Alpha Vantage request failed for {symbol}: {e}") from e

    data = resp.json()
    series = data.get("Time Series (Daily)")
    if not series:
        note = data.get("Note") or data.get("Information") or data.get("Error Message") or data
        raise MarketDataError(f"Alpha Vantage returned no data for {symbol}: {note}")

    dates_sorted = sorted(series.keys())
    closes = [float(series[d]["4. close"]) for d in dates_sorted]
    return closes[-lookback_days:] if len(closes) > lookback_days else closes


def _fetch_yfinance(symbol: str, lookback_days: int) -> List[float]:
    try:
        import yfinance as yf
    except ImportError as e:
        raise MarketDataError("yfinance not installed. Run: pip install yfinance") from e

    try:
        hist = yf.Ticker(symbol).history(period=f"{lookback_days}d", interval="1d", auto_adjust=True)
    except Exception as e:
        raise MarketDataError(f"yfinance request failed for {symbol}: {e}") from e

    if hist is None or hist.empty or "Close" not in hist:
        raise MarketDataError(f"yfinance returned no data for {symbol}")

    return hist["Close"].dropna().tolist()


def fetch_price_history(symbol: str, lookback_days: int = 180) -> List[float]:
    """Fetch real daily closing prices for one symbol.

    Tries Alpha Vantage first (if ALPHA_VANTAGE_API_KEY is set), then
    falls back to Yahoo Finance. Raises MarketDataError with every
    attempted-source failure reason if neither works — never fabricates
    data as a fallback.
    """
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    errors = []

    if api_key:
        try:
            closes = _fetch_alpha_vantage(symbol, api_key, lookback_days)
            if len(closes) >= 30:
                return closes
            errors.append(f"Alpha Vantage returned only {len(closes)} days (need >= 30)")
        except MarketDataError as e:
            errors.append(str(e))
    else:
        errors.append("ALPHA_VANTAGE_API_KEY not set, skipped")

    try:
        closes = _fetch_yfinance(symbol, lookback_days)
        if len(closes) >= 30:
            return closes
        errors.append(f"yfinance returned only {len(closes)} days (need >= 30)")
    except MarketDataError as e:
        errors.append(str(e))

    raise MarketDataError(
        f"Could not fetch real market data for {symbol} from any configured source. "
        f"Attempts: {'; '.join(errors)}. "
        f"Set ALPHA_VANTAGE_API_KEY, confirm outbound network access to the data "
        f"provider is permitted for this environment, and confirm the symbol is valid."
    )


def fetch_sp500_universe(
    symbols: List[str],
    lookback_days: int = 180,
    rate_limit_delay: float = 0.0,
) -> Dict[str, List[float]]:
    """Fetch real price history for a list of symbols.

    Fails loudly: if any symbol cannot be fetched, raises MarketDataError
    listing every failure. Never returns a partial result silently padded
    with fake data.
    """
    data: Dict[str, List[float]] = {}
    errors: Dict[str, str] = {}

    for symbol in symbols:
        try:
            data[symbol] = fetch_price_history(symbol, lookback_days)
        except MarketDataError as e:
            errors[symbol] = str(e)
        if rate_limit_delay:
            time.sleep(rate_limit_delay)

    if errors:
        raise MarketDataError(
            "Failed to fetch real market data for one or more symbols:\n"
            + "\n".join(f"  - {sym}: {msg}" for sym, msg in errors.items())
        )

    return data
