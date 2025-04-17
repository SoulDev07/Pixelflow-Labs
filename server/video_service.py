import os
import json
import logging
import google.generativeai as genai
from regex import F
import requests
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# External video API configuration
VIDEO_API_URL = os.getenv("VIDEO_API_URL", "http://localhost:5000/generate-video")


def generate_video_prompt(form_data, trends_data):
    """
    Generate a video prompt using Gemini model with form data and trends
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
Create a concise yet detailed video generation prompt that effectively showcases the product using the information provided below. The video should be cinematic, engaging, and visually rich, incorporating relevant current trends to enhance appeal. The final output should describe a short-form video concept—ideally under 5 seconds—that feels modern and compelling.

PRODUCT INFORMATION:

Product Name: {form_data.get('productName')}
Description: {form_data.get('description')}
Suggested Scenes or Key Moments: {form_data.get('scenes')}

CURRENT TRENDS TO INCORPORATE:
{json.dumps(trends_data, indent=2)}

Make sure the prompt is visually descriptive, trend-aware, and tailored to a short video format suitable for platforms like TikTok, Instagram Reels, or YouTube Shorts.
Dont give any audio or music descriptions, video will be silent.
        """

        response = model.generate_content(prompt)
        video_prompt = response.text

        logger.info("Video prompt generated successfully")
        print(f"Video prompt: {video_prompt}")

        response = model.generate_content(f"""
Simplify {video_prompt}. Reduce it to 10 words, it should be very concise and clear. It is a Ad.
Prompt should be like: an object performing an action in a specific environment. It should be generalized, not product name like "a cat is walking".     

        """
        )

        video_prompt = response.text

        logger.info("Video prompt simplified successfully")
        print(f"Simplified video prompt: {video_prompt}")

        return video_prompt

    except Exception as e:
        logger.error(f"Error generating video prompt: {e}")
        return None


def call_video_generation_api(video_prompt, **kwargs):
    """
    Call external video generation API with the prompt and optional parameters

    Parameters:
    - video_prompt (str): Text prompt for video generation
    - kwargs: Optional parameters for video generation
        - negative_prompt (str): Negative prompt for video generation
        - num_inference_steps (int): Number of inference steps
        - guidance_scale (float): Guidance scale
        - height (int): Video height
        - width (int): Video width
        - num_frames (int): Number of frames
        - fps (int): Frames per second
    """
    try:
        headers = {
            "Content-Type": "application/json"
        }

        # Default parameters
        payload = {
            "prompt": video_prompt,
            "negative_prompt": kwargs.get("negative_prompt", "low quality, blurry, artifacts"),
            "num_inference_steps": kwargs.get("num_inference_steps", 50),
            "guidance_scale": kwargs.get("guidance_scale", 7.5),
            "height": kwargs.get("height", 256),
            "width": kwargs.get("width", 256),
            "num_frames": kwargs.get("num_frames", 24),
            "fps": kwargs.get("fps", 8)
        }

        # Stream the response to get the file directly
        with requests.post(VIDEO_API_URL, headers=headers, json=payload, stream=True) as response:
            response.raise_for_status()

            # Check if the response is JSON or a file
            content_type = response.headers.get('Content-Type', '')

            if 'application/json' in content_type:
                return {'json_response': response.json()}
            elif 'video/mp4' in content_type:
                # Create a temporary file for the video
                import tempfile
                import os

                temp_dir = tempfile.gettempdir()
                video_filename = f"generated_video_{os.urandom(4).hex()}.mp4"
                video_path = os.path.join(temp_dir, video_filename)

                print(f"Saving video to {video_path}")

                # Write the video file
                with open(video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                return {'video_path': video_path, 'prompt': video_prompt}
            else:
                logger.error(f"Unexpected content type: {content_type}")
                return None

    except Exception as e:
        logger.error(f"Error calling video generation API: {e}")
        return None
