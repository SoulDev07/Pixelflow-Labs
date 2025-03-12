import os
import re
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pymongo import MongoClient
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt_tab',quiet=True)

# Initialize MongoDB connection
def initialize_mongodb():
    """Connect to MongoDB and return relevant collections"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['trend_analytics']
        trends_collection = db['trends']
        sentiment_collection = db['sentiment_analysis']
        keywords_collection = db['keywords']
        
        return {
            'client': client,
            'trends': trends_collection,
            'sentiment': sentiment_collection,
            'keywords': keywords_collection
        }
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None

# Initialize sentiment analysis model
def initialize_sentiment_model():
    """Initialize and return a sentiment analysis pipeline"""
    sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    return sentiment_model

# Text preprocessing utilities
class TextProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
    def clean_text(self, text):
        """Clean and normalize text"""
        if not isinstance(text, str):
            return ""
            
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        # Tokenize
        tokens = word_tokenize(text)
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens if word not in self.stop_words and len(word) > 2]
        return ' '.join(tokens)
    
    def extract_hashtags(self, text):
        """Extract hashtags from text"""
        if not isinstance(text, str):
            return []
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags
    
    def extract_keywords(self, text, n=10):
        """Extract most common keywords from processed text"""
        if not text:
            return []
        words = text.split()
        word_counts = Counter(words)
        return word_counts.most_common(n)

# Google Trends data collector
# Google Trends data collector with improved error handling
class GoogleTrendsCollector:
    def __init__(self, domain=""):
        # Add backoff and retry logic
        self.domain = domain
        self.max_retries = 3
        self.backoff_factor = 2
        self.initialize_pytrends()
    
    def initialize_pytrends(self):
        """Initialize pytrends with custom headers to avoid detection"""
        try:
            # Use custom headers to mimic a real browser
            self.pytrends = TrendReq(
                hl='en-US', 
                tz=360,
                timeout=(10, 25),  # Connect timeout, Read timeout
                retries=2,
                backoff_factor=1,
                requests_args={
                    'headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                    }
                }
            )
            return True
        except Exception as e:
            print(f"Error initializing pytrends: {e}")
            return False
    
    def get_trending_searches(self, geo='US', count=20):
        """Get real-time trending searches with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Try different methods to get trending searches
                try:
                    # Try the trending_searches method first
                    trending_searches = self.pytrends.trending_searches(pn=geo)
                    trending_searches.columns = ['topic']
                except Exception as e1:
                    print(f"Trending searches method failed: {e1}, trying realtime_trending_searches")
                    # Fall back to realtime_trending_searches method
                    trending_searches = self.pytrends.realtime_trending_searches(pn=geo)
                    # Extract titles
                    if 'title' in trending_searches.columns:
                        trending_searches = trending_searches[['title']].rename(columns={'title': 'topic'})
                    else:
                        # Last resort: create a minimal dataframe
                        print("Could not get trending searches from Google Trends")
                        return pd.DataFrame(columns=['topic'])
                
                # Filter by domain if specified
                if self.domain and not trending_searches.empty:
                    # Simple keyword match for filtering
                    mask = trending_searches['topic'].str.lower().str.contains(self.domain.lower(), na=False)
                    filtered_df = trending_searches[mask]
                    
                    # If no direct matches, keep original
                    if not filtered_df.empty:
                        trending_searches = filtered_df
                
                return trending_searches.head(count)
            
            except Exception as e:
                wait_time = self.backoff_factor ** attempt
                print(f"Attempt {attempt+1}/{self.max_retries} failed: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                # Reinitialize pytrends for next attempt
                self.initialize_pytrends()
        
        print("All attempts to get trending searches failed")
        return pd.DataFrame(columns=['topic'])
    
    # Rest of the methods remain the same but with similar retry logic added
    
    def get_interest_over_time(self, keywords, timeframe='now 7-d', geo=''):
        """Get interest over time for specific keywords"""
        try:
            self.pytrends.build_payload(kw_list=keywords, timeframe=timeframe, geo=geo)
            interest_df = self.pytrends.interest_over_time()
            if not interest_df.empty:
                interest_df = interest_df.drop(columns=['isPartial'], errors='ignore')
            return interest_df
        except Exception as e:
            print(f"Error getting interest over time: {e}")
            return pd.DataFrame()
    
    def get_related_queries(self, keyword, geo=''):
        """Get related queries for a keyword"""
        try:
            self.pytrends.build_payload(kw_list=[keyword], timeframe='now 7-d', geo=geo)
            related_queries = self.pytrends.related_queries()
            result = {}
            
            if related_queries[keyword]['top'] is not None:
                result['top'] = related_queries[keyword]['top']
            if related_queries[keyword]['rising'] is not None:
                result['rising'] = related_queries[keyword]['rising']
                
            return result
        except Exception as e:
            print(f"Error getting related queries: {e}")
            return {}

# Reddit data collector
class RedditDataCollector:
    def __init__(self, domain=""):
        self.domain = domain
        
    def scrape_subreddit(self, subreddit_name, limit=25):
        """Scrape top posts from a subreddit without using API"""
        try:
            # Reddit URL
            url = f"https://www.reddit.com/r/{subreddit_name}/top.json?limit={limit}&t=week"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Error accessing Reddit: Status code {response.status_code}")
                return pd.DataFrame()
                
            data = response.json()
            posts = []
            
            for post in data['data']['children']:
                post_data = post['data']
                
                # Filter by domain if specified
                if self.domain and self.domain.lower() not in post_data['title'].lower():
                    continue
                    
                posts.append({
                    'title': post_data['title'],
                    'score': post_data['score'],
                    'num_comments': post_data['num_comments'],
                    'created_utc': datetime.fromtimestamp(post_data['created_utc']),
                    'url': post_data['url'],
                    'selftext': post_data.get('selftext', '')
                })
                
            return pd.DataFrame(posts)
        except Exception as e:
            print(f"Error scraping Reddit: {e}")
            return pd.DataFrame()

# News API collector (using newsapi.org)
class NewsCollector:
    def __init__(self, api_key, domain=""):
        self.api_key = api_key
        self.domain = domain
        
    def get_top_headlines(self, country='us', category=None, q=None, page_size=20):
        """Get top headlines from News API"""
        try:
            base_url = "https://newsapi.org/v2/top-headlines?"
            
            # Build query parameters
            params = {
                'country': country,
                'apiKey': self.api_key,
                'pageSize': page_size
            }
            
            if category:
                params['category'] = category
                
            if q or self.domain:
                params['q'] = q or self.domain
                
            response = requests.get(base_url, params=params)
            if response.status_code != 200:
                print(f"Error accessing News API: Status code {response.status_code}")
                return pd.DataFrame()
                
            data = response.json()
            
            if data['status'] != 'ok':
                print(f"Error from News API: {data['message'] if 'message' in data else 'Unknown error'}")
                return pd.DataFrame()
                
            articles = []
            for article in data['articles']:
                articles.append({
                    'title': article['title'],
                    'description': article['description'],
                    'source': article['source']['name'],
                    'url': article['url'],
                    'publishedAt': article['publishedAt'],
                    'content': article['content']
                })
                
            return pd.DataFrame(articles)
        except Exception as e:
            print(f"Error getting news headlines: {e}")
            return pd.DataFrame()

# Trend analyzer
class TrendAnalyzer:
    def __init__(self, text_processor, sentiment_model):
        self.text_processor = text_processor
        self.sentiment_model = sentiment_model
        
    def analyze_sentiment(self, texts):
        """Analyze sentiment for a list of texts"""
        results = []
        
        for text in texts:
            if not isinstance(text, str) or not text:
                results.append({"label": "NEUTRAL", "score": 0.5})
                continue
                
            # Truncate long texts to avoid exceeding model's max token limit
            truncated_text = text[:512] if len(text) > 512 else text
            
            try:
                sentiment = self.sentiment_model(truncated_text)[0]
                results.append(sentiment)
            except Exception as e:
                print(f"Error in sentiment analysis: {e}")
                results.append({"label": "NEUTRAL", "score": 0.5})
                
        return results
    
    def calculate_sentiment_stats(self, sentiments):
        """Calculate sentiment statistics"""
        if not sentiments:
            return {
                "positive_ratio": 0,
                "negative_ratio": 0,
                "neutral_ratio": 0,
                "average_positive_score": 0,
                "average_negative_score": 0
            }
            
        positive = [s for s in sentiments if s["label"] == "POSITIVE"]
        negative = [s for s in sentiments if s["label"] == "NEGATIVE"]
        
        total = len(sentiments)
        
        return {
            "positive_ratio": len(positive) / total if total > 0 else 0,
            "negative_ratio": len(negative) / total if total > 0 else 0,
            "neutral_ratio": (total - len(positive) - len(negative)) / total if total > 0 else 0,
            "average_positive_score": sum(s["score"] for s in positive) / len(positive) if positive else 0,
            "average_negative_score": sum(s["score"] for s in negative) / len(negative) if negative else 0
        }
    
    def extract_all_hashtags(self, texts):
        """Extract and count hashtags from all texts"""
        all_hashtags = []
        
        for text in texts:
            if not isinstance(text, str):
                continue
            hashtags = self.text_processor.extract_hashtags(text)
            all_hashtags.extend(hashtags)
            
        return Counter(all_hashtags).most_common(20)
    
    def get_combined_keywords(self, texts, n=20):
        """Extract keywords from combined cleaned texts"""
        cleaned_texts = [self.text_processor.clean_text(text) for text in texts if isinstance(text, str)]
        combined_text = " ".join(cleaned_texts)
        
        words = combined_text.split()
        word_counts = Counter(words)
        return word_counts.most_common(n)

# Main trend collection and analysis function
def collect_and_analyze_trends(domain="", mongodb_collections=None):
    """Collect and analyze trends, store results in MongoDB"""
    # Initialize required components
    text_processor = TextProcessor()
    sentiment_model = initialize_sentiment_model()
    trend_analyzer = TrendAnalyzer(text_processor, sentiment_model)
    
    # Initialize data collectors
    google_trends = GoogleTrendsCollector(domain)
    reddit_collector = RedditDataCollector(domain)
    
    # Only initialize news collector if API key is available
    news_api_key = os.environ.get("NEWS_API_KEY")
    news_collector = None
    if news_api_key:
        news_collector = NewsCollector(news_api_key, domain)
    
    # Timestamp for this analysis
    timestamp = datetime.now()
    
    # Results dictionary to be stored in MongoDB
    results = {
        "timestamp": timestamp,
        "domain": domain,
        "google_trends": {},
        "reddit_data": {},
        "news_data": {},
        "combined_analysis": {}
    }
    
    # Collect Google Trends data
    print("Collecting Google Trends data...")
    trending_searches_df = google_trends.get_trending_searches(count=20)
    
    if not trending_searches_df.empty:
        trending_topics = trending_searches_df['topic'].tolist()
        
        # Get interest over time for top 5 topics
        top_topics = trending_topics[:5]
        interest_data = {}
        
        for topic in top_topics:
            interest_df = google_trends.get_interest_over_time([topic])
            if not interest_df.empty:
                interest_data[topic] = interest_df[topic].to_dict()
                
        # Get related queries for domain if specified
        related_queries = {}
        if domain:
            related_queries = google_trends.get_related_queries(domain)
            
        results["google_trends"] = {
            "trending_topics": trending_topics,
            "interest_over_time": interest_data,
            "related_queries": related_queries
        }
    
    # Collect Reddit data
    print("Collecting Reddit data...")
    all_texts = []
    
    # List of subreddits to scrape based on domain
    subreddits = ["popular", "news", "technology"]
    
    # Add domain-specific subreddits if domain is provided
    if domain:
        if domain.lower() in ["tech", "technology"]:
            subreddits.extend(["gadgets", "technews", "coding", "programming"])
        elif domain.lower() in ["fashion", "style"]:
            subreddits.extend(["malefashionadvice", "femalefashionadvice", "streetwear"])
        elif domain.lower() in ["food", "cooking"]:
            subreddits.extend(["food", "cooking", "recipes"])
        elif domain.lower() in ["travel", "tourism"]:
            subreddits.extend(["travel", "backpacking", "travelhacks"])
        elif domain.lower() in ["health", "fitness"]:
            subreddits.extend(["fitness", "health", "nutrition"])
    
    reddit_data = {}
    
    for subreddit in subreddits:
        df = reddit_collector.scrape_subreddit(subreddit)
        if not df.empty:
            reddit_data[subreddit] = {
                "post_count": len(df),
                "average_score": df['score'].mean() if 'score' in df.columns else 0,
                "top_posts": df.sort_values(by='score', ascending=False).head(5)[['title', 'score']].to_dict('records') if 'score' in df.columns else []
            }
            
            # Collect text for further analysis
            if 'title' in df.columns:
                all_texts.extend(df['title'].tolist())
            if 'selftext' in df.columns:
                all_texts.extend(df['selftext'].tolist())
    
    results["reddit_data"] = reddit_data
    
    # Collect News data if API key is available
    if news_collector:
        print("Collecting News data...")
        categories = ["general", "technology", "business", "entertainment", "health", "science", "sports"]
        
        news_data = {}
        for category in categories:
            df = news_collector.get_top_headlines(category=category, q=domain if domain else None)
            if not df.empty:
                news_data[category] = {
                    "article_count": len(df),
                    "sources": df['source'].value_counts().to_dict(),
                    "top_headlines": df[['title', 'source']].head(5).to_dict('records')
                }
                
                # Collect text for further analysis
                if 'title' in df.columns:
                    all_texts.extend(df['title'].tolist())
                if 'description' in df.columns:
                    all_texts.extend([desc for desc in df['description'].tolist() if desc])
        
        results["news_data"] = news_data
    
    # Perform combined analysis on all collected texts
    print("Performing text analysis...")
    
    # Sentiment analysis
    sentiments = trend_analyzer.analyze_sentiment(all_texts)
    sentiment_stats = trend_analyzer.calculate_sentiment_stats(sentiments)
    
    # Extract hashtags
    hashtags = trend_analyzer.extract_all_hashtags(all_texts)
    
    # Extract keywords
    keywords = trend_analyzer.get_combined_keywords(all_texts)
    
    # Add combined analysis to results
    results["combined_analysis"] = {
        "sentiment": sentiment_stats,
        "top_hashtags": hashtags,
        "top_keywords": keywords,
        "text_count": len(all_texts)
    }
    
    # Store results in MongoDB if available
    if mongodb_collections:
        print("Storing results in MongoDB...")
        try:
            # Store main trends document
            trends_id = mongodb_collections['trends'].insert_one(results).inserted_id
            print(f"Stored trends data with ID: {trends_id}")
            
            # Store sentiment analysis separately for time-series analysis
            sentiment_doc = {
                "timestamp": timestamp,
                "domain": domain,
                "sentiment_stats": sentiment_stats,
                "trend_id": trends_id
            }
            mongodb_collections['sentiment'].insert_one(sentiment_doc)
            
            # Store keywords separately for easier querying
            keywords_doc = {
                "timestamp": timestamp,
                "domain": domain,
                "hashtags": hashtags,
                "keywords": keywords,
                "trend_id": trends_id
            }
            mongodb_collections['keywords'].insert_one(keywords_doc)
        except Exception as e:
            print(f"Error storing data in MongoDB: {e}")
    
    return results

# Main execution function
def main():
    """Main function to run the trend analysis"""
    # Get domain from command line argument or use empty string
    import sys
    domain = sys.argv[1] if len(sys.argv) > 1 else ""
    
    print(f"Starting trend analysis{' for domain: ' + domain if domain else ''}...")
    
    # Initialize MongoDB
    mongo_collections = initialize_mongodb()
    
    # Collect and analyze trends
    results = collect_and_analyze_trends(domain, mongo_collections)
    
    print("Analysis complete!")
    
    # Close MongoDB connection
    if mongo_collections:
        mongo_collections['client'].close()
    
    return results

if __name__ == "__main__":
    main()