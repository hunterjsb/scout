from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, Generic, Optional, Any

from .source import create_source

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

    def __init__(self, raw_source: Any):
        self.source = create_source(raw_source)
        self.raw_source = raw_source

    @abstractmethod
    def scrape(self) -> ScrapeResult[T]:
        """Scrape data from the configured source."""
        pass
