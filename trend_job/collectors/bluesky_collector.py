from collections import Counter
from api_clients import init_bluesky, logger
from text_processing import extract_hashtags, is_domain_related

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
