from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, Generic, Optional, Any

from .source import create_source
from .cache import Cache

T = TypeVar('T')


@dataclass
class ScrapeResult(Generic[T]):
    """Result container for scraped data."""
    data: list[T]
    timestamp: datetime
    error: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class Scraper(ABC, Generic[T]):
    """Base class for all scrapers."""

    def __init__(self, raw_source: Any, cache: Optional[Cache] = None):
        self.source = create_source(raw_source)
        self.raw_source = raw_source
        self.cache = cache

    @abstractmethod
    def scrape(self) -> ScrapeResult[T]:
        """Scrape data from the configured source."""
        pass

    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key for scraping operations."""
        from .cache import create_cache_key
        return f"{self.__class__.__name__}:{create_cache_key(*args, **kwargs)}"

    def _cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache if available."""
        if self.cache is None:
            return None
        return self.cache.get(key)

    def _cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache if available."""
        if self.cache is not None:
            self.cache.set(key, value, ttl)
