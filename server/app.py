from flask import Flask, jsonify
import os
from pymongo import MongoClient
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trends_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Initialize MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(MONGO_URI)
    db = client["PixelFlowLabs"]
    collection = db["trends"]
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    client = None

@app.route('/api/trends', methods=['GET'])
def get_latest_trends():
    """
    Endpoint to retrieve the most recent trends data from MongoDB
    """
    try:
        # Check if MongoDB connection is available
        if not client:
            return jsonify({"error": "Database connection not available"}), 500
        
        # Get the latest trend document sorted by timestamp in descending order
        latest_trend = collection.find_one(
            {},  # empty query to match all documents
            {"platform_data": 0},  # exclude platform_data field
            sort=[("timestamp", -1)]  # sort by timestamp in descending order
        )
        
        # If no trends found
        if not latest_trend:
            return jsonify({"error": "No trend data available"}), 404
        
        # Convert ObjectId to string for JSON serialization
        if "_id" in latest_trend:
            latest_trend["_id"] = str(latest_trend["_id"])
        
        logger.info(f"Retrieved latest trend data from {latest_trend.get('timestamp', 'unknown timestamp')}")
        
        return jsonify(latest_trend)
    
    except Exception as e:
        logger.error(f"Error retrieving trend data: {e}")
        return jsonify({"error": f"Failed to retrieve trend data: {str(e)}"}), 500

if __name__ == "__main__":
    logger.info("Starting Flask Trends API server on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)