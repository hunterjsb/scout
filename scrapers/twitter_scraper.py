from datetime import datetime
import os
import tweepy

from .scraper import Scraper, ScrapeResult

# Type aliases to reduce repetition
TwitterTweet = tweepy.Tweet
TwitterClient = tweepy.Client
TwitterResult = ScrapeResult[TwitterTweet]


class TwitterScraper(Scraper[TwitterTweet]):
    """Twitter/X scraper using Tweepy's Tweet model and v2 API."""

    def __init__(self, tweepy_client: TwitterClient):
        super().__init__(tweepy_client)
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
        """Fetch tweets using Tweepy v2 API."""
        # Example: Get recent tweets from public timeline
        # You can modify this to fetch from specific users, search, etc.

        # Demo: Show what methods are available through introspection
        print(f"Source: {self.source}")
        print(f"Available methods: {list(self.source.get_methods().keys())[:10]}...")  # Show first 10

        # Example: Call methods directly with full typing
        user = self.source.get_user(username='elonmusk')
        print(user)

        # For now, return empty list - implement actual API calls here
        return []


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
    scraper = TwitterScraper(client)
    result = scraper.scrape()

    if result.error:
        print(f"Error: {result.error}")
    else:
        print(f"Scraped {len(result.data)} tweets")
