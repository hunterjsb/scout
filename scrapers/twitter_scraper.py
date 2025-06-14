from datetime import datetime
import os
import tweepy
import redis
import json

from .scraper import Scraper, ScrapeResult

# Type aliases to reduce repetition
TwitterTweet = tweepy.Tweet
TwitterClient = tweepy.Client
TwitterResult = ScrapeResult[TwitterTweet]


class TwitterScraper(Scraper[TwitterTweet]):
    """Twitter/X scraper using Tweepy's Tweet model and v2 API."""

    def __init__(self, tweepy_client: TwitterClient, redis_client: redis.Redis):
        super().__init__(tweepy_client)
        # Access the raw tweepy client
        self.client = self.raw_source
        # Simple Redis cache
        self.redis = redis_client

    def scrape(self) -> TwitterResult:
        """Scrape tweets from the configured source."""
        tweets = self._fetch_tweets()
        return ScrapeResult(
            data=tweets,
            timestamp=datetime.now()
        )

    def _fetch_tweets(self) -> list[TwitterTweet]:
        """Fetch tweets using Tweepy v2 API with caching."""
        print(f"Source: {self.source}")
        print(f"Available methods: {list(self.source.get_methods().keys())[:10]}...")  # Show first 10

        user = self._get_user_cached('elonmusk')
        print(user)

        # TODO return tweets
        return []

    def _get_user_cached(self, username: str):
        """Get user with caching support."""
        cache_key = f"twitter_user:{username}"

        # Try cache first
        cached = self.redis.get(cache_key)
        if cached:
            print(f"Cache hit for user: {username}")
            return json.loads(str(cached))

        # Make API call
        print(f"API call for user: {username}")
        user_response = self.source.get_user(username=username)

        # Extract essential user data for caching
        user_dict = {
            "id": user_response.data.id,
            "username": user_response.data.username,
            "name": user_response.data.name,
            "public_metrics": getattr(user_response.data, 'public_metrics', {}),
            "verified": getattr(user_response.data, 'verified', False)
        }

        # Cache for 5 minutes
        self.redis.setex(cache_key, 300, json.dumps(user_dict))

        return user_dict


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

    # Create simple Redis connection
    redis_client = redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        db=int(os.environ.get("REDIS_DB", "0")),
        decode_responses=True
    )
    print("Connected to Redis")

    # Create scraper with caching
    scraper = TwitterScraper(client, redis_client)
    result = scraper.scrape()

    if result.error:
        print(f"Error: {result.error}")
    else:
        print(f"Scraped {len(result.data)} tweets")
