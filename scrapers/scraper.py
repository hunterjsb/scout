from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, Generic, Optional
from urllib.parse import urlparse


T = TypeVar('T')


@dataclass
class ScrapeSource:
    """Source configuration for scraping."""
    name: str
    url: str

    def __post_init__(self):
        # Basic URL validation
        parsed = urlparse(self.url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {self.url}")


@dataclass
class ScrapeResult(Generic[T]):
    """Result container for scraped data."""
    data: list[T]
    timestamp: datetime
    source: ScrapeSource
    error: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class Scraper(ABC, Generic[T]):
    """Base class for all scrapers."""

    def __init__(self, source: ScrapeSource):
        self.source = source

    @abstractmethod
    def scrape(self) -> ScrapeResult[T]:
        """Scrape data from the configured source."""
        pass
