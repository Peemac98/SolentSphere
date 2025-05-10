"""
SolentSphere Chatbot - Flask Web Application

This script creates a Flask web application that serves both the chatbot API
and the web interface for interacting with the chatbot.

Key components:
1. Web interface with HTML, CSS, and JavaScript
2. API endpoints for chatbot interactions
3. Error handling
4. Basic request logging
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import time
import logging
from datetime import datetime
import os
import traceback

# Import chatbot functionality from chatbot.py
from chatbot import chatbot_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SolentSphere-API")

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes and origins
CORS(app)

# Display welcome message
logger.info("=" * 50)
logger.info("SOLENTSPHERE CHATBOT - STARTING UP")
logger.info("=" * 50)
logger.info(f"Application started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("-" * 50)

@app.route('/')
def home():
    """
    Serve the main chatbot web interface.
    """
    return render_template('index.html')



@app.route('/api/health')
def health_check():
    """
    Health check endpoint to verify the API is operational.
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main endpoint for chatbot interactions.
    
    Expects a JSON payload with:
    {
        "message": "user's message here"
    }
    
    Returns a JSON response with:
    {
        "status": "success",
        "response": "chatbot's response here",
        "timestamp": "ISO format timestamp",
        "response_time_ms": response time in milliseconds
    }
    """
    try:
        # Start timer for performance tracking
        start_time = time.time()
        
        # Get the JSON data from the request
        data = request.get_json()
        
        # Check if 'message' field exists in the request
        if 'message' not in data:
            return jsonify({
                "status": "error",
                "error": "Missing 'message' field in request",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Get the user message
        user_message = data['message']
        
        # Log the incoming message
        logger.info(f"Received message: {user_message}")
        
        # Get chatbot response
        response = chatbot_response(user_message)
        
        # Calculate response time
        response_time = round((time.time() - start_time) * 1000)  # in milliseconds
        
        # Log the response and performance
        logger.info(f"Response: {response}")
        logger.info(f"Response time: {response_time}ms")
        
        # Return the response
        return jsonify({
            "status": "success",
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "response_time_ms": response_time
        })
        
    except Exception as e:
        # Log the error
        logger.error(f"Error processing request: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return error response
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.errorhandler(404)
def page_not_found(e):
    """
    Handle 404 errors.
    """
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    """
    Handle 500 errors.
    """
    logger.error(f"Server error: {str(e)}")
    return jsonify({
        "status": "error",
        "error": "Internal server error",
        "message": "Something went wrong on our end. Please try again later.",
        "timestamp": datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    # Check if port is specified in environment variable
    port = int(os.environ.get("PORT", 5000))
    
    # Run the app with debug mode enabled for development
    app.run(host='0.0.0.0', port=port, debug=True)