from api_clients import init_youtube, logger

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
