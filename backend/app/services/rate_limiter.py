"""In-memory rate limiting for per-user actions and per-IP abuse protection."""
import time
from collections import defaultdict
import threading


class InMemoryRateLimiter:
    """Tracks (user_id, action) → timestamps for per-user rate limiting."""

    def __init__(self):
        # Maps (user_id, action) to a list of timestamps (floats)
        self._requests: dict[tuple[str, str], list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def is_rate_limited(self, user_id: str, action: str, limit_per_minute: int, limit_per_day: int) -> bool:
        now = time.time()
        key = (user_id, action)

        with self._lock:
            timestamps = self._requests[key]

            # 1. Clean up older timestamps (older than 1 day: 86400 seconds)
            cutoff_day = now - 86400.0
            timestamps = [t for t in timestamps if t > cutoff_day]

            # 2. Count in the last minute (60 seconds)
            cutoff_minute = now - 60.0
            requests_last_minute = sum(1 for t in timestamps if t > cutoff_minute)
            requests_last_day = len(timestamps)

            # 3. Check bounds
            if requests_last_minute >= limit_per_minute:
                # Update with current cleaned list before returning
                self._requests[key] = timestamps
                return True
            if requests_last_day >= limit_per_day:
                self._requests[key] = timestamps
                return True

            # 4. Record the request
            timestamps.append(now)
            self._requests[key] = timestamps
            return False

    def get_remaining(self, user_id: str, action: str, limit_per_minute: int, limit_per_day: int) -> dict:
        """Return remaining budget and retry-after seconds (0 if not limited).

        Keys:
          remaining_minute  – requests left in the current 60-second window
          remaining_daily   – requests left in the current 24-hour window
          retry_after       – seconds to wait before the oldest expiring request
                              opens a slot (0 when not limited)
        """
        now = time.time()
        key = (user_id, action)

        with self._lock:
            timestamps = self._requests.get(key, [])
            cutoff_day = now - 86400.0
            timestamps = [t for t in timestamps if t > cutoff_day]

            cutoff_minute = now - 60.0
            minute_timestamps = [t for t in timestamps if t > cutoff_minute]

            remaining_minute = max(0, limit_per_minute - len(minute_timestamps))
            remaining_daily = max(0, limit_per_day - len(timestamps))

            retry_after = 0.0
            if remaining_minute == 0 and minute_timestamps:
                # Oldest minute-window request: wait until it expires
                retry_after = max(0.0, minute_timestamps[0] - cutoff_minute)
            elif remaining_daily == 0 and timestamps:
                retry_after = max(0.0, timestamps[0] - cutoff_day)

            return {
                "remaining_minute": remaining_minute,
                "remaining_daily": remaining_daily,
                "retry_after": int(retry_after) + 1 if retry_after > 0 else 0,
            }

    def clear(self) -> None:
        """Helper for unit tests to reset limits."""
        with self._lock:
            self._requests.clear()


class GlobalIPLimiter:
    """Lightweight per-IP rate limiter for the global middleware.

    Uses a sliding-window counter: tracks timestamps per IP and rejects
    when the count in the last ``window_seconds`` exceeds ``max_requests``.
    """

    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0):
        self._max = max_requests
        self._window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def is_blocked(self, ip: str) -> tuple[bool, int]:
        """Check whether *ip* should be blocked.

        Returns ``(blocked, retry_after_seconds)``.
        """
        now = time.time()
        cutoff = now - self._window

        with self._lock:
            timestamps = self._hits[ip]
            timestamps = [t for t in timestamps if t > cutoff]

            if len(timestamps) >= self._max:
                self._hits[ip] = timestamps
                retry_after = int(timestamps[0] - cutoff) + 1 if timestamps else 1
                return True, retry_after

            timestamps.append(now)
            self._hits[ip] = timestamps
            return False, 0

    def update_limit(self, max_requests: int) -> None:
        """Allow dynamic reconfiguration (e.g. from settings reload)."""
        self._max = max_requests

    def clear(self) -> None:
        """Helper for unit tests."""
        with self._lock:
            self._hits.clear()


limiter = InMemoryRateLimiter()
