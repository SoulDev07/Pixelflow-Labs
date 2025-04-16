import json
import re
import datetime
from api_clients import gemini_model, logger, GEMINI_AVAILABLE

def generate_ai_analysis(analysis_data, domain=None):
    """
    Use Gemini AI to analyze trends and provide insights
    """
    if not GEMINI_AVAILABLE:
        logger.warning("Gemini AI not available, skipping AI analysis")
        return {
            "error": "Gemini AI not configured properly",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    
    try:
        # Prepare context for the AI
        domain_context = f"in the {domain} domain" if domain else "across social media"
        
        # Extract key information for analysis
        top_hashtags = list(analysis_data.get("top_hashtags", {}).keys())[:10]
        top_words = list(analysis_data.get("top_words", {}).keys())[:10]
        top_trends = analysis_data.get("top_trends", [])[:10]
        sentiment_data = analysis_data.get("sentiment", {})
        
        # Get platform-specific data
        reddit_data = analysis_data.get("platform_data", {}).get("reddit", {})
        youtube_data = analysis_data.get("platform_data", {}).get("youtube", {})
        bluesky_data = analysis_data.get("platform_data", {}).get("bluesky", {})
        
        # Extract top posts/videos from platforms
        reddit_posts = reddit_data.get("hot_posts", [])[:5]
        youtube_videos = youtube_data.get("trending_videos", [])[:5]
        bluesky_posts = bluesky_data.get("popular_posts", [])[:5]
        
        # Construct prompt for Gemini
        prompt = f"""
        As a social media trend analyst, analyze the following trending data {domain_context} and provide insights:
        
        Top Hashtags: {', '.join(top_hashtags) if top_hashtags else 'None available'}
        
        Top Keywords: {', '.join(top_words) if top_words else 'None available'}
        
        Top Trends: {', '.join(top_trends) if top_trends else 'None available'}
        
        Overall Sentiment: {sentiment_data.get('overall_mood', 'neutral')}
        
        Sample Content:
        - Reddit: {[post.get('title', '') for post in reddit_posts] if reddit_posts else 'None available'}
        - YouTube: {[video.get('title', '') for video in youtube_videos] if youtube_videos else 'None available'}
        - Bluesky: {[post.get('text', '') for post in bluesky_posts] if bluesky_posts else 'None available'}
        
        Based on this data, provide:
        1. Key insights about current trends {domain_context} (3-5 bullet points)
        2. Emerging patterns or themes
        3. User sentiment analysis and what it reveals
        4. Content strategy recommendations based on these trends
        5. Predicted trend trajectory for the next 24-48 hours
        
        Format your response as JSON with the following keys:
        - "key_insights": array of strings
        - "emerging_patterns": array of strings
        - "sentiment_analysis": string
        - "content_recommendations": array of strings
        - "trend_prediction": string
        - "summary": string (brief overall summary)
        """
        
        # Request analysis from Gemini
        logger.info("Sending request to Gemini AI for trend analysis")
        response = gemini_model.generate_content(prompt)
        
        # Process the response
        if hasattr(response, 'text'):
            response_text = response.text
            
            # Try to extract JSON from the response
            try:
                # Find JSON content in the response
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # If no code block, try to parse the entire response
                    json_str = response_text
                
                # Parse the JSON content
                ai_analysis = json.loads(json_str)
                
                # Add timestamp
                ai_analysis["timestamp"] = datetime.datetime.utcnow().isoformat()
                
                logger.info("Successfully generated AI analysis")
                return ai_analysis
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                
                # Fallback: create a structured response manually
                return {
                    "error": "Could not parse AI response as JSON",
                    "raw_response": response_text,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
        else:
            logger.error("Gemini response didn't contain text attribute")
            return {
                "error": "Invalid response from Gemini AI",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error generating AI analysis: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "error": f"Failed to generate AI analysis: {str(e)}",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
