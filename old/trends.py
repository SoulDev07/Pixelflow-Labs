import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import pymongo
from pymongo import MongoClient
import time
import re
import nltk
from nltk.corpus import stopwords
from collections import Counter
from wordcloud import WordCloud
import logging
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import random
from fake_useragent import UserAgent
import json
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import os
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SocialMediaTrendAnalyzer:
    def __init__(self, mongodb_uri, db_name="trend_analysis"):
        """Initialize the analyzer with MongoDB connection"""
        # MongoDB setup
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        self.trends_collection = self.db.trends
        self.posts_collection = self.db.posts
        self.analysis_collection = self.db.analysis
        
        # Initialize sentiment analyzers
        self.vader = SentimentIntensityAnalyzer()
        
        # Download NLTK resources if not already downloaded
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            nltk.download('punkt')
        
        self.stop_words = set(stopwords.words('english'))
        
        # Set up a rotating user agent to avoid detection
        self.ua = UserAgent()
        
        # API keys for free services
        self.newsapi_key = None  # You'll need to register for a free key at newsapi.org
        self.reddit_api_credentials = {
            'client_id': None,      # Register an app on Reddit to get these
            'client_secret': None,  # https://www.reddit.com/prefs/apps
            'user_agent': 'TrendAnalyzer/1.0'
        }
        
        # Proxy setup (if needed)
        self.proxies = None
        
        logger.info("Social Media Trend Analyzer initialized successfully")

    def set_newsapi_key(self, api_key):
        """Set NewsAPI key for retrieving news trends"""
        self.newsapi_key = api_key
        logger.info("NewsAPI key set successfully")
    
    def set_reddit_credentials(self, client_id, client_secret, user_agent=None):
        """Set Reddit API credentials"""
        self.reddit_api_credentials = {
            'client_id': client_id,
            'client_secret': client_secret,
            'user_agent': user_agent or 'TrendAnalyzer/1.0'
        }
        logger.info("Reddit API credentials set successfully")
    
    def get_random_headers(self):
        """Generate random headers to avoid detection"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
    
    def setup_proxies(self, proxy_list=None):
        """Set up proxies for requests (optional)"""
        if proxy_list and isinstance(proxy_list, list) and len(proxy_list) > 0:
            self.proxies = proxy_list
            logger.info(f"Set up {len(proxy_list)} proxies")
    
    def get_random_proxy(self):
        """Get a random proxy from the list if available"""
        if self.proxies:
            proxy = random.choice(self.proxies)
            return {'http': proxy, 'https': proxy}
        return None
    
    def make_request(self, url, retries=3, delay=2, headers=None, params=None):
        """Make a request with retries and random headers"""
        for attempt in range(retries):
            try:
                _headers = headers or self.get_random_headers()
                proxies = self.get_random_proxy()
                
                response = requests.get(
                    url, 
                    headers=_headers, 
                    proxies=proxies,
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    return response
                
                logger.warning(f"Request to {url} returned status code {response.status_code}")
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed for {url}: {str(e)}")
            
            # Wait before retrying
            time.sleep(delay * (attempt + 1))
        
        logger.error(f"Failed to retrieve {url} after {retries} attempts")
        return None
    
    def get_newsapi_trends(self, query='', country=None, category=None, page_size=None):
        """Use newsdata.io API to fetch trending news stories"""
        if not self.newsapi_key:
            logger.warning("NewsAPI key not set. Use set_newsapi_key() method to set it.")
            return []
        
        try:
            url = "https://newsdata.io/api/1/latest"
            params = {
                'apikey': self.newsapi_key
            }
            
            # Add optional parameters according to newsdata.io specs
            if query:
                params['q'] = query
            if country:
                params['country'] = country  # Use comma-separated list for multiple countries
            if category:
                params['category'] = category.lower()  # newsdata.io uses lowercase categories
            
            response = self.make_request(url, params=params)
            
            if not response:
                return []
            
            data = response.json()
            if data.get('status') != 'success':
                logger.error(f"NewsAPI returned error: {data.get('results', 'Unknown error')}")
                return []
            
            timestamp = datetime.datetime.now()
            processed_trends = []
            
            for article in data.get('results', []):
                # Skip non-English articles if they slip through
                if article.get('language') != 'english':
                    continue
                    
                trend_data = {
                    'name': article.get('title', ''),
                    'url': article.get('link', ''),
                    'source': {
                        'id': article.get('source_id', ''),
                        'name': article.get('source_name', ''),
                        'url': article.get('source_url', ''),
                        'priority': article.get('source_priority', 0)
                    },
                    'article_id': article.get('article_id', ''),
                    'published_at': article.get('pubDate'),
                    'timezone': article.get('pubDateTZ', 'UTC'),
                    'description': article.get('description', ''),
                    'image_url': article.get('image_url'),
                    'video_url': article.get('video_url'),
                    'keywords': article.get('keywords', []),
                    'category': article.get('category', []),
                    'country': article.get('country', []),
                    'is_duplicate': article.get('duplicate', False),
                    'trend_source': 'newsdata',
                    'timestamp': timestamp
                }
                processed_trends.append(trend_data)
            
            # Store in MongoDB
            if processed_trends:
                self.trends_collection.insert_many(processed_trends)
                logger.info(f"Stored {len(processed_trends)} newsdata.io trends")
            
            return processed_trends
        except Exception as e:
            logger.error(f"Error fetching newsdata.io trends: {str(e)}")
            return []
    
    def get_reddit_api_trends(self, subreddit='all', limit=25):
        """Use Reddit API to fetch trending posts"""
        if not self.reddit_api_credentials.get('client_id') or not self.reddit_api_credentials.get('client_secret'):
            logger.warning("Reddit API credentials not set. Use set_reddit_credentials() method to set them.")
            return []
        
        try:
            # First get an OAuth token
            auth_url = "https://www.reddit.com/api/v1/access_token"
            auth_data = {
                'grant_type': 'client_credentials'
            }
            auth_headers = {
                'User-Agent': self.reddit_api_credentials.get('user_agent')
            }
            
            auth_response = requests.post(
                auth_url,
                auth=(self.reddit_api_credentials.get('client_id'), self.reddit_api_credentials.get('client_secret')),
                data=auth_data,
                headers=auth_headers
            )
            
            if auth_response.status_code != 200:
                logger.error(f"Failed to get Reddit token: {auth_response.text}")
                return []
            
            token_data = auth_response.json()
            access_token = token_data.get('access_token')
            
            if not access_token:
                logger.error("No access token in Reddit API response")
                return []
            
            # Now use the token to get trending posts
            url = f"https://oauth.reddit.com/r/{subreddit}/hot"
            headers = {
                'Authorization': f"Bearer {access_token}",
                'User-Agent': self.reddit_api_credentials.get('user_agent')
            }
            params = {
                'limit': limit
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"Reddit API error: {response.text}")
                return []
            
            data = response.json()
            timestamp = datetime.datetime.now()
            processed_trends = []
            
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                
                trend_data = {
                    'name': post_data.get('title', ''),
                    'url': f"https://www.reddit.com{post_data.get('permalink', '')}",
                    'score': post_data.get('score', 0),
                    'num_comments': post_data.get('num_comments', 0),
                    'subreddit': post_data.get('subreddit', ''),
                    'author': post_data.get('author', ''),
                    'is_video': post_data.get('is_video', False),
                    'created_utc': datetime.datetime.fromtimestamp(post_data.get('created_utc', 0)),
                    'trend_source': 'reddit',
                    'timestamp': timestamp
                }
                processed_trends.append(trend_data)
            
            # Store in MongoDB
            if processed_trends:
                self.trends_collection.insert_many(processed_trends)
                logger.info(f"Stored {len(processed_trends)} Reddit API trends")
            
            return processed_trends
        except Exception as e:
            logger.error(f"Error fetching Reddit API trends: {str(e)}")
            return []
    
    def get_hacker_news_trends(self, limit=30):
        """Fetch trending stories from Hacker News through their API"""
        try:
            # Fetch top story IDs
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = self.make_request(url)
            
            if not response:
                return []
            
            story_ids = response.json()[:limit]  # Get top stories
            timestamp = datetime.datetime.now()
            processed_trends = []
            
            # Fetch details for each story
            for story_id in story_ids:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_response = self.make_request(story_url)
                
                if not story_response:
                    continue
                
                story = story_response.json()
                
                trend_data = {
                    'name': story.get('title', ''),
                    'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                    'score': story.get('score', 0),
                    'num_comments': story.get('descendants', 0),
                    'author': story.get('by', ''),
                    'created_at': datetime.datetime.fromtimestamp(story.get('time', 0)),
                    'trend_source': 'hackernews',
                    'timestamp': timestamp
                }
                processed_trends.append(trend_data)
            
            # Store in MongoDB
            if processed_trends:
                self.trends_collection.insert_many(processed_trends)
                logger.info(f"Stored {len(processed_trends)} Hacker News trends")
            
            return processed_trends
        except Exception as e:
            logger.error(f"Error fetching Hacker News trends: {str(e)}")
            return []
    
    def get_github_trends(self, language=None):
        """Scrape trending repositories from GitHub"""
        try:
            url = "https://github.com/trending"
            if language:
                url += f"/{language}"
            
            response = self.make_request(url)
            
            if not response:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            timestamp = datetime.datetime.now()
            
            processed_trends = []
            repo_items = soup.select('article.Box-row')
            
            for item in repo_items:
                # Get repository details
                repo_link = item.select_one('h2 a')
                if not repo_link:
                    continue
                
                repo_path = repo_link.get('href', '').strip('/')
                if not repo_path:
                    continue
                
                # Get repository description
                description_elem = item.select_one('p')
                description = description_elem.text.strip() if description_elem else ''
                
                # Get stars count
                stars_elem = item.select_one('a.Link--muted')
                stars = 0
                if stars_elem:
                    stars_text = stars_elem.text.strip()
                    stars_match = re.search(r'(\d+(?:,\d+)*)', stars_text)
                    if stars_match:
                        stars = int(stars_match.group(1).replace(',', ''))
                
                # Get language
                lang_elem = item.select_one('span[itemprop="programmingLanguage"]')
                lang = lang_elem.text.strip() if lang_elem else None
                
                trend_data = {
                    'name': repo_path,
                    'url': f"https://github.com/{repo_path}",
                    'description': description,
                    'stars': stars,
                    'language': lang,
                    'trend_source': 'github',
                    'timestamp': timestamp
                }
                processed_trends.append(trend_data)
            
            # Store in MongoDB
            if processed_trends:
                self.trends_collection.insert_many(processed_trends)
                logger.info(f"Stored {len(processed_trends)} GitHub trends")
            
            return processed_trends
        except Exception as e:
            logger.error(f"Error fetching GitHub trends: {str(e)}")
            return []
    
    def get_stackexchange_hot_questions(self, site='stackoverflow'):
        """Fetch hot questions from Stack Exchange API"""
        try:
            url = f"https://api.stackexchange.com/2.3/questions"
            params = {
                'order': 'desc',
                'sort': 'hot',
                'site': site,
                'pagesize': 30
            }
            
            response = self.make_request(url, params=params)
            
            if not response:
                return []
            
            data = response.json()
            timestamp = datetime.datetime.now()
            
            processed_trends = []
            
            for question in data.get('items', []):
                trend_data = {
                    'name': question.get('title', ''),
                    'url': question.get('link', ''),
                    'score': question.get('score', 0),
                    'answer_count': question.get('answer_count', 0),
                    'view_count': question.get('view_count', 0),
                    'tags': question.get('tags', []),
                    'created_at': datetime.datetime.fromtimestamp(question.get('creation_date', 0)),
                    'trend_source': f'stackexchange_{site}',
                    'timestamp': timestamp
                }
                processed_trends.append(trend_data)
            
            # Store in MongoDB
            if processed_trends:
                self.trends_collection.insert_many(processed_trends)
                logger.info(f"Stored {len(processed_trends)} Stack Exchange ({site}) questions")
            
            return processed_trends
        except Exception as e:
            logger.error(f"Error fetching Stack Exchange questions: {str(e)}")
            return []
    
    def fetch_reddit_comments(self, post_url, limit=100):
        """Fetch comments for a Reddit post using Reddit JSON API"""
        try:
            # Reddit provides a JSON endpoint for any post
            json_url = f"{post_url}.json"
            
            response = self.make_request(json_url)
            if not response:
                return []
            
            data = response.json()
            timestamp = datetime.datetime.now()
            
            # Extract post ID from URL
            post_id_match = re.search(r'/comments/([a-z0-9]+)/', post_url)
            post_id = post_id_match.group(1) if post_id_match else 'unknown'
            
            processed_comments = []
            
            # The first element in the array is the post, the second is the comments
            if len(data) < 2:
                return []
                
            # Extract post data for reference
            post_data = data[0]['data']['children'][0]['data']
            
            # Process comments (recursive function to handle nested comments)
            def process_comments(comments, parent_id=None, depth=0):
                result = []
                
                for comment in comments:
                    # Skip non-comment items
                    if comment['kind'] != 't1':
                        continue
                        
                    c_data = comment['data']
                    
                    # Skip deleted or removed comments
                    if c_data.get('body') in ['[deleted]', '[removed]']:
                        continue
                    
                    comment_data = {
                        'id': c_data.get('id', 'unknown'),
                        'post_id': post_id,
                        'parent_id': parent_id,
                        'author': c_data.get('author', '[deleted]'),
                        'body': c_data.get('body', ''),
                        'score': c_data.get('score', 0),
                        'created_at': datetime.datetime.fromtimestamp(c_data.get('created_utc', 0)),
                        'depth': depth,
                        'source': 'reddit',
                        'query': post_data.get('title', ''),
                        'timestamp': timestamp
                    }
                    
                    result.append(comment_data)
                    
                    # Process replies (if any and not too deep)
                    if depth < 3 and 'replies' in c_data and c_data['replies'] and 'data' in c_data['replies']:
                        child_comments = process_comments(
                            c_data['replies']['data']['children'], 
                            parent_id=c_data.get('id'), 
                            depth=depth+1
                        )
                        result.extend(child_comments)
                    
                    # Limit total comments
                    if len(result) >= limit:
                        break
                
                return result
            
            # Start processing top-level comments
            comments_data = data[1]['data']['children']
            processed_comments = process_comments(comments_data)
            
            # Store in MongoDB
            if processed_comments:
                self.posts_collection.insert_many(processed_comments)
                logger.info(f"Stored {len(processed_comments)} Reddit comments for post: {post_id}")
            
            return processed_comments
        except Exception as e:
            logger.error(f"Error fetching Reddit comments for {post_url}: {str(e)}")
            return []
    
    def fetch_hackernews_comments(self, story_id, limit=100):
        """Fetch comments for a Hacker News story using their API"""
        try:
            # First get the story to get its comments
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story_response = self.make_request(story_url)
            
            if not story_response:
                return []
            
            story = story_response.json()
            comment_ids = story.get('kids', [])[:limit]  # Limit the number of comments
            timestamp = datetime.datetime.now()
            
            processed_comments = []
            
            # Fetch each comment
            for comment_id in comment_ids:
                comment_url = f"https://hacker-news.firebaseio.com/v0/item/{comment_id}.json"
                comment_response = self.make_request(comment_url)
                
                if not comment_response:
                    continue
                
                comment = comment_response.json()
                
                # Skip deleted comments
                if comment.get('deleted', False) or comment.get('dead', False):
                    continue
                
                comment_data = {
                    'id': str(comment.get('id')),
                    'post_id': str(story_id),
                    'parent_id': str(comment.get('parent')),
                    'author': comment.get('by', '[deleted]'),
                    'text': comment.get('text', ''),
                    'created_at': datetime.datetime.fromtimestamp(comment.get('time', 0)),
                    'source': 'hackernews',
                    'query': story.get('title', ''),
                    'timestamp': timestamp
                }
                
                processed_comments.append(comment_data)
            
            # Store in MongoDB
            if processed_comments:
                self.posts_collection.insert_many(processed_comments)
                logger.info(f"Stored {len(processed_comments)} Hacker News comments for story: {story_id}")
            
            return processed_comments
        except Exception as e:
            logger.error(f"Error fetching Hacker News comments for {story_id}: {str(e)}")
            return []
    
    def analyze_sentiment(self, text):
        """Perform sentiment analysis using multiple methods"""
        if not text or pd.isna(text):
            return {
                'vader': {'compound': 0, 'pos': 0, 'neu': 0, 'neg': 0},
                'textblob': {'polarity': 0, 'subjectivity': 0}
            }
        
        # VADER sentiment analysis
        vader_sentiment = self.vader.polarity_scores(text)
        
        # TextBlob sentiment analysis
        blob = TextBlob(text)
        textblob_sentiment = {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
        
        return {
            'vader': vader_sentiment,
            'textblob': textblob_sentiment
        }
    
    def extract_hashtags(self, text):
        """Extract hashtags from text"""
        if not text or pd.isna(text):
            return []
        
        # Extract hashtags using regex
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags
    
    def extract_keywords(self, text, top_n=10):
        """Extract most important keywords from text"""
        if not text or pd.isna(text):
            return []
        
        # Tokenize and clean text
        words = re.sub(r'[^\w\s]', '', text.lower()).split()
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # Count word frequency
        word_freq = Counter(words)
        return word_freq.most_common(top_n)
    
    def analyze_posts(self, posts):
        """Analyze posts for sentiment, hashtags, and keywords"""
        timestamp = datetime.datetime.now()
        
        for post in posts:
            # Determine which field contains the main content
            if 'text' in post:
                content = post['text']
            elif 'body' in post:
                content = post['body']
            elif 'title' in post:
                content = post['title']
            else:
                content = ""
            
            # Perform sentiment analysis
            sentiment = self.analyze_sentiment(content)
            
            # Extract hashtags
            hashtags = self.extract_hashtags(content)
            
            # Extract keywords
            keywords = self.extract_keywords(content)
            
            # Create analysis document
            analysis = {
                'post_id': post['id'],
                'source': post['source'],
                'query': post.get('query', ''),
                'sentiment': sentiment,
                'hashtags': hashtags,
                'keywords': keywords,
                'timestamp': timestamp
            }
            
            # Store in MongoDB
            self.analysis_collection.insert_one(analysis)
        
        logger.info(f"Analyzed {len(posts)} posts")
        return True
    
    def aggregate_sentiment_by_trend(self, trend_name, time_window=24):
        """Aggregate sentiment analysis results for a specific trend over time"""
        # Calculate time threshold
        time_threshold = datetime.datetime.now() - datetime.timedelta(hours=time_window)
        
        # Get all posts related to this trend
        posts = list(self.posts_collection.find({
            'query': trend_name,
            'timestamp': {'$gte': time_threshold}
        }))
        
        if not posts:
            return None
        
        # Extract sentiment scores
        vader_compound_scores = []
        textblob_polarity_scores = []
        
        for post in posts:
            post_id = post['id']
            analysis = self.analysis_collection.find_one({'post_id': post_id})
            
            if analysis and 'sentiment' in analysis:
                vader_compound_scores.append(analysis['sentiment']['vader']['compound'])
                textblob_polarity_scores.append(analysis['sentiment']['textblob']['polarity'])
        
        # Calculate average sentiment
        avg_vader = sum(vader_compound_scores) / len(vader_compound_scores) if vader_compound_scores else 0
        avg_textblob = sum(textblob_polarity_scores) / len(textblob_polarity_scores) if textblob_polarity_scores else 0
        
        return {
            'trend': trend_name,
            'num_posts': len(posts),
            'avg_vader_compound': avg_vader,
            'avg_textblob_polarity': avg_textblob,
            'time_window_hours': time_window,
            'timestamp': datetime.datetime.now()
        }
    
    def get_trend_metrics(self, hours=24, limit=10):
        """Get metrics for top trends including sentiment and volume"""
        time_threshold = datetime.datetime.now() - datetime.timedelta(hours=hours)
        
        # Combine metrics from different sources
        all_trends = list(self.trends_collection.find({
            'timestamp': {'$gte': time_threshold}
        }))
        
        # Normalize scores across different platforms
        def get_normalized_score(trend):
            source = trend.get('trend_source', '')
            
            if source == 'newsapi':
                # For news, we don't have a direct score, give it medium priority
                return 500
            elif source == 'reddit':
                # Reddit scores can be very high, normalize
                return trend.get('score', 0) * 0.5
            elif source == 'hackernews':
                # HN scores are relatively moderate
                return trend.get('score', 0) * 2
            elif source == 'github':
                # GitHub stars can be very high for trending repos
                return trend.get('stars', 0) * 0.2
            elif 'stackexchange' in source:
                # Stack Exchange scores tend to be lower
                return trend.get('score', 0) * 5 + trend.get('view_count', 0) * 0.1
            else:
                # Default normalization
                return trend.get('score', 0)
        
        # Sort trends by normalized score
        sorted_trends = sorted(all_trends, key=get_normalized_score, reverse=True)[:limit]
        
        trend_metrics = []
        for trend in sorted_trends:
            sentiment_metrics = self.aggregate_sentiment_by_trend(trend['name'])
            if sentiment_metrics:
                trend_metrics.append({
                    **trend,
                    'sentiment_metrics': sentiment_metrics
                })
            else:
                trend_metrics.append(trend)
        
        return trend_metrics
    
    def generate_trending_hashtags(self, hours=24, limit=20):
        """Generate list of trending hashtags with count and sentiment"""
        time_threshold = datetime.datetime.now() - datetime.timedelta(hours=hours)
        
        # Get all analyses in the time period
        analyses = list(self.analysis_collection.find({
            'timestamp': {'$gte': time_threshold}
        }))
        
        # Collect all hashtags
        hashtag_counter = Counter()
        hashtag_sentiment = {}
        
        for analysis in analyses:
            for hashtag in analysis.get('hashtags', []):
                hashtag_counter[hashtag] += 1
                
                # Update running average of sentiment for this hashtag
                vader_compound = analysis['sentiment']['vader']['compound']
                if hashtag in hashtag_sentiment:
                    count, current_avg = hashtag_sentiment[hashtag]
                    new_avg = (current_avg * count + vader_compound) / (count + 1)
                    hashtag_sentiment[hashtag] = (count + 1, new_avg)
                else:
                    hashtag_sentiment[hashtag] = (1, vader_compound)
        
        # Get top hashtags
        top_hashtags = hashtag_counter.most_common(limit)
        
        # Format results
        results = []
        for hashtag, count in top_hashtags:
            count, avg_sentiment = hashtag_sentiment.get(hashtag, (0, 0))
            results.append({
                'hashtag': hashtag,
                'count': count,
                'avg_sentiment': avg_sentiment,
                'timestamp': datetime.datetime.now()
            })
        
        return results
    
    def generate_word_cloud(self, sources=None, hours=24):
        """Generate data for a word cloud based on trending topics"""
        time_threshold = datetime.datetime.now() - datetime.timedelta(hours=hours)
        
        # Filter by sources if provided
        query = {'timestamp': {'$gte': time_threshold}}
        if sources:
            query['source'] = {'$in': sources}
        
        # Get all analyses in the time period
        analyses = list(self.analysis_collection.find(query))
        
        # Collect all keywords
        all_words = []
        for analysis in analyses:
            for word, count in analysis.get('keywords', []):
                all_words.extend([word] * count)
        
        # Create word count
        word_count = Counter(all_words)
        
        # Generate WordCloud data
        if word_count:
            try:
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_count)
                
                # Save wordcloud image to base64 for web display
                img_buffer = io.BytesIO()
                wordcloud.to_image().save(img_buffer, format='PNG')
                img_str = base64.b64encode(img_buffer.getvalue()).decode()
                
                return {
                    'word_frequencies': dict(word_count.most_common(100)),
                    'sources': sources,
                    'time_window_hours': hours,
                    'timestamp': datetime.datetime.now(),
                    'wordcloud_image': img_str
                }
            except Exception as e:
                logger.error(f"Error generating word cloud: {str(e)}")
                return None
        return None

def main():
    mongodb_uri = "mongodb://localhost:27017/"
    
    try:
        analyzer = SocialMediaTrendAnalyzer(mongodb_uri)
        
        # Set up API credentials
        analyzer.set_newsapi_key(os.getenv("NEWS_API"))
        
        # Fetch news with specific topics - using correct parameters
        try:
            news_trends = analyzer.get_newsapi_trends(
                query='technology',  # Simplified query
                category='technology',  # Must be one of newsdata.io's supported categories
                country='us'  # Single country code
            )
            if news_trends:
                logger.info(f"Retrieved {len(news_trends)} news articles")
            else:
                logger.warning("Failed to fetch newsdata.io trends - check your API key")
        except Exception as e:
            logger.error(f"newsdata.io API error: {str(e)}")

        # Remove duplicate newsapi setup and continue with other sources
        analyzer.set_reddit_credentials(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRECT"),
            user_agent="TrendAnalyzer/1.0"
        )
        
        # Fetch and store trends with error handling
        trends_data = []
        
        try:
            news_trends = analyzer.get_newsapi_trends(country='us', category='technology')
            if news_trends:
                trends_data.extend(news_trends)
            else:
                logger.warning("Failed to fetch NewsAPI trends - check your API key")
        except Exception as e:
            logger.error(f"NewsAPI error: {str(e)}")
        
        try:
            reddit_trends = analyzer.get_reddit_api_trends(subreddit='technology')
            if reddit_trends:
                trends_data.extend(reddit_trends)
        except Exception as e:
            logger.error(f"Reddit API error: {str(e)}")
        
        try:
            hn_trends = analyzer.get_hacker_news_trends()
            if hn_trends:
                trends_data.extend(hn_trends)
        except Exception as e:
            logger.error(f"Hacker News API error: {str(e)}")
        
        try:
            github_trends = analyzer.get_github_trends(language='python')
            if github_trends:
                trends_data.extend(github_trends)
        except Exception as e:
            logger.error(f"GitHub trends error: {str(e)}")
        
        try:
            stack_trends = analyzer.get_stackexchange_hot_questions()
            if stack_trends:
                trends_data.extend(stack_trends)
        except Exception as e:
            logger.error(f"Stack Exchange API error: {str(e)}")
        
        if not trends_data:
            logger.error("No trends data could be fetched from any source")
            return
        
        # Analyze Reddit comments if available
        if reddit_trends:
            try:
                first_trend = reddit_trends[0]
                comments = analyzer.fetch_reddit_comments(first_trend['url'])
                if comments:
                    analyzer.analyze_posts(comments)
            except Exception as e:
                logger.error(f"Error analyzing Reddit comments: {str(e)}")
        
        # Generate analytics
        try:
            metrics = analyzer.get_trend_metrics(hours=24, limit=10)
            hashtags = analyzer.generate_trending_hashtags(hours=24)
            wordcloud = analyzer.generate_word_cloud(hours=24)
            
            # Print results
            print("\nTop Trends:")
            for trend in metrics[:5]:
                print(f"- {trend['name']} ({trend['trend_source']})")
            
            print("\nTop Hashtags:")
            for hashtag in hashtags[:5]:
                print(f"- #{hashtag['hashtag']} (mentioned {hashtag['count']} times)")
            
            if wordcloud:
                print("\nWord cloud generated successfully!")
                
        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
        
    except Exception as e:
        logger.error(f"Critical error in main function: {str(e)}")
        raise

if __name__ == "__main__":
    main()