import time
import threading
from typing import Dict, List, Optional
from fastapi import Request, HTTPException, status
from app.core.config import settings


class RateLimiter:
    """
    Thread-safe in-memory sliding-window rate limiter for sensitive endpoints.
    Protects against credential stuffing, brute force, and denial of service.
    """

    def __init__(self, times: int = 10, seconds: int = 60, name: str = "default"):
        self.times = times
        self.seconds = seconds
        self.name = name
        self.requests: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def reset(self) -> None:
        """Clear all stored rate limit history (useful for test isolation)."""
        with self._lock:
            self.requests.clear()

    def __call__(self, request: Request) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return

        # Determine client identifier (IP or fallback)
        client_ip = request.client.host if request.client else "127.0.0.1"
        # Check X-Forwarded-For if behind a proxy
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        key = f"{self.name}:{client_ip}"
        now = time.time()
        window_start = now - self.seconds

        with self._lock:
            # Clean up old timestamps
            timestamps = [t for t in self.requests.get(key, []) if t > window_start]

            if len(timestamps) >= self.times:
                retry_after = int(timestamps[0] + self.seconds - now) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded for {self.name}. Maximum {self.times} requests per {self.seconds}s. Please retry in {retry_after}s.",
                    headers={"Retry-After": str(max(1, retry_after))},
                )

            timestamps.append(now)
            self.requests[key] = timestamps


# Pre-configured endpoint rate limiters
rate_limit_login = RateLimiter(times=settings.RATE_LIMIT_LOGIN_PER_MINUTE, seconds=60, name="login")
rate_limit_register = RateLimiter(times=settings.RATE_LIMIT_REGISTER_PER_MINUTE, seconds=60, name="register")
rate_limit_agent = RateLimiter(times=settings.RATE_LIMIT_AGENT_PER_MINUTE, seconds=60, name="agent")
rate_limit_upload = RateLimiter(times=settings.RATE_LIMIT_UPLOAD_PER_MINUTE, seconds=60, name="upload")
rate_limit_claim = RateLimiter(times=settings.RATE_LIMIT_CLAIM_PER_MINUTE, seconds=60, name="claim")
