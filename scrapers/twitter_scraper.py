from datetime import datetime
import os
import tweepy

from .scraper import Scraper, ScrapeResult
from .cache import RedisCache, Cache
from typing import Optional

# Type aliases to reduce repetition
TwitterTweet = tweepy.Tweet
TwitterClient = tweepy.Client
TwitterResult = ScrapeResult[TwitterTweet]


class TwitterScraper(Scraper[TwitterTweet]):
    """Twitter/X scraper using Tweepy's Tweet model and v2 API."""

    def __init__(self, tweepy_client: TwitterClient, cache: Optional[Cache] = None):
        super().__init__(tweepy_client, cache)
        # Access the raw tweepy client
        self.client = self.raw_source

    def scrape(self) -> TwitterResult:
        """Scrape tweets from the configured source."""
        tweets = self._fetch_tweets()
        return ScrapeResult(
            data=tweets,
            timestamp=datetime.now()
        )

    def _fetch_tweets(self) -> list[TwitterTweet]:
        """Fetch tweets using Tweepy v2 API with caching."""
        # Example: Get recent tweets from public timeline
        # You can modify this to fetch from specific users, search, etc.

        # Demo: Show what methods are available through introspection
        print(f"Source: {self.source}")
        print(f"Available methods: {list(self.source.get_methods().keys())[:10]}...")  # Show first 10

        # Example: Call methods directly with full typing
        user = self._get_user_cached('elonmusk')
        print(user)

        # For now, return empty list - implement actual API calls here
        return []

    def _get_user_cached(self, username: str):
        """Get user with caching support."""
        cache_key = self._get_cache_key('get_user', username=username)

        # Try cache first
        cached_result = self._cache_get(cache_key)
        if cached_result is not None:
            print(f"Cache hit for user: {username}")
            return cached_result

        # Make API call
        print(f"API call for user: {username}")
        user = self.source.get_user(username=username)

        # Cache for 5 minutes (300 seconds)
        self._cache_set(cache_key, user, ttl=300)

        return user


# Example usage
if __name__ == "__main__":
    from utils.dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Get bearer token from environment
    bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        print("Error: TWITTER_BEARER_TOKEN not found in environment")
        exit(1)

    # Create Client as source
    client = tweepy.Client(bearer_token)

    # Create Redis cache from environment variables
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    redis_port = int(os.environ.get("REDIS_PORT", "6379"))
    redis_db = int(os.environ.get("REDIS_DB", "0"))

    try:
        cache: Optional[Cache] = RedisCache(host=redis_host, port=redis_port, db=redis_db)
        print(f"Connected to Redis at {redis_host}:{redis_port}")
    except Exception as e:
        print(f"Redis connection failed: {e}, falling back to no cache")
        cache = None

    # Create scraper with caching
    scraper = TwitterScraper(client, cache)
    result = scraper.scrape()

    if result.error:
        print(f"Error: {result.error}")
    else:
        print(f"Scraped {len(result.data)} tweets")
