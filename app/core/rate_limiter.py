from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Callable
from threading import Lock

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import settings


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def _cleanup(self, client_id: str, now: float) -> None:
        cutoff = now - self.window_seconds
        self._buckets[client_id] = [
            t for t in self._buckets[client_id] if t > cutoff
        ]
        if not self._buckets[client_id]:
            del self._buckets[client_id]

    def check(self, client_id: str) -> None:
        now = time.monotonic()
        with self._lock:
            self._cleanup(client_id, now)
            if len(self._buckets[client_id]) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later.",
                    headers={"Retry-After": str(int(self.window_seconds))},
                )
            self._buckets[client_id].append(now)

    def __call__(self, request: Request) -> None:
        if settings.is_development:
            return
        client_id = request.client.host if request.client else "unknown"
        self.check(client_id)


def rate_limit(
    max_requests: int = 10, window_seconds: int = 60
) -> Callable[[Request], None]:
    limiter = SlidingWindowRateLimiter(max_requests, window_seconds)
    return limiter
