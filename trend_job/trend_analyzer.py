import datetime
from collections import Counter
from api_clients import logger, save_trend_analysis
from text_processing import get_top_words, extract_hashtags
from sentiment_analysis import get_aggregate_sentiment
from collectors.reddit_collector import fetch_reddit_trends
from collectors.youtube_collector import fetch_youtube_trends
from collectors.bluesky_collector import fetch_bluesky_trends
from ai_analysis import generate_ai_analysis

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
    
    # Create the initial analysis document
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
    
    # Add AI analysis
    logger.info("Generating AI analysis of trends")
    ai_analysis = generate_ai_analysis(analysis_doc, domain)
    analysis_doc["ai_analysis"] = ai_analysis
    
    # Store in MongoDB
    save_trend_analysis(analysis_doc)
    
    logger.info("Trend analysis with AI insights completed successfully")
    
    return analysis_doc
