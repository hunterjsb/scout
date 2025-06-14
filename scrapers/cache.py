import json
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Optional
import redis


class Cache(ABC):
    """Abstract base class for caching implementations."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL in seconds."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete key from cache."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass


class RedisCache(Cache):
    """Redis-based cache implementation."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0,
                 key_prefix: str = "scout:"):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.key_prefix = key_prefix

    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.key_prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            data = self.client.get(self._make_key(key))
            if data is None:
                return None
            return json.loads(str(data))
        except (redis.RedisError, json.JSONDecodeError):
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in Redis cache."""
        try:
            serialized = json.dumps(value, default=str)  # default=str handles datetime
            if ttl:
                self.client.setex(self._make_key(key), ttl, serialized)
            else:
                self.client.set(self._make_key(key), serialized)
        except (redis.RedisError, json.JSONDecodeError):
            pass  # Fail silently for caching errors

    def delete(self, key: str) -> None:
        """Delete key from Redis cache."""
        try:
            self.client.delete(self._make_key(key))
        except redis.RedisError:
            pass

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        try:
            return bool(self.client.exists(self._make_key(key)))
        except redis.RedisError:
            return False


class MemoryCache(Cache):
    """Simple in-memory cache implementation for testing."""

    def __init__(self):
        self._cache = {}
        self._expiry = {}

    def _is_expired(self, key: str) -> bool:
        """Check if key has expired."""
        if key not in self._expiry:
            return False
        return datetime.now() > self._expiry[key]

    def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache."""
        if key not in self._cache or self._is_expired(key):
            if key in self._cache:
                del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return None
        return self._cache[key]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in memory cache."""
        self._cache[key] = value
        if ttl:
            self._expiry[key] = datetime.now() + timedelta(seconds=ttl)
        elif key in self._expiry:
            del self._expiry[key]

    def delete(self, key: str) -> None:
        """Delete key from memory cache."""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)

    def exists(self, key: str) -> bool:
        """Check if key exists in memory cache."""
        return key in self._cache and not self._is_expired(key)


def create_cache_key(*args, **kwargs) -> str:
    """Create a cache key from function arguments."""
    # Create a deterministic hash from arguments
    key_data = {"args": args, "kwargs": sorted(kwargs.items())}
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


class CachedMethod:
    """Decorator to cache method results."""

    def __init__(self, cache: Cache, ttl: Optional[int] = None, key_prefix: str = ""):
        self.cache = cache
        self.ttl = ttl
        self.key_prefix = key_prefix

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{self.key_prefix}{func.__name__}:{create_cache_key(*args[1:], **kwargs)}"

            # Try to get from cache
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Call original function
            result = func(*args, **kwargs)

            # Cache the result
            self.cache.set(cache_key, result, self.ttl)

            return result
        return wrapper
