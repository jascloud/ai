#!/usr/bin/env python3
"""
Real market data fetching for S&P 500 momentum backtesting.

TradingView has no public REST API for historical OHLCV data — it is a
charting/broker-integration product, not a data-licensing API. The real
data sources wired in here, tried in order:

  1. Local cache file (MOMENTUM_PRICE_CACHE_FILE, default
     market_data_cache.json if present) - real closes fetched by whoever
     is orchestrating a run (e.g. via an MCP broker connector such as
     Interactive Brokers) and written to disk in the format
     {"SYMBOL": {"dates": [...], "closes": [...]}, ...}. Useful when this
     process has no direct outbound HTTPS to a data vendor, but something
     upstream does.
  2. Alpha Vantage (requires ALPHA_VANTAGE_API_KEY)
  3. Yahoo Finance via yfinance (no key required, but the host must be
     reachable from wherever this runs)

This module never fabricates data. Every failure raises MarketDataError
with the specific cause so callers can report it and stop, instead of
silently falling back to randomly generated prices.
"""

import json
import os
import time
from typing import Dict, List, Tuple

import requests

DEFAULT_CACHE_FILE = "market_data_cache.json"


class MarketDataError(Exception):
    """Raised when real market data cannot be fetched or is insufficient."""


def _fetch_from_cache_file(symbol: str, lookback_days: int) -> List[float]:
    dates, closes = _fetch_from_cache_file_with_dates(symbol, lookback_days)
    return closes


def _fetch_from_cache_file_with_dates(symbol: str, lookback_days: int) -> "Tuple[List[str], List[float]]":
    cache_path = os.environ.get("MOMENTUM_PRICE_CACHE_FILE", DEFAULT_CACHE_FILE)
    if not os.path.isfile(cache_path):
        raise MarketDataError(f"Cache file not found: {cache_path}")

    try:
        with open(cache_path) as f:
            cache = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise MarketDataError(f"Could not read cache file {cache_path}: {e}") from e

    entry = cache.get(symbol)
    if not entry or "closes" not in entry:
        raise MarketDataError(f"No cached data for {symbol} in {cache_path}")

    closes = [float(c) for c in entry["closes"]]
    if len(closes) < 30:
        raise MarketDataError(f"Cache file has only {len(closes)} days for {symbol} (need >= 30)")

    raw_dates = entry.get("dates")
    if not raw_dates or len(raw_dates) != len(closes):
        raise MarketDataError(f"Cache file for {symbol} is missing a 'dates' array aligned to 'closes'")

    if len(closes) > lookback_days:
        return raw_dates[-lookback_days:], closes[-lookback_days:]
    return raw_dates, closes


def _fetch_alpha_vantage(symbol: str, api_key: str, lookback_days: int) -> List[float]:
    dates, closes = _fetch_alpha_vantage_with_dates(symbol, api_key, lookback_days)
    return closes


def _fetch_alpha_vantage_with_dates(symbol: str, api_key: str, lookback_days: int) -> Tuple[List[str], List[float]]:
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
    if len(closes) > lookback_days:
        return dates_sorted[-lookback_days:], closes[-lookback_days:]
    return dates_sorted, closes


def _fetch_yfinance(symbol: str, lookback_days: int) -> List[float]:
    dates, closes = _fetch_yfinance_with_dates(symbol, lookback_days)
    return closes


def _fetch_yfinance_with_dates(symbol: str, lookback_days: int) -> Tuple[List[str], List[float]]:
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

    hist = hist["Close"].dropna()
    dates = [ts.strftime("%Y-%m-%d") for ts in hist.index]
    closes = hist.tolist()
    return dates, closes


def fetch_price_history(symbol: str, lookback_days: int = 180) -> List[float]:
    """Fetch real daily closing prices for one symbol.

    Tries, in order: a local cache file (MOMENTUM_PRICE_CACHE_FILE /
    market_data_cache.json), then Alpha Vantage (if ALPHA_VANTAGE_API_KEY
    is set), then Yahoo Finance. Raises MarketDataError with every
    attempted-source failure reason if none works — never fabricates
    data as a fallback.
    """
    errors = []

    try:
        return _fetch_from_cache_file(symbol, lookback_days)
    except MarketDataError as e:
        errors.append(str(e))

    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
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


def fetch_price_history_with_dates(symbol: str, lookback_days: int = 180) -> Tuple[List[str], List[float]]:
    """Same source-fallback chain as fetch_price_history, but also returns
    the calendar date (YYYY-MM-DD) for each close, parallel-indexed.

    Needed to align daily backtest bars with real intraday (5-min)
    engulfing pattern data, which is keyed by calendar date, not by a
    bare trading-day index. Never fabricates dates: each source's real
    date field is threaded straight through instead of being synthesized
    from lookback_days (which would drift across weekends/holidays).
    """
    errors = []

    try:
        return _fetch_from_cache_file_with_dates(symbol, lookback_days)
    except MarketDataError as e:
        errors.append(str(e))

    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if api_key:
        try:
            dates, closes = _fetch_alpha_vantage_with_dates(symbol, api_key, lookback_days)
            if len(closes) >= 30:
                return dates, closes
            errors.append(f"Alpha Vantage returned only {len(closes)} days (need >= 30)")
        except MarketDataError as e:
            errors.append(str(e))
    else:
        errors.append("ALPHA_VANTAGE_API_KEY not set, skipped")

    try:
        dates, closes = _fetch_yfinance_with_dates(symbol, lookback_days)
        if len(closes) >= 30:
            return dates, closes
        errors.append(f"yfinance returned only {len(closes)} days (need >= 30)")
    except MarketDataError as e:
        errors.append(str(e))

    raise MarketDataError(
        f"Could not fetch real market data (with dates) for {symbol} from any configured source. "
        f"Attempts: {'; '.join(errors)}."
    )


def fetch_sp500_universe_with_dates(
    symbols: List[str],
    lookback_days: int = 180,
    rate_limit_delay: float = 0.0,
) -> Dict[str, Tuple[List[str], List[float]]]:
    """Date-aware counterpart to fetch_sp500_universe. Returns
    {symbol: (dates, closes)}. Fails loudly on any symbol, same as the
    non-dated version."""
    data: Dict[str, Tuple[List[str], List[float]]] = {}
    errors: Dict[str, str] = {}

    for symbol in symbols:
        try:
            data[symbol] = fetch_price_history_with_dates(symbol, lookback_days)
        except MarketDataError as e:
            errors[symbol] = str(e)
        if rate_limit_delay:
            time.sleep(rate_limit_delay)

    if errors:
        raise MarketDataError(
            "Failed to fetch real market data (with dates) for one or more symbols:\n"
            + "\n".join(f"  - {sym}: {msg}" for sym, msg in errors.items())
        )

    return data
