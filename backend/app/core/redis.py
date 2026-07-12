"""Redis client (shared by Celery broker + direct use).

Used for short-lived, ephemeral data such as email verification codes, where
native TTL expiry is a better fit than writing rows to PostgreSQL.
"""

from __future__ import annotations

from typing import Any

from app.core.config import settings

_client: Any = None


def get_redis() -> Any:
    """Return a shared Redis client (decoded responses -> str, not bytes)."""
    global _client
    if _client is None:
        import redis  # local import keeps import-time cost off the test path

        _client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _client
