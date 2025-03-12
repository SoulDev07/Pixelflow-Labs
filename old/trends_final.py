import os
import time
import schedule
import requests
import json
import re
import datetime
from collections import Counter
from pymongo import MongoClient
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from textblob import TextBlob
import praw
from googleapiclient.discovery import build
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from transformers import pipeline
from atproto import Client
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trend_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Download NLTK resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.error(f"Failed to download NLTK resources: {e}")

# Initialize MongoDB client
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["PixelFlowLabs"]
collection = db["analysis"]

# Initialize sentiment analysis pipeline
try:
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
except Exception as e:
    logger.error(f"Failed to load transformer model: {e}")
    sentiment_analyzer = None

# Check if a text is related to a domain
def is_domain_related(text, domain_keywords):
    if not text or not domain_keywords:
        return False
    
    text = text.lower()
    for keyword in domain_keywords:
        if keyword.lower() in text:
            return True
    return False

# Initialize API clients
def init_reddit():
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "trend_analyzer_script v1.0")
        )
        return reddit
    except Exception as e:
        logger.error(f"Failed to initialize Reddit client: {e}")
        return None

def init_youtube():
    try:
        youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))
        return youtube
    except Exception as e:
        logger.error(f"Failed to initialize YouTube client: {e}")
        return None

def init_bluesky():
    try:
        atproto_client = Client()
        atproto_client.login(os.getenv("BLUESKY_EMAIL"), os.getenv("BLUESKY_PASSWORD"))
        return atproto_client
    except Exception as e:
        logger.error(f"Failed to initialize Bluesky client: {e}")
        return None

# Text preprocessing functions
def preprocess_text(text):
    if not text:
        return ""
    # Convert to lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    return text

def extract_hashtags(text):
    if not text:
        return []
    # Find all hashtags in the text
    hashtags = re.findall(r'#(\w+)', text)
    return hashtags

def remove_stopwords(text):
    if not text:
        return ""
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_text = [word for word in word_tokens if word not in stop_words]
    return ' '.join(filtered_text)

def get_top_words(texts, n=10):
    """Get top N words from a list of texts"""
    # Initialize Counter
    word_counts = Counter()
    
    # Get stopwords
    stop_words = set(stopwords.words('english'))
    
    for text in texts:
        if not isinstance(text, str):
            continue
            
        # Tokenize and clean text
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        words = word_tokenize(text)
        
        # Filter words
        words = [word for word in words 
                if word.isalnum() 
                and len(word) > 2 
                and word not in stop_words]
        
        # Update counter
        word_counts.update(words)
    
    # Return top N words
    return dict(word_counts.most_common(n))

# Sentiment analysis functions
def analyze_sentiment_textblob(text):
    if not text:
        return {"polarity": 0, "subjectivity": 0}
    analysis = TextBlob(text)
    return {
        "polarity": analysis.sentiment.polarity,
        "subjectivity": analysis.sentiment.subjectivity
    }

def analyze_sentiment_transformers(text):
    if not sentiment_analyzer or not text:
        return {"label": "NEUTRAL", "score": 0.5}
    try:
        result = sentiment_analyzer(text[:512])[0]  # Limit text length for the model
        return result
    except Exception as e:
        logger.error(f"Transformer sentiment analysis error: {e}")
        return {"label": "NEUTRAL", "score": 0.5}

