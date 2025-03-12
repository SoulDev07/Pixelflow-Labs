import os
import json
import time
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from pymongo import MongoClient
from dotenv import load_dotenv
import requests
from transformers import pipeline
from pytrends.request import TrendReq
from googleapiclient.discovery import build
import praw
import tweepy
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

class TrendAnalyzer:
    def __init__(self, domain):
        """
        Initialize the TrendAnalyzer with the specified domain.
        
        Args:
            domain (str): The domain/industry to analyze trends for (e.g., "fashion", "technology")
        """
        self.domain = domain
        self.now = datetime.utcnow()
        
        # Connect to MongoDB
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client['trend_analysis']
        self.collection = self.db['domain_trends']
        
        # Initialize sentiment analyzer
        self.sentiment_analyzer = pipeline('sentiment-analysis')
        
        # API keys and configurations
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.reddit_user_agent = os.getenv('REDDIT_USER_AGENT', f'TrendAnalyzer/1.0')
        
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.twitter_api_key = os.getenv('TWITTER_API_KEY')
        self.twitter_api_secret = os.getenv('TWITTER_API_SECRET')
        self.twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.twitter_access_secret = os.getenv('TWITTER_ACCESS_SECRET')
        
        # Initialize API clients
        self._initialize_api_clients()
        
        # Set time ranges
        self.start_date = (self.now - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.end_date = self.now.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Results dictionary
        self.results = {
            'domain': self.domain,
            'timestamp': self.now,
            'google_trends': {},
            'youtube_trends': {},
            'reddit_trends': {},
            'twitter_trends': {},
            'keywords': {},
            'hashtags': {},
            'sentiment_analysis': {},
            'ad_recommendations': {}
        }

    def _initialize_api_clients(self):
        """Initialize API clients for different platforms."""
        # Google Trends
        self.pytrends = TrendReq(hl='en-US', timeout=(10, 25))
        
        # YouTube
        if self.google_api_key:
            self.youtube = build('youtube', 'v3', developerKey=self.google_api_key)
        else:
            self.youtube = None
            print("Warning: Google API key not found. YouTube analysis will be skipped.")
        
        # Reddit
        if self.reddit_client_id and self.reddit_client_secret:
            self.reddit = praw.Reddit(
                client_id=self.reddit_client_id,
                client_secret=self.reddit_client_secret,
                user_agent=self.reddit_user_agent
            )
        else:
            self.reddit = None
            print("Warning: Reddit API credentials not found. Reddit analysis will be skipped.")
        
        # Twitter/X
        if self.twitter_api_key and self.twitter_api_secret and self.twitter_access_token and self.twitter_access_secret:
            auth = tweepy.OAuth1UserHandler(
                self.twitter_api_key, 
                self.twitter_api_secret,
                self.twitter_access_token,
                self.twitter_access_secret
            )
            self.twitter = tweepy.API(auth)
        elif self.twitter_bearer_token:
            self.twitter = tweepy.Client(bearer_token=self.twitter_bearer_token)
        else:
            self.twitter = None
            print("Warning: Twitter API credentials not found. Twitter analysis will be skipped.")

    def analyze_google_trends(self):
        """Analyze Google Trends for the specified domain."""
        print(f"Analyzing Google Trends for domain: {self.domain}")
        
        try:
            # Get related queries and topics
            self.pytrends.build_payload([self.domain], timeframe='today 1-m')
            
            # Get related topics
            related_topics = self.pytrends.related_topics()
            
            # Get related queries
            related_queries = self.pytrends.related_queries()
            
            # Get interest over time
            interest_over_time = self.pytrends.interest_over_time()
            
            # Process and store the data
            if self.domain in related_topics:
                top_topics = related_topics[self.domain]['top']
                if isinstance(top_topics, pd.DataFrame) and not top_topics.empty:
                    self.results['google_trends']['top_topics'] = top_topics.head(10).to_dict('records')
            
            if self.domain in related_queries:
                top_queries = related_queries[self.domain]['top']
                if isinstance(top_queries, pd.DataFrame) and not top_queries.empty:
                    self.results['google_trends']['top_queries'] = top_queries.head(10).to_dict('records')
            
            if not interest_over_time.empty:
                self.results['google_trends']['interest_over_time'] = interest_over_time[self.domain].to_dict()
            
            # Extract keywords from related queries and topics
            keywords = []
            if 'top_queries' in self.results['google_trends']:
                for item in self.results['google_trends']['top_queries']:
                    keywords.append(item.get('query', ''))
            
            if 'top_topics' in self.results['google_trends']:
                for item in self.results['google_trends']['top_topics']:
                    keywords.append(item.get('topic_title', ''))
            
            self.results['keywords']['google_trends'] = keywords
            
            print("Google Trends analysis completed.")
        except Exception as e:
            print(f"Error analyzing Google Trends: {e}")
            self.results['google_trends']['error'] = str(e)

    def analyze_youtube_trends(self):
        """Analyze YouTube trends related to the domain."""
        print(f"Analyzing YouTube trends for domain: {self.domain}")
        
        if not self.youtube:
            self.results['youtube_trends']['error'] = "YouTube API not configured"
            return
        
        try:
            # Search for videos related to the domain
            request = self.youtube.search().list(
                part="snippet",
                q=self.domain,
                type="video",
                order="viewCount",
                publishedAfter=self.start_date,
                publishedBefore=self.end_date,
                maxResults=50
            )
            
            response = request.execute()
            
            videos = []
            video_ids = []
            
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                video_ids.append(video_id)
                videos.append({
                    'id': video_id,
                    'title': item['snippet']['title'],
                    'channel_id': item['snippet']['channelId'],
                    'published_at': item['snippet']['publishedAt'],
                    'description': item['snippet']['description']
                })
            
            # Get video statistics
            if video_ids:
                stats_request = self.youtube.videos().list(
                    part="statistics,contentDetails",
                    id=','.join(video_ids[:50])  # API limit
                )
                
                stats_response = stats_request.execute()
                
                # Map statistics to videos
                stats_map = {item['id']: item for item in stats_response.get('items', [])}
                
                for video in videos:
                    if video['id'] in stats_map:
                        stats = stats_map[video['id']].get('statistics', {})
                        video['views'] = stats.get('viewCount', 0)
                        video['likes'] = stats.get('likeCount', 0)
                        video['comments'] = stats.get('commentCount', 0)
            
            # Process videos
            if videos:
                # Sort by views
                videos.sort(key=lambda x: int(x.get('views', 0)), reverse=True)
                self.results['youtube_trends']['top_videos'] = videos[:10]
                
                # Extract keywords from titles and descriptions
                keywords = []
                for video in videos:
                    keywords.extend(self._extract_keywords(video.get('title', '')))
                    keywords.extend(self._extract_keywords(video.get('description', '')))
                
                self.results['keywords']['youtube'] = list(set(keywords))
                
                # Analyze sentiment of video titles
                self.results['sentiment_analysis']['youtube_titles'] = self._analyze_sentiment(
                    [video.get('title', '') for video in videos]
                )
            
            print("YouTube trends analysis completed.")
        except Exception as e:
            print(f"Error analyzing YouTube trends: {e}")
            self.results['youtube_trends']['error'] = str(e)

    def analyze_reddit_trends(self):
        """Analyze Reddit trends related to the domain."""
        print(f"Analyzing Reddit trends for domain: {self.domain}")
        
        if not self.reddit:
            self.results['reddit_trends']['error'] = "Reddit API not configured"
            return
        
        try:
            # Find relevant subreddits for the domain
            subreddits = [self.domain]
            subreddit_info = []
            
            # Search for relevant subreddits
            for sr in self.reddit.subreddits.search(self.domain, limit=5):
                subreddits.append(sr.display_name)
                subreddit_info.append({
                    'name': sr.display_name,
                    'subscribers': sr.subscribers,
                    'description': sr.public_description
                })
            
            self.results['reddit_trends']['related_subreddits'] = subreddit_info
            
            # Get top posts from relevant subreddits
            all_posts = []
            post_texts = []
            hashtags = []
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    for post in subreddit.top(time_filter='month', limit=20):
                        if post.created_utc >= (datetime.now() - timedelta(days=30)).timestamp():
                            post_data = {
                                'title': post.title,
                                'score': post.score,
                                'url': f"https://www.reddit.com{post.permalink}",
                                'created_utc': post.created_utc,
                                'num_comments': post.num_comments
                            }
                            
                            all_posts.append(post_data)
                            post_texts.append(post.title)
                            
                            # Extract hashtags from title and selftext
                            hashtags.extend(self._extract_hashtags(post.title))
                            if hasattr(post, 'selftext'):
                                hashtags.extend(self._extract_hashtags(post.selftext))
                except Exception as e:
                    print(f"Error processing subreddit {subreddit_name}: {e}")
            
            # Sort posts by score
            all_posts.sort(key=lambda x: x.get('score', 0), reverse=True)
            self.results['reddit_trends']['top_posts'] = all_posts[:10]
            
            # Extract keywords from post titles
            keywords = []
            for post in all_posts:
                keywords.extend(self._extract_keywords(post.get('title', '')))
            
            self.results['keywords']['reddit'] = list(set(keywords))
            self.results['hashtags']['reddit'] = list(set(hashtags))
            
            # Analyze sentiment of post titles
            self.results['sentiment_analysis']['reddit_posts'] = self._analyze_sentiment(post_texts)
            
            print("Reddit trends analysis completed.")
        except Exception as e:
            print(f"Error analyzing Reddit trends: {e}")
            self.results['reddit_trends']['error'] = str(e)

    def analyze_twitter_trends(self):
        """Analyze Twitter/X trends related to the domain."""
        print(f"Analyzing Twitter trends for domain: {self.domain}")
        
        if not self.twitter:
            self.results['twitter_trends']['error'] = "Twitter API not configured"
            return
        
        try:
            # Get trending topics
            if isinstance(self.twitter, tweepy.API):
                trends = self.twitter.get_place_trends(id=1)  # 1 = global
                trend_data = trends[0]['trends']
                
                self.results['twitter_trends']['global_trends'] = [
                    {'name': trend['name'], 'tweet_volume': trend['tweet_volume']}
                    for trend in trend_data if trend['tweet_volume']
                ][:10]
                
                # Search for tweets related to the domain
                tweets = self.twitter.search_tweets(
                    q=self.domain,
                    lang="en",
                    count=100,
                    result_type="popular"
                )
                
                tweet_data = []
                tweet_texts = []
                hashtags = []
                
                for tweet in tweets:
                    tweet_info = {
                        'id': tweet.id_str,
                        'text': tweet.text,
                        'created_at': tweet.created_at.isoformat(),
                        'retweet_count': tweet.retweet_count,
                        'favorite_count': tweet.favorite_count
                    }
                    
                    tweet_data.append(tweet_info)
                    tweet_texts.append(tweet.text)
                    
                    if hasattr(tweet, 'entities') and 'hashtags' in tweet.entities:
                        for hashtag in tweet.entities['hashtags']:
                            hashtags.append(hashtag['text'].lower())
                
                # Sort tweets by popularity
                tweet_data.sort(key=lambda x: (x.get('retweet_count', 0) + x.get('favorite_count', 0)), reverse=True)
                self.results['twitter_trends']['top_tweets'] = tweet_data[:10]
                
            elif isinstance(self.twitter, tweepy.Client):
                # Using v2 API with Client
                query = f"{self.domain} -is:retweet"
                tweets = self.twitter.search_recent_tweets(
                    query=query,
                    max_results=100,
                    tweet_fields=['created_at', 'public_metrics', 'entities']
                )
                
                tweet_data = []
                tweet_texts = []
                hashtags = []
                
                if tweets.data:
                    for tweet in tweets.data:
                        tweet_info = {
                            'id': tweet.id,
                            'text': tweet.text,
                            'created_at': tweet.created_at.isoformat(),
                            'retweet_count': tweet.public_metrics['retweet_count'],
                            'like_count': tweet.public_metrics['like_count']
                        }
                        
                        tweet_data.append(tweet_info)
                        tweet_texts.append(tweet.text)
                        
                        if hasattr(tweet, 'entities') and 'hashtags' in tweet.entities:
                            for hashtag in tweet.entities['hashtags']:
                                hashtags.append(hashtag['tag'].lower())
                    
                    # Sort tweets by popularity
                    tweet_data.sort(key=lambda x: (x.get('retweet_count', 0) + x.get('like_count', 0)), reverse=True)
                    self.results['twitter_trends']['top_tweets'] = tweet_data[:10]
            
            # Process hashtags and extract keywords
            if hashtags:
                hashtag_counter = {}
                for tag in hashtags:
                    if tag in hashtag_counter:
                        hashtag_counter[tag] += 1
                    else:
                        hashtag_counter[tag] = 1
                
                # Sort hashtags by frequency
                sorted_hashtags = sorted(hashtag_counter.items(), key=lambda x: x[1], reverse=True)
                self.results['hashtags']['twitter'] = [{'tag': tag, 'count': count} for tag, count in sorted_hashtags[:20]]
            
            # Extract keywords from tweets
            keywords = []
            for text in tweet_texts:
                keywords.extend(self._extract_keywords(text))
            
            self.results['keywords']['twitter'] = list(set(keywords))
            
            # Analyze sentiment of tweets
            self.results['sentiment_analysis']['tweets'] = self._analyze_sentiment(tweet_texts)
            
            print("Twitter trends analysis completed.")
        except Exception as e:
            print(f"Error analyzing Twitter trends: {e}")
            self.results['twitter_trends']['error'] = str(e)

    def _analyze_sentiment(self, texts):
        """
        Analyze the sentiment of a list of texts.
        
        Args:
            texts (list): List of strings to analyze
            
        Returns:
            dict: Sentiment analysis results
        """
        if not texts:
            return {'error': 'No texts provided for sentiment analysis'}
        
        try:
            # Sample texts if there are too many
            sample_size = min(100, len(texts))
            sampled_texts = np.random.choice(texts, sample_size, replace=False).tolist()
            
            # Analyze sentiment in batches
            results = []
            batch_size = 10
            
            for i in tqdm(range(0, len(sampled_texts), batch_size), desc="Analyzing sentiment"):
                batch = sampled_texts[i:i+batch_size]
                batch_results = self.sentiment_analyzer(batch)
                results.extend(batch_results)
            
            # Count sentiment categories
            sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
            sentiment_scores = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
            
            for result in results:
                label = result['label']
                score = result['score']
                
                sentiment_counts[label] += 1
                sentiment_scores[label] += score
            
            # Calculate average scores
            for label in sentiment_scores:
                if sentiment_counts[label] > 0:
                    sentiment_scores[label] /= sentiment_counts[label]
            
            # Calculate percentages
            total = sum(sentiment_counts.values())
            sentiment_percentages = {
                label: (count / total) * 100 for label, count in sentiment_counts.items()
            }
            
            return {
                'counts': sentiment_counts,
                'percentages': sentiment_percentages,
                'average_scores': sentiment_scores,
                'overall_sentiment': max(sentiment_counts.items(), key=lambda x: x[1])[0],
                'sample_size': sample_size
            }
        
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {'error': str(e)}

    def _extract_keywords(self, text):
        """
        Extract keywords from text.
        
        Args:
            text (str): Text to extract keywords from
            
        Returns:
            list: List of keywords
        """
        if not text:
            return []
        
        # Remove common words and punctuation
        import re
        from collections import Counter
        
        # Convert to lowercase and split
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stopwords
        stopwords = {
            'the', 'and', 'to', 'of', 'a', 'in', 'for', 'is', 'on', 'that', 'by', 'this',
            'with', 'i', 'you', 'it', 'not', 'or', 'be', 'are', 'from', 'at', 'as', 'your',
            'all', 'have', 'new', 'more', 'an', 'was', 'we', 'will', 'can', 'us', 'about'
        }
        
        filtered_words = [word for word in words if word not in stopwords]
        
        # Return unique keywords
        return list(set(filtered_words))

    def _extract_hashtags(self, text):
        """
        Extract hashtags from text.
        
        Args:
            text (str): Text to extract hashtags from
            
        Returns:
            list: List of hashtags (without #)
        """
        if not text:
            return []
        
        import re
        hashtags = re.findall(r'#(\w+)', text)
        return [tag.lower() for tag in hashtags]

    def synthesize_results(self):
        """Synthesize results and generate ad recommendations."""
        print("Synthesizing results and generating ad recommendations...")
        
        # Compile all keywords
        all_keywords = []
        for platform, keywords in self.results['keywords'].items():
            all_keywords.extend(keywords)
        
        # Count keyword frequency
        from collections import Counter
        keyword_counter = Counter(all_keywords)
        
        # Get top keywords
        top_keywords = [{'keyword': k, 'count': v} for k, v in keyword_counter.most_common(20)]
        self.results['top_keywords'] = top_keywords
        
        # Compile all hashtags
        all_hashtags = []
        for platform, hashtags in self.results['hashtags'].items():
            if isinstance(hashtags, list):
                if all(isinstance(item, dict) for item in hashtags):
                    all_hashtags.extend([item['tag'] for item in hashtags])
                else:
                    all_hashtags.extend(hashtags)
        
        # Count hashtag frequency
        hashtag_counter = Counter(all_hashtags)
        
        # Get top hashtags
        top_hashtags = [{'hashtag': h, 'count': c} for h, c in hashtag_counter.most_common(20)]
        self.results['top_hashtags'] = top_hashtags
        
        # Calculate overall sentiment
        sentiment_platforms = [
            platform for platform, data in self.results['sentiment_analysis'].items()
            if isinstance(data, dict) and 'overall_sentiment' in data
        ]
        
        if sentiment_platforms:
            sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
            
            for platform in sentiment_platforms:
                overall = self.results['sentiment_analysis'][platform]['overall_sentiment']
                sentiment_counts[overall] += 1
            
            overall_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]
            self.results['overall_sentiment'] = overall_sentiment
        
        # Generate ad recommendations
        self._generate_ad_recommendations()
        
        print("Results synthesis completed.")

    def _generate_ad_recommendations(self):
        """Generate ad recommendations based on the analysis."""
        recommendations = {
            'tone': 'neutral',
            'keywords': [],
            'hashtags': [],
            'themes': [],
            'platforms': []
        }
        
        # Determine tone based on sentiment
        if 'overall_sentiment' in self.results:
            sentiment = self.results['overall_sentiment']
            if sentiment == 'POSITIVE':
                recommendations['tone'] = 'positive and upbeat'
            elif sentiment == 'NEGATIVE':
                recommendations['tone'] = 'solution-oriented and reassuring'
            else:
                recommendations['tone'] = 'informative and balanced'
        
        # Recommend top keywords
        if 'top_keywords' in self.results:
            recommendations['keywords'] = [item['keyword'] for item in self.results['top_keywords'][:10]]
        
        # Recommend top hashtags
        if 'top_hashtags' in self.results:
            recommendations['hashtags'] = [item['hashtag'] for item in self.results['top_hashtags'][:5]]
        
        # Determine best platforms
        platforms_engagement = {}
        
        if 'youtube_trends' in self.results and 'top_videos' in self.results['youtube_trends']:
            if len(self.results['youtube_trends']['top_videos']) > 0:
                total_views = sum(int(video.get('views', 0)) for video in self.results['youtube_trends']['top_videos'])
                platforms_engagement['YouTube'] = total_views
        
        if 'reddit_trends' in self.results and 'top_posts' in self.results['reddit_trends']:
            if len(self.results['reddit_trends']['top_posts']) > 0:
                total_score = sum(post.get('score', 0) for post in self.results['reddit_trends']['top_posts'])
                platforms_engagement['Reddit'] = total_score
        
        if 'twitter_trends' in self.results and 'top_tweets' in self.results['twitter_trends']:
            if len(self.results['twitter_trends']['top_tweets']) > 0:
                total_engagement = sum((tweet.get('retweet_count', 0) + tweet.get('favorite_count', 0)) 
                                     for tweet in self.results['twitter_trends']['top_tweets'])
                platforms_engagement['Twitter'] = total_engagement
        
        # Sort platforms by engagement
        sorted_platforms = sorted(platforms_engagement.items(), key=lambda x: x[1], reverse=True)
        recommendations['platforms'] = [platform for platform, _ in sorted_platforms]
        
        # Suggest themes based on keywords
        if 'top_keywords' in self.results:
            keywords = [item['keyword'] for item in self.results['top_keywords'][:15]]
            
            # Group related keywords to identify themes
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.cluster import KMeans
            
            if len(keywords) >= 5:  # Need enough keywords for meaningful clustering
                try:
                    # Create a document for each keyword
                    keyword_docs = [f"{kw} " * 5 for kw in keywords]
                    
                    # Vectorize
                    vectorizer = CountVectorizer()
                    X = vectorizer.fit_transform(keyword_docs)
                    
                    # Cluster
                    n_clusters = min(5, len(keywords) // 2)
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                    kmeans.fit(X)
                    
                    # Get clusters
                    clusters = {}
                    for i, label in enumerate(kmeans.labels_):
                        if label not in clusters:
                            clusters[label] = []
                        clusters[label].append(keywords[i])
                    
                    # Extract themes
                    for cluster_keywords in clusters.values():
                        if len(cluster_keywords) >= 2:
                            recommendations['themes'].append(cluster_keywords)
                except Exception as e:
                    print(f"Error generating themes: {e}")
        
        self.results['ad_recommendations'] = recommendations

    def run_analysis(self):
        """Run the complete analysis pipeline."""
        print(f"Starting trend analysis for domain: {self.domain}")
        
        # Run analysis for each platform
        self.analyze_google_trends()
        self.analyze_youtube_trends()
        self.analyze_reddit_trends()
        self.analyze_twitter_trends()
        
        # Synthesize results
        self.synthesize_results()
        
        # Save to MongoDB
        self.save_to_mongodb()
        
        print(f"Trend analysis completed for domain: {self.domain}")
        return self.results

    def save_to_mongodb(self):
        """Save results to MongoDB."""
        print("Saving results to MongoDB...")
        
        # Convert datetime objects to strings for MongoDB
        import json
        
        # Use ISO format for datetime
        results_copy = self.results.copy()
        results_copy['timestamp'] = self.now.isoformat()
        
        # Remove any non-serializable objects
        try:
            json.dumps(results_copy)
        except TypeError as e:
            print(f"Warning: Non-serializable objects detected: {e}")
            # Handle non-serializable objects here if needed
        
        # Store in MongoDB
        result = self.collection.insert_one(results_copy)
        
        print(f"Results saved to MongoDB with ID: {result.inserted_id}")
        return result.inserted_id

# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze social media trends for a specific domain')
    parser.add_argument('domain', type=str, help='Domain to analyze (e.g., "fashion", "technology")')
    
    args = parser.parse_args()
    
    analyzer = TrendAnalyzer(args.domain)
    results = analyzer.run_analysis()
    
    # Print a summary
    print("\n=== Analysis Summary ===")
    print(f"Domain: {results['domain']}")
    print(f"Timestamp: {results['timestamp']}")
    
    print("\nTop Keywords:")
    if 'top_keywords' in results:
        for kw in results['top_keywords'][:10]:
            print(f"- {kw['keyword']} ({kw['count']})")
    
    print("\nTop Hashtags:")
    if 'top_hashtags' in results:
        for tag in results['top_hashtags'][:5]:
            print(f"- #{tag['hashtag']} ({tag['count']})")
    
    print("\nOverall Sentiment:")
    if 'overall_sentiment' in results:
        print(f"- {results['overall_sentiment']}")
    
    print("\nAd Recommendations:")
    if 'ad_recommendations' in results:
        rec = results['ad_recommendations']
        print(f"- Tone: {rec['tone']}")
        print("- Keywords: " + ", ".join(rec['keywords'][:5]))
        print("- Hashtags: " + ", ".join(['#'+tag for tag in rec['hashtags'][:3]]))
        print("- Recommended Platforms: " + ", ".join(rec['platforms']))