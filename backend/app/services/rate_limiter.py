import time
from collections import defaultdict
import threading

class InMemoryRateLimiter:
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

    def clear(self) -> None:
        """Helper for unit tests to reset limits."""
        with self._lock:
            self._requests.clear()

limiter = InMemoryRateLimiter()
