#!/usr/bin/env python
"""
Ensure required directories exist before starting the application.
"""

import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        # Core directories
        "data",
        "data/broker",
        "data/market_data",
        "data/logs",
        "data/signals",
        "data/dashboard",
        "logs",
        "static",  # For frontend static files
        
        # Public assets
        "public",
        "public/images",
        "public/sounds",
        
        # Broker data
        "api/broker_integration/data",
        "api/broker_integration/data/broker",
        
        # Dual bot
        "dual_bot/logs",
    ]
    
    # Create directories
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Directory exists or created: {directory}")
        except Exception as e:
            logger.error(f"Error creating directory {directory}: {e}")
    
    logger.info(f"Ensured {len(directories)} directories exist")
    return True

if __name__ == "__main__":
    logger.info("Running directory check...")
    ensure_directories()
    logger.info("Directory check complete") 