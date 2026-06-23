"""Round-robin NVIDIA NIM API key pool for parallel throughput.

Each outbound LLM call acquires the next key so concurrent requests (and
Gunicorn workers starting at different offsets) spread load across keys.
Per-key RPM throttling keeps bulk jobs under NVIDIA's ~40 RPM cap.
On rate-limit errors the caller retries with the remaining keys in the pool.
"""
from __future__ import annotations

import itertools
import logging
import os
import threading
import time
from collections import defaultdict
from typing import TYPE_CHECKING

from openai import OpenAI

if TYPE_CHECKING:
    from ..config import Settings

logger = logging.getLogger(__name__)

_pool: "NvidiaKeyPool | None" = None
_pool_lock = threading.Lock()


class _KeyRateLimiter:
    """Sliding 60s window + minimum spacing per API key."""

    def __init__(self, rpm: float) -> None:
        self._rpm = max(1.0, rpm)
        self._min_interval = 60.0 / self._rpm
        self._lock = threading.Lock()
        self._timestamps: dict[str, list[float]] = defaultdict(list)
        self._last_sent: dict[str, float] = {}
        self._cooldown_until: dict[str, float] = {}

    @property
    def rpm(self) -> float:
        return self._rpm

    def acquire(self, api_key: str) -> float:
        """Block until this key may send a request. Returns seconds waited."""
        waited = 0.0
        while True:
            with self._lock:
                now = time.monotonic()
                cooldown = self._cooldown_until.get(api_key, 0.0)
                if now < cooldown:
                    sleep_for = cooldown - now
                else:
                    window = self._timestamps[api_key]
                    window[:] = [t for t in window if now - t < 60.0]
                    last = self._last_sent.get(api_key, 0.0)
                    spacing = self._min_interval - (now - last)
                    if len(window) >= int(self._rpm):
                        sleep_for = 60.0 - (now - window[0]) + 0.05
                    elif spacing > 0:
                        sleep_for = spacing
                    else:
                        self._last_sent[api_key] = now
                        window.append(now)
                        return waited

            chunk = min(max(sleep_for, 0.05), 2.0)
            time.sleep(chunk)
            waited += chunk

    def note_rate_limit(self, api_key: str, retry_after_sec: float | None = None) -> None:
        cooldown = retry_after_sec if retry_after_sec and retry_after_sec > 0 else 60.0
        with self._lock:
            self._cooldown_until[api_key] = time.monotonic() + cooldown


class NvidiaKeyPool:
    def __init__(self, keys: list[str], base_url: str, *, rpm: float = 35.0) -> None:
        if not keys:
            raise ValueError("NvidiaKeyPool requires at least one API key")
        self._keys = keys
        self._base_url = base_url.rstrip("/")
        if self._base_url.endswith("/v1a"):
            self._base_url = self._base_url[:-1]
        self._rpm = rpm
        self._limiter = _KeyRateLimiter(rpm)
        self._counter = itertools.count(os.getpid())
        self._rotate_lock = threading.Lock()
        self._clients: dict[str, OpenAI] = {}
        self._clients_lock = threading.Lock()

    @property
    def size(self) -> int:
        return len(self._keys)

    @property
    def rpm_per_key(self) -> float:
        return self._rpm

    def keys_starting_next(self) -> list[str]:
        """All keys rotated so parallel callers pick different starting keys."""
        with self._rotate_lock:
            start = next(self._counter) % len(self._keys)
        return self._keys[start:] + self._keys[:start]

    def acquire_before_request(self, api_key: str) -> float:
        return self._limiter.acquire(api_key)

    def note_rate_limit(self, api_key: str, retry_after_sec: float | None = None) -> None:
        self._limiter.note_rate_limit(api_key, retry_after_sec)

    def client(self, api_key: str) -> OpenAI:
        with self._clients_lock:
            cached = self._clients.get(api_key)
            if cached is None:
                cached = OpenAI(base_url=self._base_url, api_key=api_key)
                self._clients[api_key] = cached
            return cached


def nvidia_api_keys_from_settings(settings: Settings) -> list[str]:
    if settings.nvidia_api_keys.strip():
        keys = [k.strip() for k in settings.nvidia_api_keys.split(",") if k.strip()]
        if keys:
            return keys
    if settings.nvidia_api_key.strip():
        return [settings.nvidia_api_key.strip()]
    return []


def get_nvidia_key_pool() -> NvidiaKeyPool | None:
    global _pool
    from ..config import settings

    keys = nvidia_api_keys_from_settings(settings)
    if not keys:
        return None

    base_url = settings.nvidia_base_url.strip().rstrip("/")
    rpm = float(settings.nvidia_rpm_per_key)

    with _pool_lock:
        if (
            _pool is None
            or _pool._keys != keys
            or _pool._base_url != base_url
            or _pool.rpm_per_key != rpm
        ):
            _pool = NvidiaKeyPool(keys, settings.nvidia_base_url, rpm=rpm)
        return _pool


def reset_nvidia_key_pool() -> None:
    """Clear cached pool (tests / settings reload)."""
    global _pool
    with _pool_lock:
        _pool = None
