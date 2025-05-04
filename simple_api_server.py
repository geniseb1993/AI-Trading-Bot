from flask import Flask, jsonify
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to create required directories and files
def setup_directories():
    os.makedirs('data/dashboard', exist_ok=True)
    os.makedirs('data/broker', exist_ok=True)
    os.makedirs('data/logs', exist_ok=True)
    
    # Create a simple dashboard file
    dashboard_path = os.path.join('data', 'dashboard', 'simple_dashboard.json')
    with open(dashboard_path, 'w') as f:
        json.dump({
            "status": "active",
            "created_at": datetime.now().isoformat()
        }, f, indent=2)
    
    logger.info("Directories and files created successfully")

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'server': 'simple_api_server',
        'version': '1.0.0'
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the status of the server."""
    logger.info("Status endpoint called")
    
    status = {
        'dual_bot': {
            'status': 'active',
            'last_active': datetime.now().isoformat(),
            'uptime': '0d 0h 10m',
            'errors': []
        }
    }
    
    return jsonify(status)

if __name__ == '__main__':
    logger.info("Starting Simple API Server on port 5001")
    print("Starting Simple API Server on http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    # Create directories at startup
    setup_directories()
    
    app.run(host='0.0.0.0', port=5001, debug=True) 