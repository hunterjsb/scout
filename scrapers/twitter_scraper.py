from datetime import datetime
import os
import tweepy
import redis

from .scraper import Scraper, ScrapeResult


class TwitterScraper(Scraper[tweepy.Tweet]):
    """Twitter/X scraper using Tweepy's Tweet model and v2 API."""

    def __init__(self, tweepy_client: tweepy.Client, redis_client: redis.Redis):
        super().__init__(tweepy_client)
        self.client: tweepy.Client = self.raw_source
        self.redis = redis_client

    def scrape(self) -> ScrapeResult[tweepy.Tweet]:
        """Scrape tweets from the configured source."""
        tweets = self._fetch_tweets()
        return ScrapeResult(
            data=tweets,
            timestamp=datetime.now()
        )

    def _fetch_tweets(self) -> list[tweepy.Tweet]:
        """Fetch tweets using Tweepy v2 API with caching."""
        # Get user ID for a specific user (e.g., elonmusk)
        username = "elonmusk"
        user_id = self._get_user_id_cached(username)

        # Get tweets for that user
        tweets = self._get_tweets_cached(user_id)

        return tweets

    def _get_user_id_cached(self, username: str) -> str:
        """Get user ID with extremely long caching since IDs never change."""
        cache_key = f"twitter_user_id:{username}"

        # Try cache first
        if self.redis:
            cached = self.redis.get(cache_key)
            if cached:
                print(f"Cache hit for user ID: {username}")
                return str(cached)

        # Make API call to get user ID
        print(f"API call for user ID: {username}")
        user_response = self.client.get_user(username=username)
        assert isinstance(user_response, tweepy.Response)
        user_id = str(user_response.data["id"])

        # Cache for 30 days (2592000 seconds) since user IDs never change
        if self.redis:
            self.redis.setex(cache_key, 2592000, user_id)

        return user_id

    def _get_tweets_cached(self, user_id: str) -> list[tweepy.Tweet]:
        """Get tweets for a user with caching."""
        cache_key = f"twitter_tweets:{user_id}"

        # TODO implement caching for tweets
        # if self.redis:
        #     cached = self.redis.get(cache_key)
        #     if cached:
        #         return []

        # Make API call to get tweets
        print(f"API call for tweets: {user_id}")
        tweets_response = self.client.get_users_tweets(id=user_id, max_results=10)
        assert isinstance(tweets_response, tweepy.Response)

        if not tweets_response.data:
            print("NO TWEETS")
            return []

        # Cache tweets for 15 minutes
        if self.redis:
            # For now, just cache the count - tweets are complex to serialize
            tweet_count = len(tweets_response.data)
            self.redis.setex(cache_key, 900, str(tweet_count))

        return tweets_response.data


# Example usage
if __name__ == "__main__":
    from utils.dotenv import load_dotenv
    load_dotenv()

    # auth
    bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        print("Error: TWITTER_BEARER_TOKEN not found in environment")
        exit(1)

    # init
    client = tweepy.Client(bearer_token)

    # cache
    redis_client = redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        db=int(os.environ.get("REDIS_DB", "0")),
        decode_responses=True
    )

    # scrape
    scraper = TwitterScraper(client, redis_client)
    result = scraper.scrape()
    print("GOT ", result)

    if result.error:
        print(f"Error: {result.error}")
    else:
        print(f"Scraped {len(result.data)} tweets")
        print(result.data)
