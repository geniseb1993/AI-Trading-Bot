import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Make sure current directory is in the path
logger.info(f"Current directory: {os.getcwd()}")
sys.path.insert(0, os.getcwd())

# Flask imports
from flask import Flask
app = Flask(__name__)

# Try to import the CEO dashboard blueprint
try:
    logger.info("Trying to import CEO dashboard routes...")
    from api.routes.ceo_dashboard_routes import ceo_dashboard_bp
    
    # Try to register the blueprint
    logger.info("Trying to register CEO dashboard blueprint...")
    app.register_blueprint(ceo_dashboard_bp)
    
    logger.info("SUCCESS! CEO dashboard routes imported and registered.")
    
    # List available routes
    logger.info("Available routes:")
    for rule in app.url_map.iter_rules():
        logger.info(f"  {rule.endpoint} -> {rule.rule}")
    
except Exception as e:
    logger.error(f"FAILED to import/register CEO dashboard routes: {e}")
    import traceback
    traceback.print_exc()

logger.info("Test completed!") 