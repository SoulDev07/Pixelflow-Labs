from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

# Import the API routes
from routes import register_routes
from db_service import initialize_db

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

# Initialize database connection
initialize_db()

# Register all routes
register_routes(app)

if __name__ == "__main__":
    logger.info("Starting Flask Trends API server on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
