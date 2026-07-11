#!/usr/bin/env python3
"""
Shared infrastructure for every real-data client added across Phases 1-6
of the momentum trading agent.

Every subclass of BaseRealDataClient gets, for free:
  - API key read from an environment variable (never hardcoded).
  - A per-instance rate limiter (sliding window).
  - Retry with exponential backoff on transient failures (network
    errors, 5xx, timeouts) — NOT retried on deliberate failures like a
    missing API key.
  - A local JSON file cache with a TTL, so repeated backtest runs don't
    re-hit the API for the same request (avoids burning quota).
  - A degraded-mode fallback: if the key is missing or the feed is down
    after retries, `fetch()` returns (None, "degraded", reason) instead
    of raising or crashing the caller. Callers are responsible for
    falling back to a clearly-labeled simulated/degraded rating — this
    layer never fabricates a "real" result.

This module has no dependency on any specific data vendor; Phase-specific
clients (data_clients/equity_quotes.py, etc.) subclass it and implement
`_fetch_live`.
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

CACHE_DIR = Path(
    os.environ.get(
        "MOMENTUM_DATA_CACHE_DIR",
        os.path.join(os.path.expanduser("~"), ".momentum_cache"),
    )
)


class DataClientError(Exception):
    """Raised internally by clients on a definitive failure (missing
    key, exhausted retries, unparseable response). Callers should catch
    this at the `fetch()` boundary and degrade — it should never
    propagate up and crash an agent's analyze() call."""


class RateLimiter:
    """Simple sliding-window rate limiter, process-local per client instance."""

    def __init__(self, max_calls: int, period_seconds: float):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self._calls = []

    def acquire(self) -> None:
        now = time.monotonic()
        self._calls = [t for t in self._calls if now - t < self.period_seconds]
        if len(self._calls) >= self.max_calls:
            sleep_for = self.period_seconds - (now - self._calls[0])
            if sleep_for > 0:
                time.sleep(sleep_for)
            now = time.monotonic()
            self._calls = [t for t in self._calls if now - t < self.period_seconds]
        self._calls.append(now)


class FileCache:
    """Local JSON cache keyed by a hash of the request parameters."""

    def __init__(self, namespace: str, ttl_seconds: int):
        self.dir = CACHE_DIR / namespace
        self.dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds

    def _path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode()).hexdigest()[:24]
        return self.dir / f"{digest}.json"

    def get(self, key: str) -> Optional[Any]:
        path = self._path(key)
        if not path.exists():
            return None
        try:
            with open(path) as f:
                payload = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
        if time.time() - payload.get("_cached_at", 0) > self.ttl_seconds:
            return None
        return payload.get("data")

    def set(self, key: str, data: Any) -> None:
        path = self._path(key)
        try:
            with open(path, "w") as f:
                json.dump({"_cached_at": time.time(), "data": data}, f)
        except OSError:
            pass  # cache write failures are non-fatal


def with_retry(func: Callable[[], Any], attempts: int = 3, base_delay: float = 1.0) -> Any:
    """Retries transient failures with exponential backoff. Deliberate
    DataClientError raises (e.g. missing key) are NOT retried — retrying
    those just wastes time reproducing the same guaranteed failure."""
    last_exc: Optional[Exception] = None
    for attempt in range(attempts):
        try:
            return func()
        except DataClientError:
            raise
        except Exception as e:  # noqa: BLE001 - intentionally broad: any network/client lib error degrades
            last_exc = e
            if attempt < attempts - 1:
                time.sleep(base_delay * (2 ** attempt))
    raise DataClientError(f"Failed after {attempts} attempts: {last_exc}") from last_exc


class BaseRealDataClient:
    """
    Subclasses set API_KEY_ENV / CACHE_NAMESPACE / CACHE_TTL_SECONDS /
    RATE_LIMIT_CALLS / RATE_LIMIT_PERIOD and implement `_fetch_live(**kwargs)`
    to perform the actual HTTP call, raising on any failure.

    `fetch(**kwargs)` wraps that with cache -> rate limit -> retry ->
    degraded-mode fallback, and is what agents should call.
    """

    API_KEY_ENV: Optional[str] = None
    CACHE_NAMESPACE = "generic"
    CACHE_TTL_SECONDS = 3600
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 60.0

    def __init__(self):
        self.api_key = os.environ.get(self.API_KEY_ENV) if self.API_KEY_ENV else "not_required"
        self.cache = FileCache(self.CACHE_NAMESPACE, self.CACHE_TTL_SECONDS)
        self.rate_limiter = RateLimiter(self.RATE_LIMIT_CALLS, self.RATE_LIMIT_PERIOD)

    def _cache_key(self, **kwargs) -> str:
        return f"{self.CACHE_NAMESPACE}:" + json.dumps(kwargs, sort_keys=True, default=str)

    def _fetch_live(self, **kwargs) -> Any:
        raise NotImplementedError

    def fetch(self, **kwargs) -> Tuple[Optional[Any], str, Optional[str]]:
        """
        Returns (data, data_source, error_reason).

        data_source is one of:
          - "real"        : fresh live fetch this call
          - "cached_real"  : served from local cache (was real when fetched)
          - "degraded"     : no data available; `data` is None and
                             `error_reason` explains why. Callers MUST
                             NOT treat this as real data.
        """
        cache_key = self._cache_key(**kwargs)

        if self.API_KEY_ENV and not self.api_key:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached, "cached_real", None
            return None, "degraded", f"{self.API_KEY_ENV} not set in environment"

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached, "cached_real", None

        try:
            self.rate_limiter.acquire()
            data = with_retry(lambda: self._fetch_live(**kwargs))
            self.cache.set(cache_key, data)
            return data, "real", None
        except DataClientError as e:
            return None, "degraded", str(e)
        except Exception as e:  # noqa: BLE001 - last-resort guard so a client bug can never crash an agent
            return None, "degraded", f"unexpected client error: {e}"


def required_env_keys(*client_classes) -> Dict[str, str]:
    """Collects {ENV_VAR: client_class_name} for every client that needs a key — used to build .env.example."""
    out = {}
    for cls in client_classes:
        if cls.API_KEY_ENV:
            out[cls.API_KEY_ENV] = cls.__name__
    return out
