import os
import logging
from dotenv import load_dotenv
import praw
from googleapiclient.discovery import build
from atproto import Client
import google.generativeai as genai

# Load environment variables
load_dotenv()

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

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# API Keys and Credentials
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "trend_analyzer_script")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

BLUESKY_EMAIL = os.getenv("BLUESKY_EMAIL")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Google Gemini AI
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
    GEMINI_AVAILABLE = True
    logger.info("Successfully initialized Gemini AI")
except Exception as e:
    logger.error(f"Failed to initialize Gemini AI: {e}")
    GEMINI_AVAILABLE = False
    gemini_model = None

# API client initialization functions
def init_reddit():
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        return reddit
    except Exception as e:
        logger.error(f"Failed to initialize Reddit client: {e}")
        return None

def init_youtube():
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        return youtube
    except Exception as e:
        logger.error(f"Failed to initialize YouTube client: {e}")
        return None

def init_bluesky():
    try:
        atproto_client = Client()
        atproto_client.login(BLUESKY_EMAIL, BLUESKY_PASSWORD)
        return atproto_client
    except Exception as e:
        logger.error(f"Failed to initialize Bluesky client: {e}")
        return None

# Database utility functions
def get_db_connection():
    """Create and return a MongoDB connection"""
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI)
        db = client["PixelFlowLabs"]
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return None

def save_trend_analysis(analysis_doc):
    """Save trend analysis data to MongoDB"""
    try:
        db = get_db_connection()
        if not db:
            return False
        
        collection = db["trends"]
        result = collection.insert_one(analysis_doc)
        logger.info(f"Successfully stored analysis data in MongoDB with id: {result.inserted_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to store data in MongoDB: {e}")
        return False
