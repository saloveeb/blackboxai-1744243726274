from textblob import TextBlob
import tweepy
import yfinance as yf
from typing import List, Dict
from ..database import SessionLocal

class SentimentAnalyzer:
    def __init__(self):
        self.db = SessionLocal()
        self.twitter_auth = {
            'consumer_key': 'YOUR_API_KEY',
            'consumer_secret': 'YOUR_API_SECRET'
        }
        
    def analyze_market_sentiment(self, symbol: str) -> Dict:
        """Analyze combined sentiment from Twitter and news"""
        twitter_score = self._get_twitter_sentiment(symbol)
        news_score = self._get_news_sentiment(symbol)
        
        return {
            'twitter_sentiment': twitter_score,
            'news_sentiment': news_score,
            'composite_score': (twitter_score + news_score) / 2
        }
        
    def _get_twitter_sentiment(self, symbol: str) -> float:
        """Get sentiment from Twitter"""
        try:
            auth = tweepy.AppAuthHandler(
                self.twitter_auth['consumer_key'],
                self.twitter_auth['consumer_secret']
            )
            api = tweepy.API(auth)
            tweets = api.search_tweets(q=f'${symbol}', count=100)
            return self._calculate_average_sentiment([t.text for t in tweets])
        except Exception as e:
            print(f"Twitter API error: {e}")
            return 0.0
            
    def _get_news_sentiment(self, symbol: str) -> float:
        """Get sentiment from news articles"""
        try:
            stock = yf.Ticker(symbol)
            news = stock.news or []
            return self._calculate_average_sentiment([n['title'] for n in news])
        except Exception as e:
            print(f"News sentiment error: {e}")
            return 0.0
            
    def _calculate_average_sentiment(self, texts: List[str]) -> float:
        """Calculate average sentiment score for list of texts"""
        if not texts:
            return 0.0
            
        sentiments = [TextBlob(text).sentiment.polarity for text in texts]
        return sum(sentiments) / len(sentiments)
