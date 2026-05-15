"""
Optional Redis cache — degrades gracefully when Redis is unavailable.
"""

from __future__ import annotations

import json
import logging
import os
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

_redis_client = None
_redis_checked = False


def get_redis():
    global _redis_client, _redis_checked
    if _redis_checked:
        return _redis_client
    _redis_checked = True
    url = os.getenv("REDIS_URL", "")
    if not url:
        return None
    try:
        import redis
        _redis_client = redis.from_url(url, decode_responses=True, socket_connect_timeout=2)
        _redis_client.ping()
        logger.info("Redis cache connected")
    except Exception as exc:
        logger.info("Redis unavailable — caching disabled: %s", exc)
        _redis_client = None
    return _redis_client


def cache_get(key: str) -> Optional[Any]:
    client = get_redis()
    if not client:
        return None
    try:
        raw = client.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None


def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    client = get_redis()
    if not client:
        return
    try:
        client.setex(key, ttl_seconds, json.dumps(value))
    except Exception:
        pass


def cached(prefix: str, ttl_seconds: int = 300):
    """Decorator for caching function results by argument hash."""

    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = f"{prefix}:{hash((args, tuple(sorted(kwargs.items()))))}"
            hit = cache_get(key)
            if hit is not None:
                return hit
            result = fn(*args, **kwargs)
            cache_set(key, result, ttl_seconds)
            return result

        return wrapper

    return decorator
