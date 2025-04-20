import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Flask imports
from flask import Flask
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

# Try to import CEO dashboard routes
try:
    from api.routes.ceo_dashboard_routes import ceo_dashboard_bp
    app.register_blueprint(ceo_dashboard_bp)
    logger.info("Successfully registered CEO dashboard routes!")
except Exception as e:
    logger.error(f"Failed to register CEO dashboard routes: {e}")
    import traceback
    traceback.print_exc()

# Test route
@app.route('/test')
def test():
    return "Test route working!"

# Run the app
if __name__ == '__main__':
    logger.info("Starting Flask app on http://localhost:5000")
    app.run(debug=True, port=5000) 