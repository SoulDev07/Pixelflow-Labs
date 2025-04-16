import datetime
from api_clients import init_reddit, logger
from text_processing import is_domain_related

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
