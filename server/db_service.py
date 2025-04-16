import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize MongoDB variables
client = None
db = None
collection = None

def initialize_db():
    """Initialize the database connection"""
    global client, db, collection
    
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    try:
        client = MongoClient(MONGO_URI)
        db = client["PixelFlowLabs"]
        collection = db["trends"]
        logger.info("Successfully connected to MongoDB")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        client = None
        return False

def get_latest_trends_data():
    """
    Function to get the latest trends data from the database
    """
    try:
        if not client:
            logger.error("Database connection not available")
            return None

        latest_trend = collection.find_one(
            {},  # empty query to match all documents
            {"platform_data": 0},  # exclude platform_data field
            sort=[("timestamp", -1)]  # sort by timestamp in descending order
        )

        if not latest_trend:
            logger.error("No trend data available")
            return {}

        # Convert ObjectId to string
        if "_id" in latest_trend:
            latest_trend["_id"] = str(latest_trend["_id"])
            
        return latest_trend
    except Exception as e:
        logger.error(f"Error retrieving trend data: {e}")
        return None