def get_aggregate_sentiment(texts):
    if not texts:
        return {
            "textblob": {"avg_polarity": 0, "avg_subjectivity": 0},
            "transformer": {"positive_percentage": 50, "avg_confidence": 0.5}
        }
    
    # TextBlob sentiment
    polarities = []
    subjectivities = []
    
    # Transformer sentiment
    positive_count = 0
    confidence_scores = []
    
    for text in texts:
        if text:
            # TextBlob analysis
            tb_sentiment = analyze_sentiment_textblob(text)
            polarities.append(tb_sentiment["polarity"])
            subjectivities.append(tb_sentiment["subjectivity"])
            
            # Transformer analysis
            if sentiment_analyzer:
                tf_sentiment = analyze_sentiment_transformers(text)
                if tf_sentiment["label"] == "POSITIVE":
                    positive_count += 1
                confidence_scores.append(tf_sentiment["score"])
    
    total = len(texts) if texts else 1
    
    return {
        "textblob": {
            "avg_polarity": sum(polarities) / len(polarities) if polarities else 0,
            "avg_subjectivity": sum(subjectivities) / len(subjectivities) if subjectivities else 0
        },
        "transformer": {
            "positive_percentage": (positive_count / total) * 100 if total > 0 else 50,
            "avg_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        }
    }

# Data fetching functions
def fetch_reddit_trends(domain_keywords=None):
    reddit = init_reddit()
    if not reddit:
        return {"success": False, "data": {}}
    
    try:
        # Get trending subreddits
        trending_subreddits = []
        
        # Get domain specific subreddits if domain keywords provided
        if domain_keywords:
            search_query = " OR ".join(domain_keywords)
            for subreddit in reddit.subreddits.search(search_query, limit=10):
                trending_subreddits.append({
                    "name": subreddit.display_name,
                    "subscribers": subreddit.subscribers,
                    "description": subreddit.public_description
                })
        # Otherwise get popular subreddits
        else:
            for subreddit in reddit.subreddits.popular(limit=10):
                trending_subreddits.append({
                    "name": subreddit.display_name,
                    "subscribers": subreddit.subscribers,
                    "description": subreddit.public_description
                })
        
        # Get hot posts
        hot_posts = []
        subreddit_to_search = "all"
        
        # If domain keywords provided, try to find domain-specific posts
        if domain_keywords:
            search_query = " OR ".join(domain_keywords)
            for submission in reddit.subreddit("all").search(search_query, sort="hot", limit=25):
                hot_posts.append({
                    "title": submission.title,
                    "subreddit": submission.subreddit.display_name,
                    "score": submission.score,
                    "comments": submission.num_comments,
                    "url": submission.url,
                    "created_utc": datetime.datetime.fromtimestamp(submission.created_utc).isoformat()
                })
        else:
            for submission in reddit.subreddit("all").hot(limit=25):
                hot_posts.append({
                    "title": submission.title,
                    "subreddit": submission.subreddit.display_name,
                    "score": submission.score,
                    "comments": submission.num_comments,
                    "url": submission.url,
                    "created_utc": datetime.datetime.fromtimestamp(submission.created_utc).isoformat()
                })
        
        # Filter by domain if needed
        if domain_keywords and hot_posts:
            hot_posts = [post for post in hot_posts if is_domain_related(post.get("title", ""), domain_keywords)]
        
        return {
            "success": True,
            "data": {
                "trending_subreddits": trending_subreddits,
                "hot_posts": hot_posts
            }
        }
    except Exception as e:
        logger.error(f"Error fetching Reddit trends: {e}")
        return {"success": False, "data": {}}

def fetch_youtube_trends(domain_keywords=None):
    youtube = init_youtube()
    if not youtube:
        return {"success": False, "data": {}}
    
    try:
        trending_videos = []
        
        # If domain keywords are provided, search for videos related to the domain
        if domain_keywords:
            for keyword in domain_keywords:
                search_request = youtube.search().list(
                    part="snippet",
                    q=keyword,
                    type="video",
                    order="viewCount", 
                    maxResults=10
                )
                search_response = search_request.execute()
                
                # Get video IDs from search results
                video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
                
                if video_ids:
                    # Get detailed information for these videos
                    videos_request = youtube.videos().list(
                        part="snippet,statistics",
                        id=','.join(video_ids)
                    )
                    videos_response = videos_request.execute()
                    
                    for item in videos_response.get('items', []):
                        snippet = item.get('snippet', {})
                        statistics = item.get('statistics', {})
                        
                        trending_videos.append({
                            "title": snippet.get("title", ""),
                            "channel": snippet.get("channelTitle", ""),
                            "description": snippet.get("description", ""),
                            "published_at": snippet.get("publishedAt", ""),
                            "view_count": int(statistics.get("viewCount", 0)),
                            "like_count": int(statistics.get("likeCount", 0)),
                            "comment_count": int(statistics.get("commentCount", 0)),
                            "video_id": item.get("id", ""),
                            "keyword": keyword
                        })
        else:
            # Get general trending videos
            trending_request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode="US",
                maxResults=25
            )
            trending_response = trending_request.execute()
            
            for item in trending_response.get("items", []):
                snippet = item.get("snippet", {})
                statistics = item.get("statistics", {})
                
                trending_videos.append({
                    "title": snippet.get("title", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "description": snippet.get("description", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "view_count": int(statistics.get("viewCount", 0)),
                    "like_count": int(statistics.get("likeCount", 0)),
                    "comment_count": int(statistics.get("commentCount", 0)),
                    "video_id": item.get("id", "")
                })
        
        # Remove duplicates by video_id
        seen_ids = set()
        unique_videos = []
        for video in trending_videos:
            if video["video_id"] not in seen_ids:
                seen_ids.add(video["video_id"])
                unique_videos.append(video)
        
        return {
            "success": True,
            "data": {
                "trending_videos": unique_videos[:25]  # Limit to 25 videos
            }
        }
    except Exception as e:
        logger.error(f"Error fetching YouTube trends: {e}")
        return {"success": False, "data": {}}

def fetch_bluesky_trends(domain_keywords=None):
    client = init_bluesky()
    if not client:
        logger.error("Failed to initialize Bluesky client")
        return {"success": False, "data": {}}
    
    try:
        posts = []
        hashtags = []
        
        # Get feed generator for trending content
        feed_generator = "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot"
        
        try:
            # Log authentication status
            logger.info("Bluesky client initialized, attempting to fetch feed")
            
            # Get trending feed
            feed = client.app.bsky.feed.get_feed({
                'feed': feed_generator,
                'limit': 100
            }, {
                'headers': {
                    'Accept-Language': "en",
                }
            })
            
            logger.info(f"Successfully retrieved Bluesky feed with {len(feed.feed) if hasattr(feed, 'feed') else 0} items")
            
            if hasattr(feed, 'feed'):
                for feed_view in feed.feed:
                    try:
                        # Extract post data with extensive error handling
                        post = feed_view.post
                        
                        if not hasattr(post, 'record'):
                            logger.warning("Post missing record attribute")
                            continue
                            
                        post_text = post.record.text if hasattr(post.record, 'text') else ''
                        
                        # Extract hashtags
                        post_hashtags = extract_hashtags(post_text)
                        hashtags.extend(post_hashtags)
                        
                        # Skip if domain filtering is enabled and post doesn't match
                        if domain_keywords and not is_domain_related(post_text, domain_keywords):
                            continue
                        
                        # Get engagement metrics
                        created_at = post.record.createdAt if hasattr(post.record, 'createdAt') else ''
                        
                        posts.append({
                            "text": post_text,
                            "created_at": created_at,
                            "likes": getattr(post, 'likeCount', 0),
                            "replies": getattr(post, 'replyCount', 0),
                            "reposts": getattr(post, 'repostCount', 0),
                            "hashtags": post_hashtags
                        })
                    except Exception as e:
                        logger.warning(f"Error processing individual Bluesky post: {e}")
                        continue
            else:
                logger.warning("Feed response missing 'feed' attribute")
                
        except Exception as e:
            # Fallback to timeline if get_feed fails
            logger.warning(f"Failed to get trending feed, falling back to timeline: {e}")
            
            try:
                timeline = client.app.bsky.feed.get_timeline({'limit': 25})
                
                logger.info(f"Successfully retrieved Bluesky timeline with {len(timeline.feed) if hasattr(timeline, 'feed') else 0} items")
                
                if hasattr(timeline, 'feed'):
                    for feed_view in timeline.feed:
                        try:
                            post = feed_view.post
                            
                            if not hasattr(post, 'record'):
                                logger.warning("Timeline post missing record attribute")
                                continue
                                
                            post_text = post.record.text if hasattr(post.record, 'text') else ''
                            
                            post_hashtags = extract_hashtags(post_text)
                            hashtags.extend(post_hashtags)
                            
                            if domain_keywords and not is_domain_related(post_text, domain_keywords):
                                continue
                            
                            created_at = post.record.createdAt if hasattr(post.record, 'createdAt') else ''
                            
                            posts.append({
                                "text": post_text,
                                "created_at": created_at,
                                "likes": getattr(post, 'likeCount', 0),
                                "replies": getattr(post, 'replyCount', 0),
                                "reposts": getattr(post, 'repostCount', 0),
                                "hashtags": post_hashtags
                            })
                        except Exception as e:
                            logger.warning(f"Error processing individual timeline post: {e}")
                            continue
                else:
                    logger.warning("Timeline response missing 'feed' attribute")
            except Exception as e:
                logger.error(f"Failed to fetch timeline: {e}")
        
        # Count hashtag frequency
        hashtag_counts = Counter(hashtags)
        
        # Filter hashtags by domain if needed
        if domain_keywords:
            hashtag_counts = Counter({
                tag: count for tag, count in hashtag_counts.items()
                if any(keyword.lower() in tag.lower() for keyword in domain_keywords)
            })
        
        logger.info(f"Processed {len(posts)} Bluesky posts and found {len(hashtag_counts)} unique hashtags")
        
        return {
            "success": True,
            "data": {
                "popular_posts": posts,
                "trending_hashtags": dict(hashtag_counts.most_common(20))
            }
        }
    except Exception as e:
        logger.error(f"Error fetching Bluesky trends: {e}")
        logger.error(f"Exception details: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "data": {}}

# Main function to collect and analyze trends
def analyze_trends(domain=None):
    logger.info(f"Starting trend analysis{' for domain: ' + domain if domain else ''}...")
    
    # Parse domain into keywords if provided
    domain_keywords = None
    if domain:
        domain_keywords = [kw.strip() for kw in domain.split(',')]
        logger.info(f"Using domain keywords: {domain_keywords}")
    
    # Get the current timestamp
    timestamp = datetime.datetime.utcnow().isoformat()
    
    # Fetch data from all platforms
    reddit_data = fetch_reddit_trends(domain_keywords)
    youtube_data = fetch_youtube_trends(domain_keywords)
    bluesky_data = fetch_bluesky_trends(domain_keywords)
    
    # Extract all text content for analysis
    all_texts = []
    
    # Process reddit data
    if reddit_data["success"]:
        for post in reddit_data["data"].get("hot_posts", []):
            all_texts.append(post.get("title", ""))
    
    # Process youtube data
    if youtube_data["success"]:
        for video in youtube_data["data"].get("trending_videos", []):
            all_texts.append(video.get("title", ""))
            all_texts.append(video.get("description", ""))
    
    # Process bluesky data
    if bluesky_data["success"]:
        for post in bluesky_data["data"].get("popular_posts", []):
            all_texts.append(post.get("text", ""))
    
    # Analyze the collected data
    top_words = get_top_words(all_texts)
    
    # Get all hashtags
    all_hashtags = []
    if bluesky_data["success"]:
        all_hashtags.extend(list(bluesky_data["data"].get("trending_hashtags", {}).keys()))
    
    for text in all_texts:
        all_hashtags.extend(extract_hashtags(text))
    
    # Count hashtag frequency
    hashtag_counts = Counter(all_hashtags)
    top_hashtags = dict(hashtag_counts.most_common(30))
    
    # Perform sentiment analysis
    sentiment_data = get_aggregate_sentiment(all_texts)
    
    # Determine overall trend mood
    trend_mood = "neutral"
    if sentiment_data["textblob"]["avg_polarity"] > 0.2:
        trend_mood = "positive"
    elif sentiment_data["textblob"]["avg_polarity"] < -0.2:
        trend_mood = "negative"
    
    # Extract top trends
    top_trends = []
    
    # From Reddit
    if reddit_data["success"]:
        for subreddit in reddit_data["data"].get("trending_subreddits", [])[:5]:
            top_trends.append(subreddit.get("name", ""))
    
    # From YouTube
    if youtube_data["success"]:
        for video in youtube_data["data"].get("trending_videos", [])[:5]:
            # Extract main topic from title
            title = video.get("title", "")
            if title:
                title_words = title.split()
                if len(title_words) > 3:
                    top_trends.append(" ".join(title_words[:3]) + "...")
                else:
                    top_trends.append(title)
    
    # Create the analysis document
    analysis_doc = {
        "timestamp": timestamp,
        "domain": domain,
        "top_hashtags": top_hashtags,
        "top_words": top_words,
        "top_trends": top_trends,
        "sentiment": {
            "overall_mood": trend_mood,
            "data": sentiment_data
        },
        "platform_data": {
            "reddit": reddit_data["data"] if reddit_data["success"] else {},
            "youtube": youtube_data["data"] if youtube_data["success"] else {},
            "bluesky": bluesky_data["data"] if bluesky_data["success"] else {}
        }
    }
    
    # Store in MongoDB
    try:
        # Use upsert to update if exists or insert if not
        collection.update_one(
            {"_id": "current_analysis"},  # Use a fixed ID for the single document
            {"$set": analysis_doc},
            upsert=True
        )
        logger.info("Successfully stored analysis data in MongoDB")
    except Exception as e:
        logger.error(f"Failed to store data in MongoDB: {e}")
    
    logger.info("Trend analysis completed successfully")

# Schedule the job to run every 30 minutes
def schedule_jobs(domain=None):
    def run_analysis():
        analyze_trends(domain)
    
    schedule.every(30).minutes.do(run_analysis)
    
    # Run immediately on startup
    run_analysis()
    
    # Keep the script running and execute scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    import argparse
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Social Media Trend Analysis Service")
    parser.add_argument("--domain", type=str, help="Domain keywords to filter trends (comma-separated)")
    args = parser.parse_args()
    
    domain = args.domain
    
    logger.info(f"Starting Social Media Trend Analysis Service{' for domain: ' + domain if domain else ''}")
    schedule_jobs(domain)