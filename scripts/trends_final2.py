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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trend_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.error(f"Failed to download NLTK resources: {e}")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["PixelFlowLabs"]
trend_collection = db["trends"]
analysis_collection = db["analysis"]

try:
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
except Exception as e:
    logger.error(f"Failed to load transformer model: {e}")
    sentiment_analyzer = None

def is_domain_related(text, domain_keywords):
    if not text or not domain_keywords:
        return False
    
    text = text.lower()
    for keyword in domain_keywords:
        if keyword.lower() in text:
            return True
    return False

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

def preprocess_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    return text

def extract_hashtags(text):
    if not text:
        return []
    hashtags = re.findall(r'#(\w+)', text)
    return hashtags

def remove_stopwords(text):
    if not text:
        return ""
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_text = [word for word in word_tokens if word not in stop_words]
    return ' '.join(filtered_text)

def get_top_words(texts, n=20):
    word_counts = Counter()
    stop_words = set(stopwords.words('english'))
    
    for text in texts:
        if not isinstance(text, str):
            continue
            
        text = preprocess_text(text)
        words = word_tokenize(text)
        
        words = [word for word in words 
                if word.isalnum() 
                and len(word) > 2 
                and word not in stop_words]
        
        word_counts.update(words)
    
    return dict(word_counts.most_common(n))

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
        result = sentiment_analyzer(text[:512])[0]
        return result
    except Exception as e:
        logger.error(f"Transformer sentiment analysis error: {e}")
        return {"label": "NEUTRAL", "score": 0.5}

def get_aggregate_sentiment(texts, domain=None):
    if not texts:
        return {
            "textblob": {"avg_polarity": 0, "avg_subjectivity": 0},
            "transformer": {"positive_percentage": 50, "avg_confidence": 0.5},
            "sentiment_label": "neutral"
        }
    
    polarities = []
    subjectivities = []
    positive_count = 0
    confidence_scores = []
    
    domain_texts = []
    if domain:
        domain_texts = [text for text in texts if is_domain_related(text, domain)]
    
    target_texts = domain_texts if domain and domain_texts else texts
    
    for text in target_texts:
        if text:
            tb_sentiment = analyze_sentiment_textblob(text)
            polarities.append(tb_sentiment["polarity"])
            subjectivities.append(tb_sentiment["subjectivity"])
            
            if sentiment_analyzer:
                tf_sentiment = analyze_sentiment_transformers(text)
                if tf_sentiment["label"] == "POSITIVE":
                    positive_count += 1
                confidence_scores.append(tf_sentiment["score"])
    
    total = len(target_texts) if target_texts else 1
    avg_polarity = sum(polarities) / len(polarities) if polarities else 0
    
    sentiment_label = "neutral"
    if avg_polarity > 0.2:
        sentiment_label = "positive"
    elif avg_polarity < -0.2:
        sentiment_label = "negative"
    
    return {
        "textblob": {
            "avg_polarity": avg_polarity,
            "avg_subjectivity": sum(subjectivities) / len(subjectivities) if subjectivities else 0
        },
        "transformer": {
            "positive_percentage": (positive_count / total) * 100 if total > 0 else 50,
            "avg_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        },
        "sentiment_label": sentiment_label
    }

def fetch_reddit_trends(domain_keywords=None):
    reddit = init_reddit()
    if not reddit:
        return {"success": False, "data": {}}
    
    try:
        trending_subreddits = []
        hot_posts = []
        
        if domain_keywords:
            search_query = " OR ".join(domain_keywords)
            for subreddit in reddit.subreddits.search(search_query, limit=10):
                trending_subreddits.append({
                    "name": subreddit.display_name,
                    "subscribers": subreddit.subscribers,
                    "description": subreddit.public_description
                })
            
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
            for subreddit in reddit.subreddits.popular(limit=10):
                trending_subreddits.append({
                    "name": subreddit.display_name,
                    "subscribers": subreddit.subscribers,
                    "description": subreddit.public_description
                })
            
            for submission in reddit.subreddit("all").hot(limit=25):
                hot_posts.append({
                    "title": submission.title,
                    "subreddit": submission.subreddit.display_name,
                    "score": submission.score,
                    "comments": submission.num_comments,
                    "url": submission.url,
                    "created_utc": datetime.datetime.fromtimestamp(submission.created_utc).isoformat()
                })
        
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
                
                video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
                
                if video_ids:
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
        
        seen_ids = set()
        unique_videos = []
        for video in trending_videos:
            if video["video_id"] not in seen_ids:
                seen_ids.add(video["video_id"])
                unique_videos.append(video)
        
        return {
            "success": True,
            "data": {
                "trending_videos": unique_videos[:25]
            }
        }
    except Exception as e:
        logger.error(f"Error fetching YouTube trends: {e}")
        return {"success": False, "data": {}}

def fetch_bluesky_trends(domain_keywords=None):
    client = init_bluesky()
    if not client:
        return {"success": False, "data": {}}
    
    try:
        posts = []
        hashtags = []
        
        feed_generator = "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot"
        
        try:
            feed = client.app.bsky.feed.get_feed({
                'feed': feed_generator,
                'limit': 100
            }, {
                'headers': {
                    'Accept-Language': "en",
                }
            })
            
            if hasattr(feed, 'feed'):
                for feed_view in feed.feed:
                    try:
                        post = feed_view.post
                        
                        if not hasattr(post, 'record'):
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
                        continue
                        
        except Exception as e:
            try:
                timeline = client.app.bsky.feed.get_timeline({'limit': 25})
                
                if hasattr(timeline, 'feed'):
                    for feed_view in timeline.feed:
                        try:
                            post = feed_view.post
                            
                            if not hasattr(post, 'record'):
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
                            continue
            except Exception as e:
                logger.error(f"Failed to fetch timeline: {e}")
        
        hashtag_counts = Counter(hashtags)
        
        if domain_keywords:
            hashtag_counts = Counter({
                tag: count for tag, count in hashtag_counts.items()
                if any(keyword.lower() in tag.lower() for keyword in domain_keywords)
            })
        
        return {
            "success": True,
            "data": {
                "popular_posts": posts,
                "trending_hashtags": dict(hashtag_counts.most_common(20))
            }
        }
    except Exception as e:
        logger.error(f"Error fetching Bluesky trends: {e}")
        return {"success": False, "data": {}}

def get_top_news(all_texts, domain_keywords=None, limit=10):
    news_items = []
    
    # Extract potential news from all texts
    for text in all_texts:
        if len(text) > 40:  # Minimum length for a news item
            if domain_keywords and not is_domain_related(text, domain_keywords):
                continue
            
            # Basic heuristic for identifying news-like content
            if any(keyword in text.lower() for keyword in ['new', 'launch', 'announce', 'discover', 'reveal', 'update']):
                news_items.append(text)
    
    # Sort by length as a very basic relevance metric (longer texts might be more informative)
    news_items.sort(key=len, reverse=True)
    
    return news_items[:limit]

def calculate_trend_metrics(reddit_data, youtube_data, bluesky_data, domain_keywords=None):
    all_texts = []
    
    # Process reddit data
    reddit_posts = []
    if reddit_data["success"]:
        reddit_posts = reddit_data["data"].get("hot_posts", [])
        for post in reddit_posts:
            all_texts.append(post.get("title", ""))
    
    # Process youtube data
    youtube_videos = []
    if youtube_data["success"]:
        youtube_videos = youtube_data["data"].get("trending_videos", [])
        for video in youtube_videos:
            all_texts.append(video.get("title", ""))
            all_texts.append(video.get("description", ""))
    
    # Process bluesky data
    bluesky_posts = []
    if bluesky_data["success"]:
        bluesky_posts = bluesky_data["data"].get("popular_posts", [])
        for post in bluesky_posts:
            all_texts.append(post.get("text", ""))
    
    # Get most used words
    most_used_words = get_top_words(all_texts, 30)
    
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
    sentiment_data = get_aggregate_sentiment(all_texts, domain_keywords)
    
    # Get top news
    top_news = get_top_news(all_texts, domain_keywords)
    
    # Calculate engagement metrics
    total_engagement = {
        "reddit": {
            "total_posts": len(reddit_posts),
            "total_score": sum(post.get("score", 0) for post in reddit_posts),
            "total_comments": sum(post.get("comments", 0) for post in reddit_posts)
        },
        "youtube": {
            "total_videos": len(youtube_videos),
            "total_views": sum(video.get("view_count", 0) for video in youtube_videos),
            "total_likes": sum(video.get("like_count", 0) for video in youtube_videos),
            "total_comments": sum(video.get("comment_count", 0) for video in youtube_videos)
        },
        "bluesky": {
            "total_posts": len(bluesky_posts),
            "total_likes": sum(post.get("likes", 0) for post in bluesky_posts),
            "total_replies": sum(post.get("replies", 0) for post in bluesky_posts),
            "total_reposts": sum(post.get("reposts", 0) for post in bluesky_posts)
        }
    }
    
    # Find top influencers
    top_reddit_authors = Counter()
    for post in reddit_posts:
        subreddit = post.get("subreddit", "")
        if subreddit:
            top_reddit_authors[subreddit] += post.get("score", 0)
    
    top_youtube_channels = Counter()
    for video in youtube_videos:
        channel = video.get("channel", "")
        if channel:
            top_youtube_channels[channel] += video.get("view_count", 0)
    
    # Prepare metrics document
    metrics = {
        "most_used_words": most_used_words,
        "top_hashtags": top_hashtags,
        "sentiment": sentiment_data,
        "top_news": top_news,
        "engagement": total_engagement,
        "top_influencers": {
            "reddit": dict(top_reddit_authors.most_common(10)),
            "youtube": dict(top_youtube_channels.most_common(10))
        }
    }
    
    return metrics

def analyze_trends(domain=None):
    logger.info(f"Starting condensed trend analysis{' for domain: ' + domain if domain else ''}...")
    
    domain_keywords = None
    if domain:
        domain_keywords = [kw.strip() for kw in domain.split(',')]
    
    timestamp = datetime.datetime.utcnow().isoformat()
    
    # Fetch data from all platforms
    reddit_data = fetch_reddit_trends(domain_keywords)
    youtube_data = fetch_youtube_trends(domain_keywords)
    bluesky_data = fetch_bluesky_trends(domain_keywords)
    
    # Calculate consolidated metrics
    metrics = calculate_trend_metrics(reddit_data, youtube_data, bluesky_data, domain_keywords)
    
    # Create the condensed analysis document
    condensed_doc = {
        "timestamp": timestamp,
        "domain": domain,
        "metrics": metrics
    }
    
    # Create time series entry for tracking changes over time
    time_series_doc = {
        "timestamp": timestamp,
        "domain": domain,
        "most_used_words": metrics["most_used_words"],
        "top_hashtags": metrics["top_hashtags"],
        "sentiment": metrics["sentiment"],
        "engagement": metrics["engagement"]
    }
    
    # Store in MongoDB
    try:
        # Use upsert for current analysis
        trend_collection.update_one(
            {"_id": f"current_trends{'_' + domain.replace(',', '_') if domain else ''}"},
            {"$set": condensed_doc},
            upsert=True
        )
        
        # Insert time series data with unique timestamp ID
        analysis_collection.insert_one({
            "_id": f"trends_{timestamp.replace(':', '_').replace('.', '_')}{'_' + domain.replace(',', '_') if domain else ''}",
            **time_series_doc
        })
        
        logger.info("Successfully stored condensed analysis data in MongoDB")
    except Exception as e:
        logger.error(f"Failed to store data in MongoDB: {e}")
    
    logger.info("Condensed trend analysis completed successfully")
    return condensed_doc

def schedule_jobs(domain=None):
    def run_analysis():
        analyze_trends(domain)
    
    schedule.every(30).minutes.do(run_analysis)
    run_analysis()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Condensed Social Media Trend Analysis Service")
    parser.add_argument("--domain", type=str, help="Domain keywords to filter trends (comma-separated)")
    args = parser.parse_args()
    
    domain = args.domain
    
    logger.info(f"Starting Condensed Social Media Trend Analysis Service{' for domain: ' + domain if domain else ''}")
    schedule_jobs(domain)