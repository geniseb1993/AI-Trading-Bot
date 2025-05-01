#!/usr/bin/env python
"""
Deployment helper script for troubleshooting Render deployments.
This script will check for common deployment issues and fix them if possible.
"""

import os
import sys
import importlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_wsgi_app():
    """Check if wsgi:app is correctly configured and importable."""
    try:
        from wsgi import app
        logger.info("✅ Successfully imported wsgi:app")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import wsgi:app: {str(e)}")
        return False

def check_api_module():
    """Check if the api module is correctly configured."""
    try:
        from api import create_app
        logger.info("✅ Successfully imported api.create_app")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import api.create_app: {str(e)}")
        return False

def check_webhook_receiver():
    """Check if webhook_receiver module exists and is importable."""
    try:
        # Try to import webhook_receiver, or create it if it doesn't exist
        try:
            import webhook_receiver
            logger.info("✅ webhook_receiver module exists and is importable")
        except ImportError:
            logger.warning("⚠️ webhook_receiver module not found, creating compatibility module")
            # Create webhook_receiver.py if it doesn't exist
            with open("webhook_receiver.py", "w") as f:
                f.write("""\"\"\"
Compatibility module for Render deployment.
This file simply imports and exposes the app from wsgi.py.
\"\"\"

# Import the app from wsgi.py
from wsgi import app

# This file is referenced by Render's default gunicorn command
# No additional code needed - the import above is sufficient
""")
            logger.info("✅ Created webhook_receiver.py compatibility module")
            
            # Try importing it again
            import webhook_receiver
            logger.info("✅ webhook_receiver module created and imported successfully")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to handle webhook_receiver module: {str(e)}")
        return False

def check_directory_structure():
    """Check if the required directory structure exists."""
    required_dirs = [
        'data',
        'data/logs',
        'data/market_data',
        'data/signals',
        'data/broker',
        'logs',
        'instance'
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            logger.warning(f"⚠️ Directory {directory} does not exist, creating it")
            os.makedirs(directory, exist_ok=True)
    
    logger.info("✅ Directory structure verified")
    return True

def main():
    """Run all deployment checks and fixes."""
    logger.info("Starting deployment helper checks...")
    
    checks = [
        check_directory_structure,
        check_api_module,
        check_wsgi_app,
        check_webhook_receiver
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    if all_passed:
        logger.info("✅ All deployment checks passed")
        return 0
    else:
        logger.error("❌ Some deployment checks failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 